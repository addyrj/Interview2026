# 153. Prisma Migrations
# हिंदी में: Prisma Migrations — Schema Changes को Database में Apply करना

---

## 🔵 Simple Definition (English)
**Prisma Migrate** is Prisma's migration system. When you change `schema.prisma`, running `npx prisma migrate dev` compares the new schema to the current DB state, auto-generates a SQL migration file describing the difference, applies it to the database, and regenerates the Prisma Client. Each migration is saved as a timestamped folder with a `migration.sql` file — a versioned history of every schema change.

## 🔵 सरल परिभाषा (Hindi)
**Prisma Migrate** Prisma का migration system है। `schema.prisma` बदलने के बाद `npx prisma migrate dev` चलाने पर Prisma नई schema को current DB state से compare करता है, difference का SQL migration file auto-generate करता है, DB पर apply करता है, और Prisma Client regenerate करता है। हर migration एक timestamped folder में `migration.sql` के साथ save होता है — हर schema change की versioned history।

---

## 🔴 Problem it Solves
Manually writing SQL migrations (as with raw `pg` or even Sequelize CLI) requires the developer to hand-write `ALTER TABLE` statements correctly, track them in order, and apply them consistently across dev/staging/prod. Mistakes (wrong column type, forgetting an index) are easy to make by hand. Prisma Migrate auto-generates the correct SQL diff from a declarative schema, keeps a clear history folder in git, and separates the DEV workflow (interactive, can reset) from the PROD workflow (`deploy`, strictly applies existing files, never prompts or resets).

## 🔴 यह क्यों बना? (Hindi)
Manually SQL migrations लिखने में (raw `pg` या Sequelize CLI से) developer को `ALTER TABLE` statements हाथ से सही लिखनी पड़ती, order में track करना पड़ता, dev/staging/prod में consistently apply करना पड़ता। गलतियाँ (wrong column type, index भूलना) आसानी से हो जातीं। Prisma Migrate declarative schema से सही SQL diff auto-generate करता है, git में clear history रखता है, और DEV workflow को PROD workflow से अलग रखता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Edit `schema.prisma` (add a field, change a type, add a relation).
Step 2 → Run `npx prisma migrate dev --name add_user_phone` — Prisma computes the diff vs DB's current migration history.
Step 3 → Prisma writes a new folder `prisma/migrations/<timestamp>_add_user_phone/migration.sql` with the raw SQL.
Step 4 → Prisma applies that SQL to your dev database immediately, and records it in the `_prisma_migrations` tracking table.
Step 5 → In CI/production, run `npx prisma migrate deploy` — it ONLY applies pending migration files in order; it never generates new ones or prompts for destructive changes.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `schema.prisma` edit करो (field add, type change, relation add)।
Step 2 → `npx prisma migrate dev --name add_user_phone` चलाओ — Prisma diff compute करता है।
Step 3 → नया folder `prisma/migrations/<timestamp>_add_user_phone/migration.sql` बनता है raw SQL के साथ।
Step 4 → वो SQL dev database पर apply होता है, और `_prisma_migrations` tracking table में record होता है।
Step 5 → CI/production में `npx prisma migrate deploy` चलाओ — ये सिर्फ pending migrations order में apply करता है, नया generate नहीं करता।

---

## 🟡 Real World Example
**Amazon India's returns-processing service** stores all `prisma/migrations/*` folders in git alongside code. Every PR that touches the schema includes its migration file, so reviewers see the EXACT SQL that will run in production. The CI pipeline runs `prisma migrate deploy` automatically before deploying new app code — if a migration would be destructive (e.g., dropping a column with data), `migrate dev` warns the developer locally first, before it ever reaches production.

## 🟡 Real Example Hindi mein
**Amazon India की returns-processing service** सारे `prisma/migrations/*` folders git में code के साथ रखती है। Schema बदलने वाले हर PR में migration file शामिल होती है, reviewers exact SQL देख सकते हैं जो production में चलेगा। CI pipeline deploy से पहले automatically `prisma migrate deploy` चलाता है — destructive change (जैसे data वाला column drop करना) पर `migrate dev` developer को local में ही warn कर देता है।

---

## 💻 Code Example — Basic

