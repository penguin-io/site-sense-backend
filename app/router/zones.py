from fastapi import APIRouter, Depends, status, HTTPException
from app.manager.users import current_active_user
from app.schemas.zones import ZoneRead, ZoneCreate, ZoneUpdate
from app.db.users import User
from app.exceptions import ErrorCode, ErrorModel


def get_zone_router(get_zone_manager) -> APIRouter:
    router = APIRouter()

    @router.get(
        "/{zone_id}",
        summary="Get a zone by its id",
        responses={
            status.HTTP_404_NOT_FOUND: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            ErrorCode.ZONE_NOT_FOUND: {
                                "value": {"detail": ErrorCode.ZONE_NOT_FOUND}
                            }
                        }
                    }
                },
            },
        },
        response_model=ZoneRead,
    )
    async def get_zone(
        zone_id: int,
        zone_manager=Depends(get_zone_manager),
    ):
        """
        This route returns a zone by its id
        ### Arguments
        * zone_id: The id of the zone

        ### Response
        * zone (ZoneRead): The requested zone

        ### Raises
        * HTTPException:
            * 404 Not found: If the zone doesn't exist
        """
        zone = await zone_manager.get(zone_id)
        if zone is None:
            raise HTTPException(status_code=404, detail=ErrorCode.ZONE_NOT_FOUND)
        return zone

    @router.post(
        "/",
        summary="Create a new zone",
        response_model=ZoneRead,
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
                                "value": {"detail": ErrorCode.ZONE_NAME_EXISTS}
                            },
                        }
                    }
                },
            },
        },
    )
    async def create_zone(
        zone: ZoneCreate,
        user: User = Depends(current_active_user),
        zone_manager=Depends(get_zone_manager),
    ):
        """
        This route creates a new zone
        ### Arguments
        * zone (ZoneCreate): The zone to create

        ### Response
        * zone (ZoneRead): The created zone

        ### Raises
        * HTTPException:
            * 403 Forbidden: If the user is not the admin
            * 422 Unprocessable Entity: If the zone name already exists
        """
        if not user.is_superuser:
            raise HTTPException(status_code=403, detail=ErrorCode.ADMIN_REQUIRED)
        try:
            zone = await zone_manager.create(zone)
        except Exception as e:
            raise HTTPException(status_code=422, detail=ErrorCode.ZONE_NAME_EXISTS)
        return zone

    @router.patch("/{zone_id}")
    async def update_zone(
        zone_id: int,
        zone: ZoneUpdate,
        user: User = Depends(current_active_user),
        zone_manager=Depends(get_zone_manager),
    ):
        if not user.is_superuser:
            raise HTTPException(status_code=403, detail=ErrorCode.ADMIN_REQUIRED)
        zone = await zone_manager.update(zone_id, zone)
        if zone is None:
            raise HTTPException(status_code=404, detail=ErrorCode.ZONE_NOT_FOUND)
        return zone

    @router.delete(
        "/{zone_id}",
        summary="Delete a zone",
        status_code=status.HTTP_204_NO_CONTENT,
        responses={
            status.HTTP_404_NOT_FOUND: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            ErrorCode.ZONE_NOT_FOUND: {
                                "value": {"detail": ErrorCode.ZONE_NOT_FOUND}
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
    async def delete_zone(
        zone_id: int,
        user: User = Depends(current_active_user),
        zone_manager=Depends(get_zone_manager),
    ):
        """
        This route deletes a zone
        ### Arguments
        * zone_id: The id of the zone to delete

        ### Raises
        * HTTPException:
            * 404 Not found: If the zone doesn't exist
            * 403 Forbidden: If the user is not the admin
        """
        if not user.is_superuser:
            raise HTTPException(status_code=403, detail=ErrorCode.ADMIN_REQUIRED)
        result = await zone_manager.delete(zone_id)
        if not result:
            raise HTTPException(status_code=404, detail=ErrorCode.ZONE_NOT_FOUND)

    return router
