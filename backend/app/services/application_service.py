from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums.application_status import ApplicationStatus
from app.enums.job_status import JobStatus
from app.models.application import Application
from app.repositories.application_repository import ApplicationRepository
from app.repositories.job_repository import JobRepository
from app.repositories.resume_repository import ResumeRepository
from app.schemas.application import ApplicationResponse, ApplicationSubmitRequest


class ApplicationService:
    """Business logic for job application operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.app_repo = ApplicationRepository(session)
        self.job_repo = JobRepository(session)
        self.resume_repo = ResumeRepository(session)

    # ── helpers ───────────────────────────────────────────────────────────────

    def _to_response(self, application: Application) -> ApplicationResponse:
        return ApplicationResponse(
            id=str(application.id),
            job_id=str(application.job_id),
            resume_id=str(application.resume_id),
            message=application.message,
            status=application.status,
            created_at=application.created_at.isoformat(),
            updated_at=application.updated_at.isoformat(),
        )

    # ── submit ────────────────────────────────────────────────────────────────

    async def submit_application(
        self, data: ApplicationSubmitRequest
    ) -> ApplicationResponse:
        """
        Submit a job application linking a resume to a job posting.

        Validations:
          - Job must exist and be PUBLISHED.
          - Resume must exist and not be soft-deleted.
          - The same resume cannot be submitted to the same job twice.

        Raises:
            404 if the job or resume does not exist.
            409 if the job is not accepting applications (not PUBLISHED).
            409 if an application with the same job + resume already exists.
        """
        # 1. Validate job exists and is published
        job = await self.job_repo.get_by_id(str(data.job_id))
        if job is None or job.status == JobStatus.DELETED:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found.",
            )
        if job.status != JobStatus.PUBLISHED:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This job is not currently accepting applications.",
            )

        # 2. Validate resume exists and is not deleted
        resume = await self.resume_repo.get_by_id(data.resume_id)
        if resume is None or resume.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found.",
            )

        # 3. Prevent duplicate submissions
        existing = await self.app_repo.get_by_job_and_resume(
            job_id=data.job_id,
            resume_id=data.resume_id,
        )
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An application for this job with the same resume already exists.",
            )

        # 4. Create application
        application = Application(
            job_id=data.job_id,
            resume_id=data.resume_id,
            message=data.message,
            status=ApplicationStatus.SUBMITTED,
        )
        saved = await self.app_repo.create(application)
        return self._to_response(saved)
