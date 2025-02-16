from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.db.employees import SQLAlchemyEmployeeDatabase, Employee
from app.manager.employees import EmployeeManager

from uuid import UUID

engine = create_async_engine("sqlite+aiosqlite:///./test.db")
async_session_factory = async_sessionmaker(engine, expire_on_commit=False)

employee_manager = None


async def initialize_employee_manager():
    global employee_manager_instance
    async with async_session_factory() as session:
        employee_db = SQLAlchemyEmployeeDatabase(session, Employee)
        employee_manager_instance = EmployeeManager(employee_db)
