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

For more details, see the individual READMEs in [`backend/`](backend/README.md) and [`frontend/`](frontend/README.md).
````## Features

- Upload CSV files and preview data
- Chat with your data using natural language
- AI-generated Python code and visualizations
- Interactive charts and tables

## Configuration

- **Backend:** Set your Groq API key in `backend/.env`
- **Frontend:** Set backend API URL in `frontend/.env`

## License

MIT License

---

For more details, see the individual READMEs in [`backend/`](backend/README.md) and [`frontend/`](frontend/README.md).