---

# Q269. Builder Pattern
# Category: Design Patterns
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement a Builder for an HTTP request object that has many optional parts (method, url, headers, params, body, timeout). The builder should support chaining and validate on `build()`.

---

## 💡 Quick Concept (2 lines only)
Builder constructs a complex object step by step; each setter returns `self` for chaining and `build()` returns the final immutable object.
हिंदी: Builder बड़े object को step-by-step बनाता है; chaining के लिए हर method `self` लौटाती है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from dataclasses import dataclass, field  # Step 1: dataclass for the product


@dataclass(frozen=True)  # immutable final product
class Request:
    method: str  # HTTP verb
    url: str  # target url
    headers: dict[str, str] = field(default_factory=dict)  # optional headers
    params: dict[str, str] = field(default_factory=dict)  # optional query params
    body: str | None = None  # optional body
    timeout: float = 30.0  # seconds


class RequestBuilder:  # Step 2: the builder
    def __init__(self, url: str) -> None:
        self._url = url  # url is required
        self._method = "GET"  # default verb
        self._headers: dict[str, str] = {}  # collected headers
        self._params: dict[str, str] = {}  # collected params
        self._body: str | None = None  # no body by default
        self._timeout = 30.0  # default timeout

    def method(self, m: str) -> "RequestBuilder":
        self._method = m.upper()  # normalise the verb
        return self  # Step 3: return self to allow chaining

    def header(self, k: str, v: str) -> "RequestBuilder":
        self._headers[k] = v  # add one header
        return self  # chain

    def param(self, k: str, v: str) -> "RequestBuilder":
        self._params[k] = v  # add one query param
        return self  # chain

    def body(self, b: str) -> "RequestBuilder":
        self._body = b  # set body
        return self  # chain

    def timeout(self, t: float) -> "RequestBuilder":
        self._timeout = t  # set timeout
        return self  # chain

    def build(self) -> Request:
        if self._method in ("GET", "HEAD") and self._body:  # Step 4: validate
            raise ValueError("GET/HEAD cannot have a body")  # reject bad combo
        return Request(self._method, self._url, dict(self._headers),
                       dict(self._params), self._body, self._timeout)  # copy dicts


# ============================================
# TEST CASES
# ============================================
req = (RequestBuilder("https://api.x.io/users")  # start with required url
       .method("post")  # lower-case is normalised
       .header("Auth", "t1")  # add header
       .param("page", "2")  # add param
       .body('{"a": 1}')  # add body
       .timeout(5)  # custom timeout
       .build())  # create the object
print(req)
# Expected: Request(method='POST', url='https://api.x.io/users', headers={'Auth': 't1'}, params={'page': '2'}, body='{"a": 1}', timeout=5)
try:
    RequestBuilder("u").body("x").build()  # GET + body is invalid
except ValueError as e:
    print(e)  # Expected: GET/HEAD cannot have a body
```

---

## 🔍 Why This Works (3 lines max)
Each setter mutates the builder and returns it, so calls chain. `build()` is the single place for validation and creates a frozen object. Copying the dicts stops later builder changes from leaking in.
हिंदी: Setters `self` लौटाते हैं, validation सिर्फ `build()` में होता है और final object frozen रहता है।

---

## ⚡ Alternative Solution
```python
# Pythonic: keyword arguments + dataclass defaults often replace a builder
from dataclasses import dataclass, replace  # replace() makes modified copies


@dataclass(frozen=True)
class Request:
    url: str  # required
    method: str = "GET"  # default
    timeout: float = 30.0  # default


base = Request("https://api.x.io")  # defaults cover most cases
slow = replace(base, timeout=60.0)  # "builder step" = copy with a change
print(base)  # Expected: Request(url='https://api.x.io', method='GET', timeout=30.0)
print(slow)  # Expected: Request(url='https://api.x.io', method='GET', timeout=60.0)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: setters forget to return self - chaining breaks
class BadBuilder:
    def __init__(self) -> None:
        self.x = 0  # state

    def set_x(self, v):
        self.x = v  # returns None implicitly!


try:
    BadBuilder().set_x(1).set_x(2)  # None.set_x -> AttributeError
except AttributeError as e:
    print(e)  # Output: 'NoneType' object has no attribute 'set_x'

# ✅ Correct: `return self` at the end of every setter
```

---

## 🎯 Interview Tip (1 line)
Say: "Builder for many optional/validated parts; in Python keyword args and dataclasses often suffice, so use Builder only when construction has steps or rules."

---

## 🔗 Related Questions
→ Q246 (dataclasses) | Q262 (factory) | Q198 (query string builder)
