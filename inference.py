import requests
import time

# API URL (Localhost kyunki validator repo ke andar run karta hai)
BASE_URL = "http://127.0.0.1:7860"

def run_inference():
    # 1. Start the Task
    task_name = "Medium: Standard"
    print(f"[START] task={task_name}", flush=True)
    
    try:
        # Reset Environment
        response = requests.post(f"{BASE_URL}/reset", json={"task": task_name})
        obs = response.json().get("obs", {})
        
        total_reward = 0
        total_steps = 0
        max_steps = 50 # Jitne steps aapka environment allow kare
        
        for step in range(1, max_steps + 1):
            # --- SMART LOGIC (Same as app.py) ---
            water = obs.get('water_level', 100)
            pest = obs.get('pest_pressure', 0)
            health = obs.get('crop_health', 100)
            budget = obs.get('budget', 5000)

            if water < 35: action = 2
            elif pest > 40: action = 4
            elif health < 85 and budget > 1200: action = 3
            else: action = 0
            
            # Take Step
            resp = requests.post(f"{BASE_URL}/step", json={"action": action})
            data = resp.json()
            obs = data.get("obs", {})
            reward = data.get("reward", 0)
            done = data.get("done", False)
            
            total_reward += reward
            total_steps = step
            
            # 2. Print Step Output (Zaroori hai!)
            print(f"[STEP] step={step} reward={reward}", flush=True)
            
            if done:
                break
            time.sleep(0.1)

        # 3. End the Task (Final Score calculation)
        final_score = (obs.get('crop_health', 0) / 100) * 0.7 + (min(obs.get('budget', 0), 5000) / 5000) * 0.3
        print(f"[END] task={task_name} score={round(final_score, 4)} steps={total_steps}", flush=True)

    except Exception as e:
        print(f"Error during inference: {e}")

if __name__ == "__main__":
    # Wait for server to be ready
    time.sleep(5) 
    run_inference()
