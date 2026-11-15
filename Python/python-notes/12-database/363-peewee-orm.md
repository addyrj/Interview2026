---

# 363. Peewee ORM
# हिंदी में: Peewee ORM (छोटा और सरल Python ORM)

---

## 🔵 Simple Definition (English)
Peewee is a small, easy ORM (Object-Relational Mapper). You describe tables as Python classes, and Peewee writes the SQL for SQLite, MySQL or PostgreSQL. It is a light alternative to SQLAlchemy for small apps and scripts.

## 🔵 सरल परिभाषा (Hindi)
Peewee एक छोटा और आसान ORM (Object-Relational Mapper) है। आप tables को Python classes की तरह लिखते हैं और Peewee SQLite, MySQL या PostgreSQL के लिए SQL खुद बनाता है। छोटे apps और scripts के लिए यह SQLAlchemy का हल्का विकल्प है।

---

## 🔴 Problem it Solves
Writing raw SQL strings everywhere is repetitive, hard to refactor, and risky (typos, injection). Big ORMs like SQLAlchemy or Django ORM are powerful but have a large API to learn and need more setup. Peewee gives a small, readable API (`User.select().where(User.age > 18)`) in a single file with almost no configuration.

## 🔴 यह क्यों बना? (Hindi)
हर जगह raw SQL strings लिखना दोहराव वाला, refactor करने में कठिन और जोखिम भरा (typos, injection) है। SQLAlchemy या Django ORM जैसे बड़े ORMs शक्तिशाली हैं पर उनका API बड़ा है और setup ज्यादा चाहिए। Peewee छोटा, पढ़ने लायक API देता है (`User.select().where(User.age > 18)`), एक ही file में, लगभग बिना configuration के।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create a Database object:     db = SqliteDatabase("app.db") / PostgresqlDatabase(...)
Step 2 → Define Models (classes) with Fields; set Meta.database = db
Step 3 → db.connect(); db.create_tables([User, Post])
Step 4 → Write: Model.create(...), instance.save(), Model.update(...).execute()
Step 5 → Read:  Model.select().where(...).order_by(...).limit(n)  (lazy, runs when iterated)
Step 6 → Use db.atomic() for transactions; db.close() when done
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Database object बनाओ:       db = SqliteDatabase("app.db") / PostgresqlDatabase(...)
Step 2 → Fields के साथ Models (classes) लिखो; Meta.database = db सेट करो
Step 3 → db.connect(); db.create_tables([User, Post])
Step 4 → Write: Model.create(...), instance.save(), Model.update(...).execute()
Step 5 → Read:  Model.select().where(...).order_by(...).limit(n)  (lazy, iterate करने पर चलता है)
Step 6 → Transactions के लिए db.atomic(); काम खत्म होने पर db.close()
```

---

## 🟡 Real World Example
A small internal tool at a startup (leave tracker, coupon manager) uses Peewee with SQLite: one file, zero server setup. A data-collection script stores scraped products in SQLite through Peewee models. A Telegram bot keeps user preferences in Peewee + PostgreSQL. Teams choose it when SQLAlchemy feels too heavy.

## 🟡 Real Example Hindi mein
Startup का छोटा internal tool (leave tracker, coupon manager) Peewee + SQLite इस्तेमाल करता है: एक file, server setup की जरूरत नहीं। Data-collection script scraped products को Peewee models से SQLite में रखती है। Telegram bot user preferences Peewee + PostgreSQL में रखता है। जब SQLAlchemy भारी लगे, teams Peewee चुनती हैं।

---

## 💻 Code Example — Basic
```python
# Basic Peewee: models, create, query, update, delete (SQLite in memory)
from peewee import SqliteDatabase, Model, CharField, IntegerField, ForeignKeyField, fn   # ORM pieces

db: SqliteDatabase = SqliteDatabase(":memory:")   # in-memory database for the demo


class BaseModel(Model):
    class Meta:
        database = db                             # every model shares this database


class User(BaseModel):
    name = CharField(max_length=50)               # text column
    age = IntegerField(default=0)                 # int column with default


class Post(BaseModel):
    user = ForeignKeyField(User, backref="posts") # FK; user.posts gives reverse access
    title = CharField()                           # post title


