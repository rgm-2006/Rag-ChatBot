# -----------------------------
# IMPORTING LIBRARIES
# -----------------------------
import numpy as np
import faiss
import requests
from sentence_transformers import SentenceTransformer

# -----------------------------
# LOAD DOCUMENT
# -----------------------------
with open("data/ai_notes.txt", "r", encoding="utf-8") as file:

    text = file.read()

print("\nDOCUMENT LOADED SUCCESSFULLY\n")

text = text.replace("\n", " ")

# -----------------------------
# CHUNKING
# -----------------------------
chunk_size = 300

words = text.split()

chunks = []

current_chunk = []

current_length = 0

for word in words:

    current_chunk.append(word)

    current_length += len(word) + 1

    if current_length >= chunk_size:

        chunks.append(" ".join(current_chunk))

        current_chunk = []

        current_length = 0

if current_chunk:

    chunks.append(" ".join(current_chunk))

print("TOTAL CHUNKS CREATED:", len(chunks))

# -----------------------------
# LOAD EMBEDDING MODEL
# -----------------------------
print("\nLOADING EMBEDDING MODEL...\n")

embedding_model = SentenceTransformer(
    'paraphrase-MiniLM-L3-v2'
)

print("MODEL LOADED SUCCESSFULLY!\n")

# -----------------------------
# CREATE EMBEDDINGS
# -----------------------------
chunk_embeddings = embedding_model.encode(chunks)

print("EMBEDDINGS GENERATED SUCCESSFULLY")

# -----------------------------
# FAISS VECTOR DATABASE
# -----------------------------
print("\nCREATING FAISS INDEX...\n")

embeddings = np.array(
    chunk_embeddings
).astype('float32')

dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(dimension)

index.add(embeddings)

print("FAISS INDEX CREATED SUCCESSFULLY")

# -----------------------------
# OLLAMA FUNCTION
# -----------------------------
print("\nLOADING OLLAMA LLM...\n")

def generate_answer(prompt):

    response = requests.post(
        "http://localhost:11434/api/generate",

        json={
            "model": "tinyllama",

            "prompt": prompt,

            "stream": False
        }
    )

    return response.json()["response"]

print("OLLAMA READY!\n")

# -----------------------------
# RAG SYSTEM
# -----------------------------
print("\nRAG RETRIEVER READY!\n")

while True:

    query = input(
        "\nAsk a question (or type 'exit'): "
    )

    # -------------------------
    # EXIT CONDITION
    # -------------------------
    if query.lower() == "exit":

        print("\nExiting RAG System...\n")

        break

    # -------------------------
    # QUERY EMBEDDING
    # -------------------------
    query_embedding = embedding_model.encode(
        [query]
    ).astype('float32')

    # -------------------------
    # FAISS SEARCH
    # -------------------------
    k = 3

    distances, indices = index.search(
        query_embedding,
        k
    )

    # -------------------------
    # CONTEXT BUILDING
    # -------------------------
    context = ""

    for i in indices[0]:

        context += chunks[i] + "\n"

    # -------------------------
    # PROMPT
    # -------------------------
    input_text = f"""
You are a helpful AI assistant.

Use ONLY the context below to answer the question.

If the answer is not in the context,
say "I don't know based on the given context."

Context:
{context}

Question:
{query}

Answer in 4-5 concise sentences.
Keep the answer clear and direct.
Do not repeat information.
"""

    # -------------------------
    # GENERATE ANSWER
    # -------------------------
    print("\nGENERATING ANSWER...\n")

    answer = generate_answer(input_text)

    # -------------------------
    # FINAL OUTPUT
    # -------------------------
    print("---------------------------")

    print("AI GENERATED ANSWER")

    print("---------------------------\n")

    print(answer)