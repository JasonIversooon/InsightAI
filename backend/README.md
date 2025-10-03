# InsightAI Backend

FastAPI backend for InsightAI — CSV upload, data context extraction, LLM-driven chat, and visualization generation.

Key endpoints
- POST /api/upload — upload CSV file (multipart/form-data)
- POST /api/chat — ask questions about the uploaded dataset (JSON)
- GET  /health — simple health check

Requirements
- Python 3.10.x (runtime pinned via backend/runtime.txt)
- See backend/requirements.txt

Local setup (macOS)
1. Create venv and activate:
   ```bash
   cd backend
   python3.10 -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install --upgrade pip setuptools wheel
   pip install -r requirements.txt
   ```
3. Create a local .env (do NOT commit). Minimum:
   ```env
   GROQ_API_KEY=your_groq_key
   REDIS_URL=rediss://default:YOUR_PASSWORD@your-upstash-host:6379  # optional for multi-worker/session support
   ```
4. Run server:
   ```bash
   uvicorn api.main:app --reload --host 0.0.0.0 --port 8080
   ```

Render deployment (recommended)
- Ensure backend/runtime.txt exists in backend/ and pins Python (e.g. `python-3.10.12`).
- Render service settings:
  - Root Directory: backend
  - Environment: Python
  - Build Command: `pip install --upgrade pip setuptools wheel && pip install -r requirements.txt`
  - Start Command (production): `gunicorn -k uvicorn.workers.UvicornWorker api.main:app --bind 0.0.0.0:$PORT --workers 2`
  - Health Check Path: `/health`
- Environment variables (set in Render → Environment):
  - GROQ_API_KEY
  - REDIS_URL (rediss://... if using Upstash)
  - DATA_TTL_SECONDS (optional, default 86400)
  - Any other API keys you use (do not commit them)

Redis & session storage (why)
- For multi-worker setups, in-memory variables are not shared. Use Redis to store uploaded datasets keyed by session id.
- Set REDIS_URL in Render. Redis TTL auto-cleans temporary data — no separate cleanup script required.

Security & housekeeping
- Never commit real secrets (.env) — remove if committed and rotate keys immediately.
- To remove a committed .env from history (example):
  ```bash
  git rm --cached backend/.env
  git commit -m "Remove .env from repo"
  git push
  # rotate any exposed secrets
  ```
- Use TLS Redis URL (rediss://) when available.

Troubleshooting
- If gunicorn missing: add `gunicorn` to requirements.txt.
- If Render uses wrong Python version: ensure backend/runtime.txt is present in service root and redeploy.
- If frontend shows CORS errors: add your frontend origin to CORSMiddleware allow_origins in api/main.py and redeploy backend.

Development notes
- Logs from Render show save/load lines for Redis when upload/chat use X-Session-ID header from frontend.
- See backend/api/main.py for entry points and implementation details.