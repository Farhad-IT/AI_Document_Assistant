from app.auth.auth_service import AuthService
from app.chat.chat_service import ChatService
from app.db.session import SessionDep
from app.documents.document_service import DocumentService
from app.minio_client import client


def get_auth_service(db: SessionDep):
    """Функция для иньекции зависемости AuthService"""
    return AuthService(db=db)

def get_document_service(db: SessionDep):
    """Функция для иньекции зависемости DocumentService"""
    return DocumentService(db=db, minio_client=client)

def get_chat_service(db: SessionDep):
    """Функция для иньекции зависемости ChatService"""
    return ChatService(db=db)
