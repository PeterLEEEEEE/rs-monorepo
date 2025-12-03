import os
from pydantic import Field, ConfigDict, field_validator, PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # OpenAI API 설정
    OPENAI_API_KEY: str = Field(..., alias="OPENAI_API_KEY")
    OPENAI_API_VERSION: str = Field(..., alias="OPENAI_API_VERSION")
    OPENAI_API_BASE: str = Field(..., alias="OPENAI_API_BASE")
    OPENAI_DEPLOYMENT_NAME: str = Field(..., alias="OPENAI_DEPLOYMENT_NAME")
    
    # 애플리케이션 설정
    APP_ENV: str = Field("dev", alias="APP_ENV")
    DEBUG: bool = Field(True, alias="DEBUG")
    API_PREFIX: str = Field("/api/v1", alias="API_PREFIX")
    
    # MongoDB 설정
    MONGODB_URI: str = Field(..., alias="MONGODB_URI")
    MONGO_INITDB_ROOT_USERNAME: str = Field(..., alias="MONGO_INITDB_ROOT_USERNAME")
    MONGO_INITDB_ROOT_PASSWORD: str = Field(..., alias="MONGO_INITDB_ROOT_PASSWORD")
    MONGO_INITDB_DATABASE: str = Field(..., alias="MONGO_INITDB_DATABASE")
    MONGO_HOST: str = Field("localhost", alias="MONGO_HOST")
    MONGO_PORT: int = Field(27017, alias="MONGO_PORT")
    
    # PostgreSQL 설정
    POSTGRES_URL: PostgresDsn | None = None
    POSTGRES_USER: str = Field(..., alias="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(..., alias="POSTGRES_PASSWORD")
    
    POSTGRES_DB_URL: str = Field(..., alias="POSTGRES_DB_URL")
    POSTGRES_DB: str = Field(..., alias="POSTGRES_DB")
    DB_HOST: str = Field("postgres", alias="DB_HOST")
    DB_PORT: int = Field(5432, alias="DB_PORT")
    DB_ECHO: bool = Field(False, alias="DB_ECHO")
    DB_POOL_SIZE: int = Field(10, alias="DB_POOL_SIZE")
    DB_MAX_OVERFLOW: int = Field(20, alias="DB_MAX_OVERFLOW")
    DB_POOL_RECYCLE: int = Field(3600, alias="DB_POOL_RECYCLE")
    
    # Redis 설정
    REDIS_PASSWORD: str = Field(..., alias="REDIS_PASSWORD")
    REDIS_HOST: str = Field("localhost", alias="REDIS_HOST")
    REDIS_PORT: int = Field(6379, alias="REDIS_PORT")
    REDIS_DB: str = Field("test", alias="REDIS_DB")
    # REDIS_SSL: bool = Field(False, env="REDIS_SSL")
    
    # JWT 설정
    JWT_SECRET: str = Field("secret", alias="JWT_SECRET")
    JWT_ALGORITHM: str = Field("HS256", alias="JWT_ALGORITHM")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(60, alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # HTTPX 설정
    CLIENT_TIME_OUT: int = Field(5, alias="CLIENT_TIME_OUT")
    SIZE_POOL_HTTPX: int = Field(100, alias="SIZE_POOL_HTTPX")

    # Langfuse 설정
    LANGFUSE_HOST: str = Field("http://langfuse:3000", alias="LANGFUSE_HOST")
    LANGFUSE_PUBLIC_KEY: str = Field("", alias="LANGFUSE_PUBLIC_KEY")
    LANGFUSE_SECRET_KEY: str = Field("", alias="LANGFUSE_SECRET_KEY")
    
    # CORS Settings
    ALLOW_ORIGINS: str = Field(..., alias="ALLOW_ORIGINS")
    ALLOW_CREDENTIALS: bool = Field(True, alias="ALLOW_CREDENTIALS")
    ALLOW_METHODS: str = Field(..., alias="ALLOW_METHODS")
    ALLOW_HEADERS: str = Field(..., alias="ALLOW_HEADERS")
    
    
    model_config = ConfigDict(
        extra="ignore",
        env_file=f".env.{os.getenv('APP_ENV', 'dev')}",
        env_file_encoding="utf-8",
        env_ignore_empty=True,  # 환경 파일에 빈 값이 있더라도 오류 발생 X
        validate_default=False,  # 누락된 기본값에 대해 유효성 검사를 진행
        use_enum_values=True,
    )
    
    @field_validator("MONGODB_URI")
    def build_mongodb_uri(cls, v, values):
        if v:
            return v
        username = values.get("MONGO_INITDB_ROOT_USERNAME")
        password = values.get("MONGO_INITDB_ROOT_PASSWORD")
        host = values.get("MONGO_HOST")
        port = values.get("MONGO_PORT")
        db = values.get("MONGO_INITDB_DATABASE")
        
        if username and password:
            return f"mongodb://{username}:{password}@{host}:{port}/{db}"
        return f"mongodb://{host}:{port}/{db}"
    

    def get_db_url(self):
        """PostgreSQL DB URL 생성"""
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.POSTGRES_DB}"
    
    def get_mygration_url(self):
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@localhost:{self.DB_PORT}/{self.POSTGRES_DB}"
    
    def get_redis_url(self):
        """Redis URL 생성"""
        protocol = "rediss" if self.REDIS_SSL else "redis"
        if self.REDIS_PASSWORD:
            return f"{protocol}://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"{protocol}://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


def get_config() -> Settings:
    """
    애플리케이션 설정을 로드하여 반환
    """
    try:
        return Settings()
    except Exception as e:
        print(f"Warning: Error loading configuration: {e}")
        return Settings.model_construct()
    

config: Settings = get_config()