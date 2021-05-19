from factory import ServiceFactory

factory = ServiceFactory()

course_service = factory.create_course_service()
department_service = factory.create_department_service()
instructor_service = factory.create_instructor_service()
major_service = factory.create_major_service()
semester_service = factory.create_semester_service()
student_service = factory.create_student_service()
user_service = factory.create_user_service()

# TODO
