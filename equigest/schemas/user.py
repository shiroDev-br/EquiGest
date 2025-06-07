from pydantic import BaseModel, Field

from datetime import datetime, timedelta

from equigest.enums.enums import PaymentAccessStatus

class UserCreateSchema(BaseModel):
    username: str
    password: str
    email: str
    cellphone: str
    cpf_cnpj: str
    abacatepay_client_id: int = None
    next_payment_date: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(days=7))

class UserSchema(BaseModel):
    id: int
    username: str
    next_payment_date: datetime
    payment_status: PaymentAccessStatus