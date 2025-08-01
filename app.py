import streamlit as st
import pandas as pd
from core.data_context import generate_data_context
from agents.agent import ask_llm
from core.tools import run_user_code
import json

st.title("InsightBot: Your Conversational Data Analyst")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    # Try to read the file with the default encoding
    try:
        df = pd.read_csv(uploaded_file)
    except UnicodeDecodeError:
        # If there's a UnicodeDecodeError, try reading the file with 'latin1' encoding
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file, encoding="latin1")
    
    st.success("Data loaded!")
    context = generate_data_context(df)
    st.subheader("Data Context Summary")
    st.text(context)
    st.write("Ask me anything about your data in the next steps!")

    # --- Chat Section ---
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    def clear_input():
        st.session_state["user_input"] = ""

    user_input = st.text_input("You:", key="user_input")
    if st.button("Send", key="send_button") and user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.write(f"[DEBUG] User input: {user_input}")
        try:
            bot_response = ask_llm(
                user_input,
                context,
                st.session_state.chat_history
            )
            st.write(f"[DEBUG] LLM raw response: {bot_response}")
            tool_json = json.loads(bot_response)
            st.write(f"[DEBUG] Parsed tool_json: {tool_json}")
            tool = tool_json.get("tool")
            code = tool_json.get("code")
            st.write(f"[DEBUG] Tool: {tool}, Code: {code}")
            result = run_user_code(code, df)
            st.write(f"[DEBUG] Code execution result: {result}")
            if tool == "DataQueryTool":
                st.session_state.chat_history.append({"role": "bot", "content": str(result)})
            elif tool == "VisualizationTool" and "fig" in result:
                st.session_state.chat_history.append({"role": "bot", "content": "Here is the chart:"})
                st.session_state["last_fig"] = result["fig"]
            else:
                st.session_state.chat_history.append({"role": "bot", "content": str(result)})
        except Exception as e:
            st.session_state.chat_history.append({"role": "bot", "content": f"Error parsing LLM response: {e}"})
            st.write(f"[DEBUG] Exception: {e}")

    st.subheader("Chat History")
    for msg in st.session_state.chat_history:
        st.markdown(f"**{msg['role'].capitalize()}:** {msg['content']}")
    if "last_fig" in st.session_state:
        st.plotly_chart(st.session_state["last_fig"])
else:
    st.info("Please upload a CSV file to get started.")
