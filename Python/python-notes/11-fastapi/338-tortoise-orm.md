---

# 338. Tortoise ORM
# हिंदी में: Tortoise ORM (Async-first, Django जैसा ORM)

---

## 🔵 Simple Definition (English)
Tortoise ORM is an async-first object-relational mapper for Python with an API that looks like Django's ORM: `Model.filter(...)`, `Model.get(...)`, `Model.create(...)`. Every database call is awaited, and relations are loaded explicitly with `prefetch_related`. It integrates with FastAPI and Pydantic.

## 🔵 सरल परिभाषा (Hindi)
Tortoise ORM Python का async-first object-relational mapper है जिसकी API Django ORM जैसी दिखती है: `Model.filter(...)`, `Model.get(...)`, `Model.create(...)`। हर database call `await` होता है, और relations `prefetch_related` से साफ तौर पर load होते हैं। यह FastAPI और Pydantic के साथ जुड़ता है।

---

## 🔴 Problem it Solves
SQLAlchemy is powerful but has a large API and, in async mode, lazy-loading traps. Django's ORM is friendly but sync-first and tied to Django. Tortoise gives a small, familiar API (no sessions to manage), designed for asyncio from day one, with built-in Pydantic model generation, so small and medium async services need less boilerplate.

## 🔴 यह क्यों बना? (Hindi)
SQLAlchemy शक्तिशाली है पर उसकी API बड़ी है और async mode में lazy-loading के जाल हैं। Django ORM friendly है पर sync-first है और Django से बंधा है। Tortoise एक छोटी, जानी-पहचानी API देता है (sessions संभालने की जरूरत नहीं), जो शुरू से asyncio के लिए बनी है और Pydantic models बनाना भी built-in है, इसलिए छोटी और मध्यम async services में boilerplate कम लगता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → pip install tortoise-orm (plus a driver: aiosqlite / asyncpg)
Step 2 → Define models: class X(Model) with fields.IntField, CharField, ForeignKeyField
Step 3 → await Tortoise.init(db_url=..., modules={"models": ["app.models"]})
Step 4 → await Tortoise.generate_schemas()  (dev only; use Aerich for migrations)
Step 5 → Queries: await X.filter(...), await X.get(...), await X.create(...)
Step 6 → Relations: .prefetch_related("books") or select_related("author")
Step 7 → Transactions: async with in_transaction(): ...
Step 8 → await Tortoise.close_connections() on shutdown
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → pip install tortoise-orm (साथ में driver: aiosqlite / asyncpg)
Step 2 → Models: class X(Model) में fields.IntField, CharField, ForeignKeyField
Step 3 → await Tortoise.init(db_url=..., modules={"models": ["app.models"]})
Step 4 → await Tortoise.generate_schemas()  (सिर्फ dev; migrations के लिए Aerich)
Step 5 → Queries: await X.filter(...), await X.get(...), await X.create(...)
Step 6 → Relations: .prefetch_related("books") या select_related("author")
Step 7 → Transactions: async with in_transaction(): ...
Step 8 → Shutdown पर await Tortoise.close_connections()
```

---

## 🟡 Real World Example
A small to-do or booking microservice: tasks with owners, `GET /tasks/{id}` and `POST /tasks`. The team knows Django and wants async without learning sessions. They use Tortoise for models, `pydantic_model_creator` for response schemas, and `RegisterTortoise` in the FastAPI lifespan, which starts and stops the DB connections.

## 🟡 Real Example Hindi mein
एक छोटी to-do या booking microservice: owners के साथ tasks, `GET /tasks/{id}` और `POST /tasks`। Team Django जानती है और sessions सीखे बिना async चाहती है। वे models के लिए Tortoise, response schemas के लिए `pydantic_model_creator`, और FastAPI lifespan में `RegisterTortoise` उपयोग करते हैं, जो DB connections शुरू और बंद करता है।

---

## 💻 Code Example — Basic
```python
# Basic: models, relations, filters, prefetch, transaction rollback (verified, tortoise-orm 1.1.9)
import asyncio                                                   # run the coroutine
from tortoise import Tortoise, fields                            # init + field types
from tortoise.models import Model                                # base model
from tortoise.transactions import in_transaction                 # transaction context manager