```javascript
// This topic is CLI-driven, but here's the JS workflow around it.
// Terminal commands (run these, not JS):
//   npx prisma init                              → creates prisma/schema.prisma
//   npx prisma migrate dev --name init            → first migration, creates tables
//   npx prisma migrate dev --name add_user_phone  → after adding a "phone" field

// basic-migration-check.js — verify migration status programmatically
const { execSync } = require('child_process');

function checkMigrationStatus() {
  try {
    // `prisma migrate status` reports if DB is in sync with migration history
    const output = execSync('npx prisma migrate status', { encoding: 'utf8' });
    console.log(output);
    // Output includes: "Database schema is up to date!" or lists pending migrations
  } catch (err) {
    // Non-zero exit code means migrations are out of sync — fail CI build here
    console.error('Migration status check failed:', err.stdout?.toString());
    process.exit(1);
  }
}

checkMigrationStatus();
```

## 💻 Code Example — Advanced

```javascript
// advanced-migration-workflow.js — CI/CD deploy script pattern (Node.js wrapper)
const { execSync } = require('child_process');
const { PrismaClient } = require('@prisma/client');

async function deploySequence() {
  try {
    console.log('Step 1: Applying pending migrations (production-safe)...');
    // migrate deploy NEVER prompts, NEVER resets, NEVER generates new migrations
    // It only runs migration.sql files that haven't been applied yet, in order.
    execSync('npx prisma migrate deploy', { stdio: 'inherit' });

    console.log('Step 2: Regenerating Prisma Client to match latest schema...');
    execSync('npx prisma generate', { stdio: 'inherit' });

    console.log('Step 3: Running a smoke-test query to confirm DB connectivity...');
    const prisma = new PrismaClient();
    const userCount = await prisma.user.count();
    console.log(`Smoke test passed. Current user count: ${userCount}`);
    await prisma.$disconnect();

    console.log('Deployment migration sequence completed successfully.');
  } catch (err) {
    console.error('DEPLOY FAILED during migration step:', err.message);
    // In a real CI pipeline, this should block the app deployment entirely
    process.exit(1);
  }
}

deploySequence();

/*
Example prisma/migrations/ folder structure after multiple changes:
prisma/migrations/
  20240101120000_init/
    migration.sql
  20240115093000_add_user_phone/
    migration.sql
  20240220141500_add_order_status_index/
    migration.sql
  migration_lock.toml   ← locks the DB provider so you can't mix providers accidentally
*/
```

---

## 🟠 Express.js Integration

```javascript
// Express app — typically migrations run OUTSIDE the app (in CI/deploy scripts),
// but you can add a startup health check that verifies schema sync.
const express = require('express');
const { execSync } = require('child_process');
const { PrismaClient } = require('@prisma/client');

const app = express();
const prisma = new PrismaClient();

// Optional safety net: fail fast on boot if migrations are out of sync
function assertMigrationsApplied() {
  try {
    execSync('npx prisma migrate status', { stdio: 'pipe' });
  } catch (err) {
    console.error('FATAL: Pending migrations detected. Refusing to start server.');
    process.exit(1);
  }
}

assertMigrationsApplied(); // run once at process startup, before listening

app.get('/health', async (req, res) => {
  await prisma.$queryRaw`SELECT 1`; // simple DB connectivity check
  res.json({ status: 'ok' });
});

app.listen(3000, () => console.log('Server started after migration check'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Running `prisma migrate dev` in production
✅ Correct: `migrate dev` can prompt interactively and, in some conflict cases, RESET the database (dropping all data) to resolve drift. Production/CI must ALWAYS use `prisma migrate deploy`, which never resets or prompts.
```javascript
// Wrong (in a deploy script / CI)
execSync('npx prisma migrate dev'); // DANGEROUS in prod — may reset DB!

