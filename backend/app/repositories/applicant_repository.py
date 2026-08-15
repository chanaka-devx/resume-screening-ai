from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.applicant import Applicant


class ApplicantRepository:
    """All database operations for the Applicant table."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_email(self, email: str) -> Applicant | None:
        """Return the applicant with the given email, or None."""
        result = await self.session.execute(
            select(Applicant).where(Applicant.email == email)
        )
        return result.scalar_one_or_none()

    async def create(self, applicant: Applicant) -> Applicant:
        """Persist a new Applicant row and return the refreshed instance."""
        self.session.add(applicant)
        await self.session.commit()
        await self.session.refresh(applicant)
        return applicant
