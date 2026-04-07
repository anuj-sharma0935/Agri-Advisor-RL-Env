import gradio as gr
from fastapi import FastAPI, Request
import uvicorn
import os
import sys
from env import FarmerEnv

# 1. SERVER SETUP
app = FastAPI()
env = FarmerEnv()
current_obs, _ = env.reset()
last_level = "Medium: Standard"

# 2. API ENDPOINTS (For Baseline Agent)
@app.post("/reset")
async def reset(request: Request):
    global current_obs
    try:
        data = await request.json()
        task_input = data.get("task", "Medium: Standard")
    except:
        task_input = "Medium: Standard"
    
    mapping = {"Easy: Stable": 0, "Medium: Standard": 1, "Hard: Extreme": 2}
    task_id = mapping.get(task_input, 1)
    current_obs, _ = env.reset(options={"task": task_id})
    return {"obs": current_obs}

@app.post("/step")
async def step(request: Request):
    global current_obs
    try:
        data = await request.json()
        action = int(data.get("action", 0))
    except:
        action = 0
    obs, rew, done, _, info = env.step(action)
    current_obs = obs
    return {"obs": obs, "reward": rew, "done": done, "info": info}

# 3. UI LOGIC (Fixes the 'steps' error)
def ui_run(task):
    global current_obs, last_level
    
    # Try-except block taaki 'steps' wala error UI crash na kare
    try:
        steps_count = getattr(env, 'steps', 0)
        
        # Reset if level changed or game ended
        if task != last_level or steps_count == 0 or env.budget <= 0:
            last_level = task
            mapping = {"Easy: Stable": 0, "Medium: Standard": 1, "Hard: Extreme": 2}
            current_obs, _ = env.reset(options={"task": mapping.get(task, 1)})
        
        # Automated Rule-based AI
        if current_obs['water_level'] < 30: action = 2 # IRRIGATE
        elif current_obs['pest_pressure'] > 40: action = 4 # PESTICIDE
        else: action = 0 # WAIT

        obs, rew, done, _, _ = env.step(action)
        current_obs = obs
        
        readable_actions = {0:"WAIT", 1:"PLANT", 2:"IRRIGATE", 3:"FERTILIZE", 4:"PESTICIDE"}
        status = "🏁 Done" if done else "🟢 Active"
        
        return obs['weather'], f"₹{obs['budget']}", f"{obs['water_level']}%", \
               f"{obs['pest_pressure']}%", f"{obs['crop_health']}%", \
               readable_actions.get(action, "WAIT"), f"{rew} pts", status
               
    except Exception as e:
        return "Error", str(e), "Error", "Error", "Error", "Error", "0 pts", "❌ Error"

# 4. GRADIO INTERFACE (Exact Screenshot Layout)
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🚜 Autonomous Agri-Advisor RL System")
    
    t_in = gr.Dropdown(["Easy: Stable", "Medium: Standard", "Hard: Extreme"], label="Dropdown", value="Medium: Standard")
    
    with gr.Row():
        w = gr.Textbox(label="Weather")
        b = gr.Textbox(label="Budget")
        h = gr.Textbox(label="Health")
    
    with gr.Row():
        wat = gr.Textbox(label="Water")
        p = gr.Textbox(label="Pest")
        act = gr.Textbox(label="AI Action")
    
    r = gr.Textbox(label="Reward")
    s = gr.Label(label="Status")
    
    btn = gr.Button("🚀 EXECUTE RL STEP", variant="primary")
    btn.click(ui_run, inputs=[t_in], outputs=[w, b, wat, p, h, act, r, s])

app = gr.mount_gradio_app(app, demo, path="/")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
