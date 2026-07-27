from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.schemas.job import PublicJobListResponse
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
) -> PublicJobListResponse:
    """
    Browse all **published** job postings — open to anyone, no login required.

    **Filters**
    - `search` — case-insensitive substring match on title or description

    **Pagination**
    - `page`  — 1-based page number (default 1)
    - `limit` — results per page, max 100 (default 10)

    **Response fields** (applicant-safe — no internal recruiter data)
    - `id`, `title`, `description`, `deadline`, `posted_at`
    """
    return await JobService(session).list_public_jobs(
        page=page,
        limit=limit,
        search=search,
    )
