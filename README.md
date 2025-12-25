# Intelligent Knowledge Retrieval System

An AI-powered document retrieval system that helps case management agents find relevant documentation based on active case context. Built using RAG (Retrieval-Augmented Generation) architecture with vector search.

## 🎯 Problem Statement

Case management agents must consult vast, fragmented documentation libraries (policies, SOPs, regulations) while handling high-stakes cases. Manually searching for relevant documents leads to:
- High average handling times (AHT)
- Compliance errors
- Missed critical policy updates

## 💡 Solution

A "Just-in-Time" knowledge system that:
- Analyzes active case data automatically
- Suggests relevant documents proactively
- Provides verifiable citations (page numbers, sections)
- Uses semantic search to understand context

## 🏗️ Architecture

```
Case Data → Context Analyzer → Vector Search → Relevance Ranking → Suggested Documents with Citations
```

### Components:
1. **Document Ingestion**: PDF loading, chunking, embedding generation
2. **Vector Database**: ChromaDB for semantic search
3. **Retrieval Engine**: Context-aware search with metadata filtering
4. **UI**: Streamlit interface for agents

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd intelligent-knowledge-retrieval
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Add your documents:
```bash
# Place your PDF or DOCX files in data/documents/
# Examples: 
#   data/documents/FL_Flood_Policy.pdf
#   data/documents/COMMERCIAL_PROPERTY_CLAIMS_GUIDELINES.docx
```

4. Run document ingestion:
```bash
python main.py
```

5. Start the UI:
```bash
streamlit run ui/app.py
```

6. Open your browser to `http://localhost:8501`

## 📁 Project Structure

```
intelligent-knowledge-retrieval/
├── src/
│   ├── ingest/          # Document processing
│   ├── database/        # Vector database client
│   └── retrieval/       # Search engine
├── ui/                  # Streamlit interface
├── data/
│   ├── documents/       # Place PDFs here
│   └── mock_cases.json  # Sample cases
├── main.py             # Ingestion pipeline
└── config.py           # Configuration
```

## 💻 Usage

### 1. Ingest Documents
```bash
python main.py
```

### 2. Run the UI
```bash
streamlit run ui/app.py
```

### 3. Enter Case Details
- Select claim type, state, property type
- Enter claim amount
- Click "Find Relevant Documents"

### 4. View Results
- See top 5 relevant documents
- Each result includes:
  - Source document name
  - Exact page number
  - Confidence score
  - Text excerpt
  - Full text (expandable)

## 🔧 Configuration

Edit `config.py` to customize:
- Chunk size and overlap
- Number of results (top_k)
- Embedding model
- Database location

## 📊 Features

- ✅ Semantic search (understands meaning, not just keywords)
- ✅ Context-aware suggestions based on case data
- ✅ Verifiable citations with page numbers
- ✅ Confidence scoring
- ✅ Mock case loading for testing
- ✅ Expandable document views

## 🛠️ Tech Stack

- **Vector DB**: ChromaDB
- **Embeddings**: Sentence-BERT (all-MiniLM-L6-v2)
- **UI**: Streamlit
- **Backend**: Python, FastAPI-ready
- **PDF Processing**: PyPDF2
- **DOCX Processing**: python-docx
- **Text Splitting**: LangChain

## 🧪 Testing

Run with mock cases:
1. Start the UI
2. Check "Load Mock Case"
3. Select a case
4. Click search

## 📝 Assumptions & Limitations

### Assumptions:
- Documents are in PDF or DOCX format (text-based, not scanned)
- English language content
- Structured case data available

### Limitations:
- No multi-language support
- No OCR for scanned documents
- Requires manual re-indexing for new documents
- Mock integration (not connected to real Appian)

## 🔮 Future Enhancements

- Real-time document monitoring
- Agent feedback learning
- Multi-language support
- Conversational interface
- Integration with Appian API
- Mobile app

## 👥 Contributors

[Your Name/Team]

## 📄 License

MIT

## 🤝 Acknowledgments

Built for Appian Hackathon 2024

