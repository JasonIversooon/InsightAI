# InsightAI

AI-powered data analyst: upload CSVs, ask natural-language questions, and get visualizations.

Project layout
- backend/ — FastAPI backend, LLM integrations, Redis support
- frontend/ — React UI (Create React App)
- runtime.txt — optional repo root runtime for Render (if used)

Quick start
1. Backend (local):
   ```bash
   cd backend
   python3.10 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   export GROQ_API_KEY=your_key
   uvicorn api.main:app --reload --host 0.0.0.0 --port 8080
   ```
2. Frontend (local):
   ```bash
   cd frontend
   npm ci
   export REACT_APP_API_BASE_URL=http://localhost:8080
   npm start
   ```

Deployment summary (recommended)
- Deploy backend first (Render Web Service, backend root). Set GROQ_API_KEY, REDIS_URL, and ensure backend/runtime.txt pins Python 3.10.
- Deploy frontend as Render Static Site and set `REACT_APP_API_BASE_URL` to your backend URL before build.

Security reminder
- Do not commit secrets or .env into git. If you accidentally commit secrets, rotate them immediately and remove the file from the repository history.

More
- See `backend/README.md` and `frontend/README.md` for detailed instructions, Render settings, and troubleshooting tips.