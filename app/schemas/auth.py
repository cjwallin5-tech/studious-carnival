from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    """JSON login body (the OAuth2 form login lives at /auth/token)."""

    username: str
    password: str
