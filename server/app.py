import streamlit as st
import pandas as pd
import os
from environment import CloudCostEnv

# --- PAGE CONFIG ---
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

# --- DASHBOARD ---
st.title("Cloud FinOps AI Optimizer")

m1, m2, m3, m4 = st.columns(4)

m1.metric("Total Saved", f"${env.total_money_saved}")
m2.metric("Step", f"{env.current_step}/{env.max_steps}")

# --- FAILURE CHECK ---
is_failed = any(
    s['is_critical'] and s['status'] == 'terminated'
    for s in env.servers.values()
)

if is_failed:
    m3.error("CRITICAL FAILURE")
    m4.metric("Risk Level", "HIGH")
else:
    m3.success("STABLE")
    m4.metric("Risk Level", "LOW")

st.divider()

# --- MAIN LAYOUT ---
col_left, col_right = st.columns(2)

# --- SERVER TABLE ---
with col_left:
    st.subheader("Server Inventory")
    
    df = pd.DataFrame.from_dict(
        st.session_state.current_state['servers'],
        orient='index'
    )

    df_display = df.copy()
    df_display.columns = ['CPU %', 'Cost/hr', 'Critical', 'Status']
    
    st.dataframe(df_display, use_container_width=True)

# --- CONTROL PANEL ---
with col_right:
    st.subheader("Manual Control")
    
    if env.current_step < env.max_steps and not is_failed:
        selected_server = st.selectbox(
            "Select Server:",
            list(env.servers.keys())
        )

        if st.button("Terminate Server"):
            state, reward, done, info = env.step({
                "action_type": "terminate",
                "server_id": selected_server
            })

            st.session_state.current_state = state
            st.session_state.logs.insert(
                0,
                f"Step {env.current_step}: {info} (Reward: {reward})"
            )
            st.rerun()

    elif is_failed:
        st.error("System offline due to critical failure.")
    else:
        st.success("Simulation Complete ✅")

# --- LOGS ---
st.divider()
st.subheader("Event Logs")

for log in st.session_state.logs:
    st.text(log)