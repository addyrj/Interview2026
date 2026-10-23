---

# 361. Alembic Migrations — Complete Guide
# हिंदी में: Alembic Migrations — पूरी Guide

---

## 🔵 Simple Definition (English)
Alembic is the database migration tool for SQLAlchemy. Migrations track schema changes (add column, create table, modify index) as versioned Python scripts — like `git` for your database schema. In production: never run raw SQL manually. Use Alembic to: create migrations, apply them forward (`upgrade`), roll them back (`downgrade`). Works with PostgreSQL, MySQL, SQLite.

## 🔵 सरल परिभाषा (Hindi)
Alembic = SQLAlchemy के लिए database migration tool। Migrations = schema changes (add column, create table) versioned Python scripts — database schema के लिए `git` जैसा। Production में: raw SQL manually नहीं। Alembic से: migrations create, apply (`upgrade`), rollback (`downgrade`)।

---

## 💻 Code Example — Basic Setup
```bash
# ─── Install ──────────────────────────────────────────────────────
pip install alembic

# ─── Initialize Alembic in project ──────────────────────────────
alembic init alembic
# Creates:
# alembic/
#   env.py          ← configure your DB URL and models
#   script.py.mako  ← migration template
#   versions/       ← all migration files live here
# alembic.ini       ← config file

# ─── alembic.ini — set DB URL ────────────────────────────────────
# sqlalchemy.url = postgresql://user:pass@localhost/mydb
# (or use env var — see env.py below)
```

```python
# ─── alembic/env.py — configure to use your models ───────────────
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os

# Import your SQLAlchemy models' Base:
from myapp.models import Base   # your declarative base
from myapp.config import settings  # your settings

config = context.config

# Override DB URL from environment (don't hardcode!):
config.set_main_option("sqlalchemy.url", settings.database_url)

target_metadata = Base.metadata   # Alembic uses this to detect changes

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,   # NullPool for migrations
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()

run_migrations_online()
```

```bash
# ─── Create a migration (auto-detect model changes) ───────────────
alembic revision --autogenerate -m "add_users_table"
# Compares current DB schema vs your SQLAlchemy models
# Generates: alembic/versions/abc123_add_users_table.py

# ─── Apply migrations (upgrade to latest) ───────────────────────
alembic upgrade head           # apply all pending migrations
alembic upgrade +1             # apply one migration

# ─── Rollback ────────────────────────────────────────────────────
alembic downgrade -1           # roll back one migration
alembic downgrade base         # roll back ALL migrations

# ─── Check current version ───────────────────────────────────────
alembic current                # shows current revision
alembic history --verbose      # full migration history
```

## 💻 Code Example — Migration Files
```python
# ─── alembic/versions/001_initial_tables.py ──────────────────────
"""Initial tables

Revision ID: 001abc
Revises: 
Create Date: 2024-01-15 10:00:00
"""
from alembic import op
import sqlalchemy as sa

# Unique identifier for this migration:
revision = "001abc"
down_revision = None   # None = this is the first migration
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Apply this migration — runs on 'alembic upgrade'."""
    op.create_table(
        "tariff_codes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("hs_code", sa.String(10), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("duty_rate", sa.Float(), server_default="0.0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            onupdate=sa.func.now()
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("hs_code"),
    )
    op.create_index("ix_tariff_codes_hs_code", "tariff_codes", ["hs_code"])

def downgrade() -> None:
    """Reverse this migration — runs on 'alembic downgrade'."""
    op.drop_index("ix_tariff_codes_hs_code")
    op.drop_table("tariff_codes")

# ─── Adding a column to existing table ───────────────────────────
# alembic/versions/002_add_category.py

def upgrade() -> None:
    op.add_column(
        "tariff_codes",
        sa.Column("category", sa.String(50), nullable=True),
    )

def downgrade() -> None:
    op.drop_column("tariff_codes", "category")

# ─── Data migration (not just schema) ────────────────────────────
# alembic/versions/003_populate_categories.py

from sqlalchemy.sql import table, column

def upgrade() -> None:
    # First, add the column:
    op.add_column("tariff_codes", sa.Column("category", sa.String(50)))
    
    # Then populate it:
    tariff_table = table("tariff_codes",
        column("hs_code", sa.String),
        column("category", sa.String),
    )
    op.execute(
        tariff_table.update()
        .where(tariff_table.c.hs_code.like("85%"))
        .values(category="Electronics")
    )

def downgrade() -> None:
    op.drop_column("tariff_codes", "category")
```

```python
# ─── Running migrations in FastAPI startup ────────────────────────
from contextlib import asynccontextmanager
from alembic.config import Config
from alembic import command

def run_migrations():
    """Run Alembic migrations programmatically."""
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run migrations at startup (useful in testing/Docker):
    run_migrations()
    yield

# Or in Docker CMD:
# alembic upgrade head && uvicorn main:app ...
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python Alembic:
# alembic revision --autogenerate -m "add_users"
# alembic upgrade head

# Migration file:
def upgrade():
    op.add_column("users", sa.Column("email", sa.String(255)))

def downgrade():
    op.drop_column("users", "email")
```

```javascript
// TypeORM migrations (NestJS):
// npx typeorm migration:generate AddEmail
// npx typeorm migration:run

export class AddEmail1234 implements MigrationInterface {
    async up(queryRunner: QueryRunner) {
        await queryRunner.addColumn("users",
            new TableColumn({ name: "email", type: "varchar" })
        );
    }
    async down(queryRunner: QueryRunner) {
        await queryRunner.dropColumn("users", "email");
    }
}
```

