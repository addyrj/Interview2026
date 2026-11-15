# FastAPI Cheatsheet — Interview Ready
# हिंदी में: FastAPI Quick Reference

> Condensed from `11-fastapi/` (notes verified on fastapi 0.162, pydantic 2.14, Python 3.13).

## 🔷 Routes & Parameters

### 1. Path parameters
`{name}` in the path + a type hint = automatic conversion and validation. Bad value gives 422 (route matched, validation failed), not 404.
```python
from fastapi import FastAPI
from fastapi.testclient import TestClient
app: FastAPI = FastAPI()
@app.get("/orders/{order_id}")
def get_order(order_id: int) -> dict[str, int]:
    return {"order_id": order_id}

c: TestClient = TestClient(app)
print(c.get("/orders/42").json())
# Output: {'order_id': 42}
r = c.get("/orders/abc")
print(r.status_code, r.json()["detail"][0]["msg"])
```
**हिंदी:** path में `{order_id}` और type hint लगाओ, FastAPI खुद convert और validate करता है; गलत value पर 404 नहीं, 422 आता है। · *Source: 11-fastapi/300-path-parameters.md*

### 2. Route order trap
Routes match in declaration order. A dynamic route declared first swallows the fixed one: `/orders/me` gives 422. Declare fixed paths first.
```python
@app.get("/orders/{order_id}")
def get_order(order_id: int): return {"order_id": order_id}

@app.get("/orders/me")
def me(): return {"order": "mine"}
```
**हिंदी:** dynamic route पहले लिखा तो `/orders/me` उसी में चला जाता है; fixed path हमेशा पहले declare करो। · *Source: 11-fastapi/300-path-parameters.md*

### 3. Query parameters
Function arguments not in the path are query params. A default makes them optional; `None` default means optional with no value.
```python
from fastapi import FastAPI
from fastapi.testclient import TestClient
app: FastAPI = FastAPI()
@app.get("/items")
def items(skip: int = 0, limit: int = 10, q: str | None = None) -> dict[str, object]:
    # skip and limit have defaults -> optional; q defaults to None -> optional
    return {"skip": skip, "limit": limit, "q": q}
c: TestClient = TestClient(app)
print(c.get("/items").json())
# Output: {'skip': 0, 'limit': 10, 'q': None}
print(c.get("/items?skip=20&limit=5&q=tea").json())
# Output: {'skip': 20, 'limit': 5, 'q': 'tea'}
```
**हिंदी:** path में नहीं आने वाले arguments query params होते हैं; default देने से वे optional हो जाते हैं। · *Source: 11-fastapi/301-query-parameters.md*

### 4. Request body with a Pydantic model
A parameter typed as a `BaseModel` is read from the JSON body. Missing field gives 422 with `loc = ['body', 'price']`. With two or more body params, each name becomes a key in the JSON.
```python
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel
app: FastAPI = FastAPI()
class Item(BaseModel):
    name: str
    price: float
    qty: int = 1
@app.post("/items", status_code=201)
def create_item(item: Item) -> dict[str, object]:
    return {"name": item.name, "total": item.price * item.qty}
c: TestClient = TestClient(app)
r = c.post("/items", json={"name": "pizza", "price": 250.5, "qty": 2})
print(r.status_code, r.json())
# Output: 201 {'name': 'pizza', 'total': 501.0}
```
**हिंदी:** BaseModel वाला parameter JSON body से पढ़ा जाता है; field missing हो तो 422 और `loc` में `body` दिखता है। · *Source: 11-fastapi/302-request-body-pydantic.md*

## 🔷 Pydantic v2

### 5. Pydantic v2 basics
Lax mode converts when no information is lost (`"5"` becomes `5`). v2 names: `model_dump`, `model_validate`, `model_dump_json`, `model_copy`.
```python
from pydantic import BaseModel, ConfigDict, Field, ValidationError, TypeAdapter
class U(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)
    id: int
    name: str
    email: str | None
    tags: list[str] = Field(default_factory=list)
u = U(id="5", name="  Ria ", email=None)
print(u.model_dump(), u.model_dump_json())
```
**हिंदी:** Pydantic v2 में `.dict()` की जगह `model_dump()` और `parse_obj` की जगह `model_validate()` चलता है। · *Source: 11-fastapi/305-pydantic-v1-vs-v2.md*

### 6. Field validators
`@field_validator` + `@classmethod`; always `return` the value (a missing return turns the field into `None`). Raise `ValueError`, not `assert`. Order: before validators, type and constraints, after validators, model validators.
```python
from pydantic import BaseModel, ValidationError, field_validator
class User(BaseModel):
    name: str
    age: int

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("name must not be blank")
        return v.title()
print(User(name="  asha  ", age="30"))
# Output: name='Asha' age=30
```
**हिंदी:** validator में value `return` करना मत भूलो, वरना field `None` हो जाता है; error के लिए `ValueError` उठाओ। · *Source: 11-fastapi/304-pydantic-validators.md*

