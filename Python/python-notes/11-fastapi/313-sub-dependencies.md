---

# 313. Sub-dependencies
# हिंदी में: Sub-dependencies (dependency के अंदर dependency)

---

## 🔵 Simple Definition (English)
A sub-dependency is a dependency that itself uses `Depends(...)` on another dependency. FastAPI builds the whole chain (a graph) and runs the parts in the right order. Example: `get_db` -> `get_current_user` -> `require_admin`.

## 🔵 सरल परिभाषा (Hindi)
Sub-dependency वह dependency है जो खुद किसी दूसरी dependency पर `Depends(...)` लगाती है। FastAPI पूरी chain (graph) बनाकर सही क्रम में चलाता है। उदाहरण: `get_db` -> `get_current_user` -> `require_admin`।

---

## 🔴 Problem it Solves
Real checks build on each other: to know the admin you need the user, to know the user you need the token and the DB. Writing this chain manually in every route is repetitive and error-prone. Sub-dependencies let each small piece do one job, and FastAPI composes them.

## 🔴 यह क्यों बना? (Hindi)
असली checks एक दूसरे पर टिके होते हैं: admin जानने के लिए user चाहिए, user के लिए token और DB चाहिए। यह chain हर route में हाथ से लिखना दोहराव और गलती वाला काम है। Sub-dependencies में हर छोटा हिस्सा एक ही काम करता है और FastAPI उन्हें जोड़ देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Endpoint needs require_admin
Step 2 → require_admin needs get_current_user
Step 3 → get_current_user needs get_token (header) and get_db
Step 4 → FastAPI sorts the graph: leaves first (get_token, get_db)
Step 5 → Each runs once per request (cache), results flow upward
Step 6 → If any step raises HTTPException, the chain stops there
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Endpoint को require_admin चाहिए
Step 2 → require_admin को get_current_user चाहिए
Step 3 → get_current_user को get_token (header) और get_db चाहिए
Step 4 → FastAPI graph को क्रम में लगाता है: पहले सबसे नीचे वाले (get_token, get_db)
Step 5 → हर एक request में एक ही बार चलती है (cache), नतीजे ऊपर जाते हैं
Step 6 → किसी भी step पर HTTPException आए तो chain वहीं रुक जाती है
```

---

## 🟡 Real World Example
A Razorpay-like dashboard: `get_settings` -> `get_db` (needs the DB URL) -> `get_current_merchant` (needs the db and the API key header) -> `require_active_merchant` (blocks suspended accounts). Routes only write `merchant = Depends(require_active_merchant)`.

## 🟡 Real Example Hindi mein
Razorpay जैसे dashboard में: `get_settings` -> `get_db` (को DB URL चाहिए) -> `get_current_merchant` (को db और API key header चाहिए) -> `require_active_merchant` (suspended accounts को रोकता है)। Routes में बस `merchant = Depends(require_active_merchant)` लिखना पड़ता है।

---

## 💻 Code Example — Basic
```python
# Basic sub-dependencies - run directly (pip install fastapi httpx)
from typing import Annotated  # type tools
from fastapi import Depends, FastAPI, Header, HTTPException  # core
from fastapi.testclient import TestClient  # demo client

app: FastAPI = FastAPI()  # create app
LOG: list[str] = []  # call order recorder
USERS: dict[str, dict] = {"t1": {"name": "Asha", "role": "admin"}, "t2": {"name": "Ravi", "role": "viewer"}}  # fake DB


def get_token(authorization: Annotated[str | None, Header()] = None) -> str:  # level 1: read the header
    LOG.append("get_token")  # record
    if not authorization or not authorization.startswith("Bearer "):  # bad format
        raise HTTPException(status_code=401, detail="Missing token")  # stop chain
    return authorization.removeprefix("Bearer ")  # return only the token


def get_current_user(token: Annotated[str, Depends(get_token)]) -> dict:  # level 2: needs token
    LOG.append("get_current_user")  # record
    user: dict | None = USERS.get(token)  # look up
    if user is None:  # unknown token
        raise HTTPException(status_code=401, detail="Invalid token")  # stop chain
    return user  # pass user up


def require_admin(user: Annotated[dict, Depends(get_current_user)]) -> dict:  # level 3: needs user
    LOG.append("require_admin")  # record
    if user["role"] != "admin":  # permission check
        raise HTTPException(status_code=403, detail="Admins only")  # forbidden
    return user  # pass admin up


@app.get("/me")  # needs only level 2
def me(user: Annotated[dict, Depends(get_current_user)]) -> dict:  # endpoint
    return {"hello": user["name"]}  # response


@app.get("/admin")  # needs level 3
def admin(user: Annotated[dict, Depends(require_admin)]) -> dict:  # endpoint
    return {"admin": user["name"]}  # response


