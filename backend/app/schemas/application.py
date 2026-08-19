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
