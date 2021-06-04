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

    def __hash__(self):
        return self.value

    def __eq__(self, other):
        if isinstance(other, str):
            return self is DayOfWeek[other]
        else:
            return self is other


class CourseGrading(Enum):
    PASS_OR_FAIL = 1
    HUNDRED_MARK_SCORE = 2

    def __eq__(self, other):
        if isinstance(other, str):
            return self is CourseGrading[other]
        else:
            return self is other


class PassOrFailGrade(Enum):
    PASS = 1
    FAIL = 2

    def __eq__(self, other):
        if isinstance(other, str):
            return self is PassOrFailGrade[other]
        else:
            return self is other


Grade = Union[PassOrFailGrade, int]


class EnrollResult(Enum):
    SUCCESS = 1
    COURSE_NOT_FOUND = 2
    COURSE_IS_FULL = 3
    ALREADY_ENROLLED = 4
    ALREADY_PASSED = 5
    PREREQUISITES_NOT_FULFILLED = 6
    COURSE_CONFLICT_FOUND = 7
    UNKNOWN_ERROR = 8

    def __eq__(self, other):
        if isinstance(other, str):
            return self is EnrollResult[other]
        else:
            return self is other


class CourseType(Enum):
    ALL = 1
    MAJOR_COMPULSORY = 2
    MAJOR_ELECTIVE = 3
    CROSS_MAJOR = 4
    PUBLIC = 5

    def __eq__(self, other):
        if isinstance(other, str):
            return self is CourseType[other]
        else:
            return self is other


@dataclass()
class Department:
    id: int
    name: str

    def __eq__(self, other):
        return self.name == self.name


@dataclass()
class Major:
    id: int
    name: str
    department: Department

    def __eq__(self, other):
        return self.name == other.name and self.department == other.department


@dataclass()
class Instructor:
    id: int
    full_name: str

    def __eq__(self, other):
        if isinstance(other, dict):
            return self.full_name == other['full_name']
        return self.full_name == other.full_name

    def __hash__(self):
        return hash(self.full_name)


@dataclass()
class Student:
    id: int
    full_name: str
    enrolled_date: date
    major: Major

    def __eq__(self, other):
        return self.id == other.id and self.full_name == other.full_name and self.major == other.major


User = Union[Instructor, Student]


@dataclass()
class Course:
    id: str
    name: str
    credit: int
    class_hour: int
    grading: CourseGrading

    def __eq__(self, other):
        if isinstance(other.grading, str):
            return self.name == other.name and self.credit == other.credit and self.class_hour == other.class_hour and self.grading == \
                   CourseGrading[other.grading]
        else:
            return self.name == other.name and self.credit == other.credit and self.class_hour == other.class_hour and self.grading == other.grading


@dataclass()
class CourseSection:
    id: int
    name: str
    total_capacity: int
    left_capacity: int

    def __eq__(self, other):
        return self.name == other.name and self.total_capacity == other.total_capacity and self.left_capacity == other.left_capacity


@dataclass()
class CourseSectionClass:
    id: int
    instructor: Instructor
    day_of_week: DayOfWeek
    week_list: List[int]
    class_begin: int
    class_end: int
    location: str

    def __eq__(self, other):
        return self.instructor == other.instructor and self.day_of_week == other.day_of_week \
               and sorted(self.week_list) == sorted(other.week_list) and self.class_begin == other.class_begin \
               and self.class_end == other.class_end and self.location == other.location

    def __hash__(self):
        return 0


@dataclass()
class CourseSearchEntry:
    course: Course
    section: CourseSection
    section_classes: List[CourseSectionClass]
    conflict_course_names: List[str]

    def __eq__(self, other):
        cnt = 0
        for c in self.section_classes:
            for x in other.section_classes:
                if c == x:
                    cnt = cnt + 1
        return self.course == other.course and self.section == other.section \
               and cnt == len(self.section_classes) \
               #and self.conflict_course_names == other.conflict_course_names


@dataclass()
class CourseTableEntry:
    course_full_name: str
    instructor: Instructor
    class_begin: int
    class_end: int
    location: str

    def __eq__(self, other):
        return self.course_full_name == other.course_full_name and self.instructor == other.instructor \
               and self.class_begin == other.class_begin \
               and self.class_end == other.class_end \
               and self.location == other.location


CourseTable = Mapping[DayOfWeek, List[CourseTableEntry]]


@dataclass()
class Semester:
    id: int
    name: str
    begin: date
    end: date

    def __eq__(self, other):
        return self.name == other.name and self.begin == other.begin and self.end == other.end


Prerequisite = Union['AndPrerequisite', 'OrPrerequisite', 'CoursePrerequisite']


@dataclass()
class AndPrerequisite:
    terms: List[Prerequisite]


@dataclass()
class OrPrerequisite:
    terms: List[Prerequisite]


@dataclass()
class CoursePrerequisite:
    course_id: str
