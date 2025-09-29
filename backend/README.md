# InsightAI Backend

This is the backend API for InsightAI, an AI-powered data analysis and visualization tool. The backend is built with FastAPI and integrates with LLMs for natural language data queries.

## Features

- CSV file upload and parsing
- Data context extraction and summary
- Natural language chat interface for data analysis
- AI-generated Python code execution (with safety checks)
- Automatic chart/visualization generation using Plotly
- REST API for frontend integration

## Requirements

- Python 3.10+
- See [`requirements.txt`](requirements.txt) for dependencies

## Setup

1. **Create a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables:**
   - Create a `.env` file in `/backend` with your Groq API key:
     ```
     GROQ_API_KEY=your_groq_api_key_here
     ```

4. **Run the server:**
   ```bash
   uvicorn api.main:app --reload --host 0.0.0.0 --port 8080
   ```

## API Endpoints

- `POST /api/upload` — Upload a CSV file
- `POST /api/chat` — Send a chat message/query about your data
- `GET /health` — Health check

## Development

- Code is organized into `api/`, `core/`, `agents/`, and `utils/`.
- Logging is enabled for debugging.
- See `main.py` for entrypoint and API routes.

## Testing

```bash
pytest
```