import gymnasium as gym
from gymnasium import spaces
import numpy as np
import random

class FarmerEnv(gym.Env):
    def __init__(self):
        super(FarmerEnv, self).__init__()
        
        # Actions: 0:WAIT, 1:PLANT, 2:IRRIGATE, 3:FERTILIZE, 4:PESTICIDE
        self.action_space = spaces.Discrete(5)
        
        # Observation Space: Budget, Water, Pests, Health
        self.observation_space = spaces.Dict({
            "budget": spaces.Box(low=0, high=10000, shape=(1,), dtype=np.float32),
            "water_level": spaces.Box(low=0, high=100, shape=(1,), dtype=np.float32),
            "pest_pressure": spaces.Box(low=0, high=100, shape=(1,), dtype=np.float32),
            "crop_health": spaces.Box(low=0, high=100, shape=(1,), dtype=np.float32)
        })
        
        self.max_steps = 15
        self.metadata = {"render_modes": ["human"]}

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        
        # --- TASK SELECTION LOGIC ---
        task_input = options.get('task', 1) if options else 1
        
        # Mapping string to int if coming from UI
        if isinstance(task_input, str):
            mapping = {"easy": 0, "medium": 1, "hard": 2, 
                       "easy: stable": 0, "medium: standard": 1, "hard: extreme": 2}
            self.task = mapping.get(task_input.lower(), 1)
        else:
            self.task = task_input
        
        # --- DYNAMIC INITIALIZATION (Randomness starting mein hi) ---
        if self.task == 0: # Easy
            self.budget = random.uniform(7500.0, 9500.0)
            self.water = random.uniform(70.0, 85.0)
            self.pest = random.uniform(2.0, 8.0)
        elif self.task == 2: # Hard
            self.budget = random.uniform(1500.0, 2800.0)
            self.water = random.uniform(25.0, 40.0)
            self.pest = random.uniform(35.0, 50.0)
        else: # Medium
            self.budget = 5000.0
            self.water = 60.0
            self.pest = 15.0
            
        self.health = 100.0
        self.weather = "Sunny"
        self.event_log = "System Initialized"
        self.steps = 0
        
        return self._get_obs(), {}

    def _get_obs(self):
        return {
            "budget": round(float(self.budget), 2),
            "water_level": round(float(self.water), 2),
            "pest_pressure": round(float(self.pest), 2),
            "crop_health": round(float(self.health), 2),
            "weather": self.weather,
            "event": getattr(self, 'event_log', "Monitoring")
        }

    def step(self, action):
        self.steps += 1
        reward = 0.0
        self.event_log = "Normal Operations"

        # --- 1. DYNAMIC WEATHER RANDOMNESS ---
        weather_roll = random.random()
        if weather_roll < 0.15:
            self.weather = "Heatwave"
            self.water -= random.uniform(12, 18)
            reward -= 0.3
            self.event_log = "⚠️ Heatwave! Water level dropping fast."
        elif weather_roll < 0.40:
            self.weather = "Rainy"
            self.water = min(100, self.water + random.uniform(10, 20))
            reward += 0.4
            self.event_log = "🌧️ Natural Rain! Resources replenished."
        elif weather_roll < 0.60:
            self.weather = "Cloudy"
            self.water -= random.uniform(1, 3)
            self.event_log = "☁️ Overcast weather."
        else:
            self.weather = "Sunny"
            self.water -= random.uniform(4, 7)
            reward += 0.1

        # --- 2. RANDOM PEST GROWTH ---
        self.pest += random.uniform(3, 10)

        # --- 3. ACTION COSTS & LOGIC ---
        if action == 1: # PLANT
            self.budget -= 500
            reward += 0.5
            self.event_log = "🌱 Sowing new crops."
        elif action == 2: # IRRIGATE
            self.water = min(100, self.water + 20)
            self.budget -= 200
            reward -= 0.1
            self.event_log = "💧 Irrigation active."
        elif action == 4: # PESTICIDE
            self.pest = max(0, self.pest - 30)
            self.budget -= 400
            reward -= 0.2
            self.event_log = "🛡️ Pesticides applied."

        # --- 4. RANDOM OPERATIONAL LOSS (Fixed -50 hata diya) ---
        # Har step par ₹100 se ₹400 tak ka random market loss ya maintenance kharcha
        market_fluctuation = random.uniform(100, 400)
        self.budget -= market_fluctuation

        # --- 5. CROP HEALTH DYNAMICS ---
        if self.water < 20 or self.water > 90:
            self.health -= 7
            reward -= 0.5
        if self.pest > 40:
            self.health -= 10
            reward -= 0.7

        # --- 6. TERMINAL CONDITIONS & BOUNDARIES ---
        if self.budget < 0: self.budget = 0
        
        done = False
        if self.budget <= 0 or self.health <= 25 or self.steps >= self.max_steps:
            done = True
            # Final Bonus for good farming
            if self.health > 75 and self.budget > 500:
                reward += 10.0
                self.event_log = "🏆 Harvest Successful!"
            elif self.budget <= 0:
                self.event_log = "❌ Bankrupt! Game Over."

        return self._get_obs(), round(reward, 2), done, False, {}
