from fastapi import Depends
from app.db.projects import Worksite, get_project_db
from app.db.worksites import get_worksite_db
from app.exceptions import InvalidProjectError
from app.schemas.worksites import WorksiteCreate, WorksiteUpdate
from uuid import UUID


class WorksiteManager:
    def __init__(self, worksite_table, project_table):
        self.worksite_table = worksite_table
        self.project_table = project_table

    async def get(self, worksite_id: UUID) -> Worksite:
        """
        Fetch a worksite by its id

        :param worksite_id: The id of the worksite
        :return: The requested worksite
        """
        worksite = await self.worksite_table.get(worksite_id)
        return worksite

    async def create(self, worksite_create: WorksiteCreate) -> Worksite:
        """
        Create a new worksite
        :param worksite_create: The worksite to create
        :return: The created worksite, None if an error occurred
        """
        project = await self.project_table.get(worksite_create.project_id)
        if project is None:
            raise InvalidProjectError
        worksite = await self.worksite_table.create(worksite_create)
        if worksite is None:
            raise Exception("Error creating worksite")
        return worksite

    async def update(
        self, worksite_id: UUID, worksite_update: WorksiteUpdate
    ) -> Worksite:
        """
        Update an existing worksite
        :param worksite_id: The id of the target worksite
        :param worksite_update: The updated worksite
        :return: The updated worksite
        """
        await self.worksite_table.update(worksite_id, worksite_update)
        worksite = await self.worksite_table.get(worksite_id)
        return worksite

    async def delete(self, worksite_id: UUID):
        """
        Delete a worksite
        :param worksite_id: The id of the worksite to delete
        :return: success - True if the worksite was deleted, False otherwise
        """
        result = await self.worksite_table.delete(worksite_id)
        return result


async def get_worksite_manager(
    worksite_table=Depends(get_worksite_db), project_table=Depends(get_project_db)
):
    yield WorksiteManager(worksite_table, project_table)
