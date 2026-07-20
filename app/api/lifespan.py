from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.db.base import Base
from app.db.session import engine


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as coon:
        await coon.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()