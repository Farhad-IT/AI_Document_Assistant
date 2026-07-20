from sqlalchemy import Sequence, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat_history_model import ChatHistoryModel


class ChatRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_chat_history(self, user_id: int, limit: int, offset: int) -> Sequence[ChatHistoryModel]:
        history = await self.db.execute(
            select(ChatHistoryModel)
            .filter_by(user_id=user_id)
            .order_by(ChatHistoryModel.created_at.desc())
            .limit(limit=limit)
            .offset(offset=offset)
        )
        return history.scalars().all()

    async def add_chat_history(self, user_id: int, message: str, answer: str) -> ChatHistoryModel:
        history = ChatHistoryModel(user_id=user_id, message=message, answer=answer)
        self.db.add(history)
        return history
