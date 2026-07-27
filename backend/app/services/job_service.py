from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job_posting import JobPosting
from app.models.recruiter import Recruiter
from app.repositories.job_repository import JobRepository
from app.schemas.job import JobCreateRequest, JobResponse


class JobService:
    """Business logic for job posting creation."""

    def __init__(self, session: AsyncSession) -> None:
        self.repo = JobRepository(session)

    async def create_job(self, data: JobCreateRequest, recruiter: Recruiter) -> JobResponse:
        """
        Create a new job posting for the authenticated recruiter.
        The recruiter ID is extracted from the JWT token, not from the request.
        Input validation is fully handled by Pydantic in JobCreateRequest.
        """
        # Create JobPosting model with recruiter_id from authenticated user
        job = JobPosting(
            recruiter_id=recruiter.id,
            title=data.title,
            description=data.description,
            deadline=data.deadline,
            status="draft",
        )
        
        # Save via repository
        saved_job = await self.repo.create(job)
        
        # Return JobResponse
        return JobResponse(
            id=str(saved_job.id),
            recruiter_id=str(saved_job.recruiter_id),
            title=saved_job.title,
            description=saved_job.description,
            deadline=saved_job.deadline,
            status=saved_job.status,
            created_at=saved_job.created_at.isoformat(),
            updated_at=saved_job.updated_at.isoformat(),
        )
