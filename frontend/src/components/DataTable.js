// src/components/DataTable.js
import React, { useState, useMemo } from 'react';

const DataTable = ({ data, isFullscreen, onToggleFullscreen }) => {
  const [currentPage, setCurrentPage] = useState(0);
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });
  const rowsPerPage = isFullscreen ? 20 : 5;

  // Always define hooks before any return
  const preview = data?.preview || [];
  const columns = data?.columns || [];

  // Sorting logic
  const sortedData = useMemo(() => {
    if (!sortConfig.key) return preview;
    const sorted = [...preview].sort((a, b) => {
      const aVal = a[sortConfig.key];
      const bVal = b[sortConfig.key];
      if (aVal === undefined || aVal === null) return 1;
      if (bVal === undefined || bVal === null) return -1;
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return sortConfig.direction === 'asc' ? aVal - bVal : bVal - aVal;
      }
      return sortConfig.direction === 'asc'
        ? String(aVal).localeCompare(String(bVal))
        : String(bVal).localeCompare(String(aVal));
    });
    return sorted;
  }, [preview, sortConfig]);

  if (!data || !data.preview) return null;

  const totalPages = Math.ceil(sortedData.length / rowsPerPage);
  const startIndex = currentPage * rowsPerPage;
  const endIndex = startIndex + rowsPerPage;
  const currentData = sortedData.slice(startIndex, endIndex);

  const handleSort = (col) => {
    setCurrentPage(0); // Reset to first page on sort
    setSortConfig((prev) => {
      if (prev.key === col) {
        return { key: col, direction: prev.direction === 'asc' ? 'desc' : 'asc' };
      }
      return { key: col, direction: 'asc' };
    });
  };

  return (
    <div className={`data-table-container ${isFullscreen ? 'fullscreen' : ''}`}>
      {isFullscreen && (
        <div className="table-header">
          <h2>📋 Data Table</h2>
          <button 
            className="close-fullscreen-btn"
            onClick={onToggleFullscreen}
          >
            ✕ Close
          </button>
        </div>
      )}
      
      <div className="table-wrapper">
        <table className="data-table">
          <thead>
            <tr>
              {columns.map((col, index) => (
                <th
                  key={index}
                  onClick={() => handleSort(col)}
                  style={{ cursor: 'pointer', userSelect: 'none' }}
                >
                  {col}
                  {sortConfig.key === col && (
                    <span>
                      {sortConfig.direction === 'asc' ? ' ▲' : ' ▼'}
                    </span>
                  )}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {currentData.map((row, index) => (
              <tr key={startIndex + index}>
                {columns.map((col, colIndex) => (
                  <td key={colIndex}>
                    {row[col] !== null && row[col] !== undefined 
                      ? String(row[col]).substring(0, 50) + (String(row[col]).length > 50 ? '...' : '')
                      : 'N/A'
                    }
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      {totalPages > 1 && (
        <div className="table-pagination">
          <button 
            onClick={() => setCurrentPage(Math.max(0, currentPage - 1))}
            disabled={currentPage === 0}
            className="pagination-btn"
          >
            ← Previous
          </button>
          <span className="page-info">
            Page {currentPage + 1} of {totalPages}
          </span>
          <button 
            onClick={() => setCurrentPage(Math.min(totalPages - 1, currentPage + 1))}
            disabled={currentPage === totalPages - 1}
            className="pagination-btn"
          >
            Next →
          </button>
        </div>
      )}
      
      {!isFullscreen && (
        <button 
          className="fullscreen-toggle-btn"
          onClick={onToggleFullscreen}
        >
          🔍 View Full Table
        </button>
      )}
    </div>
  );
};

export default DataTable;