from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Load GPT-2 model and tokenizer
model_name = "gpt2"  # Small and free
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Prompt: you can replace this with any trade question
prompt = (
    "You are an export and trade advisor.\n"
    "Question: What are the main documents needed for exporting goods?\n"
    "Answer:"
)

# Encode the prompt
input_ids = tokenizer.encode(prompt, return_tensors="pt")

# Generate output
with torch.no_grad():
    output_ids = model.generate(
        input_ids,
        max_length=100,  # how long the output can be
        num_return_sequences=1,
        no_repeat_ngram_size=2,
        do_sample=True,
        temperature=0.7
    )

# Decode and print the result
generated_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
print("\n--- Response ---\n")
print(generated_text)
