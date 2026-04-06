import random

class BaselineAgent:
    def predict(self, obs):
        """
        AI Logic: 
        - Agar pani kam hai (<30) -> IRRIGATE (2)
        - Agar kide zyada hain (>30) -> PESTICIDE (4)
        - Agar sab sahi hai aur budget hai -> PLANT (1)
        - Varna -> WAIT (0)
        """
        # Dictionary se data nikalna (Safe way)
        water = obs.get('water_level', 50.0)
        pest = obs.get('pest_pressure', 0.0)
        budget = obs.get('budget', 5000.0)
        health = obs.get('crop_health', 100.0)

        # 1. Critical Water Check
        if water < 30:
            return 2  # Action: IRRIGATE
        
        # 2. Critical Pest Check
        if pest > 30:
            return 4  # Action: PESTICIDE
        
        # 3. Planting Logic (Initial step)
        if health == 100 and budget > 4000:
            return 1  # Action: PLANT_CROP
            
        # 4. Default Action
        return 0  # Action: WAIT