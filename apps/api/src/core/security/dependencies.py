from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, ExpiredSignatureError
from pydantic import BaseModel
from dependency_injector.wiring import inject, Provide

from .jwt import jwt_handler


# Bearer 토큰 스키마
bearer_scheme = HTTPBearer(auto_error=False)

# Redis 블랙리스트 키 prefix (service.py와 동일)
BLACKLIST_PREFIX = "token_blacklist:"


class CurrentUser(BaseModel):
    """현재 인증된 사용자 정보"""
    id: int
    email: str
    role: str

    class Config:
        from_attributes = True


@inject
async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    redis_client = Depends(Provide["redis_client"]),
) -> CurrentUser:
    """
    JWT 토큰에서 현재 사용자 정보 추출

    Usage:
        @router.get("/protected")
        async def protected_route(current_user: CurrentUser = Depends(get_current_user)):
            return {"user_id": current_user.id}
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증 토큰이 필요합니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        # 블랙리스트 확인
        blacklist_key = f"{BLACKLIST_PREFIX}{token}"
        is_blacklisted = await redis_client.get(blacklist_key)
        if is_blacklisted:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="로그아웃된 토큰입니다.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        payload = jwt_handler.verify_access_token(token)

        user_id = payload.get("sub")
        email = payload.get("email")
        role = payload.get("role")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 토큰입니다.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return CurrentUser(id=int(user_id), email=email, role=role)

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰이 만료되었습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )


@inject
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    redis_client = Depends(Provide["redis_client"]),
) -> Optional[CurrentUser]:
    """
    JWT 토큰에서 현재 사용자 정보 추출 (선택적)
    토큰이 없거나 유효하지 않으면 None 반환

    Usage:
        @router.get("/public")
        async def public_route(current_user: Optional[CurrentUser] = Depends(get_current_user_optional)):
            if current_user:
                return {"user_id": current_user.id}
            return {"message": "Guest"}
    """
    if credentials is None:
        return None

    try:
        return await get_current_user(credentials, redis_client)
    except HTTPException:
        return None


async def get_current_admin_user(
    current_user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    """
    관리자 권한 확인

    Usage:
        @router.get("/admin")
        async def admin_route(current_user: CurrentUser = Depends(get_current_admin_user)):
            return {"admin_id": current_user.id}
    """
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다.",
        )
    return current_user
