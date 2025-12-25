"""Main script to ingest documents and build the knowledge base."""
import logging
from pathlib import Path
from src.ingest.document_loader import DocumentLoader
from src.ingest.chunker import TextChunker
from src.ingest.embedder import DocumentEmbedder
from src.database.chroma_client import ChromaDBClient
from config import (
    DOCUMENTS_DIR,
    CHROMA_DB_DIR,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main ingestion pipeline."""
    logger.info("=" * 60)
    logger.info("STARTING DOCUMENT INGESTION PIPELINE")
    logger.info("=" * 60)
    
    # Step 1: Load documents (PDF and DOCX)
    logger.info("\n[1/5] Loading documents...")
    loader = DocumentLoader(DOCUMENTS_DIR)
    documents = loader.load_all_documents()
    
    if not documents:
        logger.error("Failed to load any documents")
        return
    
    total_pages = sum(len(pages) for pages in documents.values())
    logger.info(f"Loaded {len(documents)} documents with {total_pages} total pages")
    
    # Step 2: Chunk documents
    logger.info("\n[2/5] Chunking documents...")
    chunker = TextChunker(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    chunks = chunker.chunk_all_documents(documents)
    
    if not chunks:
        logger.error("Failed to create chunks")
        return
    
    logger.info(f"Created {len(chunks)} chunks")
    
    # Step 3: Generate embeddings
    logger.info("\n[3/5] Generating embeddings...")
    embedder = DocumentEmbedder(EMBEDDING_MODEL)
    embedded_chunks = embedder.embed_chunks(chunks)
    
    # Step 4: Initialize database
    logger.info("\n[4/5] Initializing ChromaDB...")
    db_client = ChromaDBClient(CHROMA_DB_DIR, COLLECTION_NAME)
    
    # Check if we should reset
    stats = db_client.get_collection_stats()
    if stats['document_count'] > 0:
        logger.warning(f"Collection already contains {stats['document_count']} documents")
        response = input("Reset collection? (yes/no): ").lower()
        if response == 'yes':
            db_client.reset_collection()
            logger.info("Collection reset")
    
    # Step 5: Add to database
    logger.info("\n[5/5] Adding documents to vector database...")
    db_client.add_documents(embedded_chunks)
    
    # Final stats
    final_stats = db_client.get_collection_stats()
    logger.info("\n" + "=" * 60)
    logger.info("INGESTION COMPLETE!")
    logger.info("=" * 60)
    logger.info(f"Collection: {final_stats['collection_name']}")
    logger.info(f"Total documents: {final_stats['document_count']}")
    logger.info(f"Database location: {CHROMA_DB_DIR}")
    logger.info("\nYou can now run the UI with: streamlit run ui/app.py")

if __name__ == "__main__":
    main()

