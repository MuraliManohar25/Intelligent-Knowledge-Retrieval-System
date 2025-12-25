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

# Page configuration (ONLY ONCE, TOP LEVEL)
st.set_page_config(
    page_title="Knowledge Retrieval System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.main { padding: 0rem 1rem; }
.stAlert { padding: 1rem; margin: 1rem 0; }
.confidence-high { color: #28a745; font-weight: bold; }
.confidence-medium { color: #ffc107; font-weight: bold; }
.confidence-low { color: #dc3545; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def initialize_system():
    try:
        db_client = ChromaDBClient(CHROMA_DB_DIR, COLLECTION_NAME)
        embedder = DocumentEmbedder(EMBEDDING_MODEL)
        engine = RetrievalEngine(db_client, embedder)
        return engine, db_client
    except Exception as e:
        st.error(f"Error initializing system: {e}")
        return None, None

def load_mock_cases():
    try:
        with open(DATA_DIR / "mock_cases.json", "r") as f:
            return json.load(f).get("cases", [])
    except:
        return []

def display_document(doc, rank):
    with st.expander(
        f"📄 {rank}. {doc['source_file']} (Confidence: {doc['confidence']})",
        expanded=(rank == 1)
    ):
        st.write(doc["excerpt"])
        st.info(f"📍 {doc['citation']['location']}")

def main():
    st.title("📚 Intelligent Knowledge Retrieval System")
    st.markdown("*Context-aware document suggestions for case management*")
    st.markdown("---")

    # OPTIONAL file upload (safe & correct placement)
    uploaded_files = st.file_uploader(
        "Upload documents (PDF or DOCX)",
        type=["pdf", "docx"],
        accept_multiple_files=True
    )

    with st.spinner("Initializing system..."):
        engine, db_client = initialize_system()

    if engine is None:
        st.error("System initialization failed.")
        return

    stats = db_client.get_collection_stats()
    if stats["document_count"] == 0:
        st.warning("No documents indexed. Run `python main.py` first.")
        return

    with st.sidebar:
        st.header("📋 Active Case")

        case_id = st.text_input("Case ID", "CLM-2024-00123")
        claim_type = st.selectbox("Claim Type", ["Flood", "Fire", "Hurricane"])
        state = st.selectbox("State", ["Florida", "Texas", "California"])
        property_type = st.selectbox("Property Type", ["Residential", "Commercial"])
        claim_amount = st.number_input("Claim Amount", 0, 1_000_000, 50000, step=5000)

        search_button = st.button("🔍 Find Relevant Documents", use_container_width=True)

    if search_button:
        case_data = {
            "case_id": case_id,
            "claim_type": claim_type,
            "state": state,
            "property_type": property_type,
            "claim_amount": claim_amount
        }

        with st.spinner("Searching..."):
            results = engine.retrieve_documents(case_data, top_k=5)

        if results:
            for doc in results:
                display_document(doc, doc["rank"])
        else:
            st.warning("No relevant documents found.")
    else:
        st.info("👈 Enter case details and click search to begin.")

if __name__ == "__main__":
    main()
