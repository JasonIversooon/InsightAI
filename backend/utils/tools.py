import re
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from io import StringIO

def viz(chart_type: str,
        df: pd.DataFrame,
        x: str | None = None,
        y: str | None = None,
        values: str | None = None,
        names: str | None = None,
        color: str | None = None,
        title: str | None = None,
        orientation: str | None = None,
        nbins: int | None = None,
        marginal: str | None = None,
        trendline: str | None = None,
        facet_col: str | None = None,
        facet_row: str | None = None,
        text: str | None = None):
    """
    Create a Plotly figure by chart_type. Minimal, safe wrapper around plotly.express.
    Supported chart_type: bar, stacked_bar, line, area, pie, scatter, histogram, box, heatmap.
    """
    ct = (chart_type or "").lower().strip()

    if ct in ("pie", "donut", "doughnut"):
        fig = px.pie(df, values=values or y, names=names or x, title=title)
        if ct in ("donut", "doughnut"):
            fig.update_traces(hole=0.4)
        return fig

    if ct in ("bar", "stacked_bar"):
        fig = px.bar(df, x=x, y=y, color=color, title=title, facet_col=facet_col, facet_row=facet_row, text=text)
        if ct == "stacked_bar":
            fig.update_layout(barmode="stack")
        if orientation in ("h", "horizontal"):
            fig.update_traces(orientation="h")
        return fig

    if ct in ("line", "area"):
        fig = px.line(df, x=x, y=y, color=color, title=title, facet_col=facet_col, facet_row=facet_row)
        if ct == "area":
            fig.update_traces(fill="tozeroy")
        return fig

    if ct in ("scatter", "bubble"):
        fig = px.scatter(df, x=x, y=y, color=color, title=title, trendline=trendline, facet_col=facet_col, facet_row=facet_row)
        return fig

    if ct in ("hist", "histogram"):
        fig = px.histogram(df, x=x, y=y, color=color, nbins=nbins, title=title, marginal=marginal, facet_col=facet_col, facet_row=facet_row)
        return fig

    if ct in ("box", "boxplot"):
        fig = px.box(df, x=x, y=y, color=color, title=title, facet_col=facet_col, facet_row=facet_row)
        return fig

    if ct in ("heatmap", "heat_map", "corr", "correlation"):
        # Correlation heatmap of numeric columns
        num_cols = df.select_dtypes(include=["number"])
        if num_cols.shape[1] >= 2:
            corr = num_cols.corr()
            fig = px.imshow(corr, text_auto=True, title=title or "Correlation heatmap", color_continuous_scale="RdBu", zmin=-1, zmax=1)
            return fig
        else:
            # Fallback: histogram if not enough numeric columns
            return px.histogram(df, x=x or num_cols.columns[0] if len(num_cols.columns) else None, title=title or "Histogram")

    # Default fallback
    return px.scatter(df, x=x, y=y, color=color, title=title or "Scatter")

def run_user_code(code, df, local_vars=None):
    """
    Safely execute user code with restricted globals and proper error handling.
    
    Args:
        code (str): Python code to execute
        df (pd.DataFrame): DataFrame to make available in the execution context
        local_vars (dict): Dictionary of local variables to maintain context
    
    Returns:
        dict or any: Result of code execution or error information
    """
    # Remove import statements for safety
    code = re.sub(r'^\s*import\s+[^\n]+', '', code, flags=re.MULTILINE)
    code = re.sub(r'^\s*from\s+[^\n]+import\s+[^\n]+', '', code, flags=re.MULTILINE)
    
    # Create safe execution environment
    safe_globals = {
        "__builtins__": {
            # Allow only safe built-ins
            "len": len,
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "list": list,
            "dict": dict,
            "tuple": tuple,
            "set": set,
            "min": min,
            "max": max,
            "sum": sum,
            "abs": abs,
            "round": round,
            "sorted": sorted,
            "enumerate": enumerate,
            "zip": zip,
            "range": range,
        },
        "pd": pd,
        "df": df,
        "px": px,
        "go": go,
        "viz": viz,  # NEW: convenience chart builder
    }
    
    # Initialize or update local variables
    local_vars = local_vars or {}
    safe_globals.update(local_vars)  # Add local vars to globals
    
    # Capture stdout for print statements
    old_stdout = sys.stdout
    sys.stdout = captured_output = StringIO()
    
    try:
        print(f"Executing: {code}")  # Debug print
        
        # Try to evaluate as expression first
        try:
            result = eval(code, safe_globals, local_vars)
            if result is not None:
                local_vars['result'] = result
                print(f"Eval result: {type(result)} - {result}")  # Debug print
                return local_vars
        except SyntaxError:
            # If eval fails, try exec
            print(f"Eval failed, trying exec...")  # Debug print
            exec(code, safe_globals, local_vars)
            print(f"Local vars after exec: {list(local_vars.keys())}")  # Debug print
            return local_vars
            
    except Exception as e:
        print(f"Execution error: {str(e)}")  # Debug print
        return {"error": f"Execution error: {str(e)}"}
    finally:
        # Restore stdout
        sys.stdout = old_stdout

def _format_result(result, captured_output):
    """
    Format the result from code execution to handle different types properly.
    
    Args:
        result: The result from code execution
        captured_output: StringIO object containing printed output
    
    Returns:
        Formatted result
    """
    # Handle pandas objects
    if isinstance(result, (pd.DataFrame, pd.Series)):
        return result
    
    # Handle plotly figures
    if hasattr(result, 'to_dict') and hasattr(result, 'data'):
        return result
    
    # Handle numeric results
    if isinstance(result, (int, float, bool)):
        return str(result)
    
    # Handle string results
    if isinstance(result, str):
        return result
    
    # Handle list/dict results
    if isinstance(result, (list, dict, tuple)):
        return result
    
    # For other types, try to convert to string
    try:
        return str(result)
    except:
        # If all else fails, return the captured output
        output = captured_output.getvalue()
        return output if output.strip() else "Code executed successfully"

def validate_dataframe_operation(df, operation_type):
    """
    Validate if a DataFrame operation can be safely performed.
    
    Args:
        df (pd.DataFrame): DataFrame to validate
        operation_type (str): Type of operation to validate
    
    Returns:
        bool: True if operation is safe, False otherwise
    """
    if df is None or df.empty:
        return False
    
    if operation_type == "groupby" and df.shape[0] > 100000:
        return False  # Prevent groupby on very large datasets
    
    if operation_type == "plot" and df.shape[0] > 10000:
        return False  # Prevent plotting too many points
    
    return True

def safe_column_access(df, column_name):
    """
    Safely access a column from a DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame to access
        column_name (str): Name of the column
    
    Returns:
        pd.Series or None: Column data or None if not found
    """
    try:
        if column_name in df.columns:
            return df[column_name]
        return None
    except Exception:
        return None