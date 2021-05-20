from configparser import ConfigParser
from pathlib import Path

import asyncpg

from service import *


def create_async_context():
    # You can customize the async context manager in this function.
    # e.g., you may use other connection pool implementation.
    config = ConfigParser()
    config.read(Path(__file__).parent / 'config.ini')
    db_cfg = config['database']
    return asyncpg.create_pool(host=db_cfg['host'],
                               port=db_cfg['port'],
                               database=db_cfg['database'],
                               user=db_cfg['username'],
                               password=db_cfg['password'])


class ServiceFactory:
    def __init__(self, context):
        self._context = context
        # You can add initialization steps here

    async def async_init(self):
        # You can add asynchronous initialization steps here.
        pass

    def create_course_service(self) -> CourseService:
        # TODO: return an instance of your implementation
        raise NotImplementedError

    def create_department_service(self) -> DepartmentService:
        # TODO: return an instance of your implementation
        raise NotImplementedError

    def create_instructor_service(self) -> InstructorService:
        # TODO: return an instance of your implementation
        raise NotImplementedError

    def create_major_service(self) -> MajorService:
        # TODO: return an instance of your implementation
        raise NotImplementedError

    def create_semester_service(self) -> SemesterService:
        # TODO: return an instance of your implementation
        raise NotImplementedError

    def create_student_service(self) -> StudentService:
        # TODO: return an instance of your implementation
        raise NotImplementedError

    def create_user_service(self) -> UserService:
        # TODO: return an instance of your implementation
        raise NotImplementedError
