# 305. Setup Python (actions/setup-python)
# हिंदी में: Python Setup करना (actions/setup-python)

---

## 🔵 Simple Definition (English)
`actions/setup-python` installs a specific **Python version** (CPython or PyPy) on the runner, adds `python` and `pip` to PATH, and can **cache** pip, pipenv, or poetry downloads. It is the Python counterpart of `setup-node` and is what you use for FastAPI CI.

## 🔵 सरल परिभाषा (Hindi)
`actions/setup-python` runner पर एक विशेष **Python version** (CPython या PyPy) install करती है, `python` और `pip` को PATH में जोड़ती है, और pip, pipenv या poetry के downloads **cache** कर सकती है। यह `setup-node` का Python वाला साथी है और FastAPI की CI में इसी का इस्तेमाल होता है।

---

## 🔴 Problem it Solves
The runner has a system Python managed by the OS, often with a different minor version than production (3.10 vs your 3.12). Installing packages into the system Python can fail with "externally-managed-environment" errors on recent Ubuntu images. Without caching, installing FastAPI + SQLAlchemy + pandas wheels on each run takes minutes.
`setup-python` gives the exact version, fast installs, and a clean isolated environment when combined with a venv.

## 🔴 यह क्यों बना? (Hindi)
Runner पर OS का system Python होता है, जिसका minor version अक्सर production से अलग होता है (3.10 बनाम आपका 3.12)। नई Ubuntu images पर system Python में packages install करने पर "externally-managed-environment" error आ सकता है। Caching के बिना FastAPI + SQLAlchemy + pandas wheels हर run में install होने में minutes लगते हैं।
`setup-python` सही version, तेज़ installs और venv के साथ साफ़ isolated environment देती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Step reads python-version (e.g. "3.12") or python-version-file
Step 2 → Looks in runner tool cache for matching Python build
Step 3 → If missing, downloads a prebuilt Python from actions/python-versions
Step 4 → Adds python/pip to PATH, sets outputs python-version, cache-hit
Step 5 → If cache: pip, locates requirements*.txt (or poetry.lock/Pipfile.lock)
Step 6 → Restores ~/.cache/pip keyed by OS + Python version + file hash
Step 7 → Your steps create venv, pip install, run ruff/pytest
Step 8 → Post step saves updated pip cache
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Step python-version (जैसे "3.12") या python-version-file पढ़ता है
Step 2 → Runner के tool cache में matching Python build ढूँढता है
Step 3 → न मिले तो actions/python-versions से prebuilt Python download करता है
Step 4 → python/pip को PATH में जोड़ता है, outputs python-version, cache-hit सेट करता है
Step 5 → cache: pip हो तो requirements*.txt (या poetry.lock/Pipfile.lock) ढूँढता है
Step 6 → OS + Python version + file hash के key से ~/.cache/pip restore करता है
Step 7 → आपके steps venv बनाते हैं, pip install करते हैं, ruff/pytest चलाते हैं
Step 8 → Post step अपडेटेड pip cache save करता है
```

---

## 🟡 Real World Example
A fintech runs a FastAPI pricing service on Python 3.12 in Docker. CI uses `python-version: "3.12"` plus pip caching, cutting install time from 90 s to 15 s. They also test against 3.11 and 3.13 in a matrix to prepare for upgrades. A nightly job runs `pip-audit` against `requirements.txt` to catch vulnerable packages.

## 🟡 Real Example Hindi mein
एक fintech की FastAPI pricing service Docker में Python 3.12 पर चलती है। CI `python-version: "3.12"` और pip caching इस्तेमाल करती है, जिससे install समय 90 सेकंड से 15 सेकंड रह गया। Upgrade की तैयारी के लिए वे matrix में 3.11 और 3.13 पर भी test करते हैं। रात का एक job कमज़ोर packages पकड़ने के लिए `requirements.txt` पर `pip-audit` चलाता है।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/python-basic.yml
name: Python Basic                  # workflow name

on: [push, pull_request]            # triggers

jobs:
  test:
    runs-on: ubuntu-latest          # Linux runner
    steps:
      - uses: actions/checkout@v4   # get code
      - uses: actions/setup-python@v5   # install Python
        with:
          python-version: "3.12"    # QUOTE it, else 3.10 becomes 3.1
          cache: pip                # cache pip downloads (needs requirements.txt)
      - run: python --version       # confirm version
      - run: pip install -r requirements.txt   # install dependencies
      - run: pytest -q              # run tests
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/python-advanced.yml
name: Python Advanced

on:
  pull_request:
    paths: ["pricing/**", ".github/workflows/python-advanced.yml"]
  push:
    branches: [main]

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    defaults:
      run:
        working-directory: pricing        # FastAPI service folder
    strategy:
      fail-fast: false
      matrix:
        python: ["3.11", "3.12", "3.13"]   # example versions; update to what you support
    services:
      postgres:                            # real DB for integration tests
        image: postgres:16-alpine
        env:
          POSTGRES_PASSWORD: test          # CI-only throwaway password
          POSTGRES_DB: pricing_test
        ports: ["5432:5432"]
        options: >-
          --health-cmd "pg_isready -U postgres"
          --health-interval 5s
          --health-timeout 5s
          --health-retries 10
    env:
      DATABASE_URL: postgresql://postgres:test@localhost:5432/pricing_test
    steps:
      - uses: actions/checkout@v4
        with:
          persist-credentials: false

      - uses: actions/setup-python@v5
        id: py                              # id to read outputs
        with:
          python-version: ${{ matrix.python }}
          cache: pip
          cache-dependency-path: |          # all files that define dependencies
            pricing/requirements.txt
            pricing/requirements-dev.txt

      - name: Create virtualenv and install
        run: |
          python -m venv .venv              # isolated environment
          . .venv/bin/activate              # activate for this step
          python -m pip install --upgrade pip
          pip install -r requirements.txt -r requirements-dev.txt

      - name: Lint and type check
        run: |
          . .venv/bin/activate
          ruff check .                      # fast linter
          mypy app                          # optional static typing

      - name: Tests with coverage
        run: |
          . .venv/bin/activate
          pytest -q --cov=app --cov-report=xml   # produces coverage.xml

      - name: Report
        run: echo "Python ${{ steps.py.outputs.python-version }} cache-hit=${{ steps.py.outputs.cache-hit }}"

  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version-file: pricing/.python-version   # single source of truth
      - run: pip install pip-audit && pip-audit -r pricing/requirements.txt   # known CVEs
```

