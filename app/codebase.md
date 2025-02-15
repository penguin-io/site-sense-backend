# Tree View:
```
.
├─app.py
├─casbin.py
├─codebase.md
├─db
│ ├─projects.py
│ ├─users.py
│ ├─worksites.py
│ └─zones.py
├─exceptions.py
├─manager
│ ├─projects.py
│ ├─users.py
│ ├─worksites.py
│ └─zones.py
├─router
│ ├─__init__.py
│ ├─projects.py
│ ├─worksites.py
│ └─zones.py
└─schemas
  ├─projects.py
  ├─users.py
  ├─worksites.py
  └─zones.py
```

# Content:

## app.py
```py
from contextlib import asynccontextmanager

from fastapi import FastAPI

import casbin
from app.casbin import CasbinMiddleware, AuthMiddleware
from app.db.projects import create_project_db_and_tables
from app.db.users import create_user_db_and_tables
from app.manager.users import fastapi_users, auth_backend
from app.router import project_router, worksite_router, zone_router
from app.schemas.users import UserCreate, UserRead, UserUpdate


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Not needed if you setup a migration system like Alembic
    await create_user_db_and_tables()
    await create_project_db_and_tables()
    yield


enforcer = casbin.Enforcer("rbac_model.conf", "rbac_policy.csv")
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
# app.include_router(
#    fastapi_users.get_verify_router(UserRead),
#    prefix="/auth",
#    tags=["auth"],
# )
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

```

## casbin.py
```py
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

```

## codebase.md
```md
# Tree View:
```
.
├─app.py
├─casbin.py
├─codebase.md
├─db
│ ├─projects.py
│ ├─users.py
│ ├─worksites.py
│ └─zones.py
├─exceptions.py
├─manager
│ ├─projects.py
│ ├─users.py
│ ├─worksites.py
│ └─zones.py
├─router
│ ├─__init__.py
│ ├─projects.py
│ ├─worksites.py
│ └─zones.py
└─schemas
  ├─projects.py
  ├─users.py
  ├─worksites.py
  └─zones.py
```

# Content:

## app.py
```py
from contextlib import asynccontextmanager

from fastapi import FastAPI

import casbin
from app.casbin import CasbinMiddleware, AuthMiddleware
from app.db.projects import create_project_db_and_tables
from app.db.users import create_user_db_and_tables
from app.manager.users import fastapi_users, auth_backend
from app.router import project_router, worksite_router, zone_router
from app.schemas.users import UserCreate, UserRead, UserUpdate


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Not needed if you setup a migration system like Alembic
    await create_user_db_and_tables()
    await create_project_db_and_tables()
    yield


enforcer = casbin.Enforcer("rbac_model.conf", "rbac_policy.csv")
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
# app.include_router(
#    fastapi_users.get_verify_router(UserRead),
#    prefix="/auth",
#    tags=["auth"],
# )
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

```

## casbin.py
```py
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

```


```

