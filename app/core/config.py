import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))


class AppSettings():
    def __init__(self):
        self._load_environment()
        self._load_config()

    def _load_environment(self):
        base_dir = Path(__file__).resolve().parent.parent.parent
        env = os.getenv("APP_ENV", "dev")
        env_file = base_dir / f".env.{env}"

        if env_file.exists():
            load_dotenv(dotenv_path=env_file, override=True)
        else:
            fallback = base_dir / ".env"
            load_dotenv(dotenv_path=fallback, override=True)

    def _load_config(self):
        # server config
        self.HOST = os.getenv("HOST", "0.0.0.0")
        self.PORT = int(os.getenv("PORT", 8000))
        self.DEBUG = os.getenv("DEBUG", "false").lower() == "true"

        self.POSTGRES_USER = os.getenv("POSTGRES_USER")
        self.POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
        self.POSTGRES_DB = os.getenv("POSTGRES_DB")
        self.POSTGRES_HOST = os.getenv("POSTGRES_HOST")
        self.POSTGRES_PORT = os.getenv("POSTGRES_PORT")
        self.DATABASE_URL = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

        self.MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
        self.MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
        self.MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
        self.MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME")
        self.MINIO_SECURE = os.getenv("MINIO_SECURE")

        self.ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
        # self.REFRESH_TOKEN_EXPIRE_MINUTES = os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES")
        self.SECRET_KEY = os.getenv("SECRET_KEY")
        self.ALGORITHM = os.getenv("ALGORITHM")

settings = AppSettings()
