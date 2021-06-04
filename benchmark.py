#!/usr/bin/env python3

import asyncio

from factory import ServiceFactory, create_async_context


async def main():
    async with create_async_context() as context:
        factory = ServiceFactory(context)
        if hasattr(factory, 'async_init') and callable(getattr(factory, 'async_init')):
            await factory.async_init()

        # Create service instances
        course_service = factory.create_course_service()
        department_service = factory.create_department_service()
        instructor_service = factory.create_instructor_service()
        major_service = factory.create_major_service()
        semester_service = factory.create_semester_service()
        student_service = factory.create_student_service()
        user_service = factory.create_user_service()

        # Asynchronous methods on services will be invoked here using `await`


if __name__ == '__main__':
    asyncio.run(main())
