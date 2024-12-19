from pydantic import EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvConfig(BaseSettings):
    """
    Configuration class for loading environment variables.

    This class uses `pydantic`'s `BaseSettings` to load environment variables
    from an `.env` file, providing a way to configure the application's settings.

    Attributes:
        POSTGRES_USER (str): The PostgreSQL user for the database connection.
        POSTGRES_PASSWORD (str): The password for the PostgreSQL user.
        POSTGRES_DB_NAME (str): The name of the PostgreSQL database.
        POSTGRES_HOST (str): The host for the PostgreSQL database.
        POSTGRES_PORT (str): The port for the PostgreSQL database.
        AUTH_SECRETE_KEY (str): The secret key used for JWT encoding/decoding.
        AUTH_ALGORITHM (str): The algorithm used for JWT encoding/decoding.
        ADMIN_DEFAULT_EMAIL (EmailStr): The default email for the admin user.
        ADMIN_DEFAULT_NAME (str): The default name for the admin user.
        ADMIN_DEFAULT_PASSWORD (str): The default password for the admin user.

    This class loads the environment variables from a `.env` file located
    at the root of the project directory.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB_NAME: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    AUTH_SECRETE_KEY: str
    AUTH_ALGORITHM: str
    ADMIN_DEFAULT_EMAIL: EmailStr
    ADMIN_DEFAULT_NAME: str
    ADMIN_DEFAULT_PASSWORD: str


env = EnvConfig()
