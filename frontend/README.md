# InsightAI Frontend

React frontend for InsightAI — upload data, chat with it, and view generated visualizations.

Requirements
- Node.js 16+ (use Node 18+ for CI/build)

Local development
1. Install:
   ```bash
   cd frontend
   npm ci
   ```
2. Start dev server (local backend example):
   ```bash
   # point frontend to local backend during dev
   export REACT_APP_API_BASE_URL=http://localhost:8080
   npm start
   ```
3. The app stores a session id in localStorage (insightai_session) and sends it as X-Session-ID with upload/chat requests.

Build & deploy (Render Static Site)
- Create a Static Site on Render and point Root Directory to `frontend`.
- Render settings:
  - Build Command: `npm ci && npm run build`
  - Publish Directory: `build`
  - Environment variable (set before build): `REACT_APP_API_BASE_URL=https://<your-backend-domain>`
- Important: Create React App reads REACT_APP_* at build time — change it in Render and redeploy to update the built site.

API integration
- The frontend sends:
  - Upload: `POST /api/upload` (multipart/form-data) with header `X-Session-ID`
  - Chat: `POST /api/chat` with JSON body `{ message, chat_history }` and header `X-Session-ID`
- REACT_APP_API_BASE_URL must match your deployed backend root (include https).

Common issues
- CORS errors: add the frontend origin to backend CORSMiddleware allow_origins and redeploy backend.
- No server response: confirm backend URL and that backend is healthy (`/health`).

Build locally for test
```bash
cd frontend
REACT_APP_API_BASE_URL=https://insightai-vfi7.onrender.com npm ci
REACT_APP_API_BASE_URL=https://insightai-vfi7.onrender.com npm run build
npx serve -s build
```

Notes
- Do not include secrets in frontend .env. Only expose public endpoints (API base URL).
- For portfolio: list both frontend and backend Render URLs in your README or portfolio site.