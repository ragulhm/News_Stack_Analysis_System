from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import os

class Settings(BaseSettings):
    MONGODB_URI: str = Field(..., validation_alias="MONGODB_URI")
    SECRET_KEY: str = Field(..., validation_alias="SECRET_KEY")
    ALGORITHM: str = Field(default="HS256", validation_alias="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=1440, validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    NEWS_API_KEY: str = Field(..., validation_alias="NEWS_API_KEY")
    
    # Domain Matrix
    DB_NAME: str = "stockscope_matrix"
    COLLECTION_USERS: str = "users"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
