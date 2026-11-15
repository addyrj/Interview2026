---

# 308. HTTP Methods
# हिंदी में: HTTP Methods (GET, POST, PUT, PATCH, DELETE)

---

## 🔵 Simple Definition (English)
HTTP methods are verbs that say what you want to do with a resource: GET reads, POST creates, PUT replaces, PATCH changes part, DELETE removes. FastAPI has one decorator for each: `@app.get`, `@app.post`, `@app.put`, `@app.patch`, `@app.delete`.

## 🔵 सरल परिभाषा (Hindi)
HTTP methods क्रियाएँ (verbs) हैं जो बताती हैं कि resource के साथ क्या करना है: GET पढ़ता है, POST बनाता है, PUT पूरा बदलता है, PATCH थोड़ा बदलता है, DELETE हटाता है। FastAPI में हर एक के लिए decorator है: `@app.get`, `@app.post`, `@app.put`, `@app.patch`, `@app.delete`।

---

## 🔴 Problem it Solves
Before REST conventions, APIs had URLs like `/getUser`, `/deleteUser`, `/updateUser`, with everything done by POST. Caches, browsers and tools could not know what is safe to retry or cache. Methods give a shared language: GET is safe and cacheable, PUT and DELETE are idempotent, so retries are safe.

## 🔴 यह क्यों बना? (Hindi)
REST conventions से पहले URLs ऐसे होते थे `/getUser`, `/deleteUser`, `/updateUser` और सब कुछ POST से होता था। Cache, browser और tools को पता नहीं चलता था कि क्या दोबारा चलाना सुरक्षित है। Methods एक साझा भाषा देते हैं: GET सुरक्षित और cache हो सकने वाला है, PUT और DELETE idempotent हैं इसलिए retry सुरक्षित है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Client sends: METHOD + URL (e.g. PATCH /products/7)
Step 2 → FastAPI router matches both path AND method
Step 3 → Path match but wrong method → 405 Method Not Allowed
Step 4 → Your function runs and returns data
Step 5 → Client/proxies rely on method rules: safe? idempotent? cacheable?
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Client भेजता है: METHOD + URL (जैसे PATCH /products/7)
Step 2 → FastAPI router path और method दोनों match करता है
Step 3 → Path मिले पर method गलत हो तो 405 Method Not Allowed
Step 4 → आपका function चलता है और data लौटाता है
Step 5 → Client/proxy method के नियम मानते हैं: safe? idempotent? cacheable?
```

---

## 🟡 Real World Example
Flipkart product service: `GET /products` lists, `GET /products/7` reads one, `POST /products` creates, `PUT /products/7` replaces the whole product, `PATCH /products/7` changes only the price, `DELETE /products/7` removes it. A payment gateway makes POST safe to retry with an `Idempotency-Key` header because POST is not idempotent by itself.

## 🟡 Real Example Hindi mein
Flipkart product service में `GET /products` list देता है, `GET /products/7` एक product पढ़ता है, `POST /products` बनाता है, `PUT /products/7` पूरा product बदलता है, `PATCH /products/7` सिर्फ़ price बदलता है, `DELETE /products/7` हटाता है। Payment gateway POST को retry-safe बनाने के लिए `Idempotency-Key` header लेता है क्योंकि POST खुद idempotent नहीं होता।

---

## 💻 Code Example — Basic
```python
# Basic CRUD with all methods - run directly (pip install fastapi httpx)
from typing import Optional  # for optional fields
from fastapi import FastAPI, HTTPException  # app and errors
from fastapi.testclient import TestClient  # demo client
from pydantic import BaseModel  # models

app: FastAPI = FastAPI()  # create app


class Product(BaseModel):  # full product (used by POST and PUT)
    name: str  # product name
    price: float  # product price


class ProductPatch(BaseModel):  # partial update (PATCH)
    name: Optional[str] = None  # may be missing
    price: Optional[float] = None  # may be missing


DB: dict[int, Product] = {}  # in-memory table
NEXT_ID: list[int] = [1]  # mutable counter


@app.post("/products", status_code=201)  # CREATE
def create(p: Product) -> dict:  # body is a Product
    pid: int = NEXT_ID[0]  # take next id
    NEXT_ID[0] += 1  # advance counter
    DB[pid] = p  # save
    return {"id": pid, **p.model_dump()}  # return created item


@app.get("/products/{pid}")  # READ
def read(pid: int) -> Product:  # returns a Product
    if pid not in DB:  # not found
        raise HTTPException(404, "Not found")  # 404
    return DB[pid]  # found


@app.put("/products/{pid}")  # REPLACE everything
def replace(pid: int, p: Product) -> Product:  # whole object needed
    DB[pid] = p  # overwrite (creates if missing)
    return p  # return new value


