from pydantic import BaseModel
from typing import Optional

class CreateTicket(BaseModel):
    customer_name: str
    customer_email: str
    subject: str
    description: str

class UpdateTicket(BaseModel):
    status: Optional[str] = None
    note: Optional[str] = None
