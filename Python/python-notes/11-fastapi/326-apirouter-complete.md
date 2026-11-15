---

# 326. APIRouter — Complete
# हिंदी में: APIRouter — पूरी जानकारी

---

## 🔵 Simple Definition (English)
`APIRouter` is a mini FastAPI app: you declare routes on it in any file, then plug it into the main app with `app.include_router()`. It can carry a shared prefix, tags, dependencies and extra responses.

## 🔵 सरल परिभाषा (Hindi)
`APIRouter` एक छोटा FastAPI app है: आप किसी भी file में इस पर routes लिखते हैं और फिर `app.include_router()` से main app में जोड़ते हैं। इसमें साझा prefix, tags, dependencies और extra responses रखे जा सकते हैं।

---

## 🔴 Problem it Solves
One `main.py` with 80 endpoints is unreadable, and every route repeats `/api/v1/users`, the same tag and the same auth dependency. APIRouter groups related routes in one module and applies the common settings once.

## 🔴 यह क्यों बना? (Hindi)
80 endpoints वाली एक `main.py` पढ़ना मुश्किल है, और हर route में `/api/v1/users`, वही tag और वही auth dependency दोहरानी पड़ती है। APIRouter संबंधित routes को एक module में रखता है और साझा settings एक बार लगाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → `router = APIRouter(prefix='/users', tags=['users'], dependencies=[...])`
Step 2 → Decorate functions with `@router.get('/')`, `@router.post('/')` ...
Step 3 → In main: `app.include_router(router)` (optionally extra `prefix`, `tags`, `dependencies`)
Step 4 → Final path = include prefix + router prefix + route path
Step 5 → Router dependencies run before every route in it
Step 6 → Routers can include other routers (nesting)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → `router = APIRouter(prefix='/users', tags=['users'], dependencies=[...])`
Step 2 → Functions पर `@router.get('/')`, `@router.post('/')` ... लगाएँ
Step 3 → Main में: `app.include_router(router)` (चाहें तो अलग `prefix`, `tags`, `dependencies`)
Step 4 → अंतिम path = include prefix + router prefix + route path
Step 5 → Router की dependencies उसके हर route से पहले चलती हैं
Step 6 → Routers दूसरे routers को include कर सकते हैं (nesting)
```

---

## 🟡 Real World Example
A Swiggy-style backend has `users`, `restaurants`, `orders`, `payments` routers, each in its own file and owned by a different team. The `admin` router adds `dependencies=[Depends(require_admin)]` once, protecting all its routes.

## 🟡 Real Example Hindi mein
Swiggy जैसे backend में `users`, `restaurants`, `orders`, `payments` routers होते हैं, हर एक अलग file में और अलग team के पास। `admin` router एक बार `dependencies=[Depends(require_admin)]` लगाकर अपने सभी routes सुरक्षित करता है।

---

## 💻 Code Example — Basic
A router with a prefix and tag, included in the app.

```python
# Basic APIRouter - every line commented
from fastapi import APIRouter, FastAPI  # router and app
from fastapi.testclient import TestClient  # test client

router: APIRouter = APIRouter(prefix="/users", tags=["users"])  # all paths start with /users


@router.get("/")  # becomes GET /users/
def list_users() -> list[str]:  # handler
    return ["asha", "ravi"]  # fake data


@router.get("/{user_id}")  # becomes GET /users/{user_id}
def get_user(user_id: int) -> dict[str, int]:  # handler
    return {"id": user_id}  # fake data


app: FastAPI = FastAPI()  # main app
app.include_router(router)  # plug the router in (without this nothing works)

client: TestClient = TestClient(app)  # client
print(client.get("/users/").json(), client.get("/users/7").json())  # call both
# Output: ['asha', 'ravi'] {'id': 7}
print(sorted(app.openapi()["paths"]))  # registered paths (from the OpenAPI schema)
# Output: ['/users/', '/users/{user_id}']
```

## 💻 Code Example — Advanced
Router-level auth dependency, shared responses, nesting, and an extra prefix at include time.

```python
# Production style: router-level dependencies, responses, nesting, prefixes at include time
from typing import Annotated  # for Annotated dependencies
from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException  # tools
from fastapi.testclient import TestClient  # test client


def require_token(x_token: Annotated[str, Header()]) -> str:  # auth dependency
    if x_token != "secret":  # simple check
        raise HTTPException(status_code=401, detail="bad token")  # reject
    return x_token  # pass


admin: APIRouter = APIRouter(  # admin router
    prefix="/admin",  # shared prefix
    tags=["admin"],  # shared tag
    dependencies=[Depends(require_token)],  # applies to EVERY route here
    responses={401: {"description": "Unauthorized"}},  # documented in OpenAPI
)
users: APIRouter = APIRouter(prefix="/users")  # nested child router


@users.get("/")  # GET /admin/users/
def users_list() -> list[str]:  # handler
    return ["asha"]  # data


admin.include_router(users)  # nest: users inside admin

app: FastAPI = FastAPI()  # app
app.include_router(admin, prefix="/v1")  # extra prefix when including -> /v1/admin/users/

