"""Streamlit UI for the Intelligent Knowledge Retrieval System."""
import streamlit as st
import json
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.database.chroma_client import ChromaDBClient
from src.ingest.embedder import DocumentEmbedder
from src.retrieval.search import RetrievalEngine
from config import (
    CHROMA_DB_DIR,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
    DATA_DIR
)

# Page configuration
st.set_page_config(
    page_title="Knowledge Retrieval System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stAlert {
        padding: 1rem;
        margin: 1rem 0;
    }
    .document-card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        margin: 1rem 0;
        background-color: #f8f9fa;
    }
    .confidence-high {
        color: #28a745;
        font-weight: bold;
    }
    .confidence-medium {
        color: #ffc107;
        font-weight: bold;
    }
    .confidence-low {
        color: #dc3545;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_resource
def initialize_system():
    """Initialize the retrieval system (cached)."""
    try:
        db_client = ChromaDBClient(CHROMA_DB_DIR, COLLECTION_NAME)
        embedder = DocumentEmbedder(EMBEDDING_MODEL)
        engine = RetrievalEngine(db_client, embedder)
        return engine, db_client
    except Exception as e:
        st.error(f"Error initializing system: {e}")
        return None, None

def load_mock_cases():
    """Load mock cases from JSON."""
    try:
        with open(DATA_DIR / "mock_cases.json", 'r') as f:
            data = json.load(f)
            return data['cases']
    except:
        return []

def display_document(doc, rank):
    """Display a single document result."""
    # Confidence color
    conf_class = f"confidence-{doc['confidence'].lower()}"
    
    # Create expandable card
    with st.expander(
        f"📄 **{rank}. {doc['source_file']}** - Page {doc['page_number']} "
        f"(Confidence: {doc['confidence']})",
        expanded=(rank == 1)
    ):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"**Excerpt:**")
            st.write(doc['excerpt'])
            
            st.markdown(f"**Citation:**")
            st.info(f"📍 {doc['citation']['location']} - {doc['source_file']}")
        
        with col2:
            st.metric("Relevance", f"{doc['relevance_score']:.1%}")
            st.metric("Similarity", f"{doc['similarity_score']:.1%}")
            
            if st.button("📖 View Full Text", key=f"view_{doc['chunk_id']}"):
                st.session_state[f"show_full_{doc['chunk_id']}"] = True
        
        # Show full text if requested
        if st.session_state.get(f"show_full_{doc['chunk_id']}", False):
            st.markdown("---")
            st.markdown("**Full Text:**")
            st.text_area(
                "Full content",
                doc['full_text'],
                height=200,
                key=f"full_{doc['chunk_id']}",
                label_visibility="collapsed"
            )

def main():
    """Main application."""
    
    # Header
    st.title("📚 Intelligent Knowledge Retrieval System")
    st.markdown("*Context-aware document suggestions for case management*")
    st.markdown("---")
    
    # Initialize system
    with st.spinner("Initializing system..."):
        engine, db_client = initialize_system()
    
    if engine is None:
        st.error("Failed to initialize system. Please run main.py first to ingest documents.")
        return
    
    # Show database stats
    stats = db_client.get_collection_stats()
    if stats['document_count'] == 0:
        st.warning("⚠️ No documents in database. Please run `python main.py` to ingest documents first.")
        return
    
    # Sidebar - Case Input
    with st.sidebar:
        st.header("📋 Active Case")
        
        # Load mock cases
        mock_cases = load_mock_cases()
        
        # Option to load mock case
        if mock_cases:
            load_mock = st.checkbox("Load Mock Case", value=False)
            if load_mock:
                selected_case = st.selectbox(
                    "Select Case",
                    options=range(len(mock_cases)),
                    format_func=lambda i: f"{mock_cases[i]['case_id']} - {mock_cases[i]['claim_type']}"
                )
                case = mock_cases[selected_case]
            else:
                case = None
        else:
            case = None
        
        st.markdown("---")
        
        # Case input form
        case_id = st.text_input(
            "Case ID",
            value=case['case_id'] if case else "CLM-2024-00123"
        )
        
        claim_type = st.selectbox(
            "Claim Type",
            options=["Flood", "Fire", "Hurricane", "Theft", "Water Damage", "Wind Damage"],
            index=0 if not case else ["Flood", "Fire", "Hurricane", "Theft", "Water Damage"].index(case['claim_type']) if case['claim_type'] in ["Flood", "Fire", "Hurricane", "Theft", "Water Damage"] else 0
        )
        
        state = st.selectbox(
            "State",
            options=["Florida", "Texas", "California", "New York", "Georgia"],
            index=0 if not case else ["Florida", "Texas", "California", "New York"].index(case['state']) if case['state'] in ["Florida", "Texas", "California", "New York"] else 0
        )
        
        property_type = st.selectbox(
            "Property Type",
            options=["Residential", "Commercial"],
            index=0 if not case else (["Residential", "Commercial"].index(case['property_type']) if case['property_type'] in ["Residential", "Commercial"] else 0)
        )
        
        claim_amount = st.number_input(
            "Claim Amount ($)",
            min_value=0,
            max_value=1000000,
            value=case['claim_amount'] if case else 50000,
            step=5000
        )
        
        date_filed = st.date_input(
            "Date Filed",
            value=None
        )
        
        st.markdown("---")
        
        # Search button
        search_button = st.button("🔍 Find Relevant Documents", type="primary", use_container_width=True)
        
        st.markdown("---")
        st.caption(f"📊 Database: {stats['document_count']} chunks indexed")
    
    # Main content area
    if search_button:
        # Build case data
        case_data = {
            'case_id': case_id,
            'claim_type': claim_type,
            'state': state,
            'property_type': property_type,
            'claim_amount': claim_amount,
            'date_filed': str(date_filed) if date_filed else None
        }
        
        # Show case summary
        st.subheader("📋 Case Summary")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Claim Type", claim_type)
        col2.metric("State", state)
        col3.metric("Property", property_type)
        col4.metric("Amount", f"${claim_amount:,}")
        
        st.markdown("---")
        
        # Perform search
        with st.spinner("🔍 Searching for relevant documents..."):
            results = engine.retrieve_documents(case_data, top_k=5)
        
        # Display results
        if results:
            st.subheader(f"📚 Found {len(results)} Relevant Documents")
            st.markdown("Documents are ranked by relevance to your case.")
            
            for doc in results:
                display_document(doc, doc['rank'])
        else:
            st.warning("No relevant documents found. Try adjusting the case parameters.")
    
    else:
        # Welcome message
        st.info("👈 Enter case details in the sidebar and click 'Find Relevant Documents' to get started.")
        
        # Show example
        st.subheader("How it works:")
        st.markdown("""
        1. **Enter case details** in the sidebar (or load a mock case)
        2. **Click search** to find relevant documents
        3. **View suggestions** with citations to exact pages
        4. **Expand documents** to see full text and citations
        
        The system uses AI to understand your case context and automatically suggests 
        the most relevant policies, procedures, and regulations.
        """)

if __name__ == "__main__":
    main()

