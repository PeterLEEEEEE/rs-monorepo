from sqlalchemy import Integer, String, Boolean, VARCHAR, Float
from sqlalchemy.sql import expression
from sqlalchemy.orm import Mapped, mapped_column
from src.db.postgres.conn import Base
from src.db.mixins.mixin import Mixin


class Complex(Base, Mixin):
    __tablename__ = "complexes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    complex_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="APT")  # e.g., "APARTMENT
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)  # 가격
    size: Mapped[float] = mapped_column(Float, nullable=False)  # 면적


class ComplexComment(Base, Mixin):
    __tablename__ = "complex_comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    complex_id: Mapped[int] = mapped_column(Integer, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(VARCHAR(500), nullable=False)  # 댓글 내용
    # like_count: Mapped[int] = mapped_column(Integer, nullable=False)  # 좋아요 수 (캐시 때문에 분리할까 고민중)


class CommentLike(Base, Mixin):
    __tablename__ = "comment_likes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    comment_id: Mapped[int] = mapped_column(Integer, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)  # 좋아요 누른 사용자 ID


