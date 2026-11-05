---

# 368. Database Migration Pipeline
# हिंदी में: Database Migration Pipeline

---

## 🔵 Simple Definition (English)
A database migration pipeline applies versioned schema changes (Alembic, Prisma, TypeORM, Flyway) automatically and safely as part of a release. It tests migrations on a fresh and a copy-of-production database, takes a backup, runs them once, and only then starts the new application version.

## 🔵 सरल परिभाषा (Hindi)
Database migration pipeline versioned schema बदलावों (Alembic, Prisma, TypeORM, Flyway) को release के हिस्से के रूप में automatically और safely लागू करता है। यह migrations को नए और production-copy database पर test करता है, backup लेता है, एक बार चलाता है और तभी नया application version शुरू करता है।

---

## 🔴 Problem it Solves
- Someone runs SQL by hand on production and forgets to record it.
- App code expects a new column the database does not have yet.
- Two replicas try to migrate at the same time.
- A destructive migration (drop column) runs with no backup.

## 🔴 यह क्यों बना? (Hindi)
- कोई production पर हाथ से SQL चलाता है और record करना भूल जाता है।
- App code को ऐसा नया column चाहिए जो database में अभी है ही नहीं।
- दो replicas एक साथ migrate करने की कोशिश करती हैं।
- Destructive migration (column drop) बिना backup के चल जाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Migration file committed with the code (versioned, never edited after merge)
Step 2 → CI: spin up empty Postgres, run all migrations (upgrade head)
Step 3 → CI: check "downgrade" works or that a down plan exists
Step 4 → CI: migrations vs models drift check (autogenerate produces nothing)
Step 5 → Deploy: pg_dump backup, then run migration ONCE with a lock
Step 6 → Start new app version, health check; on failure follow rollback plan
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Migration file code के साथ commit (versioned, merge के बाद edit नहीं)
Step 2 → CI: खाली Postgres चालू करके सारे migrations चलाना (upgrade head)
Step 3 → CI: "downgrade" काम करता है या down plan मौजूद है, जाँच
Step 4 → CI: migrations बनाम models drift check (autogenerate कुछ न बनाए)
Step 5 → Deploy: pg_dump backup, फिर lock के साथ migration एक बार चलाना
Step 6 → नया app version शुरू, health check; fail पर rollback plan
```

---

## 🟡 Real World Example
A SaaS billing product renamed `amount` to `amount_cents`. A direct rename would have broken old pods mid-deploy. The team used expand/contract: release 1 added `amount_cents` and wrote to both; release 2 backfilled and switched reads; release 3 dropped `amount`. The pipeline backed up the database before each step, and the zero-downtime change took three days but zero minutes of outage.

## 🟡 Real Example Hindi mein
एक SaaS billing product ने `amount` का नाम `amount_cents` करना था। सीधा rename deploy के बीच पुराने pods तोड़ देता। Team ने expand/contract अपनाया: release 1 में `amount_cents` जोड़ा और दोनों में लिखा; release 2 में backfill और reads बदले; release 3 में `amount` हटाया। हर step से पहले pipeline ने backup लिया, और बदलाव में तीन दिन लगे पर outage शून्य मिनट रहा।

---

## 💻 Code / Config Example — Basic

```yaml
# .github/workflows/migrate-test.yml
name: Migration test                   # Name
on:
  pull_request:
    paths: ["migrations/**", "app/models/**"]   # Only when schema code changes
jobs:
  migrate:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine      # Same major version as production
        env:
          POSTGRES_PASSWORD: test      # CI-only password
          POSTGRES_DB: app_test
        ports: ["5432:5432"]
        options: >-
          --health-cmd "pg_isready -U postgres"
          --health-interval 5s --health-timeout 5s --health-retries 10
    env:
      DATABASE_URL: postgresql://postgres:test@localhost:5432/app_test
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
      - run: pip install -r requirements.txt     # Includes alembic
      - run: alembic upgrade head                # Apply all migrations to empty DB
      - run: alembic downgrade -1                # Last migration reversible?
      - run: alembic upgrade head                # And re-applies cleanly
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/migrate-deploy.yml  (production migration job)
name: Migrate and deploy
on:
  workflow_dispatch:                   # Manual trigger with approval
    inputs:
      tag:
        description: Image tag to deploy
        required: true
concurrency:
  group: prod-migrations               # Never run two migrations at once
  cancel-in-progress: false            # Queue, do not cancel a running migration
