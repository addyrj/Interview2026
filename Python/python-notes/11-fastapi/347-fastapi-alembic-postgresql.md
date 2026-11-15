---

# 347. FastAPI + Alembic + PostgreSQL
# हिंदी में: FastAPI + Alembic + PostgreSQL (database migrations के साथ)

---

## 🔵 Simple Definition (English)
This is the standard production stack: FastAPI serves the API, SQLAlchemy talks to PostgreSQL, and Alembic changes the database schema step by step using versioned migration files. You change a model in Python, Alembic generates a migration, and you apply it to every environment (dev, staging, prod) in the same order.

## 🔵 सरल परिभाषा (Hindi)
यह production का standard stack है: FastAPI API चलाता है, SQLAlchemy PostgreSQL से बात करता है और Alembic versioned migration files से database schema को कदम-दर-कदम बदलता है। आप Python में model बदलते हैं, Alembic migration बनाता है, और आप उसे हर environment (dev, staging, prod) में उसी क्रम से लगाते हैं।

---

## 🔴 Problem it Solves
`Base.metadata.create_all()` only creates missing tables; it never adds a column, renames one or changes a type. Editing the production database by hand is risky and nobody knows which server has which schema. Alembic keeps a history (like git for your schema) and records the current version inside the database itself.

## 🔴 यह क्यों बना? (Hindi)
`Base.metadata.create_all()` सिर्फ़ गायब tables बनाता है; यह column जोड़ना, नाम बदलना या type बदलना नहीं करता। Production database को हाथ से बदलना जोखिम भरा है और किसी को पता नहीं रहता कि किस server पर कौन सा schema है। Alembic एक history रखता है (schema के लिए git जैसा) और मौजूदा version database के अंदर ही दर्ज करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → pip install alembic sqlalchemy "psycopg[binary]"; run `alembic init migrations`
Step 2 → In migrations/env.py: import Base.metadata, set sqlalchemy.url from env var
Step 3 → Edit a model (add class or column)
Step 4 → alembic revision --autogenerate -m "add stock"  -> new file in migrations/versions
Step 5 → REVIEW the generated file (autogenerate is a draft, not magic)
Step 6 → alembic upgrade head  -> runs upgrade(), stores revision id in alembic_version table
Step 7 → alembic downgrade -1  -> runs downgrade() of the last revision
Step 8 → In deployment, run `alembic upgrade head` BEFORE starting the new app version
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → pip install alembic sqlalchemy "psycopg[binary]"; `alembic init migrations` चलाएँ
Step 2 → migrations/env.py में Base.metadata import करें, sqlalchemy.url env var से सेट करें
Step 3 → Model बदलें (नई class या column)
Step 4 → alembic revision --autogenerate -m "add stock"  -> migrations/versions में नई file
Step 5 → बनी हुई file ज़रूर देखें (autogenerate सिर्फ़ draft है, जादू नहीं)
Step 6 → alembic upgrade head  -> upgrade() चलता है, revision id alembic_version table में जाती है
Step 7 → alembic downgrade -1  -> आखिरी revision का downgrade() चलता है
Step 8 → Deployment में नए app से पहले `alembic upgrade head` चलाएँ
```

---

## 🟡 Real World Example
A Swiggy-like team adds `stock` to the `products` table. A developer edits the model, generates a migration, and commits both. In CI the pipeline starts a Postgres container, runs `alembic upgrade head`, runs tests, and in production a one-off job (or init container) runs `alembic upgrade head` before the new pods start. If something breaks, `alembic downgrade -1` rolls back the schema.

## 🟡 Real Example Hindi mein
Swiggy जैसी team `products` table में `stock` जोड़ती है। Developer model बदलता है, migration बनाता है और दोनों commit करता है। CI pipeline में Postgres container चलता है, `alembic upgrade head` चलता है, फिर tests चलते हैं। Production में नए pods से पहले एक one-off job (या init container) `alembic upgrade head` चलाता है। कुछ बिगड़े तो `alembic downgrade -1` से schema वापस हो जाता है।

---

## 💻 Code Example — Basic
```python
# Basic: model + engine + FastAPI route (sync SQLAlchemy 2.x + psycopg 3)
# pip install fastapi httpx sqlalchemy "psycopg[binary]"
# Verified against a real PostgreSQL 16 server (started locally for this note).
from decimal import Decimal  # exact money type
from typing import Annotated, Iterator, List  # type hints

