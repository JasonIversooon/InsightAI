# backend/api/main.py
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import io
from typing import List, Dict, Any
import numpy as np

# Import optimized modules
from agents.agent import ask_llm
from core.data_context import generate_data_context
from core.data_processor import DataProcessor

app = FastAPI(title="InsightAI API", version="1.0.0")

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    chat_history: List[ChatMessage] = []

class ChatResponse(BaseModel):
    response: str
    chat_history: List[ChatMessage]
    visualization: Dict[str, Any] = None

# Initialize data processor
data_processor = DataProcessor()

# Global state (use proper state management in production)
current_df = None
current_context = None

def convert_ndarrays(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, dict):
        return {k: convert_ndarrays(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convert_ndarrays(i) for i in obj]
    return obj

def extract_chart_hint(text: str) -> str | None:
    """
    Very simple keyword-based chart intent detection.
    Returns a normalized chart type string (e.g., 'pie', 'bar', 'stacked_bar', 'line', 'area',
    'scatter', 'histogram', 'box', 'heatmap') or None if no clear intent.
    """
    if not text:
        return None
    t = text.lower()

    # Specific before generic to avoid false positives
    if "stacked bar" in t or ("stacked" in t and "bar" in t):
        return "stacked_bar"
    if "donut" in t or "doughnut" in t or "ring" in t:
        return "pie"  # we'll treat donut as pie with hole
    if "heat map" in t or "heatmap" in t or "correlation matrix" in t or "corr matrix" in t:
        return "heatmap"
    if "boxplot" in t or "box plot" in t or "box" in t:
        return "box"
    if "histogram" in t or "hist" in t or "distribution" in t or "freq" in t:
        return "histogram"
    if "scatter" in t or "bubble" in t or "relationship" in t or "correlation" in t:
        return "scatter"
    if "area" in t:
        return "area"
    if "line" in t or "trend" in t or "over time" in t or "time series" in t or "timeseries" in t:
        return "line"
    if "pie" in t or "share" in t or "composition" in t:
        return "pie"
    if "bar" in t or "column" in t or "columns" in t or "compare categories" in t:
        return "bar"

    return None

@app.get("/")
async def root():
    return {"message": "InsightAI API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

@app.post("/api/upload")
async def upload_csv(file: UploadFile = File(...)):
    """Handle CSV file upload and processing"""
    global current_df, current_context
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    try:
        # Read CSV file
        contents = await file.read()
        
        # Try different encodings
        try:
            df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(io.StringIO(contents.decode('latin1')))
            except Exception:
                df = pd.read_csv(io.StringIO(contents.decode('cp1252')))
        
        # Validate dataframe
        if df.empty:
            raise HTTPException(status_code=400, detail="The uploaded CSV file is empty")
        
        # Store dataframe and generate context
        current_df = df
        current_context = generate_data_context(df)
        
        # Prepare response data
        preview_limit = 100  # keep responses small
        preview_data = df.head(preview_limit).to_dict('records')

        return {
            "message": "File uploaded successfully",
            "filename": file.filename,
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "preview": preview_data,
            "preview_limit": preview_limit,
            "context": current_context
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_data(request: ChatRequest):
    global current_df, current_context
    if current_df is None:
        raise HTTPException(status_code=400, detail="No dataset uploaded yet.")

    chat_history = [msg.model_dump() for msg in request.chat_history]
    chat_history.append({'role': 'user', 'content': request.message})

    # NEW: detect chart intent from the user's message
    chart_hint = extract_chart_hint(request.message)

    # Pass chart_hint to LLM so it either obeys or auto-selects a suitable chart
    bot_response = ask_llm(request.message, current_context, chat_history, chart_hint=chart_hint)

    result, visualization = data_processor.process_llm_response(
        bot_response, current_df, request.message
    )

    if isinstance(result, dict) and 'answer' in result:
        answer = result['answer']
    elif isinstance(result, str):
        answer = result
    else:
        answer = "Analysis completed. Check the visualization for details."

    chat_history.append({'role': 'bot', 'content': answer})
    response_history = [ChatMessage(**msg) for msg in chat_history]

    return ChatResponse(
        response=answer,
        chat_history=response_history,
        visualization=convert_ndarrays(visualization)
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=True)