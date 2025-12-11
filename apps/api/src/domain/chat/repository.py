from datetime import datetime, timezone
from sqlalchemy import select, desc, func, update

from src.db.base_repository import BaseRepository
from .models import ChatRoom, ChatMessage


class ChatRepository(BaseRepository):
    """Chat Repository"""

    async def get_next_turn_id(self, room_id: str) -> int:
        """채팅방의 다음 turn_id 반환"""
        query = select(func.max(ChatMessage.turn_id)).where(
            ChatMessage.chat_room_id == room_id
        )
        result = await self.session.execute(query)
        max_turn = result.scalar()
        return (max_turn or 0) + 1

    async def create_chatroom(self, user_id: str, title: str = None) -> ChatRoom:
        """채팅방 생성 후 ChatRoom 객체 반환"""
        chat_room = ChatRoom(user_id=user_id, title=title)
        self.session.add(chat_room)
        await self.session.flush()
        await self.session.refresh(chat_room)
        return chat_room

    async def get_chatroom(self, room_id: str) -> ChatRoom | None:
        """채팅방 조회"""
        query = select(ChatRoom).where(
            ChatRoom.id == room_id,
            ChatRoom.is_deleted.is_(False)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_chatrooms_paginated(
        self, user_id: str, page: int = 1, limit: int = 10
    ) -> tuple[list[ChatRoom], int]:
        """사용자의 채팅방 목록 조회 (페이지네이션)"""
        # 전체 개수 조회
        count_query = select(func.count(ChatRoom.id)).where(
            ChatRoom.user_id == user_id,
            ChatRoom.is_deleted.is_(False)
        )
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0

        # 페이지네이션된 목록 조회
        offset = (page - 1) * limit
        query = select(ChatRoom).where(
            ChatRoom.user_id == user_id,
            ChatRoom.is_deleted.is_(False)
        ).order_by(desc(ChatRoom.updated_at)).offset(offset).limit(limit)
        result = await self.session.execute(query)
        rooms = list(result.scalars().all())

        return rooms, total

    async def update_chatroom(self, room_id: str, title: str) -> ChatRoom | None:
        """채팅방 제목 수정"""
        query = select(ChatRoom).where(
            ChatRoom.id == room_id,
            ChatRoom.is_deleted.is_(False)
        )
        result = await self.session.execute(query)
        chat_room = result.scalar_one_or_none()
        if chat_room:
            chat_room.title = title
            chat_room.updated_at = datetime.now(timezone.utc)
            await self.session.flush()
            await self.session.refresh(chat_room)
        return chat_room

    async def delete_chatroom(self, room_id: str) -> bool:
        """채팅방 soft delete"""
        query = select(ChatRoom).where(ChatRoom.id == room_id)
        result = await self.session.execute(query)
        chat_room = result.scalar_one_or_none()
        if chat_room:
            chat_room.is_deleted = True
            chat_room.deleted_at = datetime.now(timezone.utc)
            await self.session.flush()
            return True
        return False

    async def hard_delete_chatroom(self, room_id: str) -> bool:
        """채팅방 물리 삭제 (메시지가 없는 경우용)"""
        query = select(ChatRoom).where(ChatRoom.id == room_id)
        result = await self.session.execute(query)
        chat_room = result.scalar_one_or_none()
        if chat_room:
            await self.session.delete(chat_room)
            await self.session.flush()
            return True
        return False

    async def add_message(self, room_id: str, turn_id: int, role: str, content: str) -> ChatMessage:
        """메시지 저장"""
        message = ChatMessage(chat_room_id=room_id, turn_id=turn_id, role=role, content=content)
        self.session.add(message)
        await self.session.flush()
        await self.session.refresh(message)
        return message

    async def get_messages_paginated(
        self, room_id: str, page: int = 1, limit: int = 20
    ) -> tuple[list[ChatMessage], int]:
        """채팅방 메시지 조회 (페이지네이션)"""
        # 전체 메시지 개수 조회
        count_query = select(func.count(ChatMessage.id)).where(
            ChatMessage.chat_room_id == room_id
        )
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0

        # 페이지네이션 (최신 메시지부터)
        offset = (page - 1) * limit
        query = select(ChatMessage).where(
            ChatMessage.chat_room_id == room_id
        ).order_by(desc(ChatMessage.created_at)).offset(offset).limit(limit)
        result = await self.session.execute(query)
        # 시간순 정렬로 반환
        messages = list(reversed(result.scalars().all()))

        return messages, total

    async def get_messages(self, room_id: str, limit: int = 50) -> list[ChatMessage]:
        """채팅방 메시지 조회 (Agent용 - 최근 N개)"""
        query = select(ChatMessage).where(
            ChatMessage.chat_room_id == room_id
        ).order_by(desc(ChatMessage.created_at)).limit(limit)
        result = await self.session.execute(query)
        return list(reversed(result.scalars().all()))

    async def get_message_count(self, room_id: str) -> int:
        """채팅방 메시지 개수 조회"""
        query = select(func.count(ChatMessage.id)).where(
            ChatMessage.chat_room_id == room_id
        )
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def get_last_message(self, room_id: str) -> ChatMessage | None:
        """채팅방 마지막 메시지 조회"""
        query = select(ChatMessage).where(
            ChatMessage.chat_room_id == room_id
        ).order_by(desc(ChatMessage.created_at)).limit(1)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def update_room_timestamp(self, room_id: str) -> None:
        """채팅방 updated_at 갱신"""
        stmt = update(ChatRoom).where(
            ChatRoom.id == room_id
        ).values(updated_at=datetime.now(timezone.utc))
        await self.session.execute(stmt)
        await self.session.flush()