## db/projects.py
```py
from typing import TYPE_CHECKING, AsyncGenerator, List

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase, relationship
from sqlalchemy import (
    Text,
    String,
    DateTime,
    select,
    Uuid,
    delete,
    update,
    Integer,
    ForeignKey,
)
from datetime import datetime, timezone
from fastapi import Depends
from uuid import UUID, uuid4

from app.schemas.projects import ProjectCreate, ProjectUpdate
from app.schemas.worksites import WorksiteCreate, WorksiteUpdate
from app.schemas.zones import ZoneCreate, ZoneUpdate


class Base(DeclarativeBase):
    pass


class Project(Base):
    """SQLAlchemy project table definition."""

    __tablename__ = "projects"
    if TYPE_CHECKING:
        id: UUID
        name: str
        description: str
        created_time: datetime
    else:
        id: Mapped[UUID] = mapped_column(
            Uuid, unique=True, primary_key=True, index=True, default=uuid4
        )
        name: Mapped[str] = mapped_column(
            String(length=64), unique=True, index=True, nullable=False
        )
        description: Mapped[str] = mapped_column(Text(length=512), nullable=True)
        created_time: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.now(timezone.utc), nullable=False
        )
        worksites: Mapped[List["Worksite"]] = relationship(
            back_populates="project",
            cascade="save-update, merge, delete, delete-orphan",
        )


class Worksite(Base):
    """SQLAlchemy worksite table definition."""

    __tablename__ = "worksites"
    if TYPE_CHECKING:
        id: UUID
        name: str
        description: str
        created_time: datetime
    else:
        id: Mapped[UUID] = mapped_column(
            Uuid, primary_key=True, unique=True, index=True, default=uuid4
        )
        name: Mapped[str] = mapped_column(String(length=64), index=True, nullable=False)
        description: Mapped[str] = mapped_column(Text(length=512), nullable=True)
        created_time: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.now(timezone.utc), nullable=False
        )
        project: Mapped["Project"] = relationship(back_populates="worksites")
        project_id: Mapped[UUID] = mapped_column(
            ForeignKey("projects.id", ondelete="CASCADE"), index=True, nullable=False
        )
        zones: Mapped[List["Zone"]] = relationship(
            back_populates="worksite",
            cascade="save-update, merge, delete, delete-orphan",
        )


class Zone(Base):
    """SQLAlchemy zone table definition."""

    __tablename__ = "zones"
    if TYPE_CHECKING:
        id: int
        name: str
        description: str
        created_time: datetime
        feed_uri: str
    else:
        id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
        name: Mapped[str] = mapped_column(String(length=64), index=True, nullable=False)
        description: Mapped[str] = mapped_column(Text(length=512), nullable=True)
        created_time: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.now(timezone.utc), nullable=False
        )
        feed_uri: Mapped[str] = mapped_column(Text(length=512), nullable=True)
        worksite: Mapped["Worksite"] = relationship(back_populates="zones")
        worksite_id: Mapped[int] = mapped_column(
            ForeignKey("worksites.id", ondelete="CASCADE"), index=True, nullable=False
        )

        @hybrid_property
        def project(self):
            return self.worksite.project

        @hybrid_property
        def project_id(self):
            return self.worksite.project_id


class SQLAlchemyProjectDatabase:
    """
    Database adapter for SQLAlchemy

    :param session: SQLAlchemy session instance.
    :param project_table: SQLAlchemy project model.
    """

    session: AsyncSession

    def __init__(self, session: AsyncSession, project_table):
        self.session = session
        self.project_table = project_table

    async def get(self, project_id: UUID):
        statement = select(self.project_table).where(
            self.project_table.id == project_id
        )
        results = await self.session.execute(statement)
        return results.unique().scalar_one_or_none()

    async def get_all(self):
        statement = select(self.project_table)
        results = await self.session.execute(statement)
        return results.scalars().all()

    async def get_worksites(self, project_id: UUID):
        statement = select(Worksite).where(Worksite.project_id == project_id)
        results = await self.session.execute(statement)
        return results.scalars().all()

    async def create(self, project_create: ProjectCreate) -> Project:
        project = self.project_table(**project_create.model_dump())
        try:
            self.session.add(project)
            await self.session.commit()
            await self.session.refresh(project)
        except Exception as e:
            await self.session.rollback()
            return None
        return project

    async def update(self, project_id: str, project_update: ProjectUpdate):
        statement = (
            update(self.project_table)
            .where(self.project_table.id == project_id)
            .values(**project_update.model_dump())
        )
        await self.session.execute(statement)
        await self.session.commit()

    async def delete(self, project_id: str):
        statement = delete(self.project_table).where(
            self.project_table.id == project_id
        )
        result = await self.session.execute(statement)
        await self.session.commit()
        if result.rowcount == 0:
            return False
        return True


DATABASE_URL = "sqlite+aiosqlite:///./test.db"
engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def create_project_db_and_tables():
    # creates worksite and zone db and tables too
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_project_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyProjectDatabase(session, Project)

```

## db/users.py
```py
from typing import TYPE_CHECKING
from collections.abc import AsyncGenerator

from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from sqlalchemy import String
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped

import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DB_URL")


class Base(DeclarativeBase):
    pass


class User(SQLAlchemyBaseUserTableUUID, Base):
    if TYPE_CHECKING:
        username: str
    else:
        username: Mapped[str] = mapped_column(
            String(length=24), unique=True, index=True, nullable=False
        )


engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def create_user_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)

```

