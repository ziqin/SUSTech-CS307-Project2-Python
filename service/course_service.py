from abc import ABC
from typing import List, Optional

from dto import (Course, CourseGrading, CourseSection, CourseSectionClass,
                 DayOfWeek, Prerequisite, Student)


class CourseService(ABC):
    async def add_course(self, course_id: str, course_name: str, credit: int,
                         class_hour: int, grading: CourseGrading,
                         prerequisite: Optional[Prerequisite]):
        raise NotImplementedError

    async def add_course_section(self, course_id: str, semester_id: int,
                                 section_name: str, total_capacity: int
                                 ) -> int:
        raise NotImplementedError

    async def add_course_section_class(self, section_id: int,
                                       instructor_id: int,
                                       day_of_week: DayOfWeek,
                                       week_list: List[int],
                                       class_start: int,
                                       class_end: int,
                                       location: str) -> int:
        raise NotImplementedError

    async def remove_course(self, course_id: str):
        raise NotImplementedError

    async def remove_course_section(self, section_id: int):
        raise NotImplementedError

    async def remove_course_section_class(self, class_id: int):
        raise NotImplementedError

    async def get_all_courses(self) -> List[Course]:
        raise NotImplementedError

    async def get_course_sections_in_semester(self, course_id: str,
                                              semester_id: int
                                              ) -> List[CourseSection]:
        raise NotImplementedError

    async def get_course_by_section(self, section_id: int) -> Course:
        raise NotImplementedError

    async def get_course_section_classes(self, section_id: int) \
            -> List[CourseSectionClass]:
        raise NotImplementedError

    async def get_course_section_by_class(self, class_id: int) \
            -> CourseSection:
        raise NotImplementedError

    async def get_enrolled_students_in_semester(self, course_id: str,
                                                semester_id: int
                                                ) -> List[Student]:
        raise NotImplementedError
