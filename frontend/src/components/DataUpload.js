// frontend/src/components/DataUpload.js
import React, { useState } from 'react';
import '../styles/DataUpload.css';
import axios from 'axios';

const DataUpload = ({ onDataUpload }) => {
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [dragActive, setDragActive] = useState(false);

  const handleFileUpload = async (file) => {
    if (!file) return;

    console.log('Uploading file:', file.name, 'Size:', file.size, 'Type:', file.type);

    setUploading(true);
    setUploadStatus(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      console.log('Sending request to backend...');
      const response = await axios.post('http://192.168.0.110:8080/api/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 30000, // 30 second timeout
      });

      console.log('Full response:', response);
      console.log('Response data:', response.data);
      console.log('Response status:', response.status);

      // Check if response has the expected structure
      if (response.data && response.data.shape) {
        setUploadStatus({
          type: 'success',
          message: `Successfully loaded ${response.data.shape[0]} rows and ${response.data.shape[1]} columns`
        });
        
        console.log('Calling onDataUpload with:', response.data);
        onDataUpload(response.data);
      } else {
        console.error('Unexpected response structure:', response.data);
        setUploadStatus({
          type: 'error',
          message: 'Unexpected response from server. Please try again.'
        });
      }
    } catch (error) {
      console.error('Upload error details:', {
        message: error.message,
        response: error.response,
        request: error.request,
        code: error.code
      });

      let errorMessage = 'Failed to upload file';
      
      if (error.response) {
        // Server responded with error status
        console.error('Server error response:', error.response.data);
        errorMessage = error.response.data?.detail || `Server error: ${error.response.status}`;
      } else if (error.request) {
        // Request was made but no response received
        console.error('No response received:', error.request);
        errorMessage = 'No response from server. Please check your connection.';
      } else {
        // Something else happened
        console.error('Request setup error:', error.message);
        errorMessage = error.message;
      }

      setUploadStatus({
        type: 'error',
        message: errorMessage
      });
    } finally {
      setUploading(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragActive(false);
    const file = e.dataTransfer.files[0];
    if (file && file.name.endsWith('.csv')) {
      handleFileUpload(file);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragActive(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragActive(false);
  };

  return (
    <div className="upload-container">
      <div 
        className={`upload-area ${dragActive ? 'drag-active' : ''}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        <input
          type="file"
          accept=".csv"
          onChange={(e) => handleFileUpload(e.target.files[0])}
          disabled={uploading}
          id="file-upload"
          className="file-input"
        />
        <label htmlFor="file-upload" className="upload-label">
          <div className="upload-content">
            {uploading ? (
              <div className="upload-loading">
                <div className="spinner"></div>
                <p>Uploading...</p>
              </div>
            ) : (
              <>
                <div className="upload-icon">📁</div>
                <p className="upload-text">Drop your CSV file here</p>
                <p className="upload-subtext">or click to browse</p>
                <span className="browse-btn">
                  Choose File
                </span>
              </>
            )}
          </div>
        </label>
      </div>
      
      {uploadStatus && (
        <div className={`upload-status ${uploadStatus.type}`}>
          {uploadStatus.message}
        </div>
      )}
    </div>
  );
};

export default DataUpload;