# 285. Caching in GitHub Actions
# हिंदी में: GitHub Actions में Caching

---

## 🔵 Simple Definition (English)
Caching in GitHub Actions means saving files that are slow to recreate (npm packages, pip wheels, Docker layers, build output) after one run and restoring them at the start of the next run. Runners are fresh VMs, so without cache every run downloads everything again. Cache is stored by GitHub per repository, identified by a **key**, and is meant for speed only, never for correctness.

## 🔵 सरल परिभाषा (Hindi)
GitHub Actions में caching का मतलब है ऐसी files (npm packages, pip wheels, Docker layers, build output) जिन्हें दोबारा बनाना धीमा है, उन्हें एक run के बाद सहेजना और अगले run की शुरुआत में restore करना। Runner हर बार नई VM होती है, इसलिए cache के बिना हर run में सब कुछ फिर download होता है। Cache GitHub में repository के हिसाब से **key** से रखा जाता है और सिर्फ़ speed के लिए होता है, correctness के लिए नहीं।

---

## 🔴 Problem it Solves
A Node.js project with 900 dependencies spends 60-90 seconds on `npm ci` every push. A FastAPI project with numpy/pandas spends minutes building wheels. With 50 pushes a day across a team, that is hours of waiting and paid runner minutes burned on downloading the same bytes. Caching cuts this to a few seconds and lowers load on npm/PyPI registries.

## 🔴 यह क्यों बना? (Hindi)
900 dependencies वाला Node.js project हर push पर `npm ci` में 60-90 सेकंड लगाता है। numpy/pandas वाला FastAPI project wheels बनाने में मिनटों लगाता है। दिन में 50 pushes हों तो घंटों का इंतज़ार और वही bytes बार-बार download करने में runner minutes का खर्च। Caching इसे कुछ सेकंड में ला देती है और npm/PyPI पर load भी घटाती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Workflow starts on a clean runner (no node_modules, no ~/.npm)
Step 2 → Cache step computes a key, e.g. npm-Linux-<hash of package-lock.json>
Step 3 → GitHub looks for an exact key match; if none, tries restore-keys prefixes
Step 4 → HIT: archive is downloaded and extracted to the given path
         MISS: nothing restored, job continues and installs normally
Step 5 → Job finishes successfully; post step saves the path under the key
         (only if there was no exact hit; keys are immutable once saved)
Step 6 → Old unused caches are evicted (7 days unused, repo total limit 10 GB)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Workflow साफ़ runner पर शुरू होता है (न node_modules, न ~/.npm)
Step 2 → Cache step key बनाता है, जैसे npm-Linux-<package-lock.json का hash>
Step 3 → GitHub exact key खोजता है; न मिले तो restore-keys prefixes आज़माता है
Step 4 → HIT: archive download होकर दिए गए path में extract
         MISS: कुछ restore नहीं, job सामान्य install करता है
Step 5 → Job सफल होने पर post step path को key के नाम से save करता है
         (सिर्फ़ तब जब exact hit नहीं था; key एक बार save होकर बदलती नहीं)
