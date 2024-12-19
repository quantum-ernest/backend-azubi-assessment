from core import get_db_session
from fastapi import APIRouter, Depends, HTTPException, status
from models import UserMapper
from schemas import (
    ChangePasswordSchemaIn,
    ChangePasswordSchemaOut,
    LoginSchemaIn,
    LoginSchemaOut,
)
from services import AuthService, IsAuthenticated
from sqlalchemy.orm import Session

router = APIRouter(prefix="/auth", tags=["AUTH"])


@router.post("/login", response_model=LoginSchemaOut)
async def login(credential: LoginSchemaIn, session: Session = Depends(get_db_session)):
    """
    Handle user login by verifying the provided credentials.

    This function checks if the user exists in the database by their email and verifies the provided
    password against the stored password hash. If successful, it generates an access token for the user.

    Args:
        credential (LoginSchemaIn): The user's login credentials (email and password).
        session (Session): The database session to interact with the database. It is injected via Dependency Injection.

    Raises:
        HTTPException: If the user is not found or the password is incorrect.

    Returns:
        LoginSchemaOut: A response model containing the access token for the authenticated user.

    ‼️‼️‼️‼️:

    DEFAULT CREDENTIALS:
        **ADMIN_EMAIL  =  admin@example.com**,
        **ADMIN_PASSWORD  =  admin**,
    """
    user = UserMapper.get_by_email(session=session, email=credential.email)
    if user is False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email {credential.email} not found",
        )
    if AuthService.verify_password(credential.password, user.password) is False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
        )
    return AuthService.get_access_token(user)


@router.post("/password-change", response_model=ChangePasswordSchemaOut)
def change_password(
    credential: ChangePasswordSchemaIn,
    session: Session = Depends(get_db_session),
    auth_useer: dict = Depends(IsAuthenticated()),
):
    """
    Change the user's password.

    This function allows authenticated users to change their password. It verifies that the new password
    is different from the old password and updates the user's password in the database if valid.

    Args:
        credential (ChangePasswordSchemaIn): The user's new password credentials.
        session (Session): The database session to interact with the database.
        auth_useer (dict): The authenticated user's information.

    Raises:
        HTTPException: If the new password is the same as the old password.

    Returns:
        ChangePasswordSchemaOut: A response indicating the success of the password change.
    """
    user = UserMapper.get_by_id(session=session, pk_id=auth_useer["user_id"])

    if AuthService.verify_password(credential.new_password, user.password) is True:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The new password cannot be the same as the old password",
        )

    new_hashed_password = AuthService.hash_password(credential.new_password)
    UserMapper.update_password(session=session, user=user, password=new_hashed_password)
    return {"message": "Password changed successfully"}
