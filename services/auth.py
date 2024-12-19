from core import env
from fastapi import HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext


class AuthService:
    """
    Provides utility methods for authentication and authorization.

    Methods:
        hash_password(password: str) -> str:
            Hashes a plain-text password for secure storage.

        verify_password(plain_password: str, hashed_password: str) -> bool:
            Verifies if a plain-text password matches the hashed version.

        create_access_token(data: dict) -> str:
            Creates a JWT access token with the given payload.

        get_access_token(user) -> dict:
            Generates an access token for the specified user and returns
            it along with the user data.

        decode_token(token: str):
            Decodes and validates a JWT token. Raises an HTTPException for invalid tokens.
    """

    pwd_context = CryptContext(schemes=["sha256_crypt"])

    @classmethod
    def hash_password(cls, password: str) -> str:
        return cls.pwd_context.hash(password)

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        return cls.pwd_context.verify(plain_password, hashed_password)

    @classmethod
    def create_access_token(cls, data: dict) -> str:
        encoded_jwt = jwt.encode(
            data.copy(), env.AUTH_SECRETE_KEY, algorithm=env.AUTH_ALGORITHM
        )
        return encoded_jwt

    @classmethod
    def get_access_token(cls, user) -> dict:
        token = cls.create_access_token(
            data={
                "user_id": user.id,
                "role": jsonable_encoder(user.role_rel),
            }
        )
        return {"token": token, "user": user}

    @classmethod
    def decode_token(cls, token: str):
        try:
            return jwt.decode(
                token, env.AUTH_SECRETE_KEY, algorithms=[env.AUTH_ALGORITHM]
            )
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid Token: {e}"
            )


class UserAuthenticated(HTTPBearer):
    """
    Custom authentication class for validating JWT tokens.

    Methods:
        __call__(request: Request) -> dict:
            Extracts and decodes the JWT token from the request.

        validate_user_type(types: list, user: dict) -> dict:
            Validates the user's role against the allowed types.
            Raises an HTTPException if the user role is not authorized.
    """

    def __init__(self, auto_error: bool = True):
        super(UserAuthenticated, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        token: HTTPAuthorizationCredentials = await super(
            UserAuthenticated, self
        ).__call__(request)
        if token:
            return AuthService.decode_token(token.credentials)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Token"
            )

    def validate_user_type(self, types: list, user: dict):
        if user["role"]["name"] not in types:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not Authorized to perform this operation",
            )
        return user


class IsAuthenticated(UserAuthenticated):
    """
    Extends UserAuthenticated to enforce authentication for specific user roles.
    Roles Allowed: 'admin', 'user'

    Methods:
        __call__(request: Request) -> dict:
            Validates the user's token and checks if the role is in the allowed roles.
    """

    async def __call__(self, request: Request):
        user: dict = await UserAuthenticated.__call__(self, request)
        return UserAuthenticated.validate_user_type(
            self, types=["admin", "user"], user=user
        )


class IsAdmin(IsAuthenticated):
    """
    Extends IsAuthenticated to restrict access to admin users only.
    Role Allowed: 'admin'

    Methods:
        __call__(request: Request) -> dict:
            Validates the user's token and checks if the role is 'admin'.
    """

    async def __call__(self, request: Request):
        user: dict = await IsAuthenticated.__call__(self, request)
        return IsAuthenticated.validate_user_type(self, types=["admin"], user=user)
