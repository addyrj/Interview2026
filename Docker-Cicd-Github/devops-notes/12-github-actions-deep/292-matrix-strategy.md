# 292. Matrix Strategy
# हिंदी में: Matrix Strategy (एक job, कई combinations)

---

## 🔵 Simple Definition (English)
`jobs.<job_id>.strategy.matrix` defines variables (for example `node: [18, 20, 22]` and `os: [ubuntu-latest, windows-latest]`). GitHub creates one job run for every combination and exposes the values as `${{ matrix.node }}`, `${{ matrix.os }}`. Related keys: `include` (add/extend combinations), `exclude` (remove), `fail-fast` (cancel the rest on first failure, default true), `max-parallel` (limit concurrency). A matrix can create at most 256 jobs per workflow run.

## 🔵 सरल परिभाषा (Hindi)
`jobs.<job_id>.strategy.matrix` variables तय करता है (जैसे `node: [18, 20, 22]` और `os: [ubuntu-latest, windows-latest]`)। GitHub हर combination के लिए एक job run बनाता है और values को `${{ matrix.node }}`, `${{ matrix.os }}` की तरह देता है। संबंधित keys: `include` (combinations जोड़ना/बढ़ाना), `exclude` (हटाना), `fail-fast` (पहली failure पर बाकी रोकना, default true), `max-parallel` (एक साथ चलने की सीमा)। एक workflow run में matrix अधिकतम 256 jobs बना सकता है।

---

## 🔴 Problem it Solves
Libraries and services must work on several Node/Python versions and OSes. Copy-pasting one job per version creates huge, inconsistent YAML where one copy gets updated and others are forgotten. Matrix keeps one definition, runs variations in parallel, and shows exactly which version broke.

## 🔴 यह क्यों बना? (Hindi)
Libraries और services को कई Node/Python versions और OS पर चलना होता है। हर version के लिए job copy-paste करने से बड़ा, असंगत YAML बनता है जहाँ एक copy update होती है और बाकी भूल जाती हैं। Matrix एक ही definition रखता है, variations parallel चलाता है, और साफ़ दिखाता है कि कौन सा version टूटा।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define axes:   matrix: { node: [18,20,22], os: [ubuntu-latest, windows-latest] }
Step 2 → GitHub computes the cartesian product: 3 x 2 = 6 jobs
Step 3 → exclude removes listed combinations; include adds or extends
Step 4 → Each job gets its own runner, with matrix.* values filled in
Step 5 → Jobs run in parallel (limited by plan concurrency and max-parallel)
Step 6 → fail-fast: true => first failure cancels in-progress/queued siblings
         fail-fast: false => all combinations finish, you see the full picture
Step 7 → Job names become  "test (20, ubuntu-latest)"; a required status check must
         match these names (or use a final aggregator job)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Axes तय करें:  matrix: { node: [18,20,22], os: [ubuntu-latest, windows-latest] }
Step 2 → GitHub cartesian product निकालता है: 3 x 2 = 6 jobs
Step 3 → exclude लिखी combinations हटाता है; include जोड़ता या बढ़ाता है
Step 4 → हर job को अपना runner मिलता है, matrix.* values भरी हुई
Step 5 → Jobs parallel चलते हैं (plan concurrency और max-parallel की सीमा में)
Step 6 → fail-fast: true => पहली failure पर बाकी in-progress/queued रद्द
         fail-fast: false => सारी combinations पूरी होती हैं, पूरी तस्वीर दिखती है
Step 7 → Job नाम बनता है  "test (20, ubuntu-latest)"; required status check को ये नाम
         match करने होंगे (या अंत में एक aggregator job रखें)
