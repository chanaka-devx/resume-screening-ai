from typing import Annotated

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_recruiter
from app.dependencies.database import get_db
from app.models.recruiter import Recruiter
from app.schemas.application import ApplicationResponse, ApplicationSubmitRequest
from app.services.application_service import ApplicationService

router = APIRouter(prefix="/applications", tags=["Applications"])


# ── POST /applications ────────────────────────────────────────────────────────
@router.post(
    "",
    response_model=ApplicationResponse,
    status_code=201,
    summary="Submit a job application",
)
async def submit_application(
    data: ApplicationSubmitRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> ApplicationResponse:
    return await ApplicationService(session).submit_application(data)


# ── GET /applications/{application_id}/resume ─────────────────────────────────
@router.get(
    "/{application_id}/resume",
    status_code=200,
    summary="Download candidate resume for an application (RS-031)",
    responses={
        200: {
            "content": {"application/pdf": {}},
            "description": "Returns the PDF resume file.",
        },
        404: {"description": "Application, job, or resume not found."},
        502: {"description": "Storage retrieval failure."},
    },
)
async def download_application_resume(
    application_id: str,
    current_recruiter: Annotated[Recruiter, Depends(get_current_recruiter)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> Response:
    """
    Download the PDF resume for a candidate's application.

    - **Requires recruiter authentication**.
    - **Verifies recruiter ownership** of the job associated with this application.
    - Returns **404** if the application does not exist, job does not exist/is deleted,
      recruiter does not own the job, or resume file is missing in storage.
    - Returns **502** if storage retrieval encounters an unexpected failure.
    """
    file_bytes, filename = await ApplicationService(session).download_resume(
        application_id=application_id,
        recruiter=current_recruiter,
    )
    return Response(
        content=file_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )

