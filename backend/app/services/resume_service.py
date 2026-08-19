import io
import re
import uuid

import boto3
import pdfplumber
from botocore.config import Config
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.applicant import Applicant
from app.models.resume import Resume
from app.repositories.applicant_repository import ApplicantRepository
from app.repositories.resume_repository import ResumeRepository
from app.schemas.resume import (
    ApplicantResponse,
    ApplicantUpdateRequest,
    ResumeResponse,
    ResumeUploadResponse,
)

# ── Constants ─────────────────────────────────────────────────────────────────

_ALLOWED_CONTENT_TYPES = {"application/pdf"}
_MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB

# Regex patterns for extracting applicant details from resume text
_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
_PHONE_RE = re.compile(
    r"(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?)?\d{3,4}[\s.-]?\d{4}"
)
_LINKEDIN_RE = re.compile(r"(?:https?://)?(?:www\.)?linkedin\.com/in/[\w\-]+", re.I)
_GITHUB_RE = re.compile(r"(?:https?://)?(?:www\.)?github\.com/[\w\-]+", re.I)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_r2_client():
    """Return a boto3 S3 client configured for Cloudflare R2."""
    return boto3.client(
        "s3",
        endpoint_url=settings.R2_ENDPOINT,
        aws_access_key_id=settings.R2_ACCESS_KEY_ID,
        aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
        config=Config(signature_version="s3v4"),
        region_name="auto",
    )


def _extract_text_from_pdf(file_bytes: bytes) -> str | None:
    """Extract plain text from a PDF using pdfplumber. Returns None on failure."""
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
        text = "\n".join(pages).strip()
        return text if text else None
    except Exception:
        return None


def _parse_applicant_details(text: str) -> dict:
    """
    Extract applicant fields from raw resume text using regex.

    Returns a dict with keys: full_name, email, phone, linkedin_url, github_url.
    Only email is guaranteed; all others may be None.
    """
    email_match = _EMAIL_RE.search(text)
    phone_match = _PHONE_RE.search(text)
    linkedin_match = _LINKEDIN_RE.search(text)
    github_match = _GITHUB_RE.search(text)

    # Best-effort name: first non-empty, non-URL, non-email line
    full_name: str | None = None
    for line in text.splitlines():
        line = line.strip()
        if line and "@" not in line and "http" not in line.lower() and len(line) < 80:
            full_name = line
            break

    return {
        "full_name": full_name or "Unknown",
        "email": email_match.group(0) if email_match else None,
        "phone": phone_match.group(0) if phone_match else None,
        "linkedin_url": linkedin_match.group(0) if linkedin_match else None,
        "github_url": github_match.group(0) if github_match else None,
    }


# ── Service ───────────────────────────────────────────────────────────────────

class ResumeService:
    """Business logic for resume operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.applicant_repo = ApplicantRepository(session)
        self.resume_repo = ResumeRepository(session)

    # ── helpers ───────────────────────────────────────────────────────────────

    def _to_applicant_response(self, applicant: Applicant) -> ApplicantResponse:
        return ApplicantResponse(
            id=str(applicant.id),
            full_name=applicant.full_name,
            email=applicant.email,
            phone=applicant.phone,
            linkedin_url=applicant.linkedin_url,
            github_url=applicant.github_url,
            created_at=applicant.created_at.isoformat(),
            updated_at=applicant.updated_at.isoformat(),
        )

    def _to_resume_response(self, resume: Resume) -> ResumeResponse:
        return ResumeResponse(
            id=str(resume.id),
            applicant_id=str(resume.applicant_id),
            file_name=resume.file_name,
            file_path=resume.file_path,
            parsed_text=resume.parsed_text,
            created_at=resume.created_at.isoformat(),
            updated_at=resume.updated_at.isoformat(),
            deleted_at=resume.deleted_at.isoformat() if resume.deleted_at else None,
        )

    # ── upload ────────────────────────────────────────────────────────────────

    async def upload_resume(self, file: UploadFile) -> ResumeUploadResponse:
        """
        Upload a resume PDF, extract applicant details, and persist everything.

        Steps:
          1. Validate file type and size.
          2. Extract text from the PDF with pdfplumber.
          3. Parse applicant fields (name, email, phone, LinkedIn, GitHub) from text.
          4. Find existing applicant by email, or create a new one.
          5. Upload the PDF bytes to Cloudflare R2.
          6. Save resume metadata to the database.
          7. Return the combined ApplicantResponse + ResumeResponse.

        Raises:
            400 if not a PDF, exceeds 5 MB, or no email could be extracted.
            502 if the R2 upload fails.
        """
        # 1. Validate MIME type
        if file.content_type not in _ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are accepted.",
            )

        # 2. Read bytes and check size
        file_bytes = await file.read()
        if len(file_bytes) > _MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size must not exceed 5 MB.",
            )

        # 3. Extract text from PDF
        parsed_text = _extract_text_from_pdf(file_bytes)
        if not parsed_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract text from the PDF. Please upload a text-based PDF.",
            )

        # 4. Parse applicant details
        details = _parse_applicant_details(parsed_text)
        if not details["email"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No email address found in the resume. Please ensure the PDF contains a valid email.",
            )

        # 5. Find or create applicant (keyed by email)
        applicant = await self.applicant_repo.get_by_email(details["email"])
        if applicant is None:
            applicant = Applicant(
                full_name=details["full_name"],
                email=details["email"],
                phone=details["phone"],
                linkedin_url=details["linkedin_url"],
                github_url=details["github_url"],
            )
            applicant = await self.applicant_repo.create(applicant)

        # 6. Upload to Cloudflare R2
        safe_filename = file.filename or "resume.pdf"
        object_key = f"resumes/{applicant.id}/{uuid.uuid4().hex}_{safe_filename}"

        try:
            r2 = _get_r2_client()
            r2.put_object(
                Bucket=settings.R2_BUCKET_NAME,
                Key=object_key,
                Body=file_bytes,
                ContentType="application/pdf",
            )
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to upload file to storage: {exc}",
            )

        file_path = f"{settings.R2_PUBLIC_URL.rstrip('/')}/{object_key}"

        # 7. Persist resume metadata
        resume = Resume(
            applicant_id=applicant.id,
            file_name=safe_filename,
            file_path=file_path,
            parsed_text=parsed_text,
        )
        saved_resume = await self.resume_repo.create(resume)

        return ResumeUploadResponse(
            applicant=self._to_applicant_response(applicant),
            resume=self._to_resume_response(saved_resume),
        )

    async def update_applicant(
        self, applicant_id: uuid.UUID, data: ApplicantUpdateRequest
    ) -> ApplicantResponse:
        """Update an applicant's details (e.g. after manual confirmation/changes)."""
        applicant = await self.applicant_repo.get_by_id(applicant_id)
        if applicant is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Applicant not found.",
            )

        if data.full_name is not None:
            applicant.full_name = data.full_name
        if data.email is not None:
            applicant.email = data.email
        if data.phone is not None:
            applicant.phone = data.phone
        if data.linkedin_url is not None:
            applicant.linkedin_url = data.linkedin_url
        if data.github_url is not None:
            applicant.github_url = data.github_url

        updated = await self.applicant_repo.update(applicant)
        return self._to_applicant_response(updated)