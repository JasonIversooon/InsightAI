import pandas as pd
import plotly.express as px

def run_user_code(code, df):
    safe_globals = {"__builtins__": {}, "pd": pd, "df": df, "px": px}
    local_vars = {}
    try:
        # Try to evaluate as an expression first
        try:
            result = eval(code, safe_globals, local_vars)
            return result
        except SyntaxError:
            exec(code, safe_globals, local_vars)
            return local_vars
    except Exception as e:
        return {"error": str(e)}