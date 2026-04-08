import streamlit as st
import pandas as pd
from environment import CloudCostEnv
import os

# --- 1. OPENENV VALIDATION LOGIC (MANDATORY FOR PHASE 1) ---
query_params = st.query_params
if "action" in query_params and query_params["action"] == "reset":
    st.session_state.env = CloudCostEnv()
    st.session_state.current_state = st.session_state.env.reset()
    st.session_state.logs = ["Environment Reset by Validator"]
    st.write("OK")
    st.stop()

# --- 2. PAGE CONFIG & STYLING ---
st.set_page_config(page_title="FinOps AI Optimizer", page_icon="☁️", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric {
        background-color: #161b22;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #30363d;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #238636;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. INITIALIZATION ---
if 'env' not in st.session_state:
    st.session_state.env = CloudCostEnv()
    st.session_state.current_state = st.session_state.env.reset()
    st.session_state.logs = []

env = st.session_state.env

# --- 4. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/100/cloud-lighting.png", width=80)
    st.title("FinOps Control")
    st.info("Agent: Rule-Based-V1")
    st.divider()
    if st.button("Reset Environment 🔄"):
        st.session_state.env = CloudCostEnv()
        st.session_state.current_state = st.session_state.env.reset()
        st.session_state.logs = []
        st.rerun()

# --- 5. MAIN DASHBOARD ---
st.title("☁️ Cloud FinOps AI Optimizer")
st.caption("Monitoring & Automated Cost Reduction Engine")

m1, m2, m3, m4 = st.columns(4)
m1.metric("💰 Total Saved", f"${env.total_money_saved}")
m2.metric("⏳ Progress", f"{env.current_step}/{env.max_steps}")

is_failed = any(s['is_critical'] and s['status'] == 'terminated' for s in env.servers.values())
if is_failed:
    m3.error("Status: CRITICAL FAILURE")
    m4.metric("Risk Level", "HIGH", delta_color="inverse")
else:
    m3.success("Status: STABLE")
    m4.metric("Risk Level", "LOW")

st.divider()

col_left, col_right = st.columns(2) # Left is wider

with col_left:
    st.subheader("🖥️ Real-time Server Inventory")
    df = pd.DataFrame.from_dict(st.session_state.current_state['servers'], orient='index')
    
    def style_status(val):
        color = '#238636' if val == 'running' else '#da3633'
        return f'color: white; background-color: {color}; font-weight: bold; padding: 2px; border-radius: 5px'
    
    df_display = df.copy()
    df_display.columns = ['CPU %', 'Cost/hr', 'Critical', 'Status']
    st.dataframe(df_display.style.map(style_status, subset=['Status']), use_container_width=True)

with col_right:
    st.subheader("🤖 Agent Control")
    if env.current_step < env.max_steps and not is_failed:
        selected_server = st.selectbox("Identify Target Server:", list(env.servers.keys()))
        if st.button("🚀 Execute Termination", type="primary"):
            state, reward, done, info = env.step({"action_type": "terminate", "server_id": selected_server})
            st.session_state.current_state = state
            st.session_state.logs.insert(0, f"Step {env.current_step}: {info} (Rew: {reward})")
            st.rerun()
    elif is_failed:
        st.error("System offline due to critical failure.")
    else:
        st.success("🏁 Simulation Cycle Complete")

st.divider()
st.subheader("📜 System Event Logs")
if not st.session_state.logs:
    st.caption("No events recorded yet.")
for log in st.session_state.logs:
    if "SUCCESS" in log:
        st.success(log, icon="✅")
    elif "DISASTER" in log:
        st.error(log, icon="🚨")
    elif "WARNING" in log:
        st.warning(log, icon="⚠️")
    else:
        st.info(log, icon="ℹ️")