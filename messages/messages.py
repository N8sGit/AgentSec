from pydantic import BaseModel, Field
from typing import Optional

class UserMessage(BaseModel):
    message: str
    sender: str
    token: str

class InstructionMessage(BaseModel):
    message: str
    sender: str
    token: str
    signature: str = Field(..., description="Digital signature for message authentication")

class DataMessage(BaseModel):
    message: str
    timestamp: int
    sender: str
    clearance_lvl: Optional[int] = Field(None, description="Optional to support unclassified data")

class SensitiveDataMessage(BaseModel):
    message: str
    timestamp: int
    sender: str
    sensitivity: str = Field(..., description="Sensitivity level, e.g., 'low', 'medium', 'high'")
    clearance_lvl: int