Key similarities: both auto-generate migrations from model changes. Both use `up/upgrade` and `down/downgrade`. Both track applied migrations in a special DB table.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Auto-generate and blindly apply
```bash
# Wrong — autogenerate doesn't catch everything:
alembic revision --autogenerate -m "changes"
alembic upgrade head   # apply without reviewing!

# Correct — always review generated migration:
alembic revision --autogenerate -m "changes"
# OPEN the generated file and review it!
# Check: are all changes captured? Any destructive ops?
# Then apply:
alembic upgrade head
```

❌ Mistake 2: Dropping columns in the same migration as adding them
```python
# Wrong — data loss if upgrade succeeds but app can't handle new schema:
def upgrade():
    op.drop_column("users", "old_email")
    op.add_column("users", sa.Column("email_v2", sa.String(255)))

# Correct — do it in 3 migrations:
# Migration 1: add new column
# Migration 2: backfill data (copy old → new)
# Migration 3: drop old column (after deploy confirms all is well)
```

---

## 🧠 Tricky Interview Question

**Q**: How do you handle migrations in a zero-downtime deployment?

**Answer**: Backward-compatible migrations strategy: (1) **Expand phase** (deploy with new migration first): add new columns as nullable, add new tables. Old code ignores new columns. (2) **Migrate phase**: deploy new code that writes to both old + new columns. (3) **Contract phase** (second migration): drop old columns once all code uses new ones. Never: make a column NOT NULL without a default on an existing table (locks table), drop a column that current code still reads, rename a column (effectively drop + add). Always: use nullable + default first, give yourself a rollback window.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `--autogenerate` and manual migration?
A1: `--autogenerate` compares your SQLAlchemy models (`Base.metadata`) against the current DB schema and generates a migration script for the differences. Fast for: new tables, new columns, new indexes. Misses: custom DB types, stored procedures, complex constraints, check constraints on some DBs. Always review autogenerated migrations. Manual migration: write `op.create_table()` / `op.add_column()` etc. yourself — full control. Use autogenerate as a starting point, then edit.

Q2: What is `alembic_version` table?
A2: Alembic creates a `alembic_version` table in your database with one row: the current migration revision ID (e.g., `"abc123"`). `alembic upgrade head` checks this, runs all migrations with `down_revision` forming a chain from current to latest. `alembic current` reads from this table. Multiple heads are possible (branching migrations) — use `alembic merge` to combine branches. In testing: `alembic downgrade base` drops to clean state; `alembic upgrade head` recreates all tables.

Q3: How do you run migrations in Docker/production automatically?
A3: CMD in Dockerfile: `CMD alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000`. Or separate migration container in docker-compose: `command: alembic upgrade head` with `depends_on: db`. Kubernetes: use an init container that runs migrations before the app pod starts. FastAPI lifespan: `run_migrations()` call (works for single-instance deployment; for multi-pod: use K8s Job instead to avoid race conditions). Always: migrations before new app code deploys.

Q4: What is the difference between schema migration and data migration?
A4: **Schema migration**: changes to table structure — add/drop column, create/drop table, add index. Pure DDL (Data Definition Language). **Data migration**: transforming existing data — populate new column from old, merge two tables, normalize data. Alembic handles both but data migrations need SQL inside `op.execute()`. Risk: schema migrations are usually fast. Data migrations on large tables can lock and take minutes — do them in batches: `UPDATE ... WHERE id BETWEEN 1 AND 10000; UPDATE ... WHERE id BETWEEN 10001 AND 20000;`.

Q5: How do you test migrations?
A5: (1) CI: fresh DB, `alembic upgrade head` — verify it runs clean. (2) Also test `downgrade -1` then `upgrade +1` — verify round-trip works. (3) Check final schema matches expected: `alembic check` (raises if models don't match DB). (4) Data migration tests: seed test data, run migration, verify data transformed correctly. (5) Use separate test DB (not production!). In pytest: `@pytest.fixture(scope="session")` that creates test DB with `alembic upgrade head`, runs all tests, drops DB after.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Migration | Schema change script | Schema change script |
| revision | Migration version ID | Migration version ID |
| upgrade | Apply migration forward | Migration forward apply |
| downgrade | Roll back migration | Migration roll back |
| autogenerate | Auto-detect model changes | Model changes auto-detect |
| head | Latest migration version | Latest migration |
| alembic_version | DB table tracking current version | Current version track करना |

---

## ⚡ 3-Line Summary
English: Alembic tracks database schema changes as versioned Python scripts — `alembic revision --autogenerate -m "name"` creates, `alembic upgrade head` applies. Always review autogenerated migrations before applying — they miss stored procedures, complex constraints, and sometimes generate wrong SQL. For zero-downtime deploys: never drop columns in the same migration that adds their replacements — expand → migrate data → contract.
Hindi: Alembic = versioned schema change scripts। `--autogenerate` से create, `upgrade head` से apply। हमेशा review करो। Zero-downtime: column drop और add एक साथ नहीं — expand → data migrate → contract।

---

## ➡️ Next Topic
**352. psycopg2 vs asyncpg** — sync vs async PostgreSQL drivers. **364. pymongo** — MongoDB async driver. **370. Connection Pooling** — pgbouncer, SQLAlchemy pool settings.
