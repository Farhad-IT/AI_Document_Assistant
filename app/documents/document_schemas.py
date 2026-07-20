from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.document_model import StatusEnum


class DocumentSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    object_key: str
    status: StatusEnum
    created_at: datetime
    processed_at: datetime
