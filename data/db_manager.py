import json
from pathlib import Path
from .data_item import DataItem
from security.encryption_tools import encrypt_data, decrypt_data

DATA_DIR = Path("data/data_store")
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
    data_list.append(data_item.dict())

    # Write back all data to the file
    with open(DATA_FILE, "w") as f:
        json.dump(data_list, f, indent=4)

    # Append the new data item
    data_list.append(data_item.model_dump())

    # Write back all data to the file
    with open(DATA_FILE, "w") as f:
        json.dump(data_list, f, indent=4)

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