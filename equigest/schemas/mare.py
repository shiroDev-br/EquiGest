from typing import Optional
from datetime import datetime

from pydantic import BaseModel

from equigest.enums.enums import MareType

class MareCreateSchema(BaseModel):
    mare_name: str
    mare_type: MareType
    stallion_name: str
    donor_name: Optional[str] = None
    pregnancy_date: Optional[datetime] = None