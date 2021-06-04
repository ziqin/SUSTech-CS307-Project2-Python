#!/usr/bin/env python3

import asyncio
import json
import os

from time import time
from datetime import datetime, timedelta
from typing import Optional

import humps
from tqdm import tqdm

from dto import AndPrerequisite, OrPrerequisite, CoursePrerequisite, PassOrFailGrade, CourseSearchEntry, Course, \
    CourseSection, CourseSectionClass, CourseType, DayOfWeek, EnrollResult, CourseTableEntry, CourseGrading
from factory import ServiceFactory, create_async_context
from service import CourseService, DepartmentService, SemesterService, StudentService, MajorService, UserService, \
    InstructorService

sid = {}
sec_id = {}
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
    for c in cs:
        cd[c['id']] = c
    for c in cs:
        await insert_course(c)
        sections = css[c['id']]
        for sem in range(1, 4):
            for s in sections[f'{sem}'][1:]:
                for ss in s:
                    section_id = await rcs.add_course_section(c['id'], sid[sem], ss['name'], ss['totalCapacity'])
                    sec_id[ss['id']] = section_id
                    cls = cscs[f"{ss['id']}"][1]
                    for cl in cls:
                        await rcs.add_course_section_class(section_id, cl['instructor']['id'],
                                                           DayOfWeek[cl['dayOfWeek']],
                                                           cl['weekList'], cl['classBegin'], cl['classEnd'],
                                                           cl['location'])


async def test_add_semester():
    async def one_iter(s):
        b = datetime.fromtimestamp(float(s['begin']) / 1000).date()
        e = datetime.fromtimestamp(float(s['end']) / 1000).date()
        sid[s['id']] = await rss.add_semester(s['name'], b, e)

    await asyncio.gather(*[one_iter(s) for s in ss])


async def test_add_department():
    async def one_iter(d):
        did[d['id']] = await rds.add_department(d['name'])

    await asyncio.gather(*[one_iter(d) for d in ds])


async def test_add_major():
    async def one_iter(m):
        mid[m['id']] = await rms.add_major(m['name'], did[m['department']['id']])

    await asyncio.gather(*[one_iter(m) for m in ms])


async def test_add_major_course():
    await asyncio.gather(*[(await rms.add_major_compulsory_course(mid[int(k)], c) for c in cc[1]) for k, cc in mcc.items()])
    await asyncio.gather(*[(await rms.add_major_elective_course(mid[int(k)], c) for c in ec[1]) for k, ec in mec.items()])


async def test_add_user():
    async def one_iter(u):
        if 'Instructor' in u['@type']:
            await ris.add_instructor(u['id'], u['fullName'].split(',')[0], u['fullName'].split(',')[1])
        else:
            await rsts.add_student(u['id'], mid[u['major']['id']], u['fullName'].split(',')[0],
                                   u['fullName'].split(',')[1], datetime.fromtimestamp(u['enrolledDate'] / 1000).date())
    await asyncio.gather(*[one_iter(u) for u in us])

async def test_select_course():
    failed_cnt = 0
    for k, s in sc.items():
        for si, c in s.items():
            if si != '@type':
                if c is not None:
                    if isinstance(c, list):
                        grade = PassOrFailGrade[c[1]]
                    elif isinstance(c, dict):
                        grade = c['mark']
                else:
                    grade = None
                await rsts.add_enrolled_course_with_grade(int(k), sec_id[int(si)], grade)
    for k, s in tqdm(sc.items()):
        for si, c in s.items():
            if si != '@type':
                if c is not None:
                    try:
                        await rsts.drop_course(int(k), sec_id[int(si)])
                        failed_cnt += 1
                    except:
                        pass
    print(f"There are {failed_cnt} failed to throw exception")


async def test_course_table(path):
    fail_cnt = 0
    for x in os.listdir(path):
        if (not x.endswith('.json')) or 'Result' in x:
            continue
        params = json.load(open(f'{path}/{x}', encoding='utf-8'))
        ans = json.load(open(f'{path}/{x.split(".")[0]}Result.json', encoding='utf-8'))
        for i, p in enumerate(params):
            a = ans[i]
            s, d = p[1][0], int(p[1][1])
            d = datetime(1970, 1, 1) + timedelta(days=d)
            r = await rsts.get_course_table(s, d.date())
            for k, v in a['table'].items():
                match = 0
                for x in v:
                    for z in r[DayOfWeek[k]]:
                        if z == CourseTableEntry(**humps.decamelize(x)):
                            match += 1
                if match != len(v):
                    fail_cnt += 1
    print(f'COURSE TABLE FAIL COUNT: {fail_cnt}')
    return fail_cnt


