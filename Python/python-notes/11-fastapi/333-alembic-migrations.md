---

# 333. Alembic Migrations
# हिंदी में: Alembic Migrations (Database Schema का Version Control)

---

## 🔵 Simple Definition (English)
Alembic is the migration tool for SQLAlchemy. It keeps a numbered chain of small Python scripts, each with `upgrade()` and `downgrade()`, that change your database schema step by step. It also remembers the current version in a table called `alembic_version`.

## 🔵 सरल परिभाषा (Hindi)
Alembic SQLAlchemy का migration tool है। यह छोटी-छोटी Python scripts की numbered chain रखता है, हर एक में `upgrade()` और `downgrade()` होता है, जो database schema को कदम-दर-कदम बदलती हैं। यह मौजूदा version को `alembic_version` नाम की table में याद रखता है।

---

## 🔴 Problem it Solves
`Base.metadata.create_all()` creates only missing tables. If you add a column to a model, it does nothing for existing tables. Editing production tables by hand means no history, no rollback, and different schemas on dev, staging and prod. Alembic gives you version-controlled schema changes that every environment applies in the same order.

## 🔴 यह क्यों बना? (Hindi)
`Base.metadata.create_all()` सिर्फ गायब tables बनाता है। Model में column जोड़ने पर मौजूदा tables के लिए यह कुछ नहीं करता। Production tables हाथ से बदलने का मतलब: कोई history नहीं, rollback नहीं, और dev, staging, prod पर अलग-अलग schema। Alembic version-controlled schema changes देता है जिन्हें हर environment एक ही क्रम में लागू करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → alembic init migrations        (creates alembic.ini + migrations/env.py)
Step 2 → Set sqlalchemy.url and target_metadata = Base.metadata in env.py
Step 3 → alembic revision --autogenerate -m "msg"   (compares models vs DB)
Step 4 → Review the generated file in migrations/versions/ (ALWAYS read it)
Step 5 → alembic upgrade head           (runs upgrade() of each pending revision)
Step 6 → Alembic stores the revision id in table alembic_version
Step 7 → alembic downgrade -1           (runs downgrade() of the last revision)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → alembic init migrations        (alembic.ini + migrations/env.py बनता है)
Step 2 → env.py में sqlalchemy.url और target_metadata = Base.metadata सेट करें
Step 3 → alembic revision --autogenerate -m "msg"   (models की DB से तुलना)
Step 4 → migrations/versions/ की generated file पढ़ें (हमेशा review करें)
Step 5 → alembic upgrade head           (हर pending revision का upgrade() चलता है)
Step 6 → Alembic revision id को alembic_version table में रखता है
Step 7 → alembic downgrade -1           (आखिरी revision का downgrade() चलता है)
```

---

## 🟡 Real World Example
A Swiggy-style orders service adds a `status` column to `orders` with default `pending`, backfills old rows to `paid` where the amount is above a threshold, and adds an index. The migration runs in the CI/CD pipeline (`alembic upgrade head`) before the new container starts, so the code and the schema always match.

## 🟡 Real Example Hindi mein
Swiggy जैसी orders service `orders` में `status` column जोड़ती है (default `pending`), पुरानी rows को amount के आधार पर `paid` में backfill करती है, और index जोड़ती है। Migration CI/CD pipeline में (`alembic upgrade head`) नया container शुरू होने से पहले चलता है, ताकि code और schema हमेशा मेल खाएं।

---

## 💻 Code Example — Basic
```python
# Basic: the full Alembic workflow driven from Python (verified with SQLite)
import os                                           # change directory
import pathlib                                      # paths
import subprocess                                   # run the alembic CLI
import sys                                          # find the venv's alembic
import tempfile                                     # throwaway project folder
import textwrap                                     # clean multi-line strings

work = pathlib.Path(tempfile.mkdtemp())             # new empty folder
os.chdir(work)                                      # work inside it
alembic = [sys.prefix + "/bin/alembic"]             # the alembic executable


def run(*args: str) -> None:                        # helper: run a command, show tail of output
    r = subprocess.run(alembic + list(args), capture_output=True, text=True)   # execute
    print((r.stdout + r.stderr).strip()[-300:])     # alembic logs to stderr


run("init", "migrations")                           # 1) create the migrations folder
(work / "app_models.py").write_text(textwrap.dedent('''
    from sqlalchemy import String
    from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
    class Base(DeclarativeBase): pass
    class User(Base):
        __tablename__ = "users"
        id: Mapped[int] = mapped_column(primary_key=True)
        email: Mapped[str] = mapped_column(String(120))
'''))                                               # 2) our model file
ini = (work / "alembic.ini").read_text().replace("driver://user:pass@localhost/dbname", "sqlite:///app.db")
(work / "alembic.ini").write_text(ini)              # 3) point Alembic at SQLite
env = (work / "migrations/env.py").read_text().replace(
    "target_metadata = None",
    "import sys; sys.path.insert(0, '.')\nfrom app_models import Base\ntarget_metadata = Base.metadata")