c: TestClient = TestClient(app)  # demo client
print(c.get("/admin", headers={"Authorization": "Bearer t1"}).json(), LOG)  # whole chain runs in order
# Output: {'admin': 'Asha'} ['get_token', 'get_current_user', 'require_admin']
LOG.clear()  # reset
print(c.get("/admin", headers={"Authorization": "Bearer t2"}).status_code, LOG)  # stops at last link
# Output: 403 ['get_token', 'get_current_user', 'require_admin']
LOG.clear()  # reset
print(c.get("/me").status_code, LOG)  # stops at the very first link
# Output: 401 ['get_token']
```

## 💻 Code Example — Advanced
```python
# Production style: diamond graph with cache, parametrized sub-dependency, class-based chain, scopes
from typing import Annotated  # metadata
from fastapi import Depends, FastAPI, HTTPException  # core
from fastapi.testclient import TestClient  # demo client

app: FastAPI = FastAPI()  # app
LOG: list[str] = []  # recorder


class Settings:  # shared config object
    def __init__(self) -> None:  # build once per request via dependency
        LOG.append("Settings")  # record creation
        self.db_url: str = "sqlite://"  # pretend setting


def get_settings() -> Settings:  # root of the graph
    return Settings()  # new object per request (cached within it)


class DB:  # fake DB connection
    def __init__(self, url: str) -> None:  # needs a url
        LOG.append("DB")  # record creation
        self.url = url  # store


def get_db(s: Annotated[Settings, Depends(get_settings)]) -> DB:  # child of settings
    return DB(s.db_url)  # connect


class UserRepo:  # repository class, itself a dependency with a sub-dependency
    def __init__(self, db: Annotated[DB, Depends(get_db)], s: Annotated[Settings, Depends(get_settings)]) -> None:
        self.db = db  # uses DB
        self.s = s  # uses settings too -> diamond: Settings reached by two paths
        LOG.append("UserRepo")  # record creation

    def find(self, uid: int) -> dict:  # query method
        if uid != 1:  # only user 1 exists
            raise HTTPException(status_code=404, detail="User not found")  # 404
        return {"id": 1, "db": self.db.url}  # found


def permission(name: str):  # factory: parametrized dependency
    def check(repo: Annotated[UserRepo, Depends()]) -> str:  # sub-dependency is a class
        LOG.append(f"permission:{name}")  # record
        return name  # return permission name
    return check  # return the callable


@app.get("/users/{uid}")  # endpoint
def get_user(
    uid: int,  # path param
    repo: Annotated[UserRepo, Depends()],  # class dependency (uses its own type)
    perm: Annotated[str, Depends(permission("users:read"))],  # parametrized dependency
) -> dict:  # response body
    return {**repo.find(uid), "perm": perm}  # merge


c: TestClient = TestClient(app)  # demo client
print(c.get("/users/1").json())  # works
# Output: {'id': 1, 'db': 'sqlite://', 'perm': 'users:read'}
print(LOG)  # Settings and DB and UserRepo each created ONCE, though reachable by many paths
# Output: ['Settings', 'DB', 'UserRepo', 'permission:users:read']
print(c.get("/users/9").status_code)  # error raised deep inside the method still maps to HTTP
# Output: 404
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python (FastAPI): chain declared by signatures
def get_db(): ...
def get_user(db = Depends(get_db)): ...
def require_admin(user = Depends(get_user)): ...

@app.get("/admin")
def admin(user = Depends(require_admin)): ...
```
```javascript
// JavaScript (Express): middleware chain, order matters, data stored on req
app.get("/admin", authenticate /* sets req.user */, requireAdmin /* reads req.user */, (req, res) => {
  res.json({ admin: req.user.name });
});
// NestJS: guards + providers; a provider's constructor lists its own dependencies, like FastAPI classes
```

Key difference: in Express the order of middleware in the array is your responsibility and the link between them is the hidden `req.user`. In FastAPI the link is explicit in the function signature and FastAPI orders the graph itself.

---

## 🟠 FastAPI Connection
`OAuth2PasswordBearer` is itself a dependency (it extracts the token). `get_current_user` depends on it and on the DB. `get_current_active_user` depends on `get_current_user`. This exact chain is the official FastAPI security tutorial pattern.

```python
# FastAPI: OAuth2 bearer extraction as the first link of a chain
from typing import Annotated  # metadata
from fastapi import Depends, FastAPI  # core
from fastapi.security import OAuth2PasswordBearer  # token extractor dependency
from fastapi.testclient import TestClient  # demo client

app: FastAPI = FastAPI()  # app
oauth2: OAuth2PasswordBearer = OAuth2PasswordBearer(tokenUrl="token")  # reads Authorization: Bearer ...


