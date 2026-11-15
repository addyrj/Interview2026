---

# 288. Coverage.py
# हिंदी में: Coverage.py (tests ने कितना code चलाया)

---

## 🔵 Simple Definition (English)
`coverage.py` is a tool that measures which lines (and branches) of your code were executed while the tests ran. It prints a percentage and lists the lines that no test touched. With `pytest-cov` you get it as one flag: `pytest --cov`.

## 🔵 सरल परिभाषा (Hindi)
`coverage.py` एक tool है जो नापता है कि tests चलने के दौरान आपके code की कौन सी lines (और branches) execute हुईं। यह percentage दिखाता है और वे lines बताता है जिन्हें किसी test ने छुआ ही नहीं। `pytest-cov` के साथ यह एक flag में मिलता है: `pytest --cov`।

---

## 🔴 Problem it Solves
"We have tests" does not tell you what is tested. A team may have 200 tests that all cover the happy path while the refund logic and the error branches have none. Coverage shows the blind spots: untested files, untested `if` branches, dead code. It also gives CI a measurable gate (fail the build below 80%) so coverage does not silently drop as the code grows.

## 🔴 यह क्यों बना? (Hindi)
"हमारे पास tests हैं" यह नहीं बताता कि क्या test हुआ है। हो सकता है 200 tests सिर्फ सही रास्ता cover करें और refund logic व error branches का कोई test न हो। Coverage अंधे हिस्से दिखाता है: बिना test वाली files, बिना test वाले `if` branches, मृत code। CI को एक नापने लायक gate भी मिलता है (80% से नीचे build fail) ताकि code बढ़ने पर coverage चुपचाप न गिरे।

---

## 🟢 How it Works — Step by Step

```
Step 1 → coverage hooks into Python's tracing (sys.monitoring on 3.12+, C tracer before)
Step 2 → You run the tests:  coverage run -m pytest      (or: pytest --cov=mypkg)
Step 3 → It records every (file, line) executed; with branch=True also every jump taken
Step 4 → Data is saved in a .coverage file (SQLite)
Step 5 → Report:  coverage report -m | coverage html | coverage xml | coverage json
Step 6 → Gate:    fail_under = 80  (or --cov-fail-under=80) -> non-zero exit code

Statement coverage: was the line run?   Branch coverage: were BOTH sides of each if/loop taken?
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → coverage Python की tracing में hook करता है (3.12+ में sys.monitoring, पहले C tracer)
Step 2 → आप tests चलाते हैं:  coverage run -m pytest      (या: pytest --cov=mypkg)
Step 3 → यह हर (file, line) जो चली उसे record करता है; branch=True हो तो हर jump भी
Step 4 → Data .coverage file (SQLite) में सेव होता है
Step 5 → Report:  coverage report -m | coverage html | coverage xml | coverage json
Step 6 → Gate:    fail_under = 80  (या --cov-fail-under=80) -> non-zero exit code

Statement coverage: line चली? Branch coverage: हर if/loop के DONO रास्ते चले?
```

---

## 🟡 Real World Example
A Razorpay-like billing module has a `discount()` function. Tests cover "HALF" and "no coupon" but nobody tested the "TEN" coupon or the unused `unused()` helper. The CI report shows `shop.py 81% Missing: 8, 13`, pointing exactly to the untested lines. The team adds a test for the "TEN" coupon, deletes the dead helper, and sets `fail_under = 90` so future pull requests that add untested code are blocked. The HTML report is uploaded as a CI artifact for reviewers.

## 🟡 Real Example Hindi mein
Razorpay जैसे billing module में `discount()` function है। Tests "HALF" और "कोई coupon नहीं" cover करते हैं पर "TEN" coupon या `unused()` helper का test किसी ने नहीं लिखा। CI report दिखाती है `shop.py 81% Missing: 8, 13`, जो बिना test वाली lines की ठीक जगह बताती है। Team "TEN" coupon का test जोड़ती है, मृत helper हटाती है और `fail_under = 90` रखती है ताकि बिना test वाला नया code जोड़ने वाले pull requests रुकें। Reviewers के लिए HTML report CI artifact के रूप में upload होती है।

---

## 💻 Code Example — Basic
```python
# shop.py — code under test
def discount(price: float, code: str | None) -> float:
    """Apply coupon code to price."""
    if price < 0:                                 # line 3
        raise ValueError("negative price")        # line 4
    if code == "HALF":                            # line 5
        return price / 2                          # line 6
    if code == "TEN":                             # line 7
        return price * 0.9                        # line 8  <- no test reaches this
    return price                                  # line 9


def unused() -> str:                              # never called by any test
    return "dead code"                            # line 13


# test_shop.py
import pytest                                     # framework
from shop import discount                         # code under test


def test_half() -> None:
    assert discount(100, "HALF") == 50            # covers the HALF branch


def test_none() -> None:
    assert discount(100, None) == 100             # covers the default return


def test_negative() -> None:
    with pytest.raises(ValueError):               # covers the error branch
        discount(-1, None)

# Commands (coverage 7.17, Python 3.13) and REAL output:
#   coverage run -m pytest -q          ->  3 passed
#   coverage report                    (with branch = True in .coveragerc)
#   Name      Stmts   Miss Branch BrPart  Cover   Missing
#   -----------------------------------------------------
#   shop.py      10      2      6      1    81%   8, 13
#   -----------------------------------------------------
#   TOTAL        10      2      6      1    81%
#
# Meaning: 10 statements, 2 never run (lines 8 and 13), 6 branches, 1 branch only half-taken.
```

