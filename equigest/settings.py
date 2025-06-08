from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8'
    )

    POSTGRES_URL: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: str
    POSTGRES_USER: str
    ALGORITHM: str
    SECRET_KEY: str
    REDIS_URL: str
    ABACATEPAY_DEV_APIKEY: str
    DB_HOST: str
    FERNET_SECRET_KEY: str
    ABACATEPAY_PROD_APIKEY: str
    ABACATEPAY_WEBHOOK_SECURE_PROD: str
    ENVIRONMENT: str
    RETURN_PROD_URL_ABACATEPAY: str
    COMPLET_PROD_URL_ABACATEPAY: str
    RETURN_DEV_URL_ABACATEPAY: str
    COMPLET_DEV_URL_ABACATEPAY: str