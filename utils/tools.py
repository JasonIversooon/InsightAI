import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import re
from io import StringIO

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