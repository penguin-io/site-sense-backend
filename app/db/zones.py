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

    async def get_by_worksite(self, worksite_id: int):
        statement = select(self.zone_table).where(
            self.zone_table.worksite_id == worksite_id
        )
        results = await self.session.execute(statement)
        return results.scalars().fetchall()

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
