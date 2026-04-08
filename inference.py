import os
import sys
import subprocess

# 🛡️ SAFETY NET: Agar openai install nahi hai, toh force install karo
try:
    from openai import OpenAI
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openai"])
    from openai import OpenAI

import requests
import time

# 1. LLM PROXY SETUP
client = OpenAI(
    base_url=os.environ.get("API_BASE_URL", "https://api.openai.com/v1"),
    api_key=os.environ.get("API_KEY", "dummy_key")
)

BASE_URL = "http://127.0.0.1:7860"

def get_llm_action(obs):
    """LLM Proxy ke through action mangne ka function"""
    try:
        prompt = f"Obs: {obs}. Actions: 0:WAIT, 1:PLANT, 2:IRRIGATE, 3:FERTILIZE, 4:PESTICIDE. Choose one action (0-4) as an integer."
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10
        )
        content = response.choices[0].message.content.strip()
        for s in content:
            if s.isdigit():
                return int(s)
        return 0
    except Exception as e:
        # Fallback Logic (Agar API fail ho jaye)
        water = obs.get('water_level', 100)
        pest = obs.get('pest_pressure', 0)
        if water < 35: return 2
        if pest > 40: return 4
        return 0

def run_inference():
    task_name = "Medium: Standard"
    print(f"[START] task={task_name}", flush=True)
    
    try:
        # Step 0: Wait for server to be fully ready
        time.sleep(15) 
        
        response = requests.post(f"{BASE_URL}/reset", json={"task": task_name})
        obs = response.json().get("obs", {})
        
        for step in range(1, 51):
            action = get_llm_action(obs)
            
            resp = requests.post(f"{BASE_URL}/step", json={"action": action})
            data = resp.json()
            obs = data.get("obs", {})
            reward = data.get("reward", 0)
            done = data.get("done", False)
            
            print(f"[STEP] step={step} reward={reward}", flush=True)
            
            if done: break
            time.sleep(0.2)

        health = obs.get('crop_health', 0)
        budget = obs.get('budget', 0)
        final_score = (health / 100) * 0.7 + (min(budget, 5000) / 5000) * 0.3
        print(f"[END] task={task_name} score={round(final_score, 4)} steps={step}", flush=True)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_inference()
