from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

class StatusCode:
    HTTP_500 = 500
    HTTP_400 = 400
    HTTP_401 = 401
    HTTP_403 = 403
    HTTP_404 = 404
    HTTP_405 = 405
    HTTP_409 = 409
    HTTP_422 = 422


class CustomException(Exception):
    status_code: int
    code: str
    msg: str
    detail: str
    ex: Exception

    def __init__(
        self,
        *,
        status_code: int = StatusCode.HTTP_500,
        code: str = "000000",
        msg: str = None,
        detail: str = None,
        ex: Exception = None,
    ):
        self.status_code = status_code
        self.code = code
        self.msg = msg
        self.detail = detail
        self.ex = ex
        super().__init__(ex)


class NotFoundUserEx(CustomException):
    def __init__(self, user_id: int = None, ex: Exception = None):
        super().__init__(
            status_code=StatusCode.HTTP_404,
            msg=f"해당 유저를 찾을 수 없습니다.",
            detail=f"Not Found User ID : {user_id}",
            code=f"{StatusCode.HTTP_400}{'1'.zfill(4)}",
            ex=ex,
        )

class AlreadyExistUserEx(CustomException):
    def __init__(self, ex: Exception = None):
        super().__init__(
            status_code=StatusCode.HTTP_400,
            msg=f"해당 유저는 이미 존재합니다.",
            detail=f"Already Exist User ID",
            code=f"{StatusCode.HTTP_400}{'1'.zfill(4)}",
            ex=ex,
        )


class NotAuthorized(CustomException):
    def __init__(self, ex: Exception = None):
        super().__init__(
            status_code=StatusCode.HTTP_401,
            msg=f"로그인이 필요한 서비스 입니다.",
            detail="Authorization Required",
            code=f"{StatusCode.HTTP_401}{'1'.zfill(4)}",
            ex=ex,
        )

async def exception_handler(ex: CustomException):
    return JSONResponse(
        status_code=ex.status_code,
        content={
            "code": ex.code,
            "msg": ex.msg,
            "detail": ex.detail,
        }
    )