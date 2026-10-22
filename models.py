import os
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import (
    create_engine, Column, Integer, String, Numeric, DateTime, ForeignKey, CheckConstraint
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Customer(Base):
    __tablename__ = "task3_customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    city = Column(String(50), nullable=False)
    phone = Column(String(20), nullable=True)

    orders = relationship("Order", back_populates="customer", cascade="all, delete-orphan")

class Product(Base):
    __tablename__ = "task3_products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    stock = Column(Integer, nullable=False, default=0)

    __table_args__ = (
        CheckConstraint("stock >= 0", name="check_stock_non_negative"),
    )

class Order(Base):
    __tablename__ = "task3_orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("task3_customers.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("task3_products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    ordered_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="orders")
    product = relationship("Product")