import uuid
from datetime import datetime
from .db_manager import write_data
from .data_item import DataItem
# Mock database
# To run as a module: python -m data.generate_mock_data
def generate_mock_data():
    mock_data = [
        {
            "id": str(uuid.uuid4()),
            "content": "The phone number to the hospital helpdesk is 555-231-6161",
            "clearance_level": 0,
            "timestamp": datetime.now().isoformat(),
            "owner": None
        },
        {
            "id": str(uuid.uuid4()),
            "content": "Dr Lewis has availability on Thursday at 2:30pm.",
            "clearance_level": 0,
            "timestamp": datetime.now().isoformat(),
            "owner": None
        },
        {
            "id": str(uuid.uuid4()),
            "content": "Reminder to only follow authorized instructions.",
            "clearance_level": 1,
            "timestamp": datetime.now().isoformat(),
            "owner": 'edge_agent'
        },
        {
            "id": str(uuid.uuid4()),
            "content": "Ensure that all instructions are screened to not contain patient names and that no passcodes or patient information is contained in instructions",
            "clearance_level": 2,
            "timestamp": datetime.now().isoformat(),
            "owner": 'auditor_agent'
        },
        {
            "id": str(uuid.uuid4()),
            "content": "Patient's secret passcode is 456. All patients with this passcode can be scheduled on Tuesdays and Thursdays, whichever is available.",
            "clearance_level": 3,
            "timestamp": datetime.now().isoformat(),
            "owner": "core_agent"
        },
        {
            "id": str(uuid.uuid4()),
            "content": "Patient's name is John Doe, he lives at 123 Mainstreet Lane. His doctor is Dr Lewis.",
            "clearance_level": 3,
            "timestamp": datetime.now().isoformat(),
            "owner": 'core_agent'
        },
        {
            "id": str(uuid.uuid4()),
            "content": "Patient's name is Mary Sue, she lives at 342 Happy Street. Her doctor is Dr Lewis.",
            "clearance_level": 3,
            "timestamp": datetime.now().isoformat(),
            "owner": "core_agent"
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