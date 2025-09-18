// frontend/src/components/Visualization.js
import React, { useMemo } from 'react';
import Plot from 'react-plotly.js';
import '../styles/Visualization.css';

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
    const primary = getFirstVisibleTrace(visualization.data) || visualization.data[0];
    const isArray = a => Array.isArray(a) && a.length > 0;

    // Bar: keep existing behavior
    if (primary?.type === 'bar' && isArray(primary.x) && isArray(primary.y)) {
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

    // Pie: ALWAYS render custom legend with values (and %), hide Plotly legend
    if (primary?.type === 'pie' && isArray(primary.labels) && isArray(primary.values)) {
      const labels = primary.labels.map(String);
      const values = primary.values.map(v => Number(v));

      // Aggregate duplicates for safety (in case backend didn't)
      const aggMap = new Map();
      labels.forEach((lab, i) => {
        const val = Number(values[i]);
        aggMap.set(lab, (aggMap.get(lab) || 0) + (isFinite(val) ? val : 0));
      });
      const aggEntries = Array.from(aggMap.entries());
      // Preserve first-seen order
      const uniqueLabels = [];
      const uniqueValues = [];
      aggEntries.forEach(([lab, val]) => {
        uniqueLabels.push(lab);
        uniqueValues.push(val);
      });

      const total = uniqueValues.reduce((a, b) => a + (isFinite(b) ? b : 0), 0);
      const limit = Math.min(uniqueLabels.length, MAX_CUSTOM_LEGEND_ITEMS);

      const colors = uniqueLabels.map((_, i) => PALETTE[i % PALETTE.length]);

      const newTrace = {
        ...primary,
        labels: uniqueLabels,
        values: uniqueValues,
        marker: { ...(primary.marker || {}), colors }
      };

      const legend = uniqueLabels.slice(0, limit).map((label, i) => {
        const val = uniqueValues[i];
        const pct = total > 0 ? (val / total) * 100 : 0;
        return { label, value: val, percent: pct, color: colors[i] };
      });

      const idx = visualization.data.indexOf(primary);
      const rebuilt = [
        ...visualization.data.slice(0, idx),
        newTrace,
        ...visualization.data.slice(idx + 1),
      ];

      // Hide Plotly legend for pie so we can show our own with values
      return { processedData: rebuilt, legend, shouldShowPlotlyLegend: false };
    }

    // Fallback
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
                      <span>
                        {String(item.label)}: {formatAbbrev(item.value)}
                        {typeof item.percent === 'number' ? ` (${item.percent.toFixed(1)}%)` : ''}
                      </span>
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