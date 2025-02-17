from uuid import UUID

from casbin.enforcer import Enforcer
from fastapi_users.authentication import JWTStrategy
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_403_FORBIDDEN
from starlette.types import ASGIApp, Receive, Scope, Send

from app.db.projects import SQLAlchemyProjectDatabase, Project
from app.db.users import SQLAlchemyUserDatabase, User
from app.db.worksites import Worksite, SQLAlchemyWorksiteDatabase
from app.db.zones import SQLAlchemyZoneDatabase, Zone
from app.manager.projects import ProjectManager
from app.manager.users import UserManager
from app.manager.worksites import WorksiteManager
from app.manager.zones import ZoneManager

engine = create_async_engine("sqlite+aiosqlite:///./test.db")
async_session_factory = async_sessionmaker(engine, expire_on_commit=False)


project_manager_instance = None
user_manager_instance = None
worksite_manager_instance = None
zone_manager_instance = None


async def initialize_user_manager():
    global user_manager_instance
    async with async_session_factory() as session:
        user_db = SQLAlchemyUserDatabase(session, User)
        user_manager_instance = UserManager(user_db)


async def initialize_project_manager():
    global project_manager_instance
    async with async_session_factory() as session:
        project_db = SQLAlchemyProjectDatabase(session, Project)
        project_manager_instance = ProjectManager(project_db)


async def initialize_worksite_manager():
    global worksite_manager_instance
    async with async_session_factory() as session:
        worksite_db = SQLAlchemyWorksiteDatabase(session, Worksite)
        project_db = SQLAlchemyProjectDatabase(session, Project)
        worksite_manager_instance = WorksiteManager(worksite_db, project_db)


async def initialize_zone_manager():
    global zone_manager_instance
    async with async_session_factory() as session:
        zone_db = SQLAlchemyZoneDatabase(session, Zone)
        worksite_db = SQLAlchemyWorksiteDatabase(session, Worksite)
        zone_manager_instance = ZoneManager(zone_db, worksite_db)


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

        if (await self._enforce(scope, receive)) or scope["method"] == "OPTIONS":
            await self.app(scope, receive, send)
            return
        else:
            response = JSONResponse(status_code=HTTP_403_FORBIDDEN, content="Forbidden")

            await response(scope, receive, send)
            return

    async def _enforce(self, scope: Scope, receive: Receive) -> bool:
        """
        Enforce a request

        :param user: user will be sent to enforcer
        :param request: ASGI Request
        :return: Enforce Result
        """

        self.enforcer.load_policy()
        request = Request(scope, receive)

        path = request.url.path
        method = request.method
        try:
            user = request.state.user
        except:
            user = "anonymous"

        if path.startswith("/users/"):
            return True

        if path.startswith("/projects/"):
            if not self.enforcer.enforce(user, path, method):
                project_id = path.split("/")[2]
                if project_id == "":
                    return self.enforcer.enforce(user, path, method)
                project_id = UUID(project_id)
                if project_manager_instance is None:
                    await initialize_project_manager()
                project = await project_manager_instance.get(project_id)
                if project is None:
                    return None
                if user == "anonymous":
                    return False
                user = await user_manager_instance.get_by_username(user)
                if project.id in user.project_ids:
                    return True

        if path.startswith("/worksites/"):
            if not self.enforcer.enforce(user, path, method):
                worksite_id = path.split("/")[2]
                if worksite_id == "":
                    return self.enforcer.enforce(user, path, method)
                worksite_id = UUID(worksite_id)
                if worksite_manager_instance is None:
                    await initialize_worksite_manager()
                worksite = await worksite_manager_instance.get(worksite_id)
                if worksite is None:
                    return None
                if user == "anonymous":
                    return False
                user = await user_manager_instance.get_by_username(user)
                project_ids = user.project_ids
                if worksite.project_id not in project_ids:
                    return None
                return True

        if path.startswith("/zones/camera") or path.startswith("/zones/hls"):
            return True

        if path.startswith("/zones/"):
            zone_id = path.split("/")[2]
            if zone_id == "":
                return self.enforcer.enforce(user, path, method)
            if zone_manager_instance is None:
                await initialize_zone_manager()
            zone_id = UUID(zone_id)
            zone = await zone_manager_instance.get(zone_id)
            if zone is None:
                return None
            if user == "admin":
                return True
            if user == "anonymous":
                return False
            user = await user_manager_instance.get_by_username(user)
            await user_manager_instance.user_db.session.refresh(user)
            print(user.project_ids, user.worksite_ids)
            if (
                zone.project_id in user.project_ids
                or zone.worksite_id in user.worksite_ids
            ):
                return True
            return False

        return self.enforcer.enforce(user, path, method)
