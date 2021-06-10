#!/usr/bin/env python3

import asyncio
import json
import os
from datetime import datetime
from time import time
from typing import Optional

from dto import AndPrerequisite, Instructor, OrPrerequisite, CoursePrerequisite, PassOrFailGrade, CourseSearchEntry, \
    Course, \
    CourseSection, CourseSectionClass, CourseType, DayOfWeek, EnrollResult, CourseTableEntry, CourseGrading
from factory import ServiceFactory, create_async_context
from service import CourseService, DepartmentService, SemesterService, StudentService, MajorService, UserService, \
    InstructorService

sid = {}
sec_id = {}
cls_id = {}
did = {}
mid = {}

inserted = set()
cd = {}
cs = json.load(open('data/courses.json', encoding='utf-8'))
ps = json.load(open('data/coursePrerequisites.json', encoding='utf-8'))
ss = json.load(open('data/semesters.json', encoding='utf-8'))
ds = json.load(open('data/departments.json', encoding='utf-8'))
ms = json.load(open('data/majors.json', encoding='utf-8'))
css = json.load(open('data/courseSections.json', encoding='utf-8'))
cscs = json.load(open('data/courseSectionClasses.json', encoding='utf-8'))

mcc = json.load(open('data/majorCompulsoryCourses.json', encoding='utf-8'))
mec = json.load(open('data/majorElectiveCourses.json', encoding='utf-8'))

us = json.load(open('data/users.json', encoding='utf-8'))

sc = json.load(open('data/studentCourses.json', encoding='utf-8'))

rcs: Optional[CourseService] = None
rds: Optional[DepartmentService] = None
ris: Optional[InstructorService] = None
rms: Optional[MajorService] = None
rss: Optional[SemesterService] = None
rsts: Optional[StudentService] = None
rus: Optional[UserService] = None


async def pc(pre_json: Optional[dict]):
    if pre_json is None:
        return None
    if 'And' in pre_json.get('@type', '') or 'And' in pre_json.get('@class', ''):
        return AndPrerequisite(terms=[await pc(t) for t in pre_json['terms']])
    elif 'Or' in pre_json.get('@type', '') or 'Or' in pre_json.get('@class', ''):
        return OrPrerequisite(terms=[await pc(t) for t in pre_json['terms']])
    else:
        await insert_course(cd[pre_json['courseID']])
        return CoursePrerequisite(course_id=pre_json['courseID'])


async def insert_course(c):
    if c['id'] in inserted:
        return
    p = ps[c['id']]
    inserted.add(c['id'])
    await rcs.add_course(c['id'], c['name'], c['credit'], c['classHour'], CourseGrading[c['grading']], await pc(p))


async def test_add_course():
    async def add_one(c):
        cd[c['id']] = c
        await insert_course(c)
        sections = css[c['id']]
        for sem in list(sections.keys())[1:]:
            for s in sections[f'{sem}'][1:]:
                for s2 in s:
                    section_id = await rcs.add_course_section(c['id'], sid[int(sem)], s2['name'], s2['totalCapacity'])
                    sec_id[s2['id']] = section_id
                    cls = cscs[f"{s2['id']}"][1]
                    for cl in cls:
                        class_id = await rcs.add_course_section_class(section_id, cl['instructor']['id'],
                                                                      DayOfWeek[cl['dayOfWeek']],
                                                                      cl['weekList'], cl['classBegin'], cl['classEnd'],
                                                                      cl['location'])
                        cls_id[cl['id']] = class_id

    await asyncio.gather(*[add_one(c) for c in cs])


async def test_add_semester():
    async def add_one(s):
        b = datetime.fromtimestamp(float(s['begin']) / 1000).date()
        e = datetime.fromtimestamp(float(s['end']) / 1000).date()
        sid[s['id']] = await rss.add_semester(s['name'], b, e)

    await asyncio.gather(*[add_one(s) for s in ss])


async def test_add_department():
    async def add_one(d):
        did[d['id']] = await rds.add_department(d['name'])

    await asyncio.gather(*[add_one(d) for d in ds])


async def test_add_major():
    async def add_one(m):
        mid[m['id']] = await rms.add_major(m['name'], did[m['department']['id']])

    await asyncio.gather(*[add_one(m) for m in ms])


async def test_add_major_course():
    async def add_one_major(m, cc, ec):
        for c in cc:
            await rms.add_major_compulsory_course(mid[int(m)], c)
        for c in ec:
            await rms.add_major_elective_course(mid[int(m)], c)

    await asyncio.gather(*[add_one_major(m, mcc[str(m)][1], mec[str(m)][1]) for m in mid])


