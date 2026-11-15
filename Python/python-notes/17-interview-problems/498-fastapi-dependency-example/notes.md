---

# 498. FastAPI Dependency Example
# हिंदी में: FastAPI Dependency का Example (Depends से injection)

Full runnable solution: [main.py](main.py) (yield dependency, auth, sub-dependencies, class dependency, `dependency_overrides`).

---

## 🔵 Simple Definition (English)
A dependency is a function (or class) FastAPI calls for you before your handler, injecting its result as a parameter via `Depends`. It is FastAPI's built-in dependency injection.

## 🔵 सरल परिभाषा (Hindi)
Dependency एक function (या class) है जिसे FastAPI आपके handler से पहले खुद बुलाता है और उसका नतीजा `Depends` के ज़रिए parameter में दे देता है। यह FastAPI का built-in dependency injection है।

---

## 🔴 Problem it Solves
Every endpoint needs the same things: a DB session, the current user, pagination, permission checks. Copy-pasting them is noisy and hard to test. Dependencies share this logic, run cleanup, and can be swapped in tests.

## 🔴 यह क्यों बना? (Hindi)
हर endpoint को वही चीज़ें चाहिए: DB session, current user, pagination, permission checks। उन्हें copy-paste करना गंदा और test करना कठिन है। Dependencies यह logic साझा करती हैं, cleanup चलाती हैं और tests में बदली जा सकती हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Write a function: def current_user(db: DB, x_token: Header()) -> dict
Step 2 → Declare it in a handler: user: Annotated[dict, Depends(current_user)]
Step 3 → FastAPI builds a dependency tree (current_user needs get_db)
Step 4 → Calls leaves first; a dependency used twice per request is cached
Step 5 → Handler runs; yield-dependencies resume after the response for cleanup
Step 6 → Tests: app.dependency_overrides[get_db] = fake_db
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → function लिखो: def current_user(db: DB, x_token: Header()) -> dict
Step 2 → handler में बताओ: user: Annotated[dict, Depends(current_user)]
Step 3 → FastAPI dependency tree बनाता है (current_user को get_db चाहिए)
Step 4 → पहले leaves बुलाता है; एक request में दो बार इस्तेमाल हुई dependency cache होती है
Step 5 → handler चलता है; yield-dependencies response के बाद cleanup के लिए लौटती हैं
Step 6 → Tests: app.dependency_overrides[get_db] = fake_db
```

---

## 🟡 Real World Example
A Zomato-style backend: `get_db` opens a session per request, `current_user` reads the JWT/token header, `require_admin` builds on it, and `Pagination` standardises `?page=&size=` across every list endpoint. In tests, `get_db` is replaced with an in-memory database.

## 🟡 Real Example Hindi mein
Zomato जैसा backend: `get_db` हर request पर session खोलता है, `current_user` JWT/token header पढ़ता है, `require_admin` उसी पर बनता है और `Pagination` हर list endpoint में `?page=&size=` एक जैसा रखता है। Tests में `get_db` की जगह in-memory database लग जाता है।

---

## 💻 Code Example — Basic
```python
# Basic dependency
from typing import Annotated  # modern DI style
from fastapi import Depends, FastAPI  # framework
from fastapi.testclient import TestClient  # in-process HTTP client

app = FastAPI()  # app

def common(q: str = "all") -> dict[str, str]:  # runs before the handler
    return {"q": q}  # value injected into the handler

@app.get("/search")
def search(c: Annotated[dict[str, str], Depends(common)]) -> dict[str, str]:  # receives common()'s result
    return c  # echo it

print(TestClient(app).get("/search?q=pizza").json())  # call the endpoint
# Output:
# {'q': 'pizza'}
```

## 💻 Code Example — Advanced
```python
# Excerpt from main.py: yield cleanup + chained auth
def get_db() -> Iterator[FakeDB]:
    events.append("open db")
    db = FakeDB()
    try:
        yield db  # handler runs here
    finally:
        events.append("close db")  # always runs

def current_user(db: DB, x_token: Annotated[str | None, Header()] = None) -> dict:
    if x_token is None or x_token not in db.users:
        raise HTTPException(status_code=401, detail="invalid token")
    return db.users[x_token]

def require_admin(user: User) -> dict:  # depends on current_user, which depends on get_db
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="admin only")
    return user
