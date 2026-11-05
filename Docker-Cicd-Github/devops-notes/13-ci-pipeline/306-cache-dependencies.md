# 306. Cache Dependencies
# हिंदी में: Dependencies को Cache करना

---

## 🔵 Simple Definition (English)
`actions/cache` saves a folder (like `~/.npm`, `~/.cache/pip`, or `.next/cache`) at the end of a job under a **key**, and restores it at the start of later runs when the key matches. It avoids re-downloading or rebuilding the same things every time.

## 🔵 सरल परिभाषा (Hindi)
`actions/cache` job के अंत में किसी folder (जैसे `~/.npm`, `~/.cache/pip`, `.next/cache`) को एक **key** के नीचे save करती है और बाद के runs में key match होने पर शुरुआत में restore करती है। इससे वही चीज़ें बार-बार download या build नहीं करनी पड़तीं।

---

## 🔴 Problem it Solves
Every run starts on a clean VM. Without a cache, each run downloads 800 MB of npm packages or pip wheels again, and rebuilds Next.js and TypeScript output from zero. A 3-minute job becomes 9 minutes, GitHub minutes cost money, and developers wait. Registry outages or rate limits also break builds.

## 🔴 यह क्यों बना? (Hindi)
हर run साफ़ VM पर शुरू होता है। Cache के बिना हर run में 800 MB के npm packages या pip wheels फिर से download होते हैं और Next.js व TypeScript output शून्य से बनता है। 3 मिनट की job 9 मिनट की हो जाती है, GitHub minutes पर पैसा लगता है और developers इंतज़ार करते हैं। Registry बंद हो या rate limit लगे तो builds टूटते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You define path (what to save) and key (identity of the content)
Step 2 → Typical key = OS + tool + hash of lockfile
Step 3 → At step time: exact key match? -> restore, cache-hit = 'true'
Step 4 → No exact match: try restore-keys prefixes (newest match wins)
         -> restores partial cache, cache-hit = 'false'
Step 5 → Job runs; dependencies mostly present, only new ones download
Step 6 → Post step: if there was NO exact hit, upload path under the key
Step 7 → Caches are immutable per key; a new lockfile hash = new key
Step 8 → Eviction: unused 7 days, or repo total over limit (10 GB default)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → आप path (क्या save करना है) और key (content की पहचान) तय करते हैं
Step 2 → सामान्य key = OS + tool + lockfile का hash
Step 3 → Step पर: exact key match? -> restore, cache-hit = 'true'
Step 4 → Exact match नहीं: restore-keys prefixes आज़माता है (सबसे नया match जीतता है)
         -> आंशिक cache restore, cache-hit = 'false'
Step 5 → Job चलती है; ज़्यादातर dependencies मौजूद, सिर्फ़ नई download होती हैं
Step 6 → Post step: exact hit नहीं था तो path को key के नीचे upload करता है
Step 7 → हर key का cache immutable है; नया lockfile hash = नई key
Step 8 → Eviction: 7 दिन unused, या repo का कुल size limit (default 10 GB) पार
```

---

## 🟡 Real World Example
A Next.js e-commerce app has 1,400 npm packages. CI downloaded them in 70 s every run. After caching `~/.npm` keyed by `package-lock.json`, `npm ci` takes 14 s. Caching `.next/cache` also cut `next build` from 4 min to 1.5 min because unchanged pages are reused. In a FastAPI repo, caching `~/.cache/pip` plus `~/.cache/pre-commit` saved another 40 s.

## 🟡 Real Example Hindi mein
एक Next.js e-commerce app में 1,400 npm packages हैं। CI हर run में उन्हें 70 सेकंड में download करता था। `package-lock.json` की key से `~/.npm` cache करने के बाद `npm ci` 14 सेकंड में होता है। `.next/cache` cache करने से `next build` 4 मिनट से 1.5 मिनट रह गया क्योंकि unchanged pages दोबारा इस्तेमाल होते हैं। FastAPI repo में `~/.cache/pip` और `~/.cache/pre-commit` cache करने से 40 सेकंड और बचे।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/cache-basic.yml
name: Cache Basic                      # workflow name

on: [push]                             # trigger

jobs:
  build:
    runs-on: ubuntu-latest             # Linux runner
    steps:
      - uses: actions/checkout@v4      # get code
      - uses: actions/setup-node@v4    # Node
        with:
          node-version: 20
      - name: Cache npm downloads
        id: npm-cache                  # id to read cache-hit output
        uses: actions/cache@v4         # the cache action
        with:
          path: ~/.npm                 # folder to save/restore
          key: npm-${{ runner.os }}-${{ hashFiles('package-lock.json') }}
                                       # changes only when lockfile changes
          restore-keys: |              # fallback prefixes for partial hits
            npm-${{ runner.os }}-
      - run: npm ci                    # fast: packages come from ~/.npm
      - run: echo "hit=${{ steps.npm-cache.outputs.cache-hit }}"   # true/false
```
(Tip: `setup-node` with `cache: npm` does the same in one line; use `actions/cache` directly when you need custom paths.)

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/cache-advanced.yml
name: Cache Advanced

