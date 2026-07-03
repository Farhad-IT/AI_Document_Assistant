from app.auth.auth_service import AuthService
from app.db.session import SessionDep


def get_auth_service(db: SessionDep):
    """Функция для иньекции зависемости AuthService"""
    return AuthService(db)