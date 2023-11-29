import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import User
from src.repository.users import (
    get_user_by_email,
    create_user,
    update_token,
    confirmed_email,
    update_avatar,
    update_password,
)
from src.schemas import UserModel


class UsersTestCase(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.db = MagicMock(spec=Session)

    async def test_get_user_by_email_found(self):
        email = "test@example.com"
        expected_user = User(email=email)
        self.db.query().filter().first.return_value = expected_user
        user = await get_user_by_email(email, self.db)
        self.assertEqual(user, expected_user)

    async def test_get_user_by_email_not_found(self):
        email = "test@example.com"
        self.db.query().filter().first.return_value = None
        user = await get_user_by_email(email, self.db)
        self.assertIsNone(user)

    async def test_create_user(self):
        body = UserModel(
            username="Orest", email="test@example.com", password="password"
        )
        expected_user = User(**body.model_dump())
        user = await create_user(body, self.db)
        self.assertEqual(user.username, expected_user.username)
        self.assertEqual(user.email, expected_user.email)
        self.assertEqual(user.password, expected_user.password)

    async def test_update_token(self):
        user = User()
        token = "new_token"
        await update_token(user, token, self.db)
        self.assertEqual(user.refresh_token, token)
        self.db.commit.assert_called_once()

    async def test_confirmed_email(self):
        email = "test@example.com"
        user = User(email=email)
        self.db.query.return_value.filter.return_value.first.return_value = user
        await confirmed_email(email, self.db)
        self.assertTrue(user.confirmed)
        self.db.commit.assert_called_once()

    async def test_update_avatar(self):
        email = "test@example.com"
        url = "https://example.com/avatar.jpg"
        user = User(email=email)
        self.db.commit.return_value = None
        self.db.query.return_value.filter.return_value.first.return_value = user
        updated_user = await update_avatar(email, url, self.db)
        self.assertEqual(updated_user, user)
        self.assertEqual(updated_user.avatar, url)
        self.db.commit.assert_called_once()

    async def test_update_password(self):
        user = User()
        new_hash_password = "new_hash_password"
        updated_user = await update_password(user, new_hash_password, self.db)
        self.assertEqual(updated_user, user)
        self.assertEqual(updated_user.password, new_hash_password)
        self.db.commit.assert_called_once()


if __name__ == "__main__":
    unittest.main()