jobs:
  drift-check:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
        env: { POSTGRES_PASSWORD: test, POSTGRES_DB: app_test }
        ports: ["5432:5432"]
        options: >-
          --health-cmd "pg_isready -U postgres"
          --health-interval 5s --health-timeout 5s --health-retries 10
    env:
      DATABASE_URL: postgresql://postgres:test@localhost:5432/app_test
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12", cache: pip }
      - run: pip install -r requirements.txt
      - run: alembic upgrade head
      - name: Fail if models differ from migrations
        run: alembic check             # Alembic 1.9+ command; exits non-zero if drift exists
  migrate:
    needs: drift-check
    runs-on: ubuntu-latest
    environment: production            # Requires reviewer approval
    steps:
      - uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.VPS_HOST }}
          username: deploy
          key: ${{ secrets.VPS_SSH_KEY }}
          script: |
            set -euo pipefail
            cd /opt/app
            STAMP=$(date +%Y%m%d-%H%M%S)
            # 1. Backup before touching the schema
            docker compose exec -T db pg_dump -U app -Fc app > /var/backups/app-$STAMP.dump
            test -s /var/backups/app-$STAMP.dump            # Backup must not be empty
            # 2. Run migrations once, using the NEW image
            export TAG=${{ github.event.inputs.tag }}
            docker compose pull api
            docker compose run --rm api alembic upgrade head
            # 3. Start the new version
            docker compose up -d api
            sleep 8 && curl -fs http://127.0.0.1:8000/health
```

---

## 🟠 My Stack Integration
For Node/NestJS replace Alembic with `prisma migrate deploy` or `typeorm migration:run`. For FastAPI use Alembic as shown. On a VPS keep backups off the box too:

```bash
# /opt/app/offsite-backup.sh  (run by cron after the deploy backup)
#!/usr/bin/env bash
set -euo pipefail                                   # Stop on any error
aws s3 cp /var/backups/ s3://my-db-backups/prod/ --recursive --exclude "*" --include "*.dump"  # Upload dumps
find /var/backups -name "*.dump" -mtime +7 -delete  # Keep only 7 days locally
```

Not run locally; `alembic check` needs Alembic 1.9 or later. Always rehearse restore from a dump, otherwise the backup is only hope.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Editing an already-applied migration.
✅ Correct: Add a new migration; applied history is immutable.

❌ Mistake 2: `synchronize: true` or `create_all()` in production.
✅ Correct: Explicit migrations only.

❌ Mistake 3: Migrating inside app startup on every replica.
✅ Correct: One dedicated migration step, serialised with `concurrency`.

❌ Mistake 4: Dropping a column in the same release that stops using it.
✅ Correct: Expand, deploy, then contract in a later release.

Security: migration DB user may need DDL rights, but the app runtime user should not. Keep dumps encrypted and access-controlled; they contain customer data.

---

## 🧠 Tricky Interview Question
A migration adding a NOT NULL column with a default takes 20 minutes and locks the table. How do you ship it?

Answer: On big tables a plain `ADD COLUMN ... NOT NULL DEFAULT` may rewrite or lock (behaviour depends on database version). Add the column nullable, backfill in small batches, add a CHECK ... NOT VALID then validate, finally set NOT NULL. Create indexes with `CONCURRENTLY` in Postgres. Test on a production-sized copy.

---

## ⚫ Interview Questions + Answers

Q1: What is expand/contract?
A1: Make schema changes in compatible steps: add new, support both, migrate data, remove old.

Q2: Why back up before migrating?
A2: Down migrations cannot restore deleted data. A restore point can.

Q3: Should migrations run in CI against real data?
A3: Run on an empty DB for correctness and on an anonymised production-sized copy for timing/lock risk.

Q4: How do you stop concurrent migrations?
A4: Pipeline `concurrency`, plus the tool's own lock (Alembic/Flyway use a version table; Postgres advisory locks for custom scripts).

Q5: Rollback strategy?
A5: Prefer roll-forward fixes; restore from backup for destructive failures; keep changes backward compatible so app rollback works without DB rollback.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any relational DB whose schema changes with releases.

❌ Avoid when:
- Schemaless stores with no structural changes need only data-migration scripts, not schema pipelines.

---

## 📊 Visual Diagram
```
 PR: new migration file
     |
 CI: empty DB -> upgrade head -> downgrade -1 -> upgrade -> alembic check
     |
 approval (environment: production)
     |
 VPS: pg_dump -> verify non-empty -> migrate once -> start new app -> /health
                                         |
                                  fail? restore dump / roll-forward fix
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Migration | Versioned schema change | Versioned schema बदलाव |
| Expand/contract | Safe multi-step change | सुरक्षित multi-step बदलाव |
| Drift | Models differ from DB history | Models और DB history में अंतर |
| Backfill | Fill data for new column | नए column में data भरना |
| pg_dump | Postgres backup tool | Postgres backup tool |

---

## ⚡ 3-Line Summary
English: Test migrations in CI on a fresh Postgres and check drift.
English: Back up, then migrate exactly once before starting the new app.
English: Use expand/contract so app rollback never needs DB rollback.
Hindi: CI में नए Postgres पर migrations test करें और drift जाँचें।
Hindi: Backup लें, फिर नया app शुरू करने से पहले ठीक एक बार migrate करें।
Hindi: Expand/contract अपनाएँ ताकि app rollback में DB rollback न लगे।

---

## ➡️ Next Topic
369. Scheduled Jobs Pipeline: cron-style workflows for reports, backups and maintenance.
