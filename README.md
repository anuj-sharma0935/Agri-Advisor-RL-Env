🚜 Agri-Advisor: A Custom Reinforcement Learning Environment
🌟 Overview
Agri-Advisor is a Gymnasium-compliant Reinforcement Learning (RL) environment designed to simulate real-world Indian agricultural challenges. It serves as a Digital Twin where AI agents can learn optimal crop management strategies—balancing budget, hydration, and pest control under stochastic weather conditions.

🧠 Why Reinforcement Learning?
Unlike static prediction models, this project uses an Agent-Environment loop:

State Space: Real-time monitoring of Budget, Water Levels, Pest Pressure, and Crop Health.

Action Space: 5 Strategic decisions (Wait, Plant, Irrigate, Fertilize, Pesticide).

Reward Shaping: A sophisticated mathematical reward function that promotes Sustainable Farming by penalizing resource wastage.

🛠️ Technical Stack
Engine: OpenAI Gymnasium

API: FastAPI (Headless Architecture)

Dashboard: Gradio Industrial UI

Validation: Pydantic Models

📊 Task Difficulties
Easy: High liquidity and stable environment.

Medium: Variable weather and standard resources.

Hard: Extreme stochastic events (Heatwaves & Pest Outbreaks) with limited budget.

🚀 How to Run
Install dependencies: pip install -r requirements.txt

Start the API: python app.py

Run the Baseline Agent: python baseline_agent.py
