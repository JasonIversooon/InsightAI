from dash import html, dcc, dash_table

# ---- Style Dictionaries ----
STYLES = {
    "main_container": {
        "display": "flex",
        "flexDirection": "row",
        "height": "100vh",
        "background": "#181c23",
        "color": "#fff",
        "padding": "0",
        "fontFamily": "Inter, Arial, sans-serif",
    },
    "sidebar_container": {
        "width": "380px",
        "height": "100vh",
        "background": "#20242c",
        "padding": "24px 16px 24px 24px",
        "display": "flex",
        "flexDirection": "column",
        "gap": "16px",
        "borderRight": "1px solid #23272f",
        "minWidth": "300px",
        "boxSizing": "border-box",
        "overflow": "hidden",
    },
    "sidebar": {
        "width": "340px",
        "background": "#20242c",
        "padding": "24px 16px 24px 24px",
        "display": "flex",
        "flexDirection": "column",
        "gap": "16px",
        "borderRight": "1px solid #23272f",
        "minWidth": "300px",
        "boxSizing": "border-box",
    },
    "main_area": {
        "flex": 1,
        "display": "flex",
        "flexDirection": "column",
        "padding": "32px 40px",
        "gap": "32px",
        "overflow": "auto",
    },
    "chat_plot_row": {
        "display": "flex",
        "flexDirection": "row",
        "gap": "32px",
        "flex": 1,
        "minHeight": "0",
    },
    "chat_col": {
        "flex": 1.2,
        "background": "#23272f",
        "padding": "24px",
        "borderRadius": "12px",
        "display": "flex",
        "flexDirection": "column",
        "minWidth": "350px",
        "maxWidth": "500px",
        "boxSizing": "border-box",
    },
    "plot_col": {
        "flex": 1.5,
        "background": "#23272f",
        "padding": "24px",
        "borderRadius": "12px",
        "display": "flex",
        "flexDirection": "column",
        "minWidth": "350px",
        "boxSizing": "border-box",
    },
    "chat_history": {
        "height": "320px",
        "overflowY": "auto",
        "marginBottom": "16px",
        "background": "#181c23",
        "borderRadius": "8px",
        "padding": "12px",
        "fontSize": "15px",
    },
    "chat_info": {
        "marginTop": "16px",
        "color": "#888",
    },
    "input_row": {
        "display": "flex",
        "flexDirection": "row",
        "gap": "8px",
        "marginTop": "auto",
    },
    "input": {
        "width": "100%",
        "padding": "12px",
        "borderRadius": "6px",
        "border": "1px solid #444",
        "background": "#181c23",
        "color": "#fff",
        "fontSize": "15px",
    },
    "send_btn": {
        "padding": "8px 18px",
        "borderRadius": "6px",
        "border": "none",
        "background": "#0074D9",
        "color": "#fff",
        "fontWeight": "bold",
        "fontSize": "15px",
        "cursor": "pointer",
    },
    "upload_status": {
        "marginTop": "8px",
        "color": "#4CAF50",
        "fontWeight": "bold",
        "fontSize": "15px",
    },
    "file_upload_area": {
        "border": "2px dashed #444",
        "borderRadius": "12px",
        "padding": "20px",
        "textAlign": "center",
        "background": "#1a1e26",
        "marginBottom": "16px",
    },
    "drag_text": {
        "color": "#888",
        "fontSize": "14px",
        "marginBottom": "8px",
    },
    "limit_text": {
        "color": "#666",
        "fontSize": "12px",
        "marginBottom": "16px",
    },
    "browse_button": {
        "background": "#333",
        "color": "#fff",
        "border": "none",
        "padding": "8px 16px",
        "borderRadius": "4px",
        "fontSize": "14px",
        "cursor": "pointer",
    },
    "fullscreen_btn": {
        "marginTop": "12px",
        "padding": "8px 12px",
        "background": "#444",
        "color": "#fff",
        "border": "none",
        "borderRadius": "4px",
        "cursor": "pointer",
    },
    "table_style": {
        "height": "calc(100vh - 240px)",
        "overflowY": "auto",
        "background": "#23272f",
        "borderRadius": "8px",
        "marginTop": "8px",
        "border": "1px solid #444",
        "width": "100%",
    },
    "table_cell": {
        "padding": "8px 12px",
        "minWidth": "100px",
        "maxWidth": "200px",
        "background": "#23272f",
        "color": "#fff",
        "border": "1px solid #444",
        "fontSize": "14px",
        "textAlign": "left",
        "fontFamily": "monospace",
        "overflow": "hidden",
        "textOverflow": "ellipsis",
    },
    "table_header": {
        "background": "#20242c",
        "color": "#fff",
        "fontWeight": "bold",
        "border": "1px solid #444",
        "borderBottom": "2px solid #555",
        "padding": "12px",
        "textAlign": "left",
        "height": "48px",
    },
}

# ---- UI Components ----
def upload_component():
    """Create file upload component"""
    return dcc.Upload(
        id='upload-data',
        children=html.Div([
            html.Div("Drag and drop file here", style=STYLES["drag_text"]),
            html.Div("Limit 200MB per file • CSV", style=STYLES["limit_text"]),
            html.Button("Browse files", id="browse-button", style=STYLES["browse_button"])
        ]),
        multiple=False,
        style=STYLES["file_upload_area"]
    )

def data_table_component():
    """Create data table component with optimized styling"""
    return dash_table.DataTable(
        id='data-table',
        style_table=STYLES["table_style"],
        style_cell=STYLES["table_cell"],
        style_header=STYLES["table_header"],
        style_data={"whiteSpace": "nowrap", "height": "auto"},
        style_data_conditional=[
            {
                "if": {"row_index": "odd"},
                "backgroundColor": "#1e2229",
            },
            {
                "if": {"state": "selected"},
                "backgroundColor": "#375a7f",
                "border": "1px solid #375a7f",
            },
        ],
        style_cell_conditional=[
            {
                "if": {"column_type": "numeric"},
                "textAlign": "right",
            },
            # Remove the Row_Index specific styling for now to avoid the regex issue
        ],
        page_size=25,
        fill_width=True,
        fixed_rows={'headers': True},
        row_selectable=None,
        page_action="native",
        sort_action="native",
        sort_mode="multi",
        filter_action="native",
        editable=False,
        cell_selectable=True,
        style_as_list_view=False,
    )

def chat_history_component():
    """Create chat history component"""
    return html.Div(id='chat-history', style=STYLES["chat_history"])

def chat_input_component():
    """Create chat input component"""
    return dcc.Input(
        id='user-input',
        type='text',
        placeholder='Ask a question...',
        style=STYLES["input"],
        n_submit=0,
        value=''  # <--- Ensure the input is controlled from first render to avoid React warning
    )

def chat_send_button():
    """Create send button component"""
    return html.Button('Send', id='send-btn', n_clicks=0, style=STYLES["send_btn"])

def chat_info_component():
    """Create chat info component"""
    return html.Div("Ask me anything about your data!", id='chat-info', style=STYLES["chat_info"])

def plot_component():
    """Create plot component"""
    return dcc.Graph(id='plot-area', config={"displayModeBar": False})

def store_components():
    """Create store components for state management"""
    return html.Div([
        dcc.Store(id='stored-data'),
        dcc.Store(id='chat-store'),
        dcc.Store(id='last-fig-store'),
        dcc.Store(id='fullscreen-state', data=False),  # Add this line
    ], style={"display": "none"})