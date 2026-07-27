from datetime import date
from uuid import UUID

from sqlalchemy import Date, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.enums.job_location import JobLocation
from app.enums.job_status import JobStatus
from app.models.base_model import BaseModel


class JobPosting(BaseModel):
    __tablename__ = "job_postings"

    recruiter_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("recruiters.id", ondelete="CASCADE"),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    deadline: Mapped[date | None] = mapped_column(Date, nullable=True)
    location: Mapped[JobLocation | None] = mapped_column(
        Enum(JobLocation, native_enum=False, length=20),
        nullable=True,
    )
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, native_enum=False, length=30),
        default=JobStatus.DRAFT,
    )

    recruiter: Mapped["Recruiter"] = relationship(
        back_populates="job_postings",
    )

    applications: Mapped[list["Application"]] = relationship(
        back_populates="job_posting",
        cascade="all, delete-orphan",
    )