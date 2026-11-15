---

# 360. SQLAlchemy Migrations
# हिंदी में: SQLAlchemy Migrations (Schema को सुरक्षित तरीके से बदलना)

---

## 🔵 Simple Definition (English)
A migration is a small versioned script that changes your database schema (add a column, create a table, add an index) and can undo it. For SQLAlchemy the standard tool is Alembic. It compares your models with the database, writes the migration for you, and applies scripts in order.

## 🔵 सरल परिभाषा (Hindi)
Migration एक छोटी versioned script है जो आपके database का schema बदलती है (column जोड़ना, table बनाना, index लगाना) और उसे वापस भी कर सकती है। SQLAlchemy का standard tool Alembic है। यह आपके models की database से तुलना करता है, migration खुद लिखता है और scripts को क्रम से चलाता है।

---

## 🔴 Problem it Solves
`Base.metadata.create_all()` only creates missing tables. It never adds a column to an existing table, never renames or drops anything, and never touches data. In production you cannot drop the database to apply a change. Without migrations, dev, staging and production schemas drift apart and deployments break. Migrations give version history, repeatable deployments, and rollbacks.

## 🔴 यह क्यों बना? (Hindi)
`Base.metadata.create_all()` सिर्फ गायब tables बनाता है। यह मौजूदा table में column नहीं जोड़ता, कुछ rename या drop नहीं करता और data को नहीं छूता। Production में बदलाव के लिए database drop नहीं कर सकते। Migrations के बिना dev, staging और production के schema अलग होते जाते हैं और deployments टूटते हैं। Migrations version history, दोहराने लायक deployments और rollback देते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → alembic init migrations          creates alembic.ini + migrations/env.py + versions/
Step 2 → In env.py set target_metadata = Base.metadata (your models)
Step 3 → alembic revision --autogenerate -m "add phone"
         Alembic compares models vs the live DB and writes versions/<id>_add_phone.py
Step 4 → REVIEW the file (autogenerate misses renames, some types, constraints)
Step 5 → alembic upgrade head             runs upgrade() of every pending revision
Step 6 → DB table alembic_version stores the current revision id
Step 7 → alembic downgrade -1             runs downgrade() of the last revision
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → alembic init migrations          alembic.ini + migrations/env.py + versions/ बनाता है
Step 2 → env.py में target_metadata = Base.metadata (आपके models) सेट करें
Step 3 → alembic revision --autogenerate -m "add phone"
         Alembic models और live DB की तुलना करके versions/<id>_add_phone.py लिखता है
Step 4 → फ़ाइल REVIEW करें (autogenerate renames, कुछ types, constraints चूक जाता है)
Step 5 → alembic upgrade head             हर pending revision का upgrade() चलाता है
Step 6 → DB की alembic_version table मौजूदा revision id रखती है
Step 7 → alembic downgrade -1             आखिरी revision का downgrade() चलाता है
```

---

## 🟡 Real World Example
A food-delivery app adds `phone` to `users`. A teammate makes the model change, runs autogenerate, reviews the script, and commits it. The CI pipeline runs `alembic upgrade head` against a copy of production data; on deploy the container's entrypoint runs `alembic upgrade head` before starting uvicorn. If the release is bad, `alembic downgrade -1` restores the old schema.

## 🟡 Real Example Hindi mein
Food-delivery app `users` में `phone` जोड़ता है। साथी model बदलता है, autogenerate चलाता है, script review करके commit करता है। CI pipeline production data की copy पर `alembic upgrade head` चलाती है; deploy पर container का entrypoint uvicorn शुरू करने से पहले `alembic upgrade head` चलाता है। Release खराब हो तो `alembic downgrade -1` पुराना schema लौटा देता है।

---

## 💻 Code Example — Basic
```python
# Basic: let Alembic compare models with a database and apply an operation (no CLI needed)
from alembic.autogenerate import compare_metadata        # diff engine used by --autogenerate
from alembic.migration import MigrationContext           # wraps a DB connection
from alembic.operations import Operations                # op.add_column, op.create_table, ...
import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):                                        # NEW model: has an `email` column
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str | None]                            # added after the table already existed


engine = sa.create_engine("sqlite://")                   # in-memory SQLite
with engine.begin() as conn:
    conn.exec_driver_sql("CREATE TABLE users (id INTEGER NOT NULL PRIMARY KEY, name VARCHAR NOT NULL)")   # OLD schema

    ctx = MigrationContext.configure(conn)               # context for diffing and operations
    diff = compare_metadata(ctx, Base.metadata)          # what is different?
    print([d[0] for d in diff])                          # ['add_column']
    print(diff[0][3].name)                               # email

    ops = Operations(ctx)                                # what a migration's `op` object is
    ops.add_column("users", sa.Column("email", sa.String(), nullable=True))   # the upgrade step
    print(compare_metadata(ctx, Base.metadata))          # [] -> models and DB match now
    print([c["name"] for c in sa.inspect(conn).get_columns("users")])         # ['id', 'name', 'email']