on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read
  actions: write                       # needed only if you delete caches via API

jobs:
  web:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: web
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version-file: web/.nvmrc
          cache: npm                                    # download cache handled here
          cache-dependency-path: web/package-lock.json

      # Next.js build cache: key on lockfile + source files, fall back to lockfile-only
      - name: Cache Next.js build
        uses: actions/cache@v4
        with:
          path: |                                       # multiple paths allowed
            web/.next/cache
          key: nextjs-${{ runner.os }}-${{ hashFiles('web/package-lock.json') }}-${{ hashFiles('web/src/**/*.[jt]s', 'web/src/**/*.[jt]sx') }}
          restore-keys: |
            nextjs-${{ runner.os }}-${{ hashFiles('web/package-lock.json') }}-
            nextjs-${{ runner.os }}-

      - run: npm ci
      - run: npm run build

  api:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
          cache-dependency-path: pricing/requirements*.txt

      # Docker layer cache through the GitHub Actions cache backend (BuildKit)
      - uses: docker/setup-buildx-action@v3
      - uses: docker/build-push-action@v6
        with:
          context: pricing
          push: false                                   # build only in CI
          tags: pricing:ci
          cache-from: type=gha                          # read layers from Actions cache
          cache-to: type=gha,mode=max                   # write all layers back

  # Optional hygiene: restore-only (do not write) in PRs to avoid cache churn
  restore-only-example:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/cache/restore@v4                  # restore without saving
        with:
          path: ~/.npm
          key: npm-${{ runner.os }}-${{ hashFiles('**/package-lock.json') }}
          restore-keys: npm-${{ runner.os }}-
```

---

## 🟠 My Stack Integration
- **Node.js / React:** `setup-node` `cache: npm`, plus `.next/cache` or `node_modules/.cache` (Vite/Webpack/ESLint caches).
- **FastAPI:** `cache: pip` (or poetry), plus `~/.cache/pre-commit` and `.mypy_cache`.
- **Docker / VPS:** `cache-from: type=gha` speeds image builds before pushing to your registry for the VPS to pull.
- **AWS:** cache Terraform providers (`~/.terraform.d/plugin-cache`) and `~/.cache/pip` for the AWS CLI tooling.
- **Security:** never cache secrets, `.env`, `~/.aws`, or `.npmrc` with tokens. Caches on a branch can be read by workflows on the same repo, so a poisoned cache can affect later runs.

```yaml
# safest default for your React + Express repos: let setup-node manage it
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm            # key = lockfile hash, path = ~/.npm
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Caching `node_modules` and skipping `npm ci`. It can contain wrong platform binaries and stale packages.
✅ Correct: Cache `~/.npm` and always run `npm ci`.

❌ Mistake 2: A static key like `key: my-cache`. It is saved once and never updates (keys are immutable).
✅ Correct: Include a hash: `${{ hashFiles('**/package-lock.json') }}`.

❌ Mistake 3: Forgetting `runner.os` in the key; Linux and macOS caches collide.
✅ Correct: Prefix `${{ runner.os }}-` (and architecture if self-hosted ARM).

❌ Mistake 4: Putting secrets or tokens in cached paths.
✅ Correct: Cache only public build/download data; remove credentials before the post step.

