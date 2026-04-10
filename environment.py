import random

class CloudCostEnv:
    def __init__(self):
        self.max_steps = 10
        self.current_step = 0
        self.total_money_saved = 0
        self.servers = {}

    # --- RESET ENVIRONMENT ---
    def reset(self, seed=42):
        random.seed(seed)
        self.current_step = 0
        self.total_money_saved = 0

        # Create sample servers
        self.servers = {
            "server-1": {
                "cpu_usage": random.randint(10, 90),
                "cost_per_hour": 5,
                "is_critical": False,
                "status": "running"
            },
            "server-2": {
                "cpu_usage": random.randint(10, 90),
                "cost_per_hour": 10,
                "is_critical": True,
                "status": "running"
            },
            "server-3": {
                "cpu_usage": random.randint(10, 90),
                "cost_per_hour": 3,
                "is_critical": False,
                "status": "running"
            },
            "server-4": {
                "cpu_usage": random.randint(10, 90),
                "cost_per_hour": 7,
                "is_critical": False,
                "status": "running"
            }
        }

        return {"servers": self.servers}

    # --- STEP FUNCTION ---
    def step(self, action):
        self.current_step += 1
        reward = 0
        done = False
        info = "no action"

        if action["action_type"] == "terminate":
            server_id = action["server_id"]

            if server_id in self.servers:
                server = self.servers[server_id]

                if server["status"] == "terminated":
                    reward = -5
                    info = "already terminated ⚠️"

                elif server["is_critical"]:
                    reward = -50
                    server["status"] = "terminated"
                    info = "terminated critical server ❌"

                else:
                    reward = 10
                    self.total_money_saved += server["cost_per_hour"]
                    server["status"] = "terminated"
                    info = "terminated idle server ✅"

        elif action["action_type"] == "wait":
            reward = 1
            info = "waited ⏳"

        # End condition
        if self.current_step >= self.max_steps:
            done = True

        return {"servers": self.servers}, reward, done, info