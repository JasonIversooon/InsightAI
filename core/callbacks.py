import dash
from dash import Input, Output, State, html
import plotly.express as px
import pandas as pd
import json
import base64
import io
import re
from core.data_context import generate_data_context
from agents.agent import ask_llm
from utils.tools import run_user_code

def register_callbacks(app):
    """Register all callbacks for the Dash app"""
    
    @app.callback(
        [Output('upload-status', 'children'),
         Output('data-table', 'data'),
         Output('data-table', 'columns'),
         Output('stored-data', 'data')],
        [Input('upload-data', 'contents')],
        [State('upload-data', 'filename')]
    )
    def handle_upload(contents, filename):
        """Handle CSV file upload and processing"""
        if contents is None:
            return '', [], [], None
        
        try:
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            
            # Try different encodings
            try:
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            except UnicodeDecodeError:
                df = pd.read_csv(io.StringIO(decoded.decode('latin1')))
            
            # Process dataframe for display
            df_display = df.copy()
            
            # Handle duplicate columns by making them unique
            df_display.columns = pd.Index([f"{col}_{i}" if list(df_display.columns).count(col) > 1 and list(df_display.columns)[:i+1].count(col) > 1
                                          else col for i, col in enumerate(df_display.columns)])
            
            # Add row index as first column with a unique name
            row_id_col = "Row_Index"
            counter = 1
            while row_id_col in df_display.columns:
                row_id_col = f"Row_Index_{counter}"
                counter += 1
            
            df_display.reset_index(inplace=True)
            df_display.rename(columns={'index': row_id_col}, inplace=True)
            
            # Create column configuration
            columns = _create_column_config(df_display)
            
            # Convert to records - ensure no duplicate columns
            data = _prepare_table_data(df_display)
            
            # Create status message
            status_message = html.Div([
                html.Span("Loaded: ", style={"color": "#fff"}),
                html.Span(filename, style={"color": "#4CAF50", "fontWeight": "bold"}),
                html.Span(f" ({len(df)} rows, {len(df.columns)} cols)", style={"color": "#bbb", "marginLeft": "4px"}),
            ])
            
            return status_message, data, columns, df.to_json(date_format='iso', orient='split')
            
        except Exception as e:
            error_message = html.Div(f"Error loading file: {str(e)}", style={"color": "#ff4444"})
            return error_message, [], [], None

    @app.callback(
        [Output('chat-history', 'children'),
         Output('chat-store', 'data'),
         Output('last-fig-store', 'data'),
         Output('plot-area', 'figure'),
         Output('chat-info', 'children'),
         Output('user-input', 'value')],
        [Input('send-btn', 'n_clicks'),
         Input('user-input', 'n_submit')],
        [State('user-input', 'value'),
         State('stored-data', 'data'),
         State('chat-store', 'data')],
        prevent_initial_call=True
    )
    def handle_chat(n_clicks, n_submit, user_input, stored_data, chat_history):
        """Handle chat interactions and data analysis"""
        if not stored_data or not user_input or not user_input.strip():
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, "Please upload a CSV file and enter a question.", dash.no_update
        
        try:
            df = pd.read_json(io.StringIO(stored_data), orient='split')
            context = generate_data_context(df)
            chat_history = chat_history or []
            
            # Add user message
            chat_history.append({'role': 'user', 'content': user_input.strip()})
            
            # Get LLM response
            bot_response = ask_llm(user_input.strip(), context, chat_history)
            
            # Process the response
            result, last_fig = _process_llm_response(bot_response, df, user_input)
            
            # Extract a human-readable answer
            if isinstance(result, dict):
                answer = result.get('answer')  # <-- Prefer the answer field
                if not answer:
                    answer = result.get('result')
                if isinstance(answer, dict) or answer is None:
                    answer = "I found the answer in the visualization."
            else:
                answer = str(result)

            chat_history.append({'role': 'bot', 'content': answer})
            
            # Render chat history
            chat_render = _render_chat_history(chat_history)
            
            # Create figure
            fig = last_fig if last_fig else px.scatter(title="No visualization available")
            
            return chat_render, chat_history, last_fig, fig, "Ask me anything about your data!", ""
            
        except Exception as e:
            error_msg = f"Error processing request: {str(e)}"
            chat_history = chat_history or []
            chat_history.append({'role': 'bot', 'content': error_msg})
            chat_render = _render_chat_history(chat_history)
            return chat_render, chat_history, None, px.scatter(title="Error occurred"), "Error occurred.", ""

def _create_column_config(df_display):
    """Create column configuration for the data table"""
    columns = []
    
    # Ensure columns are unique before processing
    unique_columns = df_display.columns.drop_duplicates()
    
    for col in unique_columns:
        col_name = str(col)
        col_id = str(col)
        
        # Determine column type and format
        col_type = 'numeric' if pd.api.types.is_numeric_dtype(df_display[col]) else 'text'
        col_format = {"specifier": ".2f"} if pd.api.types.is_float_dtype(df_display[col]) else None
        
        # Create column configuration
        column_config = {
            "name": col_name,
            "id": col_id,
            "type": col_type,
        }
        
        # Only add format if it's not None
        if col_format:
            column_config["format"] = col_format
        
        columns.append(column_config)
    
    return columns

