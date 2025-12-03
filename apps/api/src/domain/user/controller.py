from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_cache.decorator import cache
from dependency_injector.wiring import inject, Provide
from pydantic import BaseModel, EmailStr, Field

from src.core.handler.exception import exception_handler, AlreadyExistUserEx
from src.container import AppContainer
from src.core.middlewares.log import LogRoute
from src.db.redis.cache_manager import key_builder
from .service import UserService
from .dtos import CreateUserRequest, CreateUserResponse


# Pydantic 모델 정의
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None


class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True


# API 라우터 생성
user_router = APIRouter(tags=["users"], prefix="/users", route_class=LogRoute)


@user_router.get("/", response_model=List[UserResponse])
@cache(expire=100, key_builder=key_builder)
@inject
async def get_users(
    user_service: UserService = Depends(Provide["user_container.user_service"])
):
    """
    모든 사용자 목록을 반환합니다.
    """
    users = await user_service.get_all_users()
    return users


@user_router.get("/{user_id}", response_model=UserResponse)
@inject
async def get_user(
    user_id: int,
    user_service: UserService = Depends(Provide["user_container.user_service"])
):
    """
    특정 사용자 정보를 조회합니다.
    """
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return user


@user_router.post("/", response_model=CreateUserResponse, status_code=status.HTTP_201_CREATED)
@inject
async def create_user(
    user_data: CreateUserRequest,
    user_service: UserService = Depends(Provide["user_container.user_service"])
):
    """
    새로운 사용자를 생성합니다.
    """   
    try:
        return await user_service.create_user(user_data.model_dump())
    except AlreadyExistUserEx as e:
        return await exception_handler(e)


@user_router.put("/{user_id}", response_model=UserResponse)
@inject
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    user_service: UserService = Depends(Provide["user_container.user_service"])
):
    """
    사용자 정보를 업데이트합니다.
    """
    updated_user = await user_service.update_user(user_id, user_data.model_dump(exclude_unset=True))
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return updated_user


@user_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_user(
    user_id: int,
    user_service: UserService = Depends(Provide["user_container.user_service"])
):
    """
    사용자를 삭제합니다.
    """
    deleted = await user_service.delete_user(user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return None
