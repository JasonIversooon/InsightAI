# backend/core/data_processor.py
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import re
from typing import Tuple, Dict, Any, Optional
from utils.tools import run_user_code

class DataProcessor:
    """
    Handles data processing and code execution for the FastAPI backend.
    This class is completely AI-driven without hardcoded assumptions.
    """
    
    def __init__(self):
        self.execution_context = {}
    
    def process_llm_response(self, bot_response: str, df: pd.DataFrame, user_input: str) -> Tuple[Any, Optional[Dict]]:
        """
        Process the LLM response and execute generated code safely.
        
        Args:
            bot_response: Raw response from the LLM
            df: The dataframe to operate on
            user_input: Original user query
            
        Returns:
            Tuple of (result, visualization_dict)
        """
        try:
            # Clean and parse the LLM response
            cleaned_response = self._clean_response(bot_response)
            code, answer_template = self._parse_response(cleaned_response)
            
            if not code or not code.strip():
                return "No code was generated for your query. Please try rephrasing your question.", None

            # Execute the generated code
            execution_result = self._execute_code_safely(code, df)
            
            if isinstance(execution_result, dict) and 'error' in execution_result:
                return f"Error executing analysis: {execution_result['error']}", None

            # Extract visualization and prepare response
            visualization = self._extract_visualization(execution_result)
            final_answer = self._generate_response(execution_result, answer_template, user_input)

            return {
                'result': execution_result.get('result') if isinstance(execution_result, dict) else execution_result,
                'answer': final_answer,
                'code_executed': code,
                'visualization': visualization
            }, visualization

        except Exception as e:
            error_msg = f"Error processing your request: {str(e)}"
            print(f"DataProcessor error: {error_msg}")
            return error_msg, None

    def _clean_response(self, response: str) -> str:
        """Remove markdown code block markers and clean the response."""
        cleaned = response.strip()
        
        # Remove code block markers
        if cleaned.startswith('```'):
            lines = cleaned.split('\n')
            # Skip the first line if it's just ```python or ```
            if len(lines) > 1 and (lines[0] == '```' or lines[0].startswith('```')):
                cleaned = '\n'.join(lines[1:])
        
        if cleaned.endswith('```'):
            cleaned = cleaned.rsplit('```', 1)[0]
        
        return cleaned.strip()

    def _parse_response(self, cleaned_response: str) -> Tuple[str, Optional[str]]:
        """Parse the cleaned response to extract code and answer template."""
        try:
            # Try to parse as JSON first
            tool_json = json.loads(cleaned_response)
            code = tool_json.get("code", "")
            answer_template = tool_json.get("answer", "")
            return code, answer_template
        except json.JSONDecodeError:
            # If not JSON, treat the entire response as code
            return cleaned_response, None

    def _execute_code_safely(self, code: str, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Execute the generated code with proper error handling and context management.
        """
        try:
            # Normalize dataframe reference (replace 'data' with 'df' if needed)
            code = re.sub(r'\bdata\b(?!\w)', 'df', code)
            
            # Split code into lines for sequential execution
            code_lines = [line.strip() for line in code.split('\n') if line.strip()]
            
            # Initialize execution context
            local_vars = self.execution_context.copy()
            execution_result = {}
            
            # Execute each line
            for i, line in enumerate(code_lines):
                try:
                    # Skip comments and empty lines
                    if line.startswith('#') or not line:
                        continue
                    
                    # Execute the line
                    local_vars = run_user_code(line, df, local_vars)
                    
                    # Check for execution errors
                    if isinstance(local_vars, dict) and 'error' in local_vars:
                        return {'error': f"Error in line {i+1}: {local_vars['error']}"}
                    
                    execution_result = local_vars
                    
                except Exception as line_error:
                    return {'error': f"Error executing line {i+1} ('{line}'): {str(line_error)}"}
            
            # Update execution context for future use
            self.execution_context.update(local_vars)
            
            return execution_result if execution_result else {'result': 'Code executed successfully'}
            
        except Exception as e:
            return {'error': f"Code execution failed: {str(e)}"}

    def _extract_visualization(self, result: Any) -> Optional[Dict]:
        """Extract plotly visualization from execution result."""
        if isinstance(result, dict):
            # Look for 'fig' variable (plotly figure)
            fig = result.get('fig')
            if fig and hasattr(fig, 'to_dict'):
                try:
                    return fig.to_dict()
                except Exception as e:
                    print(f"Error converting figure to dict: {e}")
                    return None
        return None

    def _generate_response(self, result: Any, answer_template: Optional[str], user_input: str) -> str:
        """
        Generate a human-readable response from the execution result.
        This is completely dynamic based on the actual results.
        """
        # Priority 1: Use answer template from LLM if available
        if answer_template and answer_template.strip():
            return answer_template
        
        # Priority 2: Extract answer from result
        if isinstance(result, dict):
            # Check for explicit answer field
            if 'answer' in result and result['answer']:
                return str(result['answer'])
            
            # Check for result field and format it appropriately
            if 'result' in result and result['result'] is not None:
                return self._format_result_value(result['result'])
            
            # Check for any meaningful output
            for key, value in result.items():
                if key not in ['fig', 'error', 'code_executed'] and value is not None:
                    return self._format_result_value(value)
        
        # Priority 3: Format non-dict results
        elif isinstance(result, str):
            return result
        
        # Fallback
        return "Analysis completed. Please check the visualization for insights."

    def _format_result_value(self, result_value: Any) -> str:
        """Format any result value into a human-readable string."""
        try:
            # Handle pandas Series (common for groupby results)
            if hasattr(result_value, 'iloc') and hasattr(result_value, 'index'):
                if len(result_value) > 0:
                    # For Series with named index
                    if hasattr(result_value, 'name') and result_value.name:
                        top_item = result_value.index[0]
                        top_value = result_value.iloc[0]
                        if isinstance(top_value, (int, float)):
                            return f"The top result is '{top_item}' with a value of {top_value:,.2f}"
                        else:
                            return f"The top result is: {top_item}"
                    else:
                        return f"Top result: {result_value.iloc[0]}"
                else:
                    return "No results found."
            
            # Handle pandas DataFrame
            elif hasattr(result_value, 'iloc') and hasattr(result_value, 'columns'):
                if len(result_value) > 0:
                    return f"Found {len(result_value)} results. Check the visualization for details."
                else:
                    return "No results found in the data."
            
            # Handle numeric values
            elif isinstance(result_value, (int, float)):
                if isinstance(result_value, float):
                    return f"The result is: {result_value:,.2f}"
                else:
                    return f"The result is: {result_value:,}"
            
            # Handle strings and other types
            else:
                return f"Result: {str(result_value)}"
                
        except Exception:
            return f"Analysis completed with result: {str(result_value)[:100]}"

    def reset_context(self):
        """Reset the execution context (useful for new data uploads)."""
        self.execution_context = {}