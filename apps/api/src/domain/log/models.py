import uuid

import sqlalchemy as sa
from sqlalchemy import BigInteger, Column, Integer, String, VARCHAR, SMALLINT
from sqlalchemy_utils import UUIDType
from sqlalchemy.orm import Mapped, mapped_column

from src.db.postgres.conn import Base
from src.db.mixins.mixin import Mixin


class RequestResponseLog(Base, Mixin):
    __tablename__ = "request_response_log"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer)
    ip: Mapped[str] = mapped_column(VARCHAR(30), nullable=False)
    port: Mapped[int] = mapped_column(Integer, nullable=False)
    agent: Mapped[str] = mapped_column(VARCHAR, nullable=False)
    method: Mapped[str] = mapped_column(VARCHAR(30), nullable=False)
    path: Mapped[str] = mapped_column(VARCHAR(30), nullable=False)
    response_status: Mapped[int] = mapped_column(SMALLINT, nullable=False)
    request_id: Mapped[str] = mapped_column(UUIDType(binary=False), nullable=False, default=uuid.uuid4)