---

# 283. Mocking — Complete Guide
# हिंदी में: Mocking — पूरी Guide

---

## 🔵 Simple Definition (English)
Mocking replaces real dependencies (DB, HTTP, Redis, OpenAI API) with fake objects in tests. `unittest.mock.MagicMock` — general mock. `AsyncMock` — for async functions. `patch` — temporarily replace an object in a module. Goal: test one unit in isolation without external systems. FastAPI: `app.dependency_overrides` replaces injected dependencies.

## 🔵 सरल परिभाषा (Hindi)
Mocking tests में real dependencies (DB, HTTP, Redis, OpenAI) को fake objects से replace करता है। `MagicMock` = general mock। `AsyncMock` = async functions के लिए। `patch` = किसी module में object temporarily replace। FastAPI: `dependency_overrides` से injected dependencies replace।

---

## 💻 Code Example — MagicMock + AsyncMock
```python
from unittest.mock import MagicMock, AsyncMock, patch, call
import pytest

# ─── MagicMock — sync mock ────────────────────────────────────────
def test_user_service_creates_user():
    # Create fake repo:
    mock_repo = MagicMock()
    mock_repo.save.return_value = {"id": 1, "name": "Priya"}
    
    service = UserService(repo=mock_repo)
    result = service.create_user("Priya", "priya@test.com")
    
    # Assert return value:
    assert result["name"] == "Priya"
    
    # Assert mock was called correctly:
    mock_repo.save.assert_called_once()
    mock_repo.save.assert_called_with(name="Priya", email="priya@test.com")

# ─── AsyncMock — for async functions ─────────────────────────────
@pytest.mark.asyncio
async def test_async_service():
    mock_repo = AsyncMock()
    mock_repo.get_user.return_value = {"id": 1, "name": "Priya"}
    mock_repo.save.return_value = {"id": 2, "name": "Raj"}
    
    service = UserService(repo=mock_repo)
    user = await service.get_user(1)
    
    assert user["name"] == "Priya"
    mock_repo.get_user.assert_awaited_once_with(1)   # note: assert_awaited

# ─── Raise exceptions ─────────────────────────────────────────────
def test_handles_db_error():
    mock_repo = MagicMock()
    mock_repo.save.side_effect = Exception("DB connection lost")
    
    service = UserService(repo=mock_repo)
    
    with pytest.raises(ServiceError, match="Failed to save user"):
        service.create_user("Priya", "priya@test.com")

# ─── Return different values on multiple calls ────────────────────
mock_fn = MagicMock()
mock_fn.side_effect = [1, 2, 3]   # first call → 1, second → 2, etc.
print(mock_fn())   # 1
print(mock_fn())   # 2
print(mock_fn())   # 3
# mock_fn()  → StopIteration

# ─── Mock attributes ─────────────────────────────────────────────
mock_user = MagicMock()
mock_user.name = "Priya"
mock_user.email = "priya@test.com"
mock_user.is_active = True

print(mock_user.name)   # "Priya"
print(mock_user.any_attribute_you_want)   # MagicMock (auto-creates!)
```

