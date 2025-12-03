# FastAPI + LangGraph realestate Chatbot

# Base Features
- Async SQLAlchemy 
- Python dependency injector
- Docker

# Todo(구현 예정)
- 현재는 구조만 잡힌 상태
- MongoDB 체크포인터 멀티턴 토큰 소모 최적화
- Redis도 injector에 주입하게끔 해야함(src/server.py에서 container로)
- chat service 구현

# Configuration

```
touch .env.dev
```

```shell
APP_ENV=dev
API_PREFIX=/api/v1

OPENAI_API_KEY="your openai key"
OPENAI_API_VERSION="your openai api version" 
OPENAI_API_TYPE="your openai api type" 
OPENAI_API_BASE="your openai endpoint" 
OPENAI_DEPLOYMENT_NAME="your openai deployment name" 

MONGODB_URI="mongodb://admin:abc123@mongo:27017/test?authSource=admin"
MONGO_HOST=mongo
MONGO_PORT=27017
MONGO_INITDB_ROOT_USERNAME=admin
MONGO_INITDB_ROOT_PASSWORD=abc123
MONGO_INITDB_DATABASE=test

POSTGRES_DB_URL=postgresql+asyncpg://admin:abc123@postgres:5432/test
POSTGRES_DB=test
POSTGRES_USER=admin
POSTGRES_PASSWORD=abc123
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20

REDIS_DB=test
REDIS_PORT=6379
REDIS_HOST=localhost
REDIS_PASSWORD=abc123

JWT_SECRET=your_jwt_secret_key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

ALLOW_ORIGINS='*'
ALLOW_CREDENTIALS=True
ALLOW_METHODS='*'
ALLOW_HEADERS='*'

CLIENT_TIME_OUT=5
SIZE_POOL_HTTPX=100
```

## Run Server

```shell
make dc-up
```



