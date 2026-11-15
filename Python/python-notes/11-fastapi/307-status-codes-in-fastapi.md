---

# 307. Status Codes in FastAPI
# हिंदी में: FastAPI में Status Codes (HTTP जवाब का नतीजा-कोड)

---

## 🔵 Simple Definition (English)
An HTTP status code is a 3-digit number that tells the client what happened: 2xx success, 3xx redirect, 4xx client error, 5xx server error. In FastAPI you set the default with `status_code=` on the decorator and raise `HTTPException` for errors.

## 🔵 सरल परिभाषा (Hindi)
HTTP status code 3 अंकों का number है जो client को बताता है कि क्या हुआ: 2xx सफलता, 3xx redirect, 4xx client की गलती, 5xx server की गलती। FastAPI में decorator पर `status_code=` से default code तय होता है और errors के लिए `HTTPException` raise करते हैं।

---

## 🔴 Problem it Solves
Many APIs return `200 OK` for everything, even failures, and put "error" inside the JSON. Clients, browsers, proxies and monitoring tools cannot tell success from failure. Correct codes (201 for created, 404 for missing, 422 for invalid) make an API predictable and machine-readable.

## 🔴 यह क्यों बना? (Hindi)
कई APIs हर चीज़ पर `200 OK` लौटा देती हैं, failure पर भी, और JSON में "error" लिख देती हैं। तब client, browser, proxy और monitoring tools सफलता और failure में फ़र्क नहीं कर पाते। सही codes (बनने पर 201, न मिलने पर 404, गलत data पर 422) API को predictable और machine-readable बनाते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Decorator sets the success code: @app.post(..., status_code=201)
Step 2 → If your function returns normally, FastAPI sends that code
Step 3 → To fail, raise HTTPException(status_code=404, detail="...")
Step 4 → Bad input is auto-rejected by FastAPI with 422
Step 5 → Use fastapi.status constants (status.HTTP_201_CREATED) for readability
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Decorator में success code तय होता है: status_code=201
Step 2 → Function सामान्य रूप से return करे तो वही code जाता है
Step 3 → Fail करने के लिए HTTPException(status_code=404, detail="...") raise करें
Step 4 → गलत input पर FastAPI खुद 422 भेज देता है
Step 5 → पढ़ने में आसानी के लिए status.HTTP_201_CREATED जैसे constants लें
```

---

## 🟡 Real World Example
Swiggy order API: `POST /orders` returns `201 Created` with the new order id. `GET /orders/99` returns `404` if it does not exist. `DELETE /orders/5` returns `204 No Content` with an empty body. Razorpay-style rate limits return `429 Too Many Requests`. An AI chat endpoint returns `503` when the model provider is down.

## 🟡 Real Example Hindi mein
Swiggy order API में `POST /orders` नया order बनने पर `201 Created` देता है। `GET /orders/99` पर order न मिले तो `404`। `DELETE /orders/5` खाली body के साथ `204 No Content` देता है। Razorpay जैसी API rate limit पर `429 Too Many Requests` देती है। AI chat endpoint में model provider बंद हो तो `503` जाता है।

---

## 💻 Code Example — Basic
```python
# Basic status codes - run directly (pip install fastapi httpx)
from fastapi import FastAPI, HTTPException, status  # app, error class, constants
from fastapi.testclient import TestClient  # demo client
from pydantic import BaseModel  # request body model

app: FastAPI = FastAPI()  # create app
ORDERS: dict[int, str] = {1: "biryani"}  # fake database


class OrderIn(BaseModel):  # request body
    item: str  # item name


@app.post("/orders", status_code=status.HTTP_201_CREATED)  # success code is 201, not 200
def create_order(body: OrderIn) -> dict:  # create something
    new_id: int = max(ORDERS) + 1  # next id
    ORDERS[new_id] = body.item  # save
    return {"id": new_id, "item": body.item}  # body of the 201 response


@app.get("/orders/{oid}")  # default success code is 200
def get_order(oid: int) -> dict:  # read one
    if oid not in ORDERS:  # missing resource
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")  # send 404
    return {"id": oid, "item": ORDERS[oid]}  # normal 200


@app.delete("/orders/{oid}", status_code=status.HTTP_204_NO_CONTENT)  # 204 means empty body
def delete_order(oid: int) -> None:  # nothing to return
    ORDERS.pop(oid, None)  # delete if present (idempotent)


