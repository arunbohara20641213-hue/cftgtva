import React, { useState } from 'react';
import ChatWindow from './components/ChatWindow';
import DocumentManager from './components/DocumentManager';
import './App.css';

/**
 * Main App component combining chat and document management.
 */
function App() {
  const [sessionId] = useState(`session-${Date.now()}`);
  const [documents, setDocuments] = useState([]);

  const handleDocumentUploaded = (doc) => {
    setDocuments((prev) => [...prev, doc]);
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>🤖 RAG Document Chat System</h1>
        <p>Upload documents and chat with AI powered by your own data</p>
      </header>

      <div className="app-container">
        <aside className="sidebar">
          <DocumentManager onDocumentUploaded={handleDocumentUploaded} />
        </aside>

        <main className="main-content">
          <ChatWindow sessionId={sessionId} />
        </main>
      </div>

      <footer className="app-footer">
        <p>RAG System powered by LangChain, ChromaDB, and Ollama</p>
      </footer>
    </div>
  );
}

export default App;
