import requests
import time
import random

class BaselineAgent:
    def predict(self, obs):
        """
        Tera Logic:
        - Pani kam hai (<30) -> IRRIGATE (2)
        - Kide zyada hain (>30) -> PESTICIDE (4)
        - Sab sahi hai aur budget hai -> PLANT (1)
        - Varna -> WAIT (0)
        """
        # Dictionary se data nikalna
        water = obs.get('water_level', 50.0)
        pest = obs.get('pest_pressure', 0.0)
        budget = obs.get('budget', 5000.0)
        health = obs.get('crop_health', 100.0)

        # 1. Critical Water Check
        if water < 30:
            return 2  # Action: IRRIGATE
        
        # 2. Critical Pest Check
        if pest > 30:
            return 4  # Action: PESTICIDE
        
        # 3. Planting Logic
        if health == 100 and budget > 4000:
            return 1  # Action: PLANT_CROP
            
        # 4. Default Action
        return 0  # Action: WAIT

def run_inference():
    agent = BaselineAgent()
    # API URL (Make sure app.py is running on this port)
    BASE_URL = "http://127.0.0.1:8000"

    print("🚀 Starting Baseline Inference...")

    try:
        # 1. Reset Environment
        reset_resp = requests.post(f"{BASE_URL}/reset")
        if reset_resp.status_code != 200:
            print("❌ Error: Server nahi chal raha. Pehle app.py start karo!")
            return
        
        obs = reset_resp.json().get('obs')
        print(f"✅ Reset Successful. Initial State: {obs}")

        total_reward = 0
        
        # 2. Run Loop (15 steps for testing)
        for step in range(1, 16):
            # Agent se action lo
            action = agent.predict(obs)
            
            # Action API ko bhejo
            step_resp = requests.post(f"{BASE_URL}/step", json={"action": action})
            
            if step_resp.status_code == 200:
                result = step_resp.json()
                obs = result.get('obs')
                reward = result.get('reward')
                done = result.get('done')
                
                total_reward += reward
                print(f"Step {step}: Action={action} | Reward={reward:.2f} | Health={obs.get('crop_health'):.1f}")
                
                if done:
                    print("🏁 Episode Finished!")
                    break
                
                time.sleep(0.3) # Fast execution
            else:
                print(f"❌ Step {step} failed!")
                break

        # 3. Final Grader Score
        grader_resp = requests.get(f"{BASE_URL}/grader")
        score = grader_resp.json().get('score')
        print("\n--- Final Report ---")
        print(f"Total Accumulated Reward: {total_reward:.2f}")
        print(f"Grader Evaluation Score: {score}")

    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    run_inference()
