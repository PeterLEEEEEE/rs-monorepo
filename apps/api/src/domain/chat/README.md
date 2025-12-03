# Chat API

채팅방 관리 및 메시지 전송 API

## Base URL

```
/api/chat/room
```

## Endpoints

### 채팅방 생성

```
POST /api/chat/room
```

**Request Body**
```json
{
  "user_id": "string"
}
```

**Response**
```json
{
  "room_id": "uuid-xxx-xxx"
}
```

---

### 채팅방 목록 조회

```
GET /api/chat/room?user_id={user_id}
```

**Query Parameters**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | string | Yes | 사용자 ID |

**Response**
```json
[
  {
    "chatroom_id": "uuid-xxx",
    "created_at": "2025-01-01T00:00:00",
    "updated_at": "2025-01-01T00:00:00",
    "metadata": {
      "message_count": 10,
      "last_activity": "2025-01-01T00:00:00"
    }
  }
]
```

---

### 채팅 히스토리 조회

```
GET /api/chat/room/{room_id}
```

**Path Parameters**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| room_id | string | Yes | 채팅방 ID |

**Response**
```json
[
  {
    "role": "user",
    "content": "안녕하세요"
  },
  {
    "role": "assistant",
    "content": "안녕하세요! 무엇을 도와드릴까요?"
  }
]
```

---

### 채팅방 삭제

```
DELETE /api/chat/room/{room_id}
```

**Path Parameters**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| room_id | string | Yes | 채팅방 ID |

**Response**
```json
{
  "message": "deleted"
}
```

---

### 메시지 전송

```
POST /api/chat/room/{room_id}/message
```

**Path Parameters**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| room_id | string | Yes | 채팅방 ID |

**Request Body**
```json
{
  "message": "string"
}
```

**Response**
```json
{
  "response": "AI 응답 메시지"
}
```

## Error Response

모든 API는 에러 발생 시 다음 형식으로 응답합니다:

```json
{
  "detail": "에러 메시지"
}
```

| Status Code | Description |
|-------------|-------------|
| 400 | Bad Request |
| 404 | Not Found |
| 500 | Internal Server Error |
