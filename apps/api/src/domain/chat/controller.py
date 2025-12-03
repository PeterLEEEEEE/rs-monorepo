from logger import logger
from fastapi import APIRouter, Depends, HTTPException, status
from dependency_injector.wiring import inject, Provide
from pydantic import BaseModel

from .service import ChatService

chat_router = APIRouter(tags=["Chat"], prefix="/chat/room")


class MessageInput(BaseModel):
    message: str


class CreateRoomInput(BaseModel):
    user_id: str
    title: str | None = None


class RoomResponse(BaseModel):
    room_id: str


@chat_router.post("", response_model=RoomResponse)
@inject
async def create_room(
    body: CreateRoomInput,
    chat_service: ChatService = Depends(Provide["chat_container.chat_service"])
):
    """채팅방 생성"""
    logger.info(f"Creating chatroom for user {body.user_id}")
    try:
        room_id = await chat_service.add_chatroom(body.user_id, body.title)
        return RoomResponse(room_id=room_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@chat_router.get("")
@inject
async def list_rooms(
    user_id: str,
    chat_service: ChatService = Depends(Provide["chat_container.chat_service"])
):
    """채팅방 목록 조회"""
    try:
        rooms = await chat_service.get_chatrooms(user_id)
        return [
            {
                "id": str(room.id),
                "user_id": room.user_id,
                "title": room.title,
                "created_at": room.created_at.isoformat(),
                "updated_at": room.updated_at.isoformat(),
            }
            for room in rooms
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@chat_router.get("/{room_id}")
@inject
async def get_room(
    room_id: str,
    chat_service: ChatService = Depends(Provide["chat_container.chat_service"])
):
    """채팅 히스토리 조회"""
    try:
        chat_history = await chat_service.get_chat_history(room_id)
        return chat_history
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@chat_router.delete("/{room_id}")
@inject
async def delete_room(
    room_id: str,
    chat_service: ChatService = Depends(Provide["chat_container.chat_service"])
):
    """채팅방 삭제"""
    try:
        await chat_service.delete_chatroom(room_id)
        return {"message": "deleted"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@chat_router.post("/{room_id}/message")
@inject
async def send_message(
    room_id: str,
    body: MessageInput,
    chat_service: ChatService = Depends(Provide["chat_container.chat_service"])
):
    """메시지 전송 (Agent 호출)"""
    try:
        response = await chat_service.invoke_agent(body.message, room_id)
        return {"response": response}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )