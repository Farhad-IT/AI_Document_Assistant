from typing import Annotated

from fastapi import WebSocket, WebSocketDisconnect, APIRouter, Depends

from app.api.dependencies import get_chat_service
from app.api.exception import NotFoundException
from app.auth.auth_dependencies import get_current_user_ws
from app.chat.chat_service import ChatService
from app.db.session import SessionDep

ALLOWED_ORIGINS = {"http://localhost:63342"}

router = APIRouter()

ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]


@router.websocket("/chat/ws")
async def chat_ws(
    websocket: WebSocket,
    db: SessionDep,
    chat_service: ChatServiceDep,
):
    if websocket.headers.get("origin") not in ALLOWED_ORIGINS:
        await websocket.close(code=4403)
        return

    user = await get_current_user_ws(websocket, db)

    if user is None:
        await websocket.close(code=4401)
        return

    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()

            if data.get("type") != "message":
                continue

            question = data["message_text"]

            try:
                full_answer = ""

                async for token in chat_service.message_handler_stream(user_id=user.id, message=question):
                    full_answer += token
                    await websocket.send_json({"type": "chunk", "text": token})

                await websocket.send_json({"type": "done", "answer": full_answer})

            except NotFoundException as e:
                await websocket.send_json({"type": "error", "detail": str(e)})

    except WebSocketDisconnect:
        pass