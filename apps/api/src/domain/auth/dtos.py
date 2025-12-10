from datetime import datetime
from pydantic import BaseModel, EmailStr


# ============== Request Schemas ==============

class LoginRequest(BaseModel):
    """로그인 요청"""
    email: EmailStr
    password: str
    device_id: str | None = None  # FingerprintJS에서 생성된 디바이스 ID


class LogoutRequest(BaseModel):
    """로그아웃 요청 (refresh_token은 httpOnly 쿠키에서 읽음)"""
    pass


# ============== Response Schemas ==============

class UserResponse(BaseModel):
    """사용자 정보 응답"""
    id: int
    email: str
    username: str
    role: str

    class Config:
        from_attributes = True


# ============== Internal DTOs ==============

class LoginResult(BaseModel):
    """내부용 로그인 결과 (service → controller)"""
    access_token: str
    refresh_token: str  # 쿠키로 전달
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class TokenResponse(BaseModel):
    """토큰 응답"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class LoginResponse(BaseModel):
    """로그인 응답 (refresh_token은 httpOnly 쿠키로 전달)"""
    access_token: str
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
