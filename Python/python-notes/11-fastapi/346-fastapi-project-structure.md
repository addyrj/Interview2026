---

# 346. FastAPI Project Structure
# हिंदी में: FastAPI Project Structure (folders कैसे सजाएँ)

---

## 🔵 Simple Definition (English)
Project structure is how you split a FastAPI app into folders and files: routers (HTTP layer), schemas (Pydantic), models (database), services (business logic), core (config) and tests. The goal is that each file has one job, so a new developer can find things in seconds.

## 🔵 सरल परिभाषा (Hindi)
Project structure यह तय करता है कि FastAPI app को folders और files में कैसे बाँटें: routers (HTTP layer), schemas (Pydantic), models (database), services (business logic), core (config) और tests। मकसद यह है कि हर file का एक ही काम हो, ताकि नया developer चीज़ें सेकंडों में ढूँढ ले।

---

## 🔴 Problem it Solves
A single `main.py` with 2,000 lines mixes routes, SQL, validation and config. Merge conflicts grow, tests are hard, and circular imports appear. A clear layout lets teams work on different features without stepping on each other.

## 🔴 यह क्यों बना? (Hindi)
2,000 lines की एक `main.py` में routes, SQL, validation और config सब मिल जाते हैं। Merge conflicts बढ़ते हैं, tests मुश्किल होते हैं और circular imports आ जाते हैं। साफ़ layout से अलग-अलग teams अलग features पर बिना टकराए काम कर सकती हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → app/main.py only creates the app and includes routers
Step 2 → app/api/v1/*.py: thin routers (parse request, call service, return)
Step 3 → app/schemas/*.py: Pydantic input/output models
Step 4 → app/models/*.py: SQLAlchemy tables
Step 5 → app/services/*.py: business rules (no FastAPI imports)
Step 6 → app/core/config.py: settings; app/db/: engine + session
Step 7 → tests/ mirrors app/; migrations/ holds Alembic
Step 8 → Dependency direction: api -> services -> models. Never the reverse.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → app/main.py सिर्फ़ app बनाता है और routers जोड़ता है
Step 2 → app/api/v1/*.py: पतले routers (request पढ़ो, service बुलाओ, लौटाओ)
Step 3 → app/schemas/*.py: Pydantic input/output models
Step 4 → app/models/*.py: SQLAlchemy tables
Step 5 → app/services/*.py: business rules (FastAPI import नहीं)
Step 6 → app/core/config.py: settings; app/db/: engine + session
Step 7 → tests/ app/ जैसा ही; migrations/ में Alembic
Step 8 → Dependency की दिशा: api -> services -> models। कभी उल्टी नहीं।
```

---

## 🟡 Real World Example
A Razorpay-like service has features: `payments`, `refunds`, `customers`. Each feature gets a router file, a schema file and a service file. The payments team edits `services/payment_service.py` while the refunds team edits `refunds.py`; the shared `core/config.py` rarely changes. The same service code is also called from a Celery job without importing FastAPI.

## 🟡 Real Example Hindi mein
Razorpay जैसी service में features हैं: `payments`, `refunds`, `customers`। हर feature के लिए एक router file, एक schema file और एक service file होती है। Payments team `services/payment_service.py` बदलती है जबकि refunds team `refunds.py`; साझा `core/config.py` बहुत कम बदलता है। वही service code Celery job से भी बुलाया जाता है, FastAPI import किए बिना।

---

## 💻 Code Example — Basic
```python
# Basic layout (this exact tree was created and its tests were run)
# proj/
# ├── app/
# │   ├── main.py              <- creates app, includes routers
# │   ├── api/v1/products.py   <- router (HTTP only)
# │   ├── core/config.py       <- Settings
# │   ├── schemas/product.py   <- Pydantic models
# │   ├── services/product_service.py  <- business logic
# │   ├── models/              <- SQLAlchemy models (empty in this demo)
# │   └── db/                  <- engine/session (empty in this demo)
# └── tests/test_products.py
#
# app/schemas/product.py
from pydantic import BaseModel, ConfigDict, Field  # validation classes


class ProductCreate(BaseModel):  # input from client
    name: str = Field(min_length=2, max_length=50)  # 2..50 chars
    price: float = Field(gt=0)  # must be positive


class ProductOut(ProductCreate):  # output to client
    model_config = ConfigDict(from_attributes=True)  # allow ORM objects
    id: int  # server id


print(ProductOut(id=1, name="Pen", price=5).model_dump())  # quick check
# Output: {'name': 'Pen', 'price': 5.0, 'id': 1}
```

## 💻 Code Example — Advanced
```python
# Production style: the key files of the tree (each starts with its path)

# ---- app/core/config.py ----
from functools import lru_cache  # build settings once
from pydantic_settings import BaseSettings, SettingsConfigDict  # env-based config


class Settings(BaseSettings):  # one place for all config
    app_name: str = "Shop API"  # app title
    database_url: str = "sqlite:///./shop.db"  # override with env var DATABASE_URL
    debug: bool = False  # never True in prod
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")  # read .env


@lru_cache  # cached singleton
def get_settings() -> Settings:
    return Settings()  # reads env once


# ---- app/services/product_service.py ----
from typing import Dict, List  # types
from app.schemas.product import ProductCreate, ProductOut  # schemas


class ProductService:  # business logic, no FastAPI inside
    def __init__(self) -> None:
        self._rows: Dict[int, ProductOut] = {}  # fake storage

    def create(self, data: ProductCreate) -> ProductOut:
        new_id: int = len(self._rows) + 1  # next id
        row = ProductOut(id=new_id, **data.model_dump())  # build row
        self._rows[new_id] = row  # save
        return row  # return it

    def list(self) -> List[ProductOut]:
        return list(self._rows.values())  # all rows


_service = ProductService()  # module-level singleton for the demo


def get_product_service() -> ProductService:  # dependency provider
    return _service  # same instance


# ---- app/api/v1/products.py ----
from typing import Annotated, List  # types
from fastapi import APIRouter, Depends, status  # FastAPI pieces

router: APIRouter = APIRouter(prefix="/products", tags=["products"])  # URL prefix + docs tag
ServiceDep = Annotated[ProductService, Depends(get_product_service)]  # reusable alias


@router.post("", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(data: ProductCreate, svc: ServiceDep) -> ProductOut:
    return svc.create(data)  # router is thin: just call the service


@router.get("", response_model=List[ProductOut])
def list_products(svc: ServiceDep) -> List[ProductOut]:
    return svc.list()  # thin again


# ---- app/main.py ----
from contextlib import asynccontextmanager  # lifespan
from typing import AsyncIterator, Dict  # types
from fastapi import FastAPI  # app


@asynccontextmanager  # startup + shutdown
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    print("startup: open pools")  # open DB pool here
    yield  # serve
    print("shutdown: close pools")  # close pool here


def create_app() -> FastAPI:  # factory
    app = FastAPI(title=get_settings().app_name, lifespan=lifespan)  # build
    app.include_router(router, prefix="/api/v1")  # mount feature router

    @app.get("/health")  # liveness
    def health() -> Dict[str, str]:
        return {"status": "ok"}

    return app  # return app


app: FastAPI = create_app()  # uvicorn app.main:app


# ---- tests/test_products.py ----
from fastapi.testclient import TestClient  # client

client = TestClient(app)  # test client (in the real tree: from app.main import app)
r = client.post("/api/v1/products", json={"name": "Pen", "price": 5})  # create
print(r.status_code, r.json())  # check
# Output: 201 {'name': 'Pen', 'price': 5.0, 'id': 1}
print(client.post("/api/v1/products", json={"name": "P", "price": -1}).status_code)  # bad input
# Output: 422
```
The real multi-file tree was created in a scratch folder and `pytest` gave `2 passed` for the two tests (create + list, and validation 422). Run the server with `uvicorn app.main:app --reload`. Above, all files are merged into one block only so it can be read in one place; in a real project each section is its own file.

---

## 🟠 JavaScript vs Python Comparison

```python
# Python (FastAPI): feature routers
# app/main.py
app.include_router(users.router, prefix="/api/v1")  # mount router
```
```javascript
// JavaScript (Express): same idea with Router
// app.js
app.use("/api/v1/users", require("./routes/users"));  // mount router
// Typical Node tree: routes/ controllers/ services/ models/ config/
```

Key differences: Express folders are by convention only (controllers/routes/services); in FastAPI the tree is by convention too, but `APIRouter` and `Depends` make the layers explicit. Python needs `__init__.py` in older tooling (namespace packages work in 3.3+, but explicit files avoid tooling surprises).

---

## 🟠 FastAPI Connection
Two popular layouts:
1. By layer (small teams): `routers/`, `schemas/`, `models/`, `services/`.
2. By feature/domain (big teams, Netflix Dispatch style): `app/payments/{router,schemas,models,service}.py`, `app/refunds/...`.

```python
# Feature layout: app/payments/router.py
from fastapi import APIRouter  # router class

router: APIRouter = APIRouter(prefix="/payments", tags=["payments"])  # group


@router.get("/{payment_id}")  # GET /api/v1/payments/pay_1
def get_payment(payment_id: str) -> dict:
    return {"id": payment_id}  # service call goes here
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Business logic inside route functions
```python
# Wrong: 80 lines of discount logic and SQL inside the route
@router.post("/orders")
def create(...): ...

# Right: route calls order_service.create_order(...), service is testable without HTTP
```

❌ Mistake 2: Circular imports
```python
# Wrong: models imports services, services imports models
# Right: one direction only: api -> services -> models/schemas; shared types in schemas/core
```

❌ Mistake 3: Creating the DB engine at import time with hard-coded URL
```python
# Wrong:
engine = create_engine("postgresql://user:pass@localhost/db")

# Right: engine = create_engine(get_settings().database_url) from env config
```

❌ Mistake 4: Forgetting that `get_settings` is cached
```python
# Wrong: change env var in a test after first call and expect new value
# Right: get_settings.cache_clear() in the test, or override the dependency
```

---

## 🧠 Tricky Interview Question

**Q**: What is printed?

```python
import os
from functools import lru_cache

@lru_cache
def get():
    return os.environ.get("MODE", "dev")

print(get())
os.environ["MODE"] = "prod"
print(get())
get.cache_clear()
print(get())
```

**Answer**:
```
dev
dev
prod
```
`lru_cache` stores the first result, so the changed env var is ignored until `cache_clear()`. This is exactly why settings tests need `get_settings.cache_clear()`. (Verified by running.)

---

## ⚫ Interview Questions + Answers

Q1: Why keep `main.py` tiny?
A1: It should only build the app and include routers. Logic in `main.py` cannot be reused or tested in isolation.

Q2: What goes in the service layer?
A2: Business rules (pricing, stock checks, workflows). It takes plain Python/Pydantic objects, not `Request`, so Celery jobs and tests can call it.

Q3: Layer layout or feature layout?
A3: Layer layout is simple for small apps. Feature (domain) layout scales better because everything for payments sits in one folder.

Q4: Where do Alembic migrations go?
A4: A top-level `migrations/` folder plus `alembic.ini`; `env.py` imports `Base.metadata` from `app.models` (topic 347).

Q5: How do you avoid circular imports?
A5: Strict dependency direction, import types under `TYPE_CHECKING`, and keep shared schemas/constants in a low-level module.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- More than ~5 endpoints or more than one developer
- You need unit tests for business logic
- You expect the code to live for years

❌ Avoid when:
- A prototype or one-off script: a single file is fine
- Over-layering a tiny service (controller -> service -> repository -> DAO for 3 endpoints)

---

## 📊 Visual Diagram

```
project/
├── app/
│   ├── main.py ................ create_app(), include_router
│   ├── core/ .................. config, security, logging
│   ├── api/v1/ ................ routers (HTTP only)
│   ├── schemas/ ............... Pydantic in/out
│   ├── services/ .............. business logic
│   ├── models/ ................ SQLAlchemy tables
│   └── db/ .................... engine, session, get_db
├── migrations/ ................ Alembic
├── tests/ ..................... mirrors app/
├── Dockerfile  pyproject.toml  .env.example
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| APIRouter | Group of routes | routes का समूह |
| Service layer | Business logic code | business logic वाला code |
| Schema | Pydantic data shape | data का ढाँचा |
| Model | DB table class | database table class |
| Circular import | A imports B imports A | आपस में import का चक्र |
| Factory | Function creating the app | app बनाने वाला function |

---

## ⚡ 3-Line Summary
English: Keep `main.py` tiny, put HTTP in routers, data shapes in schemas, tables in models, rules in services and config in `core`. Dependencies flow one way and tests mirror the app.
Hindi: `main.py` छोटा रखें; HTTP routers में, data shapes schemas में, tables models में, rules services में और config `core` में रखें। Dependencies एक ही दिशा में बहें और tests app जैसे ही हों।

---

## ➡️ Next Topic
**347. FastAPI + Alembic + PostgreSQL** — real database migrations for your FastAPI app.
