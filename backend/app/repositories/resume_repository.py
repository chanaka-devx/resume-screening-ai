from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.resume import Resume


class ResumeRepository:
    """All database operations for the Resume table."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, resume: Resume) -> Resume:
        """Persist a new Resume row and return the refreshed instance."""
        self.session.add(resume)
        await self.session.commit()
        await self.session.refresh(resume)
        return resume

    async def get_by_id(self, resume_id: UUID) -> Resume | None:
        """Return the resume with the given UUID, or None."""
        result = await self.session.execute(
            select(Resume).where(Resume.id == resume_id)
        )
        return result.scalar_one_or_none()

    async def get_by_applicant(self, applicant_id: UUID) -> list[Resume]:
        """Return all non-deleted resumes belonging to an applicant."""
        result = await self.session.execute(
            select(Resume)
            .where(
                Resume.applicant_id == applicant_id,
                Resume.deleted_at.is_(None),
            )
            .order_by(Resume.created_at.desc())
        )
        return list(result.scalars().all())
