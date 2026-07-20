from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class LLMSettings(BaseSettings):
    GEMINI_API_KEY: str
    GEMINI_MODEL: str
    GEMINI_RESERVE_MODEL: str

llm_settings = LLMSettings()