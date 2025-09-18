// frontend/src/components/Visualization.js
import React, { useMemo } from 'react';
import Plot from 'react-plotly.js';

const PALETTE = ['#636EFA','#EF553B','#00CC96','#AB63FA','#FFA15A','#19D3F3','#FF6692','#B6E880','#FF97FF','#FECB52'];
const MAX_CUSTOM_LEGEND_ITEMS = 20; // guardrail

const formatAbbrev = (n) => {
  if (n == null) return 'N/A';
  const abs = Math.abs(n);
  if (abs >= 1e9) return (n/1e9).toFixed(1).replace(/\.0$/,'') + 'B';
  if (abs >= 1e6) return (n/1e6).toFixed(1).replace(/\.0$/,'') + 'M';
  if (abs >= 1e3) return Math.round(n/1e3) + 'k';
  return new Intl.NumberFormat().format(n);
};

const getFirstVisibleTrace = (data = []) =>
  data.find(t => t.visible === undefined || t.visible === true);

const Visualization = ({ visualization, isLoading }) => {
  const { processedData, legend, shouldShowPlotlyLegend } = useMemo(() => {
    if (!visualization || !Array.isArray(visualization.data) || visualization.data.length === 0) {
      return { processedData: null, legend: [], shouldShowPlotlyLegend: false };
    }

    // Prefer a visible trace (not "legendonly")
    const primary = getFirstVisibleTrace(visualization.data) || visualization.data[0];

    // Helper
    const isArray = a => Array.isArray(a) && a.length > 0;

    // Custom legend for single-trace bar only when:
    // - x and y exist
    // - item count is small
    // - x labels are unique (avoid duplicates exploding legend)
    if (
      primary?.type === 'bar' &&
      isArray(primary.x) &&
      isArray(primary.y)
    ) {
      const labels = primary.x.map(String);
      const unique = new Set(labels);
      const small = labels.length <= MAX_CUSTOM_LEGEND_ITEMS;
      const uniqueOnly = unique.size === labels.length;

      if (small && uniqueOnly) {
        const colors = Array.isArray(primary?.marker?.color)
          ? primary.marker.color
          : labels.map((_, i) => PALETTE[i % PALETTE.length]);

        const newTrace = {
          ...primary,
          marker: { ...(primary.marker || {}), color: colors }
        };

        const legend = labels.map((label, i) => ({
          label,
          value: primary.y[i],
          color: colors[i]
        }));

        // Rebuild data with our modified primary trace
        const idx = visualization.data.indexOf(primary);
        const rebuilt = [
          ...visualization.data.slice(0, idx),
          newTrace,
          ...visualization.data.slice(idx + 1),
        ];

        return { processedData: rebuilt, legend, shouldShowPlotlyLegend: false };
      }
      // Otherwise fall back to Plotly legend
      return { processedData: visualization.data, legend: [], shouldShowPlotlyLegend: true };
    }

    // Custom legend for pie only when slice count is small
    if (primary?.type === 'pie' && isArray(primary.labels) && isArray(primary.values)) {
      const labels = primary.labels.map(String);
      if (labels.length <= MAX_CUSTOM_LEGEND_ITEMS) {
        const colors = Array.isArray(primary?.marker?.colors)
          ? primary.marker.colors
          : labels.map((_, i) => PALETTE[i % PALETTE.length]);

        const newTrace = {
          ...primary,
          marker: { ...(primary.marker || {}), colors }
        };

        const legend = labels.map((label, i) => ({
          label,
          value: primary.values[i],
          color: colors[i]
        }));

        const idx = visualization.data.indexOf(primary);
        const rebuilt = [
          ...visualization.data.slice(0, idx),
          newTrace,
          ...visualization.data.slice(idx + 1),
        ];

        return { processedData: rebuilt, legend, shouldShowPlotlyLegend: false };
      }
      return { processedData: visualization.data, legend: [], shouldShowPlotlyLegend: true };
    }

    // Fallback: use Plotly's native legend for other chart types or large series
    return { processedData: visualization.data, legend: [], shouldShowPlotlyLegend: true };
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
                showlegend: shouldShowPlotlyLegend,
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