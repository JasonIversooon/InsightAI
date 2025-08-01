def generate_data_context(df):
    """
    Generate a string summary of the DataFrame for LLM context.
    Includes columns, dtypes, head, and summary statistics.
    """
    return f"""
Columns: {df.columns.tolist()}
DTypes: {df.dtypes.to_dict()}
Head:\n{df.head().to_string()}
Summary:\n{df.describe().to_string()}
"""