## db/worksites.py
```py
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.projects import Worksite, get_async_session, Zone
from app.schemas.worksites import WorksiteCreate, WorksiteUpdate
from fastapi import Depends
from uuid import UUID


class SQLAlchemyWorksiteDatabase:
    """
    Database adapter for SQLAlchemy

    :param session: SQLAlchemy session instance.
    :param worksite_table: SQLAlchemy worksite model.
    """

    session: AsyncSession

    def __init__(self, session: AsyncSession, worksite_table):
        self.session = session
        self.worksite_table = worksite_table

    async def get(self, worksite_id: UUID):
        statement = select(self.worksite_table).where(
            self.worksite_table.id == worksite_id
        )
        results = await self.session.execute(statement)
        return results.unique().scalar_one_or_none()

    async def get_zones(self, worksite_id: UUID):
        statement = select(Zone).where(Zone.worksite_id == worksite_id)
        results = await self.session.execute(statement)
        return results.scalars().all()

    async def create(self, worksite_create: WorksiteCreate) -> Worksite:
        worksite = self.worksite_table(**worksite_create.model_dump())
        try:
            self.session.add(worksite)
            await self.session.commit()
            await self.session.refresh(worksite)
        except Exception as e:
            await self.session.rollback()
            return None
        return worksite

    async def update(self, worksite_id: UUID, worksite_update: WorksiteUpdate):
        statement = (
            update(self.worksite_table)
            .where(self.worksite_table.id == worksite_id)
            .values(**worksite_update.model_dump())
        )
        await self.session.execute(statement)
        await self.session.commit()

    async def delete(self, worksite_id: UUID):
        statement = delete(self.worksite_table).where(
            self.worksite_table.id == worksite_id
        )
        result = await self.session.execute(statement)
        await self.session.commit()
        if result.rowcount == 0:
            return False
        return True


async def get_worksite_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyWorksiteDatabase(session, Worksite)

```

## db/zones.py
```py
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.projects import Zone, get_async_session
from app.schemas.zones import ZoneCreate, ZoneUpdate
from fastapi import Depends


class SQLAlchemyZoneDatabase:
    """
    Database adapter for SQLAlchemy

    :param session: SQLAlchemy session instance.
    :param zone_table: SQLAlchemy zone model.
    """

    session: AsyncSession

    def __init__(self, session: AsyncSession, zone_table):
        self.session = session
        self.zone_table = zone_table

    async def get(self, zone_id: int):
        statement = select(self.zone_table).where(self.zone_table.id == zone_id)
        results = await self.session.execute(statement)
        return results.unique().scalar_one_or_none()

    async def create(self, zone_create: ZoneCreate) -> Zone:
        zone = self.zone_table(**zone_create.model_dump())
        try:
            self.session.add(zone)
            await self.session.commit()
            await self.session.refresh(zone)
        except Exception as e:
            await self.session.rollback()
            return None
        return zone

    async def update(self, zone_id: str, zone_update: ZoneUpdate):
        statement = (
            update(self.zone_table)
            .where(self.zone_table.id == zone_id)
            .values(**zone_update.model_dump())
        )
        await self.session.execute(statement)
        await self.session.commit()

    async def delete(self, zone_id: str):
        statement = delete(self.zone_table).where(self.zone_table.id == zone_id)
        result = await self.session.execute(statement)
        await self.session.commit()
        if result.rowcount == 0:
            return False
        return True


async def get_zone_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyZoneDatabase(session, Zone)

```

## exceptions.py
```py
from typing import Union, Dict
from enum import Enum
from pydantic import BaseModel


class InvalidProjectError(Exception):
    pass


class InvalidWorksiteError(Exception):
    pass


class ErrorModel(BaseModel):
    detail: Union[str, Dict[str, str]]


class ErrorCode(str, Enum):
    ADMIN_REQUIRED = "admin access required :("
    PROJECT_NOT_FOUND = "project not found :("
    PROJECT_NAME_EXISTS = "project with same name already exists :("
    WORKSITE_NOT_FOUND = "worksite not found :("
    ZONE_NOT_FOUND = "zone not found :("

```

## manager/projects.py
```py
from typing import List
from uuid import UUID

from fastapi import Depends

from app.db.projects import Project, get_project_db, Worksite
from app.schemas.projects import ProjectCreate, ProjectUpdate

SECRET = "SECRET"


class ProjectManager:
    def __init__(self, project_table):
        self.project_table = project_table

    verification_token_secret = SECRET

    async def get(self, project_id: UUID) -> Project:
        """
        Fetch a project by its id

        :param project_id: The id of the project
        :return: The requested project
        """
        project = await self.project_table.get(project_id)
        return project

    async def get_all(self) -> List[Project]:
        """
        Fetch all projects

        :return: List of projects
        """
        projects = await self.project_table.get_all()
        return projects

    async def get_worksites(self, project_id: UUID) -> List[Worksite]:
        """
        Fetch all worksites for a project

        :param project_id: The id of the project
        :return: List of worksites for the project
        """
        worksites = await self.project_table.get_worksites(project_id)
        return worksites

    async def create(self, project_create: ProjectCreate) -> Project:
        """
        Create a new project
        :param project_create: The project to create
        :return: The created project, None if an error occurred
        """
        project = await self.project_table.create(project_create)
        if project is None:
            raise Exception("Error creating project")
        return project

    async def update(self, project_id: UUID, project_update: ProjectUpdate) -> Project:
        """
        Update an existing project
        :param project_id: The id of the target project
        :param project_update: The updated project
        :return: The updated project
        """
        await self.project_table.update(project_id, project_update)
        project = await self.project_table.get(project_id)
        return project

    async def delete(self, project_id: UUID):
        """
        Delete a project
        :param project_id: The id of the project to delete
        :return: success - True if the project was deleted, False otherwise
        """
        result = await self.project_table.delete(project_id)
        return result


async def get_project_manager(project_table=Depends(get_project_db)):
    yield ProjectManager(project_table)

```

