import os
from dotenv import load_dotenv
import motor.motor_asyncio
from pymongo import MongoClient
from urllib.parse import quote_plus

# Load environment variables from .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '..','..','.env')
load_dotenv(dotenv_path)

class Settings:
    # Project Info
    PROJECT_NAME: str = "Smart Cart API"
    PROJECT_VERSION: str = "1.0.0"
    PROJECT_DESCRIPTION: str = "API for Smart Cart application"

    # PostgreSQL Database Configuration
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "smart_cart_db")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", 5432))
    DATABASE_URL: str = (
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )

    # MongoDB Configuration
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
    MONGO_CLUSTER_NAME = os.getenv('MONGO_CLUSTER_NAME', 'trailcluster')
    MONGO_USERNAME = quote_plus(os.getenv('MONGO_USERNAME'))
    MONGO_PASSWORD = quote_plus(os.getenv('MONGO_PASSWORD'))
    MONGO_URI = f'mongodb+srv://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_CLUSTER_NAME}.f5n8za4.mongodb.net/'

    # LLM API Key
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "your-gemini-api-key")

    # JWT Security Settings
    JWT_SECRET_KEY: str = os.getenv('JWT_SECRET_KEY')
    JWT_ALGORITHM: str = os.getenv('JWT_ALGORITHM', 'HS256')
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRE_MINUTES', 30))

settings = Settings()