client: TestClient = TestClient(app)  # demo client
r = client.post("/orders", json={"item": "pizza"})  # create
print(r.status_code, r.json())  # 201 and the new order
# Output: 201 {'id': 2, 'item': 'pizza'}
print(client.get("/orders/99").status_code, client.get("/orders/99").json())  # missing
# Output: 404 {'detail': 'Order not found'}
print(client.post("/orders", json={}).status_code)  # missing field -> automatic validation error
# Output: 422
d = client.delete("/orders/2")  # delete
print(d.status_code, repr(d.content))  # no body at all
# Output: 204 b''
```

## 💻 Code Example — Advanced
```python
# Production style: dynamic status, custom headers on errors, status per response, docs
from fastapi import FastAPI, HTTPException, Response, status  # core pieces
from fastapi.testclient import TestClient  # demo client

app: FastAPI = FastAPI()  # app
CACHE: dict[str, str] = {}  # simple in-memory store


@app.put(  # PUT can create (201) or update (200)
    "/profiles/{name}",  # path
    responses={201: {"description": "Created"}, 200: {"description": "Updated"}},  # docs for both
)
def upsert(name: str, bio: str, response: Response) -> dict:  # Response lets us change status
    existed: bool = name in CACHE  # did we have it before?
    CACHE[name] = bio  # store it
    response.status_code = status.HTTP_200_OK if existed else status.HTTP_201_CREATED  # choose code
    return {"name": name, "bio": bio}  # body


@app.get("/secure")  # auth demo
def secure(token: str = "") -> dict:  # token from query
    if token != "abc":  # wrong token
        raise HTTPException(  # 401 should tell the client how to authenticate
            status_code=status.HTTP_401_UNAUTHORIZED,  # unauthenticated
            detail="Invalid token",  # message
            headers={"WWW-Authenticate": "Bearer"},  # standard header
        )
    return {"ok": True}  # success


@app.get("/forbidden")  # 403 demo
def forbidden() -> None:  # no return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins only")  # known user, no rights


client: TestClient = TestClient(app)  # demo client
print(client.put("/profiles/asha", params={"bio": "hi"}).status_code)  # first time
# Output: 201
print(client.put("/profiles/asha", params={"bio": "hello"}).status_code)  # second time
# Output: 200
r = client.get("/secure", params={"token": "bad"})  # wrong token
print(r.status_code, r.headers["www-authenticate"], r.json())  # 401 + header + detail
# Output: 401 Bearer {'detail': 'Invalid token'}
print(client.get("/forbidden").status_code)  # 403
# Output: 403
print(status.HTTP_422_UNPROCESSABLE_CONTENT if hasattr(status, "HTTP_422_UNPROCESSABLE_CONTENT") else 422)  # name varies by version
# Output: 422
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python (FastAPI)
@app.post("/orders", status_code=201)
def create(): ...
raise HTTPException(status_code=404, detail="Not found")
```
```javascript
// JavaScript (Express)
app.post("/orders", (req, res) => res.status(201).json({ id: 1 }));
app.get("/orders/:id", (req, res) => res.status(404).json({ detail: "Not found" }));
res.sendStatus(204);   // empty body
```

Key difference: in Express you call `res.status(...)` on every route and forget it easily (default 200). FastAPI lets you declare the success code once in the decorator, and `raise HTTPException` stops the function at once (Express needs `return res.status(...)`).

---

## 🟠 FastAPI Connection
FastAPI auto-generates 422 for validation errors and documents your declared codes in Swagger. Use `responses={...}` to document extra codes, `HTTPException` for business errors, and custom exception handlers for a uniform error format.

```python
# FastAPI: custom exception + handler returning a uniform error body
from fastapi import FastAPI, Request  # app and request
from fastapi.responses import JSONResponse  # custom response
from fastapi.testclient import TestClient  # demo client


class InsufficientBalance(Exception):  # our own domain error
    def __init__(self, needed: int) -> None:  # store data
        self.needed = needed  # how much is missing


app: FastAPI = FastAPI()  # app


@app.exception_handler(InsufficientBalance)  # map exception -> HTTP response
async def handle_balance(request: Request, exc: InsufficientBalance) -> JSONResponse:  # handler
    return JSONResponse(status_code=402, content={"error": "payment_required", "needed": exc.needed})  # 402


@app.post("/pay")  # endpoint
def pay(amount: int) -> dict:  # amount from query
    if amount > 100:  # business rule
        raise InsufficientBalance(amount - 100)  # raise domain error
    return {"paid": amount}  # success


