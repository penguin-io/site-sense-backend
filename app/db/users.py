from sqlalchemy import select
from typing import TYPE_CHECKING, List
from collections.abc import AsyncGenerator

from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from fastapi_users.db import SQLAlchemyUserDatabase as SQLAlchemyUserDatabaseX
from sqlalchemy import String, Column, ForeignKey, Table
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy

from app.db.projects import Project, Worksite
from app.db.base import Base

import os
from dotenv import load_dotenv
from uuid import UUID
import casbin

load_dotenv()
DATABASE_URL = os.getenv("DB_URL")


project_association = Table(
    "project_association",
    Base.metadata,
    Column("user", ForeignKey("user.id"), primary_key=True),
    Column("project", ForeignKey("projects.id"), primary_key=True),
)
worksite_association = Table(
    "worksite_association",
    Base.metadata,
    Column("user", ForeignKey("user.id"), primary_key=True),
    Column("worksite", ForeignKey("worksites.id"), primary_key=True),
)


class User(SQLAlchemyBaseUserTableUUID, Base):
    if TYPE_CHECKING:
        username: str
    else:
        username: Mapped[str] = mapped_column(
            String(length=24), unique=True, index=True, nullable=False
        )
        role: Mapped[str] = mapped_column(
            String(length=24), nullable=False, default="wadmin"
        )
        organization: Mapped[str] = mapped_column(String(length=24), nullable=True)
        projects: Mapped[List[Project]] = relationship(
            lazy="joined", secondary=project_association, back_populates="users"
        )
        worksites: Mapped[List[Worksite]] = relationship(
            lazy="joined", secondary=worksite_association, back_populates="users"
        )

        project_ids: AssociationProxy[List[UUID]] = association_proxy("projects", "id")
        worksite_ids: AssociationProxy[List[UUID]] = association_proxy(
            "worksites", "id"
        )


class SQLAlchemyUserDatabase(SQLAlchemyUserDatabaseX):
    """Database adapter for SQLAlchemy."""

    async def set_access(self, access_request):
        enforcer = casbin.Enforcer("rbac_model.conf", "rbac_policy.csv")
        try:
            user = await self.get(access_request.user_id)
            resources = None
            target = None
            if access_request.resource_type == "project":
                resources = await self.session.execute(
                    select(Project).where(Project.id.in_(access_request.resource_ids))
                )
                target = user.projects
            else:
                resources = await self.session.execute(
                    select(Worksite).where(Worksite.id.in_(access_request.resource_ids))
                )
                target = user.worksites
            resources = resources.scalars().all()
            if access_request.access == "allow":
                for r in resources:
                    if not r in target:
                        target.append(r)
                        enforcer.add_policy(
                            user.username,
                            "/" + access_request.resource_type + "s/" + str(r.id) + "*",
                            "*",
                        )
            else:
                for r in resources:
                    if r in target:
                        target.remove(r)
                        enforcer.remove_policy(
                            user.username,
                            "/" + access_request.resource_type + "s/" + str(r.id) + "*",
                            "*",
                        )
            enforcer.save_policy()
            await self.session.commit()
            await self.session.refresh(user)
        except Exception as e:
            print(e)
            return None

    async def get_by_username(self, username: str) -> User:
        statement = select(User).where(User.username == username)
        results = await self.session.execute(statement)
        return results.unique().scalar_one_or_none()


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
