---

# 302. Request Body (Pydantic)
# हिंदी में: Request Body (Pydantic models से JSON लेना)

---

## 🔵 Simple Definition (English)
A request body is the JSON data a client sends with POST, PUT or PATCH. In FastAPI you describe its shape with a Pydantic model and use it as a function argument. FastAPI reads the JSON, validates every field, converts types, and gives you a ready Python object.

## 🔵 सरल परिभाषा (Hindi)
Request body वह JSON data है जो client POST, PUT या PATCH के साथ भेजता है। FastAPI में आप उसका आकार Pydantic model से बताते हैं और उसे function argument बनाते हैं। FastAPI JSON पढ़ता है, हर field validate करता है, types बदलता है और आपको तैयार Python object देता है।

---

## 🔴 Problem it Solves
Without models you read `await request.json()` and get a raw dict: you must check each key exists, check types, check nested values and write error messages. Missing one check causes crashes or bad data in the database. A Pydantic model does all of it declaratively and also produces schema documentation.

## 🔴 यह क्यों बना? (Hindi)
Models के बिना `await request.json()` से कच्चा dict मिलता है: हर key की मौजूदगी, type, nested मान जाँचना और error messages लिखना खुद करना पड़ता है। एक भी जाँच छूटे तो crash या database में खराब data आता है। Pydantic model यह सब declarative तरीके से करता है और schema documentation भी बनाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define a class that extends pydantic.BaseModel with typed fields
Step 2 → Use it as a function parameter:  def create(order: OrderIn)
Step 3 → Client sends POST with header Content-Type: application/json and a JSON body
Step 4 → FastAPI parses the JSON (invalid JSON -> 422 json_invalid)
Step 5 → Pydantic validates fields, nested models, lists, constraints (Field)
Step 6 → Errors -> 422 listing every bad field; success -> `order` is a model instance
Step 7 → Return a dict/model; FastAPI serializes it to JSON (use response_model to filter)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → pydantic.BaseModel को extend करने वाली class बनाएँ, typed fields के साथ
Step 2 → उसे function parameter बनाएँ:  def create(order: OrderIn)
Step 3 → Client Content-Type: application/json header और JSON body के साथ POST भेजता है
Step 4 → FastAPI JSON parse करता है (गलत JSON -> 422 json_invalid)
Step 5 → Pydantic fields, nested models, lists, constraints (Field) validate करता है
Step 6 → गलती -> सभी खराब fields की सूची के साथ 422; सही -> `order` एक model instance है
Step 7 → dict/model लौटाएँ; FastAPI JSON बनाता है (छानने के लिए response_model)
```

---

## 🟡 Real World Example
A Swiggy order creation call: `POST /orders` with JSON containing a list of items (name, price, quantity), a delivery address (city, 6-digit pin) and an optional note. One model defines it. If the PIN is `41` or an item price is negative, the client gets a clear 422 listing exactly which fields are wrong, and the database is never touched.

## 🟡 Real Example Hindi mein
Swiggy का order बनाने वाला call: `POST /orders` जिसमें items की list (नाम, कीमत, मात्रा), delivery address (शहर, 6 अंकों का pin) और वैकल्पिक note वाला JSON होता है। एक model यह सब परिभाषित करता है। PIN `41` हो या कीमत negative हो तो client को साफ 422 मिलता है जिसमें ठीक वही fields बताए जाते हैं, और database छुआ भी नहीं जाता।

---

## 💻 Code Example — Basic
```python
# Basic request body (verified: fastapi 0.162, pydantic 2.14, Python 3.13)
from fastapi import FastAPI  # framework
from fastapi.testclient import TestClient  # in-process client
from pydantic import BaseModel  # base class for models

app: FastAPI = FastAPI()  # create app


class Item(BaseModel):  # describes the JSON body
    name: str  # required string
    price: float  # required number
    qty: int = 1  # optional, default 1


@app.post("/items", status_code=201)  # POST with 201 Created
def create_item(item: Item) -> dict[str, object]:  # a model parameter = request body
    return {"name": item.name, "total": item.price * item.qty}  # use attributes, not dict keys


c: TestClient = TestClient(app)  # client
r = c.post("/items", json={"name": "pizza", "price": 250.5, "qty": 2})  # valid JSON body
print(r.status_code, r.json())  # created
# Output: 201 {'name': 'pizza', 'total': 501.0}
r = c.post("/items", json={"name": "tea"})  # price is missing
print(r.status_code, r.json()["detail"][0]["loc"], r.json()["detail"][0]["type"])
# Output: 422 ['body', 'price'] missing
```

## 💻 Code Example — Advanced
```python
# Production style: nested models, constraints, errors, body + path + extra Body field (verified)
from typing import Annotated  # for Body() metadata
from fastapi import Body, FastAPI  # framework + Body
from fastapi.testclient import TestClient  # client
from pydantic import BaseModel, Field  # model + constraints

