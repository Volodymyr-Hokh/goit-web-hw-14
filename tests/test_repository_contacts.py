import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date
import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.repository.contacts import (
    create_contact,
    find_contacts_by_birthday,
    get_contact,
    get_contacts,
    remove_contact,
    search_contacts,
    update_contact,
)
from src.schemas import ContactRequest


class ContactsTestCase(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.user = User(id=1)
        self.db = MagicMock(spec=Session)

    async def test_get_contacts(self):
        offset = 0
        limit = 10
        expected_contacts = [Contact(id=1), Contact(id=2)]
        self.db.query().filter().offset().limit().all.return_value = expected_contacts
        contacts = await get_contacts(offset, limit, self.user, self.db)
        self.assertEqual(contacts, expected_contacts)

    async def test_get_contact_found(self):
        contact_id = 1
        expected_contact = Contact(id=contact_id)
        self.db.query().filter().filter().first.return_value = expected_contact
        contact = await get_contact(contact_id, self.user, self.db)
        self.assertEqual(contact, expected_contact)

    async def test_get_contact_not_found(self):
        contact_id = 1
        self.db.query().filter().filter().first.return_value = None
        contact = await get_contact(contact_id, self.user, self.db)
        self.assertIsNone(contact)

    async def test_create_contact(self):
        body = ContactRequest(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone_number="123456789012",
            birthday=date.today(),
        )
        self.db.add.return_value = None
        self.db.commit.return_value = None
        self.db.refresh.return_value = None

        contact = await create_contact(body, self.user, self.db)

        self.assertEqual(contact.first_name, body.first_name)
        self.assertEqual(contact.last_name, body.last_name)
        self.assertEqual(contact.email, body.email)
        self.assertEqual(contact.phone_number, body.phone_number)
        self.assertEqual(contact.birthday, body.birthday)
        self.assertTrue(hasattr(contact, "id"))

    async def test_update_contact_found(self):
        contact_id = 1
        body = ContactRequest(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone_number="123456789012",
            birthday=date.today(),
        )
        expected_contact = Contact()
        self.db.query().filter().first.return_value = expected_contact
        contact = await update_contact(contact_id, body, self.user, self.db)
        self.assertEqual(contact, expected_contact)

    async def test_update_contact_not_found(self):
        contact_id = 1
        body = ContactRequest(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone_number="123456789012",
            birthday=date.today(),
        )
        self.db.query().filter().first.return_value = None
        contact = await update_contact(contact_id, body, self.user, self.db)
        self.assertIsNone(contact)

    async def test_remove_contact_found(self):
        expected_contact = Contact()
        self.db.query().filter().first.return_value = expected_contact
        contact = await remove_contact(1, self.user, self.db)
        self.assertEqual(contact, expected_contact)

    async def test_remove_note_not_found(self):
        contact_id = 1
        self.db.query().filter().first.return_value = None
        contact = await remove_contact(contact_id, self.user, self.db)
        self.assertIsNone(contact)

    async def test_search_contacts(self):
        query = "John"
        offset = 0
        limit = 10
        expected_contacts = [Contact(id=1), Contact(id=2)]
        self.db.query().filter().offset().limit().all.return_value = expected_contacts
        contacts = await search_contacts(query, offset, limit, self.user, self.db)
        self.assertEqual(contacts, expected_contacts)

    async def test_find_contacts_by_birthday(self):
        offset = 0
        limit = 10
        expected_contacts = [Contact(id=1), Contact(id=2)]
        self.db.query().filter().params().all.return_value = expected_contacts
        contacts = await find_contacts_by_birthday(offset, limit, self.user, self.db)
        self.assertEqual(contacts, expected_contacts)


if __name__ == "__main__":
    unittest.main()
