#from pydantic_settings import BaseSettings, SettingsConfigDict

import pydantic_settings

class Settings(pydantic_settings.BaseSettings):
    client_id: str
    client_secret: str
    refresh_token: str
    
    model_config = pydantic_settings.SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

settings = Settings(_env_file='.env', _env_file_encoding='utf-8')

