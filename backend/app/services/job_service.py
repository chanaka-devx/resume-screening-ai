from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums.job_status import JobStatus
from app.models.job_posting import JobPosting
from app.models.recruiter import Recruiter
from app.repositories.job_repository import JobRepository
from app.schemas.job import JobCreateRequest, JobResponse


class JobService:
    """Business logic for job posting operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.repo = JobRepository(session)

    # ── helpers ──────────────────────────────────────────────────────────────

    def _to_response(self, job: JobPosting) -> JobResponse:
        return JobResponse(
            id=str(job.id),
            recruiter_id=str(job.recruiter_id),
            title=job.title,
            description=job.description,
            deadline=job.deadline,
            status=job.status,
            created_at=job.created_at.isoformat(),
            updated_at=job.updated_at.isoformat(),
        )

    async def _get_owned_job(self, job_id: str, recruiter: Recruiter) -> JobPosting:
        """
        Fetch a job by ID and verify the recruiter owns it.
        Raises 404 if not found, 403 if not the owner.
        """
        job = await self.repo.get_by_id(job_id)
        if job is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found.",
            )
        if job.recruiter_id != recruiter.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to modify this job.",
            )
        return job

    # ── create ───────────────────────────────────────────────────────────────

    async def create_job(self, data: JobCreateRequest, recruiter: Recruiter) -> JobResponse:
        """
        Create a new job posting for the authenticated recruiter.
        Recruiter ID comes from the JWT — never from the request body.
        Input validation is fully handled by Pydantic in JobCreateRequest.
        """
        job = JobPosting(
            recruiter_id=recruiter.id,
            title=data.title,
            description=data.description,
            deadline=data.deadline,
            status=JobStatus.DRAFT,
        )
        saved_job = await self.repo.create(job)
        return self._to_response(saved_job)

    # ── publish ───────────────────────────────────────────────────────────────

    async def publish_job(self, job_id: str, recruiter: Recruiter) -> JobResponse:
        """
        Transition a job from DRAFT → PUBLISHED.

        Raises:
            404 if the job does not exist.
            403 if the recruiter does not own the job.
            409 if the job is already PUBLISHED.
            409 if the job is CLOSED (cannot re-publish).
        """
        job = await self._get_owned_job(job_id, recruiter)

        if job.status == JobStatus.PUBLISHED:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Job is already published.",
            )
        if job.status == JobStatus.CLOSED:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A closed job cannot be published again.",
            )

        job.status = JobStatus.PUBLISHED
        updated_job = await self.repo.update(job)
        return self._to_response(updated_job)

    # ── close ─────────────────────────────────────────────────────────────────

    async def close_job(self, job_id: str, recruiter: Recruiter) -> JobResponse:
        """
        Transition a job from PUBLISHED → CLOSED.

        Raises:
            404 if the job does not exist.
            403 if the recruiter does not own the job.
            409 if the job is already CLOSED.
            409 if the job is still DRAFT (must be published first).
        """
        job = await self._get_owned_job(job_id, recruiter)

        if job.status == JobStatus.CLOSED:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Job is already closed.",
            )
        if job.status == JobStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A draft job must be published before it can be closed.",
            )

        job.status = JobStatus.CLOSED
        updated_job = await self.repo.update(job)
        return self._to_response(updated_job)
