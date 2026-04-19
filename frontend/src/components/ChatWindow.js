import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { chatAPI } from '../api/client';

/**
 * Typing indicator component with animated dots.
 */
function TypingIndicator() {
  return (
    <div className="typing-indicator">
      <span></span>
      <span></span>
      <span></span>
    </div>
  );
}

/**
 * ChatWindow component for displaying and sending messages.
 * Features:
 * - Markdown rendering for formatted responses
 * - Typing indicator while waiting for response
 * - Message bubbles with user/assistant styling
 * - Auto-scroll to latest message
 * - Source citations with confidence scores
 */
const ChatWindow = ({ sessionId, onSourceClick }) => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);
  const messagesContainerRef = useRef(null);

  // Auto-scroll to bottom with smooth behavior
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, loading]);

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

    // Add user message to display immediately
    setMessages((prev) => [...prev, { role: 'user', content: userMessage, timestamp: new Date() }]);

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
          sources: response.sources || [],
          timestamp: new Date(),
        },
      ]);
    } catch (err) {
      setError(err.message);
      // Remove user message if request failed
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
        <h2>💬 Chat with Documents</h2>
        <p className="chat-subtitle">Ask questions about your uploaded documents</p>
      </div>

      <div className="chat-messages" ref={messagesContainerRef}>
        {messages.length === 0 && (
          <div className="empty-state">
            <div className="empty-icon">📄</div>
            <p>No messages yet.</p>
            <p className="empty-hint">Upload documents and start asking questions!</p>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div key={idx} className={`message-wrapper message-${msg.role}`}>
            <div className="message-bubble">
              <div className="message-avatar">
                {msg.role === 'user' ? '👤' : '🤖'}
              </div>
              <div className="message-content">
                {msg.role === 'user' ? (
                  <p className="user-message">{msg.content}</p>
                ) : (
                  <div className="assistant-message">
                    <ReactMarkdown
                      components={{
                        p: ({ node, ...props }) => <p className="markdown-paragraph" {...props} />,
                        h1: ({ node, ...props }) => <h1 className="markdown-h1" {...props} />,
                        h2: ({ node, ...props }) => <h2 className="markdown-h2" {...props} />,
                        h3: ({ node, ...props }) => <h3 className="markdown-h3" {...props} />,
                        code: ({ node, inline, ...props }) =>
                          inline ? (
                            <code className="markdown-code-inline" {...props} />
                          ) : (
                            <pre className="markdown-code-block">
                              <code {...props} />
                            </pre>
                          ),
                        ul: ({ node, ...props }) => <ul className="markdown-list" {...props} />,
                        ol: ({ node, ...props }) => <ol className="markdown-list-ordered" {...props} />,
                        li: ({ node, ...props }) => <li className="markdown-list-item" {...props} />,
                        blockquote: ({ node, ...props }) => <blockquote className="markdown-blockquote" {...props} />,
                        a: ({ node, ...props }) => <a className="markdown-link" target="_blank" rel="noopener noreferrer" {...props} />,
                        table: ({ node, ...props }) => <table className="markdown-table" {...props} />,
                      }}
                    >
                      {msg.content}
                    </ReactMarkdown>
                  </div>
                )}

                {msg.sources && msg.sources.length > 0 && (
                  <div className="sources-section">
                    <details className="sources-details">
                      <summary className="sources-summary">
                        📎 {msg.sources.length} Source{msg.sources.length !== 1 ? 's' : ''}
                      </summary>
                      <div className="sources-list">
                        {msg.sources.map((source, sidx) => (
                          <div key={sidx} className="source-tag">
                            <span className="source-name">{source.source_name || 'Unknown'}</span>
                            {source.confidence && (
                              <span className={`source-confidence confidence-${Math.round(source.confidence * 10) * 10}`}>
                                {(source.confidence * 100).toFixed(0)}%
                              </span>
                            )}
                          </div>
                        ))}
                      </div>
                    </details>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}

        {loading && (
          <div className="message-wrapper message-system">
            <div className="message-bubble">
              <div className="message-avatar">🤖</div>
              <div className="message-content">
                <div className="typing-message">
                  <p>Thinking</p>
                  <TypingIndicator />
                </div>
              </div>
            </div>
          </div>
        )}

        {error && (
          <div className="message-wrapper message-error">
            <div className="message-bubble error-bubble">
              <div className="message-avatar">⚠️</div>
              <div className="message-content">
                <p className="error-message">{error}</p>
              </div>
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
          autoFocus
        />
        <button type="submit" disabled={loading || !inputValue.trim()} className="chat-send-button">
          {loading ? '⏳' : '📤'}
        </button>
      </form>
    </div>
  );
};
};

export default ChatWindow;
