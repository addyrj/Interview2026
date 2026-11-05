# 355. Database Migrations in CD
# हिंदी में: CD में Database Migrations

---

## 🔵 Simple Definition (English)
A database migration is a versioned script that changes the schema (add a column, create a table, add an index). In CD, migrations run automatically as a controlled step of the pipeline, in the right order relative to the code release, using tools like Alembic (FastAPI), Prisma/Knex/Sequelize (Node.js) or Flyway.

## 🔵 सरल परिभाषा (Hindi)
Database migration एक versioned script है जो schema बदलती है (column जोड़ना, table बनाना, index जोड़ना)। CD में migrations pipeline के नियंत्रित step के रूप में, code release के सही क्रम में, अपने-आप चलती हैं, Alembic (FastAPI), Prisma/Knex/Sequelize (Node.js) या Flyway जैसे tools से।

---

## 🔴 Problem it Solves
Without automation, someone runs SQL by hand on production, forgets one, or runs the migration after the new code starts and the app crashes on a missing column. Schema drift appears between dev, staging and production. Worse, a destructive change (dropping a column) during a deploy makes rollback impossible because the old code still needs that column.

## 🔴 यह क्यों बना? (Hindi)
Automation के बिना कोई production पर हाथ से SQL चलाता है, एक भूल जाता है, या नया code शुरू होने के बाद migration चलाता है और app missing column पर crash होता है। Dev, staging और production में schema drift आ जाता है। इससे भी बुरा, deploy के दौरान column drop करने से rollback असंभव हो जाता है क्योंकि पुराने code को वह column चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Developer writes a migration file (versioned, in git)
Step 2 → CI applies all migrations to a throwaway database and runs tests
Step 3 → CD backs up / snapshots the production database
Step 4 → CD runs "migrate up" ONCE using the NEW image (before traffic switch)
Step 5 → The migration tool records applied versions in a table (alembic_version)
Step 6 → New code starts; old code still works on the new schema (expand phase)
Step 7 → A later release removes unused columns (contract phase)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Developer migration file लिखता है (versioned, git में)
Step 2 → CI सारी migrations एक throwaway database पर चलाकर tests करता है
Step 3 → CD production database का backup / snapshot लेता है
Step 4 → CD नई image से "migrate up" एक बार चलाता है (traffic switch से पहले)
Step 5 → Migration tool applied versions को table (alembic_version) में लिखता है
Step 6 → नया code शुरू होता है; पुराना code भी नए schema पर चलता है (expand चरण)
Step 7 → बाद का release unused columns हटाता है (contract चरण)
```

---

## 🟡 Real World Example
A team renames `users.name` to `users.full_name`. A naive migration renames the column and deploys; during the rolling update old pods crash because they still query `name`. The safe approach: release 1 adds `full_name` and writes to both columns; a backfill job copies old data; release 2 reads only `full_name`; release 3 drops `name`. Three small safe steps replace one risky step. Companies with zero-downtime requirements (Razorpay, Stripe style) follow this "expand and contract" pattern.

## 🟡 Real Example Hindi mein
एक team `users.name` को `users.full_name` में rename करती है। Naive migration column rename करके deploy करती है; rolling update के दौरान पुराने pods crash होते हैं क्योंकि वे अब भी `name` query करते हैं। सुरक्षित तरीका: release 1 में `full_name` जोड़ो और दोनों columns में लिखो; backfill job पुराना data copy करे; release 2 सिर्फ `full_name` पढ़े; release 3 में `name` drop करो। एक जोखिम भरे कदम की जगह तीन छोटे सुरक्षित कदम।

---

## 💻 Code / Config Example — Basic

```python
# migrations/versions/0002_add_phone.py - Alembic migration (FastAPI/SQLAlchemy)
"""add phone to users"""
from alembic import op            # Alembic operations
import sqlalchemy as sa           # column types

revision = "0002"                 # id of this migration
down_revision = "0001"            # previous migration id (the chain)

def upgrade():
    # nullable column = safe: old code ignores it, inserts without it still work
    op.add_column("users", sa.Column("phone", sa.String(20), nullable=True))

def downgrade():
    # reverse operation (use only when data loss is acceptable)
    op.drop_column("users", "phone")
```

```bash
# basic manual commands
alembic upgrade head              # apply all pending migrations
alembic current                   # show the version applied now
alembic downgrade -1              # revert exactly one step
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/deploy-with-migrations.yml
name: Deploy with Migrations
on:
  push:
    branches: [main]
permissions:
  contents: read
  packages: write
jobs:
  test-migrations:
    runs-on: ubuntu-latest
    services:
      postgres:                                  # throwaway DB for CI
        image: postgres:16-alpine                # example tag
        env:
          POSTGRES_PASSWORD: ci_password         # CI-only secret value
          POSTGRES_DB: app_test
        ports: ["5432:5432"]
        options: >-
          --health-cmd "pg_isready -U postgres"
          --health-interval 5s
          --health-timeout 5s
          --health-retries 10
    env:
      DATABASE_URL: postgresql+psycopg2://postgres:ci_password@localhost:5432/app_test
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12", cache: pip }
      - run: pip install -r requirements.txt
      - run: alembic upgrade head                # apply from scratch
      - run: alembic downgrade base              # prove downgrade works
      - run: alembic upgrade head                # and up again
      - run: pytest -q                           # tests on the migrated schema
  deploy:
    needs: test-migrations                       # only if migrations are sound
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: appleboy/ssh-action@v1.0.3         # example version
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          script: |
            set -euo pipefail
            cd /srv/myapp
            # 1) backup first (compressed custom format)
            docker compose exec -T db pg_dump -U postgres -Fc appdb > "backups/pre_${{ github.sha }}.dump"
            # 2) pull new image
            docker compose pull api
            # 3) run migrations ONCE with the new image, with a lock to prevent concurrent runs
            flock -n /tmp/migrate.lock docker compose run --rm api alembic upgrade head
            # 4) start the new app
            docker compose up -d api