### 7. response_model hides fields
Use separate input and output models. `response_model` filters the returned data, so secrets such as `password` never leave the API.
```python
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel
app: FastAPI = FastAPI()
class UserIn(BaseModel):
    name: str
    email: str
    password: str

class UserOut(BaseModel):
    id: int
    name: str
    email: str

@app.post("/users", response_model=UserOut)
def create_user(user: UserIn) -> dict:
    return {"id": 1, **user.model_dump()}
client: TestClient = TestClient(app)
resp = client.post("/users", json={"name": "Asha", "email": "a@x.com", "password": "s3cret"})
print(resp.status_code)
# Output: 200
print(resp.json())
# Output: {'id': 1, 'name': 'Asha', 'email': 'a@x.com'}
```
**हिंदी:** response_model से output filter होता है, इसलिए password जैसे fields response में कभी नहीं जाते। · *Source: 11-fastapi/306-response-models.md*

## 🔷 Dependencies

### 8. Dependency with yield (DB session pattern)
Code before `yield` runs before the endpoint, code in `finally` runs after, even when the endpoint raises `HTTPException`. Use `Annotated[T, Depends(fn)]`.
```python
from typing import Annotated, Iterator
from fastapi import Depends, FastAPI, HTTPException
from fastapi.testclient import TestClient
app: FastAPI = FastAPI()
EVENTS: list[str] = []
class FakeSession:
    def __init__(self) -> None:
        self.closed: bool = False
    def close(self) -> None:
        self.closed = True
        EVENTS.append("session closed")
def get_db() -> Iterator[FakeSession]:
    db: FakeSession = FakeSession()
    EVENTS.append("session opened")
    try:
        yield db
    finally:
        db.close()
@app.get("/ok")
def ok(db: Annotated[FakeSession, Depends(get_db)]) -> dict:
    EVENTS.append("endpoint running")
    return {"closed_inside": db.closed}
c: TestClient = TestClient(app)
print(c.get("/ok").json(), EVENTS)
# Output: {'closed_inside': False} ['session opened', 'endpoint running', 'session closed']
```
**हिंदी:** `yield` से पहले का code setup है और `finally` वाला cleanup; endpoint में error आए तब भी session बंद होता है। · *Source: 11-fastapi/314-dependencies-with-yield.md*

## 🔷 Auth

### 9. OAuth2 password flow + current user
`OAuth2PasswordBearer` reads the `Authorization: Bearer` header; `get_current_user` is a dependency; no token gives 401 `Not authenticated`. Needs `python-multipart` for the form login.
```python
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.testclient import TestClient
app: FastAPI = FastAPI()
oauth2_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(tokenUrl="token")
FAKE_USERS: dict[str, dict] = {"asha": {"username": "asha", "password": "pw1", "full_name": "Asha Rao"}}
@app.post("/token")
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()]) -> dict:
    user: dict | None = FAKE_USERS.get(form.username)
    if user is None or user["password"] != form.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    return {"access_token": f"token-{user['username']}", "token_type": "bearer"}
def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    username: str = token.removeprefix("token-")
    user: dict | None = FAKE_USERS.get(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
@app.get("/users/me")
def me(user: Annotated[dict, Depends(get_current_user)]) -> dict:
    return {"username": user["username"], "full_name": user["full_name"]}
c: TestClient = TestClient(app)
tok: dict = c.post("/token", data={"username": "asha", "password": "pw1"}).json()
print(tok)
# Output: {'access_token': 'token-asha', 'token_type': 'bearer'}
print(c.get("/users/me", headers={"Authorization": f"Bearer {tok['access_token']}"}).json())
```
**हिंदी:** login पर token मिलता है, फिर `get_current_user` dependency हर protected route पर token जाँचती है। · *Source: 11-fastapi/315-oauth2-in-fastapi.md*

### 10. JWT with PyJWT
A JWT has 3 dot-separated parts. Always pass `algorithms=[...]` to `decode`. Expired token raises `ExpiredSignatureError`; tampered token raises `InvalidSignatureError`.
```python
import time
import jwt
SECRET: str = "change-me-use-a-long-random-string-32chars+"
ALGO: str = "HS256"
payload: dict = {"sub": "asha", "role": "admin", "exp": int(time.time()) + 60}
token: str = jwt.encode(payload, SECRET, algorithm=ALGO)
decoded: dict = jwt.decode(token, SECRET, algorithms=[ALGO])
print(decoded["sub"], decoded["role"])
# Output: asha admin
try:
    old: str = jwt.encode({"sub": "asha", "exp": int(time.time()) - 10}, SECRET, algorithm=ALGO)
    jwt.decode(old, SECRET, algorithms=[ALGO])
except jwt.ExpiredSignatureError:
    print("expired")
# Output: expired
```
**हिंदी:** decode करते समय `algorithms=[...]` ज़रूर दो; token बदला हो या expire हो तो exception आती है। · *Source: 11-fastapi/316-jwt-auth-in-fastapi.md*