@app.patch("/products/{pid}")  # CHANGE some fields
def patch(pid: int, changes: ProductPatch) -> Product:  # partial body
    if pid not in DB:  # must exist
        raise HTTPException(404, "Not found")  # 404
    data: dict = changes.model_dump(exclude_unset=True)  # only fields the client sent
    DB[pid] = DB[pid].model_copy(update=data)  # merge into the old value
    return DB[pid]  # updated value


@app.delete("/products/{pid}", status_code=204)  # REMOVE
def remove(pid: int) -> None:  # nothing returned
    DB.pop(pid, None)  # idempotent delete


c: TestClient = TestClient(app)  # demo client
print(c.post("/products", json={"name": "Phone", "price": 100}).json())  # create
# Output: {'id': 1, 'name': 'Phone', 'price': 100.0}
print(c.patch("/products/1", json={"price": 90}).json())  # only price changes
# Output: {'name': 'Phone', 'price': 90.0}
print(c.put("/products/1", json={"name": "Tab", "price": 50}).json())  # replace all
# Output: {'name': 'Tab', 'price': 50.0}
print(c.delete("/products/1").status_code, c.delete("/products/1").status_code)  # idempotent
# Output: 204 204
print(c.get("/products/1").status_code)  # gone
# Output: 404
```

## 💻 Code Example — Advanced
```python
# Production style: 405, HEAD/OPTIONS, multiple methods on one route, idempotency key
from fastapi import FastAPI, Header  # app and header reader
from fastapi.testclient import TestClient  # demo client
from typing import Optional  # type hint

app: FastAPI = FastAPI()  # app
PAYMENTS: dict[str, dict] = {}  # idempotency store: key -> saved response
COUNTER: list[int] = [0]  # how many real payments were made


@app.post("/pay")  # POST is NOT idempotent by default
def pay(amount: int, idempotency_key: Optional[str] = Header(default=None)) -> dict:  # key from header
    if idempotency_key and idempotency_key in PAYMENTS:  # retry with same key
        return PAYMENTS[idempotency_key]  # replay the old response, no double charge
    COUNTER[0] += 1  # charge for real
    result: dict = {"payment_id": COUNTER[0], "amount": amount}  # response body
    if idempotency_key:  # remember it
        PAYMENTS[idempotency_key] = result  # store under the key
    return result  # response


@app.api_route("/health", methods=["GET", "HEAD"])  # one handler for two methods
def health() -> dict:  # simple probe
    return {"status": "ok"}  # body (HEAD drops the body automatically)


c: TestClient = TestClient(app)  # demo client
h: dict = {"Idempotency-Key": "k1"}  # same key for both calls
print(c.post("/pay", params={"amount": 50}, headers=h).json())  # first call
# Output: {'payment_id': 1, 'amount': 50}
print(c.post("/pay", params={"amount": 50}, headers=h).json())  # retry, same result
# Output: {'payment_id': 1, 'amount': 50}
print(c.post("/pay", params={"amount": 50}).json())  # no key, charged again
# Output: {'payment_id': 2, 'amount': 50}
r = c.get("/pay", params={"amount": 1})  # wrong method on an existing path
print(r.status_code, r.headers["allow"])  # 405 and the allowed methods
# Output: 405 POST
print(c.head("/health").status_code, c.get("/health").json())  # HEAD and GET both work
# Output: 200 {'status': 'ok'}
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python (FastAPI)
@app.get("/items")
def list_items(): ...
@app.post("/items")
def create_item(item: Item): ...
@app.delete("/items/{id}")
def delete_item(id: int): ...
```
```javascript
// JavaScript (Express)
app.get("/items", (req, res) => { /* list */ });
app.post("/items", (req, res) => { /* create, body in req.body */ });
app.delete("/items/:id", (req, res) => { /* req.params.id is a STRING */ });
// fetch client: fetch(url, { method: "PATCH", body: JSON.stringify(data) })
```

Key difference: the concept is identical. In FastAPI the body is validated into a Pydantic model and path params are converted to `int` automatically, while Express gives raw strings and you validate yourself.

---

## 🟠 FastAPI Connection
FastAPI registers each decorator in a router and builds OpenAPI operations per method. Use `APIRouter` to group CRUD routes, `tags` for Swagger sections and `methods=[...]` with `api_route` only when you truly need several verbs on one function.

```python
# FastAPI: router grouping with a prefix
from fastapi import APIRouter, FastAPI  # router and app
from fastapi.testclient import TestClient  # demo client

router: APIRouter = APIRouter(prefix="/users", tags=["users"])  # all routes start with /users


@router.get("")  # GET /users
def users() -> list[str]:  # list
    return ["asha", "ravi"]  # data


@router.post("", status_code=201)  # POST /users
def add_user(name: str) -> dict:  # create
    return {"name": name}  # echo


