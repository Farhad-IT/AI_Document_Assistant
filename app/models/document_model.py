from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user_model import UserModel

from datetime import datetime
from enum import Enum

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as SqlEnum, DateTime, func, ForeignKey

from app.db.base import Base

class StatusEnum(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    READY = "READY"
    FAILED = "FAILED"


class DocumentModel(Base):
    __tablename__ = 'documents'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    filename: Mapped[str]
    object_key: Mapped[str] = mapped_column(unique=True, nullable=False)
    status: Mapped["StatusEnum"] = mapped_column(SqlEnum(StatusEnum), default=StatusEnum.PENDING)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), server_default=func.now(), nullable=False
    )
    processed_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)

    user: Mapped["UserModel"] = relationship(back_populates="documents")
    document_chunks: Mapped[list["DocumentChunksModel"]] = relationship(back_populates="document", passive_deletes=True)


class DocumentChunksModel(Base):
    __tablename__ = 'document_chunks'

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey('documents.id', ondelete="CASCADE"))
    index: Mapped[int]
    text: Mapped[str]
    page: Mapped[int]

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), server_default=func.now(), nullable=False
    )

    document: Mapped["DocumentModel"] = relationship(back_populates="document_chunks")