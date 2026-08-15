from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.enums.job_location import JobLocation
from app.schemas.job import PublicJobListResponse, PublicJobResponse
from app.services.job_service import JobService

router = APIRouter(prefix="/public", tags=["Public"])


# ── GET /public/jobs ──────────────────────────────────────────────────────────
@router.get(
    "/jobs",
    response_model=PublicJobListResponse,
    status_code=200,
    summary="Browse published job postings (no auth required)",
)
async def list_public_jobs(
    session: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(default=1, ge=1, description="Page number (1-based)"),
    limit: int = Query(default=10, ge=1, le=100, description="Items per page (max 100)"),
    search: str | None = Query(
        default=None,
        min_length=1,
        max_length=100,
        description="Search in job title and description",
    ),
    location: JobLocation | None = Query(default=None, description="Filter by location type"),
) -> PublicJobListResponse:
    """
    Browse all **published** job postings — open to anyone, no login required.

    **Filters**
    - `search`   — case-insensitive substring match on title or description
    - `location` — one of `on-site`, `hybrid`, `remote`

    **Pagination**
    - `page`  — 1-based page number (default 1)
    - `limit` — results per page, max 100 (default 10)

    **Response fields** (applicant-safe — no internal recruiter data)
    - `id`, `title`, `description`, `location`, `deadline`, `posted_at`
    """
    return await JobService(session).list_public_jobs(
        page=page,
        limit=limit,
        search=search,
        location=location,
    )


# ── GET /public/jobs/{job_id} ─────────────────────────────────────────────
@router.get(
    "/jobs/{job_id}",
    response_model=PublicJobResponse,
    status_code=200,
    summary="Get a single published job posting (no auth required)",
)
async def get_public_job(
    job_id: str,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> PublicJobResponse:
    """
    Retrieve a single **published** job posting by its ID.

    Returns **404** if the job does not exist or is not published.
    Draft and closed jobs are intentionally hidden from public view.
    """
    return await JobService(session).get_public_job(job_id)