app: FastAPI = FastAPI()  # app
app.include_router(router)  # attach router
c: TestClient = TestClient(app)  # client
print(c.get("/users").json(), c.post("/users", params={"name": "x"}).status_code)  # both methods
# Output: ['asha', 'ravi'] 201
print(sorted(app.openapi()["paths"]["/users"].keys()))  # operations in docs
# Output: ['get', 'post']
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using GET to change data
```python
# Wrong - crawlers, prefetch and caches may trigger it
@app.get("/delete-user/{id}")

# Correct
@app.delete("/users/{id}")
```

❌ Mistake 2: Using PUT for partial updates
```python
# Wrong - PUT means "replace all", missing fields get lost/defaulted
@app.put("/users/{id}")  # client sends only email

# Correct - PATCH for partial change
@app.patch("/users/{id}")
```

❌ Mistake 3: Using a body in GET and verbs in URLs
```python
# Wrong - /getAllUsers with a JSON body in GET (many proxies drop it)
# Correct - nouns in URLs, filters in query params: GET /users?city=Pune
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()
counter = {"n": 0}

@app.post("/inc")
def inc():
    counter["n"] += 1
    return counter["n"]

@app.put("/set")
def set_(v: int):
    counter["n"] = v
    return counter["n"]

c = TestClient(app)
print([c.post("/inc").json() for _ in range(3)])
print([c.put("/set", params={"v": 5}).json() for _ in range(3)])
print(c.get("/inc").status_code)
```

**Answer**:
```
[1, 2, 3]
[5, 5, 5]
405
```
POST is not idempotent: repeating it changes state every time. PUT is idempotent: the same call repeated gives the same final state. A GET to a POST-only path returns 405 Method Not Allowed, not 404, because the path exists.

---

## ⚫ Interview Questions + Answers

Q1: What does "safe" and "idempotent" mean?
A1: Safe means it does not change server state (GET, HEAD, OPTIONS). Idempotent means repeating it has the same effect as doing it once (GET, PUT, DELETE, HEAD, OPTIONS). POST and PATCH are generally not idempotent.

Q2: PUT vs PATCH?
A2: PUT replaces the whole resource, so the client sends all fields. PATCH changes only the fields sent. In FastAPI use a model with optional fields and `model_dump(exclude_unset=True)` for PATCH.

Q3: How do you make POST safe to retry?
A3: Use an idempotency key header. The server stores the first response under that key and replays it for retries (Stripe/Razorpay pattern).

Q4: What is 405 and how is it different from 404?
A4: 404 means the path does not exist. 405 means the path exists but not for that method; the response has an `Allow` header listing valid methods.

Q5: Why does a browser send OPTIONS?
A5: For CORS preflight, before a cross-origin request with custom headers or non-simple methods. In FastAPI add `CORSMiddleware` to answer it.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- GET for reads, POST for create/actions, PUT for full replace, PATCH for partial update, DELETE for removal
- Plural nouns in URLs (`/products/7`), verbs from the method

❌ Avoid when:
- Changing data in a GET
- Verbs in URLs (`/createUser`), unless it is a true action like `POST /orders/7/cancel`
- Sending a request body with GET or DELETE

---

## 📊 Visual Diagram

```
 Method   Purpose        Body?  Safe  Idempotent  Typical status
 GET      read           no     yes   yes         200
 POST     create/action  yes    no    no          201
 PUT      replace all    yes    no    yes         200/201
 PATCH    change part    yes    no    no*         200
 DELETE   remove         no     no    yes         204
 HEAD     headers only   no     yes   yes         200
 OPTIONS  allowed verbs  no     yes   yes         200/204

 /products ──► GET list, POST create
 /products/7 ─► GET one, PUT, PATCH, DELETE
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Method / Verb | Action on a resource | resource पर की जाने वाली क्रिया |
| Idempotent | Repeat = same result | बार-बार चलाने पर वही नतीजा |
| Safe | Does not change data | data नहीं बदलता |
| CRUD | Create, Read, Update, Delete | बनाना, पढ़ना, बदलना, हटाना |
| 405 | Method not allowed | method की अनुमति नहीं |
| Idempotency key | Token to dedupe retries | retry दोहराव रोकने वाला token |

---

## ⚡ 3-Line Summary
English: GET reads, POST creates, PUT replaces, PATCH changes part, DELETE removes. Know which are safe and idempotent so retries are correct. FastAPI gives one decorator per method and returns 405 for a wrong one.
Hindi: GET पढ़ता है, POST बनाता है, PUT पूरा बदलता है, PATCH थोड़ा बदलता है, DELETE हटाता है। जानिए कौन safe और idempotent है ताकि retry सही रहे। FastAPI हर method का अलग decorator देता है और गलत method पर 405 भेजता है।

---

## ➡️ Next Topic
**309. Form Data + File Upload** — requests that are not JSON: HTML forms and multipart file uploads.
