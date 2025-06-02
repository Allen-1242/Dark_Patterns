from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json

# Load embedding model and index
model = SentenceTransformer('all-MiniLM-L6-v2')
index = faiss.read_index("bait_switch_index.faiss")
with open("bait_switch_texts.index.json", "r") as f:
    corpus = json.load(f)

def retrieve_context(query, top_k=3):
    embedding = model.encode([query])
    D, I = index.search(np.array(embedding), top_k)
    return [corpus[i] for i in I[0]]

# Quick test
if __name__ == "__main__":
    test_query = "Clicking Cancel opened a subscription popup"
    print("Query:", test_query)
    print("Top Matches:")
    for match in retrieve_context(test_query):
        print("-", match)
