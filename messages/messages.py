# messages/messages.py
from dataclasses import dataclass

@dataclass
class InstructionMessage:
    content: str
    source: str
    clearance_lvl: int
    token: str  # Include the authentication token

@dataclass
class DataMessage:
    content: str
    source: str