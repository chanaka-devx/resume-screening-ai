from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.schemas.application import ApplicationResponse, ApplicationSubmitRequest
from app.services.application_service import ApplicationService

router = APIRouter(prefix="/applications", tags=["Applications"])


# ── POST /applications ────────────────────────────────────────────────────────
@router.post(
    "",
    response_model=ApplicationResponse,
    status_code=201,
    summary="Submit a job application",
)
async def submit_application(
    data: ApplicationSubmitRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> ApplicationResponse:
    
    return await ApplicationService(session).submit_application(data)