async def test_enroll_course(path):
    for x in os.listdir(path):
        if (not x.endswith('.json')) or 'Result' in x:
            continue
        params = json.load(open(f'{path}/{x}'))
        ans = json.load(open(f'{path}/{x.split(".")[0]}Result.json'))
        ls = []
        for i, p in enumerate(params):
            a = ans[i]
            s, cl = p[1][0], int(p[1][1])
            if cl in sec_id:
                cl = sec_id[cl]
            res = await rsts.enroll_course(s, cl)
            if res is not EnrollResult[a[1]]:
                print(f'Enroll result error: {res}, expected: {EnrollResult[a[1]]}')
            if res is EnrollResult.SUCCESS:
                ls.append((s, cl))
        for s, cl in ls:
            try:
                await rsts.drop_course(s, cl)
            except:
                print(f"DROP FAILED {s}, {cl}")


async def json_query_reader(f):
    query = json.load(f)
    res = []
    for q in query:
        x = q[1]
        if x[8] is not None:
            x[8] = CourseType[x[8][1]]
        if x[5] is not None:
            x[5] = DayOfWeek[x[5][1]]
        if x[7] is not None:
            x[7] = x[7][1]
        res.append(await rsts.search_course(student_id=x[0], semester_id=sid[x[1]], search_cid=x[2], search_name=x[3],
                                            search_instructor=x[4],
                                            search_day_of_week=x[5], search_class_time=x[6],
                                            search_class_locations=x[7],
                                            search_course_type=x[8], ignore_full=x[9], ignore_conflict=x[10],
                                            ignore_passed=x[11],
                                            ignore_missing_prerequisites=x[12], page_size=x[13],
                                            page_index=x[14]))
    return res


async def json_answer_reader(f):
    ans = json.load(f)
    res = []
    for a in ans:
        r = []
        for e in a[1]:
            entry = CourseSearchEntry(
                Course(**humps.decamelize(e['course'])),
                CourseSection(**humps.decamelize(e['section'])),
                [CourseSectionClass(**humps.decamelize(k)) for k in e['sectionClasses']],
                [s for s in e['conflictCourseNames']]
            )
            r.append(entry)
        res.append(r)
    return res


async def test_query(path: str):
    ok = 0
    for x in os.listdir(path):
        if (not x.endswith('.json')) or 'Result' in x:
            continue
        res = await json_query_reader(open(f'{path}/{x}', encoding='utf-8'))
        ans = await json_answer_reader(open(f"{path}/{x.split('.')[0]}Result.json", encoding='utf-8'))
        for (r, a) in zip(res, ans):
            if r == a:
                ok += 1
    print(f'Test search course: {ok}')


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
        print('Add departments')
        await test_add_department()
        print('Add majors')
        await test_add_major()
        print('Add users')
        await test_add_user()
        print('Add semesters')
        await test_add_semester()
        print('Add courses')
        await test_add_course()
        print('Add major courses')
        await test_add_major_course()
        print(f'Add time usage: {time() - start}s')
        print('Test search course 1')
        start = time()
        await test_query('data/searchCourse1')
        print(f'Test search course 1: {time() - start}s')
        print('Test enroll 1')
        start = time()
        await test_enroll_course('data/enrollCourse1')
        print(f'Test enroll course 1: {time() - start}s')
        print('Add student courses')
        await test_select_course()
        print('Test search course 2')
        start = time()
        await test_query('data/searchCourse2')
        print(f'Test search course 2: {time() - start}s')
        print('Test course table 2')
        start = time()
        await test_course_table('data/courseTable2')
        print(f'Test course table 2: {time() - start}s')
        print('Test enroll course 2')
        start = time()
        await test_enroll_course('data/enrollCourse2')
        print(f'Test enroll course 2: {time() - start}s')


if __name__ == '__main__':
    asyncio.run(main())
