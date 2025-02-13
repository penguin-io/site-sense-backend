from app.manager.projects import get_project_manager
from app.manager.worksites import get_worksite_manager
from app.manager.zones import get_zone_manager
from .projects import get_project_router
from .worksites import get_worksite_router
from .zones import get_zone_router
from fastapi import APIRouter


class project_router:
    def __init__(self, get_project_manager):
        self.get_project_manager = get_project_manager

    def get_project_router(self):
        return get_project_router(self.get_project_manager)


class worksite_router:
    def __init__(self, get_worksite_manager):
        self.get_worksite_manager = get_worksite_manager

    def get_worksite_router(self):
        return get_worksite_router(self.get_worksite_manager)


class zone_router:
    def __init__(self, get_zone_manager):
        self.get_zone_manager = get_zone_manager

    def get_zone_router(self):
        return get_zone_router(self.get_zone_manager)


project_router = project_router(get_project_manager)
router = APIRouter()
router.include_router(project_router.get_project_router())
project_router = router

worksite_router = worksite_router(get_worksite_manager)
router = APIRouter()
router.include_router(worksite_router.get_worksite_router())
worksite_router = router

zone_router = zone_router(get_zone_manager)
router = APIRouter()
router.include_router(zone_router.get_zone_router())
zone_router = router
