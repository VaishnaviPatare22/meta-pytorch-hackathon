from environment import CloudCostEnv

# --- REQUIRED MAIN FUNCTION ---
def main():
    env = CloudCostEnv()
    state = env.reset()

    total_reward = 0

    for step in range(1, env.max_steps + 1):

        # Simple rule-based logic
        action = {"action_type": "wait", "server_id": None}

        for sid, server in state["servers"].items():
            if not server["is_critical"] and server["cpu_usage"] < 40:
                action = {"action_type": "terminate", "server_id": sid}
                break

        state, reward, done, info = env.step(action)
        total_reward += reward

        if done:
            break

    return {
        "success": total_reward > 0,
        "total_reward": total_reward
    }

# --- IMPORTANT ---
if __name__ == "__main__":
    print(main())