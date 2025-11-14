import os
from typing import Optional

from pydantic_settings import BaseSettings


class DatabaseConfig(BaseSettings):
    db_host: Optional[str] = "localhost"
    db_out_port: Optional[int] = 5432
    postgres_connection_port: Optional[int] = 5432
    postgres_user: Optional[str] = "postgres"
    postgres_password: Optional[str] = "postgres"
    postgres_db: Optional[str] = "burnout_db"

    class Config:
        env_prefix = ""

    @property
    def dsn(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.db_host}:{self.postgres_connection_port}/{self.postgres_db}"

    @property
    def sync_dsn(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.db_host}:{self.postgres_connection_port}/{self.postgres_db}"

class Config:
    db: DatabaseConfig = DatabaseConfig()
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def setup_config() -> Config:
    return Config()