## manager/users.py
```py
import uuid
from typing import Optional

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin, models
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase

from app.db.users import User, get_user_db

import os
from dotenv import load_dotenv

load_dotenv()

SECRET = os.getenv("TOKEN_SECRET")


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy[models.UP, models.ID]:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)

```

## manager/worksites.py
```py
from typing import List
from fastapi import Depends
from app.db.projects import Worksite, get_project_db, Zone
from app.db.worksites import get_worksite_db
from app.exceptions import InvalidProjectError
from app.schemas.worksites import WorksiteCreate, WorksiteUpdate
from uuid import UUID


class WorksiteManager:
    def __init__(self, worksite_table, project_table):
        self.worksite_table = worksite_table
        self.project_table = project_table

    async def get(self, worksite_id: UUID) -> Worksite:
        """
        Fetch a worksite by its id

        :param worksite_id: The id of the worksite
        :return: The requested worksite
        """
        worksite = await self.worksite_table.get(worksite_id)
        return worksite

    async def get_zones(self, worksite_id: UUID) -> List[Zone]:
        """
        Fetch all zones for a worksite

        :param worksite_id: The id of the worksite
        :return: List of zones for the worksite
        """
        zones = await self.worksite_table.get_zones(worksite_id)
        return zones

    async def create(self, worksite_create: WorksiteCreate) -> Worksite:
        """
        Create a new worksite
        :param worksite_create: The worksite to create
        :return: The created worksite, None if an error occurred
        """
        project = await self.project_table.get(worksite_create.project_id)
        if project is None:
            raise InvalidProjectError
        worksite = await self.worksite_table.create(worksite_create)
        if worksite is None:
            raise Exception("Error creating worksite")
        return worksite

    async def update(
        self, worksite_id: UUID, worksite_update: WorksiteUpdate
    ) -> Worksite:
        """
        Update an existing worksite
        :param worksite_id: The id of the target worksite
        :param worksite_update: The updated worksite
        :return: The updated worksite
        """
        await self.worksite_table.update(worksite_id, worksite_update)
        worksite = await self.worksite_table.get(worksite_id)
        return worksite

    async def delete(self, worksite_id: UUID):
        """
        Delete a worksite
        :param worksite_id: The id of the worksite to delete
        :return: success - True if the worksite was deleted, False otherwise
        """
        result = await self.worksite_table.delete(worksite_id)
        return result


async def get_worksite_manager(
    worksite_table=Depends(get_worksite_db), project_table=Depends(get_project_db)
):
    yield WorksiteManager(worksite_table, project_table)

```

## manager/zones.py
```py
from fastapi import Depends
from app.db.projects import Zone
from app.db.worksites import get_worksite_db
from app.db.zones import get_zone_db
from app.schemas.zones import ZoneCreate, ZoneUpdate
from app.exceptions import InvalidWorksiteError
from uuid import UUID


class ZoneManager:
    def __init__(self, zone_table, worksite_table):
        self.zone_table = zone_table
        self.worksite_table = worksite_table

    async def get(self, zone_id: UUID) -> Zone:
        """
        Fetch a zone by its id

        :param zone_id: The id of the zone
        :return: The requested zone
        """
        zone = await self.zone_table.get(zone_id)
        return zone

    async def create(self, zone_create: ZoneCreate) -> Zone:
        """
        Create a new zone
        :param zone_create: The zone to create
        :return: The created zone, None if an error occurred
        """
        worksite = await self.worksite_table.get(zone_create.worksite_id)
        if worksite is None:
            raise InvalidWorksiteError
        zone = await self.zone_table.create(zone_create)
        if zone is None:
            raise Exception("Error creating zone")
        return zone

    async def update(self, zone_id: UUID, zone_update: ZoneUpdate) -> Zone:
        """
        Update an existing zone
        :param zone_id: The id of the target zone
        :param zone_update: The updated zone
        :return: The updated zone
        """
        await self.zone_table.update(zone_id, zone_update)
        zone = await self.zone_table.get(zone_id)
        return zone

    async def delete(self, zone_id: UUID):
        """
        Delete a zone
        :param zone_id: The id of the zone to delete
        :return: success - True if the zone was deleted, False otherwise
        """
        result = await self.zone_table.delete(zone_id)
        return result


async def get_zone_manager(
    zone_table=Depends(get_zone_db), worksite_table=Depends(get_worksite_db)
):
    yield ZoneManager(zone_table, worksite_table)

```

