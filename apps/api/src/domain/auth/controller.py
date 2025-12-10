from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dependency_injector.wiring import inject, Provide
from typing import Optional

from src.core.security.dependencies import get_current_user, CurrentUser, bearer_scheme
from src.core.config.settings import config

from .service import AuthService
from .dtos import (
    LoginRequest,
    LoginResponse,
    LoginResult,
    LogoutRequest,
    RefreshResponse,
    UserResponse,
    MessageResponse,
)


auth_router = APIRouter(tags=["Auth"], prefix="/auth")


@auth_router.post("/login", response_model=LoginResponse)
@inject
async def login(
    body: LoginRequest,
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(Provide["auth_container.auth_service"]),
):
    """
    로그인

    - email, password로 인증
    - 성공 시 access_token 반환, refresh_token은 httpOnly 쿠키로 설정
    - 같은 device_id로 재로그인 시 기존 토큰 삭제 후 새로 발급
    """
    # 클라이언트 IP 주소 추출
    ip_address = request.client.host if request.client else None

    result = await auth_service.login(
        email=body.email,
        password=body.password,
        device_id=body.device_id,
        ip_address=ip_address,
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Refresh Token을 httpOnly 쿠키로 설정
    response.set_cookie(
        key="refresh_token",
        value=result.refresh_token,
        httponly=True,
        secure=config.COOKIE_SECURE,
        samesite=config.COOKIE_SAMESITE,
        max_age=config.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/api/v1/auth",  # auth 경로에서만 쿠키 전송
    )

    return LoginResponse(
        access_token=result.access_token,
        token_type=result.token_type,
        expires_in=result.expires_in,
        user=result.user,
    )


@auth_router.post("/refresh", response_model=RefreshResponse)
@inject
async def refresh_token(
    refresh_token: Optional[str] = Cookie(None),
    auth_service: AuthService = Depends(Provide["auth_container.auth_service"]),
):
    """
    Access Token 갱신

    - httpOnly 쿠키의 refresh_token으로 새 access_token 발급
    """
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token이 없습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await auth_service.refresh_access_token(refresh_token)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 refresh token입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return result


@auth_router.post("/logout", response_model=MessageResponse)
@inject
async def logout(
    response: Response,
    refresh_token: Optional[str] = Cookie(None),
    current_user: CurrentUser = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    auth_service: AuthService = Depends(Provide["auth_container.auth_service"]),
):
    """
    로그아웃

    - Access Token을 Redis 블랙리스트에 추가
    - Refresh Token을 DB에서 삭제
    - Refresh Token 쿠키 삭제
    """
    access_token = credentials.credentials
    success = await auth_service.logout(access_token, refresh_token or "")

    # Refresh Token 쿠키 삭제
    response.delete_cookie(
        key="refresh_token",
        path="/api/v1/auth",
        httponly=True,
        secure=config.COOKIE_SECURE,
        samesite=config.COOKIE_SAMESITE,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="로그아웃 처리 중 오류가 발생했습니다.",
        )

    return MessageResponse(message="로그아웃되었습니다.")


@auth_router.get("/me", response_model=UserResponse)
@inject
async def get_me(
    current_user: CurrentUser = Depends(get_current_user),
    auth_service: AuthService = Depends(Provide["auth_container.auth_service"]),
):
    """
    현재 로그인한 사용자 정보 조회
    """
    user = await auth_service.get_user_by_id(current_user.id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다.",
        )

    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        role=user.role,
    )
