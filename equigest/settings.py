from typing import Optional

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
    REDIS_URL_DEV: str

    ABACATEPAY_KEY: Optional[str] = None
    RETURN_URL: Optional[str] = None
    COMPLET_URL: Optional[str] = None

    DEFINITIVE_REDIS_URL: Optional[str] = None

    def model_post_init(self, __context) -> None:
        if self.ENVIRONMENT == "production":
            self.ABACATEPAY_KEY = self.ABACATEPAY_PROD_APIKEY
            self.RETURN_URL = self.RETURN_PROD_URL_ABACATEPAY
            self.COMPLET_URL = self.COMPLET_PROD_URL_ABACATEPAY

            self.DEFINITIVE_REDIS_URL = self.REDIS_URL
        else:
            self.ABACATEPAY_KEY = self.ABACATEPAY_DEV_APIKEY
            self.RETURN_URL = self.RETURN_DEV_URL_ABACATEPAY
            self.COMPLET_URL = self.COMPLET_DEV_URL_ABACATEPAY

            self.DEFINITIVE_REDIS_URL = self.REDIS_URL_DEV
