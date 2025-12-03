from fastapi import APIRouter, Depends, Response

# from application.core.authority.permissions import AllowAll
# from application.core.dependencies import PermissionDependency
# from application.core.fastapi.log_route import LogRoute

# home_router = APIRouter(route_class=LogRoute)
home_router = APIRouter()


# @home_router.get("/health", dependencies=[Depends(PermissionDependency([AllowAll]))])
@home_router.get("/health")
async def home():
    return Response(status_code=200)