---

# 301. Query Parameters
# हिंदी में: Query Parameters (URL में ? के बाद वाले मान)

---

## 🔵 Simple Definition (English)
Query parameters are the key=value pairs after `?` in a URL, like `/search?q=pizza&page=2`. In FastAPI, any function argument that is not in the path and not a Pydantic body model is read as a query parameter, converted by its type hint, and validated with `Query()` rules.

## 🔵 सरल परिभाषा (Hindi)
Query parameters URL में `?` के बाद आने वाले key=value जोड़े हैं, जैसे `/search?q=pizza&page=2`। FastAPI में जो function argument path में नहीं है और Pydantic body model भी नहीं है, वह query parameter माना जाता है, type hint से बदला जाता है और `Query()` के नियमों से validate होता है।

---

## 🔴 Problem it Solves
List endpoints need optional filters, sorting and pagination. Without a framework you parse `request.url.query`, convert types, apply defaults, check ranges and return errors manually. Query parameters let you declare all that in the function signature, and the docs show them automatically.

## 🔴 यह क्यों बना? (Hindi)
List endpoints को वैकल्पिक filters, sorting और pagination चाहिए। Framework के बिना `request.url.query` को parse करना, types बदलना, defaults लगाना, range जाँचना और errors लौटाना खुद करना पड़ता। Query parameters में यह सब function signature में घोषित हो जाता है, और docs में अपने-आप दिखता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Declare function arguments that are NOT in the route path
Step 2 → No default value  -> required;  default value  -> optional
Step 3 → Request: GET /search?q=pizza&page=2
Step 4 → FastAPI reads each name from the query string
Step 5 → Converts by type hint: "2" -> int, "yes"/"true"/"1" -> bool, repeated key -> list
Step 6 → Query(min_length, ge, le, pattern ...) applies extra validation
Step 7 → Errors -> 422 with loc ["query", "<name>"]; unknown extra params are ignored
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → वे function arguments लिखें जो route path में नहीं हैं
Step 2 → default नहीं -> ज़रूरी;  default है -> वैकल्पिक
Step 3 → Request: GET /search?q=pizza&page=2
Step 4 → FastAPI query string से हर नाम पढ़ता है
Step 5 → hint से बदलता है: "2" -> int, "yes"/"true"/"1" -> bool, दोहराई key -> list
Step 6 → Query(min_length, ge, le, pattern ...) अतिरिक्त validation करता है
Step 7 → error -> 422 जिसमें loc ["query", "<name>"]; अनजाने extra params अनदेखे रहते हैं
```

---

## 🟡 Real World Example
A Zomato-style search: `GET /search?q=biryani&veg=true&sort=rating&page=2&size=20&tags=spicy&tags=cheap`. The server validates that `q` has at least 2 characters, `size` is at most 100 (so nobody requests a million rows), `sort` is one of two values, and `tags` can repeat to form a list.

## 🟡 Real Example Hindi mein
Zomato जैसी search: `GET /search?q=biryani&veg=true&sort=rating&page=2&size=20&tags=spicy&tags=cheap`। Server जाँचता है कि `q` में कम से कम 2 अक्षर हों, `size` अधिकतम 100 हो (ताकि कोई 10 लाख rows न माँगे), `sort` दो मानों में से एक हो, और `tags` दोहराकर list बन सके।

---

## 💻 Code Example — Basic
```python
# Basic query parameters (verified: fastapi 0.162, Python 3.13)
from fastapi import FastAPI  # framework
from fastapi.testclient import TestClient  # in-process client

app: FastAPI = FastAPI()  # create app


@app.get("/items")  # no path variables, so every argument is a query parameter
def items(skip: int = 0, limit: int = 10, q: str | None = None) -> dict[str, object]:
    # skip and limit have defaults -> optional; q defaults to None -> optional
    return {"skip": skip, "limit": limit, "q": q}  # echo what we received


c: TestClient = TestClient(app)  # test client
print(c.get("/items").json())  # no query string -> all defaults used
# Output: {'skip': 0, 'limit': 10, 'q': None}
print(c.get("/items?skip=20&limit=5&q=tea").json())  # strings converted to int
# Output: {'skip': 20, 'limit': 5, 'q': 'tea'}
r = c.get("/items?skip=abc")  # not an integer
print(r.status_code, r.json()["detail"][0]["loc"])  # location shows it is a query error
# Output: 422 ['query', 'skip']
```

## 💻 Code Example — Advanced
```python
# Production style: Query() validation, Literal, list, bool (verified)
from typing import Annotated, Literal  # metadata + restricted values
from fastapi import FastAPI, Query  # Query adds rules + docs
from fastapi.testclient import TestClient  # in-process client

