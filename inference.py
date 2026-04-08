import os
import json
import asyncio
from openai import OpenAI
from server.environment import CloudCostEnv

# --- Configuration and Client Initialization ---
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.getenv("HF_TOKEN") 

client = OpenAI(
    base_url=API_BASE_URL,
    api_key=HF_TOKEN
)

# --- Required Logging Functions ---
def log_start(task, env, model):
    print(f"[START] task={task} env={env} model={model}")

def log_step(step, action, reward, done, error_message="null"):
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error={error_message}")

def log_end(success, steps, score, rewards):
    rewards_str = ",".join([f"{r:.2f}" for r in rewards])
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}")

async def run_task(task_name):
    env = CloudCostEnv()
    state = env.reset()
    total_reward = 0
    rewards = []

    log_start(task=task_name, env="cloud-cost-env", model=MODEL_NAME)

    for step in range(1, env.max_steps + 1):
        # 1. Create a clear prompt for the LLM
        state_json = json.dumps(state["servers"], indent=2)
        prompt = f"""
You are an expert FinOps agent. Your goal is to minimize cloud costs by terminating idle, non-critical servers.
RULES:
1. You MUST NOT terminate a server if 'is_critical' is true.
2. You SHOULD terminate a server if it is NOT critical and its 'cpu_usage' is low (e.g., under 40%).
3. If no servers should be terminated, you MUST respond with 'wait'.
CURRENT SERVER STATE:
{state_json}
AVAILABLE ACTIONS:
- "terminate <server_id>"
- "wait"
Respond with ONLY the action string.
"""

        action_str = "wait"
        action = {"action_type": "wait", "server_id": None}
        error_message = "null"

        try:
            # 2. Call the LLM
            completion = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=20,
                temperature=0.0
            )
            llm_response = completion.choices.message.content.strip()

            # 3. Parse Response
            parts = llm_response.split()
            if len(parts) == 2 and parts == "terminate" and parts in state["servers"]:
                action_str = llm_response
                action = {"action_type": "terminate", "server_id": parts}
            elif llm_response != "wait":
                error_message = f"invalid_response:_{llm_response[:10].replace(' ', '_')}"

        except Exception as e:
            # This line is now fixed to avoid the AttributeError
            error_message = f"api_error:_{type(e).__name__}"
            print(f"An error occurred during API call: {e}")

        # 4. Take action
        state, reward, done, info = env.step(action)
        total_reward += reward
        rewards.append(reward)

        log_step(step, action_str, reward, done, error_message=error_message)

        if done:
            break

    score = max(min(total_reward / 100, 1.0), 0.0)
    success = score > 0.5
    log_end(success, step, score, rewards)

async def main():
    tasks = ["task-1", "task-2", "task-3"]
    for task in tasks:
        await run_task(task)

if __name__ == "__main__":
    asyncio.run(main())
