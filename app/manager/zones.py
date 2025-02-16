from fastapi import Depends
from app.db.projects import Zone
from app.db.worksites import get_worksite_db
from app.db.zones import get_zone_db
from app.schemas.zones import ZoneCreate, ZoneUpdate
from app.exceptions import InvalidWorksiteError
from uuid import UUID
import subprocess


class ZoneManager:
    def __init__(self, zone_table, worksite_table):
        self.zone_table = zone_table
        self.worksite_table = worksite_table

    async def get(self, zone_id: UUID) -> Zone:
        """
        Fetch a zone by its id

        :param zone_id: The id of the zone
        :return: The requested zone
        """
        zone = await self.zone_table.get(zone_id)
        return zone

    async def create(self, zone_create: ZoneCreate) -> Zone:
        """
        Create a new zone
        :param zone_create: The zone to create
        :return: The created zone, None if an error occurred
        """
        worksite = await self.worksite_table.get(zone_create.worksite_id)
        if worksite is None:
            raise InvalidWorksiteError
        zone = await self.zone_table.create(zone_create)
        if zone is None:
            raise Exception("Error creating zone")
        return zone

    async def update(self, zone_id: UUID, zone_update: ZoneUpdate) -> Zone:
        """
        Update an existing zone
        :param zone_id: The id of the target zone
        :param zone_update: The updated zone
        :return: The updated zone
        """
        await self.zone_table.update(zone_id, zone_update)
        zone = await self.zone_table.get(zone_id)
        return zone

    async def delete(self, zone_id: UUID):
        """
        Delete a zone
        :param zone_id: The id of the zone to delete
        :return: success - True if the zone was deleted, False otherwise
        """
        result = await self.zone_table.delete(zone_id)
        return result

    async def begin_stream(self, zone_id: UUID):
        try:
            result = await self.zone_table.begin_stream(zone_id)
            return result
        except Exception as e:
            print(e)
            return False


async def get_zone_manager(
    zone_table=Depends(get_zone_db), worksite_table=Depends(get_worksite_db)
):
    yield ZoneManager(zone_table, worksite_table)
