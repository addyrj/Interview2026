---

# 261. Exceptions — Complete Guide
# हिंदी में: Exceptions — पूरी Guide

---

## 🔵 Simple Definition (English)
Exceptions are runtime errors that interrupt normal program flow. Python uses try/except/else/finally blocks to handle them gracefully. Unlike return codes, exceptions propagate up the call stack until caught — or crash the program. Python has a rich exception hierarchy rooted at `BaseException`. The `else` block runs only if no exception occurred; `finally` always runs (used for cleanup).

## 🔵 सरल परिभाषा (Hindi)
Exceptions runtime errors हैं जो normal program flow को interrupt करती हैं। Python `try/except/else/finally` blocks से handle करता है। Exception call stack में ऊपर propagate होती है जब तक catch न हो। `else` = no exception होने पर। `finally` = हमेशा — cleanup के लिए।

---

## 💻 Code Example — Basic
```python
# ─── Basic try/except ─────────────────────────────────────────────
try:
    result = 10 / 0
except ZeroDivisionError:
    print("Can't divide by zero!")

# ─── Catching multiple exceptions ─────────────────────────────────
def parse_age(value: str) -> int:
    try:
        age = int(value)
        if age < 0 or age > 150:
            raise ValueError(f"Age {age} out of valid range")
        return age
    except ValueError as e:
        print(f"Invalid age: {e}")
        return 0
    except TypeError as e:
        print(f"Wrong type: {e}")
        return 0

# Catch multiple in one except:
try:
    data = int(input_value)
except (ValueError, TypeError) as e:
    print(f"Conversion error: {e}")

# ─── else and finally ─────────────────────────────────────────────
def read_config(filepath: str) -> dict:
    try:
        with open(filepath) as f:
            import json
            data = json.load(f)
    except FileNotFoundError:
        print(f"Config file not found: {filepath}")
        return {}
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
        return {}
    else:
        # Runs ONLY if no exception occurred in try block:
        print("Config loaded successfully")
        return data
    finally:
        # ALWAYS runs — even if exception, even if return:
        print("Config read attempt complete")

# ─── Raising exceptions ───────────────────────────────────────────
def get_user(user_id: int) -> dict:
    if user_id <= 0:
        raise ValueError(f"user_id must be positive, got {user_id}")
    if user_id > 1000:
        raise LookupError(f"User {user_id} not found")
    return {"id": user_id, "name": "Priya"}

# Re-raise the current exception:
try:
    get_user(-1)
except ValueError as e:
    print(f"Logging: {e}")
    raise   # re-raises the same exception with same traceback

# ─── Common built-in exceptions ───────────────────────────────────
# ValueError    — right type, wrong value: int("hello")
# TypeError     — wrong type: 1 + "two"
# KeyError      — dict key missing: d["missing"]
# IndexError    — list index out of range: lst[99]
# AttributeError — object has no attribute: None.split()
# FileNotFoundError — file not found (subclass of OSError)
# ZeroDivisionError — divide by zero: 1/0
# NameError     — variable not defined: print(undefined_var)
# ImportError   — module not found: import nonexistent
# StopIteration — iterator exhausted (raised by next())
# RuntimeError  — general runtime error
# NotImplementedError — abstract method not implemented
```

