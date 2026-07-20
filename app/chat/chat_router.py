from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import get_chat_service
from app.auth.auth_dependencies import CurrentUser
from app.chat.chat_schemas import MessageSchema, ChatHistorySchema
from app.chat.chat_service import ChatService
from app.redis.rate_limiter import rate_limiter

router = APIRouter(prefix="/chat", tags=["chat"])

ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]


@router.post("/message", status_code=201, dependencies=[Depends(rate_limiter(max_requests=3, window_seconds=60))])
async def create_chat_message(
        message: MessageSchema,
        current_user: CurrentUser,
        chat_service: ChatServiceDep
):
    return await chat_service.message_handler(user_id=current_user.id, message=message.message_text)


@router.get("/history", status_code=200, dependencies=[Depends(rate_limiter(max_requests=10, window_seconds=60))])
async def get_chat_history(
        current_user: CurrentUser,
        chat_service: ChatServiceDep,
        limit: int = 10,
        page: int = 1,
) -> list[ChatHistorySchema]:
    return await chat_service.get_history(user_id=current_user.id, limit=limit, page=page)