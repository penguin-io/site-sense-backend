from typing import List
from uuid import UUID

from fastapi import Depends

from app.db.projects import Project, get_project_db, Worksite
from app.schemas.projects import ProjectCreate, ProjectUpdate

SECRET = "SECRET"


class ProjectManager:
    def __init__(self, project_table):
        self.project_table = project_table

    verification_token_secret = SECRET

    async def get(self, project_id: UUID) -> Project:
        """
        Fetch a project by its id

        :param project_id: The id of the project
        :return: The requested project
        """
        project = await self.project_table.get(project_id)
        return project

    async def get_all(self) -> List[Project]:
        """
        Fetch all projects

        :return: List of projects
        """
        projects = await self.project_table.get_all()
        return projects

    async def get_worksites(self, project_id: UUID) -> List[Worksite]:
        """
        Fetch all worksites for a project

        :param project_id: The id of the project
        :return: List of worksites for the project
        """
        worksites = await self.project_table.get_worksites(project_id)
        return worksites

    async def create(self, project_create: ProjectCreate) -> Project:
        """
        Create a new project
        :param project_create: The project to create
        :return: The created project, None if an error occurred
        """
        project = await self.project_table.create(project_create)
        if project is None:
            raise Exception("Error creating project")
        return project

    async def update(self, project_id: UUID, project_update: ProjectUpdate) -> Project:
        """
        Update an existing project
        :param project_id: The id of the target project
        :param project_update: The updated project
        :return: The updated project
        """
        await self.project_table.update(project_id, project_update)
        project = await self.project_table.get(project_id)
        return project

    async def delete(self, project_id: UUID):
        """
        Delete a project
        :param project_id: The id of the project to delete
        :return: success - True if the project was deleted, False otherwise
        """
        result = await self.project_table.delete(project_id)
        return result


async def get_project_manager(project_table=Depends(get_project_db)):
    yield ProjectManager(project_table)
