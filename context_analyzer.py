"""Extract and analyze context from case data."""
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class ContextAnalyzer:
    """Analyze case data and extract search context."""
    
    def __init__(self):
        self.field_weights = {
            'claim_type': 0.3,
            'state': 0.25,
            'property_type': 0.2,
            'claim_amount': 0.15,
            'date_filed': 0.1
        }
    
    def extract_context(self, case_data: Dict) -> Dict:
        """
        Extract relevant context from case data.
        
        Args:
            case_data: Case information dict
            
        Returns:
            Structured context for retrieval
        """
        context = {
            'query': self._build_query(case_data),
            'filters': self._build_filters(case_data),
            'boost_fields': self._identify_boost_fields(case_data),
            'raw_case': case_data
        }
        
        logger.info(f"Extracted context - Query: {context['query']}")
        return context
    
    def _build_query(self, case_data: Dict) -> str:
        """Build natural language query from case data."""
        query_parts = []
        
        if 'claim_type' in case_data:
            query_parts.append(case_data['claim_type'])
        
        if 'state' in case_data:
            query_parts.append(f"in {case_data['state']}")
        
        if 'property_type' in case_data:
            query_parts.append(f"for {case_data['property_type']} property")
        
        if 'claim_amount' in case_data:
            amount = case_data['claim_amount']
            if amount < 50000:
                query_parts.append("small claim")
            elif amount < 200000:
                query_parts.append("medium claim")
            else:
                query_parts.append("large claim")
        
        query = " ".join(query_parts) if query_parts else "general insurance claim"
        return query
    
    def _build_filters(self, case_data: Dict) -> Optional[Dict]:
        """Build metadata filters for search."""
        filters = {}
        
        # Note: ChromaDB filtering is limited, so we keep it simple
        # More complex filtering can be done post-retrieval
        
        return filters if filters else None
    
    def _identify_boost_fields(self, case_data: Dict) -> List[str]:
        """Identify which fields should boost relevance."""
        boost_fields = []
        
        if 'claim_type' in case_data:
            boost_fields.append('claim_type')
        if 'state' in case_data:
            boost_fields.append('state')
        
        return boost_fields

# Test function
if __name__ == "__main__":
    analyzer = ContextAnalyzer()
    test_case = {
        'case_id': 'CLM-123',
        'claim_type': 'Flood',
        'state': 'Florida',
        'property_type': 'Residential',
        'claim_amount': 50000
    }
    context = analyzer.extract_context(test_case)
    print(f"Query: {context['query']}")
    print(f"Filters: {context['filters']}")

