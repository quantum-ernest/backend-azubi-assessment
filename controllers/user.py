from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core import get_db_session
from models import UserMapper, RoleMapper
from schemas import UserSchemaOut, UserSchemaIn
from services import IsAuthenticated, IsAdmin, AuthService

router = APIRouter(prefix="/users", tags=["USER"])


@router.get("/", response_model=List[UserSchemaOut], dependencies=[Depends(IsAdmin())])
async def get(
    session: Session = Depends(get_db_session),
):
    """
    Retrieve all users from the database.

    This function fetches and returns all users in the system. Only accessible to users with admin privileges.

    Args:
        session (Session): The database session to interact with the database.

    Dependencies:
        IsAdmin: A dependency that checks if the user has admin privileges.

    Returns:
        List[UserSchemaOut]: A list of users in the system.
    """
    return UserMapper.get_all(session=session)


@router.get("/profile", response_model=UserSchemaOut)
async def get_profile(
    session: Session = Depends(get_db_session),
    auth_user: dict = Depends(IsAuthenticated()),
):
    """
    Retrieve the profile of the authenticated user.

    This function fetches and returns the details of the currently authenticated user.

    Args:
        session (Session): The database session to interact with the database.
        auth_user (dict): The authenticated user's information.

    Dependencies:
        IsAuthenticated: A dependency that checks if the user is authenticated.

    Returns:
        UserSchemaOut: The profile of the authenticated user.
    """
    return UserMapper.get_by_id(session=session, pk_id=auth_user["user_id"])


@router.post("", response_model=UserSchemaOut)
async def create(data: UserSchemaIn, session: Session = Depends(get_db_session)):
    """
    Create a new user in the system.

    This function allows the creation of a new user after validating the provided data (e.g., checking if the email
    is already registered and if the passwords match).

    Args:
        data (UserSchemaIn): The user's input data for account creation.
        session (Session): The database session to interact with the database.

    Raises:
        HTTPException: If the email is already registered or if the passwords do not match.

    Returns:
        UserSchemaOut: The newly created user.
    """
    val_email = UserMapper.get_by_email(session=session, email=data.email)
    if val_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    if data.password == data.confirm_password:
        hashed_password = AuthService.hash_password(data.password)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Password do not match"
        )
    role = RoleMapper.get_role_by_name(session=session, name="user")
    user_obj = data.model_dump()
    user_obj.pop("confirm_password")
    user_obj.update(
        {
            "password": hashed_password,
            "role_id": role.id,
        }
    )
    return UserMapper.create(session=session, data=user_obj)
