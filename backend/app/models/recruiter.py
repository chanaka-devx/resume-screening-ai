from sqlalchemy import Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.enums.recruiter_role import RecruiterRole
from app.models.base_model import BaseModel


class Recruiter(BaseModel):
    __tablename__ = "recruiters"

    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String)
    company: Mapped[str] = mapped_column(String(255))
    role: Mapped[RecruiterRole] = mapped_column(
        Enum(RecruiterRole, native_enum=False, length=50),
        default=RecruiterRole.RECRUITER,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    job_postings: Mapped[list["JobPosting"]] = relationship(
        back_populates="recruiter",
        cascade="all, delete-orphan",
    )