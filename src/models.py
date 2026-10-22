from sqlalchemy import Column, Integer, String
from src.database import Base

class CustomerModel(Base):
    __tablename__ = "api_customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    city = Column(String(50), nullable=True)

class CustomerModel(Base):
  __tablename__ = "api_customers"
  __table_args__ = {'extend_existing': True}

  id = Column(Integer, primary_key=True, index=True)
  name = Column(String(100), nullable=False)
  email = Column(String(100), unique=True, nullable=False, index=True)
  city = Column(String(50), nullable=True)
  phone = Column(
      String(20), nullable=True
  )  
