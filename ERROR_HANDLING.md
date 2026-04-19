# RAG System - Error Handling & Troubleshooting Guide

**Last Updated:** April 19, 2026  
**Scope:** Backend (FastAPI), Frontend (React), Ollama Integration, ChromaDB

---

## Table of Contents

1. [Ollama Errors](#ollama-errors)
2. [Python Environment Errors](#python-environment-errors)
3. [FastAPI Backend Errors](#fastapi-backend-errors)
4. [React Frontend Errors](#react-frontend-errors)
5. [ChromaDB & Vector Store Errors](#chromadb--vector-store-errors)
6. [Network & Connectivity Errors](#network--connectivity-errors)
7. [Configuration Errors](#configuration-errors)
8. [Document Processing Errors](#document-processing-errors)
9. [Performance & Timeout Issues](#performance--timeout-issues)
10. [Debugging Commands](#debugging-commands)

---

## Ollama Errors

### Error 1: Ollama Service Not Running
**Error Message:**
```
ConnectionRefusedError: [WinError 10061] No connection could be made because the target machine actively refused it
```
or
```
Failed to connect to http://localhost:11434
```

**Cause:** Ollama service is not running

**Solution:**
```bash
# Start Ollama in a new terminal
ollama serve

# Verify it's running
curl http://localhost:11434/api/tags
```

**Prevention:** Keep Ollama running in background or use systemd service

---

### Error 2: Model Not Found
**Error Message:**
```
ollama._types.ResponseError: model "nomic-embed-text" not found, try pulling it first (status code: 404)
```

**Cause:** Required model is not installed

**Solution:**
```bash
# Pull the missing model
ollama pull nomic-embed-text
ollama pull llama2

# Verify models are installed
ollama list
```

**Expected Output:**
```
NAME                    ID              SIZE
llama2:latest          78e26419b446    3.8 GB
nomic-embed-text:latest 0a109f422b47    274 MB
```

**Prevention:** Run setup script before first launch:
```bash
ollama pull llama2 nomic-embed-text
```

---

### Error 3: Out of Memory (OOM)
**Error Message:**
```
CUDA out of memory
```
or
```
Killed - process terminated (exit code 137)
```

**Cause:** Insufficient system memory or VRAM for model loading

**Solutions:**

**Option 1: Reduce Model Complexity**
```bash
# Use smaller models
ollama pull orca-mini  # Smaller alternative to llama2
ollama pull all-minilm:22m  # Tiny embedding model

# Update .env
OLLAMA_LLM_MODEL=orca-mini
OLLAMA_EMBEDDING_MODEL=all-minilm:22m
```

**Option 2: Use CPU Only**
```bash
# Disable GPU (edit ollama config)
export OLLAMA_CUDA_VISIBLE_DEVICES=""
ollama serve
```

**Option 3: Increase Swap/Page File**
- Windows: System Properties → Advanced → Performance → Virtual Memory
- Linux: `fallocate -l 4G /swapfile && chmod 600 /swapfile && mkswap /swapfile && swapon /swapfile`

**Prevention:** Check system specs before deploying:
```bash
# Windows: Check available memory
Get-WmiObject -Class Win32_ComputerSystem | Select-Object TotalPhysicalMemory

# Linux: Check memory
free -h
```

---

### Error 4: Model Timeout During Generation
**Error Message:**
```
TimeoutError: Request to Ollama timed out after 300 seconds
```

**Cause:** Model taking too long to generate response

**Solution:**
```bash
# Increase timeout in backend/.env
OLLAMA_REQUEST_TIMEOUT=600  # 10 minutes

# Or reduce query complexity in frontend
# (Shorter queries = faster responses)
```

**Prevention:** Monitor response times and optimize prompts

---

## Python Environment Errors

### Error 5: Module Not Found - pydantic_settings
**Error Message:**
```
ModuleNotFoundError: No module named 'pydantic_settings'
```

**Cause:** Python dependencies not installed

**Solution:**
```bash
cd backend
pip install -r requirements.txt

# Or install specific package
pip install pydantic-settings>=2.0.0
```

**Prevention:** Always run after cloning:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

### Error 6: Python Version Incompatibility
**Error Message:**
```
SyntaxError: invalid syntax (f-strings or type hints not supported)
```

**Cause:** Python version < 3.8

**Solution:**
```bash
# Check Python version
python --version

# Update Python to 3.8+
# Windows: Download from python.org
# macOS: brew install python@3.11
# Linux: apt install python3.11
```

---

### Error 7: Virtual Environment Not Activated
**Error Message:**
```
pip not found
```
or
```
ImportError: No module named 'langchain'
```

**Cause:** Virtual environment not activated

**Solution:**
```bash
# Windows
cd backend
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Verify activation (prompt should show (venv))
which python  # Should show path inside venv
```

---

### Error 8: Conflicting Package Versions
**Error Message:**
```
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed
```

**Cause:** Incompatible package versions

**Solution:**
```bash
# Clean install
pip cache purge
pip uninstall -r requirements.txt -y
pip install -r requirements.txt

# Or upgrade pip/setuptools
pip install --upgrade pip setuptools wheel
```

---

## FastAPI Backend Errors

### Error 9: Pydantic Validation Error
**Error Message:**
```
pydantic_core._pydantic_core.ValidationError: 1 validation error for OllamaEmbeddings
request_timeout
  Extra inputs are not permitted [type=extra_forbidden, input_value=300, input_type=int]
```

**Cause:** Parameter not accepted by newer version of library

**Solution:**
```bash
# Update/downgrade library
pip install --upgrade langchain-ollama

# Or remove unsupported parameter from code
# In backend/core/embeddings.py, remove: request_timeout=settings.OLLAMA_REQUEST_TIMEOUT
```

---

### Error 10: Port Already in Use
**Error Message:**
```
OSError: [WinError 10048] Only one usage of each socket address is normally permitted
```
or
```
Address already in use
```

**Cause:** Port 8000 is already in use

**Solution:**
```bash
# Find process using port 8000
netstat -ano | findstr :8000  # Windows
lsof -i :8000  # macOS/Linux

# Kill the process
taskkill /PID <PID> /F  # Windows
kill -9 <PID>  # macOS/Linux

# Or use different port
python -m uvicorn app:app --port 8001

# Or update .env
API_PORT=8001
```

---

### Error 11: CORS Error
**Error Message:**
```
Access to XMLHttpRequest at 'http://localhost:8000/api/chat' from origin 'http://localhost:3000' has been blocked by CORS policy
```

**Cause:** Frontend and backend on different origins without proper CORS headers

**Solution:**

In `backend/app.py`, verify CORS is configured:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Or update for production:
```python
allow_origins=[
    "https://yourdomain.com",
    "https://api.yourdomain.com"
]
```

---

### Error 12: 500 Internal Server Error
**Error Message:**
```
HTTP 500: Internal Server Error
```

**Cause:** Multiple possible causes (see details in logs)

**Solution:**
```bash
# Check backend logs
tail -f backend/logs/app.log

# Or run with verbose logging
python -m uvicorn app:app --reload --log-level debug

# Check specific error in terminal output
```

---

### Error 13: Health Check Fails
**Error Message:**
```
GET /health returned 503 Service Unavailable
```

**Cause:** One or more services not initialized (Ollama, ChromaDB, etc.)

**Solution:**
```bash
# Test Ollama connectivity
curl http://localhost:11434/api/tags

# Check ChromaDB access
ls -la backend/storage/chroma/

# Check .env file
cat backend/.env | grep OLLAMA
```

---

## React Frontend Errors

### Error 14: Blank Screen / App Won't Load
**Error Message:**
```
Blank white page in browser
```

**Cause:** Multiple possible causes (see console)

**Solution:**
```bash
# Check browser console (F12 → Console tab)
# Common issues:
# 1. Backend not running → Start backend API
# 2. Port 3000 not available → Use different port
# 3. Node modules corrupted → Reinstall

cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

---

### Error 15: API Connection Failed
**Error Message:**
```
Network Error: Failed to connect to API
```
or in console:
```
GET http://localhost:8000/api/health 404 (Not Found)
```

**Cause:** Backend not running or wrong URL

**Solution:**
```bash
# Verify backend is running
curl http://localhost:8000/health

# Check frontend environment
cat frontend/.env  # or .env.local

# Update API URL if needed
echo "REACT_APP_API_URL=http://localhost:8000" > frontend/.env.local

# Restart frontend
npm start
```

---

### Error 16: npm Dependencies Failed to Install
**Error Message:**
```
npm ERR! ERESOLVE unable to resolve dependency tree
```

**Cause:** Conflicting package versions

**Solution:**
```bash
# Force install with legacy peer deps
npm install --legacy-peer-deps

# Or use npm@9+
npm install -g npm@latest
npm install
```

---

### Error 17: React Hot Reload Not Working
**Error Message:**
```
No hot reload on file changes
```

**Cause:** File watcher limit exceeded or .gitignore issue

**Solution:**
```bash
# Increase file watcher limit (Linux)
echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# Or restart development server
npm start

# Check if files are in .gitignore (should not be)
cat frontend/.gitignore
```

---

## ChromaDB & Vector Store Errors

### Error 18: ChromaDB Connection Failed
**Error Message:**
```
Failed to connect to ChromaDB at ./storage/chroma
```
or
```
sqlite3.OperationalError: database is locked
```

**Cause:** Database file corrupted, locked, or missing

**Solution:**
```bash
# Backup existing database
cp -r backend/storage/chroma backend/storage/chroma.backup

# Delete corrupted database
rm -rf backend/storage/chroma

# Restart application (will create new empty database)
python -m uvicorn app:app --reload
```

---

### Error 19: Vector Dimension Mismatch
**Error Message:**
```
ValueError: Vector dimension mismatch. Expected 384, got 768
```

**Cause:** Changed embedding model but old vectors still in database

**Solution:**
```bash
# Backup and reset database
rm -rf backend/storage/chroma

# Update embedding model in .env if intentional
OLLAMA_EMBEDDING_MODEL=nomic-embed-text  # 384 dimensions

# Restart and upload documents again
python -m uvicorn app:app --reload
```

---

### Error 20: Out of Disk Space
**Error Message:**
```
OSError: No space left on device
```

**Cause:** ChromaDB database too large or disk full

**Solution:**
```bash
# Check disk space
df -h  # Linux/macOS
Get-Volume  # PowerShell Windows

# Delete old/unnecessary collections
# Option 1: Clean up old documents
# Option 2: Archive old database
# Option 3: Increase disk space

# If collections getting too large, consider pagination:
# In config.py, reduce RETRIEVAL_K
RETRIEVAL_K=3  # Default, reduce for large indices
```

---

## Network & Connectivity Errors

### Error 21: Cannot Reach Ollama from Backend
**Error Message:**
```
Failed to establish a new connection to localhost:11434
```

**Cause:** Ollama bound to wrong interface or firewall blocking

**Solution:**
```bash
# Verify Ollama is listening on all interfaces
# Check Ollama logs/settings

# Test connectivity
curl -v http://localhost:11434/api/tags
curl -v http://127.0.0.1:11434/api/tags

# If behind Docker, use special hostname
# Update backend/.env
OLLAMA_BASE_URL=http://host.docker.internal:11434  # Docker Desktop
# or
OLLAMA_BASE_URL=http://ollama:11434  # Docker Compose network
```

---

### Error 22: Frontend Cannot Connect to Backend
**Error Message:**
```
XMLHttpRequest cannot load http://localhost:8000/api/chat. No 'Access-Control-Allow-Origin' header
```

**Cause:** CORS not configured properly

**Solution:** See Error 11 above

---

### Error 23: DNS Resolution Failed
**Error Message:**
```
Failed to resolve hostname
```

**Cause:** Network connectivity issue or DNS misconfigured

**Solution:**
```bash
# Test DNS
nslookup google.com  # Windows
dig google.com  # macOS/Linux

# Test basic connectivity
ping 8.8.8.8

# Update /etc/hosts or Windows hosts file if needed
# Windows: C:\Windows\System32\drivers\etc\hosts
# Linux/macOS: /etc/hosts

# Example: Add local mapping
127.0.0.1 localhost
127.0.0.1 rag-system.local
```

---

## Configuration Errors

### Error 24: Missing Environment Variables
**Error Message:**
```
KeyError: 'OLLAMA_BASE_URL'
```
or
```
ValidationError: Configuration error: Required field missing
```

**Cause:** .env file missing or incomplete

**Solution:**
```bash
# Copy example to actual .env
cp backend/.env.example backend/.env

# Verify all required variables
cat backend/.env | grep OLLAMA
cat backend/.env | grep API_

# Check required fields
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_LLM_MODEL=llama2
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
API_PORT=8000
```

---

### Error 25: Invalid Configuration Values
**Error Message:**
```
ValueError: Invalid value for CHUNK_SIZE: -100
```

**Cause:** Configuration value out of valid range

**Solution:**
```bash
# Valid ranges (update backend/.env):
CHUNK_SIZE=500  # Recommended: 500-2000
CHUNK_OVERLAP=200  # Should be < CHUNK_SIZE
RETRIEVAL_K=3  # Recommended: 2-10
AGENT_TEMPERATURE=0.7  # Range: 0.0-1.0
MAX_CONVERSATION_HISTORY=10  # Recommended: 5-20
```

---

### Error 26: File Path Issues (Windows)
**Error Message:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'backend\storage\chroma'
```

**Cause:** Path separator issues or missing directory

**Solution:**
```bash
# Use forward slashes in .env (Python handles conversion)
CHROMA_DB_PATH=./storage/chroma

# Or create directory manually
mkdir -p backend/storage/chroma  # Or in Windows: md backend\storage\chroma

# Verify path exists
ls -la backend/storage/
```

---

## Document Processing Errors

### Error 27: Unsupported File Format
**Error Message:**
```
ValueError: Unsupported file type: .docx
```

**Cause:** File format not supported

**Supported Formats:**
- `.pdf` - PDF documents (PyPDF2)
- `.txt` - Plain text files
- `.md` - Markdown files
- URLs - Web pages

**Solution:**
```bash
# Convert unsupported formats first
# .docx → .pdf (use LibreOffice, Word)
# .html → .md (use pandoc: pandoc file.html -t markdown -o file.md)
# Images → OCR first (use Tesseract)

# Then upload the converted file
```

---

### Error 28: PDF Extraction Failed
**Error Message:**
```
PdfReadError: Could not read PDF file
```

**Cause:** Corrupted PDF or encryption

**Solution:**
```bash
# Validate PDF
# Option 1: Try opening in Adobe Reader
# Option 2: Verify with command:
pdfinfo file.pdf  # Linux/macOS

# Re-save PDF in simpler format
# Use: Adobe Acrobat or online tools

# Test with known good PDF first
```

---

### Error 29: Chunk Size Too Small
**Error Message:**
```
Warning: Chunks too small (< 100 chars), may lack context
```

**Cause:** CHUNK_SIZE configured too small

**Solution:**
```bash
# Update backend/.env
CHUNK_SIZE=1000  # Minimum: 500
CHUNK_OVERLAP=200  # 20% overlap recommended

# Formula: CHUNK_OVERLAP should be ~20% of CHUNK_SIZE
# Example: Size=1000, Overlap=200 ✓
```

---

### Error 30: Memory Usage Spike During Upload
**Error Message:**
```
MemoryError: Unable to allocate X GiB for array
```

**Cause:** Very large document or high chunk count

**Solution:**
```bash
# Option 1: Split large documents
# Documents > 100MB should be split first

# Option 2: Reduce chunk size
CHUNK_SIZE=500  # Smaller chunks = less memory per operation

# Option 3: Upload in batches with delays
# Wait 10 seconds between uploads

# Option 4: Increase available memory
# See Error 3: Out of Memory
```

---

## Performance & Timeout Issues

### Error 31: Slow Document Upload (> 30 seconds)
**Cause:** Large document or slow embedding model

**Diagnosis:**
```bash
# Test embedding speed
python -c "
from langchain_ollama import OllamaEmbeddings
embeddings = OllamaEmbeddings(model='nomic-embed-text')
import time
start = time.time()
result = embeddings.embed_query('test text')
print(f'Time: {time.time() - start:.2f}s')
"
```

**Solutions:**
1. **Use faster embedding model:**
   ```bash
   ollama pull all-minilm:22m
   # Update .env: OLLAMA_EMBEDDING_MODEL=all-minilm:22m
   ```

2. **Reduce chunk size** (fewer chunks to embed):
   ```bash
   CHUNK_SIZE=500
   CHUNK_OVERLAP=100
   ```

3. **Increase GPU memory** or use larger VRAM allocation

---

### Error 32: Slow Chat Responses (> 10 seconds)
**Cause:** LLM taking time to generate or retrieval slow

**Diagnosis:**
```bash
# Test LLM response time
curl -X POST http://localhost:11434/api/generate \
  -d '{"model":"llama2","prompt":"Hello","stream":false}' \
  -H "Content-Type: application/json"

# Check response time in terminal output
```

**Solutions:**
1. **Use faster model:**
   ```bash
   ollama pull orca-mini  # Faster than llama2
   # Update .env: OLLAMA_LLM_MODEL=orca-mini
   ```

2. **Increase timeout:**
   ```bash
   OLLAMA_REQUEST_TIMEOUT=600  # 10 minutes
   ```

3. **Reduce context window:**
   ```bash
   RETRIEVAL_K=1  # Fewer documents = faster search
   ```

4. **Use CPU + GPU:**
   - Ensure GPU drivers are up-to-date
   - Monitor GPU usage: `nvidia-smi`

---

### Error 33: Request Timeout
**Error Message:**
```
TimeoutError: Request timed out after 300 seconds
```

**Solution:**
```bash
# Increase timeout in .env
OLLAMA_REQUEST_TIMEOUT=600

# Or in code, set per-request:
# (For advanced users, modify service/chat_service.py)
```

---

## Debugging Commands

### General Diagnostics
```bash
# Check Python environment
python --version
pip list | grep langchain

# Check Ollama status
ollama --version
ollama list

# Check ports in use
netstat -ano | findstr "8000\|3000\|11434"  # Windows
lsof -i :8000,:3000,:11434  # macOS/Linux

# Check disk space
df -h /  # Linux/macOS
Get-Volume  # PowerShell
```

### Backend Debugging
```bash
# Run with debug logging
python -m uvicorn app:app --reload --log-level debug

# Test specific endpoint
curl -X GET http://localhost:8000/health

# Test with verbose output
curl -v http://localhost:8000/health

# Check request/response
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello"}' -v
```

### Frontend Debugging
```bash
# Check build errors
npm run build

# Run with verbose output
npm start --verbose

# Check for console errors
# F12 in browser → Console tab

# Test API connectivity
fetch('http://localhost:8000/health').then(r => r.json()).then(console.log)
```

### ChromaDB Debugging
```bash
# List collections
python -c "
from chromadb import PersistentClient
client = PersistentClient(path='backend/storage/chroma')
print(client.list_collections())
"

# Check collection size
python -c "
from chromadb import PersistentClient
client = PersistentClient(path='backend/storage/chroma')
col = client.get_collection('documents')
print(f'Count: {col.count()}')
"
```

### Ollama Debugging
```bash
# View Ollama logs
ollama serve  # Logs appear in terminal

# Test model availability
curl http://localhost:11434/api/tags

# Test model generation
curl -X POST http://localhost:11434/api/generate \
  -d '{"model":"llama2","prompt":"test"}' \
  -H "Content-Type: application/json"
```

---

## Common Error Combinations

### Scenario A: "Everything is broken after starting fresh"
1. Check Ollama: `ollama list`
2. Check Python deps: `pip list | grep langchain`
3. Check ports: `netstat -ano | findstr "8000\|11434"`
4. Check files: `ls -la backend/` (permissions?)
5. Check .env: `cat backend/.env`

**Quick Fix:**
```bash
# Full reset
rm -rf backend/storage/chroma
pip install -r requirements.txt --force-reinstall
ollama pull llama2 nomic-embed-text
python -m uvicorn app:app --reload
```

### Scenario B: "Works locally, fails in Docker"
1. Check network: `docker network inspect bridge`
2. Check volumes: `docker volume ls`
3. Update OLLAMA_BASE_URL: `http://host.docker.internal:11434`
4. Check port mapping: `-p 8000:8000`

**Docker Fix:**
```bash
docker-compose down
docker-compose up --build
```

### Scenario C: "Frontend loads but no responses from API"
1. Backend running? `curl http://localhost:8000/health`
2. CORS enabled? Check app.py
3. Network? Check browser console (F12)
4. Ports? `netstat -ano | findstr 8000`

**Quick Fix:**
```bash
# Restart backend
Ctrl+C in terminal
python -m uvicorn app:app --reload

# Clear frontend cache
Ctrl+Shift+R in browser (hard refresh)
```

---

## Getting Help

### When Nothing Works
1. **Collect diagnostics:**
   ```bash
   # Save all logs
   python -m uvicorn app:app --reload 2>&1 | tee backend.log
   npm start 2>&1 | tee frontend.log
   ollama serve 2>&1 | tee ollama.log
   ```

2. **Check existing issues:**
   - GitHub Issues: Check closed issues for similar problems
   - LangChain Issues: https://github.com/langchain-ai/langchain/issues
   - Ollama Issues: https://github.com/ollama/ollama/issues

3. **Create detailed issue report:**
   - Exact error message
   - Steps to reproduce
   - Python version
   - System specs (RAM, GPU)
   - Full logs (sanitized)
   - .env file (sanitized)

4. **Stack Overflow tags:**
   ```
   [python] [langchain] [fastapi] [chromadb] [ollama]
   ```

---

## Prevention Best Practices

### Daily
- Monitor logs: `tail -f backend.log`
- Check disk space: `df -h /`
- Monitor memory: `top` or Task Manager

### Weekly
- Backup database: `cp -r backend/storage/chroma backend/storage/chroma.backup`
- Review error logs for patterns
- Test with new documents

### Monthly
- Update packages: `pip list --outdated`
- Update Ollama models: `ollama pull llama2` (latest version)
- Run test suite: `pytest tests/`

### Before Production
- Run full test suite
- Load test with `locust` or similar
- Security audit (.env exposed?)
- Add monitoring/alerting
- Set up backup strategy
- Document deployment process

---

## Quick Reference Table

| Error | Cause | Fix |
|-------|-------|-----|
| Connection Refused | Ollama not running | `ollama serve` |
| Model not found | Not downloaded | `ollama pull llama2` |
| Module not found | Deps not installed | `pip install -r requirements.txt` |
| Port in use | Another service using port | `taskkill /PID` or use different port |
| CORS error | Backend CORS not configured | Add CORSMiddleware in app.py |
| 500 error | Backend crash | Check logs with `--log-level debug` |
| Blank frontend | Backend down or API error | Check console (F12) |
| Timeout | Request too slow | Increase timeout or use faster model |
| OOM error | Insufficient memory | Use smaller model or reduce batch size |
| DB locked | ChromaDB busy | Restart application |

---

**Last Reviewed:** April 19, 2026  
**Maintainer:** RAG System Team  
**Status:** Complete & Ready for Production
