---

# 271. Logging Errors Properly
# हिंदी में: Errors को सही तरीके से log करना

---

## 🔵 Simple Definition (English)
Logging an error properly means writing it to a logger with the full traceback (`logger.exception` or `exc_info=True`), enough context (ids, inputs), at the right level, and only once. It is how you debug production, where you cannot attach a debugger.

## 🔵 सरल परिभाषा (Hindi)
Error को सही तरीके से log करने का मतलब है उसे logger में पूरे traceback (`logger.exception` या `exc_info=True`), ज़रूरी context (ids, inputs), सही level पर और सिर्फ़ एक बार लिखना। Production में debugger नहीं लगा सकते, इसलिए debugging इसी से होती है।

---

## 🔴 Problem it Solves
`print(e)` loses the traceback, goes to no file, has no level or time, and gives you no idea where it failed at 3 AM. Logging everywhere gives duplicate noise, while swallowing errors gives silence. A clear policy makes errors findable and searchable.

## 🔴 यह क्यों बना? (Hindi)
`print(e)` से traceback खो जाता है, कोई file नहीं बनती, level या समय नहीं होता, और रात 3 बजे पता नहीं चलता कहाँ fail हुआ। हर जगह log करने से duplicate शोर होता है और error निगल जाने से खामोशी। एक साफ़ नीति से errors खोजने योग्य बनती हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create one module-level logger: logger = logging.getLogger(__name__)
Step 2 → Catch the error where you can DECIDE something (usually the boundary)
Step 3 → Call logger.exception('what failed', extra/ids) inside the except block
Step 4 → logging formats the message and attaches the traceback from sys.exc_info()
Step 5 → Handlers send the record to console, file or a log service (JSON formatter)
Step 6 → Then re-raise, return a fallback or translate to an HTTP error. Do not log again higher up
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Module-level logger बनाएँ: logger = logging.getLogger(__name__)
Step 2 → Error वहाँ पकड़ें जहाँ कोई फ़ैसला ले सकें (आमतौर पर boundary)
Step 3 → except block में logger.exception('क्या fail हुआ', ids) बुलाएँ
Step 4 → logging message format करता है और sys.exc_info() से traceback जोड़ देता है
Step 5 → Handlers record को console, file या log service (JSON formatter) में भेजते हैं
Step 6 → फिर re-raise करें, fallback लौटाएँ या HTTP error बनाएँ। ऊपर दोबारा log न करें
```

---

## 🟡 Real World Example
A Razorpay checkout service logs `logger.exception('payment failed', extra={'order_id': ...})` once at the API boundary. The JSON log goes to a log service where on-call engineers search by `order_id`. Card numbers and tokens are never logged. A FastAPI global handler logs unexpected errors with full traceback and returns a generic 500 body.

## 🟡 Real Example Hindi mein
Razorpay checkout service API boundary पर एक बार `logger.exception('payment failed', extra={'order_id': ...})` लिखती है। JSON log log-service में जाता है जहाँ on-call engineers `order_id` से खोजते हैं। Card number और tokens कभी log नहीं होते। FastAPI का global handler अनपेक्षित errors को पूरे traceback के साथ log करता है और client को generic 500 देता है।

---

## 💻 Code Example — Basic
```python
# Basic: log errors with logger.exception - every line commented
import logging  # standard logging
import sys  # stdout handler

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")  # simple setup
logger: logging.Logger = logging.getLogger("payments")  # named logger


def divide(a: int, b: int) -> float:  # function that can fail
    try:  # guard
        return a / b  # may raise ZeroDivisionError
    except ZeroDivisionError:  # handle it
        logger.exception("divide failed a=%s b=%s", a, b)  # ERROR level + full traceback
        return float("nan")  # fallback value


print(divide(4, 2))  # normal
print(divide(1, 0))  # logs the traceback, returns nan
logger.error("only message, no traceback")  # error without traceback
try:  # second way to include traceback
    int("x")  # ValueError
except ValueError as exc:  # catch
    logger.error("parse failed: %s", exc, exc_info=True)  # exc_info=True adds traceback

# --- Real output (run on Python 3.13; ids/timings may vary) ---
# 2.0
# ERROR payments: divide failed a=1 b=0
# Traceback (most recent call last):
#   File "/app/b.py", line 11, in divide
#     return a / b  # may raise ZeroDivisionError
#            ~~^~~
# ZeroDivisionError: division by zero
# nan
# ERROR payments: only message, no traceback
# ERROR payments: parse failed: invalid literal for int() with base 10: 'x'
# Traceback (most recent call last):
#   File "/app/b.py", line 21, in <module>
#     int("x")  # ValueError
#     ~~~^^^^^
# ValueError: invalid literal for int() with base 10: 'x'
```

## 💻 Code Example — Advanced
```python
# Production style: JSON-ish structured error logs, log once, extra context, no secrets
import json  # to build structured records
import logging  # logging
import sys  # stdout


