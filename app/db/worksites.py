from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.projects import Worksite, get_async_session, Zone, Project
from app.db.users import User
from app.schemas.worksites import WorksiteCreate, WorksiteUpdate
from fastapi import Depends
from uuid import UUID
from app.db.employees import Employee, SQLAlchemyEmployeeDatabase


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

    async def get_all(self):
        statement = select(self.worksite_table)
        results = await self.session.execute(statement)
        return results.unique().scalars().all()

    async def get_accessible_worksites(self, user_id):
        response = set()
        statement = select(User).where(User.id == user_id)
        user = (await self.session.execute(statement)).unique().scalar_one_or_none()
        for project_id in user.project_ids:
            statement = select(Project).where(Project.id == project_id)
            project = (
                (await self.session.execute(statement)).unique().scalar_one_or_none()
            )
            for worksite_id in project.worksite_ids:
                worksite = await self.get(worksite_id)
                response.add(worksite)
        for worksite_id in user.worksite_ids:
            worksite = await self.get(worksite_id)
            response.add(worksite)
        return response

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


async def get_employee_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyEmployeeDatabase(session, Employee)
