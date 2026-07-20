from google import genai
from dotenv import load_dotenv
from google.genai.errors import ServerError

from app.api.exception import GeminiException
from app.core.log import logger
from app.core.settings import llm_settings

load_dotenv()


class GeminiClient:
    def __init__(self) -> None:
        self.client = genai.Client(api_key=llm_settings.GEMINI_API_KEY)

    async def send_prompt(self, prompt: str):
        try:
            result = await self.client.aio.models.generate_content(
                model=llm_settings.GEMINI_MODEL,
                contents=prompt
            )
            logger.info(f"sent prompt to gemini server.")
            return result
        except ServerError as e:
            if e.code == 503:
                result = await self.client.aio.models.generate_content(
                    model=llm_settings.GEMINI_RESERVE_MODEL,
                    contents=prompt
                )
                logger.info(f"sent prompt to the backup gemini server")
                return result
            else:
                logger.error(f"Server error: {e}")
                raise GeminiException("Overloaded gemini models. Retry-After.")

    async def send_prompt_stream(self, prompt: str):
        try:
            result = await self.client.aio.models.generate_content_stream(
                model=llm_settings.GEMINI_MODEL,
                contents=prompt
            )
            logger.info(f"sent prompt to gemini server.")
            return result
        except ServerError as e:
            if e.code == 503:
                result = await self.client.aio.models.generate_content_stream(
                    model=llm_settings.GEMINI_RESERVE_MODEL,
                    contents=prompt
                )
                logger.info(f"sent prompt to the backup gemini server")
                return result
            else:
                logger.error(f"Server error: {e}")
                raise GeminiException("Overloaded gemini models. Retry-After.")
