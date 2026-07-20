from uuid import uuid4

from fastapi import UploadFile
from minio import Minio
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.exception import NotFoundException
from app.documents.document_repository import DocumentRepository
from app.documents.document_schemas import DocumentSchema
from app.documents.minio_service import MinioService
from app.worker.tasks import document_handler


class DocumentService:
    def __init__(self, db: AsyncSession, minio_client: Minio):
        self.db = db
        self.minio_client = minio_client
        self.document_repository = DocumentRepository(db=db)
        self.minio_service = MinioService(minio_client=minio_client)

    async def get_all_documents(self, user_id: int) -> list[DocumentSchema]:
        documents = await self.document_repository.get_all_documents(user_id=user_id)

        if not documents:
            raise NotFoundException("Document not found")

        return [DocumentSchema.model_validate(doc) for doc in documents]

    async def upload_document(self, user_id: int, file: UploadFile) -> DocumentSchema:
        object_key = f"{uuid4()}_{file.filename}"
        document_metadata = await self.document_repository.create_document(user_id=user_id, filename=file.filename, object_key=object_key)
        await self.minio_service.upload_document(object_name=object_key, file=file)

        await self.db.commit()
        await self.db.refresh(document_metadata)
        document_handler.delay(user_id=user_id, object_key=object_key)
        return DocumentSchema.model_validate(document_metadata)

    async def delete_document(self, user_id: int, object_key: str) -> None:
        document = await self.document_repository.get_by_object_key(user_id=user_id, object_key=object_key)

        if not document:
            raise NotFoundException("Document not found")

        await self.document_repository.delete_document(document=document)
        await self.minio_service.delete_document(object_name=object_key)
        await self.db.commit()