## router/__init__.py
```py
from app.manager.projects import get_project_manager
from app.manager.worksites import get_worksite_manager
from app.manager.zones import get_zone_manager
from .projects import get_project_router
from .worksites import get_worksite_router
from .zones import get_zone_router
from fastapi import APIRouter


class project_router:
    def __init__(self, get_project_manager):
        self.get_project_manager = get_project_manager

    def get_project_router(self):
        return get_project_router(self.get_project_manager)


class worksite_router:
    def __init__(self, get_worksite_manager):
        self.get_worksite_manager = get_worksite_manager

    def get_worksite_router(self):
        return get_worksite_router(self.get_worksite_manager)


class zone_router:
    def __init__(self, get_zone_manager):
        self.get_zone_manager = get_zone_manager

    def get_zone_router(self):
        return get_zone_router(self.get_zone_manager)


project_router = project_router(get_project_manager)
router = APIRouter()
router.include_router(project_router.get_project_router())
project_router = router

worksite_router = worksite_router(get_worksite_manager)
router = APIRouter()
router.include_router(worksite_router.get_worksite_router())
worksite_router = router

zone_router = zone_router(get_zone_manager)
router = APIRouter()
router.include_router(zone_router.get_zone_router())
zone_router = router

```

## router/projects.py
```py
from uuid import UUID

from fastapi import APIRouter, Depends, status, HTTPException

from app.db.users import User
from app.exceptions import ErrorCode, ErrorModel
from app.manager.users import current_active_user
from app.schemas.projects import ProjectCreate, ProjectRead, ProjectUpdate, ProjectsRead
from app.schemas.worksites import WorksitesRead


def get_project_router(get_project_manager) -> APIRouter:
    router = APIRouter()

    @router.get("/all", response_model=ProjectsRead, summary="Get all projects")
    async def get_all_projects(
        user=Depends(current_active_user), project_manager=Depends(get_project_manager)
    ):
        """
        This route returns all projects

        ### Response
        * projects (ProjectsRead): The projects list
        """
        projects = await project_manager.get_all()
        return projects

    @router.get(
        "/{project_id}",
        summary="Get a project by its id",
        responses={
            status.HTTP_404_NOT_FOUND: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            ErrorCode.PROJECT_NOT_FOUND: {
                                "value": {"detail": ErrorCode.PROJECT_NOT_FOUND}
                            }
                        }
                    }
                },
            },
        },
        response_model=ProjectRead,
    )
    async def get_project(
        project_id: UUID,
        project_manager=Depends(get_project_manager),
        user: User = Depends(current_active_user),
    ):
        """
        This route returns a project by its id
        ### Arguments
        * project_id: The id of the project

        ### Response
        * project (ProjectRead): The requested project

        ### Raises
        * HTTPException:
            * 404 Not found: If the project doesn't exist
        """
        project = await project_manager.get(project_id)
        if project is None:
            raise HTTPException(status_code=404, detail=ErrorCode.PROJECT_NOT_FOUND)
        return project

    @router.get(
        "/{project_id}/worksites",
        summary="Get all worksites of a project by its id",
        responses={
            status.HTTP_404_NOT_FOUND: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            ErrorCode.PROJECT_NOT_FOUND: {
                                "value": {"detail": ErrorCode.PROJECT_NOT_FOUND}
                            }
                        }
                    }
                },
            },
        },
        response_model=WorksitesRead,
    )
    async def get_worksites(
        project_id: UUID,
        project_manager=Depends(get_project_manager),
        user=Depends(current_active_user),
    ):
        """
        This route returns all worksites of a project by its id
        ### Arguments
        * project_id: The id of the project

        ### Response
        * worksites (WorksitesRead): The worksites of the requested project

        ### Raises
        * HTTPException:
            * 404 Not found: If the project doesn't exist
        """
        worksites = await project_manager.get_worksites(project_id)
        if worksites is None:
            raise HTTPException(status_code=404, detail=ErrorCode.PROJECT_NOT_FOUND)
        return worksites

    @router.post(
        "/",
        summary="Create a new project",
        response_model=ProjectRead,
        status_code=status.HTTP_201_CREATED,
        responses={
            status.HTTP_422_UNPROCESSABLE_ENTITY: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            ErrorCode.PROJECT_NAME_EXISTS: {
                                "value": {"detail": ErrorCode.PROJECT_NAME_EXISTS}
                            },
                        }
                    }
                },
            },
        },
    )
    async def create_project(
        project: ProjectCreate,
        user: User = Depends(current_active_user),
        project_manager=Depends(get_project_manager),
    ):
        """
        This route creates a new project
        ### Arguments
        * project (ProjectCreate): The project to create

        ### Response
        * project (ProjectRead): The created project

        ### Raises
        * HTTPException:
            * 422 Unprocessable Entity: If the project name already exists
        """
        try:
            project = await project_manager.create(project)
        except Exception as e:
            raise HTTPException(status_code=422, detail=ErrorCode.PROJECT_NAME_EXISTS)
        return project

    @router.patch(
        "/{project_id}", summary="Update a project", response_model=ProjectRead
    )
    async def update_project(
        project_id: UUID,
        project: ProjectUpdate,
        user: User = Depends(current_active_user),
        project_manager=Depends(get_project_manager),
    ):
        """
        This route updates a project

        ### Arguments
        * project_id: The id of the project to update
        * project (ProjectUpdate): The project to update

        ### Response
        * project (ProjectRead): The updated project

        ### Raises
        * HTTPException:
            * 404 Not found: If the project doesn't exist
        """
        project = await project_manager.update(project_id, project)
        if project is None:
            raise HTTPException(status_code=404, detail=ErrorCode.PROJECT_NOT_FOUND)
        return project

    @router.delete(
        "/{project_id}",
        summary="Delete a project",
        status_code=status.HTTP_204_NO_CONTENT,
        responses={
            status.HTTP_404_NOT_FOUND: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            ErrorCode.PROJECT_NOT_FOUND: {
                                "value": {"detail": ErrorCode.PROJECT_NOT_FOUND}
                            }
                        }
                    }
                },
            },
        },
    )
    async def delete_project(
        project_id: UUID,
        user: User = Depends(current_active_user),
        project_manager=Depends(get_project_manager),
    ):
        """
        This route deletes a project
        ### Arguments
        * project_id: The id of the project to delete

        ### Raises
        * HTTPException:
            * 404 Not found: If the project doesn't exist
        """
        result = await project_manager.delete(project_id)
        if not result:
            raise HTTPException(status_code=404, detail=ErrorCode.PROJECT_NOT_FOUND)

    return router

```

