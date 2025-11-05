from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    #AZURE_OPENAI_ENDPOINT: str
    #AZURE_OPENAI_API_VERSION: str = '2024-12-01-preview'
    MODEL_NAME: str = 'gpt-4.1-mini'
    #AZURE_STORAGE_ACCOUNT_CONNECTION_STRING: str
    #AZURE_STORAGE_ACCOUNT_NAME: str
    
    model_config = SettingsConfigDict(env_file=".env", extra="allow")
    
def get_settings():
    return Settings()

settings = get_settings()