Step 6 → पुराने unused caches हटते हैं (7 दिन unused, repo की कुल limit 10 GB)
```

---

## 🟡 Real World Example
A startup's monorepo (React + Node API) took 7 minutes per CI run, 3 of them installing packages. After adding `setup-node` with `cache: npm` and a pip cache for the FastAPI service, the install phase dropped to ~20 seconds. With 80 runs a day, the team saved roughly 4 hours of runner time daily. The same idea powers big companies: Swiggy-style monorepos cache `node_modules`/Gradle so PR checks return in minutes.

## 🟡 Real Example Hindi mein
एक startup के monorepo (React + Node API) का CI run 7 मिनट लेता था, जिसमें 3 मिनट packages install में जाते थे। `setup-node` में `cache: npm` और FastAPI के लिए pip cache जोड़ने पर install ~20 सेकंड में हो गया। दिन में 80 runs पर team ने रोज़ लगभग 4 घंटे runner time बचाया। Swiggy जैसे बड़े monorepos भी `node_modules`/Gradle cache करके PR checks मिनटों में पूरे करते हैं।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/ci-basic.yml
name: ci-basic                            # workflow name
on: [push, pull_request]                  # run on push and PRs
jobs:
  test:
    runs-on: ubuntu-latest                # GitHub-hosted runner
    steps:
      - uses: actions/checkout@v4         # fetch the code
      - uses: actions/setup-node@v4       # install Node.js
        with:
          node-version: 20                # example version
          cache: npm                      # built-in caching of ~/.npm, key from package-lock.json
      - run: npm ci                       # fast on cache hit (uses local npm cache)
      - run: npm test                     # run unit tests
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/ci-advanced.yml
# Node (React + API) and Python (FastAPI) with explicit caches
name: ci-advanced                         # workflow name
on:
  pull_request:                           # checks on PRs
  push:
    branches: [main]                      # and on main (main creates caches PRs can read)
permissions:
  contents: read                          # least privilege
jobs:
  web:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - name: Cache npm download cache    # cache the npm cache dir, not node_modules
        uses: actions/cache@v4            # example version
        with:
          path: ~/.npm                    # npm's global cache directory
          key: npm-${{ runner.os }}-${{ hashFiles('web/package-lock.json') }}   # changes when deps change
          restore-keys: |
            npm-${{ runner.os }}-
      - run: npm ci                       # clean, reproducible install
        working-directory: web
      - run: npm run build                # build React
        working-directory: web
  api:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5     # install Python
        with:
          python-version: '3.12'          # example version
          cache: pip                      # caches pip download cache
          cache-dependency-path: api/requirements.txt   # hash source for the key
      - run: pip install -r requirements.txt   # fast after first run
        working-directory: api
      - run: python -m pytest -q          # run tests
        working-directory: api
  docker:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3   # buildx needed for cache backends
      - uses: docker/build-push-action@v6     # example version
        with:
          context: .                      # build context
          push: false                     # just build in CI
          cache-from: type=gha            # read layers from the GitHub cache
          cache-to: type=gha,mode=max     # write all layers back
```

---

## 🟠 My Stack Integration
- **Node.js / React**: cache `~/.npm` (safe) rather than `node_modules` (OS and Node-version sensitive). `setup-node` with `cache:` does this for you.
- **FastAPI**: `setup-python` with `cache: pip`, or cache `~/.cache/pip`; for uv/poetry cache their own directories.
- **Docker image builds** for the VPS/ECR: `type=gha` BuildKit cache saves layers.
- **Nginx / VPS**: caches live only in CI, never on the VPS; deploy steps should not depend on cache.
- **AWS**: caches are free within 10 GB per repo; for huge caches use self-hosted runners with local disk or S3-based cache actions.

