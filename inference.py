import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from env import FarmerEnv
from openai import OpenAI

def run_inference():
    env = FarmerEnv()

    # 🔥 SAFE ENV VARIABLES
    api_key = os.environ.get("API_KEY")
    base_url = os.environ.get("API_BASE_URL")
    model_name = os.environ.get("MODEL_NAME", "gpt-3.5-turbo")

    client = OpenAI(base_url=base_url, api_key=api_key)

    task_name = "medium"
    print(f"[START] task={task_name}", flush=True)

    obs, _ = env.reset(options={"task": task_name})

    total_steps = 0

    for step in range(1, 31):
        try:
            prompt = f"""
            water={obs['water_level']},
            pest={obs['pest_pressure']},
            health={obs['crop_health']},
            budget={obs['budget']}

            Choose action:
            0 WAIT
            1 PLANT
            2 IRRIGATE
            4 PESTICIDE
            Only return number.
            """

            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=5
            )

            text = response.choices[0].message.content.strip()
            action = int(''.join(filter(str.isdigit, text))) if any(c.isdigit() for c in text) else 0

        except:
            # fallback (VERY IMPORTANT)
            water = obs.get('water_level', 100)
            pest = obs.get('pest_pressure', 0)

            if water < 35:
                action = 2
            elif pest > 40:
                action = 4
            else:
                action = 0

        obs, reward, done, _, _ = env.step(action)
        total_steps = step

        print(f"[STEP] step={step} reward={reward}", flush=True)

        if done:
            break

    health = obs.get('crop_health', 0)
    budget = obs.get('budget', 0)
    score = (health / 100) * 0.7 + (budget / 10000) * 0.3

    print(f"[END] task={task_name} score={round(score, 4)} steps={total_steps}", flush=True)


if __name__ == "__main__":
    run_inference()
