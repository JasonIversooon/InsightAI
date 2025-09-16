# backend/api/main.py
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI, UploadFile, File, HTTPException
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
    """Handle chat interactions and data analysis"""
    global current_df, current_context
    
    if current_df is None:
        raise HTTPException(status_code=400, detail="No data uploaded. Please upload a CSV file first.")
    
    try:
        # Convert Pydantic models to dict
        chat_history = [msg.model_dump() for msg in request.chat_history]
        
        # Add user message
        chat_history.append({'role': 'user', 'content': request.message})
        
        # Get LLM response
        bot_response = ask_llm(request.message, current_context, chat_history)
        
        # Process the response
        result, visualization = data_processor.process_llm_response(
            bot_response, current_df, request.message
        )
        
        # Generate final answer
        if isinstance(result, dict) and 'answer' in result:
            answer = result['answer']
        elif isinstance(result, str):
            answer = result
        else:
            answer = "Analysis completed. Check the visualization for details."
        
        # Add bot response to chat history
        chat_history.append({'role': 'bot', 'content': answer})
        
        # Convert back to Pydantic models
        response_history = [ChatMessage(**msg) for msg in chat_history]
        
        # Convert visualization (and result if needed) to be JSON serializable
        visualization = convert_ndarrays(visualization)

        return ChatResponse(
            response=answer,
            chat_history=response_history,
            visualization=visualization
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=True)