from pydantic import BaseModel, EmailStr, model_validator
from typing_extensions import Any


class UserInfoRequest(BaseModel):
    user_id: str
    

class UserInfoResponse(BaseModel):
    username: str


class CreateUserRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

    @model_validator(mode="before")
    def validate(cls, data):
        if len(data.username) < 4 or len(data.username) > 10:
            raise ValueError("Username must be between 4 and 10 characters long")
        
        if len(data.password) < 6:
            raise ValueError("Password must be at least 6 characters long")


class CreateUserResponse(BaseModel):
    id: int
    email: EmailStr