app: FastAPI = FastAPI()  # app


class Item(BaseModel):  # one order line
    name: str = Field(min_length=1)  # not empty
    price: float = Field(gt=0)  # strictly positive
    qty: int = 1  # default quantity


class Address(BaseModel):  # nested object
    city: str
    pin: str = Field(pattern=r"^\d{6}$")  # exactly 6 digits


class OrderIn(BaseModel):  # the full request body
    items: list[Item]  # list of nested models
    address: Address  # nested model
    note: str | None = None  # optional


@app.post("/orders", status_code=201)  # create
def create(order: OrderIn) -> dict[str, object]:
    total: float = sum(i.price * i.qty for i in order.items)  # business logic on typed data
    return {"total": total, "city": order.address.city, "note": order.note}


@app.put("/orders/{oid}")  # path param + body model + extra body value
def update(oid: int, order: OrderIn, priority: Annotated[int, Body()] = 0) -> dict[str, int]:
    return {"oid": oid, "priority": priority, "n": len(order.items)}  # two body parts -> embedded


c: TestClient = TestClient(app)  # client
good = {  # valid payload; note price "40" is a string -> converted to float
    "items": [{"name": "pizza", "price": 250.5, "qty": 2}, {"name": "coke", "price": "40"}],
    "address": {"city": "Pune", "pin": "411001"},
}
r = c.post("/orders", json=good)  # send
print(r.status_code, r.json())  # 250.5*2 + 40*1 = 541.0
# Output: 201 {'total': 541.0, 'city': 'Pune', 'note': None}

bad = {"items": [{"name": "", "price": -1}], "address": {"city": "Pune", "pin": "41"}}  # 3 errors
r = c.post("/orders", json=bad)  # send bad data
print(r.status_code)  # all errors are reported together
# Output: 422
for e in r.json()["detail"]:  # each error has loc, type, msg
    print(e["loc"], e["type"])  # where and why
# Output:
# ['body', 'items', 0, 'name'] string_too_short
# ['body', 'items', 0, 'price'] greater_than
# ['body', 'address', 'pin'] string_pattern_mismatch

print(c.post("/orders", content="not json", headers={"content-type": "application/json"}).json()["detail"][0]["type"])
# Output: json_invalid
print(c.post("/orders").json()["detail"][0]["type"])  # no body at all
# Output: missing
r = c.put("/orders/5", json={"order": good, "priority": 3})  # two body params -> keys "order" and "priority"
print(r.status_code, r.json())
# Output: 200 {'oid': 5, 'priority': 3, 'n': 2}
```

---

## 🟠 JavaScript vs Python Comparison
In Express you add `express.json()` and read `req.body`, but nothing validates it unless you add zod/Joi. A Pydantic model is like a zod schema that is also the TypeScript type and the API docs.

```python
# Python (FastAPI + Pydantic)
class Item(BaseModel):
    name: str
    price: float

@app.post("/items")
def create(item: Item) -> Item:
    return item                      # validated, typed, documented
```
```javascript
// JavaScript (Express + zod)
const Item = z.object({ name: z.string(), price: z.number() });

app.post('/items', express.json(), (req, res) => {
  const parsed = Item.safeParse(req.body);              // manual step
  if (!parsed.success) return res.status(400).json(parsed.error);
  res.json(parsed.data);
});
```

Key differences: JS needs a separate validation library and manual error replies; FastAPI wires Pydantic into the request cycle and returns a standard 422. Also, FastAPI does not use `express.json()`: body parsing is automatic.

---

## 🟠 FastAPI Connection
FastAPI uses three models per resource in production: `OrderCreate` (input), `OrderUpdate` (partial input), `OrderOut` (output without secret fields). With `response_model`, extra fields like `password_hash` never leak.

```python
# FastAPI: input model vs output model (needs: pip install fastapi pydantic)
from fastapi import FastAPI  # framework
from pydantic import BaseModel, Field  # models

app: FastAPI = FastAPI()  # app


class UserCreate(BaseModel):  # what the client sends
    email: str
    password: str = Field(min_length=8)  # never returned


class UserOut(BaseModel):  # what the client receives
    id: int
    email: str


@app.post("/users", response_model=UserOut, status_code=201)  # output is filtered by UserOut
def create_user(user: UserCreate) -> dict[str, object]:
    return {"id": 1, "email": user.email, "password": user.password}  # password is dropped
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Sending form data or wrong Content-Type and expecting JSON parsing
✅ Correct: Send `Content-Type: application/json` with valid JSON. With `requests`/`httpx` use `json=...`, not `data=...`.

