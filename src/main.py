import hashlib
import hmac
import os
from typing import List, Optional
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from src.database import Base, engine, get_db
from src.models import CustomerModel
from src.schemas import CustomerCreate, CustomerResponse, CustomerUpdate

load_dotenv()

API_KEY = os.getenv("API_KEY", "my_secure_api_key_123")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "my_webhook_secret_key_456")

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Task 4 - Secured API")

def verify_api_key(x_api_key: Optional[str] = Header(None)):
    if not x_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing API Key")
    if x_api_key != API_KEY:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API Key")
    return x_api_key

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/customers", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_api_key)])
def create_customer(payload: CustomerCreate, db: Session = Depends(get_db)):
    existing = db.query(CustomerModel).filter(CustomerModel.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Customer with this email already exists")
    cust = CustomerModel(name=payload.name, email=payload.email, city=payload.city)
    db.add(cust)
    db.commit()
    db.refresh(cust)
    return cust

@app.get("/customers", response_model=List[CustomerResponse], dependencies=[Depends(verify_api_key)])
def list_customers(
    page: int = Query(1, ge=1),
    per_page: int = Query(5, ge=1, le=100),
    db: Session = Depends(get_db)
):
    offset = (page - 1) * per_page
    return db.query(CustomerModel).offset(offset).limit(per_page).all()

@app.get("/customers/{customer_id}", response_model=CustomerResponse, dependencies=[Depends(verify_api_key)])
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    cust = db.query(CustomerModel).filter(CustomerModel.id == customer_id).first()
    if not cust:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return cust

@app.put("/customers/{customer_id}", response_model=CustomerResponse, dependencies=[Depends(verify_api_key)])
def update_customer(customer_id: int, payload: CustomerUpdate, db: Session = Depends(get_db)):
    cust = db.query(CustomerModel).filter(CustomerModel.id == customer_id).first()
    if not cust:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    if payload.email and payload.email != cust.email:
        conflict = db.query(CustomerModel).filter(CustomerModel.email == payload.email).first()
        if conflict:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already taken")
        cust.email = payload.email
    if payload.name:
        cust.name = payload.name
    if payload.city:
        cust.city = payload.city
    db.commit()
    db.refresh(cust)
    return cust

@app.delete("/customers/{customer_id}", dependencies=[Depends(verify_api_key)])
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    cust = db.query(CustomerModel).filter(CustomerModel.id == customer_id).first()
    if not cust:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    db.delete(cust)
    db.commit()
    return {"message": "Customer deleted successfully"}

@app.post("/webhooks/order-events")
async def webhook_receiver(request: Request, x_signature: Optional[str] = Header(None)):
    if not x_signature:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing signature header")
    body = await request.body()
    expected_sig = hmac.new(WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected_sig, x_signature):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid signature")
    return {"status": "received"}