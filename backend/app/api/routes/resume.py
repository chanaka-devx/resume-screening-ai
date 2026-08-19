import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.schemas.resume import (
    ApplicantResponse,
    ApplicantUpdateRequest,
    ResumeUploadResponse,
)
from app.services.resume_service import ResumeService

router = APIRouter(prefix="/resumes", tags=["Resumes"])


# ── POST /resumes/upload ──────────────────────────────────────────────────────
@router.post(
    "/upload",
    response_model=ResumeUploadResponse,
    status_code=201,
    summary="Upload a resume PDF",
)
async def upload_resume(
    session: Annotated[AsyncSession, Depends(get_db)],
    file: UploadFile = File(..., description="PDF resume file (max 5 MB)"),
) -> ResumeUploadResponse:
    """
    Upload a resume PDF. No prior sign-up required.

    The server will automatically:
    1. Extract text from the PDF.
    2. Parse the applicant's details (name, email, phone, LinkedIn, GitHub).
    3. Create an applicant record, or reuse the existing one if the email is already known.
    4. Store the PDF in Cloudflare R2 object storage.
    5. Save the resume metadata to the database.

    **Returns** the created applicant record and resume record.

    **Errors**
    - `400` — not a PDF, exceeds 5 MB, unreadable PDF, or no email found in text.
    - `502` — R2 storage upload failed.
    """
    return await ResumeService(session).upload_resume(file=file)


# ── PATCH /resumes/applicant/{applicant_id} ──────────────────────────────────
@router.patch(
    "/applicant/{applicant_id}",
    response_model=ApplicantResponse,
    status_code=200,
    summary="Update applicant details",
)
async def update_applicant(
    applicant_id: uuid.UUID,
    data: ApplicantUpdateRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> ApplicantResponse:
    """Update applicant information (e.g. when user submits with manual corrections)."""
    return await ResumeService(session).update_applicant(applicant_id, data)

