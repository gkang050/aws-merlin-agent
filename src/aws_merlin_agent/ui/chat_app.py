"""
MERLIN AI Agent Chat Interface

Conversational UI powered by Amazon Bedrock Agent Core with Nova/Claude reasoning.
Demonstrates autonomous agent capabilities for the AWS AI Agent Hackathon.
"""
import sys
import uuid
from pathlib import Path

import streamlit as st

# Add src to path for Streamlit Cloud deployment
src_path = Path(__file__).parent.parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from aws_merlin_agent.agent.workflows.agent_plan import MerlinAgentWorkflow

st.set_page_config(
    page_title="MERLIN AI Agent",
    page_icon="🧙‍♂️",
    layout="wide"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Header
st.title("🧙‍♂️ MERLIN AI Agent")
st.caption("Marketplace Earnings & Revenue Learning Intelligence Network")
st.markdown("---")

# Sidebar with info
with st.sidebar:
    st.header("About MERLIN")
    st.markdown("""
    MERLIN is an AI-powered agent for Amazon marketplace sellers, built with:
    
    - 🤖 **Amazon Bedrock Agent Core** - Autonomous orchestration
    - 🧠 **Amazon Nova Pro** - Reasoning LLM
    - 📊 **Amazon SageMaker** - ML forecasting
    - 🗄️ **AWS Data Platform** - S3, Glue, Athena
    
    **Capabilities:**
    - Natural language queries
    - Performance analysis
    - Demand forecasting
    - Actionable recommendations
    """)
    
    st.markdown("---")
    st.caption(f"Session: {st.session_state.session_id[:8]}...")
    
    if st.button("🔄 New Session"):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

# Initialize workflow
workflow = MerlinAgentWorkflow()

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Show trace if available
        if message.get("trace"):
            with st.expander("🔍 Agent Reasoning Trace"):
                st.json(message["trace"])

# Chat input
if prompt := st.chat_input("Ask MERLIN anything about your marketplace performance..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get agent response
    with st.chat_message("assistant"):
        with st.spinner("🧙‍♂️ MERLIN is thinking..."):
            try:
                response = workflow.conversational_query(
                    user_query=prompt,
                    session_id=st.session_state.session_id
                )
                
                agent_message = response.get("response", "I apologize, but I encountered an issue processing your request.")
                st.markdown(agent_message)
                
                # Show reasoning trace
                if response.get("trace"):
                    with st.expander("🔍 Agent Reasoning Trace"):
                        st.json(response["trace"])
                
                # Show tool outputs if any
                if response.get("tool_output"):
                    with st.expander("📊 Data Retrieved"):
                        st.json(response["tool_output"])
                
                # Save assistant message
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": agent_message,
                    "trace": response.get("trace"),
                    "tool_output": response.get("tool_output")
                })
                
            except Exception as e:
                error_msg = f"⚠️ Error: {str(e)}\n\nPlease ensure Bedrock model access is enabled in your AWS account."
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })

# Quick action buttons
st.markdown("---")
st.subheader("Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📈 Analyze Performance"):
        quick_prompt = "Analyze the performance of SKU-001 over the last 7 days and provide recommendations."
        st.session_state.messages.append({"role": "user", "content": quick_prompt})
        st.rerun()

with col2:
    if st.button("🔮 Forecast Demand"):
        quick_prompt = "Generate a demand forecast for SKU-001 and explain the key factors."
        st.session_state.messages.append({"role": "user", "content": quick_prompt})
        st.rerun()

with col3:
    if st.button("💡 Get Recommendations"):
        quick_prompt = "What are the top 3 actions I should take to improve my marketplace performance?"
        st.session_state.messages.append({"role": "user", "content": quick_prompt})
        st.rerun()

# Advanced mode (for testing)
with st.expander("🔧 Advanced: Direct Tool Access"):
    st.caption("For testing individual components")
    
    tab1, tab2 = st.tabs(["Performance Summary", "Forecast"])
    
    with tab1:
        sku = st.text_input("SKU", value="SKU-001", key="adv_sku")
        if st.button("Get Summary", key="adv_summary"):
            with st.spinner("Fetching data..."):
                try:
                    result = workflow.summarize_performance(sku)
                    st.success("Summary Generated")
                    st.markdown(f"**Narrative:** {result['narrative']}")
                    st.json(result['rows'])
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with tab2:
        sku_forecast = st.text_input("SKU for Forecast", value="SKU-001", key="adv_forecast_sku")
        if st.button("Generate Forecast", key="adv_forecast"):
            with st.spinner("Running ML model..."):
                try:
                    forecast = workflow.forecast(sku=sku_forecast)
                    st.success("Forecast Complete")
                    st.json(forecast)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
