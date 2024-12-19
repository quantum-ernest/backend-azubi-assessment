import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, insert
from sqlalchemy.orm import sessionmaker
from main import app  # Replace `your_app.main` with your app module
from models import Base, UserMapper, RoleMapper  # Replace with your database module
from core import get_db_session
from services import AuthService

# Create a test database (use SQLite in-memory for demo purposes)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  # SQLite file-based demo
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Create a dependency override for testing
def override_get_db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def override_is_authenticated():
    print("invoked")
    return {"user_id": 1, "role": "admin"}


app.dependency_overrides[get_db_session] = override_get_db


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    with TestingSessionLocal() as session:
        session.execute(insert(RoleMapper).values(id=1, name="admin"))
        session.execute(insert(RoleMapper).values(id=2, name="user"))
        session.execute(
            insert(UserMapper).values(
                email="test@example.com",
                name="Test User",
                role_id=1,
                password=AuthService.hash_password("TestPass"),
            )
        )
        session.commit()
    yield
    Base.metadata.drop_all(bind=engine)
    os.remove("test.db")


client = TestClient(app)


@pytest.fixture(scope="module")
def auth_token():
    response = client.post(
        "/auth/login", json={"email": "test@example.com", "password": "TestPass"}
    )
    token = response.json()["token"]
    assert response.status_code == 200
    assert response.json()["user"]["email"] == "test@example.com"
    assert response.json()["user"]["name"] == "Test User"
    assert response.json()["user"]["role_rel"]["name"] == "admin"
    assert token is not None
    return token


@pytest.fixture(scope="module")
def create_product(auth_token):
    response = client.post(
        "/products",
        data={"name": "Laptop", "price": 250, "category": "Electronics"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Laptop"
    return response.json()


@pytest.fixture(scope="module")
def create_cart(auth_token, create_product):
    product_id = create_product["id"]
    response = client.post(
        "/cart",
        json={"quantity": 5, "product_id": product_id},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    assert response.json()["quantity"] == 5
    assert response.json()["product_rel"]["name"] == "Laptop"
    return response.json()


def test_get_all_product(auth_token):
    response = client.get(
        "/products", headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 0


def test_get_product(auth_token, create_product):
    product_id = create_product.get("id")
    response = client.get(
        f"/products/{product_id}", headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Laptop"


def test_update_product(auth_token, create_product):
    product_id = create_product.get("id")
    response = client.put(
        f"/products/{product_id}",
        data={"id": 1, "name": "Laptop", "price": 150, "category": "Electronics"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    assert response.json()["price"] == 150


def test_get_cart(auth_token):
    response = client.get("/cart", headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 200
    assert len(response.json()) == 0


def test_update_cart(auth_token, create_cart, create_product):
    product_id = create_product.get("id")
    cart_id = create_cart.get("id")
    response = client.put(
        f"/cart/{cart_id}",
        json={"quantity": 10, "product_id": product_id},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    assert response.json()["quantity"] == 10
    assert response.json()["product_rel"]["name"] == "Laptop"


def test_delete_cart(auth_token, create_cart):
    cart_id = create_cart.get("id")
    response = client.delete(
        f"/cart/{cart_id}", headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert response.text == "204"


def test_delete_product(auth_token, create_product):
    product_id = create_product.get("id")
    response = client.delete(
        f"/products/{product_id}", headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert response.text == "204"
