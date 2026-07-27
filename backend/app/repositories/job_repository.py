from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job_posting import JobPosting


class JobRepository:
    """All database operations for the JobPosting table."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, job: JobPosting) -> JobPosting:
        """Persist a new JobPosting row and return the refreshed instance."""
        self.session.add(job)
        await self.session.commit()
        await self.session.refresh(job)
        return job

    async def get_by_id(self, job_id: str) -> JobPosting | None:
        """Return the job posting with the given UUID, or None."""
        result = await self.session.execute(
            select(JobPosting).where(JobPosting.id == job_id)
        )
        return result.scalar_one_or_none()

    async def update(self, job: JobPosting) -> JobPosting:
        """Persist changes to an existing JobPosting row and return the refreshed instance."""
        await self.session.flush()
        await self.session.commit()
        await self.session.refresh(job)
        return job
