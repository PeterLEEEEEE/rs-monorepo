CREATE EXTENSION IF NOT EXISTS vector;

DROP TABLE IF EXISTS request_response_log;
CREATE TABLE request_response_log (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER,
    ip VARCHAR(45) NOT NULL,
    port INTEGER NOT NULL,
    agent TEXT NOT NULL,
    method VARCHAR(30) NOT NULL,
    path TEXT NOT NULL,
    response_status SMALLINT NOT NULL,
    request_id UUID NOT NULL DEFAULT gen_random_uuid(),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

DROP TABLE IF EXISTS complexes;
CREATE TABLE complexes (
    id BIGSERIAL PRIMARY KEY,
    complex_id VARCHAR(50) NOT NULL,
    address VARCHAR(50) NOT NULL,
    data_vector VECTOR(1536) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

DROP TABLE IF EXISTS price_histories;
CREATE TABLE price_histories (
    id BIGSERIAL PRIMARY KEY,
    floor INTEGER NOT NULL,
    area_type VARCHAR(10) NOT NULL,
    area_info INTEGER NOT NULL,
    trade_type VARCHAR(10) NOT NULL,
    trade_date VARCHAR (10) NOT NULL, 
    sold_price INTEGER NOT NULL,
    complex_id VARCHAR(50) NOT NULL,
    address VARCHAR(50) NOT NULL,
    data_vector VECTOR(1536) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);


DROP TABLE IF EXISTS chat_histories;
CREATE TABLE chat_histories (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER,
    question TEXT NOT NULL,
    agent_id VARCHAR(120) NOT NULL,
    sender_id VARCHAR(120) NOT NULL, 
    chatroom_id VARCHAR(120) NOT NULL,
    chat_message TEXT NOT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);


-- TODO: conversations, messages 테이블 생성 후 주석 해제
-- CREATE TABLE IF NOT EXISTS conversation_turns (
--     id BIGSERIAL PRIMARY KEY,
--     conversation_id BIGINT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
--     user_message_id BIGINT NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
--     agent_message_id BIGINT NULL REFERENCES messages(id) ON DELETE SET NULL,
--     started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
--     completed_at TIMESTAMPTZ NULL,
--     latency_ms INT NULL,
--     model TEXT NULL,
--     meta JSONB NULL
-- );