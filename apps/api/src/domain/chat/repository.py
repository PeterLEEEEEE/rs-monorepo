from datetime import datetime
from sqlalchemy import select, desc, func, update

from .base import BaseAlchemyRepository
from .models import ChatRoom, ChatMessage


class ChatRepository(BaseAlchemyRepository[ChatRoom]):

    def __init__(self, session_factory):
        super().__init__(model=ChatRoom, session_factory=session_factory)

    async def get_next_turn_id(self, room_id: str) -> int:
        """채팅방의 다음 turn_id 반환"""
        async with self.session_factory() as session:
            query = select(func.max(ChatMessage.turn_id)).where(
                ChatMessage.chat_room_id == room_id
            )
            result = await session.execute(query)
            max_turn = result.scalar()
            return (max_turn or 0) + 1

    async def create_chatroom(self, user_id: str, title: str = None) -> ChatRoom:
        """채팅방 생성 후 ChatRoom 객체 반환"""
        async with self.session_factory() as session:
            chat_room = ChatRoom(user_id=user_id, title=title)
            session.add(chat_room)
            await session.commit()
            await session.refresh(chat_room)
            return chat_room

    async def get_chatroom(self, room_id: str) -> ChatRoom | None:
        """채팅방 조회"""
        async with self.session_factory() as session:
            query = select(ChatRoom).where(
                ChatRoom.id == room_id,
                ChatRoom.is_deleted == False
            )
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def get_chatrooms_paginated(
        self, user_id: str, page: int = 1, limit: int = 10
    ) -> tuple[list[ChatRoom], int]:
        """사용자의 채팅방 목록 조회 (페이지네이션)"""
        async with self.session_factory() as session:
            # 전체 개수 조회
            count_query = select(func.count(ChatRoom.id)).where(
                ChatRoom.user_id == user_id,
                ChatRoom.is_deleted == False
            )
            total_result = await session.execute(count_query)
            total = total_result.scalar() or 0

            # 페이지네이션된 목록 조회
            offset = (page - 1) * limit
            query = select(ChatRoom).where(
                ChatRoom.user_id == user_id,
                ChatRoom.is_deleted == False
            ).order_by(desc(ChatRoom.updated_at)).offset(offset).limit(limit)
            result = await session.execute(query)
            rooms = list(result.scalars().all())

            return rooms, total

    async def update_chatroom(self, room_id: str, title: str) -> ChatRoom | None:
        """채팅방 제목 수정"""
        async with self.session_factory() as session:
            query = select(ChatRoom).where(
                ChatRoom.id == room_id,
                ChatRoom.is_deleted == False
            )
            result = await session.execute(query)
            chat_room = result.scalar_one_or_none()
            if chat_room:
                chat_room.title = title
                chat_room.updated_at = datetime.utcnow()
                await session.commit()
                await session.refresh(chat_room)
            return chat_room

    async def delete_chatroom(self, room_id: str) -> bool:
        """채팅방 soft delete"""
        async with self.session_factory() as session:
            query = select(ChatRoom).where(ChatRoom.id == room_id)
            result = await session.execute(query)
            chat_room = result.scalar_one_or_none()
            if chat_room:
                chat_room.is_deleted = True
                chat_room.deleted_at = datetime.utcnow()
                await session.commit()
                return True
            return False

    async def add_message(self, room_id: str, turn_id: int, role: str, content: str) -> ChatMessage:
        """메시지 저장"""
        async with self.session_factory() as session:
            message = ChatMessage(chat_room_id=room_id, turn_id=turn_id, role=role, content=content)
            session.add(message)
            await session.commit()
            await session.refresh(message)
            return message

    async def get_messages_paginated(
        self, room_id: str, page: int = 1, limit: int = 20
    ) -> tuple[list[ChatMessage], int]:
        """채팅방 메시지 조회 (페이지네이션)"""
        async with self.session_factory() as session:
            # 전체 메시지 개수 조회
            count_query = select(func.count(ChatMessage.id)).where(
                ChatMessage.chat_room_id == room_id
            )
            total_result = await session.execute(count_query)
            total = total_result.scalar() or 0

            # 페이지네이션 (최신 메시지부터)
            offset = (page - 1) * limit
            query = select(ChatMessage).where(
                ChatMessage.chat_room_id == room_id
            ).order_by(desc(ChatMessage.created_at)).offset(offset).limit(limit)
            result = await session.execute(query)
            # 시간순 정렬로 반환
            messages = list(reversed(result.scalars().all()))

            return messages, total

    async def get_messages(self, room_id: str, limit: int = 50) -> list[ChatMessage]:
        """채팅방 메시지 조회 (Agent용 - 최근 N개)"""
        async with self.session_factory() as session:
            query = select(ChatMessage).where(
                ChatMessage.chat_room_id == room_id
            ).order_by(desc(ChatMessage.created_at)).limit(limit)
            result = await session.execute(query)
            return list(reversed(result.scalars().all()))

    async def get_message_count(self, room_id: str) -> int:
        """채팅방 메시지 개수 조회"""
        async with self.session_factory() as session:
            query = select(func.count(ChatMessage.id)).where(
                ChatMessage.chat_room_id == room_id
            )
            result = await session.execute(query)
            return result.scalar() or 0

    async def get_last_message(self, room_id: str) -> ChatMessage | None:
        """채팅방 마지막 메시지 조회"""
        async with self.session_factory() as session:
            query = select(ChatMessage).where(
                ChatMessage.chat_room_id == room_id
            ).order_by(desc(ChatMessage.created_at)).limit(1)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def update_room_timestamp(self, room_id: str) -> None:
        """채팅방 updated_at 갱신"""
        async with self.session_factory() as session:
            stmt = update(ChatRoom).where(
                ChatRoom.id == room_id
            ).values(updated_at=datetime.utcnow())
            await session.execute(stmt)
            await session.commit()