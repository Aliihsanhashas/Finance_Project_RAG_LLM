"""
Vectordb fonksiyonları
"""


# !arch -arm64 pip install python-docx
# !arch -arm64 pip install chromadb -U

import chromadb
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
from docx import Document

# embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2") # this is used by default

chromadb_dir = "chromadb_store"

chroma_client =   chromadb.PersistentClient(path=chromadb_dir)
try:
    collection = chroma_client.create_collection(name="KAP")
except:
    pass