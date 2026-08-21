from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.enums.application_status import ApplicationStatus
from app.models.application import Application
from app.models.resume import Resume


class ApplicationRepository:
    """All database operations for the Application table."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, application: Application) -> Application:
        """Persist a new Application row and return the refreshed instance."""
        self.session.add(application)
        await self.session.commit()
        await self.session.refresh(application)
        return application

    async def get_by_id(self, application_id: UUID) -> Application | None:
        """Return the application with the given UUID, or None."""
        result = await self.session.execute(
            select(Application).where(Application.id == application_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id_with_relations(
        self, application_id: UUID
    ) -> Application | None:
        """
        Return the application with job_posting and resume eagerly loaded.
        """
        result = await self.session.execute(
            select(Application)
            .options(
                selectinload(Application.job_posting),
                selectinload(Application.resume),
            )
            .where(Application.id == application_id)
        )
        return result.scalar_one_or_none()


    async def get_by_job_and_resume(
        self, job_id: UUID, resume_id: UUID
    ) -> Application | None:
        """
        Return an existing application for the given job + resume combination.
        Used to prevent duplicate submissions.
        """
        result = await self.session.execute(
            select(Application).where(
                Application.job_id == job_id,
                Application.resume_id == resume_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_applications_by_job(
        self,
        job_id: UUID,
        skip: int = 0,
        limit: int = 10,
        status: ApplicationStatus | None = None,
    ) -> tuple[list[Application], int]:
        """
        Return a paginated list of applications for a specific job posting,
        with resume and applicant eagerly loaded.

        Returns:
            (items, total)
        """
        base_filter = [Application.job_id == job_id]

        if status is not None:
            status_value = status.value if hasattr(status, "value") else str(status)
            base_filter.append(Application.status == status_value)

        # Count query
        count_result = await self.session.execute(
            select(func.count()).select_from(Application).where(*base_filter)
        )
        total = count_result.scalar_one()

        # Paginated rows
        rows_result = await self.session.execute(
            select(Application)
            .options(
                selectinload(Application.resume).selectinload(Resume.applicant)
            )
            .where(*base_filter)
            .order_by(Application.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        items = list(rows_result.scalars().all())

        return items, total

