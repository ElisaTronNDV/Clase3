import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE = timedelta(hours=int(os.getenv("ACCESS_TOKEN_EXPIRE_HOURS", "24")))
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./lasercore.db")
CORS_ORIGINS = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:4200").split(",")]