async def test_add_user():
    async def add_one(u):
        if 'Instructor' in u['@type']:
            await (ris.add_instructor(u['id'], u['fullName'].split(',')[0], u['fullName'].split(',')[1]))
        else:
            await (rsts.add_student(u['id'], mid[u['major']['id']], u['fullName'].split(',')[0],
                                    u['fullName'].split(',')[1],
                                    datetime.fromtimestamp(u['enrolledDate'] / 1000).date()))

    await asyncio.gather(*[add_one(u) for u in us])


async def test_drop_except():
    async def drop_one_student(stu, gradebook):
        exc = 0
        for sec in gradebook:
            if sec == '@type' or gradebook[sec] is None:
                continue
            try:
                await rsts.drop_course(int(stu), sec_id[int(sec)])
            except Exception:
                exc += 1
        return exc

    return sum(await asyncio.gather(*[drop_one_student(k, sc[k]) for k in sc]))


async def test_import_course():
    async def import_one_student(stu, gradebook):
        ok = 0
        for sec in gradebook:
            if sec == '@type':
                continue
            grade = gradebook[sec]
            if grade is None:
                pass
            else:
                if isinstance(grade, dict):
                    grade = grade['mark']
                if isinstance(grade, list):
                    grade = PassOrFailGrade[grade[1]]
            try:
                await rsts.add_enrolled_course_with_grade(int(stu), sec_id[int(sec)], grade)
                ok += 1
            except Exception:
                pass
        return ok

    return sum(await asyncio.gather(*[import_one_student(k, sc[k]) for k in sc]))


async def test_course_table(path):
    async def test_one(p, a):
        ans = {DayOfWeek[k]: [CourseTableEntry(e['courseFullName'],
                                               Instructor(e['instructor']['id'],
                                                          e['instructor']['fullName']
                                                          ),
                                               e['classBegin'],
                                               e['classEnd'],
                                               e['location']
                                               ) for e in a['table'][k]].sort(key=lambda it: it.course_full_name)
               for k in a['table']}
        s = p[1][0]
        d = datetime.fromtimestamp(p[1][1] * 86400).date()
        res = await rsts.get_course_table(s, d)
        res = {k: res[k].sort(key=lambda it: it.course_full_name) for k in res.keys()}
        if ans == res:
            return 1
        else:
            return 0

    ok = 0
    for x in os.listdir(path):
        if (not x.endswith('.json')) or 'Result' in x:
            continue
        params = json.load(open(f'{path}/{x}', encoding='utf-8'))
        ans = json.load(open(f'{path}/{x.split(".")[0]}Result.json', encoding='utf-8'))
        ok += sum(await asyncio.gather(*[test_one(p, a) for (p, a) in zip(params, ans)]))
    return ok


async def test_enroll_course(path):
    async def test_one(p, a):
        stu = p[1][0]
        sec = int(p[1][1])
        sec = sec_id[sec] if sec in sec_id else sec
        res = await rsts.enroll_course(stu, sec)
        ans = EnrollResult[a[1]]
        if res is ans:
            return 1
        else:
            return 0
            # print(f'ENROLL RESULT ERROR: {res}, EXPECTED: {ans}')

    ok = 0
    for x in os.listdir(path):
        if (not x.endswith('.json')) or 'Result' in x:
            continue
        params = json.load(open(f'{path}/{x}'))
        ans = json.load(open(f'{path}/{x.split(".")[0]}Result.json'))
        ok += sum(await asyncio.gather(*[test_one(p, a) for p, a in zip(params, ans)]))
    return ok


async def test_drop_course(path):
    async def drop_one(p):
        stu = p[1][0]
        sec = int(p[1][1])
        sec = sec_id[sec] if sec in sec_id else sec
        try:
            await rsts.drop_course(stu, sec)
            return 1
        except Exception:
            return 0
            # print(f'DROP FAIL {stu} {sec}')

    ok = 0
    for x in os.listdir(path):
        if (not x.endswith('.json')) or 'Result' in x:
            continue
        params = json.load(open(f'{path}/{x}'))
        ans = json.load(open(f'{path}/{x.split(".")[0]}Result.json'))
        ok += sum(await asyncio.gather(*[drop_one(p) for p, a in zip(params, ans) if a[1]=='SUCCESS']))
    return ok


async def json_query_reader(f):
    async def query_one(q):
        x = q[1]
        if x[8] is not None:
            x[8] = CourseType[x[8][1]]
        if x[5] is not None:
            x[5] = DayOfWeek[x[5][1]]
        if x[7] is not None:
            x[7] = x[7][1]
        return await rsts.search_course(student_id=x[0],
                                        semester_id=sid[x[1]],
                                        search_cid=x[2],
                                        search_name=x[3],
                                        search_instructor=x[4],
                                        search_day_of_week=x[5],
                                        search_class_time=x[6],
                                        search_class_locations=x[7],
                                        search_course_type=x[8],
                                        ignore_full=x[9],
                                        ignore_conflict=x[10],
                                        ignore_passed=x[11],
                                        ignore_missing_prerequisites=x[12],
                                        page_size=x[13],
                                        page_index=x[14])

    query = json.load(f)
    return await asyncio.gather(*[query_one(q) for q in query])


