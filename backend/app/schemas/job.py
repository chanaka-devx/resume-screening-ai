from datetime import date
from pydantic import BaseModel, Field, field_validator

from app.enums.job_status import JobStatus


class JobCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    deadline: date | None = None

    @field_validator("deadline")
    @classmethod
    def validate_deadline(cls, v: date | None) -> date | None:
        if v is not None and v < date.today():
            raise ValueError("deadline must be a future date")
        return v


class JobResponse(BaseModel):
    id: str
    recruiter_id: str
    title: str
    description: str
    deadline: date | None
    status: JobStatus
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


class JobListResponse(BaseModel):
    """Paginated list of job postings."""

    items: list[JobResponse]
    total: int
    page: int
    limit: int
    total_pages: int
