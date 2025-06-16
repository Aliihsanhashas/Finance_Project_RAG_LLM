"""
Vectordb fonksiyonları
"""


# !arch -arm64 pip install python-docx
# !arch -arm64 pip install chromadb -U

import os
import chromadb
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
from docx import Document
import uuid

# embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2") # this is used by default

chromadb_dir = "chromadb_store"

chroma_client =   chromadb.PersistentClient(path=chromadb_dir)

if "KAP" in [c.name for c in chroma_client.list_collections()]:
    collection = chroma_client.get_collection(name="KAP")
else:
    collection = chroma_client.get_or_create_collection(name="KAP")



    def chunk_text(text, chunk_size=300):
        """Chunk text every chunk_size words."""
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size):
            chunk_words = words[i:i+chunk_size]
            chunk_text = " ".join(chunk_words)
            start = i
            end = i + len(chunk_words)
            chunks.append((chunk_text, start, end))
        return chunks


    def read_docx(file_path):
        """Reads text from a .docx file."""
        try:
            doc = Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None
        


    def read_txt(file_path):
        """Reads text from a .txt file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None

    documents = []
    ids = []
    metadatas = []

    for root, _, files in os.walk(chromadb_dir):
        for file in files:
            if file.endswith(".txt") or file.endswith(".docx"):
                file_path = os.path.join(root, file)
                if file.endswith(".txt"):
                    text = read_txt(file_path)

                if text:
                    relative_path = os.path.relpath(file_path, chromadb_dir)
                    chunks = chunk_text(text, chunk_size=300)
                    for chunk_text_content, start, end in chunks:
                        documents.append(chunk_text_content)
                        ids.append(str(uuid.uuid4()))
                        # Metadata: dir/filename + chunk range
                        metadatas.append({
                            "file_chunk": f"{relative_path}_{start}-{end}"
                        })

    if documents:
        collection.add(documents=documents, ids=ids, metadatas=metadatas)
        print(f"Added {len(documents)} documents to the 'KAP' collection with chunk metadata.")
    else:
        print("No valid documents found.")
