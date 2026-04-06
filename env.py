import gymnasium as gym
from gymnasium import spaces
import numpy as np
import random

class FarmerEnv(gym.Env):
    def __init__(self):
        super(FarmerEnv, self).__init__()
        # Actions: 0:WAIT, 1:PLANT, 2:IRRIGATE, 3:FERTILIZE, 4:PESTICIDE
        self.action_space = spaces.Discrete(5)
        self.observation_space = spaces.Dict({
            "budget": spaces.Box(low=0, high=10000, shape=(1,), dtype=np.float32),
            "water_level": spaces.Box(low=0, high=100, shape=(1,), dtype=np.float32),
            "pest_pressure": spaces.Box(low=0, high=100, shape=(1,), dtype=np.float32),
            "crop_health": spaces.Box(low=0, high=100, shape=(1,), dtype=np.float32)
        })
        self.max_steps = 15

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.task = options.get('task', 1) if options else 1
        
        # Initial Scaling based on Task
        if self.task == 0: # Easy
            self.budget, self.water, self.pest = 8000.0, 80.0, 5.0
        elif self.task == 1: # Medium
            self.budget, self.water, self.pest = 5000.0, 60.0, 15.0
        else: # Hard
            self.budget, self.water, self.pest = 2500.0, 35.0, 40.0
            
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

        # --- 🎲 STOCHASTIC (RANDOM) WEATHER LOGIC ---
        # Har step par weather badalne ka chance
        weather_roll = random.random()
        if weather_roll < 0.2:
            self.weather = "Heatwave"
            self.water -= 15
            reward -= 0.3
            self.event_log = "⚠️ Heatwave detected! Water evaporating."
        elif weather_roll < 0.4:
            self.weather = "Cloudy"
            self.water -= 2
            reward += 0.1
        elif weather_roll < 0.5:
            self.weather = "Rainy"
            self.water = min(100, self.water + 15)
            reward += 0.4
            self.event_log = "🌧️ Natural Rain! Resource saved."
        else:
            self.weather = "Sunny"
            self.water -= 5
            reward += 0.2

        # --- 🪲 RANDOM PEST FLUCTUATIONS ---
        pest_growth = random.uniform(2, 10) # Har baar alag growth
        self.pest += pest_growth

        # --- ACTION LOGIC ---
        if action == 1: # PLANT
            self.budget -= 500
            reward += 0.5
        elif action == 2: # IRRIGATE
            self.water = min(100, self.water + 20)
            self.budget -= 200
            reward -= 0.1 # Penalty for cost
        elif action == 4: # PESTICIDE
            self.pest = max(0, self.pest - 30)
            self.budget -= 400
            reward -= 0.2 # Chemical penalty

        # Operational Cost
        self.budget -= 50 

        # Health Penalty
        if self.water < 25 or self.pest > 45:
            self.health -= 8
            reward -= 0.6

        # --- TERMINAL CONDITIONS ---
        done = False
        if self.budget <= 0 or self.health <= 30 or self.steps >= self.max_steps:
            done = True
            if self.health > 70: reward += 5.0 # Big Success Bonus

        return self._get_obs(), round(reward, 2), done, False, {}