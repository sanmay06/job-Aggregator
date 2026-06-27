# Security tests for the Job Aggregator backend
import os
import pytest
# Set SQLite DB for isolated testing *before* importing the app
os.environ["DATABASE_URL"] = "sqlite:///test.db"

from backend.app import app, db
from backend.database.postgres import Login

@pytest.fixture(scope="module")
def client():
    app.config["TESTING"] = True
    # The app will read DATABASE_URL from the env set above
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        # Cleanup after tests
        with app.app_context():
            db.drop_all()

def test_register_and_login_hashes_password(client):
    # Register a new user
    response = client.post("/reg", json={"username": "alice", "password": "secret123", "email": "alice@example.com"})
    assert response.status_code == 201
    # Verify password is stored hashed (not plain text)
    login_entry = Login.query.filter_by(username="alice").first()
    assert login_entry is not None
    assert login_entry.password != "secret123"
    # Login and receive JWT token
    response = client.post("/login", json={"username": "alice", "password": "secret123"})
    assert response.status_code == 200
    data = response.get_json()
    assert "token" in data
    token = data["token"]
    # Protected endpoint without token should fail
    resp_no_token = client.get("/getprofiles?user=alice")
    assert resp_no_token.status_code == 401
    # Protected endpoint with token should succeed (empty profile list)
    headers = {"Authorization": f"Bearer {token}"}
    resp_ok = client.get("/getprofiles?user=alice", headers=headers)
    assert resp_ok.status_code == 200
    assert resp_ok.get_json()["names"] == []
