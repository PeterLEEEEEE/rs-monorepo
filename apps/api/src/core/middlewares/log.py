import logging
from typing import Callable, Any
from pydantic import BaseModel, Field, ConfigDict
from fastapi.routing import APIRoute
from starlette.requests import Request
from starlette.responses import Response
from starlette.datastructures import Headers
from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = logging.getLogger(__name__)


# class LoggingMiddleware:
#     """
#     Middleware for logging requests and responses.
#     """

#     async def __call__(self, request, call_next):
#         # Log the request
#         print(f"Request: {request.method} {request.url}")

#         # Process the request
#         response = await call_next(request)

#         # Log the response
#         print(f"Response: {response.status_code}")

#         return response


class LogRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()
        
        async def custom_route_handler(request: Request) -> Response:
            await self._request_log(request)
            response: Response = await original_route_handler(request)
            self._response_log(request, response)
            return response

        return custom_route_handler
    
    @staticmethod
    def _has_json_body(request: Request) -> bool:
        if (
                request.method in ("POST", "PUT", "PATCH") 
                and request.headers.get("content-type") == "application/json"
            ):
                return True
        return False
    
    async def _request_log(self, request: Request) -> None:
        extra: dict[str, Any] = {
            "httpMethod": request.method,
            "url": request.url.path,
            "headers": request.headers,
            "queryParams": request.query_params,
        }

        if self._has_json_body(request):
            request_body = await request.body()
            extra["body"] = request_body.decode("UTF-8")

        logger.info("request", extra=extra)
    
    @staticmethod
    def _response_log(request: Request, response: Response) -> None:
        extra: dict[str, str] = {
            "httpMethod": request.method,
            "url": request.url.path,
            "body": response.body.decode("UTF-8")
        }
		
        logger.info("response", extra=extra)