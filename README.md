# RAG System: Document Chat with Local LLMs

A complete **Retrieval-Augmented Generation (RAG)** system that lets you chat with your own documents using a local LLM. Built with Python (LangChain + ChromaDB), FastAPI backend, and React frontend.

## 🎯 Features

### Core RAG Capabilities
- **Agentic RAG**: LLM decides when and how to search documents
- **Multi-Format Support**: PDF, TXT, Markdown, and Web URLs
- **Hybrid Search**: Combines vector similarity with BM25 keyword matching for better recall
- **Source Citations**: See which documents powered the answer
- **Conversation History**: Multi-turn chat with context awareness
- **Document Management**: Upload, list, and delete documents on-the-fly

### Technology Stack

| Component | Technology |
|-----------|-----------|
| **LLM** | Ollama (local models: llama2, llama3.1, mistral, etc.) |
| **Vector Store** | ChromaDB (SQLite-backed, no external DB needed) |
| **Orchestration** | LangChain + ReAct Agent Framework |
| **Embeddings** | Ollama nomic-embed-text |
| **Backend API** | FastAPI + Pydantic |
| **Frontend** | React 18 + Axios |
| **Search** | BM25 + Vector Hybrid Retrieval |

---

## 📋 Prerequisites

- **Python 3.9+**
- **Node.js 16+** (for React frontend)
- **Ollama** installed and running (available at `http://localhost:11434`)
  - Download from [ollama.com](https://ollama.com)
  - Pull required models: `ollama pull llama2` and `ollama pull nomic-embed-text`

### Verify Ollama Setup

```bash
# Start Ollama (if not already running)
ollama serve

# In another terminal, test:
ollama list  # Should show your models

# Test embedding model
curl -X POST http://localhost:11434/api/embeddings \
  -H "Content-Type: application/json" \
  -d '{"model": "nomic-embed-text", "prompt": "test"}'
```

---

## 🚀 Quick Start

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\Activate.ps1

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Optional: Create .env file (uses defaults if omitted)
cp .env.example .env

# Start backend server
python app.py
```

**Backend will run on** `http://localhost:8000`

Check health: `curl http://localhost:8000/api/health`

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

**Frontend will open** `http://localhost:3000`

### 3. Using the System

1. **Upload Documents**
   - Drag & drop PDF, TXT, or Markdown files
   - Documents are automatically split into chunks and embedded

2. **Ask Questions**
   - Type questions about your documents
   - Agent decides whether to search or respond
   - Answers cite their sources

3. **Manage Documents**
   - View all indexed documents
   - Delete individual documents or clear all

---

## 📁 Project Structure

```
rag-system/
├── backend/
│   ├── app.py                     # FastAPI application entry point
│   ├── config.py                  # Configuration & settings
│   ├── requirements.txt           # Python dependencies
│   ├── .env.example               # Environment template
│   ├── core/
│   │   ├── document_loader.py     # Load PDFs, text, URLs
│   │   ├── text_splitter.py       # Chunk documents
│   │   └── embeddings.py          # Ollama embeddings
│   ├── rag/
│   │   ├── vector_store.py        # ChromaDB operations
│   │   ├── retriever.py           # Hybrid search (vector + BM25)
│   │   ├── agent.py               # Agentic RAG with LangChain
│   │   └── prompt_templates.py    # System & context prompts
│   ├── api/
│   │   ├── routes.py              # REST endpoints
│   │   └── models.py              # Pydantic request/response schemas
│   ├── services/
│   │   ├── document_service.py    # Document processing logic
│   │   └── chat_service.py        # Chat session management
│   └── storage/
│       └── chroma/                # ChromaDB persistent storage
├── frontend/
│   ├── package.json               # React dependencies
│   ├── public/index.html          # HTML template
│   ├── src/
│   │   ├── App.js                 # Main React component
│   │   ├── App.css                # Styling
│   │   ├── index.js               # React entry point
│   │   ├── api/
│   │   │   └── client.js          # API client (axios)
│   │   └── components/
│   │       ├── ChatWindow.js       # Chat interface
│   │       └── DocumentManager.js  # Document upload/list
│   └── README.md
└── README.md (this file)
```

---

## 🔧 Configuration

### Backend Settings (backend/config.py)

All settings read from environment variables with defaults:

```python
# Ollama
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_LLM_MODEL = "llama2"  # or "llama3.1", "mistral", etc.
OLLAMA_EMBEDDING_MODEL = "nomic-embed-text"
OLLAMA_REQUEST_TIMEOUT = 300  # 5 minutes

# ChromaDB
CHROMA_DB_PATH = "./storage/chroma"
CHROMA_COLLECTION_NAME = "documents"

# Text Processing
CHUNK_SIZE = 1000  # Characters per chunk
CHUNK_OVERLAP = 200  # 20% overlap

# Retrieval
RETRIEVAL_K = 3  # Documents to retrieve
HYBRID_SEARCH_ENABLED = True
BM25_WEIGHT = 0.5  # Weight for keyword search
VECTOR_WEIGHT = 0.5  # Weight for vector search

# Agent
MAX_CONVERSATION_HISTORY = 10
AGENT_MAX_ITERATIONS = 10
AGENT_TEMPERATURE = 0.7

# FastAPI
API_HOST = "0.0.0.0"
API_PORT = 8000
FRONTEND_URL = "http://localhost:3000"
```

Override in `.env` file:

```bash
OLLAMA_LLM_MODEL=llama3.1
CHUNK_SIZE=2000
RETRIEVAL_K=5
```

---

## 📚 API Endpoints

### Chat
- **POST** `/api/chat` - Send message, get response + sources
- **GET** `/api/chat/history/{session_id}` - Get conversation history

### Documents
- **POST** `/api/documents/upload` - Upload document file
- **GET** `/api/documents` - List all indexed documents
- **DELETE** `/api/documents/{doc_id}` - Delete specific document
- **POST** `/api/documents/clear` - Clear all documents

### System
- **GET** `/api/health` - Health check
- **GET** `/api/status` - System status with service states

### Interactive API Docs
Visit `http://localhost:8000/docs` (Swagger UI) or `http://localhost:8000/redoc` (ReDoc)

---

## 🔄 Architecture

### Document Processing Pipeline

```
Upload File
    ↓
[Document Loader] → Detect format (PDF/TXT/MD/URL)
    ↓
[Text Splitter] → Break into chunks (1000 chars, 20% overlap)
    ↓
[Embeddings] → Convert to vectors (Ollama nomic-embed-text)
    ↓
[Vector Store] → Store in ChromaDB with metadata
    ↓
Ready for retrieval
```

### Chat Pipeline

```
User Message
    ↓
[RAG Agent] → Decide: search documents or respond?
    ↓
[Retriever] → Hybrid search (vector + BM25)
    ↓
[Context Formatting] → Build prompt with retrieved docs
    ↓
[LLM] → Generate response (Ollama)
    ↓
Return response + sources
```

---

## 🧪 Testing

### Backend Tests

```bash
cd backend

# Test embeddings initialization
python -c "from core.embeddings import initialize_embeddings; emb = initialize_embeddings(); print('✓ Embeddings working')"

# Test document loading
python -c "from core.document_loader import DocumentLoader; docs = DocumentLoader.load_document('test.txt'); print(f'Loaded {len(docs)} docs')"

# Test vector store
python -c "from rag.vector_store import initialize_vector_store; vs = initialize_vector_store(); print(vs.get_collection_info())"
```

### Manual API Testing

```bash
# Health check
curl http://localhost:8000/api/health

# Send message
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, what documents do I have?",
    "session_id": "test-session"
  }'

# Upload document
curl -F "file=@document.pdf" \
  http://localhost:8000/api/documents/upload

# List documents
curl http://localhost:8000/api/documents
```

---

## 🐛 Troubleshooting

### Ollama Connection Issues

```
Error: "Ollama connection failed"
```

**Solution:**
```bash
# Ensure Ollama is running
ollama serve

# Check connection
curl http://localhost:11434/api/tags

# Verify model is available
ollama list
ollama pull llama2 nomic-embed-text
```

### Import Errors in Python

```
ModuleNotFoundError: No module named 'langchain'
```

**Solution:**
```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate  # macOS/Linux

# Reinstall dependencies
pip install -r requirements.txt
```

### React Cannot Connect to Backend

```
Error: Failed to send message (CORS, 404, etc.)
```

**Solution:**
1. Verify backend running: `curl http://localhost:8000/api/health`
2. Check CORS settings in `backend/app.py` (should include localhost:3000)
3. Set API URL in frontend env: `REACT_APP_API_URL=http://localhost:8000/api npm start`

### Vector Store Errors

```
Error: Collection not found
```

**Solution:**
```bash
# ChromaDB data persists in storage/chroma/
# Delete and rebuild:
rm -rf backend/storage/chroma
# Restart backend - new collection created on startup
```

---

## 🚀 Deployment

### Docker Deployment (Future)

```dockerfile
# Example Dockerfile for backend
FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ .
CMD ["python", "app.py"]
```

### Production Considerations

1. **Database**: Upgrade from in-memory session storage to PostgreSQL
2. **Vector Store**: Use managed ChromaDB or Pinecone for scaling
3. **LLM**: Consider API-based models (OpenAI, Anthropic) for higher throughput
4. **Monitoring**: Add logging, metrics, and tracing (e.g., OpenTelemetry)
5. **Security**: Add authentication, rate limiting, input validation
6. **Caching**: Cache embeddings to avoid recomputation

---

## 📈 Performance Tips

1. **Chunk Size**: Larger chunks (1500-2000) contain more context, smaller chunks (500) are more precise
2. **Retrieval K**: Start with k=3, increase if answers are incomplete
3. **Hybrid Search Weights**: Adjust BM25_WEIGHT and VECTOR_WEIGHT for your data
4. **Ollama Models**: Faster: `mistral` (7B), `neural-chat` (7B) | Better: `llama3.1` (8B)
5. **Batch Processing**: Load multiple documents at once for efficiency

---

## 📝 License

MIT

---

## 🤝 Contributing

Contributions welcome! Areas for enhancement:
- Advanced retrieval: metadata filtering, MMR, hybrid ranking
- UI improvements: markdown rendering, code highlighting, dark mode
- Backend: async processing, document versioning, query optimization
- Testing: unit tests, integration tests, load testing

---

## 📚 References

- [LangChain Documentation](https://python.langchain.com)
- [ChromaDB Guide](https://docs.trychroma.com)
- [Ollama Models](https://ollama.ai/library)
- [FastAPI Docs](https://fastapi.tiangolo.com)
- [RAG Papers & Research](https://arxiv.org/search/?query=retrieval+augmented+generation)

---

## 🎓 Learning Resources

This implementation demonstrates:
- Agentic reasoning with ReAct pattern
- Vector databases and embeddings
- Hybrid search combining dense and sparse retrieval
- FastAPI REST API design
- React state management and async operations
- Context window management for LLMs
- Session-based conversation memory

Perfect for learning RAG concepts or as a foundation for production systems!

---

**Built with ❤️ for document intelligence**
