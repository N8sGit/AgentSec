from .db_manager import write_data
from .data_item import DataItem
from datetime import datetime
#Mock database
mock_data = [
    {
        "id": "3f8f6b4a5f2e4e03a0b57642b9241c1b",
        "content": "Unclassified data example.",
        "clearance_level": 0,
        "timestamp": datetime.now().isoformat(),
        "owner": None
    },
    {
        "id": "12f1c2d74e9e48d3a8b71c5d939eb07f",
        "content": "Edge-level data for operational tasks.",
        "clearance_level": 1,
        "timestamp": datetime.now().isoformat(),
        "owner": "edge_agent_one"
    },
    {
        "id": "8d36b5f8c7e6499cb85e3a4fb9f7c248",
        "content": "Auditor-level confidential information.",
        "clearance_level": 2,
        "timestamp": datetime.now().isoformat(),
        "owner": "auditor_agent"
    },
    {
        "id": "45ae23c6d4f14db8aa94222fb5c36b79",
        "content": "Core-level highly sensitive data.",
        "clearance_level": 3,
        "timestamp": datetime.now().isoformat(),
        "owner": "core_agent"
    }
]

def generate_mock_data():
    """
    Generates mock data items and writes them to the database using write_data function.
    Data with clearance levels > 0 will be encrypted during storage.
    """
    for item in mock_data:
        try:
            # Convert dictionary to DataItem object
            data_item = DataItem(**item)
            print(f"Processing data item with ID: {data_item.id}")
            write_data(data_item)  # Use the write_data function to handle encryption and storage
            print(f"Data item with ID {data_item.id} written successfully.")
        except Exception as e:
            print(f"Failed to process data item with ID {item['id']}: {e}")

if __name__ == "__main__":
    generate_mock_data()