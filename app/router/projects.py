from uuid import UUID

from fastapi import APIRouter, Depends, status, HTTPException

from app.db.users import User
from app.exceptions import ErrorCode, ErrorModel
from app.manager.users import current_active_user
from app.schemas.projects import ProjectCreate, ProjectRead, ProjectUpdate, ProjectsRead
from app.schemas.worksites import WorksitesRead


def get_project_router(get_project_manager) -> APIRouter:
    router = APIRouter()

    @router.get("/all", response_model=ProjectsRead, summary="Get all projects")
    async def get_all_projects(
        user=Depends(current_active_user), project_manager=Depends(get_project_manager)
    ):
        """
        This route returns all projects

        ### Response
        * projects (ProjectsRead): The projects list
        """
        projects = await project_manager.get_all()
        return projects

    @router.get(
        "/{project_id}",
        summary="Get a project by its id",
        responses={
            status.HTTP_404_NOT_FOUND: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            ErrorCode.PROJECT_NOT_FOUND: {
                                "value": {"detail": ErrorCode.PROJECT_NOT_FOUND}
                            }
                        }
                    }
                },
            },
        },
        response_model=ProjectRead,
    )
    async def get_project(
        project_id: UUID,
        project_manager=Depends(get_project_manager),
        user: User = Depends(current_active_user),
    ):
        """
        This route returns a project by its id
        ### Arguments
        * project_id: The id of the project

        ### Response
        * project (ProjectRead): The requested project

        ### Raises
        * HTTPException:
            * 404 Not found: If the project doesn't exist
        """
        project = await project_manager.get(project_id)
        if project is None:
            raise HTTPException(status_code=404, detail=ErrorCode.PROJECT_NOT_FOUND)
        return project

    @router.get(
        "/{project_id}/worksites",
        summary="Get all worksites of a project by its id",
        responses={
            status.HTTP_404_NOT_FOUND: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            ErrorCode.PROJECT_NOT_FOUND: {
                                "value": {"detail": ErrorCode.PROJECT_NOT_FOUND}
                            }
                        }
                    }
                },
            },
        },
        response_model=WorksitesRead,
    )
    async def get_worksites(
        project_id: UUID,
        project_manager=Depends(get_project_manager),
        user=Depends(current_active_user),
    ):
        """
        This route returns all worksites of a project by its id
        ### Arguments
        * project_id: The id of the project

        ### Response
        * worksites (WorksitesRead): The worksites of the requested project

        ### Raises
        * HTTPException:
            * 404 Not found: If the project doesn't exist
        """
        worksites = await project_manager.get_worksites(project_id)
        if worksites is None:
            raise HTTPException(status_code=404, detail=ErrorCode.PROJECT_NOT_FOUND)
        return worksites

    @router.post(
        "/",
        summary="Create a new project",
        response_model=ProjectRead,
        status_code=status.HTTP_201_CREATED,
        responses={
            status.HTTP_422_UNPROCESSABLE_ENTITY: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            ErrorCode.PROJECT_NAME_EXISTS: {
                                "value": {"detail": ErrorCode.PROJECT_NAME_EXISTS}
                            },
                        }
                    }
                },
            },
        },
    )
    async def create_project(
        project: ProjectCreate,
        user: User = Depends(current_active_user),
        project_manager=Depends(get_project_manager),
    ):
        """
        This route creates a new project
        ### Arguments
        * project (ProjectCreate): The project to create

        ### Response
        * project (ProjectRead): The created project

        ### Raises
        * HTTPException:
            * 422 Unprocessable Entity: If the project name already exists
        """
        try:
            project = await project_manager.create(project)
        except Exception as e:
            raise HTTPException(status_code=422, detail=ErrorCode.PROJECT_NAME_EXISTS)
        return project

    @router.patch(
        "/{project_id}", summary="Update a project", response_model=ProjectRead
    )
    async def update_project(
        project_id: UUID,
        project: ProjectUpdate,
        user: User = Depends(current_active_user),
        project_manager=Depends(get_project_manager),
    ):
        """
        This route updates a project

        ### Arguments
        * project_id: The id of the project to update
        * project (ProjectUpdate): The project to update

        ### Response
        * project (ProjectRead): The updated project

        ### Raises
        * HTTPException:
            * 404 Not found: If the project doesn't exist
        """
        project = await project_manager.update(project_id, project)
        if project is None:
            raise HTTPException(status_code=404, detail=ErrorCode.PROJECT_NOT_FOUND)
        return project

    @router.delete(
        "/{project_id}",
        summary="Delete a project",
        status_code=status.HTTP_204_NO_CONTENT,
        responses={
            status.HTTP_404_NOT_FOUND: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            ErrorCode.PROJECT_NOT_FOUND: {
                                "value": {"detail": ErrorCode.PROJECT_NOT_FOUND}
                            }
                        }
                    }
                },
            },
        },
    )
    async def delete_project(
        project_id: UUID,
        user: User = Depends(current_active_user),
        project_manager=Depends(get_project_manager),
    ):
        """
        This route deletes a project
        ### Arguments
        * project_id: The id of the project to delete

        ### Raises
        * HTTPException:
            * 404 Not found: If the project doesn't exist
        """
        result = await project_manager.delete(project_id)
        if not result:
            raise HTTPException(status_code=404, detail=ErrorCode.PROJECT_NOT_FOUND)

    return router
