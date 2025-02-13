from fastapi import APIRouter, Depends, status, HTTPException
from app.manager.users import current_active_user
from app.schemas.worksites import WorksiteRead, WorksiteCreate, WorksiteUpdate
from app.db.users import User
from app.exceptions import ErrorCode, ErrorModel, InvalidProjectError
from uuid import UUID


def get_worksite_router(get_worksite_manager) -> APIRouter:
    router = APIRouter()

    @router.get(
        "/{worksite_id}",
        summary="Get a worksite by its id",
        responses={
            status.HTTP_404_NOT_FOUND: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            ErrorCode.WORKSITE_NOT_FOUND: {
                                "value": {"detail": ErrorCode.WORKSITE_NOT_FOUND}
                            }
                        }
                    }
                },
            },
        },
        response_model=WorksiteRead,
    )
    async def get_worksite(
        worksite_id: int,
        worksite_manager=Depends(get_worksite_manager),
    ):
        """
        This route returns a worksite by its id
        ### Arguments
        * worksite_id: The id of the worksite

        ### Response
        * worksite (WorksiteRead): The requested worksite

        ### Raises
        * HTTPException:
            * 404 Not found: If the worksite doesn't exist
        """
        worksite = await worksite_manager.get(worksite_id)
        if worksite is None:
            raise HTTPException(status_code=404, detail=ErrorCode.WORKSITE_NOT_FOUND)
        return worksite

    @router.post(
        "/",
        summary="Create a new worksite",
        response_model=WorksiteRead,
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
                        }
                    }
                },
            },
            status.HTTP_422_UNPROCESSABLE_ENTITY: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            ErrorCode.ADMIN_REQUIRED: {
                                "value": {"detail": ErrorCode.WORKSITE_NAME_EXISTS}
                            },
                        }
                    }
                },
            },
        },
    )
    async def create_worksite(
        worksite: WorksiteCreate,
        user: User = Depends(current_active_user),
        worksite_manager=Depends(get_worksite_manager),
    ):
        """
        This route creates a new worksite
        ### Arguments
        * worksite (WorksiteCreate): The worksite to create

        ### Response
        * worksite (WorksiteRead): The created worksite

        ### Raises
        * HTTPException:
            * 403 Forbidden: If the user is not the admin
            * 422 Unprocessable Entity: If the worksite name already exists
        """
        if not user.is_superuser:
            raise HTTPException(status_code=403, detail=ErrorCode.ADMIN_REQUIRED)
        try:
            worksite = await worksite_manager.create(worksite)
        except InvalidProjectError:
            raise HTTPException(status_code=422, detail=ErrorCode.PROJECT_NOT_FOUND)
        except Exception as e:
            raise HTTPException(status_code=422, detail=ErrorCode.WORKSITE_NAME_EXISTS)
        return worksite

    @router.patch("/{worksite_id}")
    async def update_worksite(
        worksite_id: UUID,
        worksite: WorksiteUpdate,
        user: User = Depends(current_active_user),
        worksite_manager=Depends(get_worksite_manager),
    ):
        if not user.is_superuser:
            raise HTTPException(status_code=403, detail=ErrorCode.ADMIN_REQUIRED)
        worksite = await worksite_manager.update(worksite_id, worksite)
        if worksite is None:
            raise HTTPException(status_code=404, detail=ErrorCode.WORKSITE_NOT_FOUND)
        return worksite

    @router.delete(
        "/{worksite_id}",
        summary="Delete a worksite",
        status_code=status.HTTP_204_NO_CONTENT,
        responses={
            status.HTTP_404_NOT_FOUND: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            ErrorCode.WORKSITE_NOT_FOUND: {
                                "value": {"detail": ErrorCode.WORKSITE_NOT_FOUND}
                            }
                        }
                    }
                },
            },
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
    async def delete_worksite(
        worksite_id: UUID,
        user: User = Depends(current_active_user),
        worksite_manager=Depends(get_worksite_manager),
    ):
        """
        This route deletes a worksite
        ### Arguments
        * worksite_id: The id of the worksite to delete

        ### Raises
        * HTTPException:
            * 404 Not found: If the worksite doesn't exist
            * 403 Forbidden: If the user is not the admin
        """
        if not user.is_superuser:
            raise HTTPException(status_code=403, detail=ErrorCode.ADMIN_REQUIRED)
        result = await worksite_manager.delete(worksite_id)
        if not result:
            raise HTTPException(status_code=404, detail=ErrorCode.WORKSITE_NOT_FOUND)

    return router
