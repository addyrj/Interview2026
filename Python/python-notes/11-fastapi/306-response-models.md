---

# 306. Response Models
# हिंदी में: Response Models (API का जवाब कैसा दिखेगा)

---

## 🔵 Simple Definition (English)
A response model is a Pydantic class that describes the shape of the data your endpoint sends back. FastAPI filters, validates and documents the output using it. Fields that are not in the model (like `password`) are never sent.

## 🔵 सरल परिभाषा (Hindi)
Response model एक Pydantic class है जो बताती है कि endpoint का जवाब कैसा दिखेगा। FastAPI इसी से output को filter, validate और document करता है। जो field model में नहीं है (जैसे `password`) वह client को कभी नहीं जाती।

---

## 🔴 Problem it Solves
Without a response model you return whatever object you have, such as a full database row. That leaks secrets (password hash, internal flags), breaks when a field is renamed, and the docs show nothing useful. A response model gives one contract for the output: safe, validated and visible in Swagger.

## 🔴 यह क्यों बना? (Hindi)
Response model के बिना आप जो भी object हो वही लौटा देते हैं, जैसे पूरी database row। इससे password hash जैसी secret चीज़ें leak होती हैं, field का नाम बदलने पर client टूट जाता है और docs में कुछ साफ़ नहीं दिखता। Response model output का एक पक्का contract देता है: सुरक्षित, validated और Swagger में दिखने वाला।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You declare response_model=UserOut (or a return type -> UserOut)
Step 2 → Your function returns a dict, ORM object or model
Step 3 → FastAPI validates that data against UserOut
Step 4 → Extra fields are dropped, missing required fields raise an error
Step 5 → The result is converted to JSON and the schema goes to /docs
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → आप response_model=UserOut (या return type -> UserOut) लिखते हैं
Step 2 → आपका function dict, ORM object या model लौटाता है
Step 3 → FastAPI उस data को UserOut से validate करता है
Step 4 → अतिरिक्त fields हट जाती हैं, ज़रूरी field गायब हो तो error
Step 5 → नतीजा JSON बनकर जाता है और schema /docs में दिखता है
```

---

## 🟡 Real World Example
Zomato signup API: the request has `email` and `password`, but the response must return only `id`, `name`, `email`. The DB row also holds `hashed_password` and `is_admin`. A `UserOut` response model guarantees those two never leave the server. Razorpay style APIs also use different models for "list" (short) and "detail" (long) responses.

## 🟡 Real Example Hindi mein
Zomato signup API में request में `email` और `password` आता है, पर response में सिर्फ `id`, `name`, `email` जाना चाहिए। DB row में `hashed_password` और `is_admin` भी होते हैं। `UserOut` response model पक्का करता है कि ये दोनों server से बाहर न जाएँ। Razorpay जैसी APIs "list" (छोटा) और "detail" (पूरा) response के लिए अलग models रखती हैं।

---

## 💻 Code Example — Basic
```python
# Basic response_model example - run directly (pip install fastapi httpx)
from fastapi import FastAPI  # the web framework
from fastapi.testclient import TestClient  # in-process HTTP client for demos
from pydantic import BaseModel  # base class for data models

app: FastAPI = FastAPI()  # create the application


class UserIn(BaseModel):  # what the client SENDS
    name: str  # user name
    email: str  # user email
    password: str  # secret, must never be returned


class UserOut(BaseModel):  # what the client RECEIVES
    id: int  # generated id
    name: str  # same name
    email: str  # same email


@app.post("/users", response_model=UserOut)  # output is filtered by UserOut
def create_user(user: UserIn) -> dict:  # return a dict that has MORE fields
    return {"id": 1, **user.model_dump()}  # includes password on purpose


client: TestClient = TestClient(app)  # client bound to our app
resp = client.post("/users", json={"name": "Asha", "email": "a@x.com", "password": "s3cret"})  # call API
print(resp.status_code)  # HTTP status
# Output: 200
print(resp.json())  # password was filtered out
# Output: {'id': 1, 'name': 'Asha', 'email': 'a@x.com'}

schema = app.openapi()["paths"]["/users"]["post"]["responses"]["200"]  # what Swagger will show
print(schema["content"]["application/json"]["schema"])  # reference to UserOut
# Output: {'$ref': '#/components/schemas/UserOut'}
```

## 💻 Code Example — Advanced
```python
# Production style: return annotation, list, exclude_unset, ORM mode, validation error
from typing import Optional  # for optional fields
from fastapi import FastAPI  # framework
from fastapi.testclient import TestClient  # demo client
from pydantic import BaseModel, ConfigDict  # model and config

