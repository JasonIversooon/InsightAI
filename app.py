import dash
from front_end.layout import create_layout
from utils.index_string import INDEX_STRING
from core.callbacks import register_callbacks

# Initialize the Dash app
app = dash.Dash(
    __name__, 
    suppress_callback_exceptions=True,
    external_stylesheets=[
        'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap'
    ]
)

# Set the custom index string
app.index_string = INDEX_STRING

# Set the layout
app.layout = create_layout()

# Register all callbacks
register_callbacks(app)

if __name__ == '__main__':
    app.run(debug=True)