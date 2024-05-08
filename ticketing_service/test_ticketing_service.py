from fastapi.testclient import TestClient
from ticketing_service.main import app

client = TestClient(app)


def test_register_user():
    """Test case for user registration."""
    # Test successful user registration
    user_data = {"username": "testuser", "password": "testpassword", "role": "standard"}
    response = client.post("/register", json=user_data)
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"
    assert response.json()["role"] == "standard"

    # Test registration with existing username
    response = client.post("/register", json=user_data)
    assert response.status_code == 400


def test_login():
    """Test case for user login."""
    # Test successful user login
    login_data = {"username": "sanjay", "password": "kumar"}
    response = client.post("/login", data=login_data)
    assert response.status_code == 200
    assert "bearer_token" in response.json()

    # Test login with incorrect credentials
    login_data["password"] = "incorrect_password"
    response = client.post("/login", data=login_data)
    assert response.status_code == 401


def test_request_ticketing_link():
    """Test case for requesting a ticketing link."""
    # Test requesting a ticketing link for an authenticated user
    login_data = {"username": "sanjay", "password": "kumar"}
    login_response = client.post("/login", data=login_data)
    token = login_response.json()['bearer_token']

    response = client.get("/request_for_ticketing_link", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    # Todo: Add scenarios

    # Test requesting a ticketing link for a guest user
    response = client.get("/request_for_ticketing_link")
    assert response.status_code == 200


def test_get_ticketing_link():
    """Test case for getting a ticketing link."""
    # Test getting a ticketing link for an authenticated user
    login_data = {"username": "sanjay", "password": "kumar"}
    login_response = client.post("/login", data=login_data)
    token = login_response.json()['bearer_token']

    response = client.get("/get_ticketing_link", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    # Todo: Add scenarios

    # Test getting a ticketing link for a guest user
    response = client.get("/get_ticketing_link")
    assert response.status_code == 200
