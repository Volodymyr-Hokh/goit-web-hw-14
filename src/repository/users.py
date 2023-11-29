from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel


async def get_user_by_email(email: str, db: Session) -> User:
    """
    Retrieves a user from the database based on their email.

    Args:
        email (str): The email of the user.\n
        db (Session): The database session.\n\n

    Returns:
        User: The user object.

    """
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: Session) -> User:
    """
    Creates a new user in the database.

    Args:
        body (UserModel): The user data.\n
        db (Session): The database session.\n

    Returns:
        User: The newly created user object.

    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: Session) -> None:
    """
    Updates the refresh token of a user.

    Args:
        user (User): The user object.\n
        token (str | None): The new refresh token.\n
        db (Session): The database session.\n

    Returns:
        None

    """
    user.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    """
    Confirms the email of a user.

    Args:
        email (str): The email of the user.\n
        db (Session): The database session.\n

    Returns:
        None

    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email, url: str, db: Session) -> User:
    """
    Updates the avatar of a user.

    Args:
        email: The email of the user.\n
        url (str): The URL of the new avatar.\n
        db (Session): The database session.\n

    Returns:
        User: The updated user object.

    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user


async def update_password(user: UserModel, new_hash_password: str, db: Session):
    """
    Updates the password of a user.

    Args:
        user (UserModel): The user object.\n
        new_hash_password (str): The new hashed password.\n
        db (Session): The database session.\n

    Returns:
        User: The updated user object.

    """
    user.password = new_hash_password
    db.commit()
    return user
