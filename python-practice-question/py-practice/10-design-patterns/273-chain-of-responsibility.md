---

# Q273. Chain of Responsibility
# Category: Design Patterns
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Build a request-validation chain: `AuthHandler` -> `RateLimitHandler` -> `ValidationHandler`. Each handler either rejects the request or passes it to the next one.

---

## 💡 Quick Concept (2 lines only)
Request travels through a chain of handlers; each one decides to handle it or pass it on. Web middleware is the classic example.
हिंदी: Request handlers की एक चेन से गुजरती है; हर handler या तो उसे रोकता है या अगले को देता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from __future__ import annotations  # Step 1: allow forward references in hints


class Handler:  # Step 2: base class holding the link to the next handler
    def __init__(self) -> None:
        self._next: Handler | None = None  # next link in the chain

    def set_next(self, h: Handler) -> Handler:
        self._next = h  # store next handler
        return h  # return it so calls can be chained

    def handle(self, req: dict) -> str:
        if self._next:  # if a next handler exists
            return self._next.handle(req)  # pass the request on
        return "OK"  # end of chain: everything passed


class AuthHandler(Handler):  # Step 3: concrete handler 1
    def handle(self, req: dict) -> str:
        if not req.get("token"):  # no token -> reject
            return "401 Unauthorized"  # stop the chain
        return super().handle(req)  # otherwise continue


class RateLimitHandler(Handler):  # concrete handler 2
    def handle(self, req: dict) -> str:
        if req.get("calls", 0) > 100:  # too many calls -> reject
            return "429 Too Many Requests"  # stop the chain
        return super().handle(req)  # continue


class ValidationHandler(Handler):  # concrete handler 3
    def handle(self, req: dict) -> str:
        if not req.get("body"):  # empty body -> reject
            return "400 Bad Request"  # stop the chain
        return super().handle(req)  # continue


# ============================================
# TEST CASES
# ============================================
auth = AuthHandler()  # head of chain
auth.set_next(RateLimitHandler()).set_next(ValidationHandler())  # link the rest
print(auth.handle({"token": "t", "calls": 5, "body": "x"}))  # Expected: OK
print(auth.handle({"calls": 5, "body": "x"}))  # Expected: 401 Unauthorized
print(auth.handle({"token": "t", "calls": 500, "body": "x"}))  # Expected: 429 Too Many Requests
print(auth.handle({"token": "t", "calls": 5}))  # Expected: 400 Bad Request
```

---

## 🔍 Why This Works (3 lines max)
Each handler checks its own rule and either returns early or calls `super().handle()`, which forwards to the next link. The sender only knows the head of the chain.
हिंदी: हर handler अपना नियम जाँचता है और या तो वहीं रुकता है या `super().handle()` से आगे भेजता है।

---

## ⚡ Alternative Solution
```python
# Pythonic: chain = list of functions; first non-None result wins
from collections.abc import Callable  # type hint

Check = Callable[[dict], str | None]  # returns error string or None


def auth(r: dict) -> str | None:
    return None if r.get("token") else "401 Unauthorized"  # pass or fail


def body(r: dict) -> str | None:
    return None if r.get("body") else "400 Bad Request"  # pass or fail


def run(chain: list[Check], req: dict) -> str:
    for check in chain:  # walk the chain in order
        if (err := check(req)) is not None:  # walrus: stop on first error
            return err  # reject
    return "OK"  # everything passed


print(run([auth, body], {"token": "t", "body": "x"}))  # Expected: OK
print(run([auth, body], {"token": "t"}))  # Expected: 400 Bad Request
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: forgetting to forward - the chain silently stops after the first handler
class BadAuth:
    def __init__(self, nxt) -> None:
        self.nxt = nxt  # next handler

    def handle(self, req: dict) -> str:
        if not req.get("token"):
            return "401"
        return "OK"  # ❌ never calls self.nxt.handle(req)


print(BadAuth(None).handle({"token": "t"}))  # Output: OK  (later checks skipped!)

# ✅ Correct: end with `return self.nxt.handle(req)` (or super().handle(req))
```

---

## 🎯 Interview Tip (1 line)
Say: "Chain of Responsibility decouples sender from receivers — it is how middleware (FastAPI/Django/Express) and logging filters work."

---

## 🔗 Related Questions
→ Q225 (custom middleware) | Q265 (decorator pattern) | Q264 (strategy)
