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

    @model_validator(mode="after")
    def validate_fields(self):
        if len(self.username) < 4 or len(self.username) > 10:
            raise ValueError("Username must be between 4 and 10 characters long")

        if len(self.password) < 6:
            raise ValueError("Password must be at least 6 characters long")

        return self


class CreateUserResponse(BaseModel):
    id: int
    email: EmailStr