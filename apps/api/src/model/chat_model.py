from typing_extensions import Optional, Literal
from pydantic import Field, BaseModel, ConfigDict
# from pydantic_settings import BaseSettings


class ChatRoom(BaseModel):
    id: str = Field(...)
    user_id: str = Field(..., alias="userId")
    name: str = Field(
        description="Name of the chat room.",
        examples=["General Chat", "Real Estate Inquiry"],
    )
    description: Optional[str] = Field(
        default=None,
        description="Description of the chat room.",
        examples=["A chat room for general discussions.", "A chat room for real estate inquiries."],
    )
    is_deleted: bool = Field(
        default=False,
        description="Indicates whether the chat room is deleted.",
        examples=[False, True],
    )
    
    
class ChatMessage(BaseModel):
    id: str = Field(...)
    chatroom_id: str = Field(..., alias="chatroomId")
    type: Literal["human", "ai", "tool", "custom"] = Field(
        description="Role of the message.",
        examples=["human", "ai", "tool", "custom"],
    )
    content: str = Field(
        description="Content of the message.",
        examples=["Hello, world!"],
    )
    
class ChatHistory(BaseModel):
    # chat_message_id: str = Field(..., alias="chatMessageId")
    chatroom_id: str = Field(..., alias="chatroomId")
    user_id: str = Field(..., alias="userId")
    messages: list[ChatMessage] = Field(..., alias="messages")

        
    model_config = ConfigDict(
        extra="ignore",
        validate_default=False,  # 누락된 기본값에 대해 유효성 검사를 하지 않음
        use_enum_values=True,
    )
    
    # model_config = ConfigDict(
    #     extra="ignore",
    #     env_file=f".env.{os.getenv('APP_ENV', 'dev')}",
    #     env_file_encoding="utf-8",
    #     env_ignore_empty=True,  # 환경 파일에 빈 값이 있더라도 오류 발생 X
    #     validate_default=False,  # 누락된 기본값에 대해 유효성 검사를 하지 않음
    #     use_enum_values=True,
    # )