from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile

from app.api.dependencies import get_document_service
from app.auth.auth_dependencies import CurrentUser
from app.documents.document_schemas import DocumentSchema
from app.documents.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["documents"])

DocumentServiceDep = Annotated[DocumentService, Depends(get_document_service)]


@router.get("", status_code=200)
async def get_documents(
        current_user: CurrentUser,
        document_service: DocumentServiceDep
) -> list[DocumentSchema]:
    return await document_service.get_all_documents(user_id=current_user.id)


@router.post("", status_code=201)
async def upload_document(
        file: UploadFile,
        current_user: CurrentUser,
        document_service: DocumentServiceDep
) -> DocumentSchema:
    return await document_service.upload_document(user_id=current_user.id, file=file)


@router.delete("/{object_key}", status_code=204)
async def delete_document(
        object_key: str,
        current_user: CurrentUser,
        document_service: DocumentServiceDep
) -> None:
    return await document_service.delete_document(user_id=current_user.id, object_key=object_key)