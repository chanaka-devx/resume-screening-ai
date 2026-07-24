from pydantic import BaseModel, EmailStr


# ── Request schemas ───────────────────────────────────────────────────────────

class RecruiterRegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    company: str
    role: str = "recruiter"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ── Response schemas ──────────────────────────────────────────────────────────

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RecruiterResponse(BaseModel):
    id: str
    name: str
    email: str
    company: str
    role: str
    is_active: bool

    model_config = {"from_attributes": True}