```

---

## 🟡 Real World Example
An open-source Express middleware must support Node 18, 20 and 22 on Linux, and Node 20 on Windows (some path bugs only show on Windows). The matrix has 3 Linux entries plus an `include` for Windows. When Node 22 breaks due to a deprecation, only `test (22, ubuntu-latest)` goes red, and the maintainers fix it without guessing. In your own company, the same trick tests a FastAPI service on Python 3.11 and 3.12 before upgrading production.

## 🟡 Real Example Hindi mein
एक open-source Express middleware को Linux पर Node 18, 20, 22 और Windows पर Node 20 सपोर्ट करना है (कुछ path bugs सिर्फ़ Windows पर दिखते हैं)। Matrix में 3 Linux entries और Windows के लिए एक `include` है। Node 22 में deprecation से टूटे तो सिर्फ़ `test (22, ubuntu-latest)` लाल होता है और maintainers अंदाज़ा लगाए बिना ठीक करते हैं। आपकी कंपनी में भी यही तरीका production upgrade से पहले FastAPI service को Python 3.11 और 3.12 पर test करता है।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/matrix-basic.yml
name: matrix-basic                        # workflow name
on: [push, pull_request]                  # trigger
jobs:
  test:
    runs-on: ubuntu-latest                # same OS for every combination
    strategy:
      matrix:
        node: [18, 20, 22]                # three versions => three jobs
    steps:
      - uses: actions/checkout@v4         # get code
      - uses: actions/setup-node@v4       # install requested Node
        with:
          node-version: ${{ matrix.node }}   # value from the matrix
          cache: npm                      # npm cache
      - run: npm ci                       # install dependencies
      - run: npm test                     # run tests on this version
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/matrix-advanced.yml
# OS x Node matrix with exclude/include, fail-fast off, max-parallel, experimental job
name: matrix-advanced                     # workflow name
on:
  pull_request:
  push:
    branches: [main]
permissions:
  contents: read                          # least privilege
jobs:
  test:
    name: test (node ${{ matrix.node }}, ${{ matrix.os }})   # readable job name
    runs-on: ${{ matrix.os }}             # runner comes from the matrix
    timeout-minutes: 15                   # avoid hanging jobs
    continue-on-error: ${{ matrix.experimental == true }}    # allow failure only for experimental
    strategy:
      fail-fast: false                    # let every combination finish
      max-parallel: 4                     # do not hog all runners
      matrix:
        os: [ubuntu-latest, windows-latest]   # axis 1
        node: [18, 20, 22]                    # axis 2
        experimental: [false]                 # default flag for every combination
        exclude:
          - os: windows-latest            # skip Windows for old Node
            node: 18
        include:
          - os: ubuntu-latest             # extra combination (not in product)
            node: 23
            experimental: true            # allowed to fail
          - os: ubuntu-latest             # add extra variable to an existing combo
            node: 20
            coverage: true                # only this job uploads coverage
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}
          cache: npm
      - run: npm ci
      - run: npm test -- --ci
      - name: Upload coverage (one job only)
        if: matrix.coverage == true       # only the include entry with coverage: true
        uses: actions/upload-artifact@v4
        with:
          name: coverage-${{ matrix.os }}-${{ matrix.node }}   # unique artifact name per job
          path: coverage/
  all-green:                              # single required check for branch protection
    if: always()                          # run even if matrix jobs failed
    needs: test                           # wait for the whole matrix
    runs-on: ubuntu-latest
    steps:
      - run: |
          if [ "${{ needs.test.result }}" != "success" ]; then
            echo "matrix failed: ${{ needs.test.result }}"; exit 1
          fi
```

---

## 🟠 My Stack Integration
- **Node.js API**: `node: [20, 22]` before moving production from 20 to 22.
- **FastAPI**: `python: ['3.11','3.12']` with `setup-python`, plus `db: [postgres:15, postgres:16]` service containers.
- **React**: `browser: [chromium, firefox, webkit]` Playwright shards.
- **Docker multi-arch**: `platform: [linux/amd64, linux/arm64]` for ECR images (Graviton).
- **Services monorepo**: matrix over `service: [web, api, fastapi]` to build all images.

