from abc import ABC
from datetime import date
from typing import List

from dto import Semester


class SemesterService(ABC):
    async def add_semester(self, name: str, begin: date, end: date) -> int:
        raise NotImplementedError

    async def remove_semester(self, semester_id: int):
        raise NotImplementedError

    async def get_all_semesters(self) -> List[Semester]:
        raise NotImplementedError

    async def get_semester(self, semester_id: int) -> Semester:
        raise NotImplementedError
