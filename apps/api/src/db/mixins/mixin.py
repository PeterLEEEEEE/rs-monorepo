from datetime import datetime
from sqlalchemy.sql import expression
from sqlalchemy import DateTime, func, Boolean
from sqlalchemy.orm import Mapped, mapped_column


class Mixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=expression.false()  # default=False
    )
    
    deleted_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=True,
        default=None
    )

    def soft_delete(self, session):
        self.is_deleted = True
        self.deleted_at = datetime.now()
        session.commit()