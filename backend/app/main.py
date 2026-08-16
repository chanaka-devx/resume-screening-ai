from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.api.routes.auth import router as auth_router
from app.api.routes.job import router as job_router
from app.api.routes.public import router as public_router
from app.api.routes.resume import router as resume_router
from app.api.routes.application import router as application_router
from app.core.config import settings
from app.db.session import AsyncSessionLocal


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncSessionLocal() as session:
        await session.execute(text("SELECT 1"))
        print("Database connected successfully!")
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth_router, prefix="/api/v1")
app.include_router(job_router, prefix="/api/v1")
app.include_router(public_router, prefix="/api/v1")
app.include_router(resume_router, prefix="/api/v1")
app.include_router(application_router, prefix="/api/v1")


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}

