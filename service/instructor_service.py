from abc import ABC
from typing import List

from dto import CourseSection


class InstructorService(ABC):
    async def add_instructor(self, user_id: int, first_name: str,
                             last_name: str) -> int:
        raise NotImplementedError

    async def get_instructed_course_sections(self, instructor_id: int,
                                             semester_id: int
                                             ) -> List[CourseSection]:
        raise NotImplementedError