class JsonFormatter(logging.Formatter):  # one JSON object per line
    def format(self, record: logging.LogRecord) -> str:  # build the line
        payload: dict[str, object] = {  # base fields
            "level": record.levelname,  # ERROR / INFO
            "logger": record.name,  # logger name
            "msg": record.getMessage(),  # formatted message
            "order_id": getattr(record, "order_id", None),  # extra context if present
        }
        if record.exc_info:  # exception attached?
            payload["error_type"] = record.exc_info[0].__name__  # type name only (stable)
            payload["traceback"] = self.formatException(record.exc_info).splitlines()[-1]  # last line
        return json.dumps(payload)  # serialise


handler = logging.StreamHandler(sys.stdout)  # write to stdout
handler.setFormatter(JsonFormatter())  # use JSON
log = logging.getLogger("orders")  # logger
log.addHandler(handler)  # attach
log.setLevel(logging.INFO)  # level
log.propagate = False  # avoid duplicate root output


class PaymentFailed(Exception):  # domain error
    pass  # nothing extra


def charge(order_id: int, token: str) -> None:  # low-level function: RAISE, do not log
    raise PaymentFailed("bank declined")  # simulate failure


def checkout(order_id: int) -> bool:  # boundary: LOG ONCE here
    try:  # call
        charge(order_id, token="tok_secret")  # token must never be logged
    except PaymentFailed:  # handle at the boundary
        log.exception("checkout failed", extra={"order_id": order_id})  # log with context
        return False  # tell caller
    return True  # success


print(checkout(42))  # False after logging
log.info("order ok", extra={"order_id": 43})  # info record without exception

# --- Real output (run on Python 3.13; ids/timings may vary) ---
# {"level": "ERROR", "logger": "orders", "msg": "checkout failed", "order_id": 42, "error_type": "PaymentFailed", "traceback": "PaymentFailed: bank declined"}
# False
# {"level": "INFO", "logger": "orders", "msg": "order ok", "order_id": 43}
```

---

## 🟠 JavaScript vs Python Comparison
In JavaScript you usually call `console.error(err)` (prints stack) or use libraries like pino/winston. Python's `logging` is built in, supports levels, handlers and automatic traceback capture via `exception()`.

```python
try:
    risky()
except Exception:
    logger.exception('risky failed')   # level ERROR + traceback
```
```javascript
try {
  risky();
} catch (err) {
  logger.error({ err, orderId }, 'risky failed');  // pino style
  // console.error(err) prints the stack too
}
```

Key differences: Python logs the traceback automatically from the active exception; in JS you must pass the error object yourself. Python's standard logging is hierarchical (`orders.payments` inherits settings from `orders`).

---

## 🟠 FastAPI Connection
Register `@app.exception_handler(Exception)` to log unexpected errors with their traceback (`exc_info=exc`) and return a safe generic 500 to the client. Expected domain errors (404, 409) usually need only an INFO/WARNING line without traceback.

```python
# FastAPI: log unexpected errors once in a global handler, hide details from the client
import logging  # logging
from fastapi import FastAPI, Request  # app and request
from fastapi.responses import JSONResponse  # response
from fastapi.testclient import TestClient  # client

class Collect(logging.Handler):  # tiny handler that keeps records in memory (for the demo)
    def __init__(self) -> None:  # constructor
        super().__init__()  # init base
        self.records: list[logging.LogRecord] = []  # storage

    def emit(self, record: logging.LogRecord) -> None:  # called per log record
        self.records.append(record)  # store it


collector = Collect()  # create handler
log = logging.getLogger("api")  # logger
log.addHandler(collector)  # attach (production: file/stdout/JSON handler)
log.propagate = False  # no duplicate console output
app: FastAPI = FastAPI()  # app


@app.exception_handler(Exception)  # last-resort handler for unexpected errors
async def unhandled(request: Request, exc: Exception) -> JSONResponse:
    log.error("unhandled on %s %s", request.method, request.url.path, exc_info=exc)  # full traceback in logs
    return JSONResponse(status_code=500, content={"detail": "internal error"})  # generic body for client


@app.get("/boom")  # endpoint that crashes
def boom() -> None:
    raise RuntimeError("connect to db-prod:5432 failed")  # internal host must not leak to client


