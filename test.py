import hmac
import hashlib
import json
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.database import Base, get_db
from src.main import app


TEST_DB_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

API_KEY = "my_secure_api_key_123"
AUTH_HEADER = {"X-API-Key": API_KEY}
WEBHOOK_SECRET = "my_webhook_secret_key_456"

@pytest.fixture(autouse=True)
def setup_and_teardown():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


def test_missing_api_key_401():
    res = client.get("/customers")
    assert res.status_code == 401
    assert res.json()["detail"] == "Missing API Key"


def test_wrong_api_key_403():
    res = client.get("/customers", headers={"X-API-Key": "incorrect_key"})
    assert res.status_code == 403
    assert res.json()["detail"] == "Invalid API Key"


def test_create_customer_success_201():
    res = client.post(
        "/customers", 
        json={"name": "Karthik", "email": "karthik@test.com", "city": "Chennai"}, 
        headers=AUTH_HEADER
    )
    assert res.status_code == 201
    assert res.json()["email"] == "karthik@test.com"


def test_duplicate_email_409():
    payload = {"name": "User 1", "email": "dup@test.com"}
    client.post("/customers", json=payload, headers=AUTH_HEADER)
    res = client.post("/customers", json=payload, headers=AUTH_HEADER)
    assert res.status_code == 409

def test_validation_error_422():
    res = client.post("/customers", json={"name": "No Email User"}, headers=AUTH_HEADER)
    assert res.status_code == 422


def test_customer_not_found_404():
    res = client.get("/customers/999", headers=AUTH_HEADER)
    assert res.status_code == 404

def test_list_customers_pagination_200():
    for i in range(1, 6):
        client.post(
            "/customers", 
            json={"name": f"User {i}", "email": f"user{i}@test.com"}, 
            headers=AUTH_HEADER
        )
    res = client.get("/customers?page=1&per_page=5", headers=AUTH_HEADER)
    assert res.status_code == 200
    assert len(res.json()) == 5


def test_webhook_valid_signature_200():
    payload = json.dumps({"order_id": 101, "status": "shipped"}).encode("utf-8")
    sig = hmac.new(WEBHOOK_SECRET.encode(), payload, hashlib.sha256).hexdigest()
    res = client.post("/webhooks/order-events", content=payload, headers={"X-Signature": sig})
    assert res.status_code == 200
    assert res.json() == {"status": "received"}

def test_webhook_tampered_signature_401():
    payload = json.dumps({"order_id": 101, "status": "shipped"}).encode("utf-8")
    res = client.post("/webhooks/order-events", content=payload, headers={"X-Signature": "tampered_fake_signature"})
    assert res.status_code == 401
    assert res.json()["detail"] == "Invalid signature"