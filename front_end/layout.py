from dash import html
from front_end.interface import (
    STYLES, 
    create_upload_component, 
    create_data_table_component, 
    create_chat_history_component, 
    create_chat_input_component, 
    create_chat_send_button, 
    create_chat_info_component, 
    create_plot_component,
    create_store_components,
    create_fullscreen_button
)

def create_sidebar():
    """Create the sidebar layout"""
    return html.Div([
        html.H2("InsightBot", style={"marginBottom": "8px"}),
        html.Div("Upload your CSV file", style={"color": "#bbb", "marginBottom": "8px"}),
        create_upload_component(),
        html.Div(id='upload-status', style=STYLES["upload_status"]),
        # Data table container
        html.Div([
            create_data_table_component(),
        ], style=STYLES["table_container_normal"], id="table-container"),
        # Fullscreen button
        create_fullscreen_button(),
    ], style=STYLES["sidebar_container"])

def create_chat_section():
    """Create the chat section layout"""
    return html.Div([
        html.H3("Chat History", style={"marginBottom": "8px"}),
        create_chat_history_component(),
        html.Div([
            create_chat_input_component(),
            create_chat_send_button(),
        ], style=STYLES["input_row"]),
        create_chat_info_component(),
    ], style=STYLES["chat_col"])

def create_plot_section():
    """Create the plot section layout"""
    return html.Div([
        html.H3("Visualization", style={"marginBottom": "8px"}),
        create_plot_component(),
    ], style=STYLES["plot_col"])

def create_main_area():
    """Create the main content area layout"""
    return html.Div([
        html.H1("Your Conversational Data Analyst", style={"marginBottom": "16px"}),
        html.Div([
            # Chat and Plot side by side
            html.Div([
                create_chat_section(),
                create_plot_section(),
            ], style=STYLES["chat_plot_row"]),
        ], style={"flex": 1}),
    ], style=STYLES["main_area"])

def create_layout():
    """Create and return the main application layout"""
    return html.Div([
        create_sidebar(),
        create_main_area(),
        create_store_components(),
    ], style=STYLES["main_container"])