## 💻 Code Example — Advanced
```python
from __future__ import annotations
import logging

# ─── Custom exceptions ────────────────────────────────────────────
class AppError(Exception):
    """Base exception for all application errors."""
    pass

class ValidationError(AppError):
    """Input validation failed."""
    def __init__(self, field: str, message: str, value=None):
        self.field = field
        self.value = value
        super().__init__(f"Validation failed for '{field}': {message}")

class NotFoundError(AppError):
    """Resource not found."""
    def __init__(self, resource: str, id: int | str):
        self.resource = resource
        self.id = id
        super().__init__(f"{resource} with id '{id}' not found")

class DatabaseError(AppError):
    """Database operation failed."""
    pass

# Usage:
def get_tariff(code: str) -> dict:
    if not code:
        raise ValidationError("hs_code", "cannot be empty", code)
    if len(code) != 10:
        raise ValidationError("hs_code", f"must be 10 digits, got {len(code)}", code)
    
    result = db_query(code)
    if not result:
        raise NotFoundError("TariffCode", code)
    return result

# ─── Exception chaining ───────────────────────────────────────────
def fetch_user_data(user_id: int) -> dict:
    try:
        # Simulated DB query that might fail:
        raw = db_execute("SELECT * FROM users WHERE id = ?", user_id)
    except Exception as db_err:
        # Chain: original exception attached as __cause__:
        raise DatabaseError(f"Failed to fetch user {user_id}") from db_err
        # Traceback shows BOTH errors — original cause is preserved

# ─── Suppress specific exceptions ────────────────────────────────
from contextlib import suppress

# Don't raise if file doesn't exist (just ignore):
with suppress(FileNotFoundError):
    os.remove("maybe_exists.txt")
# Equivalent to:
try:
    os.remove("maybe_exists.txt")
except FileNotFoundError:
    pass

# ─── FastAPI exception handlers ───────────────────────────────────
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "field": exc.field,
            "message": str(exc),
        }
    )

@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(
        status_code=404,
        content={
            "error": "not_found",
            "resource": exc.resource,
            "id": exc.id,
        }
    )

# ─── Logging exceptions (production pattern) ─────────────────────
logger = logging.getLogger(__name__)

async def process_order(order_id: int):
    try:
        order = await get_order(order_id)
        await validate_order(order)
        await charge_payment(order)
        await fulfill_order(order)
    except ValidationError as e:
        logger.warning("Order validation failed", extra={"order_id": order_id, "error": str(e)})
        raise
    except Exception as e:
        logger.error(
            "Unexpected error processing order",
            extra={"order_id": order_id},
            exc_info=True,     # ← includes full traceback in log!
        )
        raise DatabaseError("Order processing failed") from e
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python:
try:
    data = json.loads(raw)
except json.JSONDecodeError as e:
    print(f"JSON error at line {e.lineno}: {e.msg}")
except Exception as e:
    print(f"Unexpected: {type(e).__name__}: {e}")
else:
    print("Parse successful")
finally:
    print("Always runs")
```

```javascript
// JavaScript:
try {
    const data = JSON.parse(raw);
    console.log("Parse successful");
} catch (e) {
    if (e instanceof SyntaxError) {
        console.log(`JSON error: ${e.message}`);
    } else {
        console.log(`Unexpected: ${e.constructor.name}: ${e.message}`);
    }
} finally {
    console.log("Always runs");
}
// No 'else' block in JavaScript try/catch
```

Key differences:
- Python `except ExceptionType` is type-specific. JS `catch (e)` is untyped — you check with `instanceof`.
- Python has `else` block (no exception occurred). JS does not.
- Python exception hierarchy: catch parent catches all children.
- Python `raise ... from ...` chains exceptions. JS uses `cause: e` in Error constructor (ES2022).

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Bare `except:` catches EVERYTHING including `SystemExit`, `KeyboardInterrupt`
```python
# Wrong — swallows Ctrl+C, sys.exit(), etc.:
try:
    process()
except:         # catches BaseException!
    pass

# Correct — catch specific exceptions:
try:
    process()
except Exception:     # catches Exception and subclasses (not SystemExit/KeyboardInterrupt)
    pass

# Or even more specific:
except (ValueError, TypeError) as e:
    logger.error(str(e))
```

❌ Mistake 2: Silently swallowing exceptions without logging
```python
# Wrong — hides bugs:
try:
    process_payment(order)
except Exception:
    pass    # payment failed silently!

# Correct — at minimum, log it:
try:
    process_payment(order)
except Exception as e:
    logger.error("Payment failed", exc_info=True)
    raise   # re-raise so caller knows
```

---

## 🧠 Tricky Interview Question

