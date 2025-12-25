"""PDF document loader with page-level extraction."""
import PyPDF2
from pathlib import Path
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFLoader:
    """Load and extract text from PDF documents."""
    
    def __init__(self, documents_dir: Path):
        self.documents_dir = Path(documents_dir)
    
    def load_pdf(self, pdf_path: Path) -> List[Dict[str, any]]:
        """
        Load a single PDF and extract text page by page.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of dicts with page_num and text
        """
        pages = []
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                
                logger.info(f"Loading {pdf_path.name}: {num_pages} pages")
                
                for page_num in range(num_pages):
                    try:
                        page = pdf_reader.pages[page_num]
                        text = page.extract_text()
                        
                        if text.strip():  # Only add if text exists
                            pages.append({
                                'page_num': page_num + 1,  # 1-indexed
                                'text': text,
                                'source_file': pdf_path.name
                            })
                    except Exception as e:
                        logger.warning(f"Error extracting page {page_num + 1}: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error loading PDF {pdf_path}: {e}")
            return []
        
        logger.info(f"Successfully loaded {len(pages)} pages from {pdf_path.name}")
        return pages
    
    def load_all_pdfs(self) -> Dict[str, List[Dict]]:
        """
        Load all PDF files from documents directory.
        
        Returns:
            Dict mapping filename to list of page dicts
        """
        all_documents = {}
        pdf_files = list(self.documents_dir.glob("*.pdf"))
        
        if not pdf_files:
            logger.warning(f"No PDF files found in {self.documents_dir}")
            return {}
        
        logger.info(f"Found {len(pdf_files)} PDF files")
        
        for pdf_path in pdf_files:
            pages = self.load_pdf(pdf_path)
            if pages:
                all_documents[pdf_path.name] = pages
        
        return all_documents

# Test function
if __name__ == "__main__":
    from config import DOCUMENTS_DIR
    loader = PDFLoader(DOCUMENTS_DIR)
    docs = loader.load_all_pdfs()
    print(f"Loaded {len(docs)} documents")
    for doc_name, pages in docs.items():
        print(f"  {doc_name}: {len(pages)} pages")

