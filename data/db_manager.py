import json
from pathlib import Path
from .data_item import DataItem
from security.encryption_tools import encrypt_data, decrypt_data
import os
from typing import Optional, Union

DATA_DIR = Path(os.getenv("DATA_DIR", "data/data_store"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
DATA_FILE = DATA_DIR / "data_store.json"


def write_data(data_item: DataItem) -> None:
    """Write a DataItem to the single JSON data file."""
    if data_item.clearance_level > 0:
        # Encrypt the content if the clearance level is above 0
        data_item.content = encrypt_data(data_item.content, data_item.clearance_level, data_item.owner)

    # Load existing data
    data_list = []
    if DATA_FILE.exists():
        with open(DATA_FILE, "r") as f:
            data_list = json.load(f)

    # Append the new data item
    data_list.append(data_item.model_dump())

    # Write back all data to the file
    with open(DATA_FILE, "w") as f:
        json.dump(data_list, f, indent=4)

def fetch_data_by_clearance(
    agent_clearance: int,
    data_id: Optional[str] = None,
    agent_name: Optional[str] = None
) -> Union[list, dict]:
    """
    Fetch data based on clearance level. If a specific data_id is provided, fetch that item.
    Otherwise, return all data filtered by clearance level.

    Args:
        agent_clearance (int): Clearance level of the agent (1, 2, or 3).
        data_id (Optional[str]): ID of the specific data item to fetch (default: None).
        agent_name (Optional[str]): Name of the agent for decryption (default: None).

    Returns:
        Union[list, dict]: List of data items (filtered by clearance level) or a single item.
    """
    if not DATA_FILE.exists():
        raise FileNotFoundError("Data store file not found.")

    # Load all data from the file
    with open(DATA_FILE, "r") as f:
        data_list = json.load(f)

    # Tiered clearance logic
    filtered_data = [
        data for data in data_list if data["clearance_level"] <= agent_clearance
    ]

    if data_id:
        # Fetch specific data by ID
        for data in filtered_data:
            if data["id"] == data_id:
                data_item = DataItem(**data)
                # Decrypt content if necessary
                if agent_name and data_item.clearance_level > 0:
                    data_item.content = decrypt_data(data_item.content, agent_name)
                return data_item.model_dump()
        raise FileNotFoundError(f"Data with id {data_id} not found.")

    # Decrypt all contents for clearance level > 0 if agent_name is provided
    if agent_name:
        for data in filtered_data:
            if data["clearance_level"] > 0:
                try:
                    data_item = DataItem(**data)
                    data_item.content = decrypt_data(data_item.content, agent_name)
                    data.update(data_item.model_dump())
                except Exception as e:
                    # Log decryption failure
                    print(f"[ERROR] Decryption failed for item ID {data['id']}: {e}")

    return filtered_data

def read_all_data():
    """Fetch all data from the database."""
    print(f"[DEBUG] Reading from path: {DATA_FILE.resolve()}")
    if not DATA_FILE.exists():
        print(f"[DEBUG] Data file does not exist at path: {DATA_FILE.resolve()}")
        return []

    with open(DATA_FILE, "r") as f:
        return json.load(f)

def read_data(data_id: str, agent_name: str, agent_clearance: int) -> str:
    """Read a DataItem from the file system with decryption and clearance check."""
    if not DATA_FILE.exists():
        raise FileNotFoundError("Data store file not found.")

    # Load all data from the single JSON file
    with open(DATA_FILE, "r") as f:
        data_list = json.load(f)

    # Find the specific data item by ID
    for data in data_list:
        if data["id"] == data_id:
            data_item = DataItem(**data)
            # Check clearance level
            if agent_clearance < data_item.clearance_level:
                raise PermissionError("Access denied: insufficient clearance level.")
            # Decrypt content if necessary
            if data_item.clearance_level > 0:
                data_item.content = decrypt_data(data_item.content, agent_name)
            return data_item.content

    raise FileNotFoundError(f"Data with id {data_id} not found.")


def update_data(data_id: str, updated_fields: dict) -> None:
    """Update fields of a DataItem and write back to the data store."""
    if not DATA_FILE.exists():
        raise FileNotFoundError("Data store file not found.")

    # Load all data from the single JSON file
    with open(DATA_FILE, "r") as f:
        data_list = json.load(f)

    # Update the specific data item
    for i, data in enumerate(data_list):
        if data["id"] == data_id:
            data_item = DataItem(**data)
            for key, value in updated_fields.items():
                setattr(data_item, key, value)
            # Replace the updated item back into the list
            data_list[i] = data_item.model_dump()
            break
    else:
        raise FileNotFoundError(f"Data with id {data_id} not found.")

    # Write all data back to the file
    with open(DATA_FILE, "w") as f:
        json.dump(data_list, f, indent=4)


def filter_data_by_clearance_level(agent_clearance: int):
    """Filter and return data accessible by the given clearance level."""
    if not DATA_FILE.exists():
        return []

    # Load all data from the file
    with open(DATA_FILE, "r") as f:
        data_list = json.load(f)

    # Filter data based on clearance level
    accessible_data = []
    for data in data_list:
        if data["clearance_level"] <= agent_clearance:
            accessible_data.append(data)

    return accessible_data