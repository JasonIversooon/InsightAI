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
    # Add table container styles for fullscreen functionality
    "table_container_normal": {
        "flex": "1",
        "display": "flex", 
        "flexDirection": "column",
        "width": "100%",
        "height": "calc(100vh - 200px)",
        "marginTop": "16px",
        "overflow": "hidden",
    },
    "table_container_fullscreen": {
        "position": "fixed",
        "top": "0",
        "left": "0",
        "width": "100vw",
        "height": "100vh",
        "zIndex": "9999",
        "background": "#181c23",
        "padding": "20px",
        "display": "flex",
        "flexDirection": "column",
        "overflow": "hidden",
    },
    "fullscreen_btn_normal": {
        "marginTop": "12px",
        "padding": "8px 12px",
        "background": "#444",
        "color": "#fff",
        "border": "none",
        "borderRadius": "4px",
        "cursor": "pointer",
        "zIndex": "1000",
        "position": "relative",
    },
    "fullscreen_btn_fullscreen": {
        "position": "absolute",
        "top": "20px",
        "right": "20px",
        "zIndex": "10000",
        "padding": "12px 20px",
        "background": "#ff4444",
        "color": "#fff",
        "border": "none",
        "borderRadius": "6px",
        "cursor": "pointer",
        "fontSize": "14px",
        "fontWeight": "bold",
        "boxShadow": "0 2px 8px rgba(0,0,0,0.3)"
    },
    # Chat message styles
    "chat_message_user": {
        'marginBottom': '12px',
        'padding': '8px 12px',
        'borderRadius': '6px',
        'background': '#1a1e26',
        'border': f"1px solid #4CAF5020"
    },
    "chat_message_bot": {
        'marginBottom': '12px',
        'padding': '8px 12px',
        'borderRadius': '6px',
        'background': '#2d3748',
        'border': f"1px solid #FF980020"
    },
    "chat_role_user": {
        "color": "#4CAF50", 
        "fontSize": "14px"
    },
    "chat_role_bot": {
        "color": "#FF9800", 
        "fontSize": "14px"
    },
    "chat_content": {
        "color": "#ccc", 
        "fontSize": "14px"
    },
    # Upload status message styles
    "upload_status_text": {
        "color": "#fff"
    },
    "upload_status_filename": {
        "color": "#4CAF50", 
        "fontWeight": "bold"
    },
    "upload_status_info": {
        "color": "#bbb", 
        "marginLeft": "4px"
    },
    "upload_error": {
        "color": "#ff4444"
    }
}

# ---- UI Component Creation Functions ----
def create_upload_component():
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

def create_data_table_component():
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

def create_chat_history_component():
    """Create chat history component"""
    return html.Div(id='chat-history', style=STYLES["chat_history"])

def create_chat_input_component():
    """Create chat input component"""
    return dcc.Input(
        id='user-input',
        type='text',
        placeholder='Ask a question...',
        style=STYLES["input"],
        n_submit=0,
        value=''
    )

def create_chat_send_button():
    """Create send button component"""
    return html.Button('Send', id='send-btn', n_clicks=0, style=STYLES["send_btn"])

def create_chat_info_component():
    """Create chat info component"""
    return html.Div("Ask me anything about your data!", id='chat-info', style=STYLES["chat_info"])

def create_plot_component():
    """Create plot component"""
    return dcc.Graph(id='plot-area', config={"displayModeBar": False})

def create_store_components():
    """Create store components for state management"""
    return html.Div([
        dcc.Store(id='stored-data'),
        dcc.Store(id='chat-store'),
        dcc.Store(id='last-fig-store'),
        dcc.Store(id='fullscreen-state', data=False),
    ], style={"display": "none"})

def create_fullscreen_button():
    """Create fullscreen toggle button"""
    return html.Button(
        "Toggle Fullscreen",
        id="fullscreen-btn",
        style=STYLES["fullscreen_btn_normal"]
    )

# ---- UI Helper Functions for Callbacks ----
def create_upload_status_message(filename, row_count, col_count):
    """Create upload status success message"""
    return html.Div([
        html.Span("Loaded: ", style=STYLES["upload_status_text"]),
        html.Span(filename, style=STYLES["upload_status_filename"]),
        html.Span(f" ({row_count} rows, {col_count} cols)", style=STYLES["upload_status_info"]),
    ])

def create_upload_error_message(error_msg):
    """Create upload error message"""
    return html.Div(f"Error loading file: {error_msg}", style=STYLES["upload_error"])

def create_chat_message(role, content):
    """Create a single chat message component"""
    role_color = STYLES["chat_role_user"] if role == 'user' else STYLES["chat_role_bot"]
    message_style = STYLES["chat_message_user"] if role == 'user' else STYLES["chat_message_bot"]
    
    return html.Div([
        html.B(f"{role.capitalize()}: ", style=role_color),
        html.Span(str(content), style=STYLES["chat_content"])
    ], style=message_style)

def get_table_container_style(is_fullscreen):
    """Get table container style based on fullscreen state"""
    return STYLES["table_container_fullscreen"] if is_fullscreen else STYLES["table_container_normal"]

def get_fullscreen_button_style(is_fullscreen):
    """Get fullscreen button style based on state"""
    return STYLES["fullscreen_btn_fullscreen"] if is_fullscreen else STYLES["fullscreen_btn_normal"]

def get_fullscreen_button_text(is_fullscreen):
    """Get fullscreen button text based on state"""
    return "Exit Fullscreen" if is_fullscreen else "Toggle Fullscreen"

# Maintain backward compatibility
upload_component = create_upload_component
data_table_component = create_data_table_component
chat_history_component = create_chat_history_component
chat_input_component = create_chat_input_component
chat_send_button = create_chat_send_button
chat_info_component = create_chat_info_component
plot_component = create_plot_component
store_components = create_store_components