db.connect()                                      # open connection
db.create_tables([User, Post])                    # CREATE TABLE IF NOT EXISTS
asha = User.create(name="Asha", age=25)           # INSERT and return instance
ravi = User.create(name="Ravi", age=31)           # another row
Post.create(user=asha, title="Hello")             # post by Asha
Post.create(user=asha, title="Second")            # another post
print(asha.id, User.select().count())             # 1 2
print([u.name for u in User.select().where(User.age > 26)])   # WHERE age > 26
print([p.title for p in asha.posts])              # reverse relation
q = (User.select(User.name, fn.COUNT(Post.id).alias("n"))
     .join(Post, on=(Post.user == User.id)).group_by(User.name))   # JOIN + GROUP BY
print([(u.name, u.n) for u in q])                 # [('Asha', 2)]  (INNER join drops Ravi)
User.update(age=User.age + 1).where(User.name == "Ravi").execute()   # UPDATE in SQL, no Python loop
print(User.get(User.name == "Ravi").age)          # 32
print(User.delete().where(User.name == "Ravi").execute())   # DELETE returns row count
print(User.get_or_none(User.name == "Ravi"))      # None (get() would raise DoesNotExist)
db.close()                                        # close

# Output:
# 1 2
# ['Ravi']
# ['Hello', 'Second']
# [('Asha', 2)]
# 32
# 1
# None
```

## 💻 Code Example — Advanced
```python
# Production style: transactions, unique constraint, bulk insert, pagination, error handling
from typing import Optional                       # type hints
from peewee import (SqliteDatabase, Model, CharField, IntegerField, DecimalField,
                    IntegrityError, DoesNotExist)
from decimal import Decimal                       # money type

db: SqliteDatabase = SqliteDatabase(":memory:", pragmas={"foreign_keys": 1})   # enforce FKs in SQLite


class BaseModel(Model):
    class Meta:
        database = db


class Account(BaseModel):
    email = CharField(unique=True)                # unique constraint at DB level
    balance = DecimalField(decimal_places=2, auto_round=True, default=Decimal("0"))   # exact money


def open_account(email: str, deposit: Decimal) -> Account:
    try:
        return Account.create(email=email, balance=deposit)   # insert
    except IntegrityError as e:                   # duplicate email
        raise ValueError(f"{email} already exists") from e


def transfer(src_id: int, dst_id: int, amount: Decimal) -> None:
    """All-or-nothing money transfer."""
    with db.atomic():                             # BEGIN ... COMMIT, rollback on exception
        src: Account = Account.get_by_id(src_id)  # raises DoesNotExist if missing
        if src.balance < amount:                  # business rule
            raise ValueError("insufficient funds")   # exception triggers rollback
        Account.update(balance=Account.balance - amount).where(Account.id == src_id).execute()   # debit
        credited: int = Account.update(balance=Account.balance + amount).where(Account.id == dst_id).execute()   # credit, returns rows changed
        if credited != 1:                         # destination missing: 0 rows updated, no exception!
            raise ValueError("destination account not found")   # rollback the debit too


def page(n: int, size: int = 2) -> list[str]:
    return [a.email for a in Account.select().order_by(Account.id).paginate(n, size)]   # page n (1-based)


db.connect()
db.create_tables([Account])
a = open_account("a@x.com", Decimal("100.00"))
b = open_account("b@x.com", Decimal("20.00"))
with db.atomic():                                 # bulk insert in one transaction
    Account.insert_many([{"email": f"u{i}@x.com", "balance": 0} for i in range(3)]).execute()
transfer(a.id, b.id, Decimal("30.00"))            # succeeds
print(f"{Account.get_by_id(a.id).balance:.2f} {Account.get_by_id(b.id).balance:.2f}")   # 70.00 50.00
for args in [(a.id, b.id, Decimal("999")), (a.id, 999, Decimal("5"))]:   # two failures
    try:
        transfer(*args)
    except (ValueError, DoesNotExist) as e:
        print("Error:", type(e).__name__, e)
print(f"{Account.get_by_id(a.id).balance:.2f}")   # unchanged by failures
try:
    open_account("a@x.com", Decimal("1"))         # duplicate
except ValueError as e:
    print("Error:", e)
print(page(1), page(2), page(3))                  # pagination
db.close()

