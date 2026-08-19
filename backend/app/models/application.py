from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel


class Application(BaseModel):
    __tablename__ = "applications"

    job_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("job_postings.id", ondelete="CASCADE"),
        nullable=False,
    )

    resume_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(String(30), default="submitted")
    message: Mapped[str | None] = mapped_column(Text, nullable=True)

    job_posting: Mapped["JobPosting"] = relationship(
        back_populates="applications",
        foreign_keys=[job_id],
    )

    resume: Mapped["Resume"] = relationship(
        back_populates="applications",
    )

    evaluation: Mapped["Evaluation | None"] = relationship(
        back_populates="application",
        cascade="all, delete-orphan",
        uselist=False,
    )