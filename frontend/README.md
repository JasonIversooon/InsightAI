# InsightAI Frontend

This is the React frontend for InsightAI, providing a chat-based interface for uploading data, asking questions, and visualizing results.

## Features

- CSV file upload with drag-and-drop
- Data preview and fullscreen table view
- Chat interface for natural language queries
- AI-generated charts and graphs (Plotly.js)
- Responsive and modern UI

## Requirements

- Node.js 16+
- npm

## Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Configure API URL:**
   - Edit [.env](http://_vscodecontentref_/1) to set the backend API base URL:
     ```
     REACT_APP_API_BASE_URL=http://localhost:8080
     ```

3. **Run the development server:**
   ```bash
   npm start
   ```
   - Open [http://localhost:3000](http://localhost:3000) in your browser.

## Build

```bash
npm run build
```

## Testing

```bash
npm test
```

---


