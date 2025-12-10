from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dependency_injector.wiring import inject, Provide

from src.core.security.dependencies import get_current_user, CurrentUser, bearer_scheme

from .service import AuthService
from .dtos import (
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    RefreshTokenRequest,
    RefreshResponse,
    UserResponse,
    MessageResponse,
)


auth_router = APIRouter(tags=["Auth"], prefix="/auth")


@auth_router.post("/login", response_model=LoginResponse)
@inject
async def login(
    body: LoginRequest,
    auth_service: AuthService = Depends(Provide["auth_container.auth_service"]),
):
    """
    로그인

    - email, password로 인증
    - 성공 시 access_token, refresh_token 반환
    """
    result = await auth_service.login(body.email, body.password)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return result


@auth_router.post("/refresh", response_model=RefreshResponse)
@inject
async def refresh_token(
    body: RefreshTokenRequest,
    auth_service: AuthService = Depends(Provide["auth_container.auth_service"]),
):
    """
    Access Token 갱신

    - refresh_token으로 새 access_token 발급
    """
    result = await auth_service.refresh_access_token(body.refresh_token)

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
    body: LogoutRequest,
    current_user: CurrentUser = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    auth_service: AuthService = Depends(Provide["auth_container.auth_service"]),
):
    """
    로그아웃

    - Access Token을 Redis 블랙리스트에 추가
    - Refresh Token을 DB에서 삭제
    """
    access_token = credentials.credentials
    success = await auth_service.logout(access_token, body.refresh_token)

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
