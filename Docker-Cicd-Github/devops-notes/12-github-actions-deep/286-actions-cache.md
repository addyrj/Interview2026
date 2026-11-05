# 286. actions/cache
# हिंदी में: actions/cache (विस्तार से)

---

## 🔵 Simple Definition (English)
`actions/cache` is the official Action that restores a cache at its step and automatically saves it in a post-job step. Inputs: `path` (files/dirs, multi-line), `key` (exact id), `restore-keys` (fallback prefixes), `enableCrossOsArchive`, `fail-on-cache-miss`, `lookup-only`. Output: `cache-hit` (`'true'` only for an exact key match). It also ships two sub-actions: `actions/cache/restore` and `actions/cache/save`.

## 🔵 सरल परिभाषा (Hindi)
`actions/cache` official Action है जो अपने step पर cache restore करती है और job के अंत में post step में अपने आप save करती है। Inputs: `path` (files/dirs, multi-line), `key` (exact id), `restore-keys` (fallback prefixes), `enableCrossOsArchive`, `fail-on-cache-miss`, `lookup-only`। Output: `cache-hit` (सिर्फ़ exact key मिलने पर `'true'`)। इसके दो sub-actions भी हैं: `actions/cache/restore` और `actions/cache/save`।

---

## 🔴 Problem it Solves
Built-in caching in `setup-node` covers only package manager downloads. Real pipelines also need to cache Gradle/Maven, Cargo targets, `.next/cache`, Playwright browsers, Terraform providers or ML model files. `actions/cache` is the generic tool for any path, with full control of key design and the ability to separate save from restore.

## 🔴 यह क्यों बना? (Hindi)
`setup-node` का built-in caching सिर्फ़ package manager downloads को cover करता है। असली pipelines को Gradle/Maven, Cargo targets, `.next/cache`, Playwright browsers, Terraform providers या ML model files भी cache करने होते हैं। `actions/cache` किसी भी path के लिए generic tool है, जिसमें key design पर पूरा control और save/restore को अलग करने की सुविधा है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Main step: evaluate "key" and "restore-keys"
Step 2 → Service lookup order: exact key -> each restore-key prefix (most recent match)
Step 3 → Found: download tar (zstd/gzip), extract to "path"; sets outputs
         cache-hit = true only if exact key matched
Step 4 → Not found: step succeeds anyway (unless fail-on-cache-miss: true)
Step 5 → Later steps run (build, test)
Step 6 → Post step (end of job): if job succeeded AND cache-hit != true,
         tar the "path" and upload under "key"
Step 7 → Save fails harmlessly if another job already saved that key
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Main step "key" और "restore-keys" evaluate करता है
Step 2 → खोज का क्रम: exact key -> हर restore-key prefix (सबसे हाल का match)
Step 3 → मिला: tar (zstd/gzip) download होकर "path" में extract; outputs set
         cache-hit = true सिर्फ़ exact key match पर
Step 4 → नहीं मिला: step फिर भी सफल (जब तक fail-on-cache-miss: true न हो)
Step 5 → बाद के steps चलते हैं (build, test)
Step 6 → Post step (job के अंत में): job सफल हो और cache-hit != true हो तो
         "path" को tar करके "key" के नाम से upload
