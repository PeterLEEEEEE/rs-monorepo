from sqlalchemy import select, desc, func

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

    async def add_chatroom(self, user_id: str, title: str = None) -> str:
        """채팅방 생성 후 room_id 반환"""
        async with self.session_factory() as session:
            chat_room = ChatRoom(user_id=user_id, title=title)
            session.add(chat_room)
            await session.commit()
            await session.refresh(chat_room)
            return str(chat_room.id)

    async def get_chatroom(self, room_id: str) -> ChatRoom | None:
        """채팅방 조회"""
        async with self.session_factory() as session:
            query = select(ChatRoom).where(
                ChatRoom.id == room_id,
                ChatRoom.is_deleted == False
            )
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def get_chatrooms(self, user_id: str) -> list[ChatRoom]:
        """사용자의 채팅방 목록 조회"""
        async with self.session_factory() as session:
            query = select(ChatRoom).where(
                ChatRoom.user_id == user_id,
                ChatRoom.is_deleted == False
            ).order_by(desc(ChatRoom.updated_at))
            result = await session.execute(query)
            return list(result.scalars().all())

    async def delete_chatroom(self, room_id: str) -> bool:
        """채팅방 soft delete"""
        async with self.session_factory() as session:
            query = select(ChatRoom).where(ChatRoom.id == room_id)
            result = await session.execute(query)
            chat_room = result.scalar_one_or_none()
            if chat_room:
                chat_room.is_deleted = True
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

    async def get_messages(self, room_id: str, limit: int = 50) -> list[ChatMessage]:
        """채팅방 메시지 조회 (최신순 limit개)"""
        async with self.session_factory() as session:
            query = select(ChatMessage).where(
                ChatMessage.chat_room_id == room_id
            ).order_by(desc(ChatMessage.created_at)).limit(limit)
            result = await session.execute(query)
            # 시간순 정렬로 반환
            return list(reversed(result.scalars().all()))