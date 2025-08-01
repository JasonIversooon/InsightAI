import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()  # Loads .env file

SYSTEM_PROMPT = """
You are InsightBot, an AI data analyst. Here is the data context:
{data_context}

Available tools:
- DataQueryTool: For answering data questions.
- VisualizationTool: For creating charts.

Your job is to decide which tool to use and generate the Python code for it. Respond ONLY with a JSON object specifying the tool and the code. Do not explain. Just code.

Conversation history:
{chat_history}

User query: "{question}"
"""

def ask_llm(question, data_context, chat_history):
    """
    Calls OpenRouter's Mistral 24B API to answer the user's question about the data.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return "OpenRouter API key not found. Please set OPENROUTER_API_KEY in your .env file."

    # Format chat history for the prompt
    formatted_history = "\n".join([f"{m['role']}: {m['content']}" for m in chat_history])
    system_message = SYSTEM_PROMPT.format(
        data_context=data_context,
        chat_history=formatted_history,
        question=question
    )

    messages = [
        {"role": "system", "content": system_message},
    ]

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        # "HTTP-Referer": "<YOUR_SITE_URL>",  # Optional
        # "X-Title": "<YOUR_SITE_NAME>",      # Optional
    }

    data = {
        "model": "mistralai/mistral-small-3.2-24b-instruct:free",
        "messages": messages,
    }

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        data=json.dumps(data)
    )

    if response.ok:
        return response.json()["choices"][0]["message"]["content"].strip()
    else:
        return f"Error: {response.status_code} - {response.text}"