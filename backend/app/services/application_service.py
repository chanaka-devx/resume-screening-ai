import math
from uuid import UUID

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.enums.application_status import ApplicationStatus
from app.enums.job_status import JobStatus
from app.models.application import Application
from app.models.recruiter import Recruiter
from app.repositories.application_repository import ApplicationRepository
from app.repositories.job_repository import JobRepository
from app.repositories.resume_repository import ResumeRepository
from app.schemas.application import (
    ApplicationResponse,
    ApplicationResumeInfo,
    ApplicationSubmitRequest,
    CandidateInfo,
    JobApplicationItemResponse,
    JobApplicationListResponse,
)


def _get_r2_client():
    """Return a boto3 S3 client configured for Cloudflare R2."""
    return boto3.client(
        "s3",
        endpoint_url=settings.R2_ENDPOINT,
        aws_access_key_id=settings.R2_ACCESS_KEY_ID,
        aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
        config=Config(signature_version="s3v4"),
        region_name="auto",
    )


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
            status=ApplicationStatus(application.status),
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
            status=ApplicationStatus.SUBMITTED.value,
        )
        saved = await self.app_repo.create(application)
        return self._to_response(saved)

    # ── list by job ───────────────────────────────────────────────────────────

    async def get_job_applications(
        self,
        job_id: str,
        recruiter: Recruiter,
        page: int = 1,
        limit: int = 10,
        status_filter: ApplicationStatus | None = None,
    ) -> JobApplicationListResponse:
        """
        Retrieve a paginated list of applications for a specific job posting.

        Validations:
          - Job must exist and not be DELETED.
          - Recruiter must own the job.

        Raises:
            404 if the job does not exist or is not owned by the recruiter.
        """
        try:
            job_uuid = UUID(job_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found.",
            )

        # 1. Verify job exists and recruiter owns it
        job = await self.job_repo.get_by_id(str(job_uuid))
        if (
            job is None
            or job.status == JobStatus.DELETED
            or job.recruiter_id != recruiter.id
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found.",
            )

        # 2. Fetch paginated applications
        skip = (page - 1) * limit
        applications, total = await self.app_repo.get_applications_by_job(
            job_id=job_uuid,
            skip=skip,
            limit=limit,
            status=status_filter,
        )

        # 3. Map to response schema
        items: list[JobApplicationItemResponse] = []
        for app in applications:
            applicant = (
                app.resume.applicant
                if app.resume and app.resume.applicant
                else None
            )
            resume = app.resume

            candidate_info = CandidateInfo(
                id=str(applicant.id) if applicant else "",
                full_name=applicant.full_name if applicant else "Unknown",
                email=applicant.email if applicant else "",
                phone=applicant.phone if applicant else None,
                linkedin_url=applicant.linkedin_url if applicant else None,
                github_url=applicant.github_url if applicant else None,
            )

            resume_info = ApplicationResumeInfo(
                id=str(resume.id) if resume else str(app.resume_id),
                file_name=resume.file_name if resume else "",
                file_path=resume.file_path if resume else "",
            )

            items.append(
                JobApplicationItemResponse(
                    id=str(app.id),
                    job_id=str(app.job_id),
                    resume_id=str(app.resume_id),
                    message=app.message,
                    status=ApplicationStatus(app.status),
                    created_at=app.created_at.isoformat(),
                    updated_at=app.updated_at.isoformat(),
                    candidate=candidate_info,
                    resume=resume_info,
                )
            )

        total_pages = math.ceil(total / limit) if total > 0 else 0

        return JobApplicationListResponse(
            items=items,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
        )

    # ── download resume ───────────────────────────────────────────────────────

    async def download_resume(
        self,
        application_id: str,
        recruiter: Recruiter,
    ) -> tuple[bytes, str]:
        """
        Download the resume PDF attached to an application.

        Validations:
          - Application must exist.
          - The associated Job must exist and not be DELETED.
          - Recruiter must own the job.
          - Resume must exist and not be soft-deleted.
          - File must exist in Cloudflare R2.

        Raises:
            404 if application, job, or resume is not found / not owned / missing file.
            502 if storage download fails.
        """
        try:
            app_uuid = UUID(application_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found.",
            )

        # 1. Fetch application with related job and resume
        application = await self.app_repo.get_by_id_with_relations(app_uuid)
        if application is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found.",
            )

        # 2. Verify job exists and recruiter owns it
        job = application.job_posting
        if (
            job is None
            or job.status == JobStatus.DELETED
            or job.recruiter_id != recruiter.id
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found.",
            )

        # 3. Verify resume exists and is not soft-deleted
        resume = application.resume
        if resume is None or resume.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found.",
            )

        # 4. Extract R2 object key
        if "resumes/" in resume.file_path:
            object_key = "resumes/" + resume.file_path.split("resumes/", 1)[1]
        else:
            object_key = resume.file_path

        # 5. Fetch file bytes from R2
        try:
            r2 = _get_r2_client()
            response = r2.get_object(
                Bucket=settings.R2_BUCKET_NAME,
                Key=object_key,
            )
            file_bytes: bytes = response["Body"].read()
        except ClientError as exc:
            error_code = exc.response.get("Error", {}).get("Code", "")
            if error_code in ("NoSuchKey", "404", "NoSuchBucket"):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Resume file not found in storage.",
                )
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to retrieve resume from storage: {exc}",
            )
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to retrieve resume from storage: {exc}",
            )

        filename = resume.file_name or f"resume_{application.id}.pdf"
        return file_bytes, filename