(work / "migrations/env.py").write_text(env)        # 4) tell Alembic about our models
run("revision", "--autogenerate", "-m", "create users")   # 5) detect: table users is new
run("upgrade", "head")                              # 6) apply it
run("current")                                      # 7) which version is the DB at?
# add a nullable column to the model, then migrate again
(work / "app_models.py").write_text((work / "app_models.py").read_text()
    + "    name: Mapped[str | None] = mapped_column(String(80), nullable=True)\n")
run("revision", "--autogenerate", "-m", "add name") # 8) detect: column users.name is new
run("upgrade", "head")                              # 9) apply
run("history")                                      # 10) show the chain
run("downgrade", "-1")                              # 11) roll back one step
run("current")                                      # 12) back to the first revision

# Output (verified, Alembic 1.20; revision ids are random per run; INFO noise trimmed):
# INFO ... Detected added table 'users'
# INFO ... Running upgrade  -> 99d82bf207ae, create users
# 99d82bf207ae (head)
# INFO ... Detected added column 'users.name'
# INFO ... Running upgrade 99d82bf207ae -> f4ed7774673b, add name
# 99d82bf207ae -> f4ed7774673b (head), add name
# <base> -> 99d82bf207ae, create users
# INFO ... Running downgrade f4ed7774673b -> 99d82bf207ae, add name
# 99d82bf207ae
```

The generated `*_add_name.py` looked like this (verified):
```python
def upgrade() -> None:                              # applied by "alembic upgrade"
    op.add_column('users', sa.Column('name', sa.String(length=80), nullable=True))   # ALTER TABLE ADD COLUMN


def downgrade() -> None:                            # applied by "alembic downgrade"
    op.drop_column('users', 'name')                 # undo it
```

## 💻 Code Example — Advanced
```python
# Production style: hand-written migration steps: add column + data backfill + batch alter + index
import sqlalchemy as sa                             # types and text()
from alembic import op                              # operations API used inside migrations
from alembic.migration import MigrationContext      # lets us run ops outside the CLI (for demo)
from alembic.operations import Operations           # operation context manager

engine = sa.create_engine("sqlite://")              # demo database
with engine.begin() as conn:                        # one transaction for the whole migration
    ctx = MigrationContext.configure(conn)          # alembic context bound to this connection
    with Operations.context(ctx):                   # makes the global `op` object work
        op.create_table(                            # create "orders"
            "orders",                               # table name
            sa.Column("id", sa.Integer, primary_key=True),          # PK
            sa.Column("amount", sa.Integer, nullable=False),        # NOT NULL column
        )
        conn.execute(sa.text("INSERT INTO orders (amount) VALUES (100), (250)"))   # old rows
        op.add_column(                              # new NOT NULL column needs a server_default!
            "orders",
            sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        )
        conn.execute(sa.text("UPDATE orders SET status='paid' WHERE amount > 200"))   # data backfill
        with op.batch_alter_table("orders") as batch:   # SQLite cannot ALTER in place: batch rebuilds table
            batch.alter_column("amount", existing_type=sa.Integer, type_=sa.BigInteger)   # change type
            batch.create_index("ix_orders_status", ["status"])      # add an index
        print(conn.execute(sa.text("SELECT id, amount, status FROM orders")).all())   # check data
        print([i["name"] for i in sa.inspect(conn).get_indexes("orders")])            # check index

# Output (verified):
# [(1, 100, 'pending'), (2, 250, 'paid')]
# ['ix_orders_status']
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python (Alembic) | JavaScript |
|---------|------------------|-----------|
| Tool | Alembic | Prisma Migrate, Knex, TypeORM, Sequelize CLI |
| Migration file | Python with `upgrade()` / `downgrade()` | JS/TS with `up()` / `down()` |
| Auto-generate | `--autogenerate` from models | `prisma migrate dev` from schema |
| Apply all | `alembic upgrade head` | `npx prisma migrate deploy` |
| Version table | `alembic_version` | `_prisma_migrations` / `knex_migrations` |

```python
# Python way
def upgrade() -> None:                               # apply
    op.add_column("users", sa.Column("age", sa.Integer()))   # add column
def downgrade() -> None:                             # undo
    op.drop_column("users", "age")                   # remove column
```
```javascript
// JavaScript way (Knex)
exports.up = (knex) =>                               // apply
  knex.schema.alterTable("users", (t) => t.integer("age"));   // add column
exports.down = (knex) =>                             // undo
  knex.schema.alterTable("users", (t) => t.dropColumn("age")); // remove column
```

Key difference: Prisma generates SQL from its own schema file; Alembic generates Python from your SQLAlchemy models and lets you edit it freely.

---

## 🟠 FastAPI Connection
FastAPI itself has no migration tool; Alembic is the standard partner. Import your `Base` in `env.py`, read the database URL from an environment variable (never commit passwords), and run `alembic upgrade head` in your Dockerfile entrypoint or CI job before starting uvicorn.

