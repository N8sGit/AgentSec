from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uuid


class DataItem(BaseModel):
    id: str = uuid.uuid4().hex
    content: str
    clearance_level: int = 0  # 0: unclassified, 1: edge, 2: auditor, 3: core
    timestamp: datetime = datetime.now()
    owner: Optional[str] = None