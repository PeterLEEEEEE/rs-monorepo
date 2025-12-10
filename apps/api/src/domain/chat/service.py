from typing import Optional
from logger import logger

from src.agents import OrchestratorAgent
from .base import BaseService
from .repository import ChatRepository
from .models import ChatRoom, ChatMessage


class ChatService(BaseService):
    """Chat service using multi-agent orchestrator."""

    def __init__(self, repository: ChatRepository, orchestrator: OrchestratorAgent):
        super().__init__(repository=repository, agent=orchestrator)
        self.orchestrator = orchestrator

    # ============== 채팅방 관리 ==============

    async def create_chatroom(self, user_id: str, title: str = None) -> ChatRoom:
        """채팅방 생성"""
        logger.info(f"[ChatService] Creating chatroom for user {user_id}")
        return await self.repository.create_chatroom(user_id, title)

    async def get_chatroom(self, chat_id: str) -> ChatRoom | None:
        """채팅방 조회"""
        return await self.repository.get_chatroom(chat_id)

    async def get_chatroom_list(self, user_id: str, page: int = 1, limit: int = 10) -> dict:
        """채팅방 목록 조회 (페이지네이션 + 마지막 메시지)"""
        rooms, total = await self.repository.get_chatrooms_paginated(user_id, page, limit)

        items = []
        for room in rooms:
            message_count = await self.repository.get_message_count(str(room.id))
            last_message = await self.repository.get_last_message(str(room.id))

            items.append({
                "id": str(room.id),
                "title": room.title,
                "user_id": room.user_id,
                "message_count": message_count,
                "last_message": {
                    "content": last_message.content[:100] if last_message else None,
                    "role": last_message.role if last_message else None,
                    "created_at": last_message.created_at if last_message else None,
                } if last_message else None,
                "created_at": room.created_at,
                "updated_at": room.updated_at,
            })

        total_pages = (total + limit - 1) // limit
        return {
            "items": items,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "has_next": page < total_pages,
                "has_prev": page > 1,
            }
        }

    async def get_chat_detail(self, chat_id: str, page: int = 1, limit: int = 20) -> dict:
        """채팅방 상세 조회 (방 정보 + 메시지 히스토리)"""
        room = await self.repository.get_chatroom(chat_id)
        if not room:
            return None

        messages, total = await self.repository.get_messages_paginated(chat_id, page, limit)
        message_count = await self.repository.get_message_count(chat_id)

        total_pages = (total + limit - 1) // limit
        return {
            "room": {
                "id": str(room.id),
                "title": room.title,
                "user_id": room.user_id,
                "message_count": message_count,
                "created_at": room.created_at,
                "updated_at": room.updated_at,
            },
            "messages": [
                {
                    "id": msg.id,
                    "turn_id": msg.turn_id,
                    "role": msg.role,
                    "content": msg.content,
                    "created_at": msg.created_at,
                }
                for msg in messages
            ],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "has_next": page < total_pages,
                "has_prev": page > 1,
            }
        }

    async def update_chatroom(self, chat_id: str, title: str) -> ChatRoom | None:
        """채팅방 제목 수정"""
        return await self.repository.update_chatroom(chat_id, title)

    async def delete_chatroom(self, chat_id: str) -> bool:
        """채팅방 삭제"""
        return await self.repository.delete_chatroom(chat_id)

    # ============== 메시지 처리 ==============

    async def send_message(
        self,
        user_input: str,
        chat_id: str,
        user_id: Optional[str] = None,
    ) -> dict:
        """
        메시지 전송 및 Agent 호출.

        1. DB에서 기존 메시지 히스토리 조회
        2. 새 turn_id 생성 및 사용자 메시지 저장
        3. 히스토리 + 새 메시지로 Agent 호출
        4. AI 응답 저장 후 반환 (같은 turn_id)
        """
        try:
            # 1. 기존 히스토리 조회
            history = await self.repository.get_messages(chat_id, limit=20)

            # 2. 새 turn_id 생성 및 사용자 메시지 저장
            turn_id = await self.repository.get_next_turn_id(chat_id)
            user_msg = await self.repository.add_message(chat_id, turn_id, "user", user_input)

            # 3. 히스토리를 메시지 포맷으로 변환
            messages = [(msg.role, msg.content) for msg in history]
            messages.append(("user", user_input))

            # 4. Agent 호출 (히스토리 포함)
            result = await self.orchestrator.invoke_with_history(
                messages=messages,
                context_id=chat_id,
                user_id=user_id,
            )

            # 5. AI 응답 추출 및 저장 (같은 turn_id)
            ai_response = result.get("messages", [])[-1].content if result.get("messages") else ""
            assistant_msg = await self.repository.add_message(chat_id, turn_id, "assistant", ai_response)

            # 6. 채팅방 updated_at 갱신
            await self.repository.update_room_timestamp(chat_id)

            return {
                "turn_id": turn_id,
                "user_message": {
                    "id": user_msg.id,
                    "turn_id": user_msg.turn_id,
                    "role": user_msg.role,
                    "content": user_msg.content,
                    "created_at": user_msg.created_at,
                },
                "assistant_message": {
                    "id": assistant_msg.id,
                    "turn_id": assistant_msg.turn_id,
                    "role": assistant_msg.role,
                    "content": assistant_msg.content,
                    "created_at": assistant_msg.created_at,
                }
            }

        except Exception as e:
            logger.error(f"Send message error: {e}")
            raise
