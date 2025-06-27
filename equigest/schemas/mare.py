from typing import Optional
from datetime import datetime

from pydantic import BaseModel

from equigest.enums.enums import MareType, DeleteType

class MareSchema(BaseModel):
    mare_name: str
    mare_type: MareType
    stallion_name: str
    donor_name: Optional[str] = None
    pregnancy_date: datetime

class MareListWithManagementScheduleSchema(BaseModel):
    mare: MareSchema
    management_schedule: dict

class MareCreateOrEditSchema(BaseModel):
    mare_name: str
    mare_type: MareType
    stallion_name: str
    donor_name: Optional[str] = None
    pregnancy_date: datetime

class DeleteMareSchema(BaseModel):
    mare_name: str
    delete_type: DeleteType