**Q**: What is the order of execution in `try/except/else/finally`? What if `except` block also raises an exception?

**Answer**:
1. `try` block runs
2. If exception: `except` runs → then `finally` runs (NOT `else`)
3. If no exception: `else` runs → then `finally` runs
4. `finally` ALWAYS runs — even after `return` inside `try`/`except`

If `except` block raises a new exception: the new exception propagates. `finally` still runs. The original exception is lost (unless `raise ... from original` was used). If `finally` itself raises: original exception is lost.

---

## ⚫ Interview Questions + Answers

Q1: What is the Python exception hierarchy?
A1: Root: `BaseException` → `SystemExit`, `KeyboardInterrupt`, `GeneratorExit`, and `Exception`. All user-facing exceptions inherit from `Exception`. `Exception` → `ArithmeticError` (ZeroDivisionError, OverflowError), `LookupError` (KeyError, IndexError), `ValueError`, `TypeError`, `OSError` (FileNotFoundError, PermissionError), `RuntimeError` (RecursionError). Custom exceptions should subclass `Exception` (or a more specific subclass), never `BaseException` directly.

Q2: What is exception chaining with `raise ... from ...`?
A2: `raise NewException("message") from original_exception` attaches `original_exception` as `__cause__` (explicit chain) or `__context__` (implicit chain). When printed, Python shows "The above exception was the direct cause of the following exception." Use it when: you catch a low-level exception (DB error, HTTP error) and re-raise as a domain-specific exception. Preserves the root cause for debugging. `raise NewError() from None` hides the chain (suppresses context).

Q3: When should you use `assert` vs `raise`?
A3: `assert condition, message` raises `AssertionError` if condition is False. Assertions are for: **internal invariants** — things that should never be False in correct code (e.g., `assert isinstance(result, list)`). `raise` is for: **runtime conditions** — things that can fail with correct code (missing file, bad user input, network error). NEVER use `assert` for user input validation — assertions are disabled with `python -O` flag. Use `raise ValueError/TypeError` for user-facing errors.

Q4: How do you create a custom exception with additional data?
A4: Subclass `Exception` and override `__init__`: `class ValidationError(Exception): def __init__(self, field, message): self.field = field; super().__init__(message)`. Inherit from a domain base exception (`AppError`) for easy catch-all: `except AppError`. Add data as attributes — available after catching: `except ValidationError as e: print(e.field)`. Can also add `__str__` for custom display, but calling `super().__init__(msg)` handles basic str representation.

Q5: What is the difference between `except Exception as e: raise` and `except Exception as e: raise e`?
A5: `raise` (no argument) re-raises the current exception with the **original traceback** — the traceback shows the original location where the exception was raised. `raise e` raises the exception again but with a **new traceback starting from the current line** — the original traceback is lost. Always use `raise` (bare) when you want to propagate an exception unchanged. Use `raise NewException() from e` to wrap it in a new exception while preserving the chain.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| try | Code that might fail | Code जो fail हो सकता है |
| except | Handle the exception | Exception handle करो |
| else | Run if no exception | No exception = else चलेगा |
| finally | Always runs | हमेशा चलता है |
| raise | Throw an exception | Exception throw करो |
| Exception | Base for all errors | सभी errors का base |
| traceback | Error call stack | Error call stack |

---

## ⚡ 3-Line Summary
English: Always catch specific exceptions (`except ValueError`) never bare `except:`. Use `finally` for cleanup and `else` for code that runs only on success. Create custom exceptions by subclassing `Exception`, and use `raise NewError() from original` to chain exceptions for debuggable error chains.
Hindi: हमेशा specific exceptions catch करो, bare `except:` नहीं। `finally` = cleanup, `else` = success पर। Custom exceptions `Exception` से inherit करें। `raise New() from original` से error chain बनाएं।

---

## ➡️ Next Topic
**262. try/except Deep Dive** — exception groups (Python 3.11+). **265. Custom Exceptions** — complete hierarchy design. **271. Logging Errors** — structured logging with exc_info.
