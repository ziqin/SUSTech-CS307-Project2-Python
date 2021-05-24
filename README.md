# CS307 Spring 2021 Database Project 2

## 0. Introduction

In Project 2, you will continue working on an educational management system. To ease the assessment, we have designed a
set of APIs, upon which you will implement the system.

We provide interfaces in two languages: Java and Python. You can use either of them upon your preference. Notice that
due to the inherent differences between these two languages, the **scoring policy** may also be different.

- Java version: <https://github.com/NewbieOrange/SUSTech-SQL-Project2-Public>
- Python version: <https://github.com/ziqin/SUSTech-CS307-Project2-Python>

## 1. Get Started

### Step 1: Download provided code skeleton

#### Approach A (Preferred): Clone with Git

If you have git installed, you can execute the following command to clone this Project:

```shell
git clone https://github.com/ziqin/SUSTech-CS307-Project2-Python.git
```

Please do not create a public fork of this GitHub repository before the deadline of project submission, otherwise you
may leak your source code.

#### Approach B: Download Zip directly

Download zip: <https://github.com/ziqin/SUSTech-CS307-Project2-Python/archive/refs/heads/main.zip>

### Step 2 (Optional): Environment setup

It is a good practice to create a separate virtual environment (venv) for each
Python project:

```shell
cd SUSTech-CS307-Project2-Python
python3 -m venv venv
```

Enter the virtual environment:

```shell
source ./venv/bin/activate
```

Install dependent libraries in the virtual environment:

```shell
pip install -U pip  # (Optional) Upgrade pip in the venv
pip install -r requirements.txt  # Install dependent libraries in the venv
```

To leave the virtual environment, execute:

```shell
deactivate
```

Note that you can create a virtual environment with a project wizard in some IDEs (e.g., PyCharm).

### Step 3: Start development

Please read the following text to learn about the project requirement.

## 2. Programming Requirements

### API Specification

The code skeleton structure is as follows:

- `dto` module: defines a set of data classes. Your implementation will use them as parameters or returned values.
- `service` package: defines abstract classes of services to which you should pay special attention. You need to
  create a concrete subclass for each abstract class.
- `exception` module: defines exceptions that you should `raise` if something went wrong.
- `factory` module: defines `ServiceFactory` that you need to **modify** to create your service instances.
- `config.ini`: configures database connection. You can employ the Python standard library package
  [configparser](https://docs.python.org/3/library/configparser.html) to parse this file.
- `requirements.txt`: specifies dependent Python libraries for the project. For more details, you can refer to the [pip
  documentation about Requirements Files](https://pip.pypa.io/en/stable/user_guide/#requirements-files).

### Your Tasks

- Design your (PostgreSQL) database to satisfy the API requirements.
- Extend the abstract classes in the `service` package and modifies the `ServiceFactory` class to pass testcases.
- Profile your implementation and find ways to speed it up.
- (Optional) Find other ways to implement similar functionalities as our interfaces and compare (some of) them. Discuss
  whether they are better, worse or have different use cases.

Here is a reference implementation. It shows you how to override one method of an abstract service. To get a service
working, you will have to override **all its abstract methods**.

```python
"""service_impl/department_service.py: A concrete subclass of service.DepartmentService for reference"""
import asyncpg

from service import DepartmentService
from exception import IntegrityViolationError


class DepartmentServiceImpl(DepartmentService):
    def __init__(self, pool: asyncpg.Pool):
        self._pool: asyncpg.Pool = pool

    async def add_department(self, name: str) -> int:
        async with self._pool.acquire() as conn:
            try:
                return await conn.fetchval('insert into department (name) values ($1) returning id', name)
            except asyncpg.UniqueViolationError as e:
                raise IntegrityViolationError from e

    # Some methods are omitted
```

You also need to modify `factory.py`, where you should implement `create_***_service`methods of `ServiceFactory` to
instantiate concrete services. Please don't modify the signatures of given methods.

```python
"""factory.py"""
from configparser import ConfigParser
from pathlib import Path

import asyncpg

from service import *
from service_impl.department_service import DepartmentServiceImpl


def create_async_context():
    # You can customize the async context manager in this function
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
        self._conn_pool = context

    async def async_init(self):
        pass

    def create_department_service(self) -> DepartmentService:
        return DepartmentServiceImpl(self._conn_pool)

    # Some methods are omitted
```

### Additional API Conventions

- To leverage I/O multiplexing, we use [asynchronous API](https://docs.python.org/3/library/asyncio-task.html) for all
  services.
- All `add*()` methods with return value of int should return the (presumably auto-generated) ID, which can be used to
  query added entities.
- All arguments are guaranteed to follow the [type hints](https://docs.python.org/3/library/typing.html). The benchmark
  program won't pass a `None` as argument unless the parameter is explicitly annotated with `Optional`.
- For return types with type hints, return values (and their fields) should not be `None`, unless explicitly documented.
  Use `[]`, `{}`, `set()` or their equivalents instead of `None` for empty container as return values.
- Your implementation should raise `NotImplementedError` if a method is not actually implemented, so that tests can
  fail quickly.

### Rules

- Data should be persisted on disk after each write operation instead of only modified in RAM. If you introduced a cache
  layer, you have to enforce the consistency. You should also ensure the durability in case of a sudden shutdown.
- **DO NOT** use any existing Object-Relational Mapping (ORM) frameworks such as _SQLAlchemy_.
- You **DO NOT** need to spend time on GUI/WEB, as we do not give extra scores for them.
- You should **NOT** modify any given Python files except `factory.py`. You should create your own concrete service
  classes in new file(s).
- We use [**pip**](https://pip.pypa.io/) to manage dependent python libraries. If you want to use a third-party library in your project, you need to
  record it in `requirements.txt`. Your dependencies should be downloadable from
  [The Python Package Index (PyPI)](https://pypi.org/).


## 3. What to submit?

- `cs307.sql`: An file with table creation statements, constraints, index creation statements, and stored procedures if
  you have, but **without** data in tables.
- `src.tar.gz`: An archive containing all your Python source files. We have provided a Python script named `bundle.py`
  for you to create a Gzip-compressed archive in a common format.


## 4. What to deliver?

- **PASS BASE TEST:** First and foremost, you should pass the base testcases, this is the basic requirement.

- **IMPROVE YOUR EFFICIENCY:** After you passed the base tests, you need to find ways to improve the performance of your implementation. You can work on the following aspects.

  #### Resource Consumption

    - Memory Consumption: How much memory your database takes?
    - Disk Consumption: How much disk space your database takes? How are they distributed? (index, data, other info?)

  #### Speed

    - Data Import Speed: How much time your database need to import all data?
    - Data Modify Speed (Insertion, Update, Deletion): How much time your database need to change one/one hundred/one million rows?
    - Data Query Speed: How much time your database need to fetch one/one hundred/one million rows?
    - Cache Policy: How much time your database need to fetch a row if the row was just accessed by others?

  #### Concurrency

    - Simultaneous Query Number: How many queries can your database handles simultaneously?
    - Simultaneous Query Latency: How long does it take to query if there are many users connect to your database simultaneously.
    - Transaction Safety: Is your database safe with many users concurrently writing/reading to it?

  #### Correctness

    - Malformed Data Identification: Can your database identify the malformed data automatically?
    - ACID Principle


- **(Optional) DIFFERENT WAYS SAME GOAL?** Can you find other ways to implement these functionalities? Are they **BETTER/WORSE/USECASE-RELATED?** Please do share us your amazing ideas.


## 5. Project Timeline

Code submission due by **June 6th**.

Presentation (Online): **June 15th**.
