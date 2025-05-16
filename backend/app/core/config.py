from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    アプリケーション設定。
    環境変数は .env ファイルから読み込みます。
    """
    # .env ファイルから設定を読み込む
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # アプリ全般
    PROJECT_NAME: str = "Registry Information System API"
    API_V1_STR: str = "/api/v1"

    # JWT 認証
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    DATABASE_URL: str

    # OpenAI API
    OPENAI_API_KEY: str

    # Registry System
    REGISTRY_USERNAME: str
    REGISTRY_PASSWORD: str
    OUTPUT_DIR: str = "./output"
    KEN_ALL_CSV_PATH: str = "./data/x-ken-all.csv"

    # Google Cloud Vision 認証
    GOOGLE_APPLICATION_CREDENTIALS: str

    # Redis (Celery用)
    REDIS_URL: str = "redis://localhost:6379/0"

# 設定をインスタンス化
settings = Settings()
