import os
import json
from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
from environment import CloudCostEnv

client = OpenAI(
    base_url=os.getenv("API_BASE_URL", "https://api.openai.com/v1"),
    api_key=os.getenv("API_KEY", "dummy-key")
)

# --- FastAPI App ---
app = FastAPI()

# --- Request Model ---
class ResetRequest(BaseModel):
    task_id: str
    seed: int = 42

# --- RESET ENDPOINT ---
@app.post("/reset")
def reset(req: Optional[ResetRequest] = None):
    task_id = req.task_id if req else "default_task"
    seed = req.seed if req else 42

    env = CloudCostEnv()
    state = env.reset(seed=seed)

    return {
        "task_id": task_id,
        "seed": seed,
        "observation": state
    }

# --- LOGGING FUNCTIONS ---
def log_start(task, env, model):
    print(f"[START] task={task} env={env} model={model}")

def log_step(step, action, reward, done, error_message="null"):
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error={error_message}")

def log_end(success, steps, score, rewards):
    rewards_str = ",".join([f"{r:.2f}" for r in rewards])
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}")

# --- LLM DECISION FUNCTION ---
def get_action_from_llm(state):
    prompt = f"""
You are a FinOps AI agent.

Terminate servers that:
- are NOT critical
- have CPU < 40

Otherwise return: wait

Servers:
{json.dumps(state['servers'], indent=2)}

Respond ONLY:
terminate <server_id>
OR
wait
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("LLM Error:", e)
        return "wait"

# --- TASK RUNNER ---
def run_task(task_name):
    env = CloudCostEnv()
    state = env.reset()
    total_reward = 0
    rewards = []

    log_start(task=task_name, env="cloud-cost-env", model="llm")

    for step in range(1, env.max_steps + 1):

        action_str = get_action_from_llm(state)
        error_message = "null"

        parts = action_str.split()
        action = {"action_type": "wait", "server_id": None}

        if len(parts) == 2 and parts[0] == "terminate" and parts[1] in state["servers"]:
            action = {"action_type": "terminate", "server_id": parts[1]}
        elif action_str != "wait":
            error_message = f"invalid_response:_{action_str}"

        state, reward, done, info = env.step(action)

        total_reward += reward
        rewards.append(reward)

        log_step(step, action_str, reward, done, error_message)

        if done:
            break

    score = max(min(total_reward / 100, 1.0), 0.0)
    success = score > 0.5

    log_end(success, step, score, rewards)

# --- ROOT ENDPOINT ---
@app.get("/")
def home():
    return {"message": "FinOps Optimizer API Running 🚀"}

# --- LOCAL TEST ---
if __name__ == "__main__":
    tasks = ["task-1", "task-2", "task-3"]
    for task in tasks:
        run_task(task)