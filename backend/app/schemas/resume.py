from pydantic import BaseModel


# ── Applicant schemas ─────────────────────────────────────────────────────────

class ApplicantResponse(BaseModel):
    """Applicant record extracted from the uploaded resume."""

    id: str
    full_name: str
    email: str
    phone: str | None
    linkedin_url: str | None
    github_url: str | None
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


# ── Resume schemas ────────────────────────────────────────────────────────────

class ResumeResponse(BaseModel):
    """Full resume record returned after a successful upload."""

    id: str
    applicant_id: str
    file_name: str
    file_path: str
    parsed_text: str | None
    created_at: str
    updated_at: str
    deleted_at: str | None

    model_config = {"from_attributes": True}


class ResumeUploadResponse(BaseModel):
    """Combined response returned immediately after a resume upload.

    Contains both the newly created resume record and the applicant
    record that was either found (by email) or created from the PDF text.
    """

    applicant: ApplicantResponse
    resume: ResumeResponse


class ResumeListResponse(BaseModel):
    """List of resumes belonging to an applicant."""

    items: list[ResumeResponse]
    total: int
