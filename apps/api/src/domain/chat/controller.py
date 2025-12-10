from datetime import datetime
from logger import logger
from fastapi import APIRouter, Depends, HTTPException, Query, status
from dependency_injector.wiring import inject, Provide
from pydantic import BaseModel

from src.core.security.dependencies import get_current_user, CurrentUser
from .service import ChatService

chat_router = APIRouter(tags=["Chat"], prefix="/chat")


# ============== Request Schemas ==============

class CreateChatRequest(BaseModel):
    title: str | None = None


class UpdateChatRequest(BaseModel):
    title: str


class SendMessageRequest(BaseModel):
    message: str


# ============== Response Schemas ==============

class MessageResponse(BaseModel):
    id: int
    turn_id: int
    role: str
    content: str
    created_at: datetime


class LastMessageResponse(BaseModel):
    content: str
    role: str
    created_at: datetime


class ChatRoomResponse(BaseModel):
    id: str
    title: str | None
    user_id: str
    created_at: datetime
    updated_at: datetime


class ChatRoomDetailResponse(BaseModel):
    id: str
    title: str | None
    user_id: str
    message_count: int
    created_at: datetime
    updated_at: datetime


class ChatRoomListItemResponse(BaseModel):
    id: str
    title: str | None
    user_id: str
    message_count: int
    last_message: LastMessageResponse | None
    created_at: datetime
    updated_at: datetime


class PaginationResponse(BaseModel):
    page: int
    limit: int
    total: int
    has_next: bool
    has_prev: bool


class ChatRoomListResponse(BaseModel):
    items: list[ChatRoomListItemResponse]
    pagination: PaginationResponse


class ChatRoomWithMessagesResponse(BaseModel):
    room: ChatRoomDetailResponse
    messages: list[MessageResponse]
    pagination: PaginationResponse


class SendMessageResponse(BaseModel):
    turn_id: int
    user_message: MessageResponse
    assistant_message: MessageResponse


class DeleteResponse(BaseModel):
    success: bool
    message: str


# ============== Endpoints ==============

@chat_router.post("", response_model=ChatRoomResponse, status_code=status.HTTP_201_CREATED)
@inject
async def create_chat(
    body: CreateChatRequest,
    current_user: CurrentUser = Depends(get_current_user),
    chat_service: ChatService = Depends(Provide["chat_container.chat_service"]),
):
    """채팅방 생성"""
    user_id = str(current_user.id)
    logger.info(f"Creating chatroom for user {user_id}")
    room = await chat_service.create_chatroom(user_id, body.title)
    return ChatRoomResponse(
        id=str(room.id),
        title=room.title,
        user_id=room.user_id,
        created_at=room.created_at,
        updated_at=room.updated_at,
    )


@chat_router.get("", response_model=ChatRoomListResponse)
@inject
async def list_chats(
    current_user: CurrentUser = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    chat_service: ChatService = Depends(Provide["chat_container.chat_service"]),
):
    """채팅방 목록 조회"""
    user_id = str(current_user.id)
    result = await chat_service.get_chatroom_list(user_id, page, limit)
    return result


@chat_router.get("/{chat_id}", response_model=ChatRoomWithMessagesResponse)
@inject
async def get_chat(
    chat_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    chat_service: ChatService = Depends(Provide["chat_container.chat_service"]),
):
    """채팅방 진입 (히스토리 조회)"""
    user_id = str(current_user.id)

    # 채팅방 존재 및 소유자 검증
    room = await chat_service.get_chatroom(chat_id)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="채팅방을 찾을 수 없습니다."
        )
    if room.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="접근 권한이 없습니다."
        )

    result = await chat_service.get_chat_detail(chat_id, page, limit)
    return result


@chat_router.patch("/{chat_id}", response_model=ChatRoomResponse)
@inject
async def update_chat(
    chat_id: str,
    body: UpdateChatRequest,
    current_user: CurrentUser = Depends(get_current_user),
    chat_service: ChatService = Depends(Provide["chat_container.chat_service"]),
):
    """채팅방 수정 (제목 변경)"""
    user_id = str(current_user.id)

    # 채팅방 존재 및 소유자 검증
    room = await chat_service.get_chatroom(chat_id)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="채팅방을 찾을 수 없습니다."
        )
    if room.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="수정 권한이 없습니다."
        )

    updated_room = await chat_service.update_chatroom(chat_id, body.title)
    return ChatRoomResponse(
        id=str(updated_room.id),
        title=updated_room.title,
        user_id=updated_room.user_id,
        created_at=updated_room.created_at,
        updated_at=updated_room.updated_at,
    )


@chat_router.delete("/{chat_id}", response_model=DeleteResponse)
@inject
async def delete_chat(
    chat_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    chat_service: ChatService = Depends(Provide["chat_container.chat_service"]),
):
    """채팅방 삭제"""
    user_id = str(current_user.id)

    # 채팅방 존재 및 소유자 검증
    room = await chat_service.get_chatroom(chat_id)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="채팅방을 찾을 수 없습니다."
        )
    if room.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="삭제 권한이 없습니다."
        )

    await chat_service.delete_chatroom(chat_id)
    return DeleteResponse(success=True, message="삭제되었습니다.")


@chat_router.post("/{chat_id}/message", response_model=SendMessageResponse)
@inject
async def send_message(
    chat_id: str,
    body: SendMessageRequest,
    current_user: CurrentUser = Depends(get_current_user),
    chat_service: ChatService = Depends(Provide["chat_container.chat_service"]),
):
    """메시지 전송 (Agent 호출)"""
    user_id = str(current_user.id)

    # 채팅방 존재 및 소유자 검증
    room = await chat_service.get_chatroom(chat_id)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="채팅방을 찾을 수 없습니다."
        )
    if room.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="접근 권한이 없습니다."
        )

    result = await chat_service.send_message(body.message, chat_id, user_id)
    return result