from transformers import AutoModelForCausalLM, AutoTokenizer
from sentence_transformers import SentenceTransformer
import faiss
import torch

# Load embedding model
embedder = SentenceTransformer('all-MiniLM-L6-v2')

# Load GPT-2
model_name = "gpt2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Load knowledge base
with open("knowledge_base.txt", "r", encoding="utf-8") as f:
    raw_data = f.read().strip().split("\n\n")

# Create corpus (chunks)
corpus = [entry.replace("\n", " ") for entry in raw_data]

# Embed corpus
corpus_embeddings = embedder.encode(corpus, convert_to_numpy=True)

# Create FAISS index
dimension = corpus_embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(corpus_embeddings)

# Get user question
question = input("Enter your export/trade question:\n")

# Embed question
question_embedding = embedder.encode([question])

# Search for top 1 relevant chunk
D, I = index.search(question_embedding, k=1)
retrieved_text = corpus[I[0][0]]

# Prepare prompt
prompt = (
    "You are an export and trade advisor.\n"
    f"Context:\n{retrieved_text}\n\n"
    f"Question: {question}\n"
    "Answer:"
)

# Encode prompt
input_ids = tokenizer.encode(prompt, return_tensors="pt")

# Generate output
with torch.no_grad():
    output_ids = model.generate(
        input_ids,
        max_length=150,
        num_return_sequences=1,
        no_repeat_ngram_size=2,
        do_sample=True,
        temperature=0.7
    )

# Decode and print
output_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
print("\n--- Response ---\n")
print(output_text)
