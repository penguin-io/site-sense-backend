from app.manager.projects import get_project_manager
from app.manager.worksites import get_worksite_manager
from app.manager.zones import get_zone_manager
from app.manager.users import get_user_manager
from app.manager.employees import get_employee_manager
from .projects import get_project_router
from .worksites import get_worksite_router
from .zones import get_zone_router
from .users import get_access_router
from .employees import get_employees_router
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


class access_router:
    def __init__(self, get_user_manager, get_project_manager, get_worksite_manager):
        self.get_user_manager = get_user_manager
        self.get_project_manager = get_project_manager
        self.get_worksite_manager = get_worksite_manager

    def get_access_router(self):
        return get_access_router(
            self.get_user_manager, self.get_project_manager, self.get_worksite_manager
        )


class employees_router:
    def __init__(self, get_employee_manager, get_worksite_manager):
        self.get_employee_manager = get_employee_manager
        self.get_worksite_manager = get_worksite_manager

    def get_employees_router(self):
        return get_employees_router(
            self.get_employee_manager, self.get_worksite_manager
        )


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

access_router = access_router(
    get_user_manager, get_project_manager, get_worksite_manager
)
router = APIRouter()
router.include_router(access_router.get_access_router())
access_router = router

employees_router = employees_router(get_employee_manager, get_worksite_manager)
router = APIRouter()
router.include_router(employees_router.get_employees_router())
employees_router = router