// Right
execSync('npx prisma migrate deploy'); // safe, only applies existing migrations
```

❌ Mistake 2: Editing a migration file after it's already been applied/committed
✅ Correct: Migration files are meant to be immutable history. If you need to fix something, create a NEW migration (`prisma migrate dev --name fix_xyz`) instead of editing an old `migration.sql` — editing history causes checksum mismatches that Prisma will flag as drift.

---

## 🧠 Tricky Interview Question

```
# Two developers both add a migration locally without pulling each other's changes first.
# Dev A: 20240301_add_phone
# Dev B: 20240301_add_address (created at nearly the same time, before seeing A's migration)
# Dev B pushes first. Dev A pulls and runs `prisma migrate dev`.
```
What happens?

Answer: Prisma detects that Dev A's local DB has a migration (`add_phone`) applied that ISN'T in the migration history Dev A just pulled (which now includes `add_address` but not `add_phone` from A's own earlier local run, depending on order) — this causes a **migration history conflict/drift**. Prisma will warn about divergent migration history and, in `migrate dev`, may prompt to reset the local dev DB to reconcile. The fix: always `git pull` the latest `prisma/migrations/` folder BEFORE running `migrate dev` locally, so your new migration is based on the latest shared history, avoiding conflicting migration timestamps.

---

## ⚫ Interview Questions + Answers

Q1: What's the difference between `prisma migrate dev` and `prisma migrate deploy`?
A1: `migrate dev` is for LOCAL development: it detects schema changes, generates new migration files, applies them, regenerates the client, and can interactively reset the DB if history conflicts. `migrate deploy` is for PRODUCTION/CI: it ONLY applies existing, already-generated migration files in order — it never creates new migrations, never prompts, and never resets data. You should never run `migrate dev` against a production database.

Q2: What is the `_prisma_migrations` table?
A2: It's a special table Prisma creates in your database to track which migrations have been applied, their checksums, and timestamps. This is how `migrate deploy` knows which migration files are "new" and need to run versus which are already applied — it's Prisma's internal migration ledger.

Q3: How do you handle a destructive migration (e.g., dropping a column with existing data) safely?
A3: When `migrate dev` detects a potentially destructive change, it warns you and may ask for confirmation (data loss warning). Best practice for production: split it into multiple migrations — (1) add new column, (2) backfill data via a script, (3) a LATER migration that drops the old column — deployed across separate releases so there's no data loss window.

Q4: What does `prisma migrate resolve` do?
A4: It's used to manually mark a migration as applied or rolled-back in the `_prisma_migrations` tracking table WITHOUT actually running its SQL — useful when a migration was applied manually/outside Prisma, or to recover from a failed migration in production by telling Prisma "treat this as already done" or "treat this as rolled back."

Q5: Can you use Prisma Migrate with an existing (legacy) database?
A5: Yes, via `npx prisma db pull` (introspection) — Prisma reads the existing DB structure and writes a matching `schema.prisma`. Then you'd run `prisma migrate dev --create-only` to baseline the migration history without re-applying SQL that's already there, confirming the first migration matches the existing schema before continuing with normal migrate workflow for future changes.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You want a versioned, reviewable history of every schema change checked into git
- You need separate dev vs. prod migration workflows with safety guarantees
- Working in a team where schema changes go through PR review

❌ Avoid when:
- A DBA team manages schema changes through a separate dedicated tool (Flyway, Liquibase) — don't run two migration systems against the same DB
- You need zero-downtime migrations with very specific sequencing control beyond what Prisma's generated SQL offers (you may need to hand-edit the generated `migration.sql` before applying)

---

## 📊 Visual Diagram
```
PRISMA MIGRATE WORKFLOW
──────────────────────────────────────────────
  DEV:
  schema.prisma change
        │
        ▼
  npx prisma migrate dev --name xyz
        │
        ├──▶ generates prisma/migrations/<ts>_xyz/migration.sql
        ├──▶ applies SQL to dev DB
        └──▶ regenerates PrismaClient

  (commit migrations/ folder to git)

  PROD / CI:
  git pull (includes new migration files)
        │
        ▼
  npx prisma migrate deploy
        │
        └──▶ applies ONLY pending migration.sql files, in order
             (never prompts, never resets, never generates new files)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| migrate dev | Dev-only migration command | Development-only migration command |
| migrate deploy | Production-safe apply command | Production-safe apply command |
| migration.sql | Generated raw SQL file | Generated raw SQL file |
| _prisma_migrations | Internal tracking table | Internal tracking table |
| drift | DB and schema out of sync | DB और schema out of sync |
| migrate resolve | Manually mark migration status | Migration status manually mark करना |
| db pull | Introspect existing DB into schema | Existing DB से schema बनाना |

---

## ⚡ 3-Line Summary
English:
1. `prisma migrate dev` generates and applies migrations locally; `prisma migrate deploy` applies existing migrations safely in production/CI.
2. Every migration is saved as a timestamped SQL file in `prisma/migrations/` — commit this folder to git for a reviewable history.
3. Never run `migrate dev` in production — it can prompt and even reset data; always use `migrate deploy` there.

Hindi:
1. `prisma migrate dev` local में migrations generate+apply करता है; `prisma migrate deploy` production/CI में safely existing migrations apply करता है।
2. हर migration `prisma/migrations/` में timestamped SQL file के रूप में save होती है — इसे git में commit करो।
3. Production में कभी `migrate dev` मत चलाओ — ये data reset कर सकता है; वहाँ हमेशा `migrate deploy` इस्तेमाल करो।

---

## ➡️ Next Topic
**154. Prisma CRUD Operations** — Create, Read, Update, Delete patterns using the generated Prisma Client.
