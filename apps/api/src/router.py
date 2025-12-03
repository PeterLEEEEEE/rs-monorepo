from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict
from src.domain.home.views import home_router
from src.domain.user.controller import user_router as user_v1_router # User 라우터 import
from src.domain.chat.controller import chat_router
from src.core.utils import snake2camel


class ResponseBaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=snake2camel,
        populate_by_name=True,     # allow_population_by_field_name
        from_attributes=True       # orm_mode
    )


class ErrorResponse(ResponseBaseModel):
    code: str
    message: str
    data: dict | list | None

router = APIRouter(
    responses={
        400: {
            "model": ErrorResponse
        },
        401: {
            "model": ErrorResponse
        }
    }
)


router.include_router(home_router, tags=["Home"])
router.include_router(user_v1_router)  # User 라우터 등록
router.include_router(chat_router, tags=["Chat"])