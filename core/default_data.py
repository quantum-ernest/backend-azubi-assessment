from core import SessionLocal, env
from models import RoleMapper, UserMapper
from services.auth import AuthService
from sqlalchemy.dialects.postgresql import insert


def set_default_data():
    """
    Sets up default data in the database.

    This function ensures that default roles and an admin user are created in the
    database if they don't already exist. It uses the `SessionLocal` to interact with
    the database and performs the following actions:

    - Creates a "user" role if it doesn't exist, using the `RoleMapper`.
    - Creates an "admin" role if it doesn't exist, using the `RoleMapper`.
    - Creates a default admin user with the email, name, and password defined in the environment
      variables (`env.ADMIN_DEFAULT_EMAIL`, `env.ADMIN_DEFAULT_NAME`, `env.ADMIN_DEFAULT_PASSWORD`).
      The admin user is associated with the "admin" role.

    The function uses PostgreSQL's `on_conflict_do_update` to ensure that existing records
    with the same unique constraints are updated instead of duplicated.

    Returns:
        bool: Returns `True` if the data is successfully set, indicating that the
              operation has completed.
    """
    with SessionLocal() as session:
        session.scalars(
            insert(RoleMapper)
            .values(name="user")
            .returning(RoleMapper)
            .on_conflict_do_update(
                constraint="unique_name",
                set_=dict(name="user"),
            )
        ).first()

        admin_role = session.scalars(
            insert(RoleMapper)
            .values(name="admin")
            .returning(RoleMapper)
            .on_conflict_do_update(
                constraint="unique_name",
                set_=dict(name="admin"),
            )
        ).first()
        session.scalars(
            insert(UserMapper)
            .values(
                email=env.ADMIN_DEFAULT_EMAIL,
                name=env.ADMIN_DEFAULT_NAME,
                role_id=admin_role.id,
                password=AuthService.hash_password(env.ADMIN_DEFAULT_PASSWORD),
            )
            .on_conflict_do_update(
                constraint="unique_email_name",
                set_=dict(
                    email=env.ADMIN_DEFAULT_EMAIL,
                    name=env.ADMIN_DEFAULT_NAME,
                    role_id=admin_role.id,
                    password=AuthService.hash_password(env.ADMIN_DEFAULT_PASSWORD),
                ),
            )
        ).first()
        session.commit()
    return True
