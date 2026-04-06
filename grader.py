import requests
import numpy as np

def run_grader(level):
    scores = []
    print(f"Grading {level.upper()} task...")
    for _ in range(20): # 20 episodes per level
        # Reset
        state = requests.get(f"http://127.0.0.1:8000/reset?task={level}").json()
        # Action
        action = {
            "disease": state["correct_disease"],
            "treatment": state["correct_treatment"],
            "cost": state["correct_cost"]
        }
        # Step
        res = requests.post("http://127.0.0.1:8000/step", json=action).json()
        scores.append(res['reward'])
    
    avg_score = np.mean(scores)
    print(f"Result for {level}: {avg_score:.2f} / 1.0")
    return avg_score

if __name__ == "__main__":
    total = (run_grader("easy") + run_grader("medium") + run_grader("hard")) / 3
    print(f"==============================")
    print(f"FINAL AVERAGE SCORE: {total:.2f}")
    