from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql://user:password@localhost/db"
    redis_url: str = "redis://localhost:6379"
    openai_api_key: str
    cors_origins: list[str] = ["http://localhost:3000"]
    app_name: str = "E-commerce Funnel Optimization"
    
    # SQLAlchemy settings
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    db_echo: bool = False

settings = Settings()