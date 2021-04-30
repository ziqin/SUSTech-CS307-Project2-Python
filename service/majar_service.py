from abc import ABC
from typing import List

from dto import Major


class MajorService(ABC):
    async def add_major(self, name: str, department_id: int) -> int:
        raise NotImplementedError

    async def remove_major(self, major_id: int):
        raise NotImplementedError

    async def get_all_majors(self) -> List[Major]:
        raise NotImplementedError

    async def get_major(self, major_id: int) -> Major:
        raise NotImplementedError

    async def add_major_compulsory_course(self, major_id: int, course_id: str):
        raise NotImplementedError

    async def add_major_elective_course(self, major_id: int, course_id: str):
        raise NotImplementedError
