from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments
from datasets import Dataset

# Load the model and tokenizer
model = AutoModelForCausalLM.from_pretrained("mistralai/Mixtral-8x7B-v0.1")
tokenizer = AutoTokenizer.from_pretrained("mistralai/Mixtral-8x7B-v0.1")

# Prepare your dataset
def prepare_dataset(contracts, analyses):
    return Dataset.from_dict({
        "input_text": [f"Analyze this contract:\n{contract}" for contract in contracts],
        "output_text": analyses
    })

train_dataset = prepare_dataset(train_contracts, train_analyses)
val_dataset = prepare_dataset(val_contracts, val_analyses)

# Define training arguments
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,
    per_device_train_batch_size=1,
    per_device_eval_batch_size=1,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir='./logs',
)

# Create Trainer instance
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
)

# Fine-tune the model
trainer.train()

# Save the fine-tuned model
trainer.save_model("./fine_tuned_model")