class Author(Model):                                             # authors table
    id = fields.IntField(primary_key=True)                       # integer primary key
    name = fields.CharField(max_length=50)                       # VARCHAR(50)
    books: fields.ReverseRelation["Book"]                        # reverse side of the FK (type hint only)


class Book(Model):                                               # books table
    id = fields.IntField(primary_key=True)                       # primary key
    title = fields.CharField(max_length=100)                     # title
    pages = fields.IntField(default=100)                         # int with default
    author: fields.ForeignKeyRelation[Author] = fields.ForeignKeyField(
        "models.Author", related_name="books")                   # FK to Author, reverse name "books"


async def main() -> None:                                        # async entry point
    await Tortoise.init(db_url="sqlite://:memory:", modules={"models": ["__main__"]})   # connect + register
    await Tortoise.generate_schemas()                            # CREATE TABLEs
    a = await Author.create(name="Rahul")                        # INSERT, returns instance
    await Book.create(title="Py", pages=300, author=a)           # insert a book
    await Book.bulk_create([Book(title="JS", pages=120, author=a), Book(title="Go", pages=80, author=a)])
    print(await Book.filter(pages__gt=100).order_by("pages").values_list("title", flat=True))   # lookups with __
    print(await Book.filter(author__name="Rahul").count())       # filter across relation
    au = await Author.get(id=a.id).prefetch_related("books")     # eager load the books
    print([b.title for b in au.books])                           # safe, already loaded
    print(await Author.get_or_none(id=99))                       # None instead of an exception
    try:                                                         # transaction rollback demo
        async with in_transaction():                             # begin
            await Book.create(title="Temp", author=a)            # insert inside transaction
            raise RuntimeError("boom")                           # force failure
    except RuntimeError:                                         # error caught outside
        pass                                                     # nothing to do
    print(await Book.all().count())                              # still 3 => rolled back
    await Tortoise.close_connections()                           # cleanup


asyncio.run(main())                                              # run

# Output (verified):
# ['JS', 'Py']
# 3
# ['Py', 'JS', 'Go']
# None
# 3
```

## 💻 Code Example — Advanced
```python
# Production style: FastAPI + RegisterTortoise in lifespan + auto Pydantic schema (verified)
from contextlib import asynccontextmanager                       # lifespan helper
from collections.abc import AsyncIterator                        # lifespan return type
from fastapi import FastAPI, HTTPException                       # FastAPI core
from fastapi.testclient import TestClient                        # test client
from pydantic import BaseModel                                   # request schema
from tortoise import fields                                      # field types
from tortoise.contrib.fastapi import RegisterTortoise            # FastAPI integration
from tortoise.contrib.pydantic import pydantic_model_creator     # model -> Pydantic schema
from tortoise.models import Model                                # base model


class Task(Model):                                               # tasks table
    id = fields.IntField(primary_key=True)                       # PK
    title = fields.CharField(max_length=80)                      # title
    done = fields.BooleanField(default=False)                    # flag


TaskOut = pydantic_model_creator(Task, name="TaskOut")           # auto-generated response schema


class TaskIn(BaseModel):                                         # request body
    title: str                                                   # only the title is accepted


@asynccontextmanager                                             # startup + shutdown
async def lifespan(app: FastAPI) -> AsyncIterator[None]:         # FastAPI lifespan
    async with RegisterTortoise(                                 # init on start, close on exit
        app,                                                     # attach to this app
        db_url="sqlite://:memory:",                              # prod: "postgres://user:pw@host:5432/db"
        modules={"models": ["__main__"]},                        # where models live
        generate_schemas=True,                                   # dev only; use Aerich in prod
    ):
        yield                                                    # app serves requests here


