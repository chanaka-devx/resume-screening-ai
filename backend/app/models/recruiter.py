from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel


class Recruiter(BaseModel):
    __tablename__ = "recruiters"

    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String)
    company: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(50), default="recruiter")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    job_postings: Mapped[list["JobPosting"]] = relationship(
        back_populates="recruiter",
        cascade="all, delete-orphan",
    )