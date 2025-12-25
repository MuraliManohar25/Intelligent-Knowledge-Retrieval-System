"""Generate embeddings using Sentence Transformers."""
from sentence_transformers import SentenceTransformer
from typing import List, Dict
import numpy as np
import logging

logger = logging.getLogger(__name__)

class DocumentEmbedder:
    """Generate embeddings for text chunks."""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        logger.info("Model loaded successfully")
    
    def embed_chunks(self, chunks: List[Dict]) -> List[Dict]:
        """
        Generate embeddings for all chunks.
        
        Args:
            chunks: List of chunk dicts with text
            
        Returns:
            Same chunks with added 'embedding' field
        """
        texts = [chunk['text'] for chunk in chunks]
        
        logger.info(f"Generating embeddings for {len(texts)} chunks...")
        embeddings = self.model.encode(
            texts,
            show_progress_bar=True,
            batch_size=32
        )
        
        # Add embeddings to chunks
        for chunk, embedding in zip(chunks, embeddings):
            chunk['embedding'] = embedding.tolist()
        
        logger.info("Embeddings generated successfully")
        return chunks
    
    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a search query.
        
        Args:
            query: Search query string
            
        Returns:
            Embedding vector
        """
        embedding = self.model.encode(query)
        return embedding.tolist()

# Test function
if __name__ == "__main__":
    embedder = DocumentEmbedder()
    test_chunks = [
        {'chunk_id': '1', 'text': 'This is a test chunk about insurance policies.'},
        {'chunk_id': '2', 'text': 'This chunk discusses flood damage coverage.'}
    ]
    embedded = embedder.embed_chunks(test_chunks)
    print(f"Embedding dimension: {len(embedded[0]['embedding'])}")
    print(f"First 5 values: {embedded[0]['embedding'][:5]}")

