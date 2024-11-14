# messages/messages.py
from dataclasses import dataclass

@dataclass
class InstructionMessage:
    content: str
    source: str
    clearance_lvl: int
    token: str

@dataclass
class DataMessage:
    content: str
    source: str