Step 7 → अगर कोई और job वही key save कर चुका हो तो save चुपचाप fail हो जाता है
```

---

## 🟡 Real World Example
An e-commerce team runs Playwright end-to-end tests. Downloading Chromium/Firefox/WebKit took 90 seconds every run. They cached `~/.cache/ms-playwright` with a key containing the Playwright version from `package-lock.json`, and ran `playwright install` only when `cache-hit != 'true'`. The step went from 90 s to 5 s, and the same trick works for Terraform providers on an AWS infra repo.

## 🟡 Real Example Hindi mein
एक e-commerce team Playwright end-to-end tests चलाती है। हर run में Chromium/Firefox/WebKit download में 90 सेकंड लगते थे। उन्होंने `~/.cache/ms-playwright` को ऐसी key से cache किया जिसमें `package-lock.json` से Playwright version का hash था, और `playwright install` सिर्फ़ तब चलाया जब `cache-hit != 'true'`। Step 90 s से 5 s हो गया। यही तरीका AWS infra repo में Terraform providers के लिए भी चलता है।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/cache-basic.yml
name: cache-basic                         # workflow name
on: [push]                                # run on each push
jobs:
  build:
    runs-on: ubuntu-latest                # fresh runner
    steps:
      - uses: actions/checkout@v4         # get code
      - name: Cache pip packages          # human-readable step name
        id: pipcache                      # id lets us read outputs later
        uses: actions/cache@v4            # example version
        with:
          path: ~/.cache/pip              # directory to save/restore
          key: pip-${{ runner.os }}-${{ hashFiles('requirements.txt') }}   # exact key
      - run: echo "hit=${{ steps.pipcache.outputs.cache-hit }}"   # print true/empty
      - run: pip install -r requirements.txt   # quick when cache is warm
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/e2e.yml
# Separate restore/save, conditional install, cache on failure too
name: e2e                                 # workflow name
on:
  pull_request:                           # test every PR
permissions:
  contents: read                          # least privilege
jobs:
  e2e:
    runs-on: ubuntu-latest
    timeout-minutes: 20                   # never hang forever
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm                      # package downloads cache
      - run: npm ci                       # install exact deps
      - name: Restore Playwright browsers
        id: pw                            # needed for outputs
        uses: actions/cache/restore@v4    # restore only (no automatic post-save)
        with:
          path: ~/.cache/ms-playwright    # browsers location on Linux
          key: pw-${{ runner.os }}-${{ hashFiles('package-lock.json') }}   # bump when lock changes
      - name: Install browsers if missing
        if: steps.pw.outputs.cache-hit != 'true'   # only on miss
        run: npx playwright install --with-deps chromium   # download browser + OS libs
      - name: Install OS deps only (cache hit)
        if: steps.pw.outputs.cache-hit == 'true'   # browsers cached, libs are not
        run: npx playwright install-deps chromium  # system libraries
      - name: Save browsers right away    # save before tests so a failing test still saves
        if: steps.pw.outputs.cache-hit != 'true'
        uses: actions/cache/save@v4
        with:
          path: ~/.cache/ms-playwright    # same path as restore
          key: ${{ steps.pw.outputs.cache-primary-key }}   # exact key computed by restore step
      - run: npm run test:e2e             # run Playwright tests
      - name: Check cache existence only
        uses: actions/cache/restore@v4
        with:
          path: ~/.npm
          key: npm-${{ runner.os }}-${{ hashFiles('package-lock.json') }}
          fail-on-cache-miss: false       # set true when a cache MUST exist (e.g. offline builds)
          lookup-only: true               # only check existence, do not download
```

---

## 🟠 My Stack Integration
- **React build**: cache `.vite`/`.next/cache` with key = lockfile hash + source hash and restore-keys fallback.
- **FastAPI**: cache `~/.cache/pip` or `.venv` keyed on `requirements.txt` and Python version.
- **Terraform/AWS**: cache `.terraform` providers (`~/.terraform.d/plugin-cache`).
- **Docker**: prefer `type=gha` BuildKit cache over caching `/var/lib/docker`.
- **VPS deploy**: never read cache in the deploy step; deploy from artifacts or registry images.

