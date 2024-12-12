---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.4
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
---

# Building Workers for Distributed LLM Fine-Tuning

This chapter demonstrates the process of setting up distributed workers for fine-tuning a large language model (LLM) using the DeepSpeed library. 

Focuses:
- Configuring and launching distributed workers using the Practicus framework.
- Monitoring and logging distributed job performance and resource usage.
- Terminating the distributed job after completion.

The train.py script and ds_config.json configuration files are used to define the model fine-tuning process.


#### Importing Libraries and Configuring Distributed Job

This step imports the required libraries, including `practicuscore`, and sets up the configurations for a distributed job. The key elements are:
- `job_dir`: Directory containing DeepSpeed configuration files and the training script.
- `DistJobConfig`: Defines distributed job parameters such as worker count and termination policy.
- `WorkerConfig`: Specifies worker parameters, including the Docker image, worker size, and startup script.

The configuration prepares a coordinator worker that initializes a distributed job.

### Before you begin
- Create "deepspeed/llm_fine_tune" under your "~/my" folder.
- And copy `train.py` and `ds_config.json` under this folder.

```python
import practicuscore as prt

# DeepSpeed job directory must have default files ds_config.json and train.py (can be renamed)

job_dir = "~/my/deepspeed/llm_fine_tune"
worker_count = 2

distributed_config = prt.DistJobConfig(
    job_type = prt.DistJobType.deepspeed,
    job_dir = job_dir,
    worker_count = worker_count,
    terminate_on_completion=False,
)

worker_config = prt.WorkerConfig(
    worker_image="ghcr.io/practicusai/practicus-gpu-deepspeed",
    worker_size="L-GPU",
    log_level="DEBUG",
    distributed_config=distributed_config,
    startup_script='pip install accelerate trl peft datasets'
)

# Unlike standard workers, distributed job worker requests do not wait until the cluster is created.
# You can set wait_until_ready=True to change the default behaviour.

coordinator_worker = prt.create_worker(worker_config)

job_id = coordinator_worker.job_id

assert job_id, "Could not create distributed job"
```

### Monitoring Distributed Job

The `live_view` and `view_log` utilities from the Practicus SDK are used to monitor the progress of the distributed job. This provides details such as:
- Job ID, start time, worker states, and GPU utilization.
- Resource allocation for each worker in the distributed cluster.

It helps in tracking the real-time status of the distributed job.

```python
# Live resource allocation
prt.distributed.live_view(job_dir, job_id)
```

```python
# For master logs, you can check Rank-0 logs:
prt.distributed.view_log(job_dir, job_id, rank=0)
```

```python
# For pair logs, you must specify pair IDs, e.g. 1:
prt.distributed.view_log(job_dir, job_id, rank=1)
```

### Terminating Distributed Job Cluster

The distributed job cluster and all associated workers are terminated using the `terminate` method of the coordinator worker.

```python
coordinator_worker.terminate()
```


## Supplementary Files

### ds_config.json
```json
{
    "train_batch_size": 16,
    "gradient_accumulation_steps": 1,
    "fp16": {
        "enabled": true
    },
    "zero_optimization": {
        "stage": 3,
        "overlap_comm": true,
        "contiguous_gradients": true,
        "reduce_bucket_size": 4194304,
        "stage3_prefetch_bucket_size": 3774873,
        "stage3_param_persistence_threshold": 20480,
        "stage3_gather_16bit_weights_on_model_save": true
    }
}
```

