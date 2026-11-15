---

# 447. CI/CD with GitHub Actions
# हिंदी में: GitHub Actions के साथ CI/CD (automatic test और deploy)

---

## 🔵 Simple Definition (English)
CI (Continuous Integration) means every push is automatically linted and tested. CD (Continuous Delivery/Deployment) means a green build is automatically shipped to a server. GitHub Actions runs these steps from a YAML file in `.github/workflows/`.

## 🔵 सरल परिभाषा (Hindi)
CI (Continuous Integration) का मतलब है हर push पर lint और test अपने-आप चलना। CD (Continuous Delivery/Deployment) का मतलब है test पास होने पर code अपने-आप server पर पहुँच जाना। GitHub Actions यह सब `.github/workflows/` की YAML file से चलाता है।

---

## 🔴 Problem it Solves
Manual deploys ("works on my machine", forgotten tests, SSH-ing into the server and running `git pull`) cause outages and nobody knows which commit is live. A pipeline makes every change go through the same tested, repeatable path, and a failing test blocks the merge.

## 🔴 यह क्यों बना? (Hindi)
Manual deploy में "मेरी machine पर तो चल रहा है", test भूल जाना और server पर SSH करके `git pull` चलाना आम था। इससे outage होते थे और पता नहीं चलता था कि कौन-सा commit live है। Pipeline हर बदलाव को एक ही tested और repeatable रास्ते से भेजती है, और test fail हो तो merge रुक जाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Developer pushes a commit or opens a Pull Request
Step 2 → GitHub reads .github/workflows/*.yml and matches the `on:` trigger
Step 3 → A fresh runner VM (ubuntu-latest) starts for each job
Step 4 → Steps run in order: checkout -> setup-python -> install -> lint -> test
Step 5 → `matrix` repeats the job for every Python version (3.12, 3.13)
Step 6 → If every step passes, the `deploy` job (needs: test) runs on main only
Step 7 → Secrets are injected as env vars; the job SSHes to the server and runs deploy.sh
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Developer commit push करता है या Pull Request खोलता है
Step 2 → GitHub workflow YAML पढ़कर `on:` trigger match करता है
Step 3 → हर job के लिए नई runner VM (ubuntu-latest) शुरू होती है
Step 4 → Steps क्रम से चलते हैं: checkout -> python setup -> install -> lint -> test
Step 5 → `matrix` हर Python version (3.12, 3.13) पर job दोहराता है
Step 6 → सब पास हो तो `deploy` job (needs: test) सिर्फ main branch पर चलती है
Step 7 → Secrets env variables बनकर आते हैं; job server पर SSH करके deploy.sh चलाती है
```

---

## 🟡 Real World Example
A Razorpay-style payments API lives in a GitHub repo. Every pull request runs ruff, mypy and pytest on Python 3.12 and 3.13. When the PR is merged to `main`, a `deploy` job builds the app and SSHes to the VPS to restart gunicorn. If one test fails, the merge button stays blocked through branch protection.

## 🟡 Real Example Hindi mein
Razorpay जैसी payments API GitHub repo में है। हर pull request पर ruff, mypy और pytest, Python 3.12 और 3.13 पर चलते हैं। PR `main` में merge होते ही `deploy` job VPS पर SSH करके gunicorn restart करती है। एक भी test fail हो तो branch protection की वजह से merge button बंद रहता है।

---

## 💻 Code Example — Basic
```python
# Basic: the code CI will test. File: app/calc.py + tests/test_calc.py
# (Run locally exactly as CI does:  pytest -q)

def add(a: int, b: int) -> int:  # tiny function CI can test
    """Return the sum of two integers."""  # docstring
    return a + b  # the logic


def test_add() -> None:  # pytest finds functions named test_*
    assert add(2, 3) == 5  # a failing assert makes the CI job red


def test_add_negative() -> None:  # second case
    assert add(-1, 1) == 0  # edge case with a negative number


if __name__ == "__main__":  # allow running without pytest too
    test_add()  # run test 1
    test_add_negative()  # run test 2
    print("2 tests passed")  # Output: 2 tests passed
```

Minimal workflow, `.github/workflows/ci.yml`:
```yaml
name: CI                         # name shown in the Actions tab
on: [push, pull_request]         # run on every push and every PR
jobs:
  test:                          # job id
    runs-on: ubuntu-latest       # fresh Linux VM
    steps:
      - uses: actions/checkout@v4          # download the repo code
      - uses: actions/setup-python@v5      # install Python
        with:
          python-version: "3.13"           # which version
      - run: pip install -r requirements.txt pytest   # install dependencies
      - run: pytest -q                     # a non-zero exit code fails the job
```

## 💻 Code Example — Advanced
```yaml
# Production workflow: matrix, cache, lint, types, coverage, gated deploy
name: CI
on:
  push:
    branches: [main]             # only main on push
  pull_request:                  # and every PR
concurrency:
  group: ci-${{ github.ref }}    # one run per branch at a time
  cancel-in-progress: true       # cancel the older run when new commit arrives
permissions:
  contents: read                 # least privilege for GITHUB_TOKEN
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false           # let both versions finish
      matrix:
        python-version: ["3.12", "3.13"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip             # cache ~/.cache/pip keyed on requirements
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: ruff check .        # lint
      - run: mypy app            # static types
      - run: pytest --cov=app --cov-fail-under=80   # fail below 80% coverage
  deploy:
    needs: test                  # run only if `test` is green
    if: github.ref == 'refs/heads/main'   # never deploy from a PR
    runs-on: ubuntu-latest
    environment: production      # lets you require manual approval
    steps:
      - uses: actions/checkout@v4
      - name: Deploy over SSH
        env:
          SSH_KEY: ${{ secrets.VPS_SSH_KEY }}   # secret, masked in logs
        run: |
          echo "$SSH_KEY" > key && chmod 600 key
          ssh -i key -o StrictHostKeyChecking=accept-new deploy@${{ vars.VPS_HOST }} "cd /srv/app && ./deploy.sh"
```

Verification note: this YAML was parsed with PyYAML (valid, jobs `test` and `deploy`, matrix `["3.12","3.13"]`) but it was **not run on GitHub**, because a real runner and secrets are needed. `app/calc.py` style tests were run locally with pytest-style asserts.

---

## 🟠 JavaScript vs Python Comparison
The pipeline idea is identical; only the setup action and package commands differ.

```python
# Python project steps in a workflow
# - uses: actions/setup-python@v5
# - run: pip install -r requirements.txt
# - run: pytest
# - run: ruff check .
```
```javascript
// Node project steps in a workflow
// - uses: actions/setup-node@v4
// - run: npm ci
// - run: npm test
// - run: npx eslint .
```

Key differences: Python uses `setup-python` + `pip`/`uv`, Node uses `setup-node` + `npm ci`. Python needs a matrix over interpreter versions more often because 3.12 and 3.13 differ in small behaviours. In both worlds `needs:` and `if:` gate the deploy job.

---

## 🟠 FastAPI Connection
A FastAPI service tests with `TestClient` inside CI, so no server is needed. CI should also hit `/health/ready` after deploy as a smoke test.

```python
# tests/test_api.py - runs in CI (pip install fastapi httpx pytest)
from fastapi import FastAPI  # framework
from fastapi.testclient import TestClient  # in-process HTTP client

app: FastAPI = FastAPI()  # app under test


@app.get("/ping")  # simple endpoint
def ping() -> dict[str, str]:  # typed response
    return {"msg": "pong"}  # JSON body


def test_ping() -> None:  # pytest test
    client: TestClient = TestClient(app)  # no network needed
    res = client.get("/ping")  # call the endpoint
    assert res.status_code == 200  # CI fails if this breaks
    assert res.json() == {"msg": "pong"}  # check body
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Hard-coding secrets in the YAML
✅ Correct: store them in Settings > Secrets and read `${{ secrets.NAME }}`.

```yaml
# Wrong
env:
  DB_PASSWORD: "hunter2"
# Right
env:
  DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
```

❌ Mistake 2: Unquoted Python versions
✅ Correct: quote them, because YAML reads `3.10` as the number `3.1`.

```yaml
# Wrong
python-version: [3.9, 3.10]     # 3.10 becomes 3.1 !
# Right
python-version: ["3.9", "3.10"]
```

❌ Mistake 3: Deploy job runs on pull requests or without `needs`
✅ Correct: use `needs: test` and `if: github.ref == 'refs/heads/main'`.

---

## 🧠 Tricky Interview Question

**Q**: A step in your job fails, but the later `deploy` job still ran. Why, and what is the output of this local simulation?

```python
# Simulate `needs` and `if: always()`
def test_job() -> bool:
    return False  # tests failed

def deploy(needs_ok: bool, always: bool = False) -> str:
    return "deployed" if (needs_ok or always) else "skipped"

print(deploy(test_job()))
print(deploy(test_job(), always=True))
```

**Answer**:
```
skipped
deployed
```
By default a job with `needs:` is skipped when the needed job fails. If someone writes `if: always()` (or `if: ${{ !cancelled() }}`) on the deploy job, the implicit success check is removed and it runs anyway. So always use `if: success() && github.ref == ...`-style conditions on deploy jobs.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between CI, Continuous Delivery and Continuous Deployment?
A1: CI = automatically build and test every change. Continuous Delivery = every green build is ready to release, but a human clicks deploy. Continuous Deployment = every green build goes to production automatically.

Q2: What is a `matrix` strategy?
A2: It runs the same job for each combination of values, for example Python 3.12 and 3.13 on ubuntu and windows. It catches version-specific bugs and saves writing the job many times.

Q3: How do you keep secrets safe in Actions?
A3: Use repository or environment secrets, access them as `${{ secrets.X }}`, never echo them, give `GITHUB_TOKEN` minimal `permissions`, and pin third-party actions to a version (or commit SHA). Secrets are masked in logs and are not passed to workflows from forks.

Q4: How do you speed up CI?
A4: Cache dependencies (`cache: pip`), use `concurrency` to cancel stale runs, run lint/type/test in parallel jobs, and use `pytest -n auto` or split tests.

Q5: How do you roll back a bad deploy?
A5: Redeploy the previous tag/commit (a `workflow_dispatch` job taking a version input), or keep the previous Docker image tag and switch to it. Deploy artifacts must be versioned for this to work.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Your code is on GitHub and you want tests on every PR
- You deploy to a VPS, AWS or a container registry repeatedly
- You need a matrix of Python versions

❌ Avoid when:
- The repo is a throwaway script with no tests
- The build needs very large hardware (use self-hosted runners instead)
- Secrets cannot leave an internal network (use self-hosted runners or another CI)

---

## 📊 Visual Diagram

```
 git push / PR
      │
      ▼
 ┌──────────┐   fail   ┌────────────────┐
 │  test    │ ───────► │ PR blocked ❌   │
 │ (matrix) │          └────────────────┘
 └────┬─────┘
      │ pass (needs: test)
      ▼
 ┌──────────┐  SSH   ┌───────────────┐
 │  deploy  │ ─────► │  VPS: restart │ ──► /health/ready smoke test
 │ (main)   │        └───────────────┘
 └──────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Workflow | YAML file defining automation | automation की YAML file |
| Job | Group of steps on one runner | एक runner पर steps का समूह |
| Runner | VM that executes a job | job चलाने वाली VM |
| Matrix | Run job for many values | कई values पर job चलाना |
| Secret | Encrypted variable | छिपा हुआ (encrypted) variable |
| Artifact | File saved from a run | run से बची हुई file |

---

## ⚡ 3-Line Summary
English: GitHub Actions runs lint, tests and deploy from YAML on every push or PR. Use `matrix`, caching, `needs` and secrets for safe, fast pipelines. Deploy only from main after tests pass and smoke-test the health endpoint.
Hindi: GitHub Actions हर push या PR पर YAML से lint, test और deploy चलाता है। Safe और तेज़ pipeline के लिए `matrix`, caching, `needs` और secrets इस्तेमाल करें। Deploy सिर्फ main से, test पास होने के बाद करें और health endpoint से smoke-test करें।

---

## ➡️ Next Topic
**448. Environment Management** — how dev, staging and prod get different settings and secrets without changing code.