app: FastAPI = FastAPI()  # application


@app.get("/search")  # GET /search?q=...
def search(
    q: Annotated[str, Query(min_length=2, max_length=50)],  # REQUIRED (no default), 2..50 chars
    page: Annotated[int, Query(ge=1)] = 1,  # >= 1, default 1
    size: Annotated[int, Query(ge=1, le=100)] = 10,  # 1..100 protects the database
    sort: Literal["price", "rating"] = "rating",  # only these two strings allowed
    tags: Annotated[list[str] | None, Query()] = None,  # repeated ?tags=a&tags=b -> list
    veg: bool = False,  # true/yes/1/on -> True
) -> dict[str, object]:
    return {"q": q, "page": page, "size": size, "sort": sort, "tags": tags, "veg": veg}


c: TestClient = TestClient(app)  # client
print(c.get("/search", params={"q": "pizza"}).json())  # only the required one
# Output: {'q': 'pizza', 'page': 1, 'size': 10, 'sort': 'rating', 'tags': None, 'veg': False}
print(c.get("/search?q=pizza&tags=spicy&tags=cheap&veg=yes&page=2").json())  # repeated key + bool
# Output: {'q': 'pizza', 'page': 2, 'size': 10, 'sort': 'rating', 'tags': ['spicy', 'cheap'], 'veg': True}
r = c.get("/search")  # missing required q
print(r.status_code, r.json()["detail"][0]["type"], r.json()["detail"][0]["loc"])
# Output: 422 missing ['query', 'q']
print(c.get("/search?q=a").json()["detail"][0]["msg"])  # too short
# Output: String should have at least 2 characters
print(c.get("/search?q=ab&size=500").json()["detail"][0]["msg"])  # too big
# Output: Input should be less than or equal to 100
print(c.get("/search?q=ab&sort=cheap").json()["detail"][0]["msg"])  # not in Literal
# Output: Input should be 'price' or 'rating'
print(c.get("/search?q=ab&unknown=1").status_code)  # unknown params are ignored
# Output: 200
```

---

## 🟠 JavaScript vs Python Comparison
Express gives every query value as a string (or array) in `req.query`; you convert and validate yourself. FastAPI does it from the type hints.

```python
# Python (FastAPI)
@app.get("/search")
def search(q: str, page: int = 1, size: int = 10) -> dict[str, object]:
    return {"q": q, "page": page, "size": size}   # page and size are already ints
```
```javascript
// JavaScript (Express)
app.get('/search', (req, res) => {
  const q = req.query.q;                       // string | string[] | undefined
  const page = parseInt(req.query.page ?? '1', 10);   // manual conversion
  const size = Math.min(parseInt(req.query.size ?? '10', 10), 100);  // manual limit
  if (!q) return res.status(400).json({ error: 'q required' });      // manual error
  res.json({ q, page, size });
});
```

Key differences: in JS a repeated key (`?tags=a&tags=b`) gives an array only sometimes (depends on parser), while FastAPI needs you to declare `list[str]` with `Query()`. Without `Query()`, a list argument would be treated as a request body.

---

## 🟠 FastAPI Connection
Query parameters power pagination, filtering and search on almost every list endpoint. For many related parameters, group them into a Pydantic model (FastAPI 0.115+): `filters: Annotated[Filters, Query()]`.

```python
# FastAPI: query parameter model for pagination (needs fastapi >= 0.115)
from typing import Annotated, Literal  # typing helpers
from fastapi import FastAPI, Query  # framework
from pydantic import BaseModel, Field  # model with validation

app: FastAPI = FastAPI()  # app


class PageParams(BaseModel):  # all query params in one reusable class
    page: int = Field(1, ge=1)  # page number
    size: int = Field(10, ge=1, le=100)  # page size
    order: Literal["asc", "desc"] = "asc"  # sort direction


@app.get("/orders")  # GET /orders?page=2&size=5&order=desc
def orders(p: Annotated[PageParams, Query()]) -> dict[str, int | str]:
    offset: int = (p.page - 1) * p.size  # SQL OFFSET value
    return {"offset": offset, "limit": p.size, "order": p.order}  # used in the DB query
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: No upper limit on `size` or `limit`
✅ Correct: Always cap it with `le=100`. Otherwise `?size=10000000` can crash your database.

```python
# Wrong
def items(size: int = 10): ...
# Right
def items(size: Annotated[int, Query(ge=1, le=100)] = 10): ...
```

