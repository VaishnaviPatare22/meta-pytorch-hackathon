import random

class CloudCostEnv:
    def __init__(self):
        # Setup the basic rules of the environment
        self.max_steps = 5  # The AI has 5 turns to save as much money as possible
        self.current_step = 0
        self.total_money_saved = 0.0
        self.servers = {}

    def reset(self):
        """
        Wipes the environment clean and generates a new random data center.
        """
        self.current_step = 0
        self.total_money_saved = 0.0
        
        # We generate 3 fake servers for the AI to manage
        self.servers = {
            "server_1_idle": {"cpu_usage": 2, "cost_per_hour": 5.0, "is_critical": False, "status": "running"},
            "server_2_database": {"cpu_usage": 85, "cost_per_hour": 12.0, "is_critical": True, "status": "running"},
            "server_3_idle": {"cpu_usage": 5, "cost_per_hour": 3.0, "is_critical": False, "status": "running"}
        }
        
        return self.state()

    def state(self):
        """
        Returns what the AI 'sees' right now.
        """
        return {
            "step": self.current_step,
            "money_saved": self.total_money_saved,
            "servers": self.servers
        }

    def step(self, action):
        """
        The AI sends an action here. We calculate the reward and update the world.
        Expected action format: {"action_type": "terminate", "server_id": "server_1"}
        """
        self.current_step += 1
        reward = 0
        info = "" # Text explanation of what happened
        
        action_type = action.get("action_type")
        server_id = action.get("server_id")

        # RULE 1: Did the AI choose to terminate a server?
        if action_type == "terminate" and server_id in self.servers:
            server = self.servers[server_id]
            
            if server["status"] == "terminated":
                # AI made a mistake, tried to kill a dead server.
                reward -= 5 
                info = f"Penalty: {server_id} was already terminated."
                
            else:
                server["status"] = "terminated"
                
                # RULE 2: Did the AI kill a critical server? (Bad!)
                if server["is_critical"]:
                    reward -= 100
                    info = f"DISASTER: AI terminated a critical database! Website crashed. (-100)"
                
                # RULE 3: Did the AI kill an idle server? (Good!)
                elif server["cpu_usage"] < 10:
                    reward += 50
                    self.total_money_saved += server["cost_per_hour"] * 24 # Saved a full day of costs
                    info = f"SUCCESS: AI terminated idle {server_id}. Saved money! (+50)"
                    
                # RULE 4: AI killed an active non-critical server
                else:
                    reward -= 10
                    info = f"WARNING: Terminated active server {server_id}. Users disrupted. (-10)"
                    
        else:
            # AI chose to wait or sent an invalid command
            reward -= 1
            info = "AI chose to wait or sent invalid command. Wasted a turn."

        # Check if the game is over
        done = self.current_step >= self.max_steps

        # Return standard OpenEnv output
        return self.state(), reward, done, info