"""Text chunking with overlap for better context preservation."""
from typing import List, Dict
from langchain_text_splitters import RecursiveCharacterTextSplitter
import logging

logger = logging.getLogger(__name__)

class TextChunker:
    """Chunk text into smaller pieces with overlap."""
    
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def chunk_document(self, pages: List[Dict]) -> List[Dict]:
        """
        Chunk a document's pages into smaller pieces.
        
        Args:
            pages: List of page dicts with page_num and text
            
        Returns:
            List of chunk dicts with metadata
        """
        all_chunks = []
        
        for page in pages:
            page_num = page['page_num']
            text = page['text']
            source_file = page['source_file']
            
            # Split text into chunks
            chunks = self.splitter.split_text(text)
            
            # Create chunk objects with metadata
            for idx, chunk_text in enumerate(chunks):
                if len(chunk_text.strip()) < 50:  # Skip very short chunks
                    continue
                    
                chunk_obj = {
                    'chunk_id': f"{source_file}_page{page_num}_chunk{idx}",
                    'text': chunk_text,
                    'page_num': page_num,
                    'source_file': source_file,
                    'chunk_index': idx,
                    'chunk_length': len(chunk_text)
                }
                all_chunks.append(chunk_obj)
        
        logger.info(f"Created {len(all_chunks)} chunks from {len(pages)} pages")
        return all_chunks
    
    def chunk_all_documents(self, documents: Dict[str, List[Dict]]) -> List[Dict]:
        """
        Chunk all documents.
        
        Args:
            documents: Dict mapping filename to list of pages
            
        Returns:
            List of all chunks from all documents
        """
        all_chunks = []
        
        for doc_name, pages in documents.items():
            chunks = self.chunk_document(pages)
            all_chunks.extend(chunks)
            logger.info(f"  {doc_name}: {len(chunks)} chunks")
        
        logger.info(f"Total chunks created: {len(all_chunks)}")
        return all_chunks

# Test function
if __name__ == "__main__":
    chunker = TextChunker()
    sample_pages = [
        {
            'page_num': 1,
            'text': "This is a sample text. " * 100,
            'source_file': 'test.pdf'
        }
    ]
    chunks = chunker.chunk_document(sample_pages)
    print(f"Created {len(chunks)} chunks")
    print(f"First chunk: {chunks[0]['text'][:100]}...")

