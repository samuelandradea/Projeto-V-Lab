from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://vlab:vlab@db:5432/vlab"
    API_KEY: str = "vlab-secret-key-2024"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
