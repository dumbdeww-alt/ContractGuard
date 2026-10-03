from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Contract Guard"
    app_env: str = "development"
    debug: bool = True
    host: str = "127.0.0.1"
    port: int = 8000

    # Explicit database connection URL (e.g. DATABASE_URL env var)
    database_url: str | None = None

    # PostgreSQL Database Configuration
    db_user: str = "postgres"
    db_password: str = "postgres"
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "contract_registry"

    # Kafka Event Streaming Configuration
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_topic: str = "contract-guard-events"
    kafka_consumer_group: str = "contract-guard-group"

    def get_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        return (
            f"postgresql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Provide a cached singleton instance of application settings."""
    return Settings()