## 💻 Code Example — patch + FastAPI overrides
```python
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from httpx import AsyncClient

# ─── patch() — replace object in its module ──────────────────────
# Patch where the object is USED (not defined):
# If myapp/services.py imports `openai`, patch "myapp.services.openai"

def test_classify_product():
    with patch("myapp.services.openai_client") as mock_openai:
        mock_openai.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="8517.12.00"))]
        )
        
        result = classify_product("iPhone 15")
        assert result == "8517.12.00"
        mock_openai.chat.completions.create.assert_called_once()

# ─── patch as decorator ───────────────────────────────────────────
@patch("myapp.services.send_email")
@patch("myapp.services.get_db_session")
def test_with_multiple_patches(mock_db, mock_email):
    # Note: decorators apply bottom-up → innermost = first param
    mock_db.return_value = {"id": 1}
    
    result = create_user_with_email("Priya")
    
    mock_email.assert_called_once_with("Priya", "Welcome!")

# ─── Async patch ──────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_async_openai_call():
    with patch("myapp.ai.openai_client") as mock_client:
        mock_client.chat.completions.create = AsyncMock(
            return_value=MagicMock(
                choices=[MagicMock(message=MagicMock(content="result"))],
                usage=MagicMock(prompt_tokens=100, completion_tokens=50),
            )
        )
        
        result = await classify_with_ai("iPhone")
        assert result == "result"

# ─── FastAPI dependency overrides ────────────────────────────────
# The BEST way to mock FastAPI dependencies:
from fastapi.testclient import TestClient
from myapp.main import app
from myapp.dependencies import get_db, get_current_user

@pytest.fixture
def test_client():
    # Create fake dependencies:
    fake_db = AsyncMock()
    fake_db.execute.return_value = None
    
    fake_user = {"id": 1, "name": "Test User", "role": "user"}
    
    # Override dependencies for the entire test:
    app.dependency_overrides[get_db] = lambda: fake_db
    app.dependency_overrides[get_current_user] = lambda: fake_user
    
    client = TestClient(app)
    yield client
    
    # Clean up after test:
    app.dependency_overrides.clear()

def test_get_tariff(test_client):
    response = test_client.get("/tariffs/8517120000")
    assert response.status_code == 200

# ─── Async TestClient (httpx) ─────────────────────────────────────
@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_create_tariff(async_client):
    response = await async_client.post("/tariffs", json={
        "hs_code": "8517120000",
        "description": "Smartphones",
    })
    assert response.status_code == 201

# ─── Verify call patterns ─────────────────────────────────────────
mock = MagicMock()
mock("arg1", key="val")
mock("arg2")

# Assertions:
mock.assert_called()                          # called at least once
mock.assert_called_once()                     # called exactly once (fails here — called twice)
mock.assert_called_with("arg2")               # last call was with "arg2"
mock.assert_any_call("arg1", key="val")       # any call matched
mock.assert_called_once_with("arg1", key="val")  # exactly one call with these args

# Check all calls:
print(mock.call_count)   # 2
print(mock.call_args_list)
# [call('arg1', key='val'), call('arg2')]
assert mock.call_args_list == [call("arg1", key="val"), call("arg2")]
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python unittest.mock:
from unittest.mock import AsyncMock, patch

mock_fn = AsyncMock(return_value={"data": "result"})
result = await mock_fn("arg")
mock_fn.assert_awaited_once_with("arg")

with patch("module.external_service") as mock:
    mock.call.return_value = "mocked"
    run_code_that_uses_service()
```

```javascript
// JavaScript Jest:
const mockFn = jest.fn().mockResolvedValue({ data: "result" });
const result = await mockFn("arg");
expect(mockFn).toHaveBeenCalledWith("arg");

jest.mock('./externalService', () => ({
    call: jest.fn().mockReturnValue("mocked")
}));
```

Key similarities: both replace real dependencies with fakes. Both assert calls were made with expected arguments.

Key differences: Python `patch` requires the target path (where used, not defined). JS `jest.mock` hoists to top of file. Python async requires `AsyncMock`. Python `assert_awaited_once_with` for async.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Patching the wrong location
```python
# my_module.py:
from external_lib import send_email

def notify_user(user):
    send_email(user.email, "Hello!")  # uses the imported name

# Wrong — patching where send_email is defined:
with patch("external_lib.send_email") as mock:   # DOESN'T WORK
    notify_user(user)

# Correct — patch WHERE IT'S USED (the imported reference):
with patch("my_module.send_email") as mock:   # works!
    notify_user(user)
```

❌ Mistake 2: Not using `AsyncMock` for async functions
```python
# Wrong — MagicMock doesn't support await:
mock_fn = MagicMock()
result = await mock_fn()   # TypeError: object MagicMock can't be used in 'await'

# Correct:
mock_fn = AsyncMock()
result = await mock_fn()   # works!
```

---

## 🧠 Tricky Interview Question

**Q**: What is `spec=` parameter in `MagicMock` and why should you use it?