# Output:
# ['add_column']
# email
# []
# ['id', 'name', 'email']
```

## 💻 Code Example — Advanced
```python
# Production style: a safe migration with a data backfill, a NOT NULL step, and a downgrade
# (written as plain functions using Alembic Operations, like a real versions/xxxx.py file)
import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations


def upgrade(op: Operations) -> None:
    """Add users.phone safely: nullable first, backfill, then NOT NULL (3 steps)."""
    op.add_column("users", sa.Column("phone", sa.String(15), nullable=True))   # 1. nullable: no table rewrite problems
    op.execute("UPDATE users SET phone = 'unknown' WHERE phone IS NULL")       # 2. backfill existing rows
    with op.batch_alter_table("users") as batch:                               # 3. SQLite cannot ALTER COLUMN directly,
        batch.alter_column("phone", existing_type=sa.String(15), nullable=False)  #    batch mode rebuilds the table
    op.create_index("ix_users_phone", "users", ["phone"])                      # index for lookups


def downgrade(op: Operations) -> None:
    """Exact reverse of upgrade, in reverse order."""
    op.drop_index("ix_users_phone", table_name="users")                        # remove index first
    with op.batch_alter_table("users") as batch:
        batch.drop_column("phone")                                             # then the column


def columns(conn: sa.Connection) -> list[str]:
    return [c["name"] for c in sa.inspect(conn).get_columns("users")]


engine = sa.create_engine("sqlite://")
with engine.begin() as conn:
    conn.exec_driver_sql("CREATE TABLE users (id INTEGER PRIMARY KEY, name VARCHAR NOT NULL)")
    conn.exec_driver_sql("INSERT INTO users (name) VALUES ('Asha'), ('Ravi')")
    op = Operations(MigrationContext.configure(conn))   # normally Alembic gives you `op`

    upgrade(op)                                         # alembic upgrade head
    print(columns(conn))                                # ['id', 'name', 'phone']
    print(conn.exec_driver_sql("SELECT name, phone FROM users").all())   # backfilled
    try:
        conn.exec_driver_sql("INSERT INTO users (name) VALUES ('NoPhone')")   # violates NOT NULL
    except sa.exc.IntegrityError as e:
        print("Error:", "NOT NULL" in str(e.orig))      # True

    downgrade(op)                                       # alembic downgrade -1
    print(columns(conn))                                # ['id', 'name']

# Output:
# ['id', 'name', 'phone']
# [('Asha', 'unknown'), ('Ravi', 'unknown')]
# Error: True
# ['id', 'name']
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Alembic | Prisma Migrate / Knex (JS) |
|---------|---------|-----------------------------|
| Generate | `alembic revision --autogenerate` | `prisma migrate dev` |
| Apply | `alembic upgrade head` | `prisma migrate deploy` |
| Undo | `alembic downgrade -1` | Prisma: no automatic down; Knex: `migrate:rollback` |
| Format | Python scripts | SQL files (Prisma) / JS files (Knex) |

```python
# Python way: a migration file written (or generated) by Alembic
def upgrade() -> None:
    op.add_column("users", sa.Column("phone", sa.String(15), nullable=True))   # forward
def downgrade() -> None:
    op.drop_column("users", "phone")                                            # backward
```
```javascript
// JavaScript way (Knex)
exports.up = (knex) => knex.schema.alterTable("users", t => t.string("phone", 15));   // forward
exports.down = (knex) => knex.schema.alterTable("users", t => t.dropColumn("phone")); // backward
```

Key difference: Alembic autogenerates by diffing your models against a live database, like Prisma. Unlike Prisma (SQL files), Alembic migrations are Python code, so you can write data migrations with loops and logic.

---

## 🟠 FastAPI Connection
Never call `create_all()` in a production FastAPI startup. Run migrations as a deploy step (container entrypoint or CI job) so only one process migrates, not every worker. For a quick check, an endpoint can report the current revision.

