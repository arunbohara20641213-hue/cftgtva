import React, { useState, useEffect } from 'react';
import { documentAPI } from '../api/client';

/**
 * DocumentManager component for uploading and managing documents.
 */
const DocumentManager = ({ onDocumentUploaded }) => {
  const [documents, setDocuments] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [dragOver, setDragOver] = useState(false);

  // Load documents on mount
  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      const docs = await documentAPI.list();
      setDocuments(docs);
    } catch (err) {
      console.error('Failed to load documents:', err);
    }
  };

  const handleFileUpload = async (file) => {
    if (!file) return;

    setUploading(true);
    setError(null);

    try {
      const result = await documentAPI.upload(file);
      
      // Add new document to list
      const newDoc = {
        doc_id: `doc-${Date.now()}`,
        filename: file.name,
        doc_type: result.doc_type || 'unknown',
        num_chunks: result.num_chunks || 0,
        uploaded_at: new Date().toISOString(),
        status: 'indexed',
      };

      setDocuments((prev) => [...prev, newDoc]);
      onDocumentUploaded?.(newDoc);
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileUpload(files[0]);
    }
  };

  const handleDeleteDocument = async (docId) => {
    try {
      await documentAPI.delete(docId);
      setDocuments((prev) => prev.filter((doc) => doc.doc_id !== docId));
    } catch (err) {
      setError(err.message);
    }
  };

  const handleClearAll = async () => {
    if (!window.confirm('Delete all documents? This cannot be undone.')) {
      return;
    }

    try {
      await documentAPI.clearAll();
      setDocuments([]);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="document-manager">
      <div className="manager-header">
        <h2>Documents</h2>
        {documents.length > 0 && (
          <button
            className="btn-secondary"
            onClick={handleClearAll}
            disabled={uploading}
          >
            Clear All
          </button>
        )}
      </div>

      <div
        className={`upload-zone ${dragOver ? 'drag-over' : ''}`}
        onDrop={handleDrop}
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
      >
        <label className="upload-label">
          <span className="upload-icon">📄</span>
          <span className="upload-text">
            {uploading
              ? 'Uploading...'
              : 'Drag documents here or click to select'}
          </span>
          <input
            type="file"
            accept=".pdf,.txt,.md"
            onChange={(e) => handleFileUpload(e.target.files[0])}
            disabled={uploading}
            className="file-input"
          />
        </label>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="documents-list">
        {documents.length === 0 ? (
          <p className="empty-docs">No documents uploaded yet</p>
        ) : (
          documents.map((doc) => (
            <div key={doc.doc_id} className="document-item">
              <div className="doc-info">
                <span className="doc-icon">📃</span>
                <div className="doc-details">
                  <p className="doc-filename">{doc.filename}</p>
                  <small className="doc-meta">
                    {doc.num_chunks} chunks • {doc.doc_type}
                  </small>
                </div>
              </div>
              <button
                className="btn-delete"
                onClick={() => handleDeleteDocument(doc.doc_id)}
              >
                ✕
              </button>
            </div>
          ))
        )}
      </div>

      <div className="supported-formats">
        <small>Supported formats: PDF, TXT, Markdown</small>
      </div>
    </div>
  );
};

export default DocumentManager;