app: FastAPI = FastAPI()  # application


class UserDB:  # pretend ORM object (not a dict, not a pydantic model)
    def __init__(self, id: int, name: str, hashed_password: str, nickname: Optional[str] = None) -> None:
        self.id = id  # primary key
        self.name = name  # display name
        self.hashed_password = hashed_password  # secret
        self.nickname = nickname  # optional field


class UserOut(BaseModel):  # public representation
    model_config = ConfigDict(from_attributes=True)  # allow reading from object attributes
    id: int  # id
    name: str  # name
    nickname: Optional[str] = None  # optional with default


DB: list[UserDB] = [UserDB(1, "Asha", "hash1"), UserDB(2, "Ravi", "hash2", "rv")]  # fake table


@app.get("/users")  # no response_model argument needed
def list_users() -> list[UserOut]:  # the return annotation IS the response model
    return DB  # type: ignore[return-value]  # ORM objects are converted via from_attributes


@app.get("/users/{uid}", response_model=UserOut, response_model_exclude_none=True)  # drop None values
def get_user(uid: int) -> UserDB:  # annotation is the ORM class, so we pass response_model explicitly
    return DB[uid - 1]  # return the ORM object


@app.get("/compact", response_model=UserOut, response_model_exclude_unset=True)  # only fields we set
def compact() -> dict:  # a plain dict
    return {"id": 9, "name": "Zed"}  # nickname is not set, so it is omitted


@app.get("/bad", response_model=UserOut)  # response that violates the contract
def bad() -> dict:  # dict is missing the required "name"
    return {"id": 5}  # invalid on purpose


client: TestClient = TestClient(app, raise_server_exceptions=False)  # do not re-raise, give us the 500
print(client.get("/users").json())  # list of UserOut
# Output: [{'id': 1, 'name': 'Asha', 'nickname': None}, {'id': 2, 'name': 'Ravi', 'nickname': 'rv'}]
print(client.get("/users/1").json())  # nickname is None so it is dropped
# Output: {'id': 1, 'name': 'Asha'}
print(client.get("/compact").json())  # only set fields
# Output: {'id': 9, 'name': 'Zed'}
print(client.get("/bad").status_code)  # server bug becomes a 500, bad data never reaches client
# Output: 500
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python (FastAPI): the model filters automatically
class UserOut(BaseModel):
    id: int
    name: str

@app.get("/me", response_model=UserOut)
def me() -> dict:
    return {"id": 1, "name": "Asha", "password": "x"}  # password is dropped
```
```javascript
// JavaScript (Express): you filter by hand (or use a library like zod / class-transformer)
app.get("/me", (req, res) => {
  const user = { id: 1, name: "Asha", password: "x" };
  const { password, ...safe } = user;   // manual omit, easy to forget
  res.json(safe);
});
```

Key difference: in Express nothing stops you from sending `password`. In FastAPI the response model is a whitelist, so unknown fields never leave. It also feeds the OpenAPI docs for free, similar to TypeScript types plus runtime validation.

---

## 🟠 FastAPI Connection
Almost every real endpoint pairs an input model (`UserCreate`) with an output model (`UserOut`) and uses `response_model` or the return annotation. Variants: `response_model=list[UserOut]`, `response_model_exclude_none`, `response_model_exclude_unset`, and `response_model=None` to disable filtering (for example when returning a `Response` directly).

```python
# FastAPI: separate create/read models + disabling the response model
from fastapi import FastAPI  # framework
from fastapi.responses import PlainTextResponse  # raw response
from fastapi.testclient import TestClient  # demo client
from pydantic import BaseModel  # models

app: FastAPI = FastAPI()  # app


class Item(BaseModel):  # public item
    name: str  # item name
    price: float  # price


@app.get("/items/{n}", response_model=Item)  # validated and filtered
def get_item(n: int) -> dict:  # returns extra field "cost_price"
    return {"name": f"item{n}", "price": 9.5, "cost_price": 4.0}  # cost_price stays private


@app.get("/ping", response_model=None)  # no filtering, we return a Response ourselves
def ping() -> PlainTextResponse:  # custom response class
    return PlainTextResponse("pong")  # plain text body


