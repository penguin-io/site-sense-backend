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

from app.schemas.users import RoleReq, UserUpdate, AccessReq

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

    async def get_by_username(self, username: str) -> User:
        return await self.user_db.get_by_username(username)

    async def set_role(self, role_request: RoleReq):
        user = await self.get(role_request.user_id)
        if user is None:
            return None
        if user.role == role_request.role:
            return False
        user.role = role_request.role
        user_update = UserUpdate(**user.__dict__)
        await self.update(user_update, user)
        return True

    async def set_access(self, access_request: AccessReq):
        result = await self.user_db.set_access(access_request)
        return result
        # user = await self.get(access_request.user_id)
        # if user is None:
        #    return None
        # target = None
        # if access_request.resource_type == "project":
        #    result = await self.add_projects(user, access_request.resource_ids)
        # else:
        #    result = await self.add_worksites(user, access_request.resource_ids)
        # if access_request.access == "allow":
        #    target = access_request.resource_ids
        # else:  # deny
        #    for resource in access_request.resource_ids:
        #        target.remove(resource)


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