c: TestClient = TestClient(app)  # demo client
r = c.post("/pay", params={"amount": 150})  # too much
print(r.status_code, r.json())  # handler output
# Output: 402 {'error': 'payment_required', 'needed': 50}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Returning 200 with an error message
```python
# Wrong - client thinks it succeeded
return {"error": "not found"}

# Correct
raise HTTPException(status_code=404, detail="not found")
```

❌ Mistake 2: Returning a body with 204
```python
# Wrong - 204 must have no body, servers/clients may break
@app.delete("/x", status_code=204)
def d() -> dict: return {"deleted": True}

# Correct - return None
@app.delete("/x", status_code=204)
def d() -> None: return None
```

❌ Mistake 3: Mixing up 401 and 403
```python
# Wrong - 403 for a missing/invalid token
# Correct - 401 = "who are you?" (not authenticated), 403 = "I know you, but no" (not allowed)
```

---

## 🧠 Tricky Interview Question

**Q**: What status code does the client get?

```python
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

app = FastAPI()

@app.get("/a", status_code=201)
def a():
    return {"x": 1}

@app.get("/b", status_code=201)
def b():
    raise HTTPException(status_code=404, detail="no")

@app.get("/c")
def c(n: int):
    return {"n": n}

cl = TestClient(app)
print(cl.get("/a").status_code, cl.get("/b").status_code, cl.get("/c?n=abc").status_code)
```

**Answer**:
```
201 404 422
```
The decorator code is only the code for a normal return. A raised `HTTPException` overrides it (404). `n=abc` is not an int, so FastAPI rejects the request with 422 before your function even runs.

---

## ⚫ Interview Questions + Answers

Q1: Difference between 200, 201 and 204?
A1: 200 is generic success with a body. 201 means a new resource was created (often with the new object). 204 means success with no body (typical for DELETE).

Q2: 401 vs 403?
A2: 401 Unauthorized means the client is not authenticated (missing/invalid credentials, add `WWW-Authenticate`). 403 Forbidden means authenticated but not allowed.

Q3: Why 422 and not 400 for bad input in FastAPI?
A3: 422 Unprocessable Entity means the JSON is well-formed but fails validation. FastAPI uses it with an `errors` list in `detail`. Malformed JSON gives 422 too (body parse error). Newer Starlette versions rename the constant to `HTTP_422_UNPROCESSABLE_CONTENT`.

Q4: How do you change the status code inside the function?
A4: Add a `response: Response` parameter and set `response.status_code = ...`, or return a `JSONResponse(status_code=...)` directly.

Q5: What is `HTTPException` vs a plain `raise Exception`?
A5: `HTTPException` is converted into a proper JSON response with the chosen code. A plain exception becomes a 500 Internal Server Error and may leak in logs.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Every endpoint, always set a meaningful success code (201 for create, 204 for delete)
- Raise `HTTPException` for expected business errors (404, 409, 403)
- Add `responses=` so Swagger shows error codes

❌ Avoid when:
- Using 500 for user mistakes (it is a server-fault code)
- Putting the real result only in the JSON body while keeping 200
- Returning a body with 204 or 304

---

## 📊 Visual Diagram

```
        Request
           │
   validation fails? ──yes──► 422
           │no
     your function
      │         │
  returns    raises HTTPException(404)
      │         │
 decorator    that code (404)
 status_code  + {"detail": ...}
 (200/201/204)

 1xx info | 2xx success | 3xx redirect | 4xx client error | 5xx server error
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Status code | 3-digit result number | नतीजे का 3 अंकों का code |
| 201 Created | New resource made | नया resource बन गया |
| 204 No Content | Success, empty body | सफल, body खाली |
| 401 | Not authenticated | पहचान नहीं हुई |
| 403 | Not allowed | अनुमति नहीं |
| 422 | Validation failed | Validation असफल |
| HTTPException | Error that becomes an HTTP response | HTTP जवाब बनने वाला error |

---

## ⚡ 3-Line Summary
English: Status codes tell the client the result: 2xx ok, 4xx client error, 5xx server error. Set success codes in the decorator and raise `HTTPException` for errors. FastAPI sends 422 for bad input automatically.
Hindi: Status code client को नतीजा बताता है: 2xx ठीक, 4xx client की गलती, 5xx server की गलती। Success code decorator में दें और errors के लिए `HTTPException` raise करें। गलत input पर FastAPI खुद 422 भेजता है।

---

## ➡️ Next Topic
**308. HTTP Methods** — which verb (GET, POST, PUT, PATCH, DELETE) to use with which status code.