# Output (after the destination-missing fix):
# 70.00 50.00
# Error: ValueError insufficient funds
# Error: ValueError destination account not found
# 70.00
# Error: a@x.com already exists
# ['a@x.com', 'b@x.com'] ['u0@x.com', 'u1@x.com'] ['u2@x.com']
```



---

## 🟠 JavaScript vs Python Comparison

| Concept | Python (Peewee) | JavaScript |
|---------|-----------------|-----------|
| Tiny ORM | Peewee | Knex (query builder) / Sequelize |
| Model | `class User(Model)` | `sequelize.define("User", {...})` |
| Query | `User.select().where(User.age > 18)` | `User.findAll({ where: { age: { [Op.gt]: 18 } } })` |
| Transaction | `with db.atomic():` | `sequelize.transaction(async t => ...)` |
| Migrations | `playhouse.migrate` | Sequelize CLI migrations |

```python
# Python way — Peewee query reads like Python
from peewee import SqliteDatabase, Model, CharField   # ORM
db = SqliteDatabase(":memory:")                    # database
class User(Model):
    name = CharField()                             # column
    class Meta:
        database = db                              # bind
db.create_tables([User]); User.create(name="Asha")
print([u.name for u in User.select().where(User.name == "Asha")])   # ['Asha']
```
```javascript
// JavaScript way (Sequelize)
const User = sequelize.define("User", { name: DataTypes.STRING });
await sequelize.sync();
await User.create({ name: "Asha" });
const rows = await User.findAll({ where: { name: "Asha" } });
```

Key difference: Peewee is synchronous (no async/await), and uses overloaded Python operators (`User.age > 18`, `&`, `|`) to build SQL expressions. Sequelize is promise-based and uses object filters.

---

## 🟠 FastAPI Connection
Peewee is synchronous and uses a connection per thread, so in FastAPI use plain `def` endpoints (they run in the thread pool) and open/close the connection in a dependency. Do not use it inside `async def` endpoints: a blocking query would freeze the event loop. For fully async code choose SQLAlchemy async or Tortoise. Peewee models are not Pydantic models, so return dicts or Pydantic schemas explicitly.

```python
# FastAPI + Peewee: sync endpoints, one connection per request via a dependency
from typing import Iterator                       # types
from fastapi import Depends, FastAPI, HTTPException   # web pieces
from fastapi.testclient import TestClient         # demo client
from peewee import SqliteDatabase, Model, CharField, IntegrityError   # ORM

db = SqliteDatabase("file:memdb1?mode=memory&cache=shared", uri=True, check_same_thread=False)   # shared in-memory DB usable from threads


class User(Model):
    email = CharField(unique=True)
    class Meta:
        database = db


def get_db() -> Iterator[None]:
    db.connect(reuse_if_open=True)                # open connection for this request
    try:
        yield                                     # endpoint runs
    finally:
        if not db.is_closed():
            db.close()                            # always close


app = FastAPI()


@app.post("/users", status_code=201, dependencies=[Depends(get_db)])
def create(email: str) -> dict[str, int]:         # plain def -> FastAPI runs it in a thread pool
    try:
        return {"id": User.create(email=email).id}
    except IntegrityError:
        raise HTTPException(409, "email exists")


@app.get("/users/{uid}", dependencies=[Depends(get_db)])
def read(uid: int) -> dict[str, str]:
    u = User.get_or_none(User.id == uid)          # None instead of exception
    if u is None:
        raise HTTPException(404, "not found")
    return {"email": u.email}


keeper = SqliteDatabase("file:memdb1?mode=memory&cache=shared", uri=True)   # keep the shared memory DB alive
keeper.connect()
db.connect(); db.bind([User]); db.create_tables([User]); db.close()   # create schema
client = TestClient(app)
print(client.post("/users", params={"email": "a@x.com"}).json())
print(client.post("/users", params={"email": "a@x.com"}).status_code)
print(client.get("/users/1").json(), client.get("/users/9").status_code)
keeper.close()

# Output:
# {'id': 1}
# 409
# {'email': 'a@x.com'} 404
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using Python `or` / `and` instead of `|` / `&` in `where()`
✅ Correct: use `|` and `&`, each condition in brackets

```python
from peewee import SqliteDatabase, Model, CharField
db = SqliteDatabase(":memory:")
class U(Model):
    n = CharField()
    class Meta:
        database = db
db.create_tables([U]); [U.create(n=str(i)) for i in range(3)]
# Wrong — Python evaluates (U.n == "1") or ... and returns only the FIRST expression
print(U.select().where(U.n == "1" or U.n == "2").count())        # 1
# Right
print(U.select().where((U.n == "1") | (U.n == "2")).count())     # 2
```

❌ Mistake 2: `get()` for something that may not exist
✅ Correct: use `get_or_none()` or `.first()`, or catch `DoesNotExist`