from fastapi import Depends, FastAPI  # framework
from sqlalchemy import Numeric, String, create_engine, select  # SQL pieces
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker  # ORM

# Driver name "postgresql+psycopg" = SQLAlchemy + psycopg 3. For psycopg2 use "postgresql+psycopg2".
URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/shop"  # from env in real life
engine = create_engine(URL, pool_pre_ping=True, pool_size=5, max_overflow=10)  # connection pool
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)  # session factory


class Base(DeclarativeBase):  # parent of all models
    pass


class Product(Base):  # table "products"
    __tablename__ = "products"  # table name
    id: Mapped[int] = mapped_column(primary_key=True)  # primary key
    name: Mapped[str] = mapped_column(String(100), index=True)  # indexed name
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))  # money: 2 decimals


def get_db() -> Iterator[Session]:  # one session per request
    with SessionLocal() as session:  # opens and always closes
        yield session  # give to the route


app: FastAPI = FastAPI()  # app
DbDep = Annotated[Session, Depends(get_db)]  # reusable dependency alias


@app.get("/products")  # list products
def list_products(db: DbDep) -> List[dict]:
    rows = db.scalars(select(Product).order_by(Product.id))  # SELECT ... ORDER BY id
    return [{"id": p.id, "name": p.name, "price": str(p.price)} for p in rows]  # to JSON
# Tables are NOT created here. Alembic creates them (see the advanced example).
```

## 💻 Code Example — Advanced
```python
# Production style: Alembic wiring. Files shown in order, commands in comments.

# ---------- shell ----------
# alembic init migrations                       # creates alembic.ini + migrations/env.py
# alembic revision --autogenerate -m "create products"
# alembic upgrade head                          # apply
# alembic current                               # show version
# alembic downgrade -1                          # undo last
# alembic upgrade head --sql                    # print SQL only (offline mode, for DBAs)

# ---------- app/settings.py ----------
from functools import lru_cache  # cache settings
from pydantic_settings import BaseSettings, SettingsConfigDict  # config


class Settings(BaseSettings):  # env-driven config
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/shop"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")  # DATABASE_URL env var


@lru_cache  # one instance
def get_settings() -> Settings:
    return Settings()  # build


# ---------- migrations/env.py (edit the generated file: only these parts) ----------
import os  # env + cwd
import sys  # import path

from alembic import context  # provided by alembic when env.py runs

config = context.config  # alembic Config object
sys.path.insert(0, os.getcwd())  # so `import app` works when running `alembic`
from app.db import Base  # noqa: E402  (your declarative Base)
from app import models  # noqa: E402,F401  (IMPORT MODELS or autogenerate sees nothing)

# Take the URL from env/Settings, not from alembic.ini. Escape % for configparser.
config.set_main_option("sqlalchemy.url", get_settings().database_url.replace("%", "%%"))
target_metadata = Base.metadata  # what autogenerate compares the DB against
# In run_migrations_online(): context.configure(connection=connection,
#     target_metadata=target_metadata, compare_type=True)   # also detect type changes

# ---------- a generated + reviewed migration ----------
# migrations/versions/82357e649b79_create_products.py
import sqlalchemy as sa  # column types
from alembic import op  # migration operations

revision = "82357e649b79"  # this file's id (yours will differ)
down_revision = None  # previous revision (None = first)


def upgrade() -> None:
    op.create_table(  # CREATE TABLE
        "products",
        sa.Column("id", sa.Integer(), nullable=False),  # id column
        sa.Column("name", sa.String(length=100), nullable=False),  # name column
        sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=False),  # price column
        sa.PrimaryKeyConstraint("id"),  # primary key
    )
    op.create_index(op.f("ix_products_name"), "products", ["name"], unique=False)  # index