```yaml
# Snippet: cache Python venv for FastAPI keyed on version + deps
      - uses: actions/cache@v4
        with:
          path: api/.venv                 # virtualenv folder
          key: venv-${{ runner.os }}-py3.12-${{ hashFiles('api/requirements.txt') }}   # python version in key
      - run: test -d api/.venv || python -m venv api/.venv   # create when missing
      - run: api/.venv/bin/pip install -r api/requirements.txt   # no-op when warm
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Assuming `cache-hit` is true on a restore-key (partial) match.
✅ Correct: `cache-hit` is `'true'` only on exact match; partial match gives `'false'` and the save happens with the new key.

❌ Mistake 2: Comparing with `== true` (boolean). Outputs are strings.
✅ Correct: Use `== 'true'` or `!= 'true'`.

❌ Mistake 3: Caching paths outside the runner's writable areas or using absolute paths from another OS.
✅ Correct: Use `~`, `${{ github.workspace }}` and per-OS keys (or `enableCrossOsArchive` deliberately).

❌ Mistake 4: Using one big cache for everything, so a tiny change re-uploads 2 GB.
✅ Correct: Several small caches with separate keys.

❌ Mistake 5: Using `actions/cache@v2/v3` after the cache service backend change (old versions were retired).
✅ Correct: Use a currently supported major version (v4 at the time of writing; check the Action's README).

---

## 🧠 Tricky Interview Question
The tests fail at step 10, so the job fails. The cache step was early and the cache was a miss. Next run is again a miss. Why, and how do you fix it?

Answer: The implicit post-save step only runs when the job succeeds, so a failing job never saves the cache, and every retry starts cold. Fix: split into `actions/cache/restore` plus `actions/cache/save` with `if: always()` (or right after the install step, as in the advanced example). Be careful to save only trustworthy content, because saving after failure may cache broken partial state; saving right after a successful install step is the safest.

---

## ⚫ Interview Questions + Answers

Q1: What is `cache-hit` exactly?
A1: A string output, `'true'` when the exact `key` matched, `'false'` on restore-key match, empty if none.

Q2: Why split restore and save?
A2: To control when saving happens (e.g. on failure, only on main) and to avoid saving from PR jobs. Also lets separate jobs restore without ever saving.

Q3: How does `hashFiles()` behave?
A3: It hashes the content of matching files (glob relative to workspace) with SHA-256; returns empty string if nothing matches, which then produces a weak key; always verify the glob matches.

Q4: Can two jobs write the same key?
A4: First one wins; later saves emit a warning because cache entries are immutable.

Q5: Security of caches?
A5: Caches are scoped by branch; fork PRs cannot write to the base repo cache. Still, a compromised workflow on a branch can poison its own scope, so don't cache executables you later run with high privileges on the default branch.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Dependencies, toolchains or build caches are expensive to recreate.
- You want fine control (conditional install, separate save).
- Working with languages that have no built-in cache in `setup-*`.

❌ Avoid when:
- You need guaranteed files in later jobs (use artifacts).
- Cache would hold secrets.
- Restore + extract time exceeds rebuild time.

---

## 📊 Visual Diagram
```
 actions/cache@v4 (one step, two phases)
 +-----------------------------------------------+
 | MAIN phase (at the step)                      |
 |   key exact? ---yes--> restore, cache-hit=true|
 |      | no                                     |
 |   restore-keys prefix? --yes--> restore       |
 |      | no            cache-hit=false          |
 |   nothing restored                            |
 +-----------------------+-----------------------+
                         v
              ... your build/test steps ...
                         v
 +-----------------------------------------------+
 | POST phase (end of job)                       |
 |   job success AND cache-hit != true ?         |
 |      yes -> tar path -> upload as <key>       |
 +-----------------------------------------------+
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `path` | What to cache | क्या cache करना है |
| `key` | Exact cache id | Exact cache id |
| `restore-keys` | Prefix fallbacks | Fallback prefixes |
| `cache-hit` | Exact match flag | Exact match का flag |
| `cache/restore` | Restore-only action | सिर्फ़ restore वाली action |
| `cache/save` | Save-only action | सिर्फ़ save वाली action |

---

## ⚡ 3-Line Summary
English: `actions/cache` restores at the step and saves in a post step only on success and non-exact-hit.
English: `cache-hit` is a string and true only for exact key matches.
English: Use restore/save sub-actions for fine control, e.g. saving even when tests fail.
Hindi: `actions/cache` step पर restore और job सफल व non-exact-hit होने पर post step में save करती है।
Hindi: `cache-hit` string है और सिर्फ़ exact key match पर true होता है।
Hindi: बारीक control (जैसे tests fail हों तब भी save) के लिए restore/save sub-actions इस्तेमाल करें।

---

## ➡️ Next Topic
**287. Cache Key Strategy** — how to design keys so caches are fresh, shared and safe.
