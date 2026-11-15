---

# 327. Router Organization
# हिंदी में: Router Organization (project की folder structure)

---

## 🔵 Simple Definition (English)
Router organization means arranging a FastAPI project into modules: one router file per feature, one place that assembles them, and a tiny `main.py`. It keeps the project readable as it grows from 5 to 500 endpoints.

## 🔵 सरल परिभाषा (Hindi)
Router organization का मतलब FastAPI project को modules में सजाना है: हर feature का एक router file, उन्हें जोड़ने की एक जगह और छोटा सा `main.py`। इससे project 5 से 500 endpoints तक पढ़ने लायक रहता है।

---

## 🔴 Problem it Solves
Projects start in one file, then become a 2000-line `main.py` with circular imports, merge conflicts and no clear owner for each area. A consistent layout answers: where does a new endpoint go, where is business logic, where are schemas?

## 🔴 यह क्यों बना? (Hindi)
Project एक file से शुरू होता है और फिर 2000 line की `main.py` बन जाता है, जिसमें circular imports, merge conflicts और किसी area का साफ़ मालिक नहीं होता। एक तय layout बताता है: नया endpoint कहाँ जाए, business logic कहाँ है, schemas कहाँ हैं?

---

## 🟢 How it Works — Step by Step

```
Step 1 → Pick a split: by TYPE (routers/, models/, schemas/) for small apps, by DOMAIN (users/, orders/) for large apps
Step 2 → One `router.py` per feature with `APIRouter(prefix=..., tags=[...])`
Step 3 → Keep handlers thin: call a `service.py` function, which uses `repository.py` / DB
Step 4 → `api.py` (or `routers/__init__.py`) includes all feature routers under `/api/v1`
Step 5 → `main.py` only builds the app: lifespan, middleware, handlers, `include_router`
Step 6 → Shared things go in `core/` (config, security, deps) to avoid circular imports
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Split चुनें: छोटे app में TYPE से (routers/, models/, schemas/), बड़े app में DOMAIN से (users/, orders/)
Step 2 → हर feature का एक `router.py`, जिसमें `APIRouter(prefix=..., tags=[...])`
Step 3 → Handlers पतले रखें: `service.py` का function बुलाएँ, जो `repository.py` / DB इस्तेमाल करे
Step 4 → `api.py` (या `routers/__init__.py`) सारे feature routers को `/api/v1` के नीचे include करता है
Step 5 → `main.py` सिर्फ़ app बनाता है: lifespan, middleware, handlers, `include_router`
Step 6 → साझा चीज़ें `core/` में (config, security, deps) ताकि circular imports न हों
```

---

## 🟡 Real World Example
A Razorpay-style monorepo has `app/payments`, `app/refunds`, `app/merchants`, each with `router.py`, `schemas.py`, `service.py`, `models.py`, `tests/`. A new engineer opens the folder of the feature and finds everything. The official FastAPI 'bigger applications' guide uses the type-based `routers/` layout.

## 🟡 Real Example Hindi mein
Razorpay जैसे monorepo में `app/payments`, `app/refunds`, `app/merchants` होते हैं, हर एक में `router.py`, `schemas.py`, `service.py`, `models.py`, `tests/`। नया engineer feature का folder खोलकर सब कुछ पा लेता है। FastAPI की official 'bigger applications' guide type-based `routers/` layout इस्तेमाल करती है।

---

## 💻 Code Example — Basic
Layout and two feature routers (this exact project was created and run).

```python
# Project layout
# app/
#   __init__.py
#   main.py        <- creates FastAPI(), includes api_router
#   api.py         <- assembles all routers under /api
#   routers/
#     __init__.py
#     users.py     <- APIRouter(prefix='/users')
#     orders.py    <- APIRouter(prefix='/orders')

# ---- app/routers/users.py ----
from fastapi import APIRouter  # router

router: APIRouter = APIRouter(prefix="/users", tags=["users"])  # users router


@router.get("/")  # GET /api/users/
def list_users() -> list[str]:  # handler
    return ["asha"]  # data

# ---- app/routers/orders.py ----
from fastapi import APIRouter  # router

router: APIRouter = APIRouter(prefix="/orders", tags=["orders"])  # orders router


@router.get("/")  # GET /api/orders/
def list_orders() -> list[int]:  # handler
    return [101, 102]  # data
```

## 💻 Code Example — Advanced
The assembler `api.py`, a tiny `main.py` and a runner proving all paths work (run from the project root with `python run.py`).

```python
# ---- app/api.py ----
from fastapi import APIRouter  # router
from app.routers import orders, users  # feature routers

api_router: APIRouter = APIRouter(prefix="/api")  # common prefix
api_router.include_router(users.router)  # add users
api_router.include_router(orders.router)  # add orders

# ---- app/main.py ----
from fastapi import FastAPI  # app
from app.api import api_router  # assembled routes

app: FastAPI = FastAPI(title="Shop API")  # create app
app.include_router(api_router)  # mount everything


@app.get("/health")  # tiny route allowed here
def health() -> dict[str, str]:  # handler
    return {"status": "ok"}  # ok

# ---- run.py (project root) ----
# run.py - test from the project root: python run.py
from fastapi.testclient import TestClient  # client
from app.main import app  # import the app

client: TestClient = TestClient(app)  # client
print(client.get("/api/users/").json(), client.get("/api/orders/").json(), client.get("/health").json())  # all routes
# Output: ['asha'] [101, 102] {'status': 'ok'}
print(sorted(app.openapi()["paths"]))  # all documented paths
# Output: ['/api/orders/', '/api/users/', '/health']
```

