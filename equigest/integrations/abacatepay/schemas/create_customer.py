from pydantic import BaseModel

class CreateCustomerSchema(BaseModel):
    name: str
    email: str
    cellphone: str
    tax_id: str