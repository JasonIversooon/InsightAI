// frontend/src/components/Visualization.js
import React, { useMemo } from 'react';
import Plot from 'react-plotly.js';

const PALETTE = ['#636EFA','#EF553B','#00CC96','#AB63FA','#FFA15A','#19D3F3','#FF6692','#B6E880','#FF97FF','#FECB52'];

const formatAbbrev = (n) => {
  if (n == null) return 'N/A';
  const abs = Math.abs(n);
  if (abs >= 1e9) return (n/1e9).toFixed(1).replace(/\.0$/,'') + 'B';
  if (abs >= 1e6) return (n/1e6).toFixed(1).replace(/\.0$/,'') + 'M';
  if (abs >= 1e3) return Math.round(n/1e3) + 'k';
  return new Intl.NumberFormat().format(n);
};

const Visualization = ({ visualization, isLoading }) => {
  const { processedData, legend } = useMemo(() => {
    if (!visualization || !Array.isArray(visualization.data) || visualization.data.length === 0) {
      return { processedData: null, legend: [] };
    }

    const trace = visualization.data[0];
    // Color per bar for common px.bar(output with one trace)
    if (trace?.type === 'bar' && Array.isArray(trace.x) && Array.isArray(trace.y) && trace.x.length === trace.y.length) {
      const colors = Array.isArray(trace?.marker?.color)
        ? trace.marker.color
        : trace.x.map((_, i) => PALETTE[i % PALETTE.length]);

      const newTrace = {
        ...trace,
        marker: { ...(trace.marker || {}), color: colors }
      };

      const legend = trace.x.map((label, i) => ({
        label,
        value: trace.y[i],
        color: colors[i]
      }));

      return { processedData: [newTrace, ...visualization.data.slice(1)], legend };
    }

    // Fallback: leave data untouched
    return { processedData: visualization.data, legend: [] };
  }, [visualization]);

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
              data={processedData || visualization.data}
              layout={{
                ...visualization.layout,
                autosize: true,
                showlegend: false, // we render our own legend below
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

            {legend.length > 0 && (
              <div className="custom-legend">
                <ul>
                  {legend.map((item, idx) => (
                    <li key={idx}>
                      <span className="legend-swatch" style={{ backgroundColor: item.color }} />
                      <span>{String(item.label)}: {formatAbbrev(item.value)}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
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