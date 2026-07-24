from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.dependencies.database import get_db
from app.models.recruiter import Recruiter
from app.repositories.recruiter_repository import RecruiterRepository

bearer_scheme = HTTPBearer()


async def get_current_recruiter(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> Recruiter:
    """
    FastAPI dependency — extract and validate the Bearer JWT,
    then return the matching Recruiter row.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(credentials.credentials)
        recruiter_id: str = payload.get("sub")
        if recruiter_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    repo = RecruiterRepository(session)
    recruiter = await repo.get_by_id(recruiter_id)
    if recruiter is None or not recruiter.is_active:
        raise credentials_exception

    return recruiter
