---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.6
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

# Distributed LLM Fine-Tuning with DeepSpeed

Fine-tuning large language models (LLMs) often requires distributed computing to efficiently handle the computational demands of large datasets and model sizes. Practicus AI, combined with the DeepSpeed library, provides a streamlined platform for distributed training and fine-tuning of LLMs. This notebook demonstrates the end-to-end process of dataset preparation, worker configuration, distributed job execution, and model testing using Practicus AI.

Key highlights include:
- Preparing datasets and downloading pre-trained models.
- Setting up distributed workers using DeepSpeed.
- Monitoring and logging distributed jobs.
- Testing the fine-tuned model against its base version.

With Practicus AI's flexible distributed computing framework, you can efficiently manage resource-intensive tasks like LLM fine-tuning, ensuring scalability, idempotency, and atomicity across the entire workflow.


## Dataset Preparation and Model Download

The first step in fine-tuning involves preparing the dataset and downloading the pre-trained model. These steps include:

1. Loading and saving the fine-tuning dataset.
2. Authenticating with Hugging Face to securely access model repositories.
3. Downloading a pre-trained LLM (e.g., LLaMA-3B-Instruct) from the Hugging Face Hub for fine-tuning.

```python
import pandas as pd

url = 'https://raw.githubusercontent.com/practicusai/sample-data/refs/heads/main/customer_support/Customer_Support_Dataset.csv'
df = pd.read_csv(url, index_col=0)

df.head()
```

```python
df.to_csv('Customer_Support_Dataset.csv')
```

### Hugging Face Authentication

To download models from Hugging Face, you need to authenticate using your API token. This ensures secure access to both public and private repositories.

```python
from huggingface_hub.hf_api import HfFolder
try:
    HfFolder.save_token('...')  # Replace with your Hugging Face API token

except:
    print('Hugging face token is wrong.')
```

### Download Pre-Trained Model

The pre-trained LLM is downloaded to a local directory for fine-tuning. Replace `local_dir` and `REPO_ID` with the desired directory and model ID, respectively.

```python
from huggingface_hub import snapshot_download

try:
    local_dir = "..."  # Example: /home/ubuntu/my/llm_fine_tune/llama-3B-instruct
    REPO_ID = "..."  # Example: meta-llama/Llama-3.2-3B-Instruct

    snapshot_download(repo_id=REPO_ID, local_dir=local_dir)

except:
    print("Snapshot didn't found.")
```

## Building Workers for Distributed LLM Fine-Tuning

This section demonstrates how to configure and launch distributed workers for fine-tuning an LLM using DeepSpeed. The main focus areas are:
- Configuring distributed job parameters (e.g., worker count, job directory).
- Setting up workers with appropriate Docker images and resource configurations.
- Initializing the distributed cluster for fine-tuning.

### Prerequisites
- Create a folder `~/my/deepspeed/llm_fine_tune`.
- Copy `train.py` and `ds_config.json` into this directory.

```python
import practicuscore as prt

job_dir = "~/my/deepspeed/llm_fine_tune"
worker_count = 2

distributed_config = prt.DistJobConfig(
    job_type=prt.DistJobType.deepspeed,
    job_dir=job_dir,
    worker_count=worker_count,
    terminate_on_completion=False,
)

worker_config = prt.WorkerConfig(
    worker_image="ghcr.io/practicusai/practicus-gpu-deepspeed",
    worker_size="L-GPU",
    log_level="DEBUG",
    distributed_config=distributed_config,
    startup_script='pip install accelerate trl peft datasets'
)

coordinator_worker = prt.create_worker(worker_config)
job_id = coordinator_worker.job_id
assert job_id, "Could not create distributed job"
```

### Monitoring Distributed Job

Use the `live_view` and `view_log` utilities to monitor the job's progress. These tools provide real-time insights into worker status, GPU utilization, and job logs.

```python
prt.distributed.live_view(job_dir, job_id)
```

```python
prt.distributed.view_log(job_dir, job_id, rank=0)
```

### Terminating Distributed Job Cluster

Once the job completes, terminate the distributed cluster and release resources.

```python
coordinator_worker.terminate()
```

## Testing the Fine-Tuned Model

This section demonstrates how to load and test a fine-tuned LLM. The steps include:
- Installing required libraries.
- Loading the fine-tuned model and tokenizer.
- Comparing the fine-tuned model’s outputs with those from the base model.

```python
! pip install peft accelerate
```

### Comparing Fine-Tuned Model and Base Model

The fine-tuned model and tokenizer are loaded from the `output_dir`. The `device_map='auto'` parameter ensures efficient resource allocation, distributing the model across available GPUs. A conversation-like input is passed to both models, and their outputs are compared.

```python
from transformers import AutoTokenizer, AutoModelForCausalLM

# Load the fine-tuned model
model_name_or_path = './output_dir'  # Path to the saved fine-tuned model

tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, device_map='auto')
model = AutoModelForCausalLM.from_pretrained(model_name_or_path, device_map='auto')
```

```python
# Define chat messages
messages = [{"role": "user", "content": "want assistance to cancel purchase 554"}]

# Apply chat template
prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

# Tokenize input text
inputs = tokenizer(prompt, return_tensors='pt', truncation=True).to("cuda")

# Generate model response
outputs = model.generate(**inputs, max_new_tokens=150, num_return_sequences=1)

# Decode model output
text = tokenizer.decode(outputs[0], skip_special_tokens=True)

# Extract response content
print(text.split("assistant")[1])
```

```python
# Load the base model
model_name_or_path = './llama-3B-instruct'  # Path to the saved fine-tuned model

tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, device_map='auto')
model = AutoModelForCausalLM.from_pretrained(model_name_or_path, device_map='auto')
```

```python
# Define chat messages
messages = [{"role": "user", "content": "want assistance to cancel purchase 554"}]

# Apply chat template
prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

# Tokenize input text
inputs = tokenizer(prompt, return_tensors='pt', truncation=True).to("cuda")

# Generate model response
outputs = model.generate(**inputs, max_new_tokens=150, num_return_sequences=1)

# Decode model output
text = tokenizer.decode(outputs[0], skip_special_tokens=True)

# Extract response content
print(text.split("assistant")[1])
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

**Previous**: [Intro To DeepSpeed](../basics/intro-to-deepspeed.md) | **Next**: [Ray > Interactive > Start Cluster](../../ray/interactive/start-cluster.md)
