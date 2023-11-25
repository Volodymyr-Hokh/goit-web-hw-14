from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Request
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.limiter import limiter
from src.schemas import ContactRequest, ContactResponse
from src.services.auth import auth_service
from src.repository import contacts as repository_contacts

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/", response_model=List[ContactResponse])
@limiter.limit(limit_value="2/5seconds")
async def read_contacts(
    request: Request,
    offset: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    contacts = await repository_contacts.get_contacts(offset, limit, current_user, db)
    return contacts


@router.get("/search", response_model=List[ContactResponse])
@limiter.limit(limit_value="2/5seconds")
async def search_contacts(
    request: Request,
    query: str,
    offset: int = 0,
    limit: int = 10,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    contacts = await repository_contacts.search_contacts(
        query, offset, limit, current_user, db
    )
    return contacts


@router.get("/birthday", response_model=List[ContactResponse])
@limiter.limit(limit_value="2/5seconds")
async def find_birthdays(
    request: Request,
    offset: int = 0,
    limit: int = 10,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    contacts = await repository_contacts.find_contacts_by_birthday(
        offset, limit, current_user, db
    )
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
@limiter.limit(limit_value="2/5seconds")
async def read_contact(
    request: Request,
    contact_id: int,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    contact = await repository_contacts.get_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(limit_value="10/minute")
async def create_contact(
    request: Request,
    body: ContactRequest,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    return await repository_contacts.create_contact(body, current_user, db)


@router.put("/{contact_id}", response_model=ContactResponse)
@limiter.limit(limit_value="10/minute")
async def update_contact(
    request: Request,
    body: ContactRequest,
    contact_id: int,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    contact = await repository_contacts.update_contact(
        contact_id, body, current_user, db
    )
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse)
@limiter.limit(limit_value="10/minute")
async def remove_contact(
    request: Request,
    contact_id: int,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    contact = await repository_contacts.remove_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact
