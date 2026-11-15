---

# 282. pytest Plugins
# हिंदी में: pytest Plugins (pytest की क्षमता बढ़ाना)

---

## 🔵 Simple Definition (English)
A pytest plugin is a package (or a `conftest.py`) that adds features to pytest through hooks: new command-line options, fixtures, markers, reports, or ways to run tests. You install popular ones with `pip` (pytest-cov, pytest-mock, pytest-asyncio, pytest-xdist) and pytest loads them automatically.

## 🔵 सरल परिभाषा (Hindi)
pytest plugin एक package (या `conftest.py`) है जो hooks के ज़रिए pytest में नई सुविधाएं जोड़ता है: नए command-line options, fixtures, markers, reports या tests चलाने के नए तरीके। लोकप्रिय plugins `pip` से install होते हैं (pytest-cov, pytest-mock, pytest-asyncio, pytest-xdist) और pytest उन्हें अपने आप load करता है।

---

## 🔴 Problem it Solves
pytest core is small on purpose. Real projects need coverage reports, async test support, parallel runs, mock helpers, random ordering, and custom rules (like "skip slow tests unless --runslow"). Instead of putting everything in the core, pytest exposes about 100 hooks, and anyone can write a plugin that uses them. This keeps the core stable and lets the community add features.

## 🔴 यह क्यों बना? (Hindi)
pytest का core जानबूझकर छोटा रखा गया है। असली projects को coverage reports, async test support, parallel runs, mock helpers, random ordering और custom rules ("--runslow न हो तो slow tests skip करो") चाहिए। सब कुछ core में डालने की जगह pytest लगभग 100 hooks देता है और कोई भी उनसे plugin लिख सकता है। इससे core स्थिर रहता है और community नई सुविधाएं जोड़ती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → pip install a plugin (it registers an entry point named "pytest11")
Step 2 → At startup pytest scans entry points and loads every installed plugin
Step 3 → Also loads conftest.py files (local plugins) and -p <module> plugins
Step 4 → Plugins implement hooks: pytest_addoption, pytest_configure,
         pytest_collection_modifyitems, pytest_runtest_makereport, ...
Step 5 → pytest calls each hook at the right time during: configure -> collect -> run -> report
Step 6 → Disable one if needed: pytest -p no:randomly

Header of every run lists loaded plugins:  plugins: cov-7.1.0, xdist-3.8.0, mock-3.17.0 ...
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → plugin pip से install करो (यह "pytest11" नाम का entry point register करता है)
Step 2 → Startup पर pytest entry points scan करके हर installed plugin load करता है
Step 3 → conftest.py files (local plugins) और -p <module> plugins भी load होते हैं
Step 4 → Plugins hooks implement करते हैं: pytest_addoption, pytest_configure,
         pytest_collection_modifyitems, pytest_runtest_makereport, ...
Step 5 → pytest सही समय पर हर hook बुलाता है: configure -> collect -> run -> report
Step 6 → ज़रूरत हो तो बंद करो: pytest -p no:randomly
```

---

## 🟡 Real World Example
A FastAPI team at a fintech company uses: `pytest-asyncio` to test `async def` endpoints and services, `pytest-cov` to enforce 85% coverage in CI, `pytest-xdist` (`-n auto`) to cut a 12-minute suite to 3 minutes on 4 CPU cores, `pytest-mock` for the `mocker` fixture, and `pytest-randomly` to catch tests that depend on order. Their `conftest.py` adds a custom `--runslow` option so slow integration tests are skipped by default.

## 🟡 Real Example Hindi mein
किसी fintech कंपनी की FastAPI team इस्तेमाल करती है: `async def` endpoints और services के tests के लिए `pytest-asyncio`, CI में 85% coverage लागू करने के लिए `pytest-cov`, 12 मिनट की suite को 4 CPU cores पर 3 मिनट में लाने के लिए `pytest-xdist` (`-n auto`), `mocker` fixture के लिए `pytest-mock`, और order पर निर्भर tests पकड़ने के लिए `pytest-randomly`। उनकी `conftest.py` एक custom `--runslow` option जोड़ती है ताकि slow integration tests default में skip हों।

---

## 💻 Code Example — Basic
```python
# Basic: using installed plugins (verified: pytest 9.2, pytest-cov 7.1, pytest-mock 3.17,
# pytest-xdist 3.8, pytest-asyncio 1.4, Python 3.13)
#
# pip install pytest-cov pytest-mock pytest-xdist pytest-asyncio pytest-randomly
#
# mathlib.py — code under test
import time                                       # clock (external dependency)


def slow_square(n: int) -> int:                   # function with an error branch
    if n < 0:
        raise ValueError("negative")              # error branch
    return n * n


def now() -> float:                               # something we want to fake
    return time.time()


def greeting() -> str:                            # depends on now()
    return "late" if now() > 100 else "early"


# test_plugins.py
import pytest                                     # framework
from pytest_mock import MockerFixture             # type from the pytest-mock plugin
import mathlib                                    # code under test


