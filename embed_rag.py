from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json

# Load corpus
with open("bait_switch_texts.json", "r") as f:
    texts = json.load(f)

# Load embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(texts, convert_to_numpy=True)

# Build FAISS index
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)

# Save index + text
faiss.write_index(index, "bait_switch_index.faiss")
with open("bait_switch_texts.index.json", "w") as f:
    json.dump(texts, f)
