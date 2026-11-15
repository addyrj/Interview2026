---

# 300. Path Parameters
# हिंदी में: Path Parameters (URL के अंदर बदलने वाले हिस्से)

---

## 🔵 Simple Definition (English)
A path parameter is a variable part of the URL, written in curly braces like `/orders/{order_id}`. FastAPI passes it to your function argument with the same name and converts and validates it using the type hint (`int`, `str`, `Enum`, ...).

## 🔵 सरल परिभाषा (Hindi)
Path parameter URL का बदलने वाला हिस्सा है, जिसे `/orders/{order_id}` की तरह curly braces में लिखते हैं। FastAPI उसे उसी नाम के function argument में देता है और type hint (`int`, `str`, `Enum`, ...) से उसे बदलता और validate करता है।

---

## 🔴 Problem it Solves
REST APIs identify resources by URL: `/users/42`, `/orders/9001`. Without framework support you would split the URL string, convert to int and handle bad input by hand in every function. Path parameters do the parsing, conversion, validation and documentation automatically.

## 🔴 यह क्यों बना? (Hindi)
REST APIs में resources URL से पहचाने जाते हैं: `/users/42`, `/orders/9001`। Framework के बिना हर function में URL string को तोड़ना, int में बदलना और गलत input सँभालना पड़ता। Path parameters parsing, conversion, validation और documentation अपने-आप कर देते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Declare the route:  @app.get("/orders/{order_id}")
Step 2 → Add a function argument with the SAME name: def get_order(order_id: int)
Step 3 → Request GET /orders/42 -> FastAPI extracts "42" from the URL
Step 4 → It converts "42" to int using the hint (Pydantic does this)
Step 5 → Extra rules via Path(ge=1, le=...) are checked
Step 6 → Failure -> automatic 422 JSON error; success -> your function runs
Step 7 → Routes are matched in the order they are declared (fixed paths BEFORE dynamic)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → route घोषित करें:  @app.get("/orders/{order_id}")
Step 2 → उसी नाम का function argument लिखें: def get_order(order_id: int)
Step 3 → GET /orders/42 आने पर FastAPI URL से "42" निकालता है
Step 4 → hint के हिसाब से "42" को int में बदलता है (Pydantic करता है)
Step 5 → Path(ge=1, le=...) के अतिरिक्त नियम जाँचे जाते हैं
Step 6 → विफल -> अपने-आप 422 JSON error; सफल -> आपका function चलता है
Step 7 → routes उसी क्रम में match होते हैं जिसमें लिखे गए (fixed paths पहले, dynamic बाद में)
```

---

## 🟡 Real World Example
Swiggy's `GET /orders/{order_id}` returns tracking info for one order, and `GET /restaurants/{restaurant_id}/menu` returns a menu. `GET /orders/me` must be declared before `/orders/{order_id}`, otherwise "me" would be treated as an order id. A file server uses `/files/{file_path:path}` to accept nested paths like `invoices/2026/jan.pdf`.

## 🟡 Real Example Hindi mein
Swiggy का `GET /orders/{order_id}` एक order की tracking info देता है, और `GET /restaurants/{restaurant_id}/menu` menu देता है। `GET /orders/me` को `/orders/{order_id}` से पहले लिखना ज़रूरी है, नहीं तो "me" को order id समझ लिया जाएगा। File server `/files/{file_path:path}` से `invoices/2026/jan.pdf` जैसे nested paths लेता है।

---

## 💻 Code Example — Basic
```python
# Basic path parameters (verified: fastapi 0.162, Python 3.13)
from fastapi import FastAPI  # framework
from fastapi.testclient import TestClient  # to call the app in-process

app: FastAPI = FastAPI()  # create app


@app.get("/orders/{order_id}")  # {order_id} is the variable part
def get_order(order_id: int) -> dict[str, int]:  # same name + type hint int
    return {"order_id": order_id}  # order_id is already an int here


@app.get("/users/{name}")  # a string path parameter
def get_user(name: str) -> dict[str, str]:  # str is the default behaviour
    return {"name": name}  # returned as JSON


