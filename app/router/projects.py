from fastapi import APIRouter, Depends, status, HTTPException
from app.manager.users import current_active_user
from app.schemas.projects import ProjectCreate, ProjectRead
from app.db.users import User
from app.exceptions import ErrorCode, ErrorModel
from uuid import UUID


def get_project_router(get_project_manager) -> APIRouter:
    router = APIRouter()

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

    @router.post(
        "/",
        summary="Create a new project",
        response_model=ProjectRead,
        status_code=status.HTTP_201_CREATED,
        responses={
            status.HTTP_403_FORBIDDEN: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            ErrorCode.ADMIN_REQUIRED: {
                                "value": {"detail": ErrorCode.ADMIN_REQUIRED}
                            },
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
            * 403 Forbidden: If the user is not the admin
            * 422 Unprocessable Entity: If the project name already exists
        """
        if not user.is_superuser:
            raise HTTPException(status_code=403, detail=ErrorCode.ADMIN_REQUIRED)
        try:
            project = await project_manager.create(project)
        except Exception as e:
            raise HTTPException(status_code=422, detail=ErrorCode.PROJECT_NAME_EXISTS)
        return project

    @router.delete(
        "/{project_id}",
        summary="Delete a project",
        status_code=status.HTTP_204_NO_CONTENT,
        responses={
            status.HTTP_403_FORBIDDEN: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            ErrorCode.ADMIN_REQUIRED: {
                                "value": {"detail": ErrorCode.ADMIN_REQUIRED}
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
            * 403 Forbidden: If the user is not the admin
        """
        if not user.is_superuser:
            raise HTTPException(status_code=403, detail=ErrorCode.ADMIN_REQUIRED)
        result = await project_manager.delete(project_id)
        if not result:
            raise HTTPException(status_code=404, detail=ErrorCode.PROJECT_NOT_FOUND)

    return router
