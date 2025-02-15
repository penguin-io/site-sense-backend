from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.db.users import User
from app.exceptions import ErrorCode, ErrorModel
from app.manager.users import current_active_user, get_user_manager
from app.manager.worksites import get_worksite_manager
from app.schemas.users import RoleReq, AccessReq
from uuid import UUID


def get_access_router(
    get_user_manager, get_project_manager, get_worksite_manager
) -> APIRouter:
    router = APIRouter()

    @router.post(
        "/set-role",
        summary="Set the role for a user",
        status_code=201,
        responses={
            status.HTTP_404_NOT_FOUND: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            ErrorCode.USER_NOT_FOUND: {
                                "value": {"detail": ErrorCode.USER_NOT_FOUND}
                            }
                        }
                    }
                },
            },
        },
    )
    async def set_role(
        role_request: RoleReq,
        response: Response,
        user: User = Depends(current_active_user),
        user_manager=Depends(get_user_manager),
    ):
        """
        This route sets the role for a user

        ### Arguments
        * role_request (RoleReq): The role request

        ### Raises
        * HTTPException:
            * 404 Not found: If the user doesn't exist
        """
        result = await user_manager.set_role(role_request)
        if result is None:
            raise HTTPException(status_code=404, detail=ErrorCode.USER_NOT_FOUND)
        if result is False:
            response.status_code = 200
        return result

    @router.post("/set-access", summary="Allow access to a project", status_code=201)
    async def set_access(
        access_request: AccessReq,
        user: User = Depends(current_active_user),
        user_manager=Depends(get_user_manager),
        project_manager=Depends(get_project_manager),
        worksite_manager=Depends(get_worksite_manager),
    ):
        if access_request.resource_type == "project":
            for project_id in access_request.resource_ids:
                project = await project_manager.get(project_id)
                if project is None:
                    raise HTTPException(
                        status_code=404, detail=ErrorCode.PROJECT_NOT_FOUND
                    )
        elif access_request.resource_type == "worksite":
            for worksite_id in access_request.resource_ids:
                worksite = await worksite_manager.get(worksite_id)
                if worksite is None:
                    raise HTTPException(
                        status_code=404, detail=ErrorCode.WORKSITE_NOT_FOUND
                    )
        result = await user_manager.set_access(access_request)
        return result

    return router
