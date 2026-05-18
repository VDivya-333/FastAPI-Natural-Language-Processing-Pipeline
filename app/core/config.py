from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    OPENAI_BASE_URL: str = "https://api.us.inc/usf/v1/hiring"
    
    MYSQL_DB: str
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_HOST: str
    MYSQL_PORT: int
    
    REDIS_HOST: str
    REDIS_PORT: int

    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8001
    
    CHROMA_DB_DIR: str = "./data/vector_store"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
