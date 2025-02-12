from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI

from app.db.users import User, create_user_db_and_tables
from app.db.projects import create_project_db_and_tables
from app.schemas.users import UserCreate, UserRead, UserUpdate
from app.manager.users import auth_backend, current_active_user, fastapi_users
from app.router import project_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Not needed if you setup a migration system like Alembic
    await create_user_db_and_tables()
    await create_project_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

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
