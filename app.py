import gradio as gr
from fastapi import FastAPI, Request
import uvicorn
from env import FarmerEnv

# 1. SERVER SETUP
app = FastAPI()
env = FarmerEnv()
current_obs, _ = env.reset()
last_level = "Medium: Standard"

# 2. API ENDPOINTS
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

@app.get("/grader")
async def grader():
    global current_obs
    try:
        health = current_obs.get('crop_health', 0)
        budget = current_obs.get('budget', 0)
        score = (health / 100) * 0.7 + (min(budget, 5000) / 5000) * 0.3
        return {"score": round(float(score), 2)}
    except:
        return {"score": 0.0}

# 3. UI LOGIC
def ui_run(task):
    global current_obs, last_level

    try:
        steps_count = getattr(env, 'steps', 0)

        if task != last_level or steps_count == 0 or env.budget <= 0:
            last_level = task
            mapping = {"Easy: Stable": 0, "Medium: Standard": 1, "Hard: Extreme": 2}
            current_obs, _ = env.reset(options={"task": mapping.get(task, 1)})

        if current_obs['water_level'] < 30:
            action = 2
        elif current_obs['pest_pressure'] > 45:
            action = 4
        else:
            action = 0

        obs, rew, done, _, _ = env.step(action)
        current_obs = obs

        readable_actions = {0:"WAIT", 1:"PLANT", 2:"IRRIGATE", 3:"FERTILIZE", 4:"PESTICIDE"}
        status = "🏁 Done" if done else "🟢 Active"

        return (
            obs['weather'],
            f"₹{obs['budget']}",
            f"{obs['water_level']}%",
            f"{obs['pest_pressure']}%",
            f"{obs['crop_health']}%",
            readable_actions.get(action, "WAIT"),
            f"{rew} pts",
            status
        )

    except Exception as e:
        return "Error", "Error", "0%", "0%", "0%", "ERROR", "0 pts", f"❌ {str(e)}"

# 4. UI
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🚜 Autonomous Agri-Advisor RL System")

    t_in = gr.Dropdown(
        ["Easy: Stable", "Medium: Standard", "Hard: Extreme"],
        value="Medium: Standard",
        label="Select Mode"
    )

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

# Mount Gradio
app = gr.mount_gradio_app(app, demo, path="/")

# 🔥 REQUIRED MAIN FUNCTION (IMPORTANT)
def main():
    uvicorn.run(app, host="0.0.0.0", port=7860)

# Local run
if __name__ == "__main__":
    main()