---

## 🟠 JavaScript vs Python Comparison

```python
# app/main.py
from fastapi import FastAPI
from app.api import api_router
app = FastAPI()
app.include_router(api_router)
```

```javascript
// src/app.js
const express = require('express');
const routes = require('./routes');      // routes/index.js assembles
const app = express();
app.use('/api', routes);
```

Same philosophy as Express `routes/index.js` that mounts `routes/users.js`, `routes/orders.js`. Python needs `__init__.py` (or namespace packages) and absolute imports like `from app.routers import users`; run with `python -m` / uvicorn from the project root so imports resolve.

---

## 🟠 FastAPI Connection
Common production layout (domain-based): `app/main.py`, `app/core/{config,security,deps}.py`, `app/users/{router,schemas,service,models}.py`, `app/orders/...`, `tests/`. Start uvicorn from the project root: `uvicorn app.main:app`. Avoid circular imports by letting routers import services, never the reverse, and by keeping shared dependencies in `core/`.

```python
# Run from the project root (the folder that CONTAINS app/):
#   uvicorn app.main:app --reload
#
# app/users/router.py
from fastapi import APIRouter, Depends
from app.core.deps import get_db
from app.users import service

router: APIRouter = APIRouter(prefix="/users", tags=["users"])


@router.get("/{uid}")
async def read_user(uid: int, db=Depends(get_db)) -> dict:
    return await service.get_user(db, uid)  # thin handler -> service
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Putting everything in `main.py`
```python
# main.py with 60 routes, models, helpers
```
✅ Correct:
```python
# one router per feature, main.py only assembles
```

❌ Mistake 2: Relative-path / wrong-directory imports
```python
# cd app && uvicorn main:app
from routers import users  # breaks elsewhere
```
✅ Correct:
```python
# cd project_root && uvicorn app.main:app
from app.routers import users
```

❌ Mistake 3: Circular imports between routers
```python
# users.py imports orders.py and orders.py imports users.py
```
✅ Correct:
```python
# move shared code to services/ or core/; routers only import downward
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient

router = APIRouter(prefix="/users")

@router.get("/")
def r():
    return 1

app = FastAPI()
app.include_router(router, prefix="/users")
c = TestClient(app)
print(c.get("/users/").status_code, c.get("/users/users/").status_code)
```

**Answer**:
```
404 200
```
The router has `prefix='/users'` and `include_router(..., prefix='/users')` is applied again, so the real path is `/users/users/`. `/users/` does not exist (404) and `/users/users/` does (200).

---

## ⚫ Interview Questions + Answers

Q1: Type-based or domain-based layout?
A1: Type-based (`routers/`, `models/`) is quick for small apps. Domain-based (`users/`, `orders/` each with all layers) scales better for teams because changes stay in one folder.

Q2: What belongs in main.py?
A2: App creation, lifespan, middleware, exception handlers and `include_router`. No business logic.

Q3: Why do circular imports happen?
A3: Two modules import each other, often routers sharing helpers. Fix by moving shared code to a lower layer (`core/`, `services/`) that imports nothing from routers.

Q4: How do I version the API?
A4: Create `api/v1/router.py` and `api/v2/router.py` assemblers and include each with a prefix.

Q5: Where do I run uvicorn from?
A5: The directory that contains the `app` package so `app.main:app` resolves; this also makes absolute imports work in tests.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Any app beyond a demo
- Multiple teams or features
- You plan to add tests per feature

❌ Avoid when:
- Over-engineering a 3-route script
- Too many tiny files/layers for simple CRUD
- Mixing layout styles in one repo

---

## 📊 Visual Diagram

```
project_root/
 |- app/
 |   |- main.py          (create app, include api_router)
 |   |- api.py           (assemble routers under /api)
 |   |- core/            (config, security, deps)
 |   |- users/  router.py schemas.py service.py models.py
 |   |- orders/ router.py schemas.py service.py models.py
 |- tests/
router -> service -> repository/DB   (imports only go downward)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Domain-based layout | Folder per feature | हर feature का folder |
| Thin handler | Handler only calls service | handler सिर्फ़ service बुलाता है |
| Service layer | Business logic | business logic की परत |
| Circular import | A imports B imports A | A, B को और B, A को import करे |
| Package | Folder with __init__.py | __init__.py वाला folder |
| Assembler | File that includes routers | routers जोड़ने वाली file |

---

## ⚡ 3-Line Summary
English: One router per feature, one assembler file, and a tiny `main.py`. Keep handlers thin and imports flowing downward to avoid circular imports. Run uvicorn from the project root.
Hindi: हर feature का एक router, एक assembler file और छोटा `main.py`। Handlers पतले रखें और imports नीचे की ओर रखें ताकि circular imports न हों। Uvicorn project root से चलाएँ।

---

## ➡️ Next Topic
**328. Tags + Metadata** — organize and describe your endpoints in the generated docs.

---

**Verification note:** Every code block was run with FastAPI 0.162.4, Starlette 1.10.0, Python 3.13.3 using TestClient / httpx (no real browser). The Output comments are the real printed output. The multi-file project in the examples was created in a scratch folder and run with `python run.py`.
