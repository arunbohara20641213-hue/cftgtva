#!/bin/bash
# Quick start script for RAG System (macOS/Linux)
# This script sets up and runs both backend and frontend

echo ""
echo "========================================"
echo " RAG System - Quick Start (macOS/Linux)"
echo "========================================"
echo ""

# Check prerequisites
echo "Checking prerequisites..."
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found. Please install Python 3.9+"
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js not found. Please install Node.js 16+"
    exit 1
fi

# Check Ollama
echo "Checking Ollama..."
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "ERROR: Ollama is not running. Start it with: ollama serve"
    echo "Then run this script again."
    exit 1
fi

echo "OK - All prerequisites found!"
echo ""

# Backend setup
echo "========================================"
echo "Setting up Backend..."
echo "========================================"
cd backend

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
echo "Installing/updating dependencies..."
pip install -q -r requirements.txt

echo ""
echo "========================================"
echo "Starting Backend (Port 8000)..."
echo "========================================"
echo "Backend will start at http://localhost:8000"
echo "API docs at http://localhost:8000/docs"
echo ""

# Start backend in background
python app.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Frontend setup
echo ""
echo "========================================"
echo "Setting up Frontend..."
echo "========================================"
cd ../frontend

echo "Installing dependencies..."
npm install --legacy-peer-deps > /dev/null 2>&1

echo ""
echo "========================================"
echo "Starting Frontend (Port 3000)..."
echo "========================================"
echo "Frontend will open at http://localhost:3000"
echo ""

# Start frontend
npm start

# Cleanup on exit
trap "kill $BACKEND_PID 2>/dev/null" EXIT
