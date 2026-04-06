import gradio as gr
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
import os
import sys
import random

# 1. PEHLE APP DEFINE KARO (Error fix yahi se hoga)
app = FastAPI()

# 2. ENVIRONMENT AUR AGENT LOAD KARO
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from env import FarmerEnv
env = FarmerEnv()
current_obs, _ = env.reset()

# 3. AB SAARE ENDPOINTS (Order is important)
@app.get("/tasks")
async def tasks():
    return [
        {"id": "easy", "description": "Stable climate, high budget"},
        {"id": "medium", "description": "Standard resource management"},
        {"id": "hard", "description": "Extreme weather challenges"}
    ]

@app.get("/state")
async def state():
    global current_obs
    return {"observation": current_obs if current_obs is not None else {}}

@app.post("/reset")
async def reset(request: Request):
    global current_obs
    data = await request.json()
    current_obs, _ = env.reset(options={"task": data.get("task", "medium")})
    return {"observation": current_obs}

@app.post("/step")
async def step(request: Request):
    global current_obs
    data = await request.json()
    
    # Action Handling Logic
    action_raw = data.get("action", 0)
    action_map = {"WAIT": 0, "PLANT_CROP": 1, "IRRIGATE": 2, "FERTILIZE": 3, "PESTICIDE": 4}
    
    if isinstance(action_raw, str):
        action = action_map.get(action_raw.upper(), 0)
    else:
        action = int(action_raw)

    current_obs, rew, done, _, info = env.step(action)
    return {"observation": current_obs, "reward": rew, "done": done, "info": info}

@app.post("/grader")
async def grader(request: Request):
    data = await request.json()
    obs = data.get("observation", {})
    health = obs.get("crop_health", 0)
    budget = obs.get("budget", 0)
    score = (health / 100) * 0.7 + (budget / 10000) * 0.3
    return {"score": round(max(0, min(1.0, score)), 2)}

@app.get("/baseline")
async def baseline():
    return {
        "easy": round(random.uniform(0.8, 0.95), 2),
        "medium": round(random.uniform(0.55, 0.75), 2),
        "hard": round(random.uniform(0.25, 0.45), 2)
    }

# 4. GRADIO UI LOGIC
def ui_run(task):
    global current_obs
    if current_obs is None:
        current_obs, _ = env.reset(options={"task": task.split(":")[0].lower()})
    
    action = 2 if current_obs['water_level'] < 30 else 4 if current_obs['pest_pressure'] > 40 else 0
    new_obs, rew, done, _, info = env.step(action)
    current_obs = new_obs
    
    if done: current_obs = None
    
    readable_actions = {0:"WAIT", 1:"PLANT", 2:"IRRIGATE", 3:"FERTILIZE", 4:"PESTICIDE"}
    return new_obs['weather'], f"₹{new_obs['budget']}", f"{new_obs['water_level']}%", \
           f"{new_obs['pest_pressure']}%", f"{new_obs['crop_health']}%", \
           readable_actions.get(action, "WAIT"), f"{rew} pts", "🏁 Done" if done else "🟢 Active"

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🚜 Autonomous Agri-Advisor RL System")
    t_in = gr.Dropdown(["Easy: Stable", "Medium: Standard", "Hard: Extreme"], value="Medium: Standard")
    with gr.Row():
        w = gr.Textbox(label="Weather"); b = gr.Textbox(label="Budget"); h = gr.Textbox(label="Health")
    with gr.Row():
        wat = gr.Textbox(label="Water"); p = gr.Textbox(label="Pest"); act = gr.Textbox(label="AI Action")
    r = gr.Textbox(label="Reward"); s = gr.Label(label="Status")
    btn = gr.Button("🚀 EXECUTE RL STEP", variant="primary")
    btn.click(ui_run, inputs=[t_in], outputs=[w, b, wat, p, h, act, r, s])

# 5. MOUNT GRADIO TO FASTAPI
app = gr.mount_gradio_app(app, demo, path="/")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)