```python
# Wrong — raises User.DoesNotExist when no row matches
# user = User.get(User.name == "Nobody")
# Right
user = U.get_or_none(U.n == "zzz")
print(user)                                                      # None
```

❌ Mistake 3: N+1 queries when looping over related objects
✅ Correct: join once (or use `prefetch`)

```python
from peewee import ForeignKeyField
class P(Model):
    u = ForeignKeyField(U, backref="ps")
    class Meta:
        database = db
db.create_tables([P])
# Wrong — one extra SELECT per post for p.u
for p in P.select():
    _ = p.u.n
# Right — one JOIN query
for p in P.select(P, U).join(U):
    _ = p.u.n
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
from peewee import SqliteDatabase, Model, CharField
db = SqliteDatabase(":memory:")
class U(Model):
    n = CharField()
    class Meta:
        database = db
db.create_tables([U])
for i in range(3):
    U.create(n=str(i))
print(U.select().where(U.n == "1" or U.n == "2").count())
print(U.select().where((U.n == "1") | (U.n == "2")).count())
print(U.select().where(U.n == "9").first())
```
Answer: `1`, `2`, `None`. The Python `or` is evaluated BEFORE Peewee sees anything: `U.n == '1'` is a truthy expression object, so `or` returns it and the second condition is dropped. Peewee overloads `|` and `&` (which is why brackets are needed because of operator precedence). `.first()` returns `None` when there is no row; `.get()` would raise `DoesNotExist`. Verified with Peewee 4.5.

---

## ⚫ Interview Questions + Answers

Q1: Peewee vs SQLAlchemy?
A1: Peewee is small, one-file, simple API, sync only. SQLAlchemy is larger, has Core + ORM, async support, better migrations (Alembic) and more database features. Choose Peewee for small tools and scripts, SQLAlchemy for big or async apps.

Q2: What does `db.atomic()` do?
A2: It opens a transaction (or a savepoint when nested). It commits on success and rolls back if an exception escapes. Use it for any multi-statement change such as a money transfer.

Q3: How do you avoid the N+1 problem?
A3: Use `join()` with the related model in `select(...)`, or `prefetch(users_query, posts_query)` for one-to-many. Check the generated SQL with logging.

Q4: Does Peewee do migrations?
A4: Only simple ones with `playhouse.migrate` (add column, rename, drop). For serious schema management use a dedicated tool such as `peewee-migrate` or Alembic with another ORM.

Q5: Is Peewee thread-safe?
A5: Yes, connection state is thread-local by default, so each thread has its own connection. Open a connection per request/thread and close it afterwards, or use a connection pool (`playhouse.pool`).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Small apps, scripts, internal tools, bots
- SQLite-based projects wanting a clean model layer
- You want a tiny learning curve

❌ Avoid when:
- You need async database access (FastAPI async endpoints) - use SQLAlchemy async
- Complex enterprise schemas with many migrations
- Team already standardised on SQLAlchemy or Django ORM

---

## 📊 Visual Diagram
```
Python class                      SQL generated
-------------                    ---------------
class User(Model):               CREATE TABLE user (
    name = CharField()   ---->     id INTEGER PRIMARY KEY,
    age  = IntegerField()          name VARCHAR(255) NOT NULL,
                                   age INTEGER NOT NULL);
User.select().where(User.age > 18).order_by(User.name)
     ----> SELECT ... FROM user WHERE age > 18 ORDER BY name
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ORM | Classes mapped to tables | Classes को tables से जोड़ना |
| Model | Python class for a table | Table की Python class |
| Field | Column definition | Column की definition |
| `atomic()` | Transaction block | Transaction का block |
| Backref | Reverse relation name | उल्टे relation का नाम |
| N+1 | One query per row problem | हर row पर अलग query की समस्या |

---

## ⚡ 3-Line Summary
English: Peewee is a lightweight synchronous ORM: models are classes, queries are Python expressions, and `db.atomic()` gives transactions. Use `|`/`&` not `or`/`and`, `get_or_none` for optional rows, joins to avoid N+1, and plain `def` endpoints in FastAPI.
Hindi: Peewee हल्का synchronous ORM है: models classes हैं, queries Python expressions हैं, और `db.atomic()` से transactions मिलती हैं। `or`/`and` की जगह `|`/`&` लगाएं, optional rows के लिए `get_or_none`, N+1 से बचने के लिए joins, और FastAPI में plain `def` endpoints इस्तेमाल करें।

---

## ➡️ Next Topic
**364. PyMongo — MongoDB** — the official synchronous driver for the MongoDB document database.