client: TestClient = TestClient(app)  # client
print(client.get("/v1/admin/users/").status_code)  # header missing -> validation error first
# Output: 422
print(client.get("/v1/admin/users/", headers={"X-Token": "wrong"}).status_code)  # wrong token
# Output: 401
print(client.get("/v1/admin/users/", headers={"X-Token": "secret"}).json())  # with token
# Output: ['asha']
print(app.openapi()["paths"]["/v1/admin/users/"]["get"]["tags"])  # tag inherited
# Output: ['admin']
```

---

## 🟠 JavaScript vs Python Comparison

```python
router = APIRouter(prefix="/users", tags=["users"])

@router.get("/")
def list_users(): ...

app.include_router(router)
```

```javascript
// Express Router
const router = express.Router();
router.get('/', listUsers);
app.use('/users', router);
```

`express.Router()` + `app.use('/users', router)` maps directly to `APIRouter` + `include_router`. FastAPI additionally attaches tags, dependencies and OpenAPI responses to the router, so docs and auth follow the router automatically.

---

## 🟠 FastAPI Connection
`include_router` can override or add `prefix`, `tags`, `dependencies`, `responses` for third-party routers you cannot edit. Router dependencies run in addition to route-level ones. A missing header in a dependency gives 422 (validation) before your own 401 logic runs, as the verified output shows.

```python
from fastapi import APIRouter, Depends, FastAPI
from .deps import get_current_admin  # your auth dependency

admin_router: APIRouter = APIRouter(
    prefix="/admin", tags=["admin"], dependencies=[Depends(get_current_admin)]
)

app: FastAPI = FastAPI()
app.include_router(admin_router, prefix="/api/v1")  # /api/v1/admin/...
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting `include_router`
```python
router = APIRouter()
@router.get('/x')
def x(): ...
# never included -> 404
```
✅ Correct:
```python
app.include_router(router)
```

❌ Mistake 2: Doubling prefixes
```python
router = APIRouter(prefix='/users')
app.include_router(router, prefix='/users')  # /users/users/
```
✅ Correct:
```python
router = APIRouter(prefix='/users')
app.include_router(router)  # /users/
```

❌ Mistake 3: Repeating the same dependency on each route
```python
@router.get('/a', dependencies=[Depends(auth)])
@router.get('/b', dependencies=[Depends(auth)])
```
✅ Correct:
```python
router = APIRouter(dependencies=[Depends(auth)])  # once
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient

router = APIRouter()
app = FastAPI()
app.include_router(router)

@router.get("/late")
def late():
    return {"ok": True}

print(TestClient(app).get("/late").status_code)
```

**Answer**:
```
200
```
In this FastAPI version (0.162, verified) routes added to a router AFTER `include_router` are still served, because included routers are resolved lazily. In older versions `include_router` copied the routes at call time, so this gave 404. Do not rely on it: always define routes before including the router.

---

## ⚫ Interview Questions + Answers

Q1: APIRouter vs mounting a sub-application?
A1: APIRouter shares the main app's OpenAPI, middleware and dependencies. `app.mount()` mounts a separate ASGI app with its own docs/middleware.

Q2: What is the final path of a route?
A2: include_router prefix + router prefix + decorator path.

Q3: Can routers have dependencies?
A3: Yes: `APIRouter(dependencies=[...])` or in `include_router`. They run for every route of the router.

Q4: Can I nest routers?
A4: Yes: `parent.include_router(child)`. Prefixes and tags accumulate.

Q5: Can the same router be included twice?
A5: Yes, with different prefixes (e.g. `/v1` and `/v2`); useful for versioning.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Any app with more than a handful of endpoints
- Shared prefix, tags or auth across a group
- Versioning (`/v1`, `/v2`)

❌ Avoid when:
- A tiny 3-endpoint script (one file is fine)
- Circular imports between routers (extract shared code)
- Hiding business logic inside router files

---

## 📊 Visual Diagram

```
app = FastAPI()
  |-- include_router(api_router, prefix="/api")
        |-- users.router   (prefix="/users")    -> /api/users/...
        |-- orders.router  (prefix="/orders")   -> /api/orders/...
        |-- admin.router   (deps=[auth])        -> /api/admin/...  (auth on all)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| APIRouter | Group of routes | routes का समूह |
| include_router | Plug router into app | router को app में जोड़ना |
| prefix | Common path start | साझा path शुरुआत |
| dependencies | Callables run before routes | routes से पहले चलने वाले callables |
| Nesting | Router inside router | router के अंदर router |
| Versioning | /v1, /v2 API versions | API के संस्करण |

---

## ⚡ 3-Line Summary
English: `APIRouter` groups routes with a shared prefix, tags, dependencies and responses, and `include_router` plugs it into the app. Final path = include prefix + router prefix + route path. Define routes before including.
Hindi: `APIRouter` routes को साझा prefix, tags, dependencies और responses के साथ group करता है और `include_router` इसे app में जोड़ता है। अंतिम path = include prefix + router prefix + route path। Include करने से पहले routes लिखें।

---

## ➡️ Next Topic
**327. Router Organization** — how to lay out folders and files for a growing FastAPI project.

---

**Verification note:** Every code block was run with FastAPI 0.162.4, Starlette 1.10.0, Python 3.13.3 using TestClient / httpx (no real browser). The Output comments are the real printed output.