```yaml
# Snippet: FastAPI on two Python versions with a Postgres service
  api-tests:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python: ['3.11', '3.12']          # quote: 3.10 would become 3.1 as a number!
    services:
      db:
        image: postgres:16                # example tag
        env:
          POSTGRES_PASSWORD: ci_only_password   # throwaway CI secret, not a real one
        ports: ['5432:5432']
        options: --health-cmd "pg_isready" --health-interval 5s --health-retries 10
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python }}
      - run: pip install -r api/requirements.txt && pytest api
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Writing `python: [3.9, 3.10]`. YAML parses `3.10` as the number 3.1.
✅ Correct: Quote versions: `['3.9', '3.10']`.

❌ Mistake 2: Leaving `fail-fast: true` when you need a complete compatibility report.
✅ Correct: `fail-fast: false` for compatibility matrices; keep true for cheap fast feedback.

❌ Mistake 3: Making a matrix job name the required status check. Names change with the matrix.
✅ Correct: Use an aggregator job (`all-green`) with `if: always()` and `needs`.

❌ Mistake 4: Same artifact name in each job (v4 errors on duplicates).
✅ Correct: Add matrix values into the name.

❌ Mistake 5: Exploding the matrix (5 x 5 x 5 = 125 jobs) and burning minutes.
✅ Correct: Test the edges (min and max versions), use `exclude` and `max-parallel`.

---

## 🧠 Tricky Interview Question
Your matrix is `node: [18, 20]` and you add `include: - node: 22`. Another time you add `include: - os: windows-latest` with no other keys. What happens in each case?

Answer: Case 1: `node: 22` does not match any existing combination on all original keys, so it becomes a new, separate job (22). Case 2: `include` entries first try to attach to existing combinations: if adding the keys would not overwrite an original matrix value, they are added to every matching combo. Here `os` is a new key not present in original matrix, so `os: windows-latest` is added to all existing combinations (it does not create a new job). To get an extra Windows job, you must also specify `node:` in that include entry (with a value not in the original matrix or combined to create a distinct entry). Include never overwrites original matrix values but may overwrite values added by earlier includes.

---

## ⚫ Interview Questions + Answers

Q1: What does `fail-fast` do?
A1: When true (default), a failing job cancels other running or queued matrix jobs. False lets all finish.

Q2: How many jobs can a matrix make?
A2: Up to 256 per workflow run.

Q3: How to create a dynamic matrix?
A3: Compute a JSON string in an earlier job and use `matrix: ${{ fromJSON(needs.plan.outputs.matrix) }}`.

Q4: How do I run a job only once, not per matrix entry?
A4: Put it in a separate job outside the matrix, with `needs`, or condition with `if: matrix.coverage`.

Q5: Where is a matrix value usable?
A5: In `runs-on`, `name`, `steps`, `env`, `if`, `container`, and `services` via the `matrix` context.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Supporting multiple versions, OSes, architectures or databases.
- Building many services/images from one template.
- Sharding long test suites.

❌ Avoid when:
- Only one environment matters (production runs one version).
- Jobs are expensive and do not benefit from variety.
- Deploy steps, which should run once, not per matrix entry.

---

## 📊 Visual Diagram
```
 matrix: os=[ubuntu, windows]  x  node=[18,20,22]
                         |
          cartesian product (6)  -- exclude (win,18) --> 5
                         |
      + include (ubuntu, 23, experimental)       --> 6
                         |
   +------------+------------+------------+------------+------------+-----------+
   | ubu/18     | ubu/20     | ubu/22     | win/20     | win/22     | ubu/23*   |
   +------------+------------+------------+------------+------------+-----------+
        parallel runners (max-parallel: 4)        * continue-on-error
                         |
                    needs: test
                         v
                  [ all-green job ]  <- required status check
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Matrix | Variable combinations | Variables के combinations |
| `include` | Add/extend entries | Entries जोड़ना/बढ़ाना |
| `exclude` | Remove entries | Entries हटाना |
| `fail-fast` | Cancel siblings on failure | Failure पर बाकी रोकना |
| `max-parallel` | Concurrency cap | एक साथ चलने की सीमा |
| Aggregator job | Single job summarizing matrix | Matrix का सार देने वाला job |

---

## ⚡ 3-Line Summary
English: A matrix runs one job definition across many combinations in parallel.
English: Use include/exclude, quote versions, and set fail-fast false for compatibility reports.
English: Use an aggregator job for branch protection and keep the matrix small.
Hindi: Matrix एक job definition को कई combinations पर parallel चलाता है।
Hindi: include/exclude इस्तेमाल करें, versions को quote करें, और compatibility report के लिए fail-fast false रखें।
Hindi: Branch protection के लिए aggregator job रखें और matrix छोटा रखें।

---

## ➡️ Next Topic
**293. Matrix Build** — a practical build matrix for multi-service Docker images and multi-arch.
