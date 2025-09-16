// src/App.js
import React, { useState, useRef } from 'react';
import DataUpload from './components/DataUpload';
import ChatInterface from './components/ChatInterface';
import Visualization from './components/Visualization';
import DataTable from './components/DataTable';
import './App.css';

function App() {
  const [uploadedData, setUploadedData] = useState(null);
  const [chatHistory, setChatHistory] = useState([]);
  const [currentVisualization, setCurrentVisualization] = useState(null);
  const [isTableFullscreen, setIsTableFullscreen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [showUpload, setShowUpload] = useState(false);

  const chatRef = useRef(null);

  const handleDataUpload = (data) => {
    setUploadedData(data);
    setChatHistory([
      {
        role: 'bot',
        content: `Data uploaded successfully! I can see ${data.shape[0]} rows and ${data.shape[1]} columns. What would you like to analyze?`
      }
    ]);
    setCurrentVisualization(null);
    setShowUpload(false);
    // Scroll to chat after upload
    setTimeout(() => {
      if (chatRef.current) {
        chatRef.current.scrollIntoView({ behavior: 'smooth' });
      }
    }, 300);
  };

  const handleChatResponse = (response) => {
    setChatHistory(response.chat_history);
    if (response.visualization) {
      setCurrentVisualization(response.visualization);
    }
    setIsLoading(false);
  };

  const handleChatSending = (isSending) => {
    setIsLoading(isSending);
  };

  // Helper to get preview data (first 3 rows)
  const getPreviewData = (data) => {
    if (!data || !data.preview) return [];
    return data.preview.slice(0, 3);
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>🤖 InsightAI</h1>
          <p>Your AI-powered data analyst</p>
        </div>
      </header>

      <div className="main-content-v2">
        <div className="left-panel">
          {!uploadedData && (
            <DataUpload onDataUpload={handleDataUpload} />
          )}
          {uploadedData && (
            <button
              className="upload-btn"
              onClick={() => setShowUpload(true)}
              style={{ marginBottom: '1rem', width: '100%' }}
            >
              Change Data
            </button>
          )}
          {showUpload && (
            <DataUpload
              onDataUpload={handleDataUpload}
            />
          )}
          {/* DataFrame Preview */}
          {uploadedData && (
            <div className="data-preview-section" style={{ marginBottom: '1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontWeight: 600, fontSize: '1rem' }}>Data Preview</span>
                <button
                  className="fullscreen-toggle-btn"
                  onClick={() => setIsTableFullscreen(true)}
                  style={{ width: 'auto', marginLeft: '1rem', padding: '0.5rem 1rem' }}
                >
                  🔍 Full Screen
                </button>
              </div>
              <DataTable
                data={{
                  ...uploadedData,
                  preview: getPreviewData(uploadedData)
                }}
                isFullscreen={false}
                onToggleFullscreen={() => setIsTableFullscreen(true)}
                hideFullscreenBtn={true}
              />
            </div>
          )}
          <div ref={chatRef}>
            <ChatInterface
              chatHistory={chatHistory}
              onChatResponse={handleChatResponse}
              onChatSending={handleChatSending}
              hasData={!!uploadedData}
              isLoading={isLoading}
            />
          </div>
        </div>
        <div className="right-panel">
          <Visualization
            visualization={currentVisualization}
            isLoading={isLoading}
          />
        </div>
      </div>

      {isTableFullscreen && (
        <div className="fullscreen-table">
          <DataTable
            data={uploadedData}
            isFullscreen={true}
            onToggleFullscreen={() => setIsTableFullscreen(false)}
          />
        </div>
      )}
    </div>
  );
}

export default App;