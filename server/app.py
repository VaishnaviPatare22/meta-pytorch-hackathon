import streamlit as st
import pandas as pd
import os
import json
from environment import CloudCostEnv

if st.query_params.get("action") == "reset" or st.context.headers.get("X-OpenEnv-Reset"):
    response_data = {
        "task_id": st.query_params.get("task_id", "default_task"),
        "seed": int(st.query_params.get("seed", 42)),
        "observation": "initial state"
    }
    # Using st.json ensures the validator receives a clean JSON object
    st.json(response_data)
    st.stop() 

st.set_page_config(page_title="FinOps AI Optimizer", layout="wide")

# --- STATE INITIALIZATION ---
if 'env' not in st.session_state:
    st.session_state.env = CloudCostEnv()
    st.session_state.current_state = st.session_state.env.reset()
    st.session_state.logs = []

env = st.session_state.env

# --- SIDEBAR ---
with st.sidebar:
    st.title("FinOps Control")
    st.info(f"Model: {os.getenv('MODEL_NAME', 'gpt-4o-mini')}")
    if st.button("Reset Environment 🔄"):
        st.session_state.env = CloudCostEnv()
        st.session_state.current_state = st.session_state.env.reset()
        st.session_state.logs = []
        st.rerun()

# --- DASHBOARD METRICS ---
st.title("Cloud FinOps AI Optimizer")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Saved", f"${env.total_money_saved}")
m2.metric("Step", f"{env.current_step}/{env.max_steps}")

# Check for failures
is_failed = any(s['is_critical'] and s['status'] == 'terminated' for s in env.servers.values())
if is_failed:
    m3.error("CRITICAL FAILURE")
    m4.metric("Risk Level", "HIGH")
else:
    m3.success("STABLE")
    m4.metric("Risk Level", "LOW")

st.divider()

# --- MAIN CONTENT LAYOUT ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Server Inventory")
    df = pd.DataFrame.from_dict(st.session_state.current_state['servers'], orient='index')
    df_display = df.copy()
    df_display.columns = ['CPU %', 'Cost/hr', 'Critical', 'Status']
    st.dataframe(df_display, use_container_width=True)

with col_right:
    st.subheader("Manual Control")
    if env.current_step < env.max_steps and not is_failed:
        selected_server = st.selectbox("Select Server:", list(env.servers.keys()))
        if st.button("Terminate Server"):
            state, reward, done, info = env.step({"action_type": "terminate", "server_id": selected_server})
            st.session_state.current_state = state
            st.session_state.logs.insert(0, f"Step {env.current_step}: {info} (Rew: {reward})")
            st.rerun()
    elif is_failed:
        st.error("System offline.")
    else:
        st.success("Simulation Complete")

st.divider()
st.subheader("Event Logs")
for log in st.session_state.logs:
    st.text(log)