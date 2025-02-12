from app.manager.projects import get_project_manager
from .projects import get_project_router
from fastapi import APIRouter


class project_router:
    def __init__(self, get_project_manager):
        self.get_project_manager = get_project_manager

    def get_project_router(self):
        return get_project_router(self.get_project_manager)


project_router = project_router(get_project_manager)
router = APIRouter()
router.include_router(project_router.get_project_router())
project_router = router
