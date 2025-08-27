import dash
from dash import html, dcc, Input, Output, State
import plotly.express as px
import pandas as pd
import json
from core.data_context import generate_data_context
from agents.agent import ask_llm
from core.tools import run_user_code
from front_end.interface import STYLES, upload_component, data_table_component, chat_history_component, chat_input_component, chat_send_button, chat_info_component, plot_component

app = dash.Dash(__name__)
app.title = "InsightBot: Your Conversational Data Analyst"

# Layout
app.layout = html.Div([
    html.H1("InsightBot: Your Conversational Data Analyst"),
    html.Div([
        # CSV Upload & Table
        html.Div([
            upload_component(),
            html.Div(id='upload-status'),
            data_table_component(),
        ], style=STYLES["upload_col"]),

        # Chat
        html.Div([
            html.H3("Chat History"),
            chat_history_component(),
            chat_input_component(),
            chat_send_button(),
            chat_info_component(),
        ], style=STYLES["chat_col"]),

        # Plot
        html.Div([
            html.H3("Total Sales by Region"),
            plot_component(),
        ], style=STYLES["plot_col"]),
    ], style=STYLES["flex_row"]),
    # Hidden stores for state
    dcc.Store(id='stored-data'),
    dcc.Store(id='chat-store', data=[]),
    dcc.Store(id='last-fig-store'),
], style=STYLES["main_container"])

# CSV Upload Callback
@app.callback(
    Output('upload-status', 'children'),
    Output('data-table', 'data'),
    Output('data-table', 'columns'),
    Output('stored-data', 'data'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'),
)
def handle_upload(contents, filename):
    if contents is None:
        return '', [], [], None
    content_type, content_string = contents.split(',')
    import base64, io
    decoded = base64.b64decode(content_string)
    try:
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
    except UnicodeDecodeError:
        df = pd.read_csv(io.StringIO(decoded.decode('latin1')))
    columns = [{"name": i, "id": i} for i in df.columns]
    data = df.to_dict('records')
    return f"Loaded: {filename}", data, columns, df.to_json(date_format='iso', orient='split')

# Chat Callback
@app.callback(
    Output('chat-history', 'children'),
    Output('chat-store', 'data'),
    Output('last-fig-store', 'data'),
    Output('plot-area', 'figure'),
    Output('chat-info', 'children'),
    Input('send-btn', 'n_clicks'),
    State('user-input', 'value'),
    State('stored-data', 'data'),
    State('chat-store', 'data'),
    prevent_initial_call=True
)
def handle_chat(n_clicks, user_input, stored_data, chat_history):
    if not stored_data:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, "Please upload a CSV file."
    df = pd.read_json(stored_data, orient='split')
    context = generate_data_context(df)
    chat_history = chat_history or []
    chat_history.append({'role': 'user', 'content': user_input})
    try:
        bot_response = ask_llm(user_input, context, chat_history)
        cleaned_response = bot_response.strip()
        if cleaned_response.startswith('```'):
            cleaned_response = cleaned_response.split('\n', 1)[-1]
        if cleaned_response.endswith('```'):
            cleaned_response = cleaned_response.rsplit('```', 1)[0]
        cleaned_response = cleaned_response.strip()
        tool_json = json.loads(cleaned_response)
        tool = tool_json.get("tool")
        code = tool_json.get("code")
        def structured_query_to_code(query):
            if query.get("operation") == "group_by_agg":
                group_by = query.get("group_by_cols", [])
                agg_ops = query.get("agg_operations", {})
                sort = query.get("sort", None)
                limit = query.get("limit", None)
                code_lines = [
                    f"result = df.groupby({group_by}).agg({agg_ops})"
                ]
                if sort:
                    parts = sort.split()
                    sort_col = parts[0]
                    sort_dir = parts[1] if len(parts) > 1 else "asc"
                    ascending = "False" if sort_dir.lower() in ["desc", "descending"] else "True"
                    code_lines.append(f"result = result.sort_values('{sort_col}', ascending={ascending})")
                if limit:
                    code_lines.append(f"result = result.head({limit})")
                code_lines.append("result")
                return "\n".join(code_lines)
            return "result = None\nresult"
        if isinstance(code, dict):
            code = structured_query_to_code(code)
        if isinstance(code, str):
            code = code.replace("data", "df")
        result = run_user_code(code, df)
        last_fig = None
        if tool == "DataQueryTool":
            chat_history.append({'role': 'bot', 'content': str(result)})
            # Auto-plot if possible
            if "region" in user_input.lower() and "sales" in user_input.lower():
                fig = px.bar(
                    df.groupby("Region")["Sales"].sum().reset_index(),
                    x="Region", y="Sales", title="Total Sales by Region"
                )
                last_fig = fig.to_dict()
            else:
                last_fig = None
        elif tool == "VisualizationTool" and "fig" in result:
            chat_history.append({'role': 'bot', 'content': "Here is the chart:"})
            last_fig = result["fig"].to_dict()
        else:
            chat_history.append({'role': 'bot', 'content': str(result)})
        # Render chat history
        chat_render = []
        for msg in chat_history:
            color = "#222" if msg['role'] == 'user' else "#0074D9"
            chat_render.append(html.Div([
                html.B(f"{msg['role'].capitalize()}: "),
                html.Span(msg['content'])
            ], style={'marginBottom': '8px', 'color': color}))
        # Plot
        fig = last_fig if last_fig else px.scatter()
        return chat_render, chat_history, last_fig, fig, "Ask me anything about your data!"
    except Exception as e:
        chat_history.append({'role': 'bot', 'content': f"Error parsing LLM response: {e}"})
        chat_render = []
        for msg in chat_history:
            color = "#222" if msg['role'] == 'user' else "#0074D9"
            chat_render.append(html.Div([
                html.B(f"{msg['role'].capitalize()}: "),
                html.Span(msg['content'])
            ], style={'marginBottom': '8px', 'color': color}))
        return chat_render, chat_history, None, px.scatter(), "Error occurred."

if __name__ == '__main__':
    app.run_server(debug=True)