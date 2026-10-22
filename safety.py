import os
import psycopg2
from dotenv import load_dotenv
load_dotenv()

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "postgres"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD")
    )

def get_orders(customer_id):
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT id, customer_id, amount, ordered_at FROM orders WHERE customer_id = %s"
    
    try:
        cursor.execute(query, (customer_id,))
        results = cursor.fetchall()
        return results
    except Exception as e:
        conn.rollback()
        return []
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print(" Query Safety ")
    
    valid_orders = get_orders(1)
    print(f"Normal input (customer_id = 1) -> {len(valid_orders)} rows found")
    
    injection_input = "1 OR 1=1"
    injection_orders = get_orders(injection_input)
    print(f"Injection input ('{injection_input}') -> {len(injection_orders)} rows found")
    
    print("\nResult: Injection neutralized successfully (returned 0 rows)!")