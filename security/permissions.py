import json
import os

def get_clearance_level(agent_id):
    # Construct the path relative to the working directory
    config_path = os.path.join(os.path.dirname(__file__), '..', 'configs', 'clearance_levels.json')
    config_path = os.path.abspath(config_path)  # Convert to an absolute path for clarity

    print(f"Looking for clearance_levels.json at: {config_path}")

    try:
        with open(config_path, 'r') as f:
            clearance_levels = json.load(f)
        
        # Retrieve the clearance level for the given agent_id
        agent_info = clearance_levels.get(agent_id, None)
        if agent_info and "clearance_level" in agent_info:
            return agent_info["clearance_level"]
        
        # Default value if clearance level is not found
        print(f"[DEBUG] Clearance level not found for {agent_id}. Using default value.")
        return 3
    except FileNotFoundError:
        print(f"Warning: {config_path} not found. Using default clearance level.")
        return 3