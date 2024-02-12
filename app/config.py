#from pydantic_settings import BaseSettings, SettingsConfigDict

import pydantic_settings

class Settings(pydantic_settings.BaseSettings):
    database_url: str
    client_id: str
    client_secret: str
    refresh_token: str
    google_application_credentials: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    
    model_config = pydantic_settings.SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

settings = Settings(_env_file='.env', _env_file_encoding='utf-8')

