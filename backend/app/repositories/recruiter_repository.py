from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.recruiter import Recruiter


class RecruiterRepository:
    """All database operations for the Recruiter table."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_email(self, email: str) -> Recruiter | None:
        """Return the recruiter with the given email, or None."""
        result = await self.session.execute(
            select(Recruiter).where(Recruiter.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, recruiter_id: str) -> Recruiter | None:
        """Return the recruiter with the given UUID, or None."""
        result = await self.session.execute(
            select(Recruiter).where(Recruiter.id == recruiter_id)
        )
        return result.scalar_one_or_none()

    async def create(self, recruiter: Recruiter) -> Recruiter:
        """Persist a new Recruiter row and return the refreshed instance."""
        self.session.add(recruiter)
        await self.session.commit()
        await self.session.refresh(recruiter)
        return recruiter

    async def email_exists(self, email: str) -> bool:
        """Return True if a recruiter with this email already exists."""
        return await self.get_by_email(email) is not None
