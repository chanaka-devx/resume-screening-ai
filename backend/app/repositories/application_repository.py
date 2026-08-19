from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.application import Application


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
