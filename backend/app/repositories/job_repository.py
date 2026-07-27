from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums.job_location import JobLocation
from app.enums.job_status import JobStatus
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

    async def get_jobs_by_recruiter(
        self,
        recruiter_id: UUID,
        skip: int = 0,
        limit: int = 10,
        status: JobStatus | None = None,
        location: JobLocation | None = None,
        search: str | None = None,
    ) -> tuple[list[JobPosting], int]:
        """
        Return a page of job postings owned by the recruiter.

        Filters:
          - status:   exact match on JobStatus value
          - location: exact match on JobLocation value
          - search:   case-insensitive substring match on title or description

        Returns:
          (items, total) where total is the unfiltered count for pagination math.
        """
        base_filter = [JobPosting.recruiter_id == recruiter_id]

        if status is not None:
            base_filter.append(JobPosting.status == status)

        if location is not None:
            base_filter.append(JobPosting.location == location)

        if search:
            term = f"%{search.strip()}%"
            base_filter.append(
                or_(
                    JobPosting.title.ilike(term),
                    JobPosting.description.ilike(term),
                )
            )

        # Total count (respects filters)
        count_result = await self.session.execute(
            select(func.count()).select_from(JobPosting).where(*base_filter)
        )
        total = count_result.scalar_one()

        # Paginated rows, newest first
        rows_result = await self.session.execute(
            select(JobPosting)
            .where(*base_filter)
            .order_by(JobPosting.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        items = list(rows_result.scalars().all())

        return items, total

    async def get_published_jobs(
        self,
        skip: int = 0,
        limit: int = 10,
        search: str | None = None,
        location: JobLocation | None = None,
    ) -> tuple[list[JobPosting], int]:
        """
        Return a page of PUBLISHED job postings (public, no auth required).

        Filters:
          - status is always PUBLISHED (hard-coded — not caller-controlled)
          - search:   case-insensitive substring match on title or description
          - location: exact match on JobLocation value

        Returns:
          (items, total) where total respects the active filters.
        """
        base_filter = [JobPosting.status == JobStatus.PUBLISHED]

        if search:
            term = f"%{search.strip()}%"
            base_filter.append(
                or_(
                    JobPosting.title.ilike(term),
                    JobPosting.description.ilike(term),
                )
            )

        if location is not None:
            base_filter.append(JobPosting.location == location)

        count_result = await self.session.execute(
            select(func.count()).select_from(JobPosting).where(*base_filter)
        )
        total = count_result.scalar_one()

        rows_result = await self.session.execute(
            select(JobPosting)
            .where(*base_filter)
            .order_by(JobPosting.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        items = list(rows_result.scalars().all())

        return items, total