❌ Mistake 5: Using `restore-keys` that are too broad, so a wrong old cache is used and hides real dependency problems.
✅ Correct: Use restore-keys only for performance, and keep `npm ci` / `pip install` verifying correctness.

---

## 🧠 Tricky Interview Question
**Q:** The cache key is `npm-${{ hashFiles('package-lock.json') }}`. You merge a PR that changes the lockfile; the next run on `main` is slow. A teammate's open PR (not rebased) is still fast. Why?

**Answer:** A new lockfile hash creates a new key, so `main` has a cache miss and rebuilds/saves it. The teammate's PR still has the old lockfile, so it computes the old key and hits the older cache. Caches are scoped by branch: a PR can restore from its own ref and from the base/default branch, but not from other PR branches; and entries are immutable, so nothing is overwritten. Once `main` saves the new key, rebased PRs will hit it.

---

## ⚫ Interview Questions + Answers

Q1: What is `restore-keys`?
A1: An ordered list of key prefixes used when the exact key misses. GitHub restores the most recent cache whose key starts with a prefix. The step reports `cache-hit: false` but the job gets a partial cache.

Q2: Can you overwrite an existing cache key?
A2: No, cache entries are immutable. To update, change the key (e.g. add the lockfile hash or a run id suffix with restore-keys fallback).

Q3: What are cache limits and eviction rules?
A3: By default 10 GB per repository (configurable by admins on paid plans); caches not accessed for 7 days are deleted, and oldest are evicted when over the limit. Check current docs as limits can change.

Q4: What is the difference between `actions/cache`, `actions/cache/restore`, and `.../save`?
A4: `cache` restores and then auto-saves in the post step; `restore` only restores; `save` only saves (useful when you want to save even on failure or control exactly when).

Q5: Cache vs artifact?
A5: Cache = speed-up of reusable inputs across runs (best-effort, may be missing). Artifact = output of a run you want to download or pass between jobs (reliable for that run).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Dependency downloads or compile steps repeat across runs
- Build tool caches exist (Next.js, Gradle, Terraform plugins, pre-commit)
- Docker builds with many layers (via buildx cache)

❌ Avoid when:
- Content must always be fresh or verified (use artifacts or fresh install)
- It would contain secrets
- The cache is bigger than the download time it saves

---

## 📊 Visual Diagram
```
             Run #1 (miss)                         Run #2 (hit)
  key = npm-Linux-<hash A>              key = npm-Linux-<hash A>
        |                                     |
   cache lookup: none                    cache lookup: FOUND
        |                                     |
   npm ci downloads 800MB                restore ~/.npm  (fast)
        |                                     |
   post: SAVE ~/.npm under key A         npm ci installs from disk
                                         post: skip save (exact hit)

  Lockfile changes -> hash B -> miss -> try restore-keys "npm-Linux-"
                                    -> partial restore (old packages)
                                    -> download only the difference -> save as B
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Cache key | Identity string of a cache | cache की पहचान |
| `restore-keys` | Fallback key prefixes | fallback key prefixes |
| `hashFiles()` | Hash of files for keys | files का hash |
| Cache hit/miss | Found or not found | मिला / नहीं मिला |
| Immutable | Cannot overwrite a key | key बदली नहीं जा सकती |
| Eviction | Automatic deletion of old caches | पुराने caches का हटना |
| `type=gha` | Docker BuildKit cache backend | Docker cache backend |

---

## ⚡ 3-Line Summary
English: `actions/cache` saves folders under a key and restores them in later runs.
Build the key from OS plus a hash of the lockfile, use `restore-keys` for partial hits, and never cache secrets.
Cache downloads (`~/.npm`, `~/.cache/pip`), not `node_modules`, and still run `npm ci`.
Hindi: `actions/cache` folders को एक key के नीचे save करती है और बाद के runs में restore करती है।
Key OS और lockfile hash से बनाएँ, आंशिक hits के लिए `restore-keys` लें, और secrets कभी cache न करें।
Downloads (`~/.npm`, `~/.cache/pip`) cache करें, `node_modules` नहीं, और फिर भी `npm ci` चलाएँ।

---

## ➡️ Next Topic
**307. Install Dependencies** — now that caches are warm, install packages the reproducible way.
