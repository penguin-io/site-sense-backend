from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from app.manager.users import current_active_user
from app.schemas.worksites import WorksiteRead, WorksiteCreate, WorksiteUpdate
from app.schemas.zones import ZoneRead
from app.db.users import User
from app.exceptions import ErrorCode, ErrorModel, InvalidProjectError
from uuid import UUID


def get_worksite_router(get_worksite_manager) -> APIRouter:
    router = APIRouter()

    @router.get("/all")
    async def get_all_worksites(
        user: User = Depends(current_active_user),
        worksite_manager=Depends(get_worksite_manager),
    ):
        worksites = await worksite_manager.get_all()
        return worksites

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
        worksite_id: UUID,
        worksite_manager=Depends(get_worksite_manager),
        user: User = Depends(current_active_user),
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

    @router.get("/")
    async def get_user_worksites(
        user: User = Depends(current_active_user),
        worksite_manager=Depends(get_worksite_manager),
    ):
        worksites = await worksite_manager.get_accessible_worksites(user.id)
        return worksites

    @router.get(
        "/{worksite_id}/zones",
        response_model=List[ZoneRead],
        summary="Get all zones of a worksite",
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
    )
    async def get_zones(
        worksite_id: UUID,
        user: User = Depends(current_active_user),
        worksite_manager=Depends(get_worksite_manager),
    ):
        """
        This route returns all zones of a worksite

        ### Arguments
        * worksite_id: The id of the worksite

        ### Response
        * zones (ZonesRead): The zones of the requested worksite

        ### Raises
        * HTTPException:
            * 404 Not found: If the worksite doesn't exist
        """
        zones = await worksite_manager.get_zones(worksite_id)
        if zones is None:
            raise HTTPException(status_code=404, detail=ErrorCode.WORKSITE_NOT_FOUND)
        return zones

    @router.post(
        "/",
        summary="Create a new worksite",
        response_model=WorksiteRead,
        status_code=status.HTTP_201_CREATED,
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
        """
        try:
            worksite = await worksite_manager.create(worksite)
        except InvalidProjectError:
            raise HTTPException(status_code=422, detail=ErrorCode.PROJECT_NOT_FOUND)
        return worksite

    @router.patch(
        "/{worksite_id}",
        summary="Update a worksite",
        response_model=WorksiteRead,
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
    )
    async def update_worksite(
        worksite_id: UUID,
        worksite: WorksiteUpdate,
        user: User = Depends(current_active_user),
        worksite_manager=Depends(get_worksite_manager),
    ):
        """
        This route updates a worksite

        ### Arguments
        * worksite_id: The id of the worksite to update

        ### Response
        * worksite (WorksiteRead): The updated worksite

        ### Raises
        * HTTPException:
            * 404 Not found: If the worksite doesn't exist
        """
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
        """
        result = await worksite_manager.delete(worksite_id)
        if not result:
            raise HTTPException(status_code=404, detail=ErrorCode.WORKSITE_NOT_FOUND)

    return router