c: TestClient = TestClient(app)  # test client
print(c.get("/orders/42").json())  # "42" in URL -> int 42
# Output: {'order_id': 42}
r = c.get("/orders/abc")  # not a number
print(r.status_code, r.json()["detail"][0]["msg"])  # automatic validation error
# Output: 422 Input should be a valid integer, unable to parse string as an integer
print(c.get("/orders/3.5").status_code)  # float text is not a valid int either
# Output: 422
print(c.get("/users/asha").json())  # strings need no conversion
# Output: {'name': 'asha'}
```

## 💻 Code Example — Advanced
```python
# Production style: Path() validation, Enum, :path converter, route order (verified)
from enum import Enum  # fixed set of allowed values
from typing import Annotated  # modern way to attach metadata to hints
from fastapi import FastAPI, Path  # Path adds rules + docs
from fastapi.testclient import TestClient  # in-process client

app: FastAPI = FastAPI()  # application


class Status(str, Enum):  # str mixin so values are strings in JSON
    placed = "placed"  # allowed value 1
    delivered = "delivered"  # allowed value 2


@app.get("/orders/me")  # FIXED path: must come BEFORE /orders/{order_id}
def me() -> dict[str, str]:
    return {"order": "current user's"}  # special route


@app.get("/orders/{order_id}")  # dynamic path
def get_order(
    order_id: Annotated[int, Path(ge=1, le=1_000_000, description="Order id")],  # 1..1,000,000
) -> dict[str, int]:
    return {"order_id": order_id}  # only valid ids reach here


@app.get("/status/{status}")  # only "placed" or "delivered" allowed
def by_status(status: Status) -> dict[str, str]:
    return {"status": status.value}  # use .value to get the plain string


@app.get("/files/{file_path:path}")  # :path allows slashes inside the value
def files(file_path: str) -> dict[str, str]:
    return {"file_path": file_path}  # 'a/b/c.txt' arrives as a single string


c: TestClient = TestClient(app)  # client
print(c.get("/orders/me").json())  # fixed route wins because it is declared first
# Output: {'order': "current user's"}
r = c.get("/orders/0")  # violates ge=1
print(r.status_code, r.json()["detail"][0]["msg"])
# Output: 422 Input should be greater than or equal to 1
print(c.get("/status/placed").json())  # valid enum value
# Output: {'status': 'placed'}
r = c.get("/status/lost")  # not in the enum
print(r.status_code, r.json()["detail"][0]["msg"])
# Output: 422 Input should be 'placed' or 'delivered'
print(c.get("/files/a/b/c.txt").json())  # slashes preserved
# Output: {'file_path': 'a/b/c.txt'}
```

---

## 🟠 JavaScript vs Python Comparison
Express uses `:id` and gives you strings. FastAPI uses `{id}` and gives you the correct type.

```python
# Python (FastAPI): typed and validated
@app.get("/orders/{order_id}")
def get_order(order_id: int) -> dict[str, int]:
    return {"order_id": order_id}     # already an int
```
```javascript
// JavaScript (Express): always a string, you validate manually
app.get('/orders/:orderId', (req, res) => {
  const id = Number(req.params.orderId);          // convert yourself
  if (!Number.isInteger(id) || id < 1) {
    return res.status(400).json({ error: 'bad id' });   // write error handling yourself
  }
  res.json({ order_id: id });
});
```

Key differences: Express has no built-in conversion/validation (you add Joi/zod). FastAPI returns a standard 422 with field location and error type for free. Also: Express route order matters the same way as in FastAPI.

---

## 🟠 FastAPI Connection
Path parameters identify one resource (`/users/{user_id}`), while query parameters filter or paginate collections (`/users?page=2`). In real services the path parameter usually feeds a dependency that loads the object and raises 404 if missing.

```python
# FastAPI: path param + dependency + 404 (needs: pip install fastapi)
from fastapi import Depends, FastAPI, HTTPException  # core pieces

app: FastAPI = FastAPI()  # app
DB: dict[int, str] = {1: "Asha", 2: "Ravi"}  # fake database


def get_user_or_404(user_id: int) -> str:  # path param is auto-wired into a dependency
    if user_id not in DB:  # not found
        raise HTTPException(status_code=404, detail="User not found")  # proper HTTP error
    return DB[user_id]  # found


@app.get("/users/{user_id}")  # same name user_id feeds the dependency
def read_user(name: str = Depends(get_user_or_404)) -> dict[str, str]:
    return {"name": name}  # handler stays tiny
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Argument name differs from the braces
✅ Correct: Names must match. Otherwise FastAPI treats the argument as a query parameter and the path param is missing.

