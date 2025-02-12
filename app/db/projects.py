from typing import TYPE_CHECKING, AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase
from sqlalchemy import Text, String, DateTime, select, Uuid, delete
from datetime import datetime, timezone
from fastapi import Depends
from uuid import UUID, uuid4

from app.schemas.projects import ProjectCreate


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
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_project_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyProjectDatabase(session, Project)
