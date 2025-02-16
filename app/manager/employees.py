from typing import List
from uuid import UUID

from fastapi import Depends

from app.db.employees import Employee, get_employee_db
from app.schemas.employees import EmployeeCreate, EmployeeUpdate

class EmployeeManager:
    def __init__(self, employee_table):
        self.employee_table = employee_table

    async def get(self, employee_id: UUID) -> Employee:
        """
        Return employee by id

        :param employee_id: The id of the employee
        :return: Employee
        """
        worksites = await self.employee_table.get(employee_id)
        return worksites


    async def create(self, employee_create: EmployeeCreate) -> Employee:
        """
        Create a new employee
        :param employee_create: The employee to create
        :return: The created employee, None if an error occurred
        """
        employee = await self.employee_table.create(employee_create)
        if employee is None:
            raise Exception("Error creating employee")
        return employee


    async def update(self, employee_id: UUID, employee_update: EmployeeUpdate) -> Employee:
        """
        Update an existing employee
        :param employee_id: The id of the target employee
        :param employee_update: The updated employee
        :return: The updated employee
        """
        await self.employee_table.update(employee_id, employee_update)
        employee = await self.employee_table.get(employee_id)
        return employee


    async def delete(self, employee_id: UUID):
        """
        Delete a employee
        :param employee_id: The id of the employee to delete
        :return: success - True if the employee was deleted, False otherwise
        """
        result = await self.employee_table.delete(employee_id)
        return result


