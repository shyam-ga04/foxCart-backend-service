from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SUPABASE_DB_URL: str

    class Config:
        env_file = ".env"

settings = Settings()
