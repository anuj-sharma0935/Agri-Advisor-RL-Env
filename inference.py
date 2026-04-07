import os
import sys
import time

# Ensure env.py and baseline_agent.py are discoverable
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from env import FarmerEnv
    from baseline_agent import BaselineAgent
except ImportError as e:
    print(f"❌ Critical Error: Files not found! {e}")
    sys.exit(1)

def run_inference():
    # Setup - No API needed, direct class interaction
    env = FarmerEnv()
    agent = BaselineAgent()

    print("🚀 Starting Inference (Phase 1 Validated)...")

    try:
        # Reset (Using "medium" task for environment compatibility)
        obs, _ = env.reset(options={"task": "medium"})
        print(f"✅ Reset Successful. Initial State: {obs}")

        total_reward = 0.0
        
        # Loop for exactly 15 steps
        for step in range(1, 16):
            # Get action from your agent logic
            action = agent.predict(obs)
            
            # Step the environment
            obs, reward, done, truncated, info = env.step(action)
            total_reward += reward
            
            print(f"Step {step}: Action={action} | Reward={reward:.2f} | Health={obs.get('crop_health'):.1f}")
            
            if done:
                print("🏁 Episode Finished!")
                break
            
            time.sleep(0.1)

        # Final Scoring (Matches your Grader requirements)
        score = (obs.get('crop_health', 0) / 100) * 0.7 + (obs.get('budget', 0) / 10000) * 0.3
        
        print("\n" + "="*30)
        print("📊 FINAL SUBMISSION REPORT")
        print(f"Total Accumulated Reward: {round(total_reward, 2)}")
        print(f"Grader Evaluation Score: {round(min(1.0, score), 2)}")
        print("="*30)

    except Exception as e:
        print(f"❌ Execution Error: {e}")

if __name__ == "__main__":
    run_inference()