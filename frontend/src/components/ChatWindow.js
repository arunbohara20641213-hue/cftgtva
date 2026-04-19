import React, { useState, useRef, useEffect } from 'react';
import { chatAPI } from '../api/client';

/**
 * ChatWindow component for displaying and sending messages.
 */
const ChatWindow = ({ sessionId, onSourceClick }) => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Load initial history
  useEffect(() => {
    const loadHistory = async () => {
      try {
        const history = await chatAPI.getHistory(sessionId);
        setMessages(history);
      } catch (err) {
        console.error('Failed to load history:', err);
      }
    };
    loadHistory();
  }, [sessionId]);

  const handleSendMessage = async (e) => {
    e.preventDefault();

    if (!inputValue.trim()) return;

    const userMessage = inputValue.trim();
    setInputValue('');
    setError(null);
    setLoading(true);

    // Add user message to display
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);

    try {
      const response = await chatAPI.sendMessage(
        userMessage,
        sessionId,
        messages
      );

      // Add assistant response
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: response.response,
          sources: response.sources,
        },
      ]);
    } catch (err) {
      setError(err.message);
      setMessages((prev) =>
        prev.filter((msg) => msg.content !== userMessage)
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-window">
      <div className="chat-header">
        <h2>Chat with Documents</h2>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="empty-state">
            <p>No messages yet. Upload a document and start asking questions!</p>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div key={idx} className={`message message-${msg.role}`}>
            <div className="message-content">
              <p>{msg.content}</p>

              {msg.sources && msg.sources.length > 0 && (
                <div className="sources">
                  <small>
                    <strong>Sources:</strong>
                  </small>
                  {msg.sources.map((source, sidx) => (
                    <div key={sidx} className="source-tag">
                      <span>{source.source_name}</span>
                      {source.confidence && (
                        <span className="confidence">
                          {(source.confidence * 100).toFixed(0)}%
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="message message-system">
            <div className="message-content">
              <p className="loading">Thinking...</p>
            </div>
          </div>
        )}

        {error && (
          <div className="message message-error">
            <div className="message-content">
              <p>Error: {error}</p>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input-form" onSubmit={handleSendMessage}>
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Ask a question about your documents..."
          disabled={loading}
          className="chat-input"
        />
        <button type="submit" disabled={loading || !inputValue.trim()}>
          {loading ? 'Sending...' : 'Send'}
        </button>
      </form>
    </div>
  );
};

export default ChatWindow;