```
Real output of `python main.py` (Python 3.13.3, FastAPI 0.162.4; a Starlette `httpx` deprecation warning may print first):
```
401 {'detail': 'invalid token'}
{'id': 1, 'name': 'Asha', 'role': 'admin'}
{'detail': 'admin only'}
{'by': 'Asha'}
{'offset': 40, 'size': 20} 422
['open db', 'close db'] 10
{'id': 9, 'name': 'Stub', 'role': 'admin'}
all ok
```

---

## 🟠 JavaScript vs Python Comparison
Express uses middleware that mutates `req`; NestJS has real DI with decorators. FastAPI's `Depends` is closer to Nest providers but is just functions, resolved per request.

```python
@app.get("/me")
def me(user: User): ...   # user injected by Depends
```
```javascript
app.get("/me", authMiddleware, (req, res) => res.json(req.user));  // Express: middleware sets req.user
```

---

## 🟠 FastAPI Connection
This topic is the FastAPI mechanism. Use `dependencies=[Depends(...)]` on a router for checks that return nothing, and `app.dependency_overrides` in tests.

```python
from fastapi import APIRouter, Depends  # router + DI

admin = APIRouter(prefix="/admin", dependencies=[Depends(require_admin)])  # every route here needs admin

@admin.get("/stats")
def stats() -> dict[str, int]:  # no parameter needed
    return {"users": 10}
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Calling the dependency: `Depends(get_db())`.
✅ Correct: pass the function itself: `Depends(get_db)`.

```python
# Wrong
db = Depends(get_db())
# Right
db = Depends(get_db)
```

❌ Mistake 2: `return` instead of `yield` when cleanup is needed (connection never closed).
✅ Correct: `try: yield x finally: x.close()`.

❌ Mistake 3: Overrides left in place after a test.
✅ Correct: `app.dependency_overrides.clear()` in a fixture teardown.

❌ Mistake 4: Raising 403 for a missing token.
✅ Correct: 401 for unauthenticated, 403 for unauthorised.

---

## 🧠 Tricky Interview Question
```python
def get_n() -> int:
    print("called")
    return 1

@app.get("/x")
def x(a: int = Depends(get_n), b: int = Depends(get_n)) -> int:
    return a + b
```
Answer: "called" prints once per request and the response is `2`. FastAPI caches a dependency's result within one request (`use_cache=True`). Use `Depends(get_n, use_cache=False)` to call it each time.

---

## ⚫ Interview Questions + Answers

Q1: What is `Depends` and why use it?
A1: FastAPI's injection marker. It shares logic (auth, DB, pagination), is documented in OpenAPI and is overridable for tests.

Q2: How does cleanup work in a yield dependency?
A2: Code after `yield` runs after the response is sent; wrap in `try/finally` so it runs even on errors.

Q3: How do you test with a fake DB?
A3: `app.dependency_overrides[get_db] = lambda: FakeDB()`, then clear it.

Q4: Class vs function dependencies?
A4: Both are callables. A class's `__init__` parameters become query/header params, giving an object like `Pagination`.

Q5: Router-level vs parameter dependencies?
A5: Router/decorator `dependencies=[...]` run for side effects (checks) without injecting a value; parameter dependencies inject a value.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Auth, DB sessions, pagination, rate limits, settings shared by routes
- You want easy test substitution

❌ Avoid when:
- One-off local logic only a single handler needs
- Global cross-cutting concerns better done as middleware (CORS, request logging)

---

## 📊 Visual Diagram
```
Request ──► require_admin ──► current_user ──► get_db (open)
                                                  │
                      handler(admin) ◄────────────┘
                           │
Response ◄── get_db finally (close)   (HTTPException anywhere -> 401/403 response)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Dependency injection | Framework supplies needed objects | ज़रूरी objects खुद देना |
| Depends | Marker to declare a dependency | dependency का निशान |
| Sub-dependency | Dependency that has dependencies | dependency की dependency |
| yield dependency | Setup + cleanup around handler | setup और cleanup |
| dependency_overrides | Swap dependencies in tests | tests में बदलना |
| use_cache | Reuse result in one request | एक request में दोबारा इस्तेमाल |

---

## ⚡ 3-Line Summary
English: `Depends` lets FastAPI inject shared logic into handlers.
English: Dependencies chain, yield gives cleanup, results are cached per request.
English: `dependency_overrides` makes tests easy.
Hindi: `Depends` से FastAPI साझा logic handlers में inject करता है।
Hindi: Dependencies जुड़ती हैं, yield से cleanup मिलता है, नतीजा request में cache होता है।
Hindi: `dependency_overrides` से tests आसान हो जाते हैं।

---

## ➡️ Next Topic
499. Pytest Test Suite: how to test these endpoints and functions properly.

---
