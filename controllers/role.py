from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from models import RoleMapper
from schemas import RoleSchemaOut
from services import IsAdmin
from core import get_db_session

router = APIRouter(prefix="/role", tags=["ROLE"])


@router.get("", response_model=list[RoleSchemaOut], dependencies=[Depends(IsAdmin())])
async def view_role(session: Session = Depends(get_db_session)):
    """
    Retrieve all roles from the database.

    This function fetches and returns all the roles in the system. Only accessible to users with admin privileges.

    Args:
        session (Session): The database session to interact with the database.

    Dependencies:
        IsAdmin: A dependency that checks if the user has admin privileges.

    Returns:
        list[RoleSchemaOut]: A list of roles in the system.
    """
    return RoleMapper.get_all(session=session)
