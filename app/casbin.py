from casbin.enforcer import Enforcer
from fastapi_users.authentication import JWTStrategy
from starlette.authentication import BaseUser
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_403_FORBIDDEN
from starlette.types import ASGIApp, Receive, Scope, Send


from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from fastapi_users.db import SQLAlchemyUserDatabase
from app.db.users import User
from app.manager.users import UserManager

engine = create_async_engine("sqlite+aiosqlite:///./test.db")
async_session_factory = async_sessionmaker(engine, expire_on_commit=False)


user_manager_instance = None


async def initialize_user_manager():
    global user_manager_instance
    async with async_session_factory() as session:
        user_db = SQLAlchemyUserDatabase(session, User)
        user_manager_instance = UserManager(user_db)


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, jwt_strategy: JWTStrategy):
        super().__init__(app)
        self.jwt_strategy = jwt_strategy

    async def dispatch(self, request: Request, call_next):
        token = request.headers.get("Authorization")
        if token and token.startswith("Bearer "):
            token = token.split(" ")[1]
            global user_manager_instance
            if user_manager_instance is None:
                await initialize_user_manager()
            user = await self.jwt_strategy.read_token(token, user_manager_instance)
            if user:
                request.state.user = user.username
            else:
                request.state.user = "anonymous"
        else:
            request.state.user = "anonymous"
        return await call_next(request)


class CasbinMiddleware:
    """
    Middleware for Casbin
    """

    def __init__(
        self,
        app: ASGIApp,
        enforcer: Enforcer,
    ) -> None:
        """
        Configure Casbin Middleware

        :param app:Retain for ASGI.
        :param enforcer:Casbin Enforcer, must be initialized before FastAPI start.
        """
        self.app = app
        self.enforcer = enforcer

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        if self._enforce(scope, receive) or scope["method"] == "OPTIONS":
            await self.app(scope, receive, send)
            return
        else:
            response = JSONResponse(status_code=HTTP_403_FORBIDDEN, content="Forbidden")

            await response(scope, receive, send)
            return

    def _enforce(self, scope: Scope, receive: Receive) -> bool:
        """
        Enforce a request

        :param user: user will be sent to enforcer
        :param request: ASGI Request
        :return: Enforce Result
        """

        request = Request(scope, receive)

        path = request.url.path
        method = request.method
        try:
            user = request.state.user
        except:
            user = "anonymous"

        return self.enforcer.enforce(user, path, method)
