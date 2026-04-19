/**
 * API client for RAG system backend.
 * Provides methods for chat, document upload, and management.
 */

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const chatAPI = {
  /**
   * Send a chat message to the RAG agent.
   */
  sendMessage: async (message, sessionId = 'default', conversationHistory = null) => {
    try {
      const response = await apiClient.post('/chat', {
        message,
        session_id: sessionId,
        conversation_history: conversationHistory,
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to send message');
    }
  },

  /**
   * Get conversation history for a session.
   */
  getHistory: async (sessionId = 'default') => {
    try {
      const response = await apiClient.get(`/chat/history/${sessionId}`);
      return response.data.messages || [];
    } catch (error) {
      throw new Error('Failed to get conversation history');
    }
  },
};

export const documentAPI = {
  /**
   * Upload a document to the system.
   */
  upload: async (file, sourceName = null) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      if (sourceName) {
        formData.append('source_name', sourceName);
      }

      const response = await apiClient.post('/documents/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to upload document');
    }
  },

  /**
   * List all indexed documents.
   */
  list: async () => {
    try {
      const response = await apiClient.get('/documents');
      return response.data.documents || [];
    } catch (error) {
      throw new Error('Failed to list documents');
    }
  },

  /**
   * Delete a document.
   */
  delete: async (docId) => {
    try {
      const response = await apiClient.delete(`/documents/${docId}`);
      return response.data;
    } catch (error) {
      throw new Error('Failed to delete document');
    }
  },

  /**
   * Clear all documents.
   */
  clearAll: async () => {
    try {
      const response = await apiClient.post('/documents/clear');
      return response.data;
    } catch (error) {
      throw new Error('Failed to clear documents');
    }
  },
};

export const systemAPI = {
  /**
   * Get system health status.
   */
  health: async () => {
    try {
      const response = await apiClient.get('/health');
      return response.data;
    } catch (error) {
      throw new Error('System health check failed');
    }
  },

  /**
   * Get system status.
   */
  status: async () => {
    try {
      const response = await apiClient.get('/status');
      return response.data;
    } catch (error) {
      throw new Error('Failed to get system status');
    }
  },
};

export default apiClient;
