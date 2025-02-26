# File: dashboard/app.py

import streamlit as st
import os
import sys
import threading
import time
import queue  # For thread-safe communication

# Append the path to the Core_Workflow directory
core_workflow_path = os.path.join(os.path.dirname(__file__), '..', 'Core_Workflow')
sys.path.append(core_workflow_path)

from agent_langchain import run_agent, get_logs

# Set up the Streamlit page
st.set_page_config(page_title="AgenticAI Dashboard", layout="wide")

# Custom CSS for styling
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] { background-color: #add1ad; }
    .report-box { background-color: #F5F5F5; padding: 20px; border-radius: 10px; border: 1px solid #17A2B8; }
    .thinking-text { color: #A9A9A9; font-family: 'Courier New', Courier, monospace; }
    hr { border: 1px solid #17A2B8; }
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar setup
st.sidebar.title("AgenticAI Control Panel")
query_input = st.sidebar.text_input("Enter your query", "Analyze the DPZ stock, should I buy it in Feb 2025?")
if st.sidebar.button("Generate Report", key="generate", help="Click to analyze"):
    st.session_state["query"] = query_input

# Main dashboard title with teal color
st.markdown('<h1 style="color: #17A2B8;">AgenticAI Report Dashboard</h1>', unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# Process the query if it exists
if "query" in st.session_state:
    query = st.session_state["query"]
    st.markdown(f'<h3 style="color: #17A2B8;">Report for: {query}</h3>', unsafe_allow_html=True)
    
    # Placeholder for real-time log updates
    thinking_container = st.empty()
    
    # Create a queue to pass the report from the thread
    report_queue = queue.Queue()
    
    # Define the function to run in the background thread
    def generate_report():
        try:
            report = run_agent(query)  # Generate the report
            report_queue.put({"status": "success", "report": report})
        except Exception as e:
            report_queue.put({"status": "error", "message": str(e)})
    
    # Start the background thread
    thread = threading.Thread(target=generate_report)
    thread.start()
    
    # Display logs in real-time while the thread runs
    with st.spinner("Analyzing your query..."):
        while thread.is_alive():
            logs = get_logs()
            thinking_container.markdown(
                f'<div class="thinking-text">#### Thinking...\n{logs}</div>',
                unsafe_allow_html=True
            )
            time.sleep(0.5)  # Refresh logs every half second
    
    # Wait for the thread to finish
    thread.join()
    
    # Retrieve the result from the queue
    result = report_queue.get()
    if result["status"] == "success":
        report = result["report"]
        with st.expander("View Report", expanded=True):
            thinking_container.markdown(
                f'<div class="report-box">{report}</div>',
                unsafe_allow_html=True
            )
    else:
        st.error(f"Error generating report: {result['message']}")