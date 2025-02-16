from fastapi import APIRouter, Depends, HTTPException
from app.schemas.employees import AttendanceReq
from app.kafka import send_log_to_kafka
from app.manager.worksites import get_worksite_manager
from app.manager.employees import get_employee_manager
from datetime import datetime


def get_employees_router(get_employee_manager, get_worksite_manager):
    router = APIRouter()
    @router.post("/attendance")
    async def attendance(attendance_request: AttendanceReq, employee_manager=Depends(get_employee_manager), worksite_manager=Depends(get_worksite_manager)):
        worksite = await worksite_manager.get_worksite(attendance_request.worksite_id)
        employee = await employee_manager.get_employee(attendance_request.employee_id)
        if worksite is None or employee is None:
            raise HTTPException(status_code=404, detail="Worksite or employee not found")
        log = {"event": "attendance", "data": {"worksite_id": attendance_request.worksite_id, "employee_id": attendance_request.employee_id, "time": datetime.now()}}
        await send_log_to_kafka(log)

