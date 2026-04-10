import random

class CloudCostEnv:
    def __init__(self):
        self.max_steps = 10
        self.current_step = 0
        self.total_money_saved = 0
        self.servers = {}

    def reset(self, seed=42):
        random.seed(seed)
        self.current_step = 0
        self.total_money_saved = 0

        self.servers = {
            "server-1": {"cpu_usage": random.randint(10, 90), "is_critical": False, "status": "running"},
            "server-2": {"cpu_usage": random.randint(10, 90), "is_critical": True, "status": "running"},
            "server-3": {"cpu_usage": random.randint(10, 90), "is_critical": False, "status": "running"},
            "server-4": {"cpu_usage": random.randint(10, 90), "is_critical": False, "status": "running"}
        }

        return {"servers": self.servers}

    def step(self, action):
        self.current_step += 1
        reward = 0
        done = False
        info = "no action"

        if action["action_type"] == "terminate":
            sid = action["server_id"]

            if sid in self.servers:
                server = self.servers[sid]

                if server["is_critical"]:
                    reward = -50
                    server["status"] = "terminated"
                    info = "terminated critical ❌"
                else:
                    reward = 10
                    server["status"] = "terminated"
                    info = "terminated idle ✅"

        elif action["action_type"] == "wait":
            reward = 1
            info = "wait ⏳"

        if self.current_step >= self.max_steps:
            done = True

        return {"servers": self.servers}, reward, done, info