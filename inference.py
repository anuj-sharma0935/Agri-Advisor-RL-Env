import requests
import time
import os
from openai import OpenAI

# 1. LLM PROXY SETUP (Ye validator ki requirement hai)
client = OpenAI(
    base_url=os.environ.get("API_BASE_URL", "https://api.openai.com/v1"), # Validator injects this
    api_key=os.environ.get("API_KEY", "dummy_key") # Validator injects this
)

BASE_URL = "http://127.0.0.1:7860"

def get_llm_action(obs):
    """LLM Proxy ke through action mangne ka function"""
    try:
        prompt = f"Obs: {obs}. Actions: 0:WAIT, 1:PLANT, 2:IRRIGATE, 3:FERTILIZE, 4:PESTICIDE. Choose one action (0-4) as an integer based on crop health and budget."
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", # Ya jo bhi model wo allow kar rahe hon
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10
        )
        # LLM se number nikalna
        content = response.choices[0].message.content.strip()
        # Sirf pehla digit uthao
        for s in content:
            if s.isdigit():
                return int(s)
        return 0
    except Exception as e:
        print(f"LLM Error: {e}, falling back to rule-based")
        # Fallback logic agar LLM fail ho jaye (wahi purana smart logic)
        if obs.get('water_level', 100) < 35: return 2
        if obs.get('pest_pressure', 0) > 40: return 4
        return 0

def run_inference():
    task_name = "Medium: Standard"
    print(f"[START] task={task_name}", flush=True)
    
    try:
        response = requests.post(f"{BASE_URL}/reset", json={"task": task_name})
        obs = response.json().get("obs", {})
        
        total_steps = 50 
        for step in range(1, total_steps + 1):
            # 🛑 AB HUM LLM SE POOCHENGE (Validator will track this)
            action = get_llm_action(obs)
            
            resp = requests.post(f"{BASE_URL}/step", json={"action": action})
            data = resp.json()
            obs = data.get("obs", {})
            reward = data.get("reward", 0)
            done = data.get("done", False)
            
            print(f"[STEP] step={step} reward={reward}", flush=True)
            
            if done: break
            time.sleep(0.1)

        final_score = (obs.get('crop_health', 0) / 100) * 0.7 + (min(obs.get('budget', 0), 5000) / 5000) * 0.3
        print(f"[END] task={task_name} score={round(final_score, 4)} steps={step}", flush=True)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    time.sleep(10) # Server start hone ka wait
    run_inference()
