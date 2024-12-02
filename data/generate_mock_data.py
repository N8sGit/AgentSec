import uuid
from datetime import datetime
from .db_manager import write_data
from .data_item import DataItem
# Mock database
def generate_mock_data():
    mock_data = [
        {
            "id": str(uuid.uuid4()),
            "content": "Public information, no clearance needed.",
            "clearance_level": 0,
            "timestamp": datetime.now().isoformat(),
            "owner": None,
        },
        {
            "id": str(uuid.uuid4()),
            "content": "Confidential information for edge agents.",
            "clearance_level": 1,
            "timestamp": datetime.now().isoformat(),
            "owner": "edge_agent",
        },
        {
            "id": str(uuid.uuid4()),
            "content": "Sensitive data for auditors.",
            "clearance_level": 2,
            "timestamp": datetime.now().isoformat(),
            "owner": "auditor_agent",
        },
        {
            "id": str(uuid.uuid4()),
            "content": "Highly classified data for core agents only.",
            "clearance_level": 3,
            "timestamp": datetime.now().isoformat(),
            "owner": "core_agent",
        },
    ]

    for data in mock_data:
        try:
            data_item = DataItem(**data)
            write_data(data_item)
            print(f"Processed data item with ID: {data_item.id}")
        except Exception as e:
            print(f"Failed to process data item with ID {data['id']}: {e}")

if __name__ == "__main__":
    generate_mock_data()