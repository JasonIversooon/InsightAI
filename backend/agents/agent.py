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
You are InsightBot, an AI data analyst helping with a pandas DataFrame called df.
Return ONLY a single JSON object:
{{"tool": "DataQueryTool", "code": "PYTHON_CODE_THAT_RUNS", "answer": "A concise, direct answer."}}

Rules:
- Use df as the DataFrame variable. pandas as pd, plotly.express as px are available.
- A helper function viz(chart_type, df, ...) is available to quickly create charts. It returns a Plotly figure.
  Examples:
    fig = viz('bar', df, x='Region', y='Sales', title='Sales by Region')
    fig = viz('pie', df, values='Sales', names='Region', title='Share of Sales')
    fig = viz('line', df, x='Date', y='Revenue', title='Revenue over Time')
    fig = viz('histogram', df, x='Age', title='Age distribution')
    fig = viz('box', df, x='Category', y='Price', title='Price by Category')
    fig = viz('heatmap', df, title='Correlation heatmap')
    fig = viz('area', df, x='Date', y='Revenue', title='Revenue (Area)')
- If a chart is created, assign it to fig. Put the main numeric/text answer in result.
- Do NOT import any modules. Use only pd, px, viz, and built-ins.
- Keep code minimal, deterministic, and efficient for large datasets.
- When plotting time series (datetime on x), sort by date and aggregate y by an appropriate frequency
  (daily/weekly/monthly) instead of plotting raw transactions.

Chart selection:
- If Chart Preference below is not None, follow it strictly for the chart type.
- Otherwise, auto-select a suitable chart:
  - Category comparisons: bar
  - Part-to-whole (shares): pie (or donut if requested)
  - Trends over time: line (consider area if emphasizing cumulative or fill)
  - Distributions: histogram (or box for spread/outliers)
  - Relationships between two numeric variables: scatter (optionally trendline)
  - Correlation overview of many numeric columns: heatmap

DATA CONTEXT:
{data_context}

Chart Preference: {chart_hint}

When you answer, ensure "code" sets 'result' (a concise value or sentence) and optionally 'fig'.
User question: "{question}"
"""

async def generate_response(question, data_context, chat_history, chart_hint=None):
    system_message = SYSTEM_PROMPT.format(
        data_context=data_context or "N/A",
        chart_hint=chart_hint or "None",
        question=question,
    )
    chat_messages = [{"role": "system", "content": system_message}]
    # You can include trimmed chat_history if needed for context
    chat_messages += [{"role": "user", "content": question}]

    chat_completion = await client.chat.completions.create(
        messages=chat_messages,
        model=MODEL_NAME,
        temperature=0.1,
        max_tokens=1500,
        top_p=0.9,
    )
    return chat_completion.choices[0].message.content.strip()

def ask_llm(question, data_context, chat_history, chart_hint=None) -> str:
    try:
        loop = asyncio.get_running_loop()
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(
                asyncio.run,
                generate_response(question, data_context, chat_history, chart_hint),
            )
            return future.result()
    except RuntimeError:
        return asyncio.run(generate_response(question, data_context, chat_history, chart_hint))