def downgrade() -> None:
    op.drop_index(op.f("ix_products_name"), table_name="products")  # drop index first
    op.drop_table("products")  # then the table

# ---------- second migration: adding a NOT NULL column to a table with data ----------
# Use a server_default, otherwise existing rows break the NOT NULL rule:
# op.add_column("products", sa.Column("stock", sa.Integer(), server_default="0", nullable=False))
```
What was actually run: a local PostgreSQL 16, `alembic revision --autogenerate` detected `added table 'products'` and the index, `upgrade head` ran `Running upgrade -> 82357e649b79`, `alembic current` printed `82357e649b79 (head)`, a FastAPI `POST /products` with `{"name": "Pen", "price": "12.50"}` returned `{'name': 'Pen', 'price': '12.50', 'id': 1}`, then adding `stock` autogenerated `Detected added column 'products.stock'`, `upgrade head` and `downgrade -1` both worked. Revision ids are random per project. The autogenerated file also contained `sa.Numeric(precision=10, scale=2)` and matched the code above. Note: `pip install greenlet` is needed if you use Alembic's async template (`alembic init -t async`) with `sqlalchemy.ext.asyncio`; without it you get `ImportError: ... requires that the Python 'greenlet' library`.

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: Alembic migration
def upgrade() -> None:
    op.add_column("products", sa.Column("stock", sa.Integer(), server_default="0", nullable=False))
def downgrade() -> None:
    op.drop_column("products", "stock")
# CLI: alembic revision --autogenerate -m "add stock" && alembic upgrade head
```
```javascript
// JavaScript: Knex / Sequelize / Prisma migration
exports.up = (knex) => knex.schema.alterTable("products", (t) => {
  t.integer("stock").notNullable().defaultTo(0);   // add column
});
exports.down = (knex) => knex.schema.alterTable("products", (t) => t.dropColumn("stock"));
// CLI: npx knex migrate:make add_stock && npx knex migrate:latest
// Prisma: npx prisma migrate dev  (generates SQL from schema.prisma)
```

Key differences: Alembic can autogenerate by comparing SQLAlchemy models to the live database (Prisma does similar from its schema); Knex migrations are fully hand-written. Both track versions in a table (`alembic_version` vs `knex_migrations`).

---

## 🟠 FastAPI Connection
FastAPI itself has no migration tool. The usual flow: models live in `app/models`, `get_db` is a dependency, Alembic runs outside the web process (CLI/CI/init container). Do not run migrations inside request handlers or at import time of every worker, because 4 workers would race to migrate.

```python
# Production start script idea (Docker entrypoint): migrate once, then serve
# #!/bin/sh
# set -e
# alembic upgrade head                      # one process migrates
# exec uvicorn app.main:app --host 0.0.0.0 --port 8000   # then serve

# Health route that checks the DB is reachable (useful after deploy)
from typing import Dict  # types
from fastapi import Depends, FastAPI  # framework
from sqlalchemy import text  # raw SQL

app: FastAPI = FastAPI()  # app


@app.get("/health/db")  # readiness probe
def health_db(db=Depends(get_db)) -> Dict[str, str]:  # get_db from the basic example
    db.execute(text("SELECT 1"))  # cheap connectivity check
    return {"db": "ok"}  # healthy
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Models not imported in `env.py`
```python
# Wrong: Base.metadata is empty, autogenerate creates an EMPTY migration (just `pass`)
from app.db import Base

# Right: also import the module(s) that define the models
from app.db import Base
from app import models  # noqa: F401
```

❌ Mistake 2: Trusting autogenerate blindly
```python
# Wrong: alembic upgrade head without reading the file.
# A renamed column is generated as DROP + ADD = data loss!