**Answer**: `mock = MagicMock(spec=UserRepository)` creates a mock that **only allows attributes and methods that exist on `UserRepository`**. Without `spec=`: `mock.typo_method()` succeeds silently — your test passes even though you're testing the wrong method. With `spec=`: `mock.typo_method()` raises `AttributeError` — catches typos. Also works with `spec_set` (stricter — can't set attributes either). Best practice: always use `spec=` for important mocks. `create_autospec(UserRepository)` does the same but also preserves signatures.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `MagicMock` and `Mock`?
A1: `Mock` is the base class — supports basic mocking. `MagicMock` extends `Mock` with support for magic methods (`__len__`, `__iter__`, `__str__`, `__enter__`/`__exit__`, etc.). `len(mock)` works with `MagicMock` (returns 0), fails with `Mock`. `with mock:` works with `MagicMock` (supports context manager). Use `MagicMock` by default — it handles more cases. `AsyncMock` extends `MagicMock` to support `await` — use for async functions and context managers.

Q2: What is `side_effect` and when do you use it?
A2: `mock.side_effect` overrides return value behavior. Options: (1) Exception class or instance: `mock.side_effect = ValueError("bad input")` — mock raises this. (2) Iterable: `mock.side_effect = [1, 2, 3]` — each call returns next value. (3) Callable: `mock.side_effect = lambda x: x * 2` — function is called with same args as mock. Use when: simulating failures, simulating different responses on repeated calls, or computing a dynamic return value. `return_value` is simpler for fixed returns; use `side_effect` for complex behavior.

Q3: How do FastAPI `dependency_overrides` work for testing?
A3: `app.dependency_overrides` is a dict mapping original dependency function → replacement function. `app.dependency_overrides[get_db] = lambda: fake_db` tells FastAPI: "whenever `get_db` would be called, call `lambda: fake_db` instead." Works for the entire test session until cleared. Override with `lambda: value` for simple replacement. Override with a generator function for context-manager dependencies: `async def fake_db(): yield mock_session`. Always clear: `app.dependency_overrides.clear()` in fixture teardown (or `finally`).

Q4: What is `patch.object()` and when is it needed?
A4: `patch.object(target, attribute)` patches `attribute` on `target` object directly — more targeted than `patch("module.path.attribute")`. Example: `with patch.object(user_service, "get_user", return_value=user):` patches the `get_user` method on the `user_service` instance. Use when: you have an instance and want to mock its method; path-based `patch` would be awkward. Also useful for mocking class methods: `patch.object(MyClass, "class_method", return_value=...)`.

Q5: What is the difference between `assert_called_with` and `assert_called_once_with`?
A5: `assert_called_with(*args, **kwargs)`: asserts the **most recent** call had these args — doesn't care how many total calls. `assert_called_once_with(*args, **kwargs)`: asserts the mock was called **exactly once** AND with these args. Fail scenarios: called twice → `assert_called_once_with` fails; called once with wrong args → both fail; called twice with right args last → `assert_called_with` passes, `assert_called_once_with` fails. Use `assert_called_once_with` when the function should only be called once (avoid duplicates). Use `assert_any_call` to check if any of multiple calls matched.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Mock | Fake object for testing | Testing के लिए fake object |
| MagicMock | Mock with magic methods | Magic methods वाला Mock |
| AsyncMock | Mock for async functions | Async functions के लिए Mock |
| patch | Temporarily replace object | Object temporarily replace |
| side_effect | Exception or dynamic return | Exception या dynamic return |
| return_value | What mock returns | Mock क्या return करे |
| dependency_overrides | FastAPI DI replacement | FastAPI DI replacement |

---

## ⚡ 3-Line Summary
English: Use `MagicMock` for sync, `AsyncMock` for async — set `return_value` for returns and `side_effect` for exceptions or sequences. Patch with `patch("module.where.used")` (not where defined) to isolate units from real dependencies. For FastAPI: use `app.dependency_overrides[get_db] = lambda: fake_db` — cleanest way to test endpoints without real database.
Hindi: Sync के लिए `MagicMock`, async के लिए `AsyncMock`। `patch("module.where.used")` से isolate करो। FastAPI में `dependency_overrides` से DB replace करो — cleanest test approach।

---

## ➡️ Next Topic
**278. pytest Complete** — fixtures, parametrize, marks. **287. Async Testing** — pytest-asyncio, AsyncClient. **288. Test Coverage** — coverage.py, pytest-cov.