## router/worksites.py
```py
from fastapi import APIRouter, Depends, status, HTTPException
from app.manager.users import current_active_user
from app.schemas.worksites import WorksiteRead, WorksiteCreate, WorksiteUpdate
from app.schemas.zones import ZonesRead
from app.db.users import User
from app.exceptions import ErrorCode, ErrorModel, InvalidProjectError
from uuid import UUID


def get_worksite_router(get_worksite_manager) -> APIRouter:
    router = APIRouter()

    @router.get(
        "/{worksite_id}",
        summary="Get a worksite by its id",
        responses={
            status.HTTP_404_NOT_FOUND: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            ErrorCode.WORKSITE_NOT_FOUND: {
                                "value": {"detail": ErrorCode.WORKSITE_NOT_FOUND}
                            }
                        }
                    }
                },
            },
        },
        response_model=WorksiteRead,
    )
    async def get_worksite(
        worksite_id: UUID,
        worksite_manager=Depends(get_worksite_manager),
        user: User = Depends(current_active_user),
    ):
        """
        This route returns a worksite by its id
        ### Arguments
        * worksite_id: The id of the worksite

        ### Response
        * worksite (WorksiteRead): The requested worksite

        ### Raises
        * HTTPException:
            * 404 Not found: If the worksite doesn't exist
        """
        worksite = await worksite_manager.get(worksite_id)
        if worksite is None:
            raise HTTPException(status_code=404, detail=ErrorCode.WORKSITE_NOT_FOUND)
        return worksite

    @router.get(
        "/{worksite_id}/zones}",
        response_model=ZonesRead,
        summary="Get all zones of a worksite",
        responses={
            status.HTTP_404_NOT_FOUND: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            ErrorCode.WORKSITE_NOT_FOUND: {
                                "value": {"detail": ErrorCode.WORKSITE_NOT_FOUND}
                            }
                        }
                    }
                },
            },
        },
    )
    async def get_zones(
        worksite_id: UUID,
        user: User = Depends(current_active_user),
        worksite_manager=Depends(get_worksite_manager),
    ):
        """
        This route returns all zones of a worksite

        ### Arguments
        * worksite_id: The id of the worksite

        ### Response
        * zones (ZonesRead): The zones of the requested worksite

        ### Raises
        * HTTPException:
            * 404 Not found: If the worksite doesn't exist
        """
        zones = await worksite_manager.get_zones(worksite_id)
        if zones is None:
            raise HTTPException(status_code=404, detail=ErrorCode.WORKSITE_NOT_FOUND)
        return zones

    @router.post(
        "/",
        summary="Create a new worksite",
        response_model=WorksiteRead,
        status_code=status.HTTP_201_CREATED,
    )
    async def create_worksite(
        worksite: WorksiteCreate,
        user: User = Depends(current_active_user),
        worksite_manager=Depends(get_worksite_manager),
    ):
        """
        This route creates a new worksite
        ### Arguments
        * worksite (WorksiteCreate): The worksite to create

        ### Response
        * worksite (WorksiteRead): The created worksite
        """
        try:
            worksite = await worksite_manager.create(worksite)
        except InvalidProjectError:
            raise HTTPException(status_code=422, detail=ErrorCode.PROJECT_NOT_FOUND)
        return worksite

    @router.patch(
        "/{worksite_id}",
        summary="Update a worksite",
        response_model=WorksiteRead,
        responses={
            status.HTTP_404_NOT_FOUND: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            ErrorCode.WORKSITE_NOT_FOUND: {
                                "value": {"detail": ErrorCode.WORKSITE_NOT_FOUND}
                            }
                        }
                    }
                },
            },
        },
    )
    async def update_worksite(
        worksite_id: UUID,
        worksite: WorksiteUpdate,
        user: User = Depends(current_active_user),
        worksite_manager=Depends(get_worksite_manager),
    ):
        """
        This route updates a worksite

        ### Arguments
        * worksite_id: The id of the worksite to update

        ### Response
        * worksite (WorksiteRead): The updated worksite

        ### Raises
        * HTTPException:
            * 404 Not found: If the worksite doesn't exist
        """
        if not user.is_superuser:
            raise HTTPException(status_code=403, detail=ErrorCode.ADMIN_REQUIRED)
        worksite = await worksite_manager.update(worksite_id, worksite)
        if worksite is None:
            raise HTTPException(status_code=404, detail=ErrorCode.WORKSITE_NOT_FOUND)
        return worksite

    @router.delete(
        "/{worksite_id}",
        summary="Delete a worksite",
        status_code=status.HTTP_204_NO_CONTENT,
        responses={
            status.HTTP_404_NOT_FOUND: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            ErrorCode.WORKSITE_NOT_FOUND: {
                                "value": {"detail": ErrorCode.WORKSITE_NOT_FOUND}
                            }
                        }
                    }
                },
            },
        },
    )
    async def delete_worksite(
        worksite_id: UUID,
        user: User = Depends(current_active_user),
        worksite_manager=Depends(get_worksite_manager),
    ):
        """
        This route deletes a worksite
        ### Arguments
        * worksite_id: The id of the worksite to delete

        ### Raises
        * HTTPException:
            * 404 Not found: If the worksite doesn't exist
        """
        result = await worksite_manager.delete(worksite_id)
        if not result:
            raise HTTPException(status_code=404, detail=ErrorCode.WORKSITE_NOT_FOUND)

    return router

```

