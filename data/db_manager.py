import json
from pathlib import Path
from .data_item import DataItem
from security.encryption_tools import encrypt_data, decrypt_data


DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

def write_data(data_item: DataItem) -> None:
    """Write a DataItem to the file system with encryption if required."""
    if data_item.clearance_level > 0:
        # Encrypt content if clearance level is higher than 0
        data_item.content = encrypt_data(data_item.content, data_item.clearance_level, data_item.owner)
    file_path = DATA_DIR / f"{data_item.id}.json"
    with open(file_path, "w") as f:
        json.dump(data_item.model_dump(), f)

def read_data(data_id: str, agent_name: str, agent_clearance: int) -> str:
    """Read a DataItem from the file system with decryption and clearance check."""
    file_path = DATA_DIR / f"{data_id}.json"
    if not file_path.exists():
        raise FileNotFoundError(f"Data with id {data_id} not found.")
    with open(file_path, "r") as f:
        data = json.load(f)
    data_item = DataItem(**data)
    if agent_clearance < data_item.clearance_level:
        raise PermissionError("Access denied: insufficient clearance level.")
    if data_item.clearance_level > 0:
        # Decrypt content if it was encrypted
        data_item.content = decrypt_data(data_item.content, agent_name)
    return data_item.content

def update_data(data_id: str, updated_fields: dict) -> None:
    data_item = read_data(data_id)
    for key, value in updated_fields.items():
        setattr(data_item, key, value)
    write_data(data_item)

def delete_data(data_id: str) -> None:
    file_path = DATA_DIR / f"{data_id}.json"
    if file_path.exists():
        file_path.unlink()