```python
# FastAPI: expose the DB schema revision (health/ops endpoint) using Alembic's MigrationContext
import sqlalchemy as sa
from alembic.migration import MigrationContext
from fastapi import FastAPI
from fastapi.testclient import TestClient

engine = sa.create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=sa.pool.StaticPool)
with engine.begin() as c:                                       # simulate "alembic upgrade head" result
    c.exec_driver_sql("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL PRIMARY KEY)")
    c.exec_driver_sql("INSERT INTO alembic_version VALUES ('a1b2c3d4e5f6')")

app = FastAPI()


@app.get("/health/schema")
def schema_version() -> dict[str, str | None]:
    with engine.connect() as conn:
        rev = MigrationContext.configure(conn).get_current_revision()   # reads alembic_version
    return {"revision": rev}


print(TestClient(app).get("/health/schema").json())                   # {'revision': 'a1b2c3d4e5f6'}

# Deploy entrypoint (shell, not run here):
#   alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Trusting autogenerate blindly
✅ Correct: always read the generated file. A renamed column appears as drop + add and loses data.

```python
# Wrong (autogenerated for a rename name -> full_name): data is lost
op.drop_column("users", "name")
op.add_column("users", sa.Column("full_name", sa.String()))
# Right
op.alter_column("users", "name", new_column_name="full_name")
```

❌ Mistake 2: Adding a NOT NULL column without a default to a table that has rows
✅ Correct: add nullable, backfill, then set NOT NULL (or use `server_default`)

```python
# Wrong: fails on a non-empty table
op.add_column("users", sa.Column("phone", sa.String(), nullable=False))
# Right
op.add_column("users", sa.Column("phone", sa.String(), nullable=False, server_default="unknown"))
```

❌ Mistake 3: Editing an already applied migration or using `create_all()` in production
✅ Correct: never edit applied revisions; add a new one

```python
# Wrong
Base.metadata.create_all(engine)       # in app startup: skips existing tables, no history
# Right: run `alembic upgrade head` as a separate deploy step
```

---

## 🧠 Tricky Interview Question

```python
# What will this output? (SQLite, no existing alembic setup)
import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase): pass
class T(Base):
    __tablename__ = "t"
    id: Mapped[int] = mapped_column(primary_key=True)

e = sa.create_engine("sqlite://")
with e.begin() as c:
    c.exec_driver_sql("CREATE TABLE t (id INTEGER PRIMARY KEY)")
class T2(Base):
    __tablename__ = "t2"
    id: Mapped[int] = mapped_column(primary_key=True)
Base.metadata.create_all(e)
print(sorted(sa.inspect(e).get_table_names()))
```
Answer: `['t', 't2']`. `create_all` checks each table by name, creates only the missing ones and silently skips existing ones. If you had added a column to `T`, `create_all` would not add it. That is the reason migrations exist.

---

## ⚫ Interview Questions + Answers

Q1: Why use Alembic instead of `create_all()`?
A1: `create_all` cannot alter or drop anything and keeps no history. Alembic provides versioned, ordered, reversible schema changes that behave the same in every environment.

Q2: What does autogenerate not detect?
A2: Table or column renames (seen as drop + add), changes of server defaults and some type changes (unless `compare_type=True`), anonymous constraints, and data changes. Always review.

Q3: How do you handle a data migration?
A3: Write it inside `upgrade()` using `op.execute()` or lightweight `sa.table()` constructs, not your app's ORM models (the models change over time and break old migrations). Do large backfills in batches.

Q4: How do you do zero-downtime schema changes?
A4: Use the expand/contract pattern: first add the new nullable column (old code still works), deploy code that writes both, backfill, deploy code that reads the new column, and only then drop the old one in a later release.

Q5: What are branches/heads and `alembic_version`?
A5: Each revision has a `down_revision` forming a chain. `alembic_version` stores the current head id. Two developers creating revisions from the same parent produce two heads; fix with `alembic merge heads`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any app with a real database that changes over time
- Teams where several people change the schema
- CI/CD with repeatable deployments

❌ Avoid when:
- Throwaway scripts and tests (use `create_all()` on SQLite)
- A schema you manage entirely through another tool (Django migrations, Flyway)
- Live "magic" changes at app startup in multi-worker deployments

---

## 📊 Visual Diagram
```
models (Base.metadata)              database
       |                                |
       |  alembic revision --autogenerate (compare)
       v                                v
  versions/001_init.py  <-  down_revision  <-  versions/002_add_phone.py
        (base)                                      (head)

 upgrade head:    001 --upgrade()--> 002 --upgrade()--> DB at head
 downgrade -1:    002 --downgrade()-> 001
 table alembic_version = [ '002' ]   <- where the DB is now
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Migration | Versioned schema change script | Schema बदलने वाली versioned script |
| Revision | One migration with an id | एक id वाली migration |
| head | Latest revision | सबसे नई revision |
| Autogenerate | Create migration by diffing models and DB | Models और DB की तुलना से migration बनाना |
| Downgrade | Undo a migration | Migration वापस लेना |
| Expand/contract | Safe multi-step schema change | कई चरणों में सुरक्षित schema बदलाव |

---

## ⚡ 3-Line Summary
English: Migrations track schema changes as ordered, reversible scripts, and Alembic is the SQLAlchemy tool for it. Autogenerate diffs models against the DB, but always review the output. Run `alembic upgrade head` as a deploy step, not at app startup.
Hindi: Migrations schema बदलावों को क्रमबद्ध, वापस होने लायक scripts के रूप में रखती हैं, और Alembic इसके लिए SQLAlchemy का tool है। Autogenerate models की DB से तुलना करता है, पर output हमेशा review करें। `alembic upgrade head` को deploy step की तरह चलाएं, app startup में नहीं।

---

## ➡️ Next Topic
**362. Django ORM Basics** — a different ORM: models, QuerySets and migrations built into Django.
