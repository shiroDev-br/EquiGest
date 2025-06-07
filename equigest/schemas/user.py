from pydantic import BaseModel, Field

from datetime import datetime, timedelta


class UserCreateSchema(BaseModel):
    username: str
    password: str
    next_payment_date: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(days=7))

class UserSchema(BaseModel):
    id: int
    username: str