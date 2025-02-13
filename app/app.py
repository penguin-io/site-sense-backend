from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi_users.authentication import JWTStrategy
import casbin

from app.db.users import create_user_db_and_tables
from app.db.projects import create_project_db_and_tables
from app.schemas.users import UserCreate, UserRead, UserUpdate
from app.manager.users import auth_backend, current_active_user, fastapi_users, auth_backend
from app.router import project_router, worksite_router, zone_router
from app.casbin import CasbinMiddleware, get_user_managerx


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Not needed if you setup a migration system like Alembic
    await create_user_db_and_tables()
    await create_project_db_and_tables()
    yield


enforcer = casbin.Enforcer('rbac_model.conf', 'rbac_policy.csv')





class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, jwt_strategy: JWTStrategy):
        super().__init__(app)
        self.jwt_strategy = jwt_strategy

    async def dispatch(self, request: Request, call_next):
        token = request.headers.get("Authorization")
        if token and token.startswith("Bearer "):
            token = token.split(" ")[1]
            user_manager = await get_user_managerx()
            print(type(user_manager))
            user = await self.jwt_strategy.read_token(token, user_manager)
            if user:
                request.state.user = user.email
            else:
                request.state.user = "anonymous"
        else:
            request.state.user = "anonymous"
        print(request.state.user)
        return await call_next(request)



app = FastAPI(lifespan=lifespan)
app.add_middleware(CasbinMiddleware, enforcer=enforcer)
app.add_middleware(AuthMiddleware, jwt_strategy=auth_backend.get_strategy())

app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)
app.include_router(
    project_router,
    prefix="/projects",
    tags=["projects"],
)
app.include_router(
    worksite_router,
    prefix="/worksites",
    tags=["worksites"],
)
app.include_router(
    zone_router,
    prefix="/zones",
    tags=["zones"],
)