def test_mocker(mocker: MockerFixture) -> None:   # "mocker" fixture comes from pytest-mock
    mocker.patch("mathlib.now", return_value=5.0) # patch is undone automatically after the test
    assert mathlib.greeting() == "early"


def test_error() -> None:
    with pytest.raises(ValueError):
        mathlib.slow_square(-1)


@pytest.mark.asyncio                              # mark provided by pytest-asyncio
async def test_async() -> None:
    import asyncio
    await asyncio.sleep(0)                        # real await inside the test
    assert True

# Commands and REAL results:
#   pytest -q --cov=mathlib --cov-report=term-missing
#       mathlib.py   9 stmts   1 miss   89%   Missing: 9      (the now() body is patched out)
#   pytest -q -n 2                  -> 5 passed (xdist runs tests in 2 worker processes)
#   pytest -p no:randomly           -> turns off random ordering
#   pytest (with pytest-randomly)   -> header shows "Using --randomly-seed=<number>"
#                                      reproduce that order with:  pytest --randomly-seed=<number>
```

## 💻 Code Example — Advanced
```python
# conftest.py — a LOCAL plugin: custom CLI flag + marker + hook + fixture
import pytest                                     # framework


def pytest_addoption(parser: pytest.Parser) -> None:          # hook: add --runslow flag
    parser.addoption("--runslow", action="store_true", default=False, help="run slow tests")


def pytest_configure(config: pytest.Config) -> None:          # hook: register the marker
    config.addinivalue_line("markers", "slow: slow test")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if config.getoption("--runslow"):             # flag given: run everything
        return
    skip = pytest.mark.skip(reason="need --runslow")          # otherwise skip slow tests
    for item in items:                            # inspect every collected test
        if "slow" in item.keywords:               # has @pytest.mark.slow
            item.add_marker(skip)                 # attach the skip mark


@pytest.fixture
def banner(request: pytest.FixtureRequest) -> str:
    return f"running {request.node.name}"         # plugin-provided fixture


# test file
@pytest.mark.slow
def test_slow() -> None:
    assert 9 * 9 == 81


def test_banner(banner: str) -> None:
    assert banner == "running test_banner"        # uses the fixture from conftest


# Real results:
#   pytest -rs                -> SKIPPED [1] test_plugins.py:6: need --runslow ; 4 passed, 1 skipped
#   pytest --runslow          -> 5 passed
#
# To publish your own plugin as a package, expose it in pyproject.toml:
#   [project.entry-points.pytest11]
#   myplugin = "my_package.plugin"
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | pytest | Jest |
|---------|--------|------|
| Extension point | hooks (`pytest_*`) | reporters, transforms, custom matchers |
| Install | `pip install pytest-xyz` (auto-loaded) | `npm i` + register in `jest.config.js` |
| Coverage | `pytest-cov` | built in (`--coverage`, Istanbul) |
| Parallel | `pytest-xdist` (`-n auto`) | built in (workers) |
| Local extension | `conftest.py` | `setupFilesAfterEnv` file |
| Mocks | `pytest-mock` (`mocker`) | built in (`jest.fn`, `jest.mock`) |

```python
# Python way — add options and behaviour with hooks
def pytest_addoption(parser):                     # in conftest.py
    parser.addoption("--env", default="dev")      # custom CLI option

# run: pytest --env=staging
```
```javascript
// JavaScript way — jest.config.js
module.exports = {
  setupFilesAfterEnv: ["./jest.setup.js"],        // local extension
  reporters: ["default", "jest-junit"],           // plugin-style reporter
  collectCoverage: true,                          // coverage is built in
};
```

Key difference: Jest ships coverage, mocks, and parallel running inside the core. pytest keeps these as plugins, so you choose and version them. Installed plugins load automatically (no config file needed).

---

## 🟠 FastAPI Connection
A typical FastAPI pyproject uses `pytest-asyncio` (async services/endpoints through `httpx.AsyncClient`), `pytest-cov` for coverage gates, `pytest-xdist` for speed, and a `conftest.py` that provides `client` and database fixtures. Configure all of it in one place.

```python
# pyproject.toml (TOML shown as a comment block so this file stays valid Python)
# [tool.pytest.ini_options]
# addopts = "-ra --strict-markers --cov=app --cov-report=term-missing --cov-fail-under=85 -n auto"
# asyncio_mode = "strict"
# asyncio_default_fixture_loop_scope = "function"
# markers = ["slow: slow tests", "integration: needs real services"]

# conftest.py — shared client fixture used by every FastAPI test
from collections.abc import Iterator              # yield fixture type
import pytest                                     # pytest
from fastapi.testclient import TestClient         # in-process client
from app.main import app                          # the real FastAPI app (your project)


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as c:                    # startup/shutdown handled
        yield c
```
Note: `-n auto` with `--cov` works because pytest-cov supports xdist; with xdist keep tests independent (no shared files or ports).

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Async test without pytest-asyncio (or without the mark in strict mode)
✅ Correct: install the plugin and mark the test (or set `asyncio_mode = "auto"`)