async def json_answer_reader(f):
    ans = json.load(f)
    res = []
    for a in ans:
        r = []
        for e in a[1]:
            cos = Course(e['course']['id'], e['course']['name'], e['course']['credit'], e['course']['classHour'],
                         CourseGrading[e['course']['grading']])
            sec = CourseSection(sec_id[e['section']['id']], e['section']['name'], e['section']['totalCapacity'],
                                e['section']['leftCapacity'])
            cls = [CourseSectionClass(cls_id[c['id']], Instructor(c['instructor']['id'], c['instructor']['fullName']),
                                      DayOfWeek[c['dayOfWeek']], c['weekList'], c['classBegin'], c['classEnd'],
                                      c['location']) for c in e['sectionClasses']]
            r.append(CourseSearchEntry(cos, sec, cls, e['conflictCourseNames']))
        res.append(r)
    return res


async def test_query(path: str):
    ok = 0
    for x in os.listdir(path):
        if (not x.endswith('.json')) or 'Result' in x:
            continue
        res = await json_query_reader(open(f'{path}/{x}', encoding='utf-8'))
        ans = await json_answer_reader(open(f"{path}/{x.split('.')[0]}Result.json", encoding='utf-8'))
        for r, a in zip(res, ans):
            if r == a:
                ok += 1
    return ok


async def main():
    async with create_async_context() as context:
        factory = ServiceFactory(context)
        if hasattr(factory, 'async_init') and callable(getattr(factory, 'async_init')):
            await factory.async_init()
        global rcs, rds, ris, rms, rss, rsts, rus
        rcs = factory.create_course_service()
        rds = factory.create_department_service()
        ris = factory.create_instructor_service()
        rms = factory.create_major_service()
        rss = factory.create_semester_service()
        rsts = factory.create_student_service()
        rus = factory.create_user_service()

        start = time()
        print('Import departments')
        await test_add_department()
        print('Import majors')
        await test_add_major()
        print('Import users')
        await test_add_user()
        print('Import semesters')
        await test_add_semester()
        print('Import courses')
        await test_add_course()
        print('Import major courses')
        await test_add_major_course()
        print(f'Import time usage: {round(time() - start, 2)}s')

        print('Testing search course 1')
        start = time()
        ok = await test_query('data/searchCourse1')
        print(f'Test search course 1: {ok}')
        print(f'Test search course 1 time: {round(time() - start, 2)}s')

        print('Testing enroll course 1')
        start = time()
        ok = await test_enroll_course('data/enrollCourse1')
        print(f'Test enroll course 1: {ok}')
        print(f'Test enroll course 1 time: {round(time() - start, 2)}s')

        print('Testing drop enrolled course 1')
        start = time()
        ok = await test_drop_course('data/enrollCourse1')
        print(f'Test drop enrolled course 1: {ok}')
        print(f'Test drop enrolled course 1 time: {round(time()-start, 2)}s')

        print('Importing student courses')
        start = time()
        ok = await test_import_course()
        print(f'Import student course: {ok}')
        print(f'Import student course time: {round(time() - start, 2)}s')

        print('Testing drop course exception')
        start = time()
        exc = await test_drop_except()
        print(f'Test drop course exception: {exc}')
        print(f'Test drop course exception time: {round(time()-start, 2)}s')

        print('Testing course table 2')
        start = time()
        ok = await test_course_table('data/courseTable2')
        print(f'Test course table 2: {ok}')
        print(f'Test course table 2 time: {round(time() - start, 2)}s')

        print('Testing search course 2')
        start = time()
        ok = await test_query('data/searchCourse2')
        print(f'Test search course 2: {ok}')
        print(f'Test search course 2 time: {round(time() - start, 2)}s')

        print('Testing enroll course 2')
        start = time()
        ok = await test_enroll_course('data/enrollCourse2')
        print(f'Test enroll course 2: {ok}')
        print(f'Test enroll course 2 time: {round(time() - start, 2)}s')

        print('Testing drop enrolled course 2')
        start = time()
        ok = await test_drop_course('data/enrollCourse2')
        print(f'Test drop enrolled course 2: {ok}')
        print(f'Test drop enrolled course 2 time: {round(time()-start, 2)}s')


if __name__ == '__main__':
    asyncio.run(main())
