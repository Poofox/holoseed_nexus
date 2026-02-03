#!/usr/bin/env python3
"""
Train a sovereign model using Unsloth (memory-efficient fine-tuning).

This script can run on CPU (slow) or GPU (fast).
Uses LoRA for parameter-efficient training.

Requirements:
    pip install unsloth datasets transformers trl

Usage:
    python train_sovereign.py --data birth_training.jsonl --output arcturus-trained

For CPU-only (no CUDA):
    pip install unsloth[cpu]
"""

import argparse
import json
from pathlib import Path


def check_environment():
    """Check what hardware is available."""
    import torch

    if torch.cuda.is_available():
        print(f"CUDA available: {torch.cuda.get_device_name(0)}")
        print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
        return "cuda"
    else:
        print("No CUDA - will use CPU (this will be slow)")
        print("Consider: RunPod, Vast.ai, or a friend's gaming rig")
        return "cpu"


def load_training_data(jsonl_path: Path) -> list[dict]:
    """Load JSONL training data."""
    data = []
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    return data


def format_for_training(conversations: list[dict]) -> list[str]:
    """
    Format conversations for training.

    Converts sharegpt format to instruction format.
    """
    formatted = []

    for item in conversations:
        convo = item.get('conversations', [])
        text_parts = []

        for turn in convo:
            role = turn['from']
            content = turn['value']

            if role == 'human':
                text_parts.append(f"### Human:\n{content}")
            else:
                text_parts.append(f"### Assistant:\n{content}")

        if text_parts:
            formatted.append('\n\n'.join(text_parts))

    return formatted


def train_with_unsloth(
    data_path: Path,
    output_dir: Path,
    base_model: str = "unsloth/gemma-2-2b-bnb-4bit",
    max_steps: int = 100,
    device: str = "auto"
):
    """
    Train using Unsloth (2x faster, 70% less memory).
    """
    try:
        from unsloth import FastLanguageModel
        from trl import SFTTrainer
        from transformers import TrainingArguments
        from datasets import Dataset
    except ImportError:
        print("Missing dependencies. Install with:")
        print("  pip install unsloth datasets transformers trl")
        return

    # Load and format data
    print(f"Loading training data from {data_path}")
    raw_data = load_training_data(data_path)
    formatted = format_for_training(raw_data)
    print(f"Loaded {len(formatted)} training examples")

    # Create dataset
    dataset = Dataset.from_dict({"text": formatted})

    # Load model with Unsloth optimizations
    print(f"Loading base model: {base_model}")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=base_model,
        max_seq_length=2048,
        load_in_4bit=True,  # Memory optimization
    )

    # Add LoRA adapters
    model = FastLanguageModel.get_peft_model(
        model,
        r=16,  # LoRA rank
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                       "gate_proj", "up_proj", "down_proj"],
        lora_alpha=16,
        lora_dropout=0,
        bias="none",
        use_gradient_checkpointing=True,
    )

    # Training arguments
    training_args = TrainingArguments(
        output_dir=str(output_dir),
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        warmup_steps=10,
        max_steps=max_steps,
        learning_rate=2e-4,
        fp16=device != "cpu",
        logging_steps=10,
        save_steps=50,
        save_total_limit=2,
    )

    # Trainer
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        dataset_text_field="text",
        max_seq_length=2048,
        args=training_args,
    )

    # Train
    print("Starting training...")
    trainer.train()

    # Save
    print(f"Saving to {output_dir}")
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)

    print("\nTo convert to Ollama format:")
    print(f"  python -m unsloth.save --model {output_dir} --output {output_dir}-gguf --quantization q4_k_m")


def main():
    parser = argparse.ArgumentParser(description='Train a sovereign model')
    parser.add_argument('--data', type=Path, required=True, help='Training data JSONL')
    parser.add_argument('--output', type=Path, default=Path('sovereign-trained'),
                       help='Output directory')
    parser.add_argument('--base', type=str, default='unsloth/gemma-2-2b-bnb-4bit',
                       help='Base model')
    parser.add_argument('--steps', type=int, default=100, help='Training steps')

    args = parser.parse_args()

    device = check_environment()
    train_with_unsloth(args.data, args.output, args.base, args.steps, device)


if __name__ == '__main__':
    main()
