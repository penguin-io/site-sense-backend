from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.db.employees import Employee
from app.manager.users import current_active_user
from app.schemas.employees import AttendanceReq, EmployeeCreate, EmployeeUpdate, EmployeeRead
from app.kafka import send_log_to_kafka
from app.manager.worksites import get_worksite_manager
from app.manager.employees import get_employee_manager
from app.db.users import User
from time import time


def get_employees_router(get_employee_manager, get_worksite_manager):
    router = APIRouter()

    @router.post("/attendance")
    async def attendance(
        attendance_request: AttendanceReq,
        user: User = Depends(current_active_user),
        employee_manager=Depends(get_employee_manager),
        worksite_manager=Depends(get_worksite_manager),
    ):
        worksite = await worksite_manager.get(attendance_request.worksite_id)
        employee = await employee_manager.get(attendance_request.employee_id)
        if worksite is None or employee is None:
            raise HTTPException(
                status_code=404, detail="Worksite or employee not found"
            )
        log = {
            "event": "attendance",
            "data": {
                "worksite_id": str(attendance_request.worksite_id),
                "employee_id": str(attendance_request.employee_id),
                "time": time()
            },
        }
        print(log)
        await send_log_to_kafka(log)

    @router.post("/add", response_model=EmployeeRead)
    async def add_employee(
        employee_create: EmployeeCreate,
        employee_manager=Depends(get_employee_manager),
        user: User = Depends(current_active_user),
    ):
        employee = await employee_manager.create(employee_create)
        return employee

    @router.get("/", response_model=List[EmployeeRead])
    async def get_employees(
        employee_manager=Depends(get_employee_manager),
        user: User = Depends(current_active_user),
    ):
        employees = await employee_manager.get_employees()
        return employees

    @router.get("/{employee_id}", response_model=EmployeeRead)
    async def get_employee(
        employee_id: UUID,
        employee_manager=Depends(get_employee_manager),
        user: User = Depends(current_active_user),
    ):
        employee = await employee_manager.get(employee_id)
        return employee

    @router.patch("/{employee_id}", response_model=EmployeeRead)
    async def update_employee(
        employee_id: UUID,
        employee_update: EmployeeUpdate,
        employee_manager=Depends(get_employee_manager),
        user: User = Depends(current_active_user),
    ):
        employee = await employee_manager.update(employee_id, employee_update)
        return employee

    @router.delete("/{employee_id}", status_code=204)
    async def delete_employee(
        employee_id: UUID,
        employee_manager=Depends(get_employee_manager),
        user: User = Depends(current_active_user),
    ):
        result = await employee_manager.delete(employee_id)
        return result

    return router
