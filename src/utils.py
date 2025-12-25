"""Utility functions for the knowledge retrieval system."""
import re
from typing import List, Dict
from datetime import datetime

def clean_text(text: str) -> str:
    """Clean and normalize text."""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep punctuation
    text = re.sub(r'[^\w\s.,!?;:\-\(\)]', '', text)
    return text.strip()

def generate_chunk_id(doc_name: str, page_num: int, chunk_idx: int) -> str:
    """Generate unique ID for a chunk."""
    clean_name = re.sub(r'[^\w]', '_', doc_name)
    return f"{clean_name}_page{page_num}_chunk{chunk_idx}"

def extract_filename(filepath: str) -> str:
    """Extract filename without extension."""
    return filepath.split('/')[-1].replace('.pdf', '')

def format_confidence(score: float) -> str:
    """Format confidence score as percentage."""
    return f"{score * 100:.1f}%"

def truncate_text(text: str, max_length: int = 200) -> str:
    """Truncate text to specified length."""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

