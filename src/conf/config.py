from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    sqlalchemy_database_url: str = "postgresql+psycopg2://mock:mock@mock:1234/mock"
    test_sqlalchemy_database_url: str = "postgresql+psycopg2://mock:mock@mock:1234/test"

    secret_key: str = "mock"
    algorithm: str = "mock"

    mail_username: str = "mock12345@example.com"
    mail_password: str = "mock"
    mail_from: str = "mock12345@example.com"
    mail_port: int = 465
    mail_server: str = "mock"

    redis_host: str = "mock"
    redis_port: int = 6379

    cloudinary_name: str = "mock"
    cloudinary_api_key: str = "mock"
    cloudinary_api_secret: str = "mock"

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8", extra="allow")


settings = Settings()