```

```javascript
// Node.js alternative: Prisma - run in the deploy step instead of alembic
// package.json scripts:
//   "migrate:deploy": "prisma migrate deploy"   // applies committed migrations only
// Command in CD:  docker compose run --rm web npx prisma migrate deploy
// NEVER run `prisma migrate dev` in production: it can reset data.
```

```sql
-- Expand/contract example, step 1 (release N): safe additive change
ALTER TABLE users ADD COLUMN full_name text;                      -- nullable, instant
-- Big table index: CONCURRENTLY avoids blocking writes (cannot run inside a transaction)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_full_name ON users (full_name);
-- Step 2 (backfill in small batches, from a script, not one huge UPDATE)
UPDATE users SET full_name = name WHERE id BETWEEN 1 AND 10000 AND full_name IS NULL;
```

---

## 🟠 My Stack Integration
- FastAPI: Alembic with `alembic upgrade head` as a one-off container before `up -d`.
- Node.js: Prisma `migrate deploy`, Knex `migrate:latest` or Sequelize `db:migrate`.
- VPS: take `pg_dump` before; AWS RDS: take a manual snapshot (`aws rds create-db-snapshot`) before risky changes.
- Use a DB user for migrations with DDL rights, and a separate app user with only DML rights.

```yaml
# docker-compose.yml fragment: a dedicated one-off migration service
services:
  migrate:
    image: ${API_IMAGE}                       # same image as the app
    command: ["alembic", "upgrade", "head"]   # run and exit
    env_file: .env.migrate                    # DDL-capable credentials
    depends_on:
      db:
        condition: service_healthy
    profiles: ["tools"]                       # not started by plain `up`
# run it with: docker compose run --rm migrate
```

Security: keep DDL credentials only in the migration job, never in the running app. Never log connection strings. Restrict who can approve the production environment.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Every replica runs migrations at startup.
✅ Correct: Run once in a dedicated step with a lock.

❌ Mistake 2: Dropping or renaming columns in the same release as the code change.
✅ Correct: Use expand/contract over multiple releases.

❌ Mistake 3: No backup before migrating.
✅ Correct: Take `pg_dump` or an RDS snapshot first, and test restore.

❌ Mistake 4: Adding an index without `CONCURRENTLY` on a busy Postgres table.
✅ Correct: Use `CREATE INDEX CONCURRENTLY` to avoid long write locks.

❌ Mistake 5: Editing an already-applied migration file.
✅ Correct: Add a new migration; applied history must never change.

---

## 🧠 Tricky Interview Question
Your pipeline runs the migration, then the app deploy fails its health check and you roll back the code. Is the rollback safe?

Answer: Only if the migration was backward compatible. The old code now runs against the new schema. If the migration only added nullable columns or tables, yes. If it dropped or renamed something, the old code breaks, and you would need a restore or a downgrade, which may lose data. That is why rollback safety is designed in the migration, not in the deploy tool.

---

## ⚫ Interview Questions + Answers

Q1: Why run migrations before the new code?
A1: New code usually expects the new schema. With expand-only changes, old code tolerates the new schema, so the order "migrate then deploy" works for both.

Q2: What is expand/contract?
A2: Expand by adding new structures compatibly, migrate data and code, then contract by removing old structures in a later release.

Q3: How do you prevent two pipelines migrating at once?
A3: Use a lock (`flock`, advisory lock in the DB, or the tool's own lock) and a GitHub `concurrency` group.

Q4: Should migrations be reversible?
A4: Write `downgrade` where practical, but plan for roll-forward fixes; destructive downgrades can lose data.

Q5: How do you migrate a huge table without downtime?
A5: Add columns nullable, backfill in batches, create indexes concurrently, and use online schema-change tools (pt-osc, gh-ost for MySQL).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Schema changes ship with application code regularly.
- You need repeatable environments (dev, staging, prod).

❌ Avoid when:
- A one-time data fix is needed: run it as a reviewed script/job, not as a standard migration.
- The change is huge and risky: schedule a maintenance window with a rehearsed plan.

---

## 📊 Visual Diagram
```
 push main
    |
    v
 CI: empty DB -> alembic upgrade head -> tests (and downgrade test)
    |
    v
 CD: [backup pg_dump / RDS snapshot]
    |
    v
 [docker compose run --rm api alembic upgrade head]   <- ONCE, with lock
    |
    v
 [docker compose up -d api]  --> health check --> done
        (old code must still work on the NEW schema)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Migration | Versioned schema change script | versioned schema बदलाव script |
| Expand/Contract | Add first, remove later | पहले जोड़ो, बाद में हटाओ |
| Backfill | Fill new column with old data | पुराना data नए column में भरना |
| Schema drift | Environments differ in schema | environments में schema का अंतर |
| Advisory lock | DB lock for coordination | coordination के लिए DB lock |

---

## ⚡ 3-Line Summary
English: Run versioned migrations once per release in a dedicated pipeline step, after a backup.
Make every change backward compatible with expand/contract so rollback stays possible.
Test migrations on a clean database in CI.
Hindi: Backup के बाद versioned migrations को हर release में एक dedicated step में एक बार चलाओ।
हर बदलाव expand/contract से backward compatible रखो ताकि rollback संभव रहे।
CI में साफ database पर migrations test करो।

---

## ➡️ Next Topic
**356. Rollback Strategy** — how to return to the last good version quickly and safely.
