from dash import html
from front_end.interface import (
    STYLES, upload_component, data_table_component, 
    chat_history_component, chat_input_component, 
    chat_send_button, chat_info_component, plot_component,
    store_components
)

def create_layout():
    """Create and return the main application layout"""
    return html.Div([
        # Sidebar
        html.Div([
            html.H2("InsightBot", style={"marginBottom": "8px"}),
            html.Div("Upload your CSV file", style={"color": "#bbb", "marginBottom": "8px"}),
            upload_component(),
            html.Div(id='upload-status', style=STYLES["upload_status"]),
            # Data table container
            html.Div([
                data_table_component(),
            ], style={
                "flex": "1",
                "display": "flex", 
                "flexDirection": "column",
                "width": "100%",
                "height": "calc(100vh - 200px)",
                "marginTop": "16px",
                "overflow": "hidden",
            }, id="table-container"),
            # Fullscreen button with proper styling
            html.Button(
                "Toggle Fullscreen",
                id="fullscreen-btn",
                style={
                    **STYLES["fullscreen_btn"],
                    "zIndex": "1000",
                    "position": "relative",
                }
            ),
        ], style=STYLES["sidebar_container"]),
        
        # Main area
        html.Div([
            html.H1("Your Conversational Data Analyst", style={"marginBottom": "16px"}),
            html.Div([
                # Chat and Plot side by side
                html.Div([
                    html.Div([
                        html.H3("Chat History", style={"marginBottom": "8px"}),
                        chat_history_component(),
                        html.Div([
                            chat_input_component(),
                            chat_send_button(),
                        ], style=STYLES["input_row"]),
                        chat_info_component(),
                    ], style=STYLES["chat_col"]),

                    html.Div([
                        html.H3("Visualization", style={"marginBottom": "8px"}),
                        plot_component(),
                    ], style=STYLES["plot_col"]),
                ], style=STYLES["chat_plot_row"]),
            ], style={"flex": 1}),
        ], style=STYLES["main_area"]),
        store_components(),
    ], style=STYLES["main_container"])