```yaml
# Snippet: cache the Next/Vite build cache for faster rebuilds
      - uses: actions/cache@v4
        with:
          path: web/node_modules/.vite    # Vite's cache folder (example)
          key: vite-${{ runner.os }}-${{ hashFiles('web/package-lock.json') }}-${{ hashFiles('web/src/**') }}
          restore-keys: |
            vite-${{ runner.os }}-${{ hashFiles('web/package-lock.json') }}-
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Treating cache as storage for build results needed by later jobs.
✅ Correct: Caches can be evicted anytime. Use artifacts for job-to-job data.

❌ Mistake 2: Caching secrets or `.env` files. Caches are readable by workflows on the same repo (and by PRs from the same repo).
✅ Correct: Cache only public, reproducible stuff.

❌ Mistake 3: Using a constant key like `npm-cache`, so the cache never updates (keys are immutable).
✅ Correct: Include a hash of the lockfile in the key.

❌ Mistake 4: Caching `node_modules` across Node versions or OS and getting native module errors.
✅ Correct: Cache `~/.npm` and run `npm ci`, or include `node-version` and `runner.os` in the key.

❌ Mistake 5: Expecting the cache to be saved when the job fails.
✅ Correct: Default save happens only on success; use `actions/cache/save` with `if: always()` when you want it.

---

## 🧠 Tricky Interview Question
Your cache step shows "Cache restored from key" but the build is still slow, and a teammate says the cache "is poisoned" after a bad dependency got cached. How do you reason about and fix it?

Answer: A hit only means the archive was restored, not that it is correct. Since keys are immutable, a bad cache stays until it expires or the key changes. Fix by bumping a manual version prefix in the key (`v2-npm-...`), deleting the cache via the Actions UI or `gh cache delete`, and by using `npm ci` (which verifies against the lockfile) instead of trusting cached `node_modules`. Security-wise, restrict who can write caches: caches from PRs of forks are isolated, and a branch can read caches from its base branch and default branch only.

---

## ⚫ Interview Questions + Answers

Q1: Cache vs artifact?
A1: Cache = speed optimization across runs, best-effort, may disappear. Artifact = deliberate output of a run, stored for download or later jobs, guaranteed for its retention period.

Q2: What are the cache size limits and eviction rules?
A2: 10 GB per repository by default; caches not accessed for 7 days are removed; when the limit is exceeded, least recently used are evicted. (Limits can differ per plan or settings; verify in current docs.)

Q3: Which caches can a branch read?
A3: Its own branch, its base branch (for PRs), and the default branch. Sibling feature branches cannot read each other's caches. So warm the cache on `main`.

Q4: Why `npm ci` plus cache of `~/.npm` instead of caching `node_modules`?
A4: `npm ci` deletes `node_modules` anyway and guarantees lockfile accuracy; the cache just avoids downloads.

Q5: How do you speed up Docker builds with Actions cache?
A5: Use buildx with `cache-from: type=gha` and `cache-to: type=gha,mode=max` so layers are reused across runs.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Dependency installs or compiles take significant time.
- Inputs are deterministic (lockfile hash defines the content).
- Docker layers rarely change.

❌ Avoid when:
- Data must be exactly the same across jobs (use artifacts).
- Content is secret or user specific.
- Cache restore time is greater than rebuild time (tiny projects).

---

## 📊 Visual Diagram
```
 Push -> Runner (empty)
            |
            v
   compute key: npm-Linux-<hash(lock)>
            |
     +------+-------+
     |              |
  exact hit?     no hit
     |              |
  restore       try restore-keys (npm-Linux-)
     |              |
     +------+-------+
            v
        npm ci / pip install
            |
       job succeeded?
        yes |        no -> nothing saved
            v
   save under key (only if not exact hit)
            v
   GitHub cache store (10 GB / repo, 7-day idle eviction)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Cache | Reusable files saved between runs | Runs के बीच दोबारा काम आने वाली files |
| Key | Unique id of a cache entry | Cache की पहचान |
| Hit / Miss | Found / not found | मिला / नहीं मिला |
| Eviction | Automatic deletion of old caches | पुराने cache का अपने आप हटना |
| `hashFiles()` | Hash of files for the key | Files का hash |
| BuildKit cache | Docker layer cache backend | Docker layers का cache |

---

## ⚡ 3-Line Summary
English: Caching reuses slow-to-fetch files (npm, pip, Docker layers) between workflow runs.
English: Key = lockfile hash; keys are immutable, and caches are best-effort, never a source of truth.
English: Use `setup-*` built-in cache for simple cases and `actions/cache` for custom paths.
Hindi: Caching धीमी-से-मिलने वाली files (npm, pip, Docker layers) को runs के बीच दोबारा इस्तेमाल करती है।
Hindi: Key = lockfile का hash; key बदलती नहीं, और cache सिर्फ़ best-effort है, भरोसे का स्रोत नहीं।
Hindi: सरल मामलों में `setup-*` का built-in cache, custom paths के लिए `actions/cache`।

---

## ➡️ Next Topic
**286. actions/cache** — the Action behind all this: inputs, outputs (`cache-hit`), save/restore split.
