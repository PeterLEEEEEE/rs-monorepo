from datetime import datetime
from pydantic import BaseModel, EmailStr


# ============== Request Schemas ==============

class LoginRequest(BaseModel):
    """로그인 요청"""
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    """토큰 갱신 요청"""
    refresh_token: str


class LogoutRequest(BaseModel):
    """로그아웃 요청"""
    refresh_token: str


# ============== Response Schemas ==============

class UserResponse(BaseModel):
    """사용자 정보 응답"""
    id: int
    email: str
    username: str
    role: str

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """토큰 응답"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class LoginResponse(BaseModel):
    """로그인 응답"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: UserResponse


class RefreshResponse(BaseModel):
    """토큰 갱신 응답"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class MessageResponse(BaseModel):
    """단순 메시지 응답"""
    message: str
