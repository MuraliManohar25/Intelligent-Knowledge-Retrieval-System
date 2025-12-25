"""Main search and retrieval engine."""
from typing import List, Dict
import logging
from ..database.chroma_client import ChromaDBClient
from ..ingest.embedder import DocumentEmbedder
from .context_analyzer import ContextAnalyzer

logger = logging.getLogger(__name__)

class RetrievalEngine:
    """Main retrieval engine coordinating search operations."""
    
    def __init__(self, db_client: ChromaDBClient, embedder: DocumentEmbedder):
        self.db_client = db_client
        self.embedder = embedder
        self.context_analyzer = ContextAnalyzer()
    
    def retrieve_documents(
        self,
        case_data: Dict,
        top_k: int = 5
    ) -> List[Dict]:
        """
        Retrieve relevant documents for a case.
        
        Args:
            case_data: Case information
            top_k: Number of results to return
            
        Returns:
            List of relevant documents with citations
        """
        # Extract context from case
        context = self.context_analyzer.extract_context(case_data)
        query = context['query']
        filters = context['filters']
        
        logger.info(f"Searching for: {query}")
        
        # Generate query embedding
        query_embedding = self.embedder.embed_query(query)
        
        # Search vector database
        results = self.db_client.search(
            query_embedding=query_embedding,
            top_k=top_k,
            filters=filters
        )
        
        # Format results with citations
        formatted_results = self._format_results(results, case_data)
        
        logger.info(f"Found {len(formatted_results)} relevant documents")
        return formatted_results
    
    def _format_results(self, results: Dict, case_data: Dict) -> List[Dict]:
        """Format search results with citations and metadata."""
        formatted = []
        
        if not results['ids'] or not results['ids'][0]:
            return formatted
        
        for i in range(len(results['ids'][0])):
            doc_id = results['ids'][0][i]
            document = results['documents'][0][i]
            metadata = results['metadatas'][0][i]
            distance = results['distances'][0][i]
            
            # Convert distance to similarity score (cosine)
            similarity = 1 - distance
            
            # Calculate relevance score
            relevance = self._calculate_relevance(
                similarity,
                metadata,
                case_data
            )
            
            formatted_doc = {
                'rank': i + 1,
                'chunk_id': doc_id,
                'source_file': metadata.get('source_file', 'Unknown'),
                'page_number': metadata.get('page_num', 0),
                'excerpt': self._truncate_text(document, 300),
                'full_text': document,
                'similarity_score': round(similarity, 3),
                'relevance_score': round(relevance, 3),
                'confidence': self._calculate_confidence(relevance),
                'citation': self._generate_citation(metadata, document)
            }
            
            formatted.append(formatted_doc)
        
        # Sort by relevance score
        formatted.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return formatted
    
    def _calculate_relevance(
        self,
        similarity: float,
        metadata: Dict,
        case_data: Dict
    ) -> float:
        """Calculate overall relevance score."""
        score = similarity * 0.7  # Base semantic similarity
        
        # Boost for metadata matches
        if 'state' in case_data and 'state' in str(metadata.get('source_file', '')):
            score += 0.15
        
        if 'claim_type' in case_data:
            claim_type = case_data['claim_type'].lower()
            source_file = metadata.get('source_file', '').lower()
            if claim_type in source_file:
                score += 0.15
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _calculate_confidence(self, relevance: float) -> str:
        """Convert relevance to confidence label."""
        if relevance >= 0.8:
            return "High"
        elif relevance >= 0.6:
            return "Medium"
        else:
            return "Low"
    
    def _generate_citation(self, metadata: Dict, text: str) -> Dict:
        """Generate citation information."""
        return {
            'source': metadata.get('source_file', 'Unknown'),
            'page': metadata.get('page_num', 0),
            'location': f"Page {metadata.get('page_num', 0)}",
            'preview': self._truncate_text(text, 150)
        }
    
    def _truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text to specified length."""
        if len(text) <= max_length:
            return text
        return text[:max_length].rsplit(' ', 1)[0] + "..."

# Test function
if __name__ == "__main__":
    from config import CHROMA_DB_DIR, COLLECTION_NAME, EMBEDDING_MODEL
    
    db_client = ChromaDBClient(CHROMA_DB_DIR, COLLECTION_NAME)
    embedder = DocumentEmbedder(EMBEDDING_MODEL)
    engine = RetrievalEngine(db_client, embedder)
    
    test_case = {
        'claim_type': 'Flood',
        'state': 'Florida',
        'claim_amount': 50000
    }
    
    results = engine.retrieve_documents(test_case)
    for result in results:
        print(f"\n{result['rank']}. {result['source_file']} - Page {result['page_number']}")
        print(f"   Confidence: {result['confidence']} ({result['relevance_score']:.2f})")
        print(f"   {result['excerpt']}")

