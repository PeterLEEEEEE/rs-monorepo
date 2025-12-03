from typing_extensions import Optional, Literal
from pydantic import Field, BaseModel, ConfigDict


class User(BaseModel):
    id: str = Field(...)
    username: str = Field(
        description="user name",
        examples=["peter", "john", "mary"],
    )
    email: str = Field(
        description="user email",
        examples=[""]
    )
    password: str = Field(
        description="user password",
        examples=["password123", "securepassword!"],
    )
    
    description: Optional[str] = Field(
        default=None,
        description="Description of the chat room.",
        examples=["A chat room for general discussions.", "A chat room for real estate inquiries."],
    )
    
    is_active: bool = Field(
        default=False,
        description="Indicates whether the user is deleted.",
        examples=[False, True],
    )
    is_deleted: bool = Field(
        default=False,
        description="Indicates whether the user is deleted.",
        examples=[False, True],
    )
    
    model_config = ConfigDict(
        extra="ignore",
        validate_default=False,  # 누락된 기본값에 대해 유효성 검사를 하지 않음
        use_enum_values=True,
    )