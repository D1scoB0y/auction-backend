from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env')

    SECRET_KEY: str

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    DB_URL: str

    REDIS_URL: str

    CLIENT_APP_URL: str

    MAIL_SENDER: str
    MAIL_PASSWORD: str

    PHONE_SERVICE_API_KEY: str
    PHONE_SERVICE_COMPAIGN_ID: str

    YOS_KEY_ID: str
    YOS_SECRET_KEY: str

    YOS_BUCKET: str


config = Config()  # type: ignore
