from pydantic import BaseModel, Field
from typing import Optional
import uuid

class AuthUserMessage(BaseModel):
    message: str
    sender: str
    token: str

class InstructionMessage(BaseModel):
    message: str
    timestamp: int
    id: str = str(uuid.uuid4()) 
    sender: str
    token: str
    signature: str = Field(..., description="Digital signature for message authentication")
    
class DataMessage(BaseModel):
    message: str
    timestamp: int
    sender: str
    id: str = str(uuid.uuid4()) 
    clearance_level: Optional[int] = Field(None, description="Optional to support unclassified data")