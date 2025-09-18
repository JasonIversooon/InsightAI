// src/components/ChatInterface.js
import React, { useState, useRef, useEffect } from 'react';
import '../styles/ChatInterface.css';
import axios from 'axios';

const ChatInterface = ({ chatHistory, onChatResponse, onChatSending, hasData, isLoading }) => {
  const [message, setMessage] = useState('');
  const chatEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory]);

  const sendMessage = async () => {
    if (!message.trim() || !hasData || isLoading) return;

    const userMessage = message.trim();
    setMessage('');
    onChatSending(true);

    try {
      const response = await axios.post('http://192.168.0.110:8080/api/chat', {
        message: userMessage,
        chat_history: chatHistory
      });

      onChatResponse(response.data);
    } catch (error) {
      console.error('Error sending message:', error);
      onChatResponse({
        response: 'Sorry, there was an error processing your request. Please try again.',
        chat_history: [...chatHistory, 
          { role: 'user', content: userMessage },
          { role: 'bot', content: 'Sorry, there was an error processing your request. Please try again.' }
        ]
      });
    } finally {
      onChatSending(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const suggestedQuestions = [
    "What are the main trends in this data?",
    "Show me a summary of the data",
    "Which column has the highest values?",
    "Create a visualization of the data distribution"
  ];

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <h3>💬 Chat with your data</h3>
        <p>Ask questions about your dataset in natural language</p>
      </div>
      
      <div className="chat-messages">
        {chatHistory.length === 0 ? (
          <div className="chat-suggestions">
            <p>Try asking:</p>
            {suggestedQuestions.map((question, index) => (
              <button
                key={index}
                className="suggestion-btn"
                onClick={() => setMessage(question)}
                disabled={!hasData}
              >
                {question}
              </button>
            ))}
          </div>
        ) : (
          chatHistory.map((msg, index) => (
            <div key={index} className={`message ${msg.role}`}>
              {/* Avatar first so we can flip order for user with CSS */}
              <div className="message-avatar">
                {msg.role === 'user' ? '👤' : '🤖'}
              </div>
              <div className="message-content">
                <div className="message-text">{msg.content}</div>
              </div>
            </div>
          ))
        )}
        
        {isLoading && (
          <div className="message bot">
            <div className="message-avatar">🤖</div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={chatEndRef} />
      </div>
      
      <div className="chat-input-container">
        <div className="chat-input-wrapper">
          <input
            ref={inputRef}
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={hasData ? "Ask anything about your data..." : "Upload a CSV file to start chatting"}
            disabled={!hasData || isLoading}
            className="chat-input"
          />
          <button 
            onClick={sendMessage}
            disabled={!hasData || isLoading || !message.trim()}
            className="send-btn"
          >
            {isLoading ? '⏳' : '📤'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;