// src/App.js
import React, { useState } from 'react';
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

  const handleDataUpload = (data) => {
    setUploadedData(data);
    setChatHistory([
      {
        role: 'bot',
        content: `Data uploaded successfully! I can see ${data.shape[0]} rows and ${data.shape[1]} columns. What would you like to analyze?`
      }
    ]);
    setCurrentVisualization(null);
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
          <DataUpload onDataUpload={handleDataUpload} />
          {uploadedData && (
            <div className="data-preview-section">
              <h4>Data Preview</h4>
              <DataTable
                data={{
                  ...uploadedData,
                  preview: uploadedData.preview.slice(0, 5)
                }}
                isFullscreen={false}
                onToggleFullscreen={() => setIsTableFullscreen(true)}
              />
            </div>
          )}
          <ChatInterface
            chatHistory={chatHistory}
            onChatResponse={handleChatResponse}
            onChatSending={handleChatSending}
            hasData={!!uploadedData}
            isLoading={isLoading}
          />
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