```python
# Wrong — real result: "async def functions are not natively supported" -> FAILED
async def test_x() -> None:
    assert True
# Right
import pytest
@pytest.mark.asyncio
async def test_y() -> None:
    assert True
```

❌ Mistake 2: Letting a plugin's random ordering expose hidden order dependence, then disabling it
✅ Correct: fix the shared state; use `--randomly-seed=N` to reproduce the failing order

❌ Mistake 3: Running parallel tests (`-n auto`) that share a database/file/port
✅ Correct: give each worker its own resources (e.g. `tmp_path`, a database name with the `worker_id` fixture)

❌ Mistake 4: Putting plugin hooks in a normal test file (they are ignored there)
✅ Correct: hooks go in `conftest.py` or a registered plugin module

---

## 🧠 Tricky Interview Question

```python
# conftest.py
def pytest_collection_modifyitems(items):
    items.reverse()

# test_order.py
def test_a(): print("a")
def test_b(): print("b")
def test_c(): print("c")
```
Question: What order do the tests run in with plain `pytest -s`, and what happens if `pytest-randomly` is also installed?
Answer: Without randomly: `c`, `b`, `a` — `pytest_collection_modifyitems` can reorder the collected list in place. With `pytest-randomly` installed, it also reorders items (it shuffles using a seed printed in the header: `Using --randomly-seed=...`), and plugin hook order decides who wins; use `@pytest.hookimpl(trylast=True)` or `-p no:randomly` to control it. The lesson: tests must never depend on order.

---

## ⚫ Interview Questions + Answers

Q1: How does pytest discover plugins?
A1: Through setuptools/pyproject entry points in the group `pytest11` (installed packages), `conftest.py` files, the `-p name` command-line option, and the `PYTEST_PLUGINS` environment variable. `pytest --trace-config` shows what was loaded.

Q2: Which plugins do you use for a FastAPI project and why?
A2: `pytest-asyncio` (async tests), `pytest-cov` (coverage gate), `pytest-xdist` (parallel), `pytest-mock` (`mocker` fixture), `pytest-randomly` (order independence), sometimes `pytest-timeout` (hung tests) and `respx` or `pytest-httpx` (HTTP mocking).

Q3: What is a hook in pytest?
A3: A function named `pytest_*` that pytest calls at a defined moment (add options, modify collected items, make a report). Plugins implement hooks; pluggy is the library that manages them. Example: `pytest_collection_modifyitems` edits the list of collected tests.

Q4: conftest.py vs a published plugin: when to use which?
A4: `conftest.py` for project-specific fixtures and hooks. A published plugin (with the `pytest11` entry point) when the same behaviour is shared across many repositories.

Q5: What problems come with `pytest-xdist`?
A5: Tests must be independent: shared databases, files, ports, and global state break. Session-scoped fixtures run once per worker, not once total. Output order is different. Use the `worker_id` fixture to separate resources.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need coverage, parallel runs, async tests, or mock helpers
- You want one shared feature in many repositories (publish a plugin)
- A project rule needs a CLI option (`--runslow`, `--env`)

❌ Avoid when:
- A simple fixture in `conftest.py` is enough
- You add many plugins "just in case" (slower start, version conflicts)
- You cannot make tests independent yet (do not enable xdist or randomly blindly)

---

## 📊 Visual Diagram
```
                      pytest core
                          |
   +----------+-----------+-----------+------------+
   |          |           |           |            |
pytest-cov  pytest-mock pytest-asyncio pytest-xdist conftest.py (local)
 coverage    `mocker`    async tests    parallel     --runslow, fixtures
   \__________\___________\____________/____________/
              all implement HOOKS called by pytest:
   configure -> collect (modifyitems) -> run (setup/call/teardown) -> report
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Plugin | Extension of pytest | pytest का extension |
| Hook | Function pytest calls at a fixed moment | तय समय पर बुलाया जाने वाला function |
| conftest.py | Local plugin file | Local plugin की file |
| Entry point | Package metadata that registers a plugin | Plugin register करने वाला metadata |
| xdist | Parallel test runner | Parallel test चलाने वाला |
| pytest-cov | Coverage plugin | Coverage plugin |

---

## ⚡ 3-Line Summary
English: pytest plugins add features through hooks: install them with pip (`pytest-cov`, `pytest-mock`, `pytest-asyncio`, `pytest-xdist`) or write them in `conftest.py`. They load automatically and can be disabled with `-p no:name`. Keep tests independent so parallel and random plugins work.
Hindi: pytest plugins hooks के ज़रिए सुविधाएं जोड़ते हैं: इन्हें pip से install करें (`pytest-cov`, `pytest-mock`, `pytest-asyncio`, `pytest-xdist`) या `conftest.py` में लिखें। ये अपने आप load होते हैं और `-p no:name` से बंद हो सकते हैं। Tests को independent रखें ताकि parallel और random plugins ठीक चलें।

---

## ➡️ Next Topic
**283. Mocking** — replacing real dependencies with fake objects so tests are fast and deterministic (already covered in your notes); then **284. unittest.mock** goes deeper into `Mock`, `MagicMock`, and `create_autospec`.