app: FastAPI = FastAPI(lifespan=lifespan)                        # create app


@app.post("/tasks", status_code=201)                             # create a task
async def create(body: TaskIn):                                  # async route
    obj = await Task.create(title=body.title)                    # INSERT
    return await TaskOut.from_tortoise_orm(obj)                  # model -> Pydantic -> JSON


@app.get("/tasks/{task_id}")                                     # read a task
async def read(task_id: int):                                    # async route
    obj = await Task.get_or_none(id=task_id)                     # None if missing
    if obj is None:                                              # not found
        raise HTTPException(404, "not found")                    # 404
    return await TaskOut.from_tortoise_orm(obj)                  # serialize


with TestClient(app) as c:                                       # runs lifespan startup/shutdown
    print(c.post("/tasks", json={"title": "ship"}).json())       # create
    print(c.get("/tasks/1").json())                              # read
    print(c.get("/tasks/5").status_code)                         # missing

# Output (verified):
# {'id': 1, 'title': 'ship', 'done': False}
# {'id': 1, 'title': 'ship', 'done': False}
# 404
```
Not covered by this run: Aerich migrations and PostgreSQL (`asyncpg`) were not run here.

---

## 🟠 JavaScript vs Python Comparison

| Concept | Tortoise ORM | JavaScript (Prisma / Sequelize) |
|---------|--------------|---------------------------------|
| Create | `await Task.create(title="x")` | `await prisma.task.create({data})` |
| Filter | `Task.filter(done=False)` | `prisma.task.findMany({where})` |
| Relation eager load | `.prefetch_related("books")` | `include: { books: true }` |
| Transaction | `async with in_transaction()` | `prisma.$transaction` |
| Migrations | Aerich | `prisma migrate` |

```python
# Python way
tasks = await Task.filter(done=False).order_by("-id").limit(10)   # query + await
```
```javascript
// JavaScript way (Prisma)
const tasks = await prisma.task.findMany({            // query
  where: { done: false }, orderBy: { id: "desc" }, take: 10,   // filters
});
```

Key difference: Tortoise queries are lazy query-set objects that run only when awaited, like Django; Prisma runs on each call. There is no session object in Tortoise.

---

## 🟠 FastAPI Connection
Tortoise ships `tortoise.contrib.fastapi.RegisterTortoise` (use inside `lifespan`) and `pydantic_model_creator` to build response models from your ORM models. Routes are `async def` and call models directly: no `Depends(get_db)` needed, because there is no per-request session. In tests use `sqlite://:memory:` plus the `TestClient` context manager so the lifespan runs.