## 🔷 Middleware, CORS, Background, Lifespan, Errors

### 11. Middleware
`@app.middleware("http")` wraps every request: do work before `call_next`, then change the response. It also runs for 404 responses.
```python
import time
from typing import Awaitable, Callable
from fastapi import FastAPI, Request, Response
from fastapi.testclient import TestClient
app: FastAPI = FastAPI()
@app.middleware("http")
async def add_process_time(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    start: float = time.perf_counter()
    response: Response = await call_next(request)
    elapsed_ms: float = (time.perf_counter() - start) * 1000
    response.headers["X-Process-Time-ms"] = f"{elapsed_ms:.2f}"
    return response
@app.get("/hello")
def hello() -> dict:
    return {"msg": "hi"}
c: TestClient = TestClient(app)
r = c.get("/hello")
print(r.json())
# Output: {'msg': 'hi'}
```
**हिंदी:** middleware हर request को घेरता है; `call_next` से पहले और बाद में काम कर सकते हो, 404 पर भी चलता है। · *Source: 11-fastapi/318-middleware-in-fastapi.md*

### 12. CORS
Add `CORSMiddleware` with an explicit origin list. Allowed origin gets the `access-control-allow-origin` header; others do not (the notes warn against `["*"]` together with `allow_credentials=True`).
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient
app: FastAPI = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET"],
    allow_headers=["*"],
)
@app.get("/ping")
def ping() -> dict[str, str]:
    return {"msg": "pong"}
client: TestClient = TestClient(app)
r = client.get("/ping", headers={"Origin": "http://localhost:3000"})
print(r.status_code, r.headers.get("access-control-allow-origin"))
# Output: 200 http://localhost:3000
```
**हिंदी:** CORS में origins की list साफ़ लिखो; `["*"]` को `allow_credentials=True` के साथ मत मिलाओ। · *Source: 11-fastapi/319-cors-in-fastapi.md*

### 13. BackgroundTasks
Runs after the response is sent. Good for small jobs like email or logs; heavy work belongs in a queue (Celery).
```python
from fastapi import BackgroundTasks, FastAPI
from fastapi.testclient import TestClient
app: FastAPI = FastAPI()
LOG: list[str] = []
def write_log(message: str) -> None:
    LOG.append(f"sent: {message}")
@app.post("/signup")
def signup(email: str, tasks: BackgroundTasks) -> dict[str, str]:
    tasks.add_task(write_log, email)
    return {"status": "created"}
client: TestClient = TestClient(app)
print(client.post("/signup", params={"email": "a@b.com"}).json())
# Output: {'status': 'created'}
print(LOG)
# Output: ['sent: a@b.com']
```
**हिंदी:** BackgroundTasks response भेजने के बाद चलते हैं; भारी काम के लिए Celery जैसी queue चाहिए। · *Source: 11-fastapi/320-background-tasks.md*

### 14. Lifespan (startup and shutdown)
Use an `asynccontextmanager` passed as `FastAPI(lifespan=...)`. Code before `yield` is startup, after is shutdown. `TestClient` as a context manager triggers it.
```python
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from fastapi import FastAPI
from fastapi.testclient import TestClient
STATE: list[str] = []
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    STATE.append("startup")
    yield
    STATE.append("shutdown")
app: FastAPI = FastAPI(lifespan=lifespan)
@app.get("/")
def root() -> dict[str, list[str]]:
    return {"state": STATE}
with TestClient(app) as client:
    print(client.get("/").json())
    # Output: {'state': ['startup']}
print(STATE)
# Output: ['startup', 'shutdown']
```
**हिंदी:** lifespan में `yield` से पहले startup और बाद में shutdown का code लिखो; test में `with TestClient(app)` चाहिए। · *Source: 11-fastapi/323-lifespan-events-startup-shutdown.md*

### 15. Custom exception handler
`HTTPException` gives `{'detail': ...}`. Override `RequestValidationError` to reshape 422 responses.
```python
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
app: FastAPI = FastAPI()
@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"error": "bad input", "count": len(exc.errors())})
@app.get("/items/{item_id}")
def item(item_id: int) -> dict[str, int]:
    if item_id == 0:
        raise HTTPException(status_code=404, detail="not found")
    return {"id": item_id}
