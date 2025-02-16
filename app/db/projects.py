from typing import TYPE_CHECKING, AsyncGenerator, List

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase, relationship
from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy
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
    Boolean,
    Float,
)
from datetime import datetime, timezone
from fastapi import Depends
from uuid import UUID, uuid4

from app.schemas.projects import ProjectCreate, ProjectUpdate
from app.schemas.worksites import WorksiteCreate, WorksiteUpdate
from app.schemas.zones import ZoneCreate, ZoneUpdate
from app.db.base import Base


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
            cascade="all, delete, delete-orphan",
            passive_deletes=False,
            lazy="joined",
        )
        worksite_ids: AssociationProxy[List[UUID]] = association_proxy(
            "worksites", "id"
        )
        users: Mapped[List["User"]] = relationship(
            secondary="project_association",
            back_populates="projects",
        )
        location: Mapped[str] = mapped_column(String(length=36), nullable=True)


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
        project: Mapped["Project"] = relationship(
            back_populates="worksites", lazy="joined"
        )
        project_id: Mapped[UUID] = mapped_column(
            ForeignKey("projects.id", ondelete="CASCADE"), index=True, nullable=False
        )
        zones: Mapped[List["Zone"]] = relationship(
            back_populates="worksite",
            cascade="all, delete, delete-orphan",
            passive_deletes=False,
        )
        users: Mapped[List["User"]] = relationship(
            secondary="worksite_association",
            back_populates="worksites",
        )
        status: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
        lat: Mapped[float] = mapped_column(Float, nullable=True)
        long: Mapped[float] = mapped_column(Float, nullable=True)


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
        id: Mapped[UUID] = mapped_column(
            Uuid, primary_key=True, unique=True, index=True, default=uuid4
        )
        name: Mapped[str] = mapped_column(String(length=64), index=True, nullable=False)
        description: Mapped[str] = mapped_column(Text(length=512), nullable=True)
        created_time: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.now(timezone.utc), nullable=False
        )
        feed_uri: Mapped[str] = mapped_column(Text(length=512), nullable=True)
        worksite: Mapped["Worksite"] = relationship(
            back_populates="zones", lazy="joined"
        )
        worksite_id: Mapped[UUID] = mapped_column(
            ForeignKey("worksites.id", ondelete="CASCADE"), index=True, nullable=False
        )
        location: Mapped[str] = mapped_column(String(length=36), nullable=True)

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
        return results.unique().scalars().all()

    async def create(self, project_create: ProjectCreate) -> Project:
        project = self.project_table(**project_create.model_dump())
        try:
            self.session.add(project)
            await self.session.commit()
            await self.session.refresh(project)
        except Exception as e:
            print(e)
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
