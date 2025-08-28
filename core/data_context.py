def generate_data_context(df):
    """
    Generate a concise summary of the DataFrame for LLM context.
    """
    # Get basic info
    shape_info = f"Shape: {df.shape[0]} rows, {df.shape[1]} columns"

    # Column info with types (limit to first 10 columns)
    col_info = []
    unique_samples = []
    for col in df.columns[:10]:
        dtype = str(df[col].dtype)
        if df[col].dtype in ['object', 'category']:
            unique_count = df[col].nunique()
            sample_uniques = df[col].dropna().unique()[:5]
            col_info.append(f"{col} ({dtype}, {unique_count} unique)")
            unique_samples.append(f"{col} sample values: {', '.join(map(str, sample_uniques))}")
        else:
            col_info.append(f"{col} ({dtype})")

    if len(df.columns) > 10:
        col_info.append(f"... and {len(df.columns) - 10} more columns")

    # List all columns
    all_columns = f"All columns: {', '.join(df.columns)}"

    # Sample data (first 3 rows only)
    sample_data = df.head(3).to_string(max_cols=8, max_colwidth=20)

    # Summary statistics for numeric columns only
    numeric_cols = df.select_dtypes(include=['number']).columns
    summary = ""
    if len(numeric_cols) > 0:
        summary = df[numeric_cols].describe().round(2).to_string()

    return f"""
{shape_info}

{all_columns}

Columns: {', '.join(col_info)}

{chr(10).join(unique_samples)}

Sample Data:
{sample_data}

Numeric Summary:
{summary}
"""