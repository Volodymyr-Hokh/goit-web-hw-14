from datetime import date, timedelta
from typing import List

from sqlalchemy import text, and_
from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import ContactRequest


async def get_contacts(
    offset: int, limit: int, user: User, db: Session
) -> List[Contact]:
    """
    Retrieves a list of contacts for a given user.

    Args:
        offset (int): The number of contacts to skip.\n
        limit (int): The maximum number of contacts to retrieve.\n
        user (User): The user object.\n
        db (Session): The database session.\n

    Returns:
        List[Contact]: A list of contacts.

    """
    return (
        db.query(Contact)
        .filter(Contact.user_id == user.id)
        .offset(offset)
        .limit(limit)
        .all()
    )


async def get_contact(contact_id: int, user: User, db: Session) -> Contact:
    """
    Retrieves a single contact for a given user.

    Args:
        contact_id (int): The ID of the contact.\n
        user (User): The user object.\n
        db (Session): The database session.\n

    Returns:
        Contact: The contact object.

    """
    return (
        db.query(Contact)
        .filter(Contact.user_id == user.id)
        .filter(Contact.id == contact_id)
        .first()
    )


async def create_contact(body: ContactRequest, user: User, db: Session) -> Contact:
    """
    Creates a new contact for a given user.

    Args:
        body (ContactRequest): The contact data.\n
        user (User): The user object.\n
        db (Session): The database session.\n

    Returns:
        Contact: The created contact object.

    """
    contact = Contact(
        first_name=body.first_name,
        last_name=body.last_name,
        email=body.email,
        phone_number=body.phone_number,
        birthday=body.birthday,
        user_id=user.id,
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def update_contact(
    contact_id: int, body: ContactRequest, user: User, db: Session
) -> Contact | None:
    """
    Updates an existing contact for a given user.

    Args:
        contact_id (int): The ID of the contact.\n
        body (ContactRequest): The updated contact data.\n
        user (User): The user object.\n
        db (Session): The database session.\n

    Returns:
        Contact | None: The updated contact object, or None if the contact does not exist.

    """
    contact = (
        db.query(Contact)
        .filter(and_(Contact.id == contact_id, Contact.user_id == user.id))
        .first()
    )
    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.phone_number = body.phone_number
        contact.birthday = body.birthday
        db.commit()
    return contact


async def remove_contact(contact_id: int, user: User, db: Session) -> Contact | None:
    """
    Removes a contact for a given user.

    Args:
        contact_id (int): The ID of the contact.\n
        user (User): The user object.\n
        db (Session): The database session.\n

    Returns:
        Contact | None: The removed contact object, or None if the contact does not exist.

    """
    contact = (
        db.query(Contact)
        .filter(and_(Contact.id == contact_id, Contact.user_id == user.id))
        .first()
    )
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def search_contacts(
    query: str, offset: int, limit: int, user: User, db: Session
) -> List[Contact] | None:
    """
    Searches for contacts matching a given query for a given user.

    Args:
        query (str): The search query.\n
        offset (int): The number of contacts to skip.\n
        limit (int): The maximum number of contacts to retrieve.\n
        user (User): The user object.\n
        db (Session): The database session.\n

    Returns:
        List[Contact] | None: A list of matching contacts, or None if no contacts are found.

    """
    contacts = (
        db.query(Contact)
        .filter(
            and_(
                Contact.user_id == user.id,
                (
                    Contact.first_name.ilike(query)
                    | Contact.last_name.ilike(query)
                    | Contact.email.ilike(query)
                ),
            )
        )
        .offset(offset)
        .limit(limit)
        .all()
    )
    return contacts


async def find_contacts_by_birthday(
    offset: int, limit: int, user: User, db: Session
) -> List[Contact] | None:
    """
    Retrieves contacts with upcoming birthdays for a given user.

    Args:
        offset (int): The number of contacts to skip.\n
        limit (int): The maximum number of contacts to retrieve.\n
        user (User): The user object.\n
        db (Session): The database session.\n

    Returns:
        List[Contact] | None: A list of contacts with upcoming birthdays, or None if no contacts are found.

    """
    today = date.today()
    next_week = today + timedelta(days=7)

    contacts = (
        db.query(Contact)
        .filter(
            and_(
                text("TO_CHAR(birthday, 'MM-DD') BETWEEN :start_date AND :end_date"),
                Contact.user_id == user.id,
            )
        )
        .params(
            start_date=today.strftime("%m-%d"), end_date=next_week.strftime("%m-%d")
        )
        .all()
    )

    return contacts
