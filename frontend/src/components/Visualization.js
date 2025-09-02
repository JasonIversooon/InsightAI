// frontend/src/components/Visualization.js
import React from 'react';
import Plot from 'react-plotly.js';

const Visualization = ({ visualization, isLoading }) => {
  return (
    <div className="visualization-container">
      <div className="visualization-header">
        <h3>📊 Visualization</h3>
        <p>AI-generated charts and graphs</p>
      </div>
      
      <div className="visualization-content">
        {isLoading ? (
          <div className="visualization-loading">
            <div className="spinner large"></div>
            <p>Generating visualization...</p>
          </div>
        ) : visualization ? (
          <div className="plot-wrapper">
            <Plot
              data={visualization.data}
              layout={{
                ...visualization.layout,
                autosize: true,
                margin: { t: 40, b: 40, l: 40, r: 40 },
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)',
                font: { color: '#333', family: 'Inter, sans-serif' },
                title: {
                  ...visualization.layout?.title,
                  font: { size: 18, color: '#333' }
                }
              }}
              config={{ 
                displayModeBar: true,
                displaylogo: false,
                modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
                responsive: true
              }}
              style={{ width: '100%', height: '100%' }}
              useResizeHandler={true}
            />
          </div>
        ) : (
          <div className="no-visualization">
            <div className="no-viz-icon">📈</div>
            <h4>No visualization yet</h4>
            <p>Ask a question about your data to generate charts and graphs automatically.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Visualization;