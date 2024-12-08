import logging
from typing import List, Dict, Any

from data.db_manager import read_all_data
from security.encryption_tools import decrypt_data
from security.log_chain import log_action

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class DataManager:
    """
    A DataManager that fetches data from the database and decrypts it according to clearance level.
    This class can be used by all agents. 

    Usage:
    - Initialize with the agent_id and optionally an agent_name.
    - Call fetch_data_by_clearance_level with a clearance level (1, 2, or 3).
        * Clearance 3: Returns all data
        * Clearance 2: Returns data at clearance level 2 and below
        * Clearance 1: Returns data at clearance level 1 and below

    Decryption is only attempted on items that have a clearance level > 0.
    Items that fail decryption will be skipped.
    """

    def __init__(self, agent_id: str, agent_name: str = "core_agent"):
        self.agent_id = agent_id
        self.agent_name = agent_name

    def fetch_data_by_clearance_level(self, clearance_level: int) -> List[Dict[str, Any]]:
        """
        Fetch and decrypt data by clearance level.

        Args:
            clearance_level (int): The requesting agent's clearance level (1 to 3).

        Returns:
            List[Dict[str, Any]]: A list of decrypted data items.
        """
        try:
            # Read all data from the database
            all_data = read_all_data()
            logger.debug(f"[{self.agent_id}] Raw data fetched from database: {all_data}")

            # Filter data by the agent's clearance
            # If clearance is 3, return all data. If 2, return data with clearance <= 2. If 1, <= 1.
            allowed_data = [item for item in all_data if item.get("clearance_level", 0) <= clearance_level]

            decrypted_data = []
            for index, item in enumerate(allowed_data):
                logger.debug(f"[{self.agent_id}] Processing item {index+1}/{len(allowed_data)}: ID={item.get('id')}")
                
                # If clearance > 0, attempt decryption
                if item.get("clearance_level", 0) > 0:
                    try:
                        logger.debug(f"[{self.agent_id}] Attempting to decrypt item ID={item.get('id')}")
                        decrypted_content = decrypt_data(item["content"], self.agent_name)
                        item["content"] = decrypted_content
                        log_action(self.agent_id, f"Decrypted data item {item['id']}.")
                        logger.debug(f"[{self.agent_id}] Decryption successful for item ID={item.get('id')}")
                    except Exception as e:
                        # Log and skip if decryption fails
                        log_action(self.agent_id, f"Failed to decrypt data item {item.get('id')}: {e}")
                        logger.error(f"[{self.agent_id}] Decryption failed for item ID={item.get('id')}. Error: {e}")
                        continue  # Skip this item
                
                decrypted_data.append(item)

            logger.debug(f"[{self.agent_id}] Completed processing of {len(decrypted_data)} items.")
            return decrypted_data

        except Exception as e:
            # Catch and log any unexpected errors
            log_action(self.agent_id, f"Error fetching data: {e}")
            logger.error(f"[{self.agent_id}] Unexpected error occurred while fetching data. Error: {e}")
            return []