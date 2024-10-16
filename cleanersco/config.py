from pydantic_settings import (
    BaseSettings as Config,
)

from dotenv import find_dotenv, load_dotenv
import os


load_dotenv(find_dotenv())


class AppConfig(Config):
    host: str = "localhost"
    port: int = 8080
    reload: bool = True
    environment: str = "dev"
    workers: int = 1
    factory: bool = True
    log_level: str = "warning"
    secret: str = os.environ.get("SECRET")
    db_url: str = os.environ.get("DATABASE_URL")
    jwt_algorithm: str = "HS256"
    jwt_token_duration: int = 86400


settings = AppConfig()
