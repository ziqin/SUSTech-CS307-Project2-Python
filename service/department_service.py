from abc import ABC
from typing import List

from dto import Department


class DepartmentService(ABC):
    async def add_department(self, name: str) -> int:
        raise NotImplementedError

    async def remove_department(self, department_id: int):
        raise NotImplementedError

    async def get_all_departments(self) -> List[Department]:
        raise NotImplementedError

    async def get_department(self, department_id: int) -> Department:
        raise NotImplementedError