def _prepare_table_data(df_display):
    """Prepare dataframe data for the table"""
    # Remove any duplicate columns before converting to dict
    df_clean = df_display.loc[:, ~df_display.columns.duplicated()]
    
    data = df_clean.to_dict('records')
    
    # Ensure all values are properly serializable
    for row in data:
        for key, value in row.items():
            if pd.isna(value):
                row[key] = None
            elif isinstance(value, (pd.Timestamp, pd.Timedelta)):
                row[key] = str(value)
            elif hasattr(value, 'item'):  # Handle numpy types
                row[key] = value.item()
    
    return data

def _process_llm_response(bot_response, df, user_input):
    """Process the LLM response and execute code"""
    try:
        cleaned_response = _clean_response(bot_response)
        print("LLM raw response:", cleaned_response)

        try:
            tool_json = json.loads(cleaned_response)
            code = tool_json.get("code", cleaned_response)
            answer = tool_json.get("answer")  # <-- Extract answer if present
        except json.JSONDecodeError:
            code = cleaned_response
            answer = None

        # Clean code
        if isinstance(code, str):
            code = re.sub(r'\bdata\b', 'df', code)
        
        print("Code to execute:", code)

        # Split code into lines and execute separately
        code_lines = code.strip().split('\n')
        local_vars = {}  # Create a dictionary to store local variables
        result = None
        
        # Execute each line while maintaining variable context
        for line in code_lines:
            if line.strip():
                local_vars = run_user_code(line, df, local_vars)
                if isinstance(local_vars, dict) and 'error' in local_vars:
                    return local_vars['error'], None
                result = local_vars  # Store the latest result

        # Get the final result (prioritize 'fig' over 'result')
        final_result = None
        if isinstance(result, dict):
            final_result = result.get('fig', result.get('result', result))
        else:
            final_result = result

        # Handle visualization
        fig = _extract_or_create_visualization(final_result, df, user_input)

        # When returning the final result, include both the value, figure, and answer
        return {'result': final_result, 'fig': fig, 'answer': answer}, fig

    except Exception as e:
        return f"Error processing response: {str(e)}", None

def _clean_response(response):
    """Clean the LLM response by removing code block markers"""
    cleaned = response.strip()
    if cleaned.startswith('```'):
        lines = cleaned.split('\n')
        if len(lines) > 1:
            cleaned = '\n'.join(lines[1:])
    if cleaned.endswith('```'):
        cleaned = cleaned.rsplit('```', 1)[0]
    return cleaned.strip()

def _extract_or_create_visualization(result, df, user_input):
    """Extract visualization from result or fallback to a generic empty plot."""
    # If result is an error dict, show an error plot
    if isinstance(result, dict) and 'error' in result:
        return px.scatter(title="Error: " + result['error']).to_dict()
    # If LLM returns a plotly figure (or dict), use it
    if isinstance(result, dict):
        for key in ('fig', 'plot', 'chart', 'result'):
            if key in result and result[key] is not None:
                candidate = result[key]
                if hasattr(candidate, 'to_dict'):
                    return candidate.to_dict()
                elif isinstance(candidate, dict) and 'data' in candidate:
                    return candidate
                elif key == 'result' and hasattr(candidate, 'columns'):
                    return _create_auto_plot(candidate).to_dict()
    elif hasattr(result, 'to_dict'):
        return result.to_dict()
    elif hasattr(result, 'columns'):
        return _create_auto_plot(result).to_dict()
    # Fallback: show empty plot (no attempt to guess intent)
    return px.scatter(title="No visualization available").to_dict()

def _create_auto_plot(df):
    """Create an automatic plot based on data structure"""
    numeric_cols = df.select_dtypes(include=['number']).columns
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    
    if len(numeric_cols) >= 2:
        return px.scatter(df, x=numeric_cols[0], y=numeric_cols[1], 
                         title=f"{numeric_cols[1]} vs {numeric_cols[0]}")
    elif len(numeric_cols) >= 1 and len(categorical_cols) >= 1:
        return px.bar(df.groupby(categorical_cols[0])[numeric_cols[0]].sum().reset_index(),
                     x=categorical_cols[0], y=numeric_cols[0], 
                     title=f"Total {numeric_cols[0]} by {categorical_cols[0]}")
    elif len(numeric_cols) >= 1:
        return px.histogram(df, x=numeric_cols[0], title=f"Distribution of {numeric_cols[0]}")
    else:
        return px.bar(title="No suitable data for automatic plotting")

def _render_chat_history(chat_history):
    """Render chat history as Dash components"""
    chat_render = []
    for msg in chat_history:
        role_color = "#4CAF50" if msg['role'] == 'user' else "#FF9800"
        content = str(msg['content'])
        chat_render.append(html.Div([
            html.B(f"{msg['role'].capitalize()}: ",
                  style={"color": role_color, "fontSize": "14px"}),
            html.Span(content, style={"color": "#ccc", "fontSize": "14px"})
        ], style={
            'marginBottom': '12px',
            'padding': '8px 12px',
            'borderRadius': '6px',
            'background': '#1a1e26' if msg['role'] == 'user' else '#2d3748',
            'border': f"1px solid {role_color}20"
        }))

    return chat_render