from typing import Optional
from pydantic import BaseModel, EmailStr

class CustomerCreate(BaseModel):
    name: str
    email: EmailStr
    city: Optional[str] = None

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    city: Optional[str] = None

class CustomerResponse(BaseModel):
    id: int
    name: str
    email: str
    city: Optional[str] = None

    class Config:
        from_attributes = True