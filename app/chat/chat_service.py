from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.gemini_client import GeminiClient
from app.ai.generator_prompt import generate_prompt
from app.api.exception import NotFoundException
from app.chat.chat_repository import ChatRepository
from app.chat.chat_schemas import ChatHistorySchema
from app.core.log import logger
from app.documents.document_repository import DocumentRepository


class ChatService:
    def __init__(self, db: AsyncSession):
        self.gen_client = GeminiClient()
        self.db = db
        self.document_repository = DocumentRepository(db=self.db)
        self.chat_repository = ChatRepository(db=self.db)

    async def _build_prompt(self, user_id: int, message: str) -> str:
        documents_ids = [d.id for d in await self.document_repository.get_all_documents(user_id=user_id)]

        if not documents_ids:
            raise NotFoundException("documents not found")

        chunks = await self.document_repository.get_all_chunks_by_doc_id(document_ids=documents_ids)

        if not chunks:
            raise NotFoundException("chunks not found")

        context = "\n\n".join(
            f"[Id документа: {chunk.document_id}, страница {chunk.page}]\n{chunk.text}"
            for chunk in chunks
        )

        return generate_prompt(chunks=context, question=message)

    async def message_handler(self, user_id: int, message: str) -> str:
        prompt = await self._build_prompt(user_id=user_id, message=message)

        res = await self.gen_client.send_prompt(prompt=prompt)

        await self.chat_repository.add_chat_history(user_id=user_id, message=message, answer=res.text)

        await self.db.commit()

        logger.info(f"User {user_id} message: {message}, has been processed.")
        return res.text

    async def message_handler_stream(self, user_id: int, message: str) -> AsyncIterator[str]:
        prompt = await self._build_prompt(user_id, message)

        full_answer = ""

        async for chunk in await self.gen_client.send_prompt_stream(prompt=prompt):
            token = chunk.text
            full_answer += token
            yield token

        await self.chat_repository.add_chat_history(user_id=user_id, message=message, answer=full_answer)
        await self.db.commit()
        logger.info(f"User {user_id} message: {message}, has been processed (stream).")

    async def get_history(self, user_id: int, limit: int, page: int) -> list[ChatHistorySchema]:
        page = max(page, 1)
        limit = min(limit, 50)
        offset = (page - 1) * limit
        history = await self.chat_repository.get_chat_history(user_id=user_id, limit=limit, offset=offset)
        return [ChatHistorySchema.model_validate(his) for his in history]