client: TestClient = TestClient(app)  # demo client
print(client.get("/items/3").json())  # cost_price removed
# Output: {'name': 'item3', 'price': 9.5}
print(client.get("/ping").text)  # raw text
# Output: pong
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Returning the DB/input model that contains the password
```python
# Wrong - same model for input and output leaks the password
@app.post("/users", response_model=UserIn)
def create(user: UserIn) -> UserIn: return user

# Correct - separate output model
@app.post("/users", response_model=UserOut)
def create(user: UserIn) -> dict: return {"id": 1, **user.model_dump()}
```

✅ Correct: always keep `UserCreate`, `UserOut` (and `UserInDB`) as separate classes.

❌ Mistake 2: Using a non-dict ORM object without `from_attributes=True`
```python
# Wrong - Pydantic cannot read attributes of a plain class, validation error (500)
class UserOut(BaseModel):
    id: int

# Correct - tell Pydantic to read attributes
class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # (orm_mode in Pydantic v1)
    id: int
```

❌ Mistake 3: Expecting `response_model_exclude_unset` to hide `None`
```python
# Wrong assumption - a field set to None explicitly is still "set"
# Correct - use response_model_exclude_none=True to drop None values
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class Out(BaseModel):
    a: int
    b: Optional[int] = None

@app.get("/x", response_model=Out)
def x() -> dict:
    return {"a": 1, "c": 3}

@app.get("/y", response_model=Out, response_model_exclude_unset=True)
def y() -> dict:
    return {"a": 1, "b": None}

c = TestClient(app)
print(c.get("/x").json())
print(c.get("/y").json())
```

**Answer**:
```
{'a': 1, 'b': None}
{'a': 1, 'b': None}
```
In `/x` the extra key `c` is dropped and `b` takes its default `None`. In `/y` we explicitly passed `b=None`, so it counts as "set" and stays in the output. `exclude_unset` only removes fields that were never provided.

---

## ⚫ Interview Questions + Answers

Q1: What does `response_model` do?
A1: It validates and filters the returned data against a Pydantic type, drops extra fields, converts to JSON and documents the response in OpenAPI.

Q2: `response_model=` vs a return type annotation?
A2: Both work. If both are present, `response_model` wins. The annotation lets editors and type checkers see the real type, and is the modern style. Use `response_model=` when the function returns something different (an ORM object or `dict`).

Q3: How do you hide the password in a response?
A3: Use a separate output model without the password field (a whitelist). `response_model_exclude={"password"}` also works, but a separate model is safer.

Q4: What happens when the returned data does not match the model?
A4: FastAPI raises `ResponseValidationError`, the client gets a 500 Internal Server Error and the bad data is never sent. This is a server bug, not a client bug.

Q5: How do you return a raw `Response` without filtering?
A5: Return a `Response` subclass directly (FastAPI skips validation), and use `response_model=None` if the annotation would otherwise be treated as a model.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any JSON endpoint, to hide internal fields
- You want clear Swagger docs for responses
- You return ORM objects (with `from_attributes=True`)

❌ Avoid when:
- You return a `Response`, `StreamingResponse` or `FileResponse` (set `response_model=None`)
- Huge payloads where validation cost matters (use a lightweight model or return `Response` with pre-built JSON)

---

## 📊 Visual Diagram

```
 Client ── POST {name,email,password} ──► UserIn (validate input)
                                              │
                                      your function
                                              │ returns {id,name,email,password}
                                              ▼
                                  UserOut  (response_model)
                                   keeps only id, name, email
                                              │
 Client ◄── {id, name, email} ───────────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| response_model | Model that shapes the output | output का आकार तय करने वाला model |
| Filtering | Dropping fields not in the model | model में न होने वाली fields हटाना |
| from_attributes | Read data from object attributes | object के attributes से data पढ़ना |
| exclude_unset | Omit fields never provided | जो fields दी ही नहीं गईं उन्हें हटाना |
| exclude_none | Omit fields equal to None | None वाली fields हटाना |
| Serialization | Converting model to JSON | model को JSON में बदलना |

---

## ⚡ 3-Line Summary
English: A response model is a Pydantic class that controls what an endpoint returns. It filters secret or extra fields, validates the output and builds the docs. Use separate input and output models.
Hindi: Response model एक Pydantic class है जो तय करती है कि endpoint क्या लौटाएगा। यह secret या अतिरिक्त fields हटाती है, output validate करती है और docs बनाती है। Input और output के लिए अलग models रखें।

---

## ➡️ Next Topic
**307. Status Codes in FastAPI** — after shaping the body, learn to set the right HTTP status (201, 204, 404...).
