import pandas as pd
import plotly.express as px
import sys
from io import StringIO

def run_user_code(code, df):
    """
    Safely execute user code with restricted globals and proper error handling.
    
    Args:
        code (str): Python code to execute
        df (pd.DataFrame): DataFrame to make available in the execution context
    
    Returns:
        dict or any: Result of code execution or error information
    """
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
    }
    
    local_vars = {}
    
    # Capture stdout for print statements
    old_stdout = sys.stdout
    sys.stdout = captured_output = StringIO()
    
    try:
        # Try to evaluate as expression first
        try:
            result = eval(code, safe_globals, local_vars)
            if result is not None:
                return result
            # If result is None, check if there's any printed output
            output = captured_output.getvalue()
            return output if output.strip() else "Code executed successfully"
        except SyntaxError:
            # If eval fails, try exec
            exec(code, safe_globals, local_vars)
            
            # Check for specific variables that might contain results
            for var_name in ['result', 'fig', 'chart', 'plot']:
                if var_name in local_vars:
                    return {var_name: local_vars[var_name]}
            
            # Return all local variables if no specific result variable found
            output = captured_output.getvalue()
            if output.strip():
                return output
            
            return local_vars if local_vars else "Code executed successfully"
            
    except Exception as e:
        return {"error": f"Execution error: {str(e)}"}
    finally:
        # Restore stdout
        sys.stdout = old_stdout

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