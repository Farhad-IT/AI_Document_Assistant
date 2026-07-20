from sqlalchemy import select, Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import DocumentChunksModel
from app.models.document_model import DocumentModel


class DocumentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_documents(self, user_id: int) -> Sequence[DocumentModel]:
        documents = select(DocumentModel).filter_by(user_id=user_id)
        res = await self.db.execute(documents)
        return res.scalars().all()

    async def get_all_chunks_by_doc_id(self, document_ids: list) -> Sequence[DocumentChunksModel]:
        chunks = await self.db.execute(select(DocumentChunksModel).filter(DocumentChunksModel.document_id.in_(document_ids)))
        return chunks.scalars().all()


    async def get_by_object_key(self, user_id: int, object_key: str) -> DocumentModel:
        document = select(DocumentModel).filter_by(user_id=user_id, object_key=object_key)
        res = await self.db.execute(document)
        return res.scalar_one_or_none()

    async def create_document(self, user_id: int, filename: str, object_key: str) -> DocumentModel:
        document_metadata = DocumentModel(
            user_id=user_id,
            filename=filename,
            object_key=object_key,
        )

        self.db.add(document_metadata)
        return document_metadata

    async def delete_document(self, document: DocumentModel) -> None:
        await self.db.delete(document)