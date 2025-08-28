import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """
You are InsightBot, an AI data analyst. Analyze the provided data and respond with executable Python code.

Data context:
{data_context}

IMPORTANT: Respond ONLY with a JSON object in this exact format:
{{"tool": "DataQueryTool", "code": "your_python_code_here", "answer": "your_natural_language_answer_here"}}

Guidelines:
- Use 'df' to reference the DataFrame (not 'data')
- For visualizations, always assign the plotly figure to a variable named 'fig'
- For data queries, assign result to 'result' variable
- Use pandas (pd) and plotly.express (px) for analysis and visualization
- **DO NOT include any import statements. All necessary libraries are already imported.**
- Keep code concise and focused on the user's question
- **If the user's question can be answered with a visualization, ALWAYS generate a plotly figure and assign it to 'fig', even if the answer is a single value. For example, show a bar chart of sales by region and highlight the region with the most sales.**
- When asked about regions, countries, or similar, always use the column with the most unique values matching the question (e.g., 'Region', 'Country', etc.).
- Always deduplicate x-axis values in plots and aggregate appropriately.
- If the answer is a single value, also show the relevant context in the plot (e.g., highlight the bar with the highest value).
- Only use columns that exist in the provided data context.
- When highlighting a bar in a plotly bar chart, set the color using the 'color' argument in px.bar or by creating a color array, instead of using update_traces with a selector.
- **ALWAYS fill the "answer" field with a short, clear, natural language answer to the user's question, based on the data.**

Previous conversation:
{chat_history}

User question: "{question}"
"""

def ask_llm(question, data_context, chat_history):
    """
    Calls OpenRouter's Mistral API to answer the user's question about the data.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return "OpenRouter API key not found. Please set OPENROUTER_API_KEY in your .env file."

    # Format chat history (limit to last 5 exchanges to avoid token limits)
    recent_history = chat_history[-10:] if len(chat_history) > 10 else chat_history
    formatted_history = "\n".join([f"{m['role']}: {m['content'][:100]}..." if len(m['content']) > 100 else f"{m['role']}: {m['content']}" for m in recent_history])
    
    system_message = SYSTEM_PROMPT.format(
        data_context=data_context,
        chat_history=formatted_history,
        question=question
    )

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": question}
    ]

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    data = {
        "model": "mistralai/mistral-small-3.2-24b-instruct:free",
        "messages": messages,
        "temperature": 0.1,  # Lower temperature for more consistent code generation
        "max_tokens": 1000,  # Limit response length
    }

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            data=json.dumps(data),
            timeout=30
        )

        if response.ok:
            return response.json()["choices"][0]["message"]["content"].strip()
        else:
            return f"Error: {response.status_code} - {response.text}"
    except requests.exceptions.RequestException as e:
        return f"Network error: {str(e)}"