import uuid

from pydantic import BaseModel

from app.enums.application_status import ApplicationStatus


# ── Request schemas ───────────────────────────────────────────────────────────

class ApplicationSubmitRequest(BaseModel):
    """Payload required to submit a job application."""

    job_id: uuid.UUID
    resume_id: uuid.UUID
    message: str | None = None


# ── Response schemas ──────────────────────────────────────────────────────────

class ApplicationResponse(BaseModel):
    """Full application record returned after a successful submission."""

    id: str
    job_id: str
    resume_id: str
    message: str | None = None
    status: ApplicationStatus = ApplicationStatus.SUBMITTED
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


class CandidateInfo(BaseModel):
    """Candidate details associated with an application."""

    id: str
    full_name: str
    email: str
    phone: str | None = None
    linkedin_url: str | None = None
    github_url: str | None = None

    model_config = {"from_attributes": True}


class ApplicationResumeInfo(BaseModel):
    """Resume details associated with an application."""

    id: str
    file_name: str
    file_path: str

    model_config = {"from_attributes": True}


class JobApplicationItemResponse(BaseModel):
    """Application item returned within a job's application list."""

    id: str
    job_id: str
    resume_id: str
    message: str | None = None
    status: ApplicationStatus
    created_at: str
    updated_at: str
    candidate: CandidateInfo
    resume: ApplicationResumeInfo

    model_config = {"from_attributes": True}


class JobApplicationListResponse(BaseModel):
    """Paginated list of applications for a job posting."""

    items: list[JobApplicationItemResponse]
    total: int
    page: int
    limit: int
    total_pages: int

