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

#### 3. Overall Project README (`/README.md`)

````markdown
# InsightAI

InsightAI is an AI-powered data analyst that lets you upload CSV files, chat about your data in natural language, and receive instant visualizations and insights.

## Project Structure

```
insightAI/
├── backend/   # FastAPI backend (Python)
├── frontend/  # React frontend (JavaScript)
```

## Quick Start

### 1. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r [requirements.txt](http://_vscodecontentref_/2)
# Set your GROQ_API_KEY in .env
uvicorn api.main:app --reload --host 0.0.0.0 --port 8080
```

### 2. Frontend

```bash
cd frontend
npm install
npm start
# Open http://localhost:3000
```

## Features

- Upload CSV files and preview data
- Chat with your data using natural language
- AI-generated Python code and visualizations
- Interactive charts and tables

## Configuration

- **Backend:** Set your Groq API key in `backend/.env`
- **Frontend:** Set backend API URL in `frontend/.env`