# Right: read it; for a rename write op.alter_column("t", "old", new_column_name="new") by hand
```

❌ Mistake 3: Adding NOT NULL without a default on a table that already has rows
```python
# Wrong:
op.add_column("products", sa.Column("stock", sa.Integer(), nullable=False))  # fails on existing rows

# Right: server_default="0" (or add nullable, backfill, then set NOT NULL)
```

❌ Mistake 4: Using `create_all()` together with Alembic
```python
# Wrong: Base.metadata.create_all(engine) at startup; schema drifts from migrations
# Right: only Alembic changes the schema (create_all is fine in throwaway unit tests)
```

❌ Mistake 5: Editing an already-applied migration
```python
# Wrong: change an old revision file that already ran in prod
# Right: write a NEW revision that fixes it
```

---

## 🧠 Tricky Interview Question

**Q**: You run `alembic revision --autogenerate -m "noop"` when the models match the database exactly. What do you get?

**Answer**:
```python
def upgrade() -> None:
    pass
def downgrade() -> None:
    pass
```
Alembic still creates a revision file; the bodies are just `pass`. It is harmless but pollutes history, so delete it (or use `--autogenerate` only after changing a model). Verified by running. A related gotcha: if a model is not imported in `env.py`, autogenerate will think there are no tables and generate nothing (or drop tables that exist in the DB).

---

## ⚫ Interview Questions + Answers

Q1: How does Alembic know which migrations are applied?
A1: It stores the current revision id in a one-row table `alembic_version` in your database, then walks the `down_revision` chain.

Q2: What does `compare_type=True` do?
A2: Makes autogenerate detect changes of column types (e.g. `String(50)` to `String(100)`). Recent Alembic versions enable type comparison by default, but setting it explicitly documents intent.

Q3: How do you run migrations in CI/CD safely?
A3: Run `alembic upgrade head` once per deploy (pre-deploy job or init container), keep migrations backward compatible so old and new app versions can both run during a rolling update, and take a backup before destructive changes.

Q4: What is a "multiple heads" error?
A4: Two branches created migrations from the same parent. Fix with `alembic merge heads -m "merge"`, then `upgrade head`.

Q5: Sync or async engine for Alembic?
A5: Migrations can use a normal sync driver even if the app is async (a common, simpler choice). Alembic also has an async template (`alembic init -t async`) that needs `greenlet`.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- You have a real PostgreSQL/MySQL database used by more than one environment
- Schema changes must be reviewable, repeatable and reversible
- You use SQLAlchemy models

❌ Avoid when:
- Throwaway prototypes or tests (`create_all` on SQLite is enough)
- You use another ORM with its own migrations (Django ORM, Prisma)

---

## 📊 Visual Diagram

```
 edit model ──► alembic revision --autogenerate ──► versions/abc123_add_stock.py
                                                         │ (review + commit)
                                                         ▼
 CI / deploy ──► alembic upgrade head ──► PostgreSQL
                                           ├─ products (new column)
                                           └─ alembic_version = abc123
                                                         ▲
 FastAPI app (Depends(get_db)) ──── reads/writes ───────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Migration | One versioned schema change | schema बदलाव का एक versioned कदम |
| Revision | Id of a migration file | migration file की id |
| head | Latest revision | सबसे नई revision |
| autogenerate | Create migration by diffing models vs DB | models और DB की तुलना से migration बनाना |
| alembic_version | Table storing current revision | मौजूदा revision वाली table |
| Downgrade | Undo a migration | migration को वापस करना |

---

## ⚡ 3-Line Summary
English: Alembic gives your PostgreSQL schema a version history. Import models in `env.py`, autogenerate, review the file, `upgrade head` once per deploy, and never edit applied migrations.
Hindi: Alembic आपके PostgreSQL schema को version history देता है। `env.py` में models import करें, autogenerate करें, file देखें, हर deploy पर एक बार `upgrade head` चलाएँ और लागू हो चुकी migration कभी न बदलें।

---

## ➡️ Next Topic
**348. FastAPI Performance Tips** — find and fix the slow parts of a FastAPI service.