```python
# Wrong
httpx.post(url, data={"name": "tea"})       # sent as form data -> 422
# Right
httpx.post(url, json={"name": "tea", "price": 10})
```

❌ Mistake 2: Using a body with GET, or using `dict` as the body type
✅ Correct: Use POST/PUT/PATCH for bodies, and a Pydantic model instead of a bare `dict` (a dict accepts anything, so no validation or docs).

```python
# Wrong
@app.post("/x")
def x(data: dict): ...          # anything goes; no schema in docs
# Right
@app.post("/x")
def x(data: Item): ...
```

❌ Mistake 3: Mutable defaults and returning the input model with secrets
✅ Correct: Use `Field(default_factory=list)` for list defaults, and `response_model` for output so secrets are not returned.

```python
# Wrong
class A(BaseModel):
    tags: list[str] = []            # Pydantic copies it safely, but be explicit
# Right
class A(BaseModel):
    tags: list[str] = Field(default_factory=list)
```

---

## 🧠 Tricky Interview Question

**Q**: A route has two body parameters. What JSON must the client send?

```python
@app.put("/orders/{oid}")
def update(oid: int, order: OrderIn, priority: Annotated[int, Body()] = 0): ...
```

**Answer**:
```json
{"order": { "items": [...], "address": {...} }, "priority": 3}
```
With exactly one body model, the JSON is the model itself. With two or more body parameters, FastAPI "embeds" them: each parameter name becomes a key. Sending the flat `OrderIn` JSON here would give 422 (field `order` missing). You can force embedding for one parameter with `Body(embed=True)`. (Verified: returns `200 {'oid': 5, 'priority': 3, 'n': 2}`.)

---

## ⚫ Interview Questions + Answers

Q1: How does FastAPI know a parameter is the request body?
A1: When its type is a Pydantic model (or `Body()` is used). Simple types are query parameters, names in the path are path parameters.

Q2: Which HTTP status for invalid body data?
A2: 422 Unprocessable Content, with a `detail` list of errors, each with `loc`, `msg` and `type`. Invalid JSON syntax is also 422 (`json_invalid`).

Q3: How do you make a field optional?
A3: Give it a default, e.g. `note: str | None = None`. Without a default it is required, even when its type allows `None` (Pydantic v2).

Q4: How do you read the body as a dict?
A4: `order.model_dump()` (Pydantic v2). The old `.dict()` is deprecated.

Q5: How do you accept raw bytes or a file?
A5: Use `Request` and `await request.body()`, or `UploadFile` for multipart file uploads (needs `python-multipart`).

---

## 🔷 When to Use + When Not to Use

✅ Use a request body for:
- Creating or updating resources (POST, PUT, PATCH)
- Nested or large structured data

❌ Avoid when:
- Simple filters on GET (use query parameters)
- Uploading large files in JSON (use multipart or direct upload to object storage)

---

## 📊 Visual Diagram

```
 Client                          FastAPI
 POST /orders  {JSON}  ───────►  1. parse JSON       (fail -> json_invalid)
                                 2. OrderIn.model_validate(...)
                                      ├─ items: list[Item]  ─ each Item validated
                                      ├─ address: Address   ─ pin matches ^\d{6}$
                                      └─ note: optional
                                 3. errors? ──► 422 with every bad field
                                 4. ok     ──► create(order: OrderIn) runs
                                 5. return value ──► JSON (filtered by response_model)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Request body | Data sent inside the request | request के अंदर भेजा data |
| BaseModel | Pydantic class that validates data | validate करने वाली Pydantic class |
| Field() | Adds constraints to a model field | field पर सीमाएँ लगाता है |
| Nested model | Model inside another model | model के अंदर model |
| Embed | Wrap body parts under their names | body हिस्सों को उनके नाम से रखना |
| response_model | Output schema that filters the reply | reply को छानने वाला output schema |

---

## ⚡ 3-Line Summary
English: Declare a Pydantic model and use it as a parameter to read and validate JSON bodies. Errors come back as a detailed 422 listing every bad field. Use separate input and output models so secrets never leak.
Hindi: JSON body पढ़ने और validate करने के लिए Pydantic model बनाकर उसे parameter की तरह इस्तेमाल करें। गलतियाँ हर खराब field की सूची के साथ विस्तृत 422 में आती हैं। Input और output के लिए अलग models रखें ताकि secrets लीक न हों।

---

## ➡️ Next Topic
**303. Pydantic** (already covered), then **304. Pydantic Validators** — custom rules with `field_validator` and `model_validator`.
