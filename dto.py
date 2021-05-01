from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import List, Mapping, Union


class DayOfWeek(Enum):
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7


class CourseGrading(Enum):
    PASS_OR_FAIL = 1
    HUNDRED_MARK_SCORE = 2


class PassOrFailGrade(Enum):
    PASS = 1
    FAIL = 2


Grade = Union[PassOrFailGrade, int]


class EnrollResult(Enum):
    SUCCESS = 1
    COURSE_NOT_FOUND = 2
    COURSE_IS_FULL = 3
    ALREADY_SELECTED = 4
    ALREADY_PASSED = 5
    PREREQUISITES_NOT_FULFILLED = 6
    COURSE_CONFLICT_FOUND = 7
    UNKNOWN_ERROR = 8


class CourseType(Enum):
    ALL = 1
    MAJOR_COMPULSORY = 2
    MAJOR_ELECTIVE = 3
    CROSS_MAJOR = 4
    PUBLIC = 5


@dataclass(frozen=True)
class Department:
    id: int
    name: str


@dataclass(frozen=True)
class Major:
    id: int
    name: str
    department: Department


@dataclass(frozen=True)
class Instructor:
    id: int
    full_name: str


@dataclass(frozen=True)
class Student:
    id: int
    full_name: str
    enrolled_data: date
    major: Major


User = Union[Instructor, Student]


@dataclass(frozen=True)
class Course:
    id: str
    name: str
    credit: int
    class_hour: int
    grading: CourseGrading


@dataclass(frozen=True)
class CourseSection:
    id: int
    name: str
    total_capacity: int
    left_capacity: int


@dataclass(frozen=True)
class CourseSectionClass:
    id: int
    instructor: Instructor
    day_of_week: DayOfWeek
    week_list: List[int]
    class_begin: int
    class_end: int
    location: str


@dataclass(frozen=True)
class CourseSearchEntry:
    course: Course
    section: CourseSection
    section_classes: List[CourseSectionClass]
    conflict_course_names: List[str]


@dataclass(frozen=True)
class CourseTableEntry:
    course_full_name: str
    instructor: Instructor
    class_begin: int
    class_end: int
    location: str


CourseTable = Mapping[DayOfWeek, List[CourseTableEntry]]


@dataclass(frozen=True)
class Semester:
    id: int
    name: str
    begin: date
    end: date


Prerequisite = Union['AndPrerequisite', 'OrPrerequisite', 'CoursePrerequisite']


@dataclass(frozen=True)
class AndPrerequisite:
    terms: List[Prerequisite]


@dataclass(frozen=True)
class OrPrerequisite:
    terms: List[Prerequisite]


@dataclass(frozen=True)
class CoursePrerequisite:
    course_id: str
