import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from src.database.models import User
from src.services.auth import auth_service


@pytest.fixture()
def token(client, user, session, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    client.post("/api/auth/signup", json=user)
    current_user: User = (
        session.query(User).filter(User.email == user.get("email")).first()
    )
    current_user.confirmed = True
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": user.get("email"), "password": user.get("password")},
    )
    data = response.json()
    return data["access_token"]


def test_create_contact(client, token):
    with patch.object(auth_service, "r") as r_mock:
        r_mock.get.return_value = None
        response = client.post(
            "/api/contacts",
            json={
                "first_name": "John",
                "last_name": "Doe",
                "email": "test123@example.com",
                "phone_number": "+123456789012",
                "birthday": datetime.today().strftime("%Y-%m-%d"),
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201, response.text
        data = response.json()
        assert data["first_name"] == "John"
        assert data["last_name"] == "Doe"
        assert data["email"] == "test123@example.com"
        assert data["phone_number"] == "+123456789012"
        assert data["birthday"] == datetime.today().strftime("%Y-%m-%d")
        assert "id" in data


def test_read_contacts(client, token):
    with patch.object(auth_service, "r") as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/contacts",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) == 1
    assert data[0]["first_name"] == "John"
    assert data[0]["last_name"] == "Doe"
    assert data[0]["email"] == "test123@example.com"
    assert data[0]["phone_number"] == "+123456789012"
    assert data[0]["birthday"] == datetime.today().strftime("%Y-%m-%d")
    assert data[0]["id"] == 1


def test_search_contacts_found(client, token):
    with patch.object(auth_service, "r") as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/contacts?search=John",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data[0]["first_name"] == "John"
    assert data[0]["last_name"] == "Doe"
    assert data[0]["email"] == "test123@example.com"
    assert data[0]["phone_number"] == "+123456789012"
    assert data[0]["birthday"] == datetime.today().strftime("%Y-%m-%d")
    assert data[0]["id"] == 1


def test_search_contacts_not_found(client, token):
    with patch.object(auth_service, "r") as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/contacts/search?query=Jane",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) == 0


def test_find_birthdays(client, token):
    with patch.object(auth_service, "r") as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/contacts/birthday",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data[0]["first_name"] == "John"
    assert data[0]["last_name"] == "Doe"
    assert data[0]["email"] == "test123@example.com"
    assert data[0]["phone_number"] == "+123456789012"
    assert data[0]["birthday"] == datetime.today().strftime("%Y-%m-%d")
    assert data[0]["id"] == 1


def test_read_contact_found(client, token):
    with patch.object(auth_service, "r") as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/contacts/1",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"
    assert data["email"] == "test123@example.com"
    assert data["phone_number"] == "+123456789012"
    assert data["birthday"] == datetime.today().strftime("%Y-%m-%d")
    assert data["id"] == 1


def test_read_contact_not_found(client, token):
    with patch.object(auth_service, "r") as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/contacts/2",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found"


def test_update_contact_found(client, token):
    with patch.object(auth_service, "r") as r_mock:
        r_mock.get.return_value = None
        response = client.put(
            "/api/contacts/1",
            json={
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "new_email@example.com",
                "phone_number": "+123456789012",
                "birthday": datetime.today().strftime("%Y-%m-%d"),
            },
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["first_name"] == "Jane"
    assert data["last_name"] == "Doe"
    assert data["email"] == "new_email@example.com"
    assert data["phone_number"] == "+123456789012"
    assert data["birthday"] == datetime.today().strftime("%Y-%m-%d")


def test_update_contact_not_found(client, token):
    with patch.object(auth_service, "r") as r_mock:
        r_mock.get.return_value = None
        response = client.put(
            "/api/contacts/2",
            json={
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "new_email@example.com",
                "phone_number": "+123456789012",
                "birthday": datetime.today().strftime("%Y-%m-%d"),
            },
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found"


def test_delete_contact_found(client, token):
    with patch.object(auth_service, "r") as r_mock:
        r_mock.get.return_value = None
        response = client.delete(
            "/api/contacts/1",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["first_name"] == "Jane"
    assert data["last_name"] == "Doe"
    assert data["email"] == "new_email@example.com"
    assert data["phone_number"] == "+123456789012"
    assert data["birthday"] == datetime.today().strftime("%Y-%m-%d")


def test_delete_contact_not_found(client, token):
    with patch.object(auth_service, "r") as r_mock:
        r_mock.get.return_value = None
        response = client.delete(
            "/api/contacts/2",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found"


def test_too_many_requests(client, token):
    with patch.object(auth_service, "r") as r_mock:
        r_mock.get.return_value = None
        for _ in range(10):
            response = client.get(
                "/api/contacts",
                headers={"Authorization": f"Bearer {token}"},
            )
        assert response.status_code == 429, response.text
