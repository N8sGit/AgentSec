from pydantic import BaseModel, Field
from typing import Optional

class InstructionMessage(BaseModel):
    content: str
    sender: str
    token: str
    signature: str = Field(..., description="Digital signature for message authentication")

class DataMessage(BaseModel):
    content: str
    timestamp: int
    sender: str
    clearance_lvl: Optional[int] = Field(None, description="Optional to support unclassified data")

class SensitiveDataMessage(BaseModel):
    content: str
    timestamp: int
    sender: str
    sensitivity: str = Field(..., description="Sensitivity level, e.g., 'low', 'medium', 'high'")
    clearance_lvl: int