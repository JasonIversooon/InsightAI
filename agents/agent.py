import os
import logging
from decouple import config
from groq import Groq, GroqError

# Initialize Groq client
client = Groq(
    api_key=config("GROQ_API_KEY"),
)

# Use a capable model for data analysis
MODEL_NAME = "llama3-70b-8192"  # Good balance of capability and speed for data analysis
logger = logging.getLogger("llm_client")

SYSTEM_PROMPT = """
You are InsightBot, an AI data analyst. Analyze the provided data and respond with executable Python code.

Data context:
{data_context}

IMPORTANT: Respond ONLY with a JSON object in this exact format:
{{"tool": "DataQueryTool", "code": "your_python_code_here", "answer": "A general description of what you're analyzing"}}

Guidelines:
- Use 'df' to reference the DataFrame (not 'data')
- For visualizations, always assign the plotly figure to a variable named 'fig'
- For data queries, assign result to 'result' variable
- Use pandas (pd) and plotly.express (px) for analysis and visualization
- **DO NOT include any import statements. All necessary libraries are already imported.**
- Keep code concise and focused on the user's question
- **If the user's question can be answered with a visualization, ALWAYS generate a plotly figure and assign it to 'fig'**
- When asked about regions, countries, or similar, always use the column with the most unique values matching the question
- Always deduplicate x-axis values in plots and aggregate appropriately
- Only use columns that exist in the provided data context
- For bar charts, use simple px.bar() calls without complex color mapping
- **In the "answer" field, provide a general description of what you're analyzing, NOT the specific result values (those will be computed after code execution)**
- When finding the "most" or "highest" value, show ALL categories in the visualization, not just the top one
- Use proper aggregation: df.groupby('column').sum() or df.groupby('column').mean()

Examples of good code patterns:
- For "region with most sales": 
  sales_by_region = df.groupby('Region')['Sales'].sum().sort_values(ascending=False)
  result = sales_by_region.index[0]
  fig = px.bar(x=sales_by_region.index, y=sales_by_region.values, title='Sales by Region')

Previous conversation:
{chat_history}

User question: "{question}"
"""

def ask_llm(question, data_context, chat_history):
    """
    Calls Groq API to answer the user's question about the data.
    """
    try:
        # Check if API key is configured
        api_key = config("GROQ_API_KEY", default=None)
        if not api_key:
            return "Groq API key not found. Please set GROQ_API_KEY in your .env file."

        # Format chat history (limit to last 10 exchanges to avoid token limits)
        recent_history = chat_history[-10:] if len(chat_history) > 10 else chat_history
        formatted_history = "\n".join([
            f"{m['role']}: {m['content'][:100]}..." if len(m['content']) > 100 
            else f"{m['role']}: {m['content']}" 
            for m in recent_history
        ])
        
        system_message = SYSTEM_PROMPT.format(
            data_context=data_context,
            chat_history=formatted_history,
            question=question
        )

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": question}
        ]

        # Make synchronous call to Groq
        chat_completion = client.chat.completions.create(
            messages=messages,
            model=MODEL_NAME,
            temperature=0.1,  # Lower temperature for more consistent code generation
            max_tokens=1500,  # Increased for more complex analysis
            top_p=0.9,
        )

        return chat_completion.choices[0].message.content.strip()

    except GroqError as e:
        logger.error(f"Groq API error: {e.__class__.__name__} - {e}")
        return f"[ERROR]: Groq API error - {str(e)}"
    except Exception as e:
        logger.error(f"An unexpected error occurred in ask_llm: {e}")
        return f"[ERROR]: The AI service is currently unavailable - {str(e)}"