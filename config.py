"""Configuration settings for the knowledge retrieval system."""
import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
DOCUMENTS_DIR = DATA_DIR / "documents"
CHROMA_DB_DIR = PROJECT_ROOT / "chroma_db"

# Embedding model settings
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384

# Chunking settings
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100

# Retrieval settings
TOP_K_RESULTS = 5
MIN_SIMILARITY_SCORE = 0.5

# ChromaDB settings
COLLECTION_NAME = "appian_documents"

# Ensure directories exist
DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DB_DIR.mkdir(parents=True, exist_ok=True)

