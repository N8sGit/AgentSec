# messages/messages.py
from dataclasses import dataclass

@dataclass
class InstructionMessage:
    content: str
    sender: str
    clearance_lvl: int
    token: str

@dataclass
class DataMessage:
    content: str
    timestamp: int
    sender: str