client: TestClient = TestClient(app)
print(client.get("/items/abc").json())
# Output: {'error': 'bad input', 'count': 1}
```
**हिंदी:** `RequestValidationError` का handler लिखकर 422 का format अपने हिसाब से बदल सकते हो। · *Source: 11-fastapi/324-exception-handlers.md*

## 🔷 Async vs Sync and Database

### 16. async def vs def (the classic question)
`/a` ~0.20 s, `/b` ~2.05 s (blocking call inside `async def` freezes the loop), `/c` ~0.23 s (plain `def` runs in a threadpool, 40 threads by default). Blocking code belongs in plain `def`.
```python
@app.get("/a")
async def a(): await asyncio.sleep(0.2)
@app.get("/b")
async def b(): time.sleep(0.2)
@app.get("/c")
def c(): time.sleep(0.2)
```
**हिंदी:** `async def` के अंदर `time.sleep` जैसा blocking call पूरा event loop रोक देता है; blocking काम `def` में रखो। · *Source: 11-fastapi/298-fastapi-performance.md*

### 17. SQLAlchemy 2.0 ORM CRUD
`DeclarativeBase`, `Mapped[...]`, `mapped_column`, `select()`, `Session`. In async code use `expire_on_commit=False`; lazy loading in async raises an error, so use `awaitable_attrs`.
```python
from sqlalchemy import String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
engine = create_engine("sqlite://")
class Base(DeclarativeBase):
    pass
class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    price: Mapped[int]
Base.metadata.create_all(engine)
with Session(engine) as session:
    session.add_all([Product(name="Pen", price=10), Product(name="Book", price=250)])
    session.commit()
```
**हिंदी:** SQLAlchemy 2.0 में `Mapped` और `select()` style चलता है; async session में `expire_on_commit=False` रखो। · *Source: 11-fastapi/332-database-with-fastapi-sqlalchemy.md*

## 🔷 Testing

### 18. TestClient
`TestClient(app)` calls the app without a server. Check `status_code`, `.json()`, and 422 `detail[0]['loc']`.
```python
from typing import Dict
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel
class Item(BaseModel):
    name: str
    price: float
app: FastAPI = FastAPI()
DB: Dict[int, Item] = {}
@app.post("/items", status_code=201)
def create(item: Item) -> Dict[str, int]:
    new_id: int = len(DB) + 1
    DB[new_id] = item
    return {"id": new_id}
@app.get("/items/{item_id}")
def get(item_id: int) -> Item:
    if item_id not in DB:
        raise HTTPException(status_code=404, detail="Item not found")
    return DB[item_id]
client: TestClient = TestClient(app)
r = client.post("/items", json={"name": "Pen", "price": 10.5})
print(r.status_code, r.json())
# Output: 201 {'id': 1}
r = client.get("/items/99")
print(r.status_code, r.json())
# Output: 404 {'detail': 'Item not found'}
```
**हिंदी:** TestClient server चलाए बिना app को call करता है; status code और 422 का `detail` जाँचो। · *Source: 11-fastapi/343-fastapi-testing-testclient.md*

## 🔷 Deployment

### 19. Run and package
Dev: `--reload`. Prod: several worker processes (each has its own memory, so shared state goes to Redis or PostgreSQL). Use the exec-form `CMD` so SIGTERM reaches the server.
```bash
# Dev:  uvicorn main:app --reload
# Prod: uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
# Or:   gunicorn app.main:app -k uvicorn_worker.UvicornWorker -w 4

FROM python:3.13-slim
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```
**हिंदी:** requirements पहले copy करो ताकि Docker layer cache काम करे; `CMD` exec form में लिखो ताकि SIGTERM server तक पहुँचे। · *Source: 11-fastapi/342-fastapi-docker.md , 11-fastapi/350-fastapi-deployment.md*

---

## 🔷 Key Rules

1. **Path vs query vs body** → in `{}` = path; simple type = query; `BaseModel` = JSON body
2. **Invalid input** → 422 from Pydantic before your function runs; wrong method = 405; unknown path = 404
3. **Route order** → fixed paths (`/orders/me`) before dynamic ones (`/orders/{id}`)
4. **`response_model=`** → always set it to filter sensitive fields
5. **`async def`** → never call blocking code inside it; use plain `def` or a thread
6. **Dependencies** → `Annotated[T, Depends(fn)]`; `yield` dependencies clean up even on errors
7. **JWT** → always pass `algorithms=[...]` to `decode`
8. **Multiple workers** → each has separate memory; keep shared state in Redis or a DB
9. **Pydantic v2** → `model_dump`, `model_validate`, `field_validator`; **Testing** → `with TestClient(app)` runs lifespan