---

## 🟠 My Stack Integration
- **FastAPI:** `python-version` equals the Docker base image (`FROM python:3.12-slim`); use `services: postgres/redis` for integration tests.
- **Node.js / React:** separate job with `setup-node`; do not mix both in one job unless a build needs both.
- **Nginx / VPS:** CI builds and tests the FastAPI image; deploy later pulls it on the VPS behind Nginx.
- **AWS:** if you deploy to Lambda, match `python-version` to the Lambda runtime (e.g. `python3.12`).
- Use `poetry`/`uv`? `cache: poetry` requires Poetry installed before `setup-python`; for `uv` use `astral-sh/setup-uv`.

```yaml
# cheap guard that CI Python == Docker Python
      - name: Check Dockerfile matches CI
        run: |
          grep -q "FROM python:${{ matrix.python }}" pricing/Dockerfile || echo "::warning::Dockerfile uses a different Python"
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `python-version: 3.10` unquoted. YAML parses it as float 3.1.
✅ Correct: `python-version: "3.10"`.

❌ Mistake 2: `cache: pip` with no `requirements.txt` in the repo root (monorepo subfolder).
✅ Correct: Set `cache-dependency-path: pricing/requirements.txt`.

❌ Mistake 3: `pip install` into the system Python on Ubuntu 24.04 runners (externally managed).
✅ Correct: With `setup-python` the toolcache Python allows pip, but a `venv` is cleaner and matches production.

❌ Mistake 4: Not pinning dependencies (`fastapi` without versions). CI breaks when a new release lands.
✅ Correct: Pin exact versions in `requirements.txt` (use `pip-compile`/`uv pip compile` with hashes).

❌ Mistake 5: Using a real production `DATABASE_URL` in CI.
✅ Correct: Use a service container with throwaway credentials, never production secrets.

---

## 🧠 Tricky Interview Question
**Q:** Your matrix is `python: [3.9, 3.10, 3.11]` (unquoted). The 3.10 leg of CI fails with "Version 3.1 was not found", or someone "fixes" it by deleting that leg, and then production on 3.10 crashes. What went wrong?

**Answer:** YAML reads unquoted `3.10` as the number 3.1 (trailing zero dropped), so `setup-python` is asked for Python 3.1, which does not exist. The 3.10 interpreter was never tested, so a 3.10-only bug shipped. Always quote Python versions as strings (`"3.10"`), and print `python --version` or `steps.py.outputs.python-version` so the log proves which interpreter ran.

---

## ⚫ Interview Questions + Answers

Q1: Why use a venv in CI if the runner is disposable?
A1: It mirrors production, avoids system-package conflicts, makes commands identical to local development, and makes caching and cleanup explicit.

Q2: What does `cache: pip` cache?
A2: pip's download/wheel cache (`~/.cache/pip`), keyed by OS, Python version and the hash of dependency files. It does not cache the venv itself.

Q3: How do you support Poetry?
A3: Install Poetry (`pipx install poetry`) before `setup-python`, then `cache: poetry`, then `poetry install --no-interaction`.

Q4: How do you run async FastAPI tests?
A4: `pytest` with `pytest-asyncio` or `anyio`, and `httpx.AsyncClient`/`TestClient`. CI needs nothing special beyond installing these dev dependencies.

Q5: How do you read the Python version from a file?
A5: `python-version-file: .python-version` (also supports `pyproject.toml`'s `requires-python` and `.tool-versions`).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any Python/FastAPI/Django CI job
- You need multiple Python versions
- You want pip/poetry caching

❌ Avoid when:
- Everything runs inside a Docker build (the image defines Python)
- You use `container: python:3.12` for the job already
- A tool like `uv` manages Python versions itself and you want one tool

---

## 📊 Visual Diagram
```
 python-version: "3.12" (or .python-version file)
            |
            v
   actions/setup-python@v5
     |-- tool cache has 3.12.x ? -- no --> download prebuilt CPython
     |-- PATH: python, pip -> 3.12.x
     |-- cache: pip
     |     key = pip-Linux-py3.12-<hash(requirements*.txt)>
     v
   python -m venv .venv
   pip install -r requirements.txt
   ruff -> mypy -> pytest --cov  (with postgres service container)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `python-version` | Python version to install | install होने वाला version |
| `venv` | Isolated Python environment | अलग Python environment |
| `pip cache` | Saved wheel downloads | सेव किए गए downloads |
| `requirements.txt` | Pinned dependency list | dependency सूची |
| Service container | DB/Redis container for tests | tests के लिए DB container |
| `pip-audit` | Scanner for vulnerable packages | कमज़ोर packages scanner |
| Wheel | Prebuilt Python package | prebuilt package |

---

## ⚡ 3-Line Summary
English: `setup-python` installs an exact Python version and caches pip downloads.
Quote versions, create a venv, pin dependencies, and match the Docker base image.
Use service containers for databases and a matrix to test several Python versions.
Hindi: `setup-python` सटीक Python version install करती है और pip downloads cache करती है।
Versions को quotes में लिखें, venv बनाएँ, dependencies pin करें और Docker base image से मिलाएँ।
Databases के लिए service containers और कई Python versions के लिए matrix इस्तेमाल करें।

---

## ➡️ Next Topic
**306. Cache Dependencies** — a deeper look at `actions/cache`: keys, restore-keys, scopes and limits.
