from typing import Optional
from logger import logger

from src.agents import OrchestratorAgent
from .base import BaseService
from .repository import ChatRepository


class ChatService(BaseService):
    """Chat service using multi-agent orchestrator."""

    def __init__(self, repository: ChatRepository, orchestrator: OrchestratorAgent):
        super().__init__(repository=repository, agent=orchestrator)
        self.orchestrator = orchestrator

    async def invoke_agent(
        self,
        user_input: str,
        room_id: str,
        user_id: Optional[str] = None,
    ) -> str:
        """
        Agent 호출 with 히스토리.

        1. DB에서 기존 메시지 히스토리 조회
        2. 새 turn_id 생성 및 사용자 메시지 저장
        3. 히스토리 + 새 메시지로 Agent 호출
        4. AI 응답 저장 후 반환 (같은 turn_id)
        """
        try:
            # 1. 기존 히스토리 조회
            history = await self.repository.get_messages(room_id, limit=20)

            # 2. 새 turn_id 생성 및 사용자 메시지 저장
            turn_id = await self.repository.get_next_turn_id(room_id)
            await self.repository.add_message(room_id, turn_id, "user", user_input)

            # 3. 히스토리를 메시지 포맷으로 변환
            messages = [(msg.role, msg.content) for msg in history]
            messages.append(("user", user_input))

            # 4. Agent 호출 (히스토리 포함)
            result = await self.orchestrator.invoke_with_history(
                messages=messages,
                context_id=room_id,
                user_id=user_id,
            )

            # 5. AI 응답 추출 및 저장 (같은 turn_id)
            ai_response = result.get("messages", [])[-1].content if result.get("messages") else ""
            await self.repository.add_message(room_id, turn_id, "assistant", ai_response)

            return ai_response

        except Exception as e:
            logger.error(f"Invoke error: {e}")
            raise

    async def add_chatroom(self, user_id: str, title: str = None) -> str:
        """채팅방 생성"""
        logger.info(f"[ChatService] Creating chatroom for user {user_id}")
        return await self.repository.add_chatroom(user_id, title)

    async def get_chatrooms(self, user_id: str) -> list:
        """사용자의 채팅방 목록 조회"""
        return await self.repository.get_chatrooms(user_id)

    async def get_chat_history(self, room_id: str) -> list:
        """채팅 히스토리 조회"""
        messages = await self.repository.get_messages(room_id)
        return [{"role": msg.role, "content": msg.content} for msg in messages]

    async def delete_chatroom(self, room_id: str) -> bool:
        """채팅방 삭제"""
        return await self.repository.delete_chatroom(room_id)
