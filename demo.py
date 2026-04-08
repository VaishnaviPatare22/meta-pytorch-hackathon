import time
from environment import CloudCostEnv

def run_hackathon_demo():
    print("=== STARTING CLOUD FINOPS ENVIRONMENT ===")
    
    # 1. Initialize the environment
    env = CloudCostEnv()
    
    # 2. Reset the environment to get the starting state
    current_state = env.reset()
    print("\n[INITIAL STATE]:")
    for s_id, s_data in current_state['servers'].items():
        print(f" - {s_id}: CPU {s_data['cpu_usage']}%, Cost ${s_data['cost_per_hour']}/hr, Critical: {s_data['is_critical']}")
    
    time.sleep(2)

    # 3. Simulate an AI Agent making 3 decisions
    
    # Move 1: The AI correctly identifies an idle server and kills it
    print("\n--- STEP 1 ---")
    print("AI ACTION: Terminate 'server_1_idle'")
    state, reward, done, info = env.step({"action_type": "terminate", "server_id": "server_1_idle"})
    print(f"RESULT: {info}")
    print(f"CURRENT REWARD: {reward}")
    time.sleep(2)
    
    # Move 2: The AI makes a mistake and kills the database
    print("\n--- STEP 2 ---")
    print("AI ACTION: Terminate 'server_2_database'")
    state, reward, done, info = env.step({"action_type": "terminate", "server_id": "server_2_database"})
    print(f"RESULT: {info}")
    print(f"CURRENT REWARD: {reward}")
    time.sleep(2)
    
    # Move 3: The AI makes a smart move and kills the other idle server
    print("\n--- STEP 3 ---")
    print("AI ACTION: Terminate 'server_3_idle'")
    state, reward, done, info = env.step({"action_type": "terminate", "server_id": "server_3_idle"})
    print(f"RESULT: {info}")
    print(f"CURRENT REWARD: {reward}")
    time.sleep(2)
    
    print("\n=== DEMO FINISHED ===")
    print(f"Total Money Saved for the Company: ${state['money_saved']}")

if __name__ == "__main__":
    run_hackathon_demo()