```python
# Wrong: {order_id} in URL but the function says id
@app.get("/orders/{order_id}")
def get_order(id: int): ...        # id is expected as ?id=... (query), so requests fail with 422
# Right
def get_order(order_id: int): ...
```

❌ Mistake 2: Declaring the dynamic route before the fixed one
✅ Correct: Put `/orders/me` above `/orders/{order_id}`.

```python
# Wrong: "me" is matched by {order_id} -> 422 "unable to parse string as an integer"
@app.get("/orders/{order_id}")
def a(order_id: int): ...
@app.get("/orders/me")      # never reached
def b(): ...
# Right: declare /orders/me first
```

❌ Mistake 3: Expecting a path value with slashes to work with `str`
✅ Correct: Use `{name:path}` for values that contain `/`. Also do not put secrets or personal data in URLs; they appear in logs.

---

## 🧠 Tricky Interview Question

**Q**: Given the code below, what do `GET /orders/me` and `GET /orders/me2` return?

```python
@app.get("/orders/{order_id}")
def get_order(order_id: int): return {"order_id": order_id}

@app.get("/orders/me")
def me(): return {"order": "mine"}
```

**Answer**:
```
GET /orders/me  -> 422  (the dynamic route is first, "me" cannot be an int; /orders/me is never reached)
GET /orders/me2 -> 422  (same reason)
```
FastAPI matches routes in declaration order. The first route matches any string in that segment, validation fails, and FastAPI does not "fall back" to the next route. Fix: declare `/orders/me` first. (Verified in the correct order, `/orders/me` returns `{'order': "current user's"}`.)

---

## ⚫ Interview Questions + Answers

Q1: How does FastAPI know a function argument is a path parameter?
A1: Its name appears in the route path in curly braces. Arguments not in the path are query parameters (or body, if they are Pydantic models).

Q2: How do you restrict a path parameter to certain values?
A2: Use an `Enum` type (a bad value gives 422) or `Literal["a", "b"]`.

Q3: How do you add validation rules and docs to a path parameter?
A3: `Annotated[int, Path(ge=1, le=100, description="...")]`. Path parameters are always required, so they cannot have defaults.

Q4: How can a path parameter contain slashes?
A4: `/files/{file_path:path}` (Starlette's `path` convertor).

Q5: What status code is returned for a bad path parameter?
A5: 422 Unprocessable Content with a JSON body listing `loc`, `msg`, `type` for each error. (If the route itself doesn't exist it is 404.)

---

## 🔷 When to Use + When Not to Use

✅ Use path parameters for:
- Identifying one specific resource (`/users/{id}`, `/orders/{id}/items/{item_id}`)
- Mandatory, hierarchical information

❌ Avoid path parameters for:
- Optional filters, sorting, pagination (use query parameters)
- Large or sensitive data (use the request body or headers)

---

## 📊 Visual Diagram

```
 URL:    /orders/42
 Route:  /orders/{order_id}
                    │
                    ▼  "42" (string from URL)
            Pydantic: int("42") ──► 42   (fails -> 422)
                    │
                    ▼
        def get_order(order_id: int)   -> {"order_id": 42}

 Order of declaration:   /orders/me   (checked first)
                         /orders/{order_id}
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Path parameter | Variable part of URL | URL का बदलने वाला हिस्सा |
| Path() | Adds validation and docs to it | validation और docs जोड़ता है |
| Enum | Fixed set of allowed values | तय मान वाला समूह |
| :path convertor | Allows slashes in the value | value में slash की अनुमति |
| 422 | Validation error status | validation error का status |
| Resource | Thing identified by URL | URL से पहचानी जाने वाली चीज़ |

---

## ⚡ 3-Line Summary
English: Write `{name}` in the route and a same-named argument in the function; the type hint converts and validates it. Use `Path()` for rules, `Enum` for fixed values and `:path` for slashes. Declare fixed routes before dynamic ones.
Hindi: Route में `{name}` और function में उसी नाम का argument लिखें; type hint उसे बदलता और validate करता है। नियमों के लिए `Path()`, तय मानों के लिए `Enum` और slash के लिए `:path` इस्तेमाल करें। Fixed routes को dynamic routes से पहले लिखें।

---

## ➡️ Next Topic
**301. Query Parameters** — filters, pagination and optional values after the `?` in the URL.
