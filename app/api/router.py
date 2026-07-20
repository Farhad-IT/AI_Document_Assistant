from fastapi import APIRouter
from app.auth.auth_router import router as auth_router
from app.documents.document_router import router as document_router
from app.chat.chat_router import router as chat_router
from app.websocket.ws_router import router as ws_router

router = APIRouter()

router.include_router(router=auth_router)
router.include_router(router=document_router)
router.include_router(router=chat_router)
router.include_router(router=ws_router)