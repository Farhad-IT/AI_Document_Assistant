from sqlalchemy import select, create_engine
from sqlalchemy.orm import sessionmaker

from app.celery_app import celery_app
from app.core.log import logger
from app.core.config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
from app.documents.minio_service import MinioService
from app.minio_client import client
from app.models import DocumentModel, StatusEnum, DocumentChunksModel
import os

from app.processing.document_processing import extract_and_chunk

SYNC_DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

sync_engine = create_engine(SYNC_DATABASE_URL, pool_pre_ping=True)
SyncSessionLocal = sessionmaker(bind=sync_engine, autocommit=False)
MinioService = MinioService(minio_client=client)

@celery_app.task(name="process_document", bind=True, max_retries=3, cooldown=3)
def document_handler(self, user_id: int, object_key: str) -> None:
    logger.info(f"[document {object_key}] Начата обработка")

    db = SyncSessionLocal()
    document = None
    local_path = None

    try:
        document = select(DocumentModel).filter_by(user_id=user_id, object_key=object_key)

        if document is None:
            logger.error(f"[document {object_key}] Документ не найден в БД")
            return

        res = db.execute(document)
        document = res.scalar_one_or_none()

        safe_filename = os.path.basename(str(document.filename))  # убирает любые пути, оставляет только имя файла
        local_path = f"/tmp/{document.id}_{safe_filename}"

        MinioService.get_file_stream(object_key=object_key, filepath=local_path)

        chunks = extract_and_chunk(file_path=local_path)

        for i, chunk in enumerate(chunks):
            db_chunk = DocumentChunksModel(
                document_id=document.id,
                index=i,
                text=chunk["text"],
                page=chunk["page"],
            )
            db.add(db_chunk)

        document.status = StatusEnum.READY

        db.commit()

        logger.info(f"[document {object_key}] Статус изменён на READY")

    except Exception as e:
        db.rollback()
        logger.exception(f"[document {object_key}] Ошибка обработки: {e}")

        try:
            raise self.retry(exc=e, countdown=10 * (self.request.retries + 1))
        except self.MaxRetriesExceededError:
            logger.error(f"[document {document.id}] Превышено число попыток, помечаем FAILED")
            document.status = StatusEnum.FAILED
            db.commit()

    finally:
        db.close()
        if os.path.exists(local_path):
            os.remove(local_path)
