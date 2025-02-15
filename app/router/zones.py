from fastapi import APIRouter, Depends, status, HTTPException
from app.manager.users import current_active_user
from app.schemas.zones import ZoneRead, ZoneCreate, ZoneUpdate
from app.db.users import User
from app.exceptions import ErrorCode, ErrorModel
from uuid import UUID


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
        zone_id: UUID,
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
        """
        zone = await zone_manager.create(zone)
        return zone

    @router.patch(
        "/{zone_id}",
        summary="Update a zone",
        response_model=ZoneRead,
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
    )
    async def update_zone(
        zone_id: UUID,
        zone: ZoneUpdate,
        user: User = Depends(current_active_user),
        zone_manager=Depends(get_zone_manager),
    ):
        """
        This route updates a zone

        ### Arguments
        * zone_id: The id of the zone to update

        ### Response
        * zone (ZoneRead): The updated zone

        ### Raises
        * HTTPException:
            * 404 Not found: If the zone doesn't exist
        """
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
        },
    )
    async def delete_zone(
        zone_id: UUID,
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
        """
        result = await zone_manager.delete(zone_id)
        if not result:
            raise HTTPException(status_code=404, detail=ErrorCode.ZONE_NOT_FOUND)

    return router