c = TestClient(app, raise_server_exceptions=False)  # return 500 instead of raising in test
r = c.get("/boom")  # call
print(r.status_code, r.json())  # client sees only the generic message
rec = collector.records[0]  # the log record written server-side
print(rec.levelname, rec.getMessage())  # what the log says
print(type(rec.exc_info[1]).__name__, "|", rec.exc_info[1])  # full error kept in logs only

# --- Real output (run on Python 3.13; ids/timings may vary) ---
# 500 {'detail': 'internal error'}
# ERROR unhandled on GET /boom
# RuntimeError | connect to db-prod:5432 failed
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `logger.error(str(e))` and losing the traceback
```python
# Wrong
except ValueError as e:
    logger.error(str(e))  # where did it fail?

# Right
except ValueError:
    logger.exception('parse failed')  # includes traceback
```

❌ Mistake 2: Log and re-raise at every layer (duplicate logs)
```python
# Wrong
def a():
    try: b()
    except E as e:
        logger.exception('a failed'); raise  # b and c also log

# Right
# Log ONCE at the boundary; lower layers just raise or add context
```

❌ Mistake 3: Eager f-string formatting and leaking secrets
```python
# Wrong
logger.info(f'charge {card_number}')  # formats always, leaks PII

# Right
logger.info('charge order=%s', order_id)  # lazy, no secrets
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
import logging, sys  # imports
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(levelname)s %(message)s")  # setup
log = logging.getLogger("t")  # logger

try:  # first error
    1 / 0  # error
except ZeroDivisionError:  # catch
    log.info("A: info keeps no traceback")  # no traceback
    log.error("B: error without exc_info")  # no traceback
    log.exception("C: exception has traceback")  # traceback

log.warning("D: lazy %s formatting", "args")  # args formatted only if emitted
log.exception("E: outside except block")  # no active exception
```

**Answer**:
```
INFO A: info keeps no traceback
ERROR B: error without exc_info
ERROR C: exception has traceback
Traceback (most recent call last):
  File "/app/q.py", line 6, in <module>
    1 / 0  # error
    ~~^~~
ZeroDivisionError: division by zero
WARNING D: lazy args formatting
ERROR E: outside except block
NoneType: None
```
`log.info` and `log.error` record only the message; `log.exception` (ERROR level) also appends the active traceback, so only C shows one. The lazy `%s` style formats only if the record is emitted. Calling `log.exception` with no active exception prints `NoneType: None`, a sign you used it outside `except`.

---

## ⚫ Interview Questions + Answers

Q1: `logger.exception` vs `logger.error(exc_info=True)`?
A1: Same output. `exception()` is just `error()` with `exc_info=True` and should be called inside an except block.

Q2: Why use `%s` args instead of f-strings in logging?
A2: Formatting happens only if the level is enabled, and log systems can group records by the unformatted template.

Q3: Where should you log an error?
A3: Once, where you handle it (usually the boundary: request handler, job runner). Lower layers raise.

Q4: Why not use `print` for errors?
A4: No levels, no timestamps, no handlers, not configurable and often lost in production.

Q5: What should never be logged?
A5: Passwords, tokens, card numbers, personal data (PII). Log ids instead.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Every place an unexpected error is handled
- Background jobs and workers (nobody sees the console)
- Global exception handlers in web apps

❌ Avoid when:
- Logging the same error at every layer
- Logging secrets or full request bodies
- Using `exception()` outside an except block

---

## 📊 Visual Diagram

```
raise (low layer) ──► propagates ──► boundary except
                                         │
                      logger.exception(msg, extra=ids)
                                         │
                      handler ► console / file / JSON service
                                         │
                      return fallback or HTTP 500 (generic)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| logger | Object that writes log records | log लिखने वाला object |
| traceback | Call stack at the error | error के समय की call stack |
| exc_info | Attach exception details | exception का ब्योरा जोड़ना |
| handler | Sends records somewhere | record को कहीं भेजने वाला |
| level | DEBUG..CRITICAL severity | गंभीरता का स्तर |
| PII | Personal data | निजी जानकारी |

---

## ⚡ 3-Line Summary
English: Use `logger.exception` inside `except` to record the full traceback with context, log each error once at the boundary, and never log secrets. Return a generic message to clients.
Hindi: `except` के अंदर `logger.exception` से पूरा traceback context के साथ दर्ज करें, हर error boundary पर एक बार log करें और secrets कभी log न करें। Client को generic message दें।

---

## ➡️ Next Topic
**272. Error Handling Best Practices** — a checklist of rules for production error handling.

Verification: all code blocks above were executed on Python 3.13 and the "Real output" comments are the real output.

Note: the shown tracebacks use a neutral `/app` path (the real run used a scratch path).