### train.py
```python
import os
import pandas as pd
from dataclasses import dataclass, field
from typing import Optional
import torch
from transformers import (
    set_seed,
    TrainingArguments,
    AutoModelForCausalLM,
    AutoTokenizer,
)
from trl import SFTTrainer
from peft import LoraConfig
from datasets import Dataset


BASE_DIR = "/home/ubuntu/my/deepspeed/llm_fine_tune"


@dataclass
class ModelArguments:
    model_name_or_path: str = field(
        default=os.path.join(BASE_DIR, 'llama-3B-instruct'),  # Set default model path here
        metadata={"help": "Path to pretrained model or model identifier from huggingface.co/models"}
    )
    lora_alpha: Optional[int] = field(default=16)
    lora_dropout: Optional[float] = field(default=0.1)
    lora_r: Optional[int] = field(default=64)
    lora_target_modules: Optional[str] = field(
        default="q_proj,k_proj,v_proj,o_proj,down_proj,up_proj,gate_proj",
        metadata={"help": "Comma-separated list of target modules to apply LoRA layers to."},
    )
    use_flash_attn: Optional[bool] = field(
        default=False, metadata={"help": "Enables Flash attention for training."}
    )


@dataclass
class DataTrainingArguments:
    dataset_path: str = field(
        default=os.path.join(BASE_DIR, "Customer_Support_Dataset.csv"),
        metadata={"help": "Path to the CSV file containing training data."}
    )
    input_field: str = field(
        default="instruction",
        metadata={"help": "Field name for user input in the dataset."}
    )
    target_field: str = field(
        default="response",
        metadata={"help": "Field name for target responses in the dataset."}
    )
    max_seq_length: int = field(
        default=180,
        metadata={"help": "Maximum sequence length for tokenization."}
    )


def create_and_prepare_model(args, data_args):
    # LoRA configuration
    peft_config = LoraConfig(
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        r=args.lora_r,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=args.lora_target_modules.split(",")
    )

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(args.model_name_or_path)
    tokenizer.pad_token = tokenizer.eos_token

    # Load model
    model = AutoModelForCausalLM.from_pretrained(
        args.model_name_or_path,
        attn_implementation="flash_attention_2" if args.use_flash_attn else "eager",
    )
    model.resize_token_embeddings(len(tokenizer))

    return model, peft_config, tokenizer


def preprocess_data(df, tokenizer, data_args):
    def tokenize_function(row):
        inputs = tokenizer(
            row[data_args.input_field],
            truncation=True,
            padding="max_length",
            max_length=data_args.max_seq_length
        )
        targets = tokenizer(
            row[data_args.target_field],
            truncation=True,
            padding="max_length",
            max_length=data_args.max_seq_length
        )
        return {"input_ids": inputs["input_ids"], "attention_mask": inputs["attention_mask"],
                "labels": targets["input_ids"]}

    # Adding instruction to training dataset
    instruction = """You are a top-rated customer service agent named John. 
    Be polite to customers and answer all their questions."""

    df[data_args.input_field] = df[data_args.input_field].apply(lambda x: instruction + str(x))

    # Convert pandas DataFrame to Hugging Face Dataset
    dataset = Dataset.from_pandas(df)

    # Apply tokenization
    tokenized_dataset = dataset.map(tokenize_function, batched=False)

    return tokenized_dataset


def main():
    # Define training arguments internally
    training_args = TrainingArguments(
        output_dir="output_dir",  # Directory where the model and logs will be saved
        overwrite_output_dir=True,
        do_train=True,
        per_device_train_batch_size=8,
        num_train_epochs=3,
        logging_dir="logs",
        logging_strategy="steps",
        logging_steps=500,
        save_strategy="steps",
        save_steps=500,
        save_total_limit=2,
        evaluation_strategy="steps",
        eval_steps=500,
        load_best_model_at_end=True,
        seed=42,
        deepspeed="ds_config.json",  # Path to your DeepSpeed config file
        fp16=True,
    )

    # Model and data arguments
    model_args = ModelArguments()
    data_args = DataTrainingArguments()

    # Set seed for reproducibility
    set_seed(training_args.seed)

    # Load dataset
    train_dataset = pd.read_csv(data_args.dataset_path)

    # Taking sample of the dataset
    train_dataset = train_dataset.sample(frac=1.0, random_state=65).reset_index(drop=True)
    train_dataset = train_dataset.iloc[:10]

    # Prepare model and tokenizer
    model, peft_config, tokenizer = create_and_prepare_model(model_args, data_args)

    # Tokenize data
    tokenized_data = preprocess_data(train_dataset, tokenizer, data_args)

    # Trainer setup
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        args=training_args,
        train_dataset=tokenized_data,
        eval_dataset=tokenized_data,
        peft_config=peft_config,
        max_seq_length=512
    )

    # Train the model
    trainer.train()

    # Save the final model
    trainer.save_model()


if __name__ == "__main__":
    main()

```


---

**Previous**: [Download Data Model](download-data-model.md) | **Next**: [Test](test.md)
