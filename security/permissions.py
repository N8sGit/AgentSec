import json
import os

def get_clearance_level(agent_id):
    # Construct the path relative to the working directory
    config_path = os.path.join(os.path.dirname(__file__), '..', 'configs', 'clearance_levels.json')
    config_path = os.path.abspath(config_path)  # Convert to an absolute path for clarity
    
    print(f"Looking for clearance_levels.json at: {config_path}")  # Debug statement
    
    try:
        with open(config_path, 'r') as f:
            clearance_levels = json.load(f)
        return clearance_levels.get(agent_id, 1)  # Default clearance level if agent ID not found
    except FileNotFoundError:
        print(f"Warning: {config_path} not found. Using default clearance level.")
        return 1

def has_permission(agent_name, required_level):
    agent_level = get_clearance_level(agent_name)
    return agent_level >= required_level