from fastapi import Depends, Request
from app.db.projects import Project, get_project_db
from app.schemas.projects import ProjectCreate

SECRET = "SECRET"


class ProjectManager:
    def __init__(self, project_table):
        self.project_table = project_table

    verification_token_secret = SECRET

    async def get(self, project_id) -> Project:
        """
        Fetch a project by its id

        :param project_id: The id of the project
        :raises InvalidProjectException: The project doesn't doesnt
        :return: The requested project
        """
        project = await self.project_table.get(project_id)
        return project

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

    async def delete(self, project_id):
        """
        Delete a project
        :param project_id: The id of the project to delete
        :return: success - True if the project was deleted, False otherwise
        """
        result = await self.project_table.delete(project_id)
        return result


async def get_project_manager(project_table=Depends(get_project_db)):
    yield ProjectManager(project_table)
