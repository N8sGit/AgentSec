from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
import uuid


class DataItem(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    content: str
    clearance_level: int = 0  # 0: unclassified, 1: edge, 2: auditor, 3: core
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    owner: Optional[str] = None