from starlette.authentication import AuthenticationBackend, AuthCredentials, SimpleUser
from pydantic import BaseModel, Field


class CurrentUser(BaseModel):
    id: int = Field(None, description="ID")

class CustomAuthenticationBackend(AuthenticationBackend):
    async def authenticate(self, request):
        current_user = CurrentUser()
        authorization: str = conn.headers.get("Authorization")
        if not authorization:
            return False, current_user

        try:
            scheme, credentials = authorization.split(" ")
            if scheme.lower() != "bearer":
                return False, current_user
        except ValueError:
            return False, current_user

        if not credentials:
            return False, current_user
            
    async def dispatch(self, request, call_next):
        # This method can be used to add custom logic before and after the request is processed
        response = await call_next(request)
        return response