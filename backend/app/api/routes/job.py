from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_recruiter
from app.dependencies.database import get_db
from app.models.recruiter import Recruiter
from app.schemas.job import JobCreateRequest, JobResponse
from app.services.job_service import JobService

router = APIRouter(prefix="/jobs", tags=["Jobs"])


# ── POST /jobs ───────────────────────────────────────────────────────────────
@router.post(
    "",
    response_model=JobResponse,
    status_code=201,
    summary="Create a new job posting",
)
async def create_job(
    data: JobCreateRequest,
    current_recruiter: Annotated[Recruiter, Depends(get_current_recruiter)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> JobResponse:
    """
    Create a new job posting for the authenticated recruiter.
    
    The recruiter ID is automatically extracted from the JWT token.
    The job is created with 'draft' status by default.
    """
    return await JobService(session).create_job(data, current_recruiter)
