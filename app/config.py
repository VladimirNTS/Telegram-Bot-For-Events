import os
from typing import Optional
from pydantic import BaseModel
 

class Settings(BaseModel):
    DATABASE_URL: Optional[str] = os.getenv('DB_URL')
    SECRET_KEY: Optional[str] = os.getenv('SECRET_KEY')
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ADMIN_USERNAME: Optional[str] = os.getenv('LOGIN')
    ADMIN_PASSWORD: Optional[str] = os.getenv('PASSWORD')
    
    class Config:
        env_file = ".env"


settings = Settings()

