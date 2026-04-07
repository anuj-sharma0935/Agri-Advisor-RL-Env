import random

class BaselineAgent:
    def predict(self, obs):
        """
        Tera Original Logic:
        - Pani kam hai (<30) -> IRRIGATE (2)
        - Kide zyada hain (>30) -> PESTICIDE (4)
        - Sab sahi hai aur budget hai -> PLANT (1)
        - Varna -> WAIT (0)
        """
        water = obs.get('water_level', 50.0)
        pest = obs.get('pest_pressure', 0.0)
        budget = obs.get('budget', 5000.0)
        health = obs.get('crop_health', 100.0)

        # Logical Checks (Exactly as before)
        if water < 30:
            return 2  # Action: IRRIGATE
        
        if pest > 30:
            return 4  # Action: PESTICIDE
        
        if health == 100 and budget > 4000:
            return 1  # Action: PLANT_CROP
            
        return 0  # Action: WAIT