## 💻 Code Example — Advanced
```ini
# .coveragerc — project configuration (the same keys work in pyproject.toml under [tool.coverage.*])
[run]
branch = True                  # measure branches, not just lines
source = .                     # measure all code in the project (finds files that no test imports)
omit =
    test_*.py                  # do not measure the tests themselves

[report]
show_missing = True            # print missing line numbers
fail_under = 80                # coverage report exits with status 2 below 80%
exclude_lines =
    pragma: no cover           # lines marked with this comment are ignored
    if __name__ == .__main__.: # standard main guard
```

```python
# Using it in CI with pytest-cov and the other report formats (verified commands)
#
#   pytest -q --cov=shop --cov-branch --cov-report=term-missing --cov-fail-under=95
#       shop.py   10   2   6   1   81%   8, 13
#       FAIL Required test coverage of 95% not reached. Total coverage: 81.25%
#       (pytest exits with a non-zero code, so CI fails)
#
#   coverage html         -> htmlcov/index.html (click a file to see red/green lines)
#   coverage json -o c.json  -> machine readable: totals.percent_covered_display = "81", missing_lines = 2
#   coverage xml          -> coverage.xml (for Codecov / SonarQube)
#
# Fix the gap by adding the missing test:
import pytest                                     # framework
from shop import discount                         # code under test


@pytest.mark.parametrize("code, expected", [("HALF", 50), ("TEN", 90), (None, 100)])
def test_discount_codes(code: str | None, expected: float) -> None:
    assert discount(100, code) == pytest.approx(expected)    # TEN now covered, line 8 is no longer missing


def uncovered_helper() -> str:                    # not worth testing (debug helper)
    return "debug"                                # pragma: no cover  <- excluded from the report
```
After adding `test_discount_codes`, only the dead `unused()` (line 13) stays missing: remove the function or test it.

Other useful options: `coverage run --parallel-mode` + `coverage combine` for xdist/multiprocess runs, `[run] concurrency = thread,greenlet` or `multiprocessing`, `coverage report --skip-covered`, `coverage erase`.

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|------------|
| Tool | `coverage.py` / `pytest-cov` | Istanbul / `nyc` / `c8` (built into Jest) |
| Run | `pytest --cov=pkg` | `jest --coverage` |
| Gate | `--cov-fail-under=80` | `coverageThreshold` in `jest.config.js` |
| Branch coverage | `branch = True` | included by default |
| Exclude | `# pragma: no cover` | `/* istanbul ignore next */` |
| HTML report | `coverage html` | `coverage/lcov-report/index.html` |

```python
# Python way — terminal
# pytest --cov=app --cov-report=term-missing --cov-fail-under=80
# in code: ignore a line
def debug() -> None:  # pragma: no cover
    print("only for developers")
```
```javascript
// JavaScript way — jest.config.js
module.exports = {
  collectCoverage: true,
  coverageThreshold: { global: { branches: 80, lines: 80 } },   // fail below 80%
};
// ignore:  /* istanbul ignore next */
```

Key difference: Jest has coverage built in and measures branches by default. Python needs the `coverage` package, and you must turn on `branch = True` yourself, otherwise a half-tested `if` can look 100% covered.

---

## 🟠 FastAPI Connection
For a FastAPI service point `--cov` at the app package (`--cov=app`), not at the tests. Coverage reveals untested routes, error handlers, and dependency branches (for example the 404 path). With `pytest-xdist`, `pytest-cov` combines the data automatically. Use `source` so files that no test imports still show as 0%, which exposes forgotten modules.

```python
# FastAPI route with an error branch that coverage will flag if untested
from fastapi import FastAPI, HTTPException               # FastAPI
from fastapi.testclient import TestClient                # client

app: FastAPI = FastAPI()                                 # app
USERS: dict[int, str] = {1: "asha"}                      # fake db


@app.get("/users/{uid}")
def get_user(uid: int) -> dict[str, str]:
    if uid not in USERS:                                 # branch A (not found)
        raise HTTPException(status_code=404, detail="not found")   # coverage flags this if untested
    return {"name": USERS[uid]}                          # branch B (found)


client: TestClient = TestClient(app)                     # client


def test_found() -> None:
    assert client.get("/users/1").json() == {"name": "asha"}   # covers B only


def test_not_found() -> None:
    assert client.get("/users/9").status_code == 404     # covers A: without it, the report lists the raise line

# pytest --cov=<module> --cov-branch --cov-report=term-missing --cov-fail-under=90
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Chasing 100% and writing tests with no assertions
✅ Correct: coverage shows what ran, not what was verified; assert behaviour

```python
# Wrong — "covers" the line, verifies nothing
def test_discount() -> None:
    discount(100, "TEN")
