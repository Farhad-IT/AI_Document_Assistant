from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.document_model import DocumentModel

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from app.db.base import Base


class DocumentChunksModel(Base):
    __tablename__ = 'documents_chunks'

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey('documents.id'))
    text: Mapped[str]
    page: Mapped[int]

    document: Mapped["DocumentModel"] = relationship(back_populates="document_chunks")