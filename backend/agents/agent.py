# backend/agents/agent.py
import logging
from decouple import config
from groq import AsyncGroq, GroqError
import asyncio

# Initialize AsyncGroq client
client = AsyncGroq(
    api_key=config("GROQ_API_KEY"),
)

# Use a model that works well for code generation
MODEL_NAME = "openai/gpt-oss-20b"  # Good for code generation
# Alternative models you can try:
# MODEL_NAME = "mixtral-8x7b-32768"
# MODEL_NAME = "gemma2-9b-it"

logger = logging.getLogger("llm_client")

SYSTEM_PROMPT = """
You are InsightBot, an AI data analyst. Analyze the provided data and respond with executable Python code.

Data context:
{data_context}

IMPORTANT: Respond ONLY with a JSON object in this exact format:
{{"tool": "DataQueryTool", "code": "your_python_code_here", "answer": "A concise direct answer followed by a short explanation"}}

Guidelines:
- Use 'df' to reference the DataFrame
- For visualizations, always assign the plotly figure to a variable named 'fig'
- For data queries, assign the direct answer to a variable named 'result' (string or number)
- Use pandas (pd) and plotly.express (px) for analysis and visualization
- **DO NOT include any import statements. All necessary libraries are already imported.**
- Keep code concise and focused on the user's question
- **If the user's question can be answered with a visualization, ALWAYS generate a plotly figure and assign it to 'fig'**
- Always use proper aggregation: df.groupby('column').sum() or df.groupby('column').mean()
- **In the "answer" field, START with the direct answer (e.g., "West") and then a brief explanation**
- When finding the "most" or "highest" value, show ALL categories in the visualization
- Only use columns that exist in the provided data context

Examples of good code patterns:
- For "region with most sales": 
  sales_by_region = df.groupby('Region')['Sales'].sum().sort_values(ascending=False)
  result = sales_by_region.index[0]  # e.g., 'West'
  fig = px.bar(x=sales_by_region.index, y=sales_by_region.values, title='Sales by Region')
  # answer example: "West has the highest total sales. Bar chart shows totals by region."

Previous conversation:
{chat_history}

User question: "{question}"
"""

async def generate_response(question: str, data_context: str, chat_history: list) -> str:
    """
    Generate LLM response for data analysis questions.
    
    Args:
        question: User's question
        data_context: Context about the dataset
        chat_history: Previous conversation messages
        
    Returns:
        str: LLM response
    """
    try:
        # Format chat history (limit to last 8 exchanges to avoid token limits)
        recent_history = chat_history[-8:] if len(chat_history) > 8 else chat_history
        formatted_history = "\n".join([
            f"{m['role']}: {m['content'][:80]}..." if len(m['content']) > 80 
            else f"{m['role']}: {m['content']}" 
            for m in recent_history
        ])
        
        system_message = SYSTEM_PROMPT.format(
            data_context=data_context,
            chat_history=formatted_history,
            question=question
        )

        chat_completion = await client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": question}
            ],
            model=MODEL_NAME,
            temperature=0.1,
            max_tokens=1500,
            top_p=0.9,
        )

        return chat_completion.choices[0].message.content.strip()
        
    except GroqError as e:
        logger.error(f"Groq API error: {e.__class__.__name__} - {e}")
        return '{"tool": "DataQueryTool", "code": "# API Error", "answer": "Sorry, the AI service returned an error. Please try again."}'
    except Exception as e:
        logger.error(f"Unexpected error in generate_response: {e}")
        return '{"tool": "DataQueryTool", "code": "# Unexpected Error", "answer": "An unexpected error occurred. Please try again later."}'

def ask_llm(question: str, data_context: str, chat_history: list) -> str:
    """
    Synchronous wrapper for the async LLM call.
    
    Args:
        question: User's question
        data_context: Context about the dataset
        chat_history: Previous conversation messages
        
    Returns:
        str: LLM response
    """
    try:
        # Check if we're already in an async context
        try:
            loop = asyncio.get_running_loop()
            # If we're in an async context, we need to run in a new thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, generate_response(question, data_context, chat_history))
                return future.result()
        except RuntimeError:
            # No running loop, we can use asyncio.run directly
            return asyncio.run(generate_response(question, data_context, chat_history))
            
    except Exception as e:
        logger.error(f"Error in ask_llm wrapper: {e}")
        return '{"tool": "DataQueryTool", "code": "# Error", "answer": "Sorry, there was an error processing your request."}'