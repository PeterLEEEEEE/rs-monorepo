"""SQLAlchemy 세션 관리 미들웨어"""
from uuid import uuid4

from starlette.types import ASGIApp, Receive, Scope, Send

from src.db.session import session, set_session_context, reset_session_context


class SQLAlchemyMiddleware:
    """
    모든 HTTP 요청에 session context를 설정하고 cleanup하는 미들웨어.

    - 요청 시작: session_id 생성, context 설정
    - 요청 종료: session.remove(), context reset
    - commit/rollback은 @transactional 데코레이터가 담당
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        # HTTP 요청만 처리 (websocket, lifespan 등 제외)
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        session_id = str(uuid4())
        context = set_session_context(session_id)

        try:
            await self.app(scope, receive, send)
        except Exception as e:
            raise e
        finally:
            await session.remove()
            reset_session_context(context)
