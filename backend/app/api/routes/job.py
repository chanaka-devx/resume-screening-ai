from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_recruiter
from app.dependencies.database import get_db
from app.enums.job_location import JobLocation
from app.enums.job_status import JobStatus
from app.models.recruiter import Recruiter
from app.schemas.job import (
    JobCreateRequest,
    JobListResponse,
    JobResponse,
    JobUpdateRequest,
)
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
    The job is created with **draft** status by default.
    """
    return await JobService(session).create_job(data, current_recruiter)


# ── GET /jobs ─────────────────────────────────────────────────────────
@router.get(
    "",
    response_model=JobListResponse,
    status_code=200,
    summary="List jobs for the authenticated recruiter (RS-018)",
)
async def list_jobs(
    current_recruiter: Annotated[Recruiter, Depends(get_current_recruiter)],
    session: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(default=1, ge=1, description="Page number (1-based)"),
    limit: int = Query(default=10, ge=1, le=100, description="Items per page (max 100)"),
    status: JobStatus | None = Query(default=None, description="Filter by job status"),
    location: JobLocation | None = Query(default=None, description="Filter by location type"),
    search: str | None = Query(default=None, min_length=1, max_length=100, description="Search in title and description"),
) -> JobListResponse:
    """
    Return a paginated list of **your own** job postings.

    **Filters**
    - `status`   — one of `draft`, `published`, `closed`
    - `location` — one of `on-site`, `hybrid`, `remote`
    - `search`   — case-insensitive substring match on title or description

    **Pagination**
    - `page`  — 1-based page number (default 1)
    - `limit` — results per page, max 100 (default 10)
    """
    return await JobService(session).list_recruiter_jobs(
        recruiter=current_recruiter,
        page=page,
        limit=limit,
        status_filter=status,
        location_filter=location,
        search=search,
    )

# ── GET /jobs/{job_id} ───────────────────────────────────────────────────────
@router.get(
    "/{job_id}",
    response_model=JobResponse,
    status_code=200,
    summary="Get a single job posting",
)
async def get_job(
    job_id: str,
    current_recruiter: Annotated[Recruiter, Depends(get_current_recruiter)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> JobResponse:
    """
    Retrieve one of your job postings.
    
    - Returns **404** if the job does not exist or you do not own it.
    """
    return await JobService(session).get_job(job_id, current_recruiter)


# ── PUT /jobs/{job_id} ───────────────────────────────────────────────────────
@router.put(
    "/{job_id}",
    response_model=JobResponse,
    status_code=200,
    summary="Update a draft or published job",
)
async def update_job(
    job_id: str,
    data: JobUpdateRequest,
    current_recruiter: Annotated[Recruiter, Depends(get_current_recruiter)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> JobResponse:
    """
    Update a job posting.
    
    - Jobs in **DRAFT** or **PUBLISHED** status can be updated.
    - All fields are optional. Only send the fields you wish to update.
    - Returns **409 Conflict** if the job is closed.
    """
    return await JobService(session).update_job(job_id, data, current_recruiter)


# ── PATCH /jobs/{job_id}/publish ─────────────────────────────────────────────
@router.patch(
    "/{job_id}/publish",
    response_model=JobResponse,
    status_code=200,
    summary="Publish a draft job",
)
async def publish_job(
    job_id: str,
    current_recruiter: Annotated[Recruiter, Depends(get_current_recruiter)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> JobResponse:
    """
    Transition a job from **draft → published**.

    - The job must exist and be owned by the authenticated recruiter.
    - Returns **409 Conflict** if the job is already published or closed.
    """
    return await JobService(session).publish_job(job_id, current_recruiter)


# ── PATCH /jobs/{job_id}/close ───────────────────────────────────────────────
@router.patch(
    "/{job_id}/close",
    response_model=JobResponse,
    status_code=200,
    summary="Close a published job",
)
async def close_job(
    job_id: str,
    current_recruiter: Annotated[Recruiter, Depends(get_current_recruiter)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> JobResponse:
    """
    Transition a job from **published → closed**.

    - The job must exist and be owned by the authenticated recruiter.
    - Returns **409 Conflict** if the job is already closed or still a draft.
    """
    return await JobService(session).close_job(job_id, current_recruiter)


# ── DELETE /jobs/{job_id} ────────────────────────────────────────────────────
@router.delete(
    "/{job_id}",
    response_model=JobResponse,
    status_code=200,
    summary="Soft delete a job posting",
)
async def delete_job(
    job_id: str,
    current_recruiter: Annotated[Recruiter, Depends(get_current_recruiter)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> JobResponse:
    """
    Soft delete a job posting.
    
    - The job must exist and be owned by the authenticated recruiter.
    - Changes the status to **DELETED**.
    - Deleted jobs are no longer visible via the list or detail APIs.
    """
    return await JobService(session).delete_job(job_id, current_recruiter)
