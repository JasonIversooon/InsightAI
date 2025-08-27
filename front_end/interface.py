from dash import html, dcc, dash_table

# ---- Style Dictionaries ----
STYLES = {
    "main_container": {
        "padding": "32px",
        "background": "#181c23",
        "minHeight": "100vh",
        "color": "#fff",
    },
    "flex_row": {
        "display": "flex",
        "flexDirection": "row",
        "gap": "8px",
    },
    "upload_col": {
        "flex": 2.5,
        "padding": "16px",
    },
    "chat_col": {
        "flex": 3,
        "padding": "16px",
        "borderLeft": "1px solid #222",
        "borderRight": "1px solid #222",
    },
    "plot_col": {
        "flex": 2.5,
        "padding": "16px",
    },
    "chat_history": {
        "height": "400px",
        "overflowY": "auto",
        "marginBottom": "16px",
    },
    "chat_info": {
        "marginTop": "16px",
        "color": "#888",
    },
    "table": {
        "height": "600px",
        "overflowY": "auto",
    },
    "table_cell": {
        "padding": "8px",
        "minWidth": "100px",
        "width": "100px",
        "maxWidth": "180px",
    },
    "input": {
        "width": "80%",
    }
}

# ---- UI Components ----
def upload_component():
    return dcc.Upload(
        id='upload-data',
        children=html.Button('Upload CSV'),
        multiple=False
    )

def data_table_component():
    return dash_table.DataTable(
        id='data-table',
        style_table=STYLES["table"],
        style_cell=STYLES["table_cell"],
    )

def chat_history_component():
    return html.Div(id='chat-history', style=STYLES["chat_history"])

def chat_input_component():
    return dcc.Input(id='user-input', type='text', placeholder='Ask a question...', style=STYLES["input"])

def chat_send_button():
    return html.Button('Send', id='send-btn', n_clicks=0)

def chat_info_component():
    return html.Div(id='chat-info', style=STYLES["chat_info"])

def plot_component():
    return dcc.Graph(id='plot-area')