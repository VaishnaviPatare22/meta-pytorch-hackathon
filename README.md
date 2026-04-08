---
title: Finops Optimizer
emoji: 🐳
colorFrom: purple
colorTo: gray
sdk: docker
app_port: 7860
pinned: false
---

# Cloud FinOps AI - OpenEnv Project

## 📌 Description
This project simulates a real-world cloud cost optimization problem. The AI agent decides which servers to terminate to save money while avoiding critical infrastructure failure.

## ⚙️ Files
- **server/environment.py** → Core environment logic
- **inference.py** → Main agent execution
- **server/app.py** → Streamlit UI
- **openenv.yaml** → Task definitions

## ▶️ How to Run locally
```bash
python -m streamlit run server/app.py