import uuid
from sqlalchemy import Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from src.db.postgres.conn import Base
from src.db.mixins.timestamp_mixin import TimestampMixin
from src.db.mixins.softdelete_mixin import SoftDeleteMixin


class ChatRoom(Base, TimestampMixin, SoftDeleteMixin):
    """채팅방"""
    __tablename__ = "chat_rooms"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=True)


class ChatMessage(Base, TimestampMixin):
    """채팅 메시지"""
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    chat_room_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)
    turn_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)  # 대화 턴 번호
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # "user" or "assistant"
    content: Mapped[str] = mapped_column(Text, nullable=False)