# Right
def test_discount_ok() -> None:
    assert discount(100, "TEN") == pytest.approx(90)
```

❌ Mistake 2: Measuring only line coverage (no branches)
✅ Correct: `branch = True`; a line `if x: y = 1` is "covered" even if the `else` path (x false) was never run

❌ Mistake 3: Measuring the test files or missing untested files
✅ Correct: `omit = test_*.py` and `source = <package>` so never-imported modules show 0%

❌ Mistake 4: Parallel or multiprocess runs lose data
✅ Correct: use `pytest-cov` with xdist (handled), or `parallel = True` + `coverage combine`

---

## 🧠 Tricky Interview Question

```python
# Is this function 100% covered by the single test below? (line coverage, branch = False)
def sign(x: int) -> str:
    result = "non-negative"
    if x < 0:
        result = "negative"
    return result

def test_sign() -> None:
    assert sign(-5) == "negative"
```
Answer: Line coverage reports 100%, because every line ran (the `if` body ran, and `return` ran). But the case where `x >= 0` (the `if` is false and the body is skipped) was never tested. With `branch = True`, coverage reports a partial branch (`3->5` never taken, shown in the Missing column as `3->5`). This is why branch coverage matters, and why 100% line coverage never means "fully tested". To fix it, add `assert sign(3) == "non-negative"`.

---

## ⚫ Interview Questions + Answers

Q1: What does code coverage tell you, and what does it not?
A1: It tells you which lines/branches executed during tests. It does NOT tell you whether the tests assert the right things. Low coverage proves gaps; high coverage does not prove quality.

Q2: Line (statement) vs branch coverage?
A2: Line coverage checks that a line ran. Branch coverage checks that both outcomes of each decision (if true / if false, loop entered / skipped) happened. Enable with `branch = True`; it is more honest.

Q3: How do you enforce a minimum in CI?
A3: `coverage report --fail-under=80`, `fail_under = 80` in the config, or `pytest --cov=pkg --cov-fail-under=80`. The command returns a non-zero exit code when coverage is below the limit.

Q4: How do you exclude code from coverage?
A4: `# pragma: no cover` on a line (or block), and `exclude_lines` / `omit` in config for patterns and files. Use sparingly: for type-checking-only blocks, `__main__` guards, and abstract methods.

Q5: What is a reasonable target?
A5: Many teams use 80-90% total with branch coverage, and watch the trend and the coverage of new code (diff coverage with tools like Codecov). Core business logic should be near 100%; chasing 100% everywhere often adds low-value tests.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You want to find untested code and dead code
- CI should block coverage regressions
- Reviewing a pull request: does the new code have tests?

❌ Avoid when:
- Treating the percentage as the goal (gaming it with assertion-less tests)
- Comparing teams by coverage numbers
- Measuring generated code or migrations (exclude them)

---

## 📊 Visual Diagram
```
tests run ──► coverage traces executed lines/branches ──► .coverage (SQLite)
                                                              |
              +--------------+----------------+---------------+
              v              v                v               v
        report -m        html            xml / json      fail_under=80
      (terminal)    (red/green lines)  (Codecov, Sonar)   (CI pass/fail)

shop.py
  3  if price < 0:          ✓ ran
  5  if code == "HALF":     ✓ ran
  7  if code == "TEN":      ✓ ran
  8      return price*0.9   ✗ MISSING  <- no test passes "TEN"
 13  return "dead code"     ✗ MISSING  <- function never called
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Coverage | % of code run by tests | Tests से चले code का % |
| Statement coverage | Lines executed | चली हुई lines |
| Branch coverage | Both sides of decisions taken | निर्णयों के दोनों रास्ते चले |
| Missing lines | Lines no test ran | जिन lines को कोई test नहीं चला |
| fail_under | Minimum allowed % | न्यूनतम अनुमत % |
| pragma: no cover | Exclude a line | किसी line को छोड़ देना |

---

## ⚡ 3-Line Summary
English: `coverage.py` (or `pytest --cov`) shows which lines and branches your tests executed and which are missing. Turn on branch coverage, set `fail_under` in CI, and exclude only what is truly irrelevant. High coverage is not proof of good tests: assertions matter.
Hindi: `coverage.py` (या `pytest --cov`) दिखाता है कि tests ने कौन सी lines और branches चलाईं और कौन सी छूटीं। Branch coverage चालू करें, CI में `fail_under` रखें और सिर्फ सच में गैर-ज़रूरी चीज़ें exclude करें। ज़्यादा coverage अच्छे tests का सबूत नहीं है: assertions ज़रूरी हैं।

---

## ➡️ Next Topic
**289. TDD in Python** — write the failing test first, make it pass, then refactor (red, green, refactor).
