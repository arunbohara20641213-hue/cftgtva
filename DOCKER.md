# RAG System - Docker Deployment Guide

## Quick Start with Docker

### Prerequisites
- Docker & Docker Compose installed
- Ollama running on your system (NOT in Docker)

### Start Everything

```bash
# 1. Start Ollama (in separate terminal)
ollama serve

# 2. In another terminal, start containers
cd rag-system
docker-compose up --build

# 3. Open http://localhost:3000
```

### Individual Services

```bash
# Backend only
docker build -f Dockerfile.backend -t rag-backend .
docker run -p 8000:8000 -e OLLAMA_BASE_URL=http://host.docker.internal:11434 rag-backend

# Frontend only
docker build -f Dockerfile.frontend -t rag-frontend .
docker run -p 3000:3000 rag-frontend
```

### Check Status

```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Check health
curl http://localhost:8000/api/health
curl http://localhost:3000
```

### Stop Services

```bash
docker-compose down

# Clean up volumes (removes persisted data)
docker-compose down -v
```

## Production Deployment

### AWS ECS/Fargate
```bash
# Push images to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com

docker tag rag-backend:latest <account>.dkr.ecr.us-east-1.amazonaws.com/rag-backend:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/rag-backend:latest

# Deploy with CloudFormation or AWS Console
```

### Google Cloud Run

```bash
# Build and push
gcloud builds submit --tag gcr.io/<project>/rag-backend

# Deploy
gcloud run deploy rag-backend \
  --image gcr.io/<project>/rag-backend \
  --platform managed \
  --region us-central1
```

### Heroku

```bash
# Add Procfile
echo "web: gunicorn app:app" > backend/Procfile

# Deploy
heroku login
heroku create rag-system
git push heroku main
```

## Environment Variables

Backend (.env):
```
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_LLM_MODEL=llama2
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
CHROMA_DB_PATH=/app/storage/chroma
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_URL=http://localhost:3000
```

Frontend (.env):
```
REACT_APP_API_URL=http://localhost:8000/api
```

## Troubleshooting

### "Cannot connect to Ollama"
- Ensure Ollama is running: `ollama serve`
- Check OLLAMA_BASE_URL is correct for your setup
- From Docker container, use `http://host.docker.internal:11434` (Docker Desktop)

### "Port already in use"
```bash
# Free ports
lsof -i :8000  # Find what's using 8000
kill -9 <PID>

# Or use different ports
docker-compose -f docker-compose.yml -e BACKEND_PORT=8001 up
```

### "Build fails"
```bash
# Clean and rebuild
docker-compose down
docker system prune
docker-compose up --build
```

## Advanced

### Multi-stage Build (smaller images)

```dockerfile
# Backend - in Dockerfile.backend
FROM python:3.11-slim as builder
WORKDIR /build
COPY backend/requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.11-slim
COPY --from=builder /root/.local /root/.local
COPY backend/ .
ENV PATH=/root/.local/bin:$PATH
CMD ["python", "app.py"]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rag-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: rag-backend
  template:
    metadata:
      labels:
        app: rag-backend
    spec:
      containers:
      - name: rag-backend
        image: your-registry/rag-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: OLLAMA_BASE_URL
          value: http://ollama-service:11434
        livenessProbe:
          httpGet:
            path: /api/health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 10
```

## Monitoring

### Docker Stats
```bash
docker stats
docker-compose stats
```

### Logging
```bash
# Tail logs
docker-compose logs -f --tail=100

# Filter by service
docker-compose logs -f backend
docker-compose logs -f frontend
```

## Persistence

### Save Data
```bash
# Backup ChromaDB
docker cp <container-id>:/app/storage ./backup/chroma

# Backup volumes
docker run --rm -v rag-system_chroma:/data -v $(pwd)/backup:/backup \
  alpine tar czf /backup/chroma.tar.gz -C /data .
```

## Next Steps

1. Test locally with Docker Compose
2. Push to container registry
3. Deploy to cloud platform
4. Set up monitoring & logging
5. Configure auto-scaling (if needed)
