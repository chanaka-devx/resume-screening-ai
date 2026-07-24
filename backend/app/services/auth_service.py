from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password, verify_password
from app.models.recruiter import Recruiter
from app.repositories.recruiter_repository import RecruiterRepository
from app.schemas.auth import (
    LoginRequest,
    RecruiterRegisterRequest,
    RecruiterResponse,
    TokenResponse,
)


class AuthService:
    """Business logic for recruiter registration and authentication."""

    def __init__(self, session: AsyncSession) -> None:
        self.repo = RecruiterRepository(session)

    async def register(self, data: RecruiterRegisterRequest) -> RecruiterResponse:
        """
        Register a new recruiter.
        Raises 409 if the email is already taken.
        """
        if await self.repo.email_exists(data.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A recruiter with this email already exists.",
            )

        recruiter = Recruiter(
            name=data.name,
            email=data.email,
            password_hash=hash_password(data.password),
            company=data.company,
            role=data.role,
        )
        saved = await self.repo.create(recruiter)
        return RecruiterResponse(
            id=str(saved.id),
            name=saved.name,
            email=saved.email,
            company=saved.company,
            role=saved.role,
            is_active=saved.is_active,
        )

    async def login(self, data: LoginRequest) -> TokenResponse:
        """
        Authenticate a recruiter and return a JWT.
        Raises 401 if credentials are invalid.
        """
        recruiter = await self.repo.get_by_email(data.email)

        if recruiter is None or not verify_password(data.password, recruiter.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not recruiter.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive.",
            )

        token = create_access_token({"sub": str(recruiter.id), "role": recruiter.role})
        return TokenResponse(access_token=token)
