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
        default=os.path.join(BASE_DIR, "llama-3B-instruct"),  # Set default model path here
        metadata={"help": "Path to pretrained model or model identifier from huggingface.co/models"},
    )
    lora_alpha: Optional[int] = field(default=16)
    lora_dropout: Optional[float] = field(default=0.1)
    lora_r: Optional[int] = field(default=64)
    lora_target_modules: Optional[str] = field(
        default="q_proj,k_proj,v_proj,o_proj,down_proj,up_proj,gate_proj",
        metadata={"help": "Comma-separated list of target modules to apply LoRA layers to."},
    )
    use_flash_attn: Optional[bool] = field(default=False, metadata={"help": "Enables Flash attention for training."})


@dataclass
class DataTrainingArguments:
    dataset_path: str = field(
        default=os.path.join(BASE_DIR, "Customer_Support_Dataset.csv"),
        metadata={"help": "Path to the CSV file containing training data."},
    )
    input_field: str = field(default="instruction", metadata={"help": "Field name for user input in the dataset."})
    target_field: str = field(default="response", metadata={"help": "Field name for target responses in the dataset."})
    max_seq_length: int = field(default=180, metadata={"help": "Maximum sequence length for tokenization."})


def create_and_prepare_model(args, data_args):
    # LoRA configuration
    peft_config = LoraConfig(
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        r=args.lora_r,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=args.lora_target_modules.split(","),
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
            row[data_args.input_field], truncation=True, padding="max_length", max_length=data_args.max_seq_length
        )
        targets = tokenizer(
            row[data_args.target_field], truncation=True, padding="max_length", max_length=data_args.max_seq_length
        )
        return {
            "input_ids": inputs["input_ids"],
            "attention_mask": inputs["attention_mask"],
            "labels": targets["input_ids"],
        }

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
        max_seq_length=512,
    )

    # Train the model
    trainer.train()

    # Save the final model
    trainer.save_model()


if __name__ == "__main__":
    main()
