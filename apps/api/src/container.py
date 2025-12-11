import httpx
from dependency_injector import containers, providers
from redis.asyncio.client import Redis
from langchain_openai import AzureChatOpenAI
# from pymongo import AsyncMongoClient

from src.core.config.container import config_container
from src.db.conn import SQLAlchemyConnection
from src.db.session import init_session
from src.domain.user.container import UserContainer
from src.domain.chat.container import ChatContainer
from src.domain.auth.container import AuthContainer
from src.agents.container import AgentContainer


# def get_mongo_database(client, db_name):
#     """MongoDB 데이터베이스 인스턴스를 반환하는 헬퍼 함수"""
#     return client[db_name]


def get_httpx_client(client_timeout, limit_per_host):
    # httpx는 limits 파라미터로 커넥션 풀 설정
    limits = httpx.Limits(max_connections=limit_per_host)
    return httpx.AsyncClient(timeout=client_timeout, limits=limits)


def create_db_connection(db_url: str, **kwargs) -> SQLAlchemyConnection:
    """DB 연결 생성 및 글로벌 session 초기화"""
    conn = SQLAlchemyConnection(db_url, **kwargs)
    init_session(conn.async_engine)
    return conn


class AppContainer(containers.DeclarativeContainer):
    config = config_container.config

    wiring_config = containers.WiringConfiguration(
        packages=["src"],
        modules=[__name__],
    )

    async_http_client = providers.Callable(
        get_httpx_client,
        client_timeout=config.CLIENT_TIME_OUT,
        limit_per_host=config.SIZE_POOL_HTTPX,
    )
    db = providers.Singleton(
        create_db_connection,
        db_url=config.POSTGRES_DB_URL,
        pool_size=config.DB_POOL_SIZE,
        max_overflow=config.DB_MAX_OVERFLOW,
        pool_recycle=config.DB_POOL_RECYCLE,
    )

    llm = providers.Singleton(
        AzureChatOpenAI,
        azure_deployment=config.OPENAI_DEPLOYMENT_NAME,
        api_version=config.OPENAI_API_VERSION,
        azure_endpoint=config.OPENAI_API_BASE,
        api_key=config.OPENAI_API_KEY,
    )
    
    # mongo_client = providers.Singleton(
    #     AsyncMongoClient,
    #     config.MONGODB_URI,
    # )

    # mongo_proxy = providers.Factory(
    #     get_mongo_database,
    #     client=mongo_client,
    #     db_name=config.MONGO_INITDB_DATABASE
    # )
    
    # # Redis 연결 (설정 객체의 get_redis_url 메소드 사용)
    # redis = providers.Singleton(
    #     Redis.from_url,
    #     url=config.get_redis_url(),
    # )

    redis_client = providers.Singleton(
        Redis.from_url,
        url=f"redis://:{config.REDIS_PASSWORD()}@redis:{config.REDIS_PORT()}",
        decode_responses=True
    )
    
    user_container = providers.Container(UserContainer)

    auth_container = providers.Container(
        AuthContainer,
        redis_client=redis_client,
    )

    # AgentContainer를 먼저 정의 (ChatContainer에서 orchestrator 사용)
    agent_container = providers.Container(
        AgentContainer,
        llm=llm,
    )

    chat_container = providers.Container(
        ChatContainer,
        # mongo_db=mongo_proxy,
        orchestrator=agent_container.orchestrator,  # Singleton orchestrator 주입
    )
    
    # # HomeContainer 구조 준비 (구현 시 주석 제거)
    # home_container = providers.Container(
    #     # HomeContainer,
    #     # session=session,
    #     # config=config,
    #     # redis=redis,
    # )