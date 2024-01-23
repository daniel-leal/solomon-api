from typing import Optional

from pydantic import BaseModel


class CreditCardCreate(BaseModel):
    name: str
    limit: float
    invoice_start_day: int


class CreditCardUpdate(BaseModel):
    name: Optional[str] = None
    limit: Optional[float] = None
    invoice_start_day: Optional[int] = None


class CreditCardCreatedResponse(CreditCardCreate):
    id: str


class CreditCardUpdatedResponse(CreditCardCreatedResponse):
    pass