```python
# FastAPI example — migrations/env.py (the important lines)
import os                                                    # read env vars
from alembic import context                                  # alembic runtime
from app.db import Base                                      # your declarative Base
from app import models                                       # noqa: F401  (import so tables register on Base!)

config = context.config                                      # access alembic.ini values
config.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])   # URL from the environment
target_metadata = Base.metadata                              # what autogenerate compares against
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Trusting autogenerate blindly
✅ Correct: always read the generated file; autogenerate misses renames (shows drop + add), some type changes and server defaults

```python
# Wrong — rename column looks like data loss
op.drop_column("users", "fullname")
op.add_column("users", sa.Column("name", sa.String()))
# Right — edit the file by hand
op.alter_column("users", "fullname", new_column_name="name")
```

❌ Mistake 2: Forgetting to import models before `target_metadata`
✅ Correct: import every models module in `env.py`, otherwise Alembic sees an empty schema and generates "drop table" for everything

```python
# Wrong — models module never imported, Base.metadata is empty
target_metadata = Base.metadata
# Right
from app import models   # noqa: F401  (registers tables on Base.metadata)
target_metadata = Base.metadata
```

❌ Mistake 3: Adding a NOT NULL column without a default on a table that already has rows
✅ Correct: add as nullable or with `server_default`, backfill, then tighten

```python
# Wrong — fails on a non-empty table
op.add_column("orders", sa.Column("status", sa.String(), nullable=False))
# Right
op.add_column("orders", sa.Column("status", sa.String(), nullable=False, server_default="pending"))
```

---

## 🧠 Tricky Interview Question

```python
# Two developers create migrations on separate branches, both with down_revision = "abc1".
# After merging, what happens on "alembic upgrade head"?
```
Answer: There are now two heads (a branched history). Alembic refuses with `Multiple head revisions are present for given argument 'head'`. Fix it with `alembic merge heads -m "merge"`, which creates an empty merge revision having both as parents, or by rebasing one migration's `down_revision`. `alembic heads` lists them. This is why migrations should be reviewed in the pull request and CI should run `alembic heads` to check there is exactly one.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `alembic upgrade head` and `alembic upgrade +1`?
A1: `head` applies all pending revisions up to the latest. `+1` applies exactly one revision forward. `downgrade -1` goes one back, `downgrade base` goes back to empty.

Q2: What is `alembic stamp`?
A2: It writes a revision id into `alembic_version` without running any migration. Use it to adopt Alembic on a database that already has the schema (`alembic stamp head`).

Q3: Why do we need `render_as_batch=True` for SQLite?
A3: SQLite supports only a few `ALTER TABLE` operations. Batch mode creates a new table, copies data, drops the old one and renames it. PostgreSQL and MySQL do not need it.

Q4: How do you make migrations safe on a big production table?
A4: Add nullable columns first, backfill in small batches, then add constraints; create indexes with `CONCURRENTLY` on PostgreSQL (`postgresql_concurrently=True`, outside a transaction); and keep deploys backward-compatible (expand, then contract).

Q5: Can Alembic generate SQL without touching the DB?
A5: Yes: `alembic upgrade head --sql` prints SQL ("offline mode"), useful when a DBA must review and run scripts.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You use SQLAlchemy with a persistent database in any shared environment
- You need history, review and rollback of schema changes
- Several developers or environments must stay in sync

❌ Avoid when:
- A throwaway SQLite file for a prototype (`create_all` is enough)
- You use MongoDB or other schema-less stores (no schema migrations; use data scripts)
- You use Django ORM (it has its own built-in migrations)

---

## 📊 Visual Diagram
```
 models.py ──(autogenerate: diff)──► versions/99d8_create_users.py
                                      versions/f4ed_add_name.py
                                              │
 alembic_version table:  [ f4ed7774673b ]  ◄──┘  upgrade head
                              │
        downgrade -1  ───────►  [ 99d82bf207ae ]

 base ──► 99d8 ──► f4ed ──► (head)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Migration | One versioned schema change | Schema में एक versioned बदलाव |
| Revision | Id of a migration file | Migration file की id |
| `head` | Newest revision | सबसे नया revision |
| `autogenerate` | Create migration from model diff | Models के फर्क से migration बनाना |
| `downgrade` | Undo a migration | Migration को वापस लेना |
| Stamp | Mark DB at a revision without running | बिना चलाए DB पर version चिह्न लगाना |

---

## ⚡ 3-Line Summary
English: Alembic keeps a versioned chain of schema changes with `upgrade()` and `downgrade()`. Use `--autogenerate`, but always review the file, and run `alembic upgrade head` in CI/CD before the app starts. Branching histories need `alembic merge heads`.
Hindi: Alembic schema बदलावों की versioned chain रखता है जिसमें `upgrade()` और `downgrade()` होते हैं। `--autogenerate` उपयोग करें, पर file हमेशा review करें, और app शुरू होने से पहले CI/CD में `alembic upgrade head` चलाएं। Branched history में `alembic merge heads` चाहिए।

---

## ➡️ Next Topic
**334. SQLAlchemy — Complete Guide** — models, relationships, queries, loading strategies and transactions in depth.
