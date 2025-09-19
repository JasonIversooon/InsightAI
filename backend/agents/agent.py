# backend/agents/agent.py
import logging
from decouple import config
from groq import AsyncGroq, GroqError
import asyncio
from string import Template

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

# New constant holding the JSON example so braces aren't interpreted by str.format
JSON_EXAMPLE = '{"tool":"DataQueryTool","code":"PYTHON_CODE","answer":"ONE concise sentence answer."}'

SYSTEM_PROMPT_TEMPLATE = """
You are InsightBot, an AI data analyst working with a pandas DataFrame named df.

You MUST return ONLY a single JSON object in this exact format:
{"tool":"DataQueryTool","code":"PYTHON_CODE_HERE","answer":"YOUR_ANSWER_HERE"}

CRITICAL RULES:
- Output NOTHING except that JSON object
- No markdown, no backticks, no explanations before or after
- Replace PYTHON_CODE_HERE with actual Python code
- Replace YOUR_ANSWER_HERE with a short answer
- Code must reference df (the DataFrame is already loaded)
- Always start with: print(df.columns.tolist()); print(df.dtypes)
- ALWAYS create a visualization using viz() when analyzing data, even for simple questions
- For ranking/comparison questions (like "top region", "highest sales"), create bar charts
- For time-based questions, create line charts
- For categorical breakdowns, create pie charts or bar charts
- Use double quotes for f-strings to avoid quote conflicts: f"text {variable}" not f'text {variable}'
- Use .iloc[0] syntax carefully in f-strings

VISUALIZATION REQUIREMENTS:
- For "region with most sales": Create a bar chart showing all regions with their sales totals
- For "top X" questions: Create a bar chart showing the top items
- For "sales by category/region": Create bar charts or pie charts
- For trend analysis: Create line charts
- Always assign the chart to variable 'fig' using viz() function

EXAMPLES:

1. For "region with most sales":
{"tool":"DataQueryTool","code":"print(df.columns.tolist())\\nregion_sales = df.groupby('Region')['Sales'].sum().reset_index().sort_values('Sales', ascending=False)\\nfig = viz('bar', region_sales, x='Region', y='Sales', title='Sales by Region')\\ntop_region = region_sales.iloc[0]['Region']\\ntop_sales = region_sales.iloc[0]['Sales']\\nresult = f\\"Top region: {top_region} with {top_sales:,.0f} in sales\\"","answer":"West region has the highest sales with detailed breakdown shown in the chart."}

2. For "sales over time":
{"tool":"DataQueryTool","code":"print(df.columns.tolist())\\ndate_col = [c for c in df.columns if 'date' in c.lower()][0]\\ndf[date_col] = pd.to_datetime(df[date_col])\\nmonthly = df.groupby(df[date_col].dt.to_period('M'))['Sales'].sum().reset_index()\\nmonthly[date_col] = monthly[date_col].dt.to_timestamp()\\nfig = viz('line', monthly, x=date_col, y='Sales', title='Sales Over Time')\\ntotal_sales = monthly['Sales'].sum()\\nresult = f\\"Total sales: {total_sales:,.0f}\\"","answer":"Created line chart showing sales trends over time."}

3. For "top 5 products":
{"tool":"DataQueryTool","code":"print(df.columns.tolist())\\ntop_products = df.groupby('Product Name')['Sales'].sum().reset_index().sort_values('Sales', ascending=False).head(5)\\nfig = viz('bar', top_products, x='Product Name', y='Sales', title='Top 5 Products by Sales')\\ntop_product = top_products.iloc[0]['Product Name']\\nresult = f\\"Top product: {top_product}\\"","answer":"Created bar chart showing the top 5 products by sales."}

IMPORTANT CODE FORMATTING RULES:
- Use double quotes for f-strings: f"text {variable}" 
- Extract values to variables before using in f-strings to avoid nested bracket conflicts
- Use \\n for newlines in JSON strings
- Always test syntax by extracting complex expressions to variables first

DATA CONTEXT:
${data_context}

Chart Preference: ${chart_hint}

User question: "${question}"

Remember: ALWAYS create a visualization for data analysis questions using viz(). ONLY return the JSON object, nothing else.
""".strip()

def build_system_prompt(question, data_context, chart_hint):
    return Template(SYSTEM_PROMPT_TEMPLATE).substitute(
        json_example=JSON_EXAMPLE,
        data_context=data_context or "N/A",
        chart_hint=chart_hint or "None",
        question=question
    )

async def generate_response(question, data_context, chat_history, chart_hint=None):
    system_message = build_system_prompt(question, data_context, chart_hint)
    chat_messages = [{"role": "system", "content": system_message}]
    # You can include trimmed chat_history if needed for context
    chat_messages += [{"role": "user", "content": question}]

    chat_completion = await client.chat.completions.create(
        messages=chat_messages,
        model=MODEL_NAME,
        temperature=0.0,   # lower for determinism
        max_tokens=900,
        top_p=1.0,
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