def current_user(token: Annotated[str, Depends(oauth2)]) -> str:  # link 2 uses link 1
    return f"user-for-{token}"  # decode in real life


def active_user(user: Annotated[str, Depends(current_user)]) -> str:  # link 3
    return user.upper()  # pretend extra checks


@app.get("/profile")  # endpoint
def profile(u: Annotated[str, Depends(active_user)]) -> dict:  # whole chain injected
    return {"u": u}  # response


c: TestClient = TestClient(app)  # client
print(c.get("/profile", headers={"Authorization": "Bearer abc"}).json())  # chain works
# Output: {'u': 'USER-FOR-ABC'}
print(c.get("/profile").status_code, c.get("/profile").json())  # first link fails
# Output: 401 {'detail': 'Not authenticated'}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Circular dependencies
```python
# Wrong - a needs b, b needs a: a cycle can never be resolved (and b is not even defined yet when a is written)
def a(x = Depends(b)): ...
def b(x = Depends(a)): ...

# Correct - extract the shared part into a third dependency c that both use
```

❌ Mistake 2: Doing everything in one giant dependency
```python
# Wrong - token parsing + DB + permission in one function, impossible to reuse or override
# Correct - small links: get_token, get_current_user, require_admin
```

❌ Mistake 3: Assuming each use creates a new object
```python
# Wrong - assuming two Depends(get_db) give two sessions in one request
# Correct - they share one (cached). Use use_cache=False if you really need two.
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

app = FastAPI()
log = []

def root():
    log.append("root")
    return 1

def left(r: int = Depends(root)):
    log.append("left")
    return r + 1

def right(r: int = Depends(root)):
    log.append("right")
    return r + 2

@app.get("/")
def top(l: int = Depends(left), r: int = Depends(right)):
    return l + r

c = TestClient(app)
print(c.get("/").json(), log)
```

**Answer**:
```
5 ['root', 'left', 'right']
```
This is a diamond. `root` is shared and runs once (cached), `left` returns 2 and `right` returns 3, so the sum is 5. Dependencies run in the order they are declared in the signature after their own sub-dependencies.

---

## ⚫ Interview Questions + Answers

Q1: How deep can sub-dependencies go?
A1: As deep as you need, as long as there is no cycle. FastAPI builds a dependency tree/graph once at startup per route and resolves it per request.

Q2: Is a shared sub-dependency executed multiple times?
A2: No. Within one request the result is cached by the callable (and its scopes), so a diamond runs the root once. `use_cache=False` turns this off.

Q3: What if a sub-dependency raises `HTTPException`?
A3: The chain stops immediately, later dependencies and the endpoint do not run, and the client gets that HTTP error.

Q4: Can sub-dependencies use request data?
A4: Yes. Each dependency can declare its own path/query/header/body parameters and `Request`. They all show up in the OpenAPI docs.

Q5: How do you override one link of a chain in a test?
A5: `app.dependency_overrides[get_db] = fake_db`. Everything above it uses the fake automatically.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Auth chains: token -> user -> active user -> admin
- Layered wiring: settings -> DB -> repository -> service
- Reusing a check with different parameters (permission factory)

❌ Avoid when:
- The chain is so deep that nobody can follow it (keep it to a few levels)
- A simple function argument would do
- Business logic belongs in a service, not inside dependency chains

---

## 📊 Visual Diagram

```
        get_settings
             │
          get_db ───────────┐
             │              │
        UserRepo      get_token
             │              │
             └────► get_current_user ◄─┘
                           │
                      require_admin
                           │
                       endpoint

   Leaves run first; each node runs once per request.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Sub-dependency | Dependency used by another | दूसरी dependency द्वारा इस्तेमाल की गई dependency |
| Dependency graph | Tree/DAG of dependencies | dependencies का graph |
| Diamond | Two paths share one root | दो रास्तों का एक साझा root |
| Cycle | A needs B needs A | A को B, B को A चाहिए |
| Factory | Function returning a dependency | dependency लौटाने वाला function |
| Resolve | Compute the values in order | क्रम से values निकालना |

---

## ⚡ 3-Line Summary
English: A dependency can depend on other dependencies, forming a graph that FastAPI resolves leaves-first. Shared nodes run once per request, and errors stop the chain. Keep each link small and override any link in tests.
Hindi: एक dependency दूसरी dependencies पर निर्भर हो सकती है और FastAPI graph को नीचे से ऊपर चलाता है। साझा node एक request में एक बार चलता है और error आने पर chain रुक जाती है। हर link छोटा रखें और tests में किसी भी link को बदलें।

---

## ➡️ Next Topic
**314. Dependencies with yield** — dependencies that need cleanup after the response (close DB, release locks).
