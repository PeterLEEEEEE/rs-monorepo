from sqlalchemy import Integer, String, Boolean, VARCHAR
from sqlalchemy.sql import expression
from sqlalchemy.orm import Mapped, mapped_column
from src.db.postgres.conn import Base
from src.db.mixins.mixin import Mixin


class User(Base, Mixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String(1024), nullable=False)
    role: Mapped[str] = mapped_column(VARCHAR(20), nullable=False, default="USER")  # e.g., "user", "admin"
    is_active: Mapped[bool] = mapped_column(
        Boolean, 
        nullable=False, 
        server_default=expression.true()  # default=True
    )

class UserSession(Base, Mixin):
    __tablename__ = "user_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)  # User ID
    session_token: Mapped[str] = mapped_column(String(256), nullable=False, unique=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, 
        nullable=False, 
        server_default=expression.true()  # default=True
    )
    
class LoginHistory(Base, Mixin):
    __tablename__ = "login_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)  # User ID
    event_type: Mapped[str] = mapped_column(
        String(50), 
        nullable=False, 
        default="LOGIN"  # e.g., "login", "logout", "failed"
    )
    login_time: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., ISO format datetime
    ip_address: Mapped[str] = mapped_column(String(45), nullable=True)  # IPv6 support
    

class UserPreference(Base, Mixin):
    """_summary_

    개인화 설정(알림 여부, 테마 설정 등)을 저장
    """
    __tablename__ = "user_preferences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)  # User ID
    preference_key: Mapped[str] = mapped_column(String(100), nullable=False)
    preference_value: Mapped[str] = mapped_column(String(1024), nullable=True)
    