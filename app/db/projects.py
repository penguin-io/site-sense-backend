from typing import TYPE_CHECKING, AsyncGenerator, List

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase, relationship
from sqlalchemy import Text, String, DateTime, select, Uuid, delete, update, Integer, ForeignKey
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
        worksites: Mapped[List["Worksite"]] = relationship(back_populates="project")

class Worksite(Base):
    """SQLAlchemy worksite table definition."""

    __tablename__ = "worksites"
    if TYPE_CHECKING:
        id: int
        name: str
        description: str
        created_time: datetime
    else:
        id: Mapped[int] =  mapped_column(Integer, primary_key=True, autoincrement=True)
        name: Mapped[str] = mapped_column(
            String(length=64), index=True, nullable=False
        )
        description: Mapped[str] = mapped_column(Text(length=512), nullable=True)
        created_time: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.now(timezone.utc), nullable=False
        )
        project: Mapped["Project"] = relationship(back_populates="worksites")
        project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"), index=True, nullable=False)
        zones: Mapped[List["Zone"]] = relationship(back_populates="worksite")

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
        id: Mapped[int] =  mapped_column(Integer, primary_key=True, autoincrement=True)
        name: Mapped[str] = mapped_column(
            String(length=64), index=True, nullable=False
        )
        description: Mapped[str] = mapped_column(Text(length=512), nullable=True)
        created_time: Mapped[datetime] = mapped_column(
            DateTime, default=datetime.now(timezone.utc), nullable=False
        )
        feed_uri: Mapped[str] = mapped_column(Text(length=512), nullable=True)
        worksite: Mapped["Worksite"] = relationship(back_populates="zones")
        worksite_id: Mapped[int] = mapped_column(ForeignKey("worksites.id"), index=True, nullable=False)
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

    async def get(self, worksite_id: int):
        statement = select(self.worksite_table).where(
            self.worksite_table.id == worksite_id
        )
        results = await self.session.execute(statement)
        return results.unique().scalar_one_or_none()

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

    async def update(self, worksite_id: str, worksite_update: WorksiteUpdate):
        statement = (
            update(self.worksite_table)
            .where(self.worksite_table.id == worksite_id)
            .values(**worksite_update.model_dump())
        )
        await self.session.execute(statement)
        await self.session.commit()

    async def delete(self, worksite_id: str):
        statement = delete(self.worksite_table).where(
            self.worksite_table.id == worksite_id
        )
        result = await self.session.execute(statement)
        await self.session.commit()
        if result.rowcount == 0:
            return False
        return True

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
        statement = select(self.zone_table).where(
            self.zone_table.id == zone_id
        )
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
        statement = delete(self.zone_table).where(
            self.zone_table.id == zone_id
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

async def get_worksite_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyWorksiteDatabase(session, Worksite)

async def get_zone_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyZoneDatabase(session, Zone)
