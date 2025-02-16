from typing import TYPE_CHECKING
from uuid import UUID
from sqlalchemy import Mapped, mapped_column, Uuid, String, select, update, delete, Integer
from app.db.base import Base
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.schemas.employees import EmployeeCreate, EmployeeUpdate

import uuid

class Employee(Base):
    __tablename__ = "employees"
    if TYPE_CHECKING:
        id: int
        first_name: str
        last_name: str
        phone: int
        role: str
        organization: str
    else:
        id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
        first_name: Mapped[str] = mapped_column(String(length=36), nullable=False)
        last_name: Mapped[str] = mapped_column(String(length=36), nullable=False)
        phone: Mapped[int] = mapped_column(Integer, nullable=False)
        role: Mapped[str] = mapped_column(String(length=36), nullable=True)
        organization: Mapped[str] = mapped_column(String(length=36), nullable=True)

class SQLAlchemyEmployeeDatabase:
    """
    Database adapter for SQLAlchemy

    :param session: SQLAlchemy session instance.
    :param employee_table: SQLAlchemy employee model.
    """

    session: AsyncSession

    def __init__(self, session: AsyncSession, employee_table):
        self.session = session
        self.worksite_table = employee_table

    async def get(self, employee_id: UUID):
        statement = select(self.employee_table).where(
            self.employee_table.id == employee_id
        )
        results = await self.session.execute(statement)

    async def create(self, employee_create: EmployeeCreate) -> Employee:
        employee = self.employee_table(**employee_create.model_dump())
        try:
            self.session.add(employee)
            await self.session.commit()
            await self.session.refresh(employee)
        except Exception as e:
            await self.session.rollback()
            return None
        return employee

    async def update(self, employee_id: str, employee_update: EmployeeUpdate):
        statement = (
            update(self.employee_table)
            .where(self.employee_table.id == employee_id)
            .values(**employee_update.model_dump())
        )
        await self.session.execute(statement)
        await self.session.commit()

    async def delete(self, employee_id: str):
        statement = delete(self.employee_table).where(
            self.employee_table.id == employee_id
        )
        result = await self.session.execute(statement)
        await self.session.commit()
        if result.rowcount == 0:
            return False
        return True
