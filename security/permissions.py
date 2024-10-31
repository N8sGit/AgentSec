import json

def get_clearance_level(agent_name):
    with open('configs/clearance_levels.json', 'r') as f:
        clearance_levels = json.load(f)
    return clearance_levels.get(agent_name, {}).get('clearance_level', 0)

def has_permission(agent_name, required_level):
    agent_level = get_clearance_level(agent_name)
    return agent_level >= required_level