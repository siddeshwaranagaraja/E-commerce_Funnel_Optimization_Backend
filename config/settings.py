from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql://user:password@localhost/db"
    redis_url: str = "redis://localhost:6379"
    openai_api_key: str
    cors_origins: list[str] = ["http://localhost:3000"]
    app_name: str = "E-commerce Funnel Optimization"

settings = Settings()