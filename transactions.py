from models import Base, engine, SessionLocal, Customer, Product, Order

def init_task3_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    # Reset old test rows
    db.query(Order).delete()
    db.query(Customer).delete()
    db.query(Product).delete()
    
    cust = Customer(id=1, name="Arun", city="Chennai", phone="9876543210")
    prod = Product(id=1, name="Mechanical Keyboard", price=50.00, stock=10)
    db.add_all([cust, prod])
    db.commit()
    db.close()

def place_order(customer_id: int, product_id: int, qty: int, force_error: bool = False):
    db = SessionLocal()
    try:
        
        product = db.query(Product).filter(Product.id == product_id).with_for_update().first()
        if not product or product.stock < qty:
            raise ValueError(f"Insufficient stock! Available: {product.stock if product else 0}")


        product.stock -= qty

    
        if force_error:
            raise RuntimeError("Forced error after stock reduction!")


        total = product.price * qty
        order = Order(
            customer_id=customer_id,
            product_id=product_id,
            quantity=qty,
            total_amount=total
        )
        db.add(order)
        db.commit()
        return True, product.stock
    except Exception as e:
        db.rollback()  
        return False, str(e)
    finally:
        db.close()

if __name__ == "__main__":
    init_task3_db()
    db = SessionLocal()
    
    print(" 1. Testing Normal Order Placement ")
    p = db.query(Product).filter(Product.id == 1).first()
    print(f"Initial stock: {p.stock}")
    
    success, remaining_stock = place_order(customer_id=1, product_id=1, qty=2)
    print(f"Order placed: stock 10 -> {remaining_stock}")

    print("\n 2. Testing Atomicity  ")
    current_stock = db.query(Product).filter(Product.id == 1).first().stock
    print(f"Stock before failed attempt: {current_stock}")

    success, err_msg = place_order(customer_id=1, product_id=1, qty=2, force_error=True)
    
    db.expire_all()
    stock_after_rollback = db.query(Product).filter(Product.id == 1).first().stock
    print(f"Forced failure: rolled back, stock still {stock_after_rollback}")
    
    db.close()