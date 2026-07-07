from tests.confest import client
import uuid

def test_register(client):
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "username": f"user_{uuid.uuid4().hex[:8]}",
            "email": f"{uuid.uuid4()}@gmail.com",
            "password": "Password123"
        }
    )

    print("Status:", response.status_code)
    print("Response:", response.text)

    assert response.status_code == 201