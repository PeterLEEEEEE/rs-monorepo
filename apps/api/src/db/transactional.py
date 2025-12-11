"""트랜잭션 데코레이터"""
import logging
from functools import wraps

from .session import session

logger = logging.getLogger(__name__)


def transactional(func):
    """
    Service 메서드에 트랜잭션을 적용하는 데코레이터.

    - 성공 시 commit, 실패 시 rollback
    - session context는 SQLAlchemyMiddleware가 관리
    - 단순 조회는 이 데코레이터 없이 사용 (commit 불필요)

    Usage:
        class ChatService:
            @transactional
            async def delete_chatroom(self, chat_id: str):
                count = await self.repository.get_message_count(chat_id)
                await self.repository.hard_delete(chat_id)
                # 자동 commit
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
            await session.commit()
            logger.debug(f"Transaction committed: {func.__name__}")
            return result
        except Exception as e:
            await session.rollback()
            logger.error(f"Transaction rolled back: {func.__name__} - {e}")
            raise

    return wrapper
