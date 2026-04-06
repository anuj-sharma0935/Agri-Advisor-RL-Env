def get_task_setup(level, state):
    if level == "easy":
        # 3 symptoms dikhao (Easy ID)
        return {"visible_symptoms": state["symptoms"][:3]}
    elif level == "medium":
        # 2 symptoms dikhao (Treatment Rec.)
        return {"visible_symptoms": state["symptoms"][:2]}
    else:
        # 1 symptom dikhao (Full Advisory)
        return {"visible_symptoms": state["symptoms"][:1]}
    