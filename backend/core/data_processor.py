# backend/core/data_processor.py
import json
import re
import pandas as pd
import plotly.express as px
import logging
from typing import Optional, Tuple, Dict, Any
import traceback
import sys
import io

logger = logging.getLogger(__name__)

class DataProcessor:
    """
    Handles data processing and code execution for the FastAPI backend.
    This class is completely AI-driven without hardcoded assumptions.
    """
    
    def __init__(self):
        self.context = {}
    
    def reset_context(self):
        """Reset any stored context"""
        self.context = {}
    
    def process_llm_response(self, llm_response: str, df: pd.DataFrame, user_question: str) -> Tuple[Any, Optional[Dict]]:
        """
        Process LLM response and execute code with improved error handling
        
        Args:
            llm_response: Raw response from the LLM
            df: The dataframe to operate on
            user_question: Original user query
            
        Returns:
            Tuple of (result, visualization_dict)
        """
        try:
            logger.info(f"Processing LLM response: {llm_response[:200]}...")
            
            # Parse the response to extract code
            code, answer = self._parse_response(llm_response)
            
            if not code:
                logger.warning("No code found in LLM response")
                return {
                    'answer': "No code was generated for your query. Please try rephrasing your question."
                }, None

            logger.info(f"Extracted code length: {len(code)}")
            logger.info(f"Code preview: {code[:200]}...")
            
            # Execute the code
            result, visualization = self._execute_code(code, df)
            logger.info(f"Code execution completed. Result: {result}")
            
            # Return the result with answer
            if answer:
                return {'answer': answer, 'result': result}, visualization
            else:
                return {'answer': f"Analysis completed: {result}"}, visualization
                
        except Exception as e:
            logger.error(f"Error processing LLM response: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                'answer': "I encountered an error processing your request. Please try rephrasing your question."
            }, None
    
    def _parse_response(self, response: str) -> Tuple[str, Optional[str]]:
        """
        Parse LLM response to extract code and answer with improved robustness
        """
        print(f"DEBUG: Parsing response: {response[:500]}...")
        
        # Clean the response
        cleaned_response = response.strip()
        
        # Try to parse as JSON first
        try:
            # Remove any markdown code blocks
            if "```" in cleaned_response:
                # Extract content between first pair of triple backticks
                start = cleaned_response.find("```")
                end = cleaned_response.find("```", start + 3)
                if end != -1:
                    cleaned_response = cleaned_response[start+3:end].strip()
                    # Remove language identifier if present
                    if cleaned_response.startswith(('json', 'python')):
                        lines = cleaned_response.split('\n')
                        cleaned_response = '\n'.join(lines[1:])
        
            # Try direct JSON parse
            data = json.loads(cleaned_response)
            code = data.get("code", "")
            answer = data.get("answer", "")
            
            print(f"DEBUG: Successfully parsed JSON. Code length: {len(code)}")
            return code, answer
            
        except json.JSONDecodeError as e:
            print(f"DEBUG: JSON decode failed: {e}")
            
            # Fallback: Try to extract JSON using regex
            import re
            json_pattern = r'\{[^{}]*"tool"[^{}]*"code"[^{}]*"answer"[^{}]*\}'
            matches = re.findall(json_pattern, cleaned_response, re.DOTALL)
            
            if matches:
                try:
                    data = json.loads(matches[0])
                    code = data.get("code", "")
                    answer = data.get("answer", "")
                    print(f"DEBUG: Regex extraction successful. Code length: {len(code)}")
                    return code, answer
                except:
                    pass
            
            # Another fallback: look for code between quotes after "code":
            code_match = re.search(r'"code":\s*"([^"]+)"', cleaned_response)
            answer_match = re.search(r'"answer":\s*"([^"]+)"', cleaned_response)
            
            if code_match:
                code = code_match.group(1).replace('\\n', '\n').replace('\\"', '"')
                answer = answer_match.group(1) if answer_match else "Analysis completed"
                print(f"DEBUG: Fallback extraction successful. Code length: {len(code)}")
                return code, answer
            
            print(f"DEBUG: All parsing methods failed")
            return "", None
    
    def _execute_code(self, code: str, df: pd.DataFrame) -> Tuple[Any, Optional[Dict]]:
        """
        Execute the extracted code safely with comprehensive logging
        """
        try:
            logger.info(f"Starting code execution...")
            logger.info(f"DataFrame shape: {df.shape}")
            logger.info(f"DataFrame columns: {df.columns.tolist()}")
            
            # Capture print statements
            old_stdout = sys.stdout
            sys.stdout = captured_output = io.StringIO()
            
            # Create a safe execution environment
            namespace = {
                'df': df.copy(),
                'pd': pd,
                'px': px,
                'viz': self._create_visualization,
                'result': None,
                'fig': None,
                'print': print  # Ensure print works
            }
            
            logger.info(f"Executing code: {code}")
            
            # Execute the code
            exec(code, namespace)
            
            # Restore stdout and get captured output
            sys.stdout = old_stdout
            output = captured_output.getvalue()
            
            logger.info(f"Code execution output: {output}")
            
            # Get the result
            result = namespace.get('result', 'Analysis completed')
            fig = namespace.get('fig', None)
            
            logger.info(f"Result from namespace: {result}")
            logger.info(f"Figure object: {fig is not None}")
            
            # Convert Plotly figure to dict if present
            visualization = None
            if fig is not None:
                try:
                    visualization = fig.to_dict()
                    logger.info("Visualization created successfully")
                except Exception as e:
                    logger.error(f"Error converting visualization: {e}")
            
            return result, visualization
            
        except Exception as e:
            # Restore stdout
            sys.stdout = old_stdout
            logger.error(f"Code execution failed: {e}")
            logger.error(f"Code was: {code}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return f"Error executing code: {str(e)}", None
    
    def _create_visualization(self, chart_type: str, data: pd.DataFrame, **kwargs) -> Any:
        """
        Create visualizations using Plotly Express
        """
        try:
            logger.info(f"Creating {chart_type} chart with data shape: {data.shape}")
            logger.info(f"Chart kwargs: {kwargs}")
            
            chart_type = chart_type.lower()
            
            if chart_type == 'bar':
                fig = px.bar(data, **kwargs)
            elif chart_type == 'line':
                fig = px.line(data, **kwargs)
            elif chart_type == 'scatter':
                fig = px.scatter(data, **kwargs)
            elif chart_type == 'pie':
                fig = px.pie(data, **kwargs)
            elif chart_type == 'histogram':
                fig = px.histogram(data, **kwargs)
            elif chart_type == 'box':
                fig = px.box(data, **kwargs)
            elif chart_type == 'area':
                fig = px.area(data, **kwargs)
            elif chart_type == 'heatmap':
                fig = px.imshow(data, **kwargs)
            elif chart_type == 'stacked_bar':
                fig = px.bar(data, **kwargs)
            else:
                logger.warning(f"Unknown chart type: {chart_type}, defaulting to bar")
                fig = px.bar(data, **kwargs)
            
            logger.info(f"Chart created successfully")
            return fig
                
        except Exception as e:
            logger.error(f"Error creating visualization: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise