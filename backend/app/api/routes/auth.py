from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_recruiter
from app.dependencies.database import get_db
from app.models.recruiter import Recruiter
from app.schemas.auth import (
    LoginRequest,
    RecruiterRegisterRequest,
    RecruiterResponse,
    TokenResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ── POST /auth/register ───────────────────────────────────────────────────────
@router.post(
    "/register",
    response_model=RecruiterResponse,
    status_code=201,
    summary="Register a new recruiter account",
)
async def register(
    data: RecruiterRegisterRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> RecruiterResponse:
    return await AuthService(session).register(data)


# ── POST /auth/login ──────────────────────────────────────────────────────────
@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate and receive a JWT access token",
)
async def login(
    data: LoginRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    return await AuthService(session).login(data)


# ── GET /auth/me ──────────────────────────────────────────────────────────────
@router.get(
    "/me",
    response_model=RecruiterResponse,
    summary="Return the currently authenticated recruiter",
)
async def me(
    current_recruiter: Annotated[Recruiter, Depends(get_current_recruiter)],
) -> RecruiterResponse:
    return RecruiterResponse(
        id=str(current_recruiter.id),
        name=current_recruiter.name,
        email=current_recruiter.email,
        company=current_recruiter.company,
        role=current_recruiter.role,
        is_active=current_recruiter.is_active,
    )