## router/zones.py
```py
from fastapi import APIRouter, Depends, status, HTTPException
from app.manager.users import current_active_user
from app.schemas.zones import ZoneRead, ZoneCreate, ZoneUpdate
from app.db.users import User
from app.exceptions import ErrorCode, ErrorModel
from uuid import UUID


def get_zone_router(get_zone_manager) -> APIRouter:
    router = APIRouter()

    @router.get(
        "/{zone_id}",
        summary="Get a zone by its id",
        responses={
            status.HTTP_404_NOT_FOUND: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            ErrorCode.ZONE_NOT_FOUND: {
                                "value": {"detail": ErrorCode.ZONE_NOT_FOUND}
                            }
                        }
                    }
                },
            },
        },
        response_model=ZoneRead,
    )
    async def get_zone(
        zone_id: UUID,
        zone_manager=Depends(get_zone_manager),
    ):
        """
        This route returns a zone by its id
        ### Arguments
        * zone_id: The id of the zone

        ### Response
        * zone (ZoneRead): The requested zone

        ### Raises
        * HTTPException:
            * 404 Not found: If the zone doesn't exist
        """
        zone = await zone_manager.get(zone_id)
        if zone is None:
            raise HTTPException(status_code=404, detail=ErrorCode.ZONE_NOT_FOUND)
        return zone

    @router.post(
        "/",
        summary="Create a new zone",
        response_model=ZoneRead,
        status_code=status.HTTP_201_CREATED,
    )
    async def create_zone(
        zone: ZoneCreate,
        user: User = Depends(current_active_user),
        zone_manager=Depends(get_zone_manager),
    ):
        """
        This route creates a new zone
        ### Arguments
        * zone (ZoneCreate): The zone to create

        ### Response
        * zone (ZoneRead): The created zone
        """
        zone = await zone_manager.create(zone)
        return zone

    @router.patch(
        "/{zone_id}",
        summary="Update a zone",
        response_model=ZoneRead,
        responses={
            status.HTTP_404_NOT_FOUND: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            ErrorCode.ZONE_NOT_FOUND: {
                                "value": {"detail": ErrorCode.ZONE_NOT_FOUND}
                            }
                        }
                    }
                },
            },
        },
    )
    async def update_zone(
        zone_id: UUID,
        zone: ZoneUpdate,
        user: User = Depends(current_active_user),
        zone_manager=Depends(get_zone_manager),
    ):
        """
        This route updates a zone

        ### Arguments
        * zone_id: The id of the zone to update

        ### Response
        * zone (ZoneRead): The updated zone

        ### Raises
        * HTTPException:
            * 404 Not found: If the zone doesn't exist
        """
        zone = await zone_manager.update(zone_id, zone)
        if zone is None:
            raise HTTPException(status_code=404, detail=ErrorCode.ZONE_NOT_FOUND)
        return zone

    @router.delete(
        "/{zone_id}",
        summary="Delete a zone",
        status_code=status.HTTP_204_NO_CONTENT,
        responses={
            status.HTTP_404_NOT_FOUND: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            ErrorCode.ZONE_NOT_FOUND: {
                                "value": {"detail": ErrorCode.ZONE_NOT_FOUND}
                            }
                        }
                    }
                },
            },
        },
    )
    async def delete_zone(
        zone_id: UUID,
        user: User = Depends(current_active_user),
        zone_manager=Depends(get_zone_manager),
    ):
        """
        This route deletes a zone
        ### Arguments
        * zone_id: The id of the zone to delete

        ### Raises
        * HTTPException:
            * 404 Not found: If the zone doesn't exist
        """
        result = await zone_manager.delete(zone_id)
        if not result:
            raise HTTPException(status_code=404, detail=ErrorCode.ZONE_NOT_FOUND)

    return router

```

