# RAG System - Quick Reference

## What This Is

A complete Retrieval-Augmented Generation (RAG) system that lets you chat with your own documents using a local LLM (Ollama).

Stack: Python + LangChain + ChromaDB + Ollama + React

---

## Quick Start (Choose One)

### Option 1: Automatic (Easiest)
```bash
# Windows
cd c:\Users\Arunjweh\Desktop\workspace\rag-system
start.bat

# macOS/Linux  
cd ~/Desktop/workspace/rag-system
chmod +x start.sh
./start.sh
```

### Option 2: Manual (3 terminals)
```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Start Backend
cd rag-system/backend
python -m venv venv
source venv/bin/activate  # or: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py

# Terminal 3: Start Frontend
cd rag-system/frontend
npm install
npm start
```

---

## Access Points

| Component | URL | Purpose |
|-----------|-----|---------|
| Frontend | http://localhost:3000 | Chat with documents |
| API Docs | http://localhost:8000/docs | Swagger documentation |
| API ReDoc | http://localhost:8000/redoc | Alternative API docs |
| Health Check | http://localhost:8000/api/health | System status |

---

## Documentation

| File | Purpose |
|------|---------|
| [README.md](README.md) | Full setup and features guide |
| [IMPLEMENTATION.md](IMPLEMENTATION.md) | Complete technical summary |
| [backend/README.md](backend/README.md) | Backend documentation |
| [frontend/README.md](frontend/README.md) | Frontend documentation |

---

## How to Use

1. **Ensure Ollama is running**: `ollama serve` (in separate terminal)
2. **Start the system**: Run `start.bat` or `start.sh`
3. **Open browser**: http://localhost:3000
4. **Upload documents**: Use the upload zone on the left
5. **Ask questions**: Type in the chat box
6. **View answers**: See responses with source citations

---

## Verify Installation

```bash
# Test backend
cd backend
python healthcheck.py

# Expected output:
# Python Imports       PASS
# Configuration        PASS  
# Storage              PASS
# Ollama               Ready (not running yet is OK)
```

---

## Configuration

Edit `backend/.env` to customize (examples):

```bash
# Use different LLM model
OLLAMA_LLM_MODEL=llama3.1

# Adjust document chunking
CHUNK_SIZE=2000
CHUNK_OVERLAP=400

# Tune retrieval
RETRIEVAL_K=5
BM25_WEIGHT=0.3
VECTOR_WEIGHT=0.7

# Agent reasoning
AGENT_TEMPERATURE=0.8
```

---

## 📋 API Examples

### Chat with Documents
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is this document about?",
    "session_id": "test-session"
  }'
```

### Upload Document
```bash
curl -F "file=@document.pdf" \
  http://localhost:8000/api/documents/upload
```

### List Documents
```bash
curl http://localhost:8000/api/documents
```

### Health Check
```bash
curl http://localhost:8000/api/health
```

---

## 🔍 Project Structure

```
rag-system/
├── backend/               # Python + FastAPI
│   ├── app.py            # Main application
│   ├── config.py         # Settings
│   ├── healthcheck.py    # Validation script
│   ├── core/             # Document processing
│   ├── rag/              # RAG pipeline
│   ├── api/              # REST endpoints
│   ├── services/         # Business logic
│   ├── storage/          # Vector database
│   ├── venv/             # Python environment
│   └── requirements.txt  # Dependencies
├── frontend/             # React web UI
│   ├── src/
│   │   ├── App.js        # Main component
│   │   ├── api/          # API client
│   │   └── components/   # UI components
│   └── package.json      # Dependencies
├── README.md             # Main documentation
├── IMPLEMENTATION.md     # Technical details
├── start.bat             # Windows launcher
└── start.sh              # Unix launcher
```

---

## Key Features

- Multi-format documents: PDF, TXT, Markdown, URLs  
- Intelligent retrieval: Vector + keyword hybrid search  
- Agentic reasoning: LLM decides when to search  
- Chat interface: Real-time messaging  
- Source citations: See document sources  
- Conversation memory: Multi-turn context  
- Document management: Upload, list, delete  
- Persistent storage: Local SQLite database  
- Local-first: No external APIs or internet required  

---

## Troubleshooting

### "Ollama connection failed"
Start Ollama: `ollama serve`
Verify: `curl http://localhost:11434/api/tags`

### "Cannot connect to backend from frontend"
Check backend is running: `curl http://localhost:8000/api/health`
Verify proxy in `frontend/package.json`

### "Python module not found"
Activate venv: `source venv/bin/activate` (Unix) or `.\venv\Scripts\Activate.ps1` (Windows)
Reinstall: `pip install -r requirements.txt`

### "ChromaDB errors"
Delete storage: `rm -rf backend/storage/chroma/`
Restart backend (collection auto-creates)

---

## Technology Summary

| Component | Technology |
|-----------|-----------|
| **LLM** | Ollama (local models) |
| **Embeddings** | nomic-embed-text |
| **Vector DB** | ChromaDB + SQLite |
| **Orchestration** | LangChain 1.2.15 |
| **API** | FastAPI 0.136.0 |
| **Frontend** | React 18.2.0 |
| **Python** | 3.11 (venv) |

---

## Learning Resources

- Learn about RAG: [RAG Papers](https://arxiv.org/search/?query=retrieval+augmented+generation)
- LangChain: [Documentation](https://python.langchain.com)
- ChromaDB: [Guide](https://docs.trychroma.com)
- FastAPI: [Docs](https://fastapi.tiangolo.com)
- React: [Hooks Guide](https://react.dev/reference/react)

---

## Next Steps

1. Start the system (you're here!)
2. Upload test documents
3. Start chatting
4. Customize UI (optional)
5. Tune parameters (optional)
6. Deploy (see IMPLEMENTATION.md for options)

---

## Support

### Health Check
```bash
cd backend
python healthcheck.py
```

### Test API Manually
```bash
# Backend is up?
curl http://localhost:8000/api/health

# Can access frontend?
curl http://localhost:3000
```

### View Backend Logs
Look in backend terminal for detailed logs showing:
- Document loading progress
- Vector store operations
- LLM interactions
- Request handling

---

## You're All Set!

Everything is installed and ready to run.

Next command:
```bash
cd c:\Users\Arunjweh\Desktop\workspace\rag-system
start.bat
```

Then visit: http://localhost:3000

Happy documenting!

---

Complete RAG system with agentic reasoning, hybrid search, and modern UI - ready to use.
