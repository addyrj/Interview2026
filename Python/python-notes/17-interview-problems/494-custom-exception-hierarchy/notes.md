---

# 494. Custom Exception Hierarchy
# हिंदी में: Custom Exception Hierarchy (अपनी Exception की पीढ़ियाँ)

Full runnable solution: [main.py](main.py) (AppError base, sub-classes with status/code, exception chaining, one FastAPI handler).

---

## 🔵 Simple Definition (English)
A custom exception hierarchy is a family of your own exception classes with one base (`AppError`). You catch the whole family with the base or a specific case with a child, and each class carries its HTTP status and error code.

## 🔵 सरल परिभाषा (Hindi)
Custom exception hierarchy आपकी अपनी exception classes का परिवार है जिसका एक base (`AppError`) होता है। पूरे परिवार को base से पकड़ सकते हैं या किसी खास case को child से, और हर class अपना HTTP status और error code रखती है।

---

## 🔴 Problem it Solves
Raising plain `Exception("something")` or `ValueError` everywhere forces callers to match on message strings and mixes your bugs with library errors. A hierarchy makes error handling precise, centralised and self-documenting.

## 🔴 यह क्यों बना? (Hindi)
हर जगह `Exception("something")` या `ValueError` उठाने से callers को message string से पहचानना पड़ता है और आपके bugs library errors में मिल जाते हैं। Hierarchy से error handling सटीक, एक जगह और खुद-समझाने वाली बन जाती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → class AppError(Exception): status_code, code, message, details
Step 2 → Children: NotFoundError(404), ValidationFailed(422), PaymentError(402)
Step 3 → Deeper child: InsufficientFunds(PaymentError)
Step 4 → raise InsufficientFunds("balance too low", balance=100)
Step 5 → except PaymentError catches it; except AppError catches all
Step 6 → One FastAPI exception_handler(AppError) converts any to JSON
Step 7 → `raise X from e` keeps the original cause
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → class AppError(Exception): status_code, code, message, details
Step 2 → Children: NotFoundError(404), ValidationFailed(422), PaymentError(402)
Step 3 → और गहरा child: InsufficientFunds(PaymentError)
Step 4 → raise InsufficientFunds("balance too low", balance=100)
Step 5 → except PaymentError इसे पकड़ता है; except AppError सबको
Step 6 → एक FastAPI exception_handler(AppError) किसी भी error को JSON बना देता है
Step 7 → `raise X from e` से असली कारण सुरक्षित रहता है
```

---

## 🟡 Real World Example
A Razorpay-like payment service: `PaymentError` -> `InsufficientFunds`, `CardDeclined`, `GatewayTimeout`. The API handler maps them to 402/402/504 with stable `code` strings that mobile apps switch on ("insufficient_funds" shows a top-up screen). Retries apply only to `GatewayTimeout`.

## 🟡 Real Example Hindi mein
Razorpay जैसी payment service: `PaymentError` -> `InsufficientFunds`, `CardDeclined`, `GatewayTimeout`। API handler इन्हें 402/402/504 में बदलता है और स्थिर `code` strings देता है जिन पर mobile app निर्णय लेती है ("insufficient_funds" पर top-up screen)। Retry सिर्फ़ `GatewayTimeout` पर होता है।

---

## 💻 Code Example — Basic
```python
# Small hierarchy and catching at different levels
class AppError(Exception):  # base for all our errors
    pass  # nothing extra needed

class PaymentError(AppError):  # a family
    pass  # inherits everything

class InsufficientFunds(PaymentError):  # a specific case
    pass  # inherits everything

try:  # try something that fails
    raise InsufficientFunds("low balance")  # raise the specific one
except PaymentError as e:  # catch by parent class
    print("caught:", type(e).__name__, "-", e)  # name and message
print(issubclass(InsufficientFunds, AppError))  # whole chain is related
# Output:
# caught: InsufficientFunds - low balance
# True
```

## 💻 Code Example — Advanced
```python
# Excerpt from main.py: status + code on class, one handler for the whole tree
class AppError(Exception):
    status_code: int = 500
    code: str = "internal_error"

    def __init__(self, message: str = "", **details: object) -> None:
        super().__init__(message or self.code)
        self.message = message or self.code
        self.details = details

    def to_dict(self) -> dict:
        return {"error": {"code": self.code, "message": self.message, "details": self.details}}

class NotFoundError(AppError):
    status_code, code = 404, "not_found"