## schemas/projects.py
```py
from typing import Annotated, Optional, List
from pydantic import BaseModel, Field, RootModel
from datetime import datetime
from uuid import UUID


class ProjectCreate(BaseModel):
    name: Annotated[str, Field(min_length=3, max_length=64)]
    description: Optional[Annotated[str, Field(max_length=512)]] = None


class ProjectRead(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    created_time: datetime


class ProjectsRead(RootModel):
    root: List[ProjectRead]


class ProjectUpdate(BaseModel):
    description: str

```

## schemas/users.py
```py
from typing import Annotated
import uuid

from pydantic import Field
from fastapi_users import schemas


class UserRead(schemas.BaseUser[uuid.UUID]):
    username: str


class UserCreate(schemas.BaseUserCreate):
    username: Annotated[str, Field(min_length=3, max_length=24)]


class UserUpdate(schemas.BaseUserUpdate):
    pass

```

## schemas/worksites.py
```py
from typing import List, Annotated, Optional
from pydantic import BaseModel, RootModel, Field
from datetime import datetime
from uuid import UUID


class WorksiteCreate(BaseModel):
    name: Annotated[str, Field(min_length=3, max_length=64)]
    description: Optional[Annotated[str, Field(max_length=512)]] = None
    project_id: UUID


class WorksiteRead(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    created_time: datetime
    project_id: UUID


class WorksiteUpdate(BaseModel):
    description: Optional[Annotated[str, Field(max_length=512)]] = None


class WorksitesRead(RootModel):
    root: List[WorksiteRead]

```

## schemas/zones.py
```py
from typing import Optional, List, Annotated
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


class ZoneCreate(BaseModel):
    name: Annotated[str, Field(min_length=3, max_length=64)]
    description: Optional[Annotated[str, Field(max_length=512)]] = None
    feed_uri: Optional[Annotated[str, Field(max_length=512)]] = None
    worksite_id: UUID


class ZoneRead(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    created_time: datetime
    worksite_id: UUID
    project_id: UUID


class ZonesRead(BaseModel):
    root: List[ZoneRead]


class ZoneUpdate(BaseModel):
    description: Optional[Annotated[str, Field(max_length=512)]] = None
    feed_uri: Optional[Annotated[str, Field(max_length=512)]] = None

```

