from datetime import date, timedelta
import unittest
from unittest.mock import MagicMock

from sqlalchemy import text
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
        self.db.query.assert_called_once_with(Contact)
        self.db.query().filter.assert_called_once_with(Contact.user_id == self.user.id)
        self.db.query().filter().offset.assert_called_once_with(offset)
        self.db.query().filter().limit.assert_called_once_with(limit)

    async def test_get_contact(self):
        contact_id = 1
        expected_contact = Contact(id=contact_id)
        self.db.query().filter().filter().first.return_value = expected_contact

        contact = await get_contact(contact_id, self.user, self.db)

        self.assertEqual(contact, expected_contact)
        self.db.query.assert_called_once_with(Contact)
        self.db.query().filter.assert_called_once_with(Contact.user_id == self.user.id)
        self.db.query().filter().filter.assert_called_once_with(
            Contact.id == contact_id
        )

    async def test_create_contact(self):
        body = ContactRequest(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone_number="123456789012",
            birthday=date.today(),
        )
        expected_contact = Contact(id=1)
        self.db.add.return_value = None
        self.db.commit.return_value = None
        self.db.refresh.return_value = None

        contact = await create_contact(body, self.user, self.db)

        self.assertEqual(contact, expected_contact)
        self.db.add.assert_called_once_with(
            Contact(
                first_name=body.first_name,
                last_name=body.last_name,
                email=body.email,
                phone_number=body.phone_number,
                birthday=body.birthday,
                user_id=self.user.id,
            )
        )
        self.db.commit.assert_called_once()
        self.db.refresh.assert_called_once_with(expected_contact)

    async def test_update_contact(self):
        contact_id = 1
        body = ContactRequest(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone_number="1234567890",
            birthday=date.today(),
        )
        expected_contact = Contact(id=contact_id)
        self.db.query().filter().filter().first.return_value = expected_contact
        self.db.commit.return_value = None

        contact = await update_contact(contact_id, body, self.user, self.db)

        self.assertEqual(contact, expected_contact)
        self.db.query.assert_called_once_with(Contact)
        self.db.query().filter.assert_called_once_with(
            Contact.id == contact_id, Contact.user_id == self.user.id
        )
        self.db.commit.assert_called_once()

    async def test_remove_contact(self):
        contact_id = 1
        expected_contact = Contact(id=contact_id)
        self.db.query().filter().filter().first.return_value = expected_contact
        self.db.commit.return_value = None

        contact = await remove_contact(contact_id, self.user, self.db)

        self.assertEqual(contact, expected_contact)
        self.db.query.assert_called_once_with(Contact)
        self.db.query().filter.assert_called_once_with(
            Contact.id == contact_id, Contact.user_id == self.user.id
        )
        self.db.delete.assert_called_once_with(expected_contact)
        self.db.commit.assert_called_once()

    async def test_search_contacts(self):
        query = "John"
        offset = 0
        limit = 10
        expected_contacts = [Contact(id=1), Contact(id=2)]
        self.db.query().filter().offset().limit().all.return_value = expected_contacts

        contacts = await search_contacts(query, offset, limit, self.user, self.db)

        self.assertEqual(contacts, expected_contacts)
        self.db.query.assert_called_once_with(Contact)
        self.db.query().filter.assert_called_once_with(
            Contact.user_id == self.user.id,
            (
                Contact.first_name.ilike(query)
                | Contact.last_name.ilike(query)
                | Contact.email.ilike(query)
            ),
        )
        self.db.query().filter().offset.assert_called_once_with(offset)
        self.db.query().filter().limit.assert_called_once_with(limit)

    async def test_find_contacts_by_birthday(self):
        offset = 0
        limit = 10
        expected_contacts = [Contact(id=1), Contact(id=2)]
        self.db.query().filter().params().all.return_value = expected_contacts

        contacts = await find_contacts_by_birthday(offset, limit, self.user, self.db)

        self.assertEqual(contacts, expected_contacts)
        self.db.query.assert_called_once_with(Contact)
        self.db.query().filter.assert_called_once_with(
            text("TO_CHAR(birthday, 'MM-DD') BETWEEN :start_date AND :end_date"),
            Contact.user_id == self.user.id,
        )
        self.db.query().filter().params.assert_called_once_with(
            start_date=date.today().strftime("%m-%d"),
            end_date=(date.today() + timedelta(days=7)).strftime("%m-%d"),
        )
        self.db.query().filter().params().all.assert_called_once()


if __name__ == "__main__":
    unittest.main()