@app.exception_handler(AppError)  # handles every subclass
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content=exc.to_dict())
```
Real output of `python main.py`:
```
['InsufficientFunds', 'PaymentError', 'AppError', 'Exception', 'BaseException', 'object']
404 {'error': {'code': 'not_found', 'message': 'user not found', 'details': {'user_id': 9}}}
402 {'error': {'code': 'insufficient_funds', 'message': 'balance too low', 'details': {'balance': 100, 'needed': 500}}}
DatabaseError caused by KeyError('x')
all ok
```

---

## 🟠 JavaScript vs Python Comparison
JS: `class AppError extends Error` and `instanceof`; you must set `this.name`. Python: subclass `Exception`, `except Parent` catches children, and `raise ... from e` is like `new Error(msg, { cause: e })`.

```python
class NotFound(AppError):
    status_code = 404
```
```javascript
class NotFound extends AppError { constructor(m) { super(m); this.status = 404; } }
```

---

## 🟠 FastAPI Connection
FastAPI has built-in `HTTPException`, but a domain hierarchy keeps business code free of HTTP. Domain/service layers raise `AppError`s; a single `@app.exception_handler` translates them. You can also override `RequestValidationError` for a consistent error JSON.

```python
@app.exception_handler(RequestValidationError)  # make 422 look like our errors
async def on_validation(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"error": {"code": "validation_failed", "details": exc.errors()}})
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Bare `except:` or `except Exception: pass`, which hides bugs.
✅ Correct: catch the narrowest class you can handle, log, re-raise otherwise.

❌ Mistake 2: Losing the original traceback.
✅ Correct: `raise NewError(...) from original`.

```python
# Wrong
try: lookup()
except KeyError: raise DatabaseError("failed")     # cause is only implicit context
# Right
try: lookup()
except KeyError as e: raise DatabaseError("failed") from e
```

❌ Mistake 3: Too deep or too many classes, or inheriting from `BaseException` (would catch Ctrl+C handling incorrectly).
✅ Correct: 2-3 levels, inherit from `Exception`, distinguish classes only when callers act differently.

---

## 🧠 Tricky Interview Question
```python
try:
    raise ValueError("a")
except (KeyError, ValueError) as e:
    pass
print(e)
```
Answer: `NameError: name 'e' is not defined`. At the end of an `except ... as e` block Python deletes `e` to avoid reference cycles. Copy it to another variable if you need it later. Also: order of `except` clauses matters, put children before parents, or the child clause never runs.

---

## ⚫ Interview Questions + Answers

Q1: Why inherit from Exception, not BaseException?
A1: BaseException includes `KeyboardInterrupt`, `SystemExit`, `GeneratorExit`, which normal code should not swallow.

Q2: `raise from` vs implicit chaining?
A2: `from e` sets `__cause__` explicitly ("direct cause of"); inside an except block without it, Python sets `__context__` ("during handling of"). `from None` hides the context.

Q3: Where to define status codes?
A3: On the exception class for simple APIs, or in the handler mapping for strict layering.

Q4: What is `ExceptionGroup`?
A4: 3.11+ container for multiple errors, caught with `except*` (used by TaskGroup).

Q5: EAFP vs LBYL?
A5: Python prefers trying and catching (EAFP) over checking first (LBYL).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Libraries/services with several distinct, actionable failure modes

❌ Avoid when:
- A built-in (`ValueError`, `KeyError`) already says it clearly in a small script

---

## 📊 Visual Diagram
```
 Exception
   └─ AppError (500 internal_error)
        ├─ NotFoundError (404)
        ├─ ValidationFailed (422)
        ├─ DatabaseError
        └─ PaymentError (402)
             └─ InsufficientFunds
 except InsufficientFunds < except PaymentError < except AppError  (specific -> general)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Hierarchy | Parent-child classes | parent-child classes |
| Exception chaining | Link to original error | असली error से जोड़ना |
| __cause__ | Explicit cause | स्पष्ट कारण |
| Handler | Code that converts errors | error को जवाब में बदलने वाला code |
| EAFP | Easier to ask forgiveness | पहले करो, फेल हो तो पकड़ो |

---

## ⚡ 3-Line Summary
English: Create one base exception and specific children with status and code.
Catch specific first, general later, and chain with `from`.
One FastAPI handler turns the whole family into JSON.
Hindi: एक base exception और status व code वाले specific children बनाओ।
पहले specific, फिर general पकड़ो और `from` से chain करो।
एक FastAPI handler पूरे परिवार को JSON बना देता है।

---

## ➡️ Next Topic
495. Dataclass Example: another tool for clean code, concise data containers instead of boilerplate classes.

---