❌ Mistake 2: Using `list[str]` without `Query()`
✅ Correct: A bare list is treated as a request body, not repeated query keys.

```python
# Wrong: expects a JSON body, not ?tags=a&tags=b
def f(tags: list[str] = []): ...
# Right
def f(tags: Annotated[list[str] | None, Query()] = None): ...
```

❌ Mistake 3: Required parameter after a default one, and mutable defaults
✅ Correct: In Python a non-default argument cannot follow a default one. Use `*` or `Annotated` with `Query()` and put required ones first. Use `None` (not `[]`) as a default for lists.

```python
# Wrong: SyntaxError: parameter without a default follows parameter with a default
# def f(skip: int = 0, q: str): ...
# Right
def f(q: str, skip: int = 0): ...
```

---

## 🧠 Tricky Interview Question

**Q**: What does the endpoint return for each request?

```python
@app.get("/s")
def s(flag: bool = False, n: int = 1):
    return {"flag": flag, "n": n}

# 1) GET /s?flag=yes
# 2) GET /s?flag=maybe
# 3) GET /s?n=1.0
# 4) GET /s?n=1.5
```

**Answer**:
```
1) 200 {'flag': True, 'n': 1}          ("yes", "true", "on", "1" -> True)
2) 422 bool_parsing                     ("maybe" is not a boolean)
3) 200 {'flag': False, 'n': 1}          (1.0 is a whole number so it is accepted as int 1)
4) 422 int_parsing                      ("1.5" is not a valid integer string)
```
Pydantic's default (lax) mode converts compatible strings, but rejects lossy conversions. Query values always arrive as text, so `"1.0"` is accepted (whole number) and `"1.5"` fails with `int_parsing`. (All four verified by running. Python float `12.5` passed directly to a model fails with `int_from_float` instead, see topic 305.)

---

## ⚫ Interview Questions + Answers

Q1: How does FastAPI decide between path, query and body?
A1: In the path braces = path param. Simple type (int, str, bool) not in the path = query param. Pydantic model = request body.

Q2: How do you make a query parameter required?
A2: Give it no default: `q: str`. For optional use `q: str | None = None`.

Q3: How do you accept a list in the query string?
A3: `tags: Annotated[list[str] | None, Query()] = None`; the client sends `?tags=a&tags=b`.

Q4: What is the difference between `Query(ge=1)` and `Field(ge=1)`?
A4: `Query` is for a single function argument in the URL. `Field` is for a field inside a Pydantic model (body, or a query model with `Query()`).

Q5: What happens to unknown query parameters?
A5: Ignored by default. With a Pydantic query model, set `model_config = {"extra": "forbid"}` to reject them with 422.

---

## 🔷 When to Use + When Not to Use

✅ Use query parameters for:
- Filtering, searching, sorting, pagination
- Optional flags (`?verbose=true`) on GET requests

❌ Avoid query parameters for:
- Passwords, tokens, personal data (URLs are logged and cached)
- Large or nested data (use a JSON body with POST)
- Identifying a specific resource (use a path parameter)

---

## 📊 Visual Diagram

```
 GET /search?q=pizza&page=2&tags=a&tags=b
            │       │      │
            │       │      └─► tags: list[str] = ["a", "b"]
            │       └────────► page: int = 2   ("2" converted)
            └────────────────► q: str = "pizza" (required)

 Validation pipeline:  raw string → convert type → Query rules → your function
                                       fail ──────► 422 {"loc": ["query", "..."]}
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Query string | Part of URL after `?` | URL में `?` के बाद का हिस्सा |
| Query() | Validation + docs for query params | query params के लिए validation |
| Pagination | Returning data page by page | डेटा पन्नों में देना |
| Required | No default value | कोई default नहीं |
| Literal | Only listed values allowed | केवल सूचीबद्ध मान स्वीकार |
| Lax mode | Pydantic converts compatible types | Pydantic संगत types बदल देता है |

---

## ⚡ 3-Line Summary
English: Function arguments that are not in the path and not Pydantic models become query parameters. Defaults make them optional; `Query()` adds limits like min length and `le=100`. Always cap page sizes and use `Query()` for lists.
Hindi: जो function arguments path में नहीं हैं और Pydantic models भी नहीं हैं वे query parameters बनते हैं। default देने से वे वैकल्पिक होते हैं; `Query()` से min length और `le=100` जैसी सीमाएँ लगती हैं। Page size हमेशा सीमित रखें और lists के लिए `Query()` इस्तेमाल करें।

---

## ➡️ Next Topic
**302. Request Body (Pydantic)** — sending JSON data with POST/PUT and validating it with models.