```python
# FastAPI example — list with filter and pydantic list schema
from tortoise.contrib.pydantic import pydantic_queryset_creator   # list schema generator

TaskList = pydantic_queryset_creator(Task)                         # schema for many tasks


@app.get("/tasks")                                                 # list endpoint
async def list_tasks(done: bool = False):                          # query parameter
    return await TaskList.from_queryset(Task.filter(done=done))    # query -> JSON list
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting `await`
✅ Correct: await queryset / `create` / `save`

```python
# Wrong — returns a QuerySet object, nothing is fetched, no error
tasks = Task.filter(done=False)
print(tasks)                      # <QuerySet ...> not data
# Right
tasks = await Task.filter(done=False)
```

❌ Mistake 2: Accessing a relation without `prefetch_related` / `fetch_related`
✅ Correct: load it explicitly

```python
# Wrong — a ReverseRelation not yet fetched: iterating it raises NoValuesFetched
au = await Author.get(id=1)
print([b.title for b in au.books])
# Right
au = await Author.get(id=1).prefetch_related("books")
print([b.title for b in au.books])
```

❌ Mistake 3: Using `generate_schemas=True` in production
✅ Correct: use Aerich migrations; `generate_schemas` only creates missing tables

```python
# Wrong (prod) — column changes are never applied
RegisterTortoise(app, db_url=url, modules=mods, generate_schemas=True)
# Right — aerich init-db / aerich migrate / aerich upgrade
RegisterTortoise(app, db_url=url, modules=mods, generate_schemas=False)
```

---

## 🧠 Tricky Interview Question

```python
# What does each line print?
q = Task.filter(done=False)           # (1)
print(type(q).__name__)
rows = await q                        # (2)
print(type(rows).__name__)
one = await Task.get(id=999)          # (3)
```
Answer: (1) `QuerySet`: building the query does not touch the database (lazy, like Django). (2) `list`: awaiting runs the SQL and returns a list of `Task` instances. (3) `Task.get()` raises `tortoise.exceptions.DoesNotExist` when nothing matches (and `MultipleObjectsReturned` if several do). Use `get_or_none()` if "missing" is a normal case.

---

## ⚫ Interview Questions + Answers

Q1: How is Tortoise different from SQLAlchemy?
A1: Tortoise is smaller, async-only, with a Django-like API and no explicit sessions. SQLAlchemy has Core + ORM, supports sync and async, has a much larger ecosystem, and finer control, but a steeper learning curve.

Q2: How do you do migrations in Tortoise?
A2: With Aerich (`aerich init`, `aerich init-db`, `aerich migrate`, `aerich upgrade`). It diffs the models against the last migration state and writes SQL migration files.

Q3: What is `prefetch_related` vs `select_related`?
A3: `select_related` JOINs forward (FK/OneToOne) relations in the same query. `prefetch_related` runs one extra query per relation and attaches results, used for reverse and many-to-many relations.

Q4: How do you do atomic operations?
A4: `async with in_transaction():` or the `@atomic()` decorator. If an exception escapes the block, the transaction rolls back.

Q5: Can you do raw SQL?
A5: Yes: `from tortoise import connections; conn = connections.get("default"); await conn.execute_query_dict("SELECT ...")`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Small/medium async services; team likes Django-style APIs
- You want quick Pydantic schema generation

❌ Avoid when:
- You need very complex SQL, window functions in the ORM, or multi-database features (SQLAlchemy is stronger)
- The team already standardised on SQLAlchemy + Alembic
- You need a very large ecosystem and long-term hiring familiarity

---

## 📊 Visual Diagram
```
 FastAPI lifespan ──► RegisterTortoise ──► Tortoise.init(db_url, modules)
                                                │
 async route ──► Task.filter(...)  (QuerySet, lazy)
                    │ await
                    ▼
               SQL via asyncpg / aiosqlite ──► DB
                    │
        list[Task] ──► TaskOut.from_tortoise_orm ──► JSON
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| QuerySet | Lazy query object | Lazy query object |
| `prefetch_related` | Load relations with extra query | Relations को अतिरिक्त query से लाना |
| `in_transaction` | Atomic block | Atomic block (सब या कुछ नहीं) |
| Aerich | Tortoise migration tool | Tortoise का migration tool |
| `RegisterTortoise` | FastAPI integration | FastAPI integration |
| `DoesNotExist` | `get()` found nothing | `get()` को कुछ नहीं मिला |

---

## ⚡ 3-Line Summary
English: Tortoise ORM is an async-first, Django-like ORM: define models, `await` queries, and use `prefetch_related` for relations. In FastAPI use `RegisterTortoise` in the lifespan and `pydantic_model_creator` for responses. Use Aerich for migrations, not `generate_schemas`.
Hindi: Tortoise ORM async-first, Django जैसा ORM है: models बनाएं, queries को `await` करें, और relations के लिए `prefetch_related` उपयोग करें। FastAPI में lifespan में `RegisterTortoise` और responses के लिए `pydantic_model_creator` उपयोग करें। Migrations के लिए Aerich उपयोग करें, `generate_schemas` नहीं।

---

## ➡️ Next Topic
**339. Beanie (MongoDB ODM)** — the same async, Pydantic-friendly idea, but for MongoDB documents.
