# security/blockchain.py
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def log_action(agent_name: str, action: str):
    """Log agent actions."""
    logging.info(f"{agent_name}: {action}")