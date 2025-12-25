"""ChromaDB client for vector storage and retrieval."""
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ChromaDBClient:
    """Manage ChromaDB operations."""
    
    def __init__(self, db_path: Path, collection_name: str = "appian_documents"):
        self.db_path = Path(db_path)
        self.collection_name = collection_name
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(collection_name)
            logger.info(f"Loaded existing collection: {collection_name}")
        except:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Created new collection: {collection_name}")
    
    def add_documents(self, chunks: List[Dict]) -> None:
        """
        Add document chunks to the collection.
        
        Args:
            chunks: List of chunk dicts with embeddings and metadata
        """
        if not chunks:
            logger.warning("No chunks to add")
            return
        
        ids = [chunk['chunk_id'] for chunk in chunks]
        embeddings = [chunk['embedding'] for chunk in chunks]
        documents = [chunk['text'] for chunk in chunks]
        metadatas = [
            {
                'source_file': chunk['source_file'],
                'page_num': chunk['page_num'],
                'chunk_index': chunk.get('chunk_index', 0)
            }
            for chunk in chunks
        ]
        
        # Add to collection in batches
        batch_size = 100
        for i in range(0, len(ids), batch_size):
            batch_end = min(i + batch_size, len(ids))
            
            self.collection.add(
                ids=ids[i:batch_end],
                embeddings=embeddings[i:batch_end],
                documents=documents[i:batch_end],
                metadatas=metadatas[i:batch_end]
            )
            logger.info(f"Added batch {i//batch_size + 1}: {batch_end - i} chunks")
        
        logger.info(f"Successfully added {len(ids)} chunks to collection")
    
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filters: Optional[Dict] = None
    ) -> Dict:
        """
        Search for similar documents.
        
        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            filters: Optional metadata filters
            
        Returns:
            Search results with documents and metadata
        """
        where = filters if filters else None
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where
        )
        
        return results
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the collection."""
        count = self.collection.count()
        return {
            'collection_name': self.collection_name,
            'document_count': count
        }
    
    def reset_collection(self) -> None:
        """Delete and recreate the collection."""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        logger.info(f"Reset collection: {self.collection_name}")

# Test function
if __name__ == "__main__":
    from config import CHROMA_DB_DIR, COLLECTION_NAME
    client = ChromaDBClient(CHROMA_DB_DIR, COLLECTION_NAME)
    stats = client.get_collection_stats()
    print(f"Collection stats: {stats}")

