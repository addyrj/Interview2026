---

# 199. Logging Module — Complete Guide
# हिंदी में: Logging Module — पूरी Guide

---

## 🔵 Simple Definition (English)
Python's built-in `logging` module provides production-grade logging with levels (DEBUG, INFO, WARNING, ERROR, CRITICAL), handlers (console, file, rotating file), formatters (plain text, JSON), and loggers (per-module). Never use `print()` for debugging in production — `logging` gives you control over level filtering, output destinations, and structured format. FastAPI/uvicorn also uses Python logging.

## 🔵 सरल परिभाषा (Hindi)
Python `logging` module production-grade logging देता है। Levels (DEBUG → CRITICAL), handlers (console, file), formatters, loggers। Production में `print()` नहीं — `logging` use करो। Level filtering, output destinations, structured format मिलता है।

---

## 💻 Code Example — Basic
```python
import logging

# ─── Basic setup (for scripts) ────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG,           # minimum level to show
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)  # logger named after current module

# ─── Log levels (ascending severity) ─────────────────────────────
logger.debug("Detailed debug info: variable x = %s", x)   # level 10
logger.info("User logged in: user_id=%d", user_id)         # level 20
logger.warning("Disk space low: %d%% remaining", pct)      # level 30
logger.error("Payment failed for order %s", order_id)      # level 40
logger.critical("Database connection lost!")                # level 50

# ─── Log with exception info ──────────────────────────────────────
try:
    result = risky_operation()
except Exception as e:
    logger.error("Operation failed: %s", str(e), exc_info=True)
    # exc_info=True adds the full traceback to the log entry

# Or:
logger.exception("Operation failed")  # automatically includes traceback

# ─── Level filtering ──────────────────────────────────────────────
# If logger level is WARNING, DEBUG and INFO are ignored:
logger.setLevel(logging.WARNING)
logger.debug("This won't appear")   # filtered out
logger.info("Neither will this")    # filtered out
logger.warning("This appears")      # shown
```

## 💻 Code Example — Advanced
```python
import logging
import logging.handlers
import json
from datetime import datetime

# ─── Per-module loggers (production pattern) ──────────────────────
# In each module:
logger = logging.getLogger(__name__)   # e.g. "myapp.routers.users"

# Module logger hierarchy:
# root → myapp → myapp.routers → myapp.routers.users
# Setting level on parent affects children unless child sets its own

# ─── Application-wide logging config ─────────────────────────────
def setup_logging(level: str = "INFO") -> None:
    """Configure logging for the entire application."""
    
    # Console handler:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    ))
    
    # Rotating file handler (keeps last 5 files of 10MB each):
    file_handler = logging.handlers.RotatingFileHandler(
        "app.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s:%(lineno)d | %(message)s"
    ))
    
    # Root logger:
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Silence noisy third-party loggers:
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

# ─── JSON logging (for production/observability tools) ────────────
class JSONFormatter(logging.Formatter):
    """Format log records as JSON for log aggregators (Datadog, ELK)."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)

# ─── Structured logging with extra context ────────────────────────
logger = logging.getLogger(__name__)

def process_request(request_id: str, user_id: int):
    # Add context to all log messages in this function:
    extra = {"request_id": request_id, "user_id": user_id}
    
    logger.info("Processing request", extra=extra)
    logger.debug("Request details loaded", extra=extra)
    
    try:
        result = do_work()
        logger.info("Request completed", extra={**extra, "result_count": len(result)})
        return result
    except Exception as e:
        logger.error("Request failed", extra=extra, exc_info=True)
        raise

# ─── FastAPI + logging setup ──────────────────────────────────────
from fastapi import FastAPI, Request
import time

app = FastAPI()
logger = logging.getLogger("myapp.api")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    logger.info(
        "Incoming request",
        extra={"method": request.method, "path": request.url.path}
    )
    
    response = await call_next(request)
    duration = (time.time() - start) * 1000
    
    logger.info(
        "Request complete",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "duration_ms": round(duration, 2),
        }
    )
    return response

# ─── logging.config.dictConfig (production configuration) ─────────
import logging.config

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        },
        "json": {
            "()": JSONFormatter,   # custom class
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "app.log",
            "maxBytes": 10_485_760,
            "backupCount": 5,
            "formatter": "json",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "file"],
    },
    "loggers": {
        "uvicorn": {"level": "WARNING"},
        "sqlalchemy": {"level": "WARNING"},
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python:
import logging
logger = logging.getLogger(__name__)

logger.info("User logged in: %s", user_id)
logger.error("Payment failed", exc_info=True)

# Levels: DEBUG=10, INFO=20, WARNING=30, ERROR=40, CRITICAL=50
```

```javascript
// JavaScript (using Winston or Pino):
import winston from 'winston';
const logger = winston.createLogger({
    level: 'info',
    format: winston.format.json(),
    transports: [new winston.transports.Console()],
});

logger.info('User logged in', { userId });
logger.error('Payment failed', { error: err.message, stack: err.stack });
// Levels: error=0, warn=1, info=2, http=3, verbose=4, debug=5, silly=6
```

Key differences:
- Python has `logging` built-in. Node.js needs third-party (Winston, Pino, Bunyan).
- Python levels: DEBUG < INFO < WARNING < ERROR < CRITICAL.
- Python `exc_info=True` or `.exception()` auto-attaches traceback.
- Python logger hierarchy (by name) lets you control verbosity per module.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `print()` instead of `logging` in production
```python
# Wrong — no level control, no timestamps, no destinations:
print(f"DEBUG: User {user_id} logged in")

# Correct:
logger.info("User logged in", extra={"user_id": user_id})
```

❌ Mistake 2: Using f-strings in log calls (eager formatting)
```python
# Wrong — string formatted even if level is filtered out:
logger.debug(f"Processing {len(items)} items: {items}")   # always formats

# Correct — lazy formatting (only formats if level is active):
logger.debug("Processing %d items: %s", len(items), items)
```

---

## 🧠 Tricky Interview Question

**Q**: `logging.getLogger("myapp.routers")` and `logging.getLogger("myapp.routers.users")` — are they related? How does propagation work?

**Answer**: Yes — loggers form a **hierarchy** by dot-separated names. `myapp.routers.users` is a child of `myapp.routers`, which is a child of `myapp`, which is a child of the root logger. By default, `propagate=True` — a log record travels up the hierarchy to all parent handlers. So a record logged at `myapp.routers.users` also goes to `myapp.routers` and `myapp` and root handlers. Set `propagate=False` to stop propagation. This lets you add a handler to `myapp` and all submodule loggers automatically send to it.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between a Logger, Handler, and Formatter?
A1: **Logger** (`logging.getLogger(name)`): the entry point — receives `logger.info()` calls. Sets minimum level for the logger. **Handler** (StreamHandler, FileHandler, etc.): determines WHERE the log goes (console, file, network). Each handler has its own level. **Formatter**: determines FORMAT of the message (timestamp, level, message, traceback). One logger → multiple handlers → each handler has one formatter. Hierarchy: Logger → filter by level → propagate to handlers → each handler formats and outputs.

Q2: When should you use `logger.exception()` vs `logger.error(exc_info=True)`?
A2: They're equivalent — `logger.exception(msg)` is exactly `logger.error(msg, exc_info=True)`. Both log at ERROR level with the full traceback appended. Stylistic: `exception()` is more explicit about "an exception occurred." Only call `logger.exception()` inside an `except` block (where `exc_info` is available). Outside an except block, `exc_info=True` returns `None` (no traceback). Convention: `logger.exception()` in except handlers, `logger.error("...", exc_info=True)` when you have explicit exc_info tuple.

Q3: How do you prevent log duplication?
A3: Log duplication happens when multiple handlers are added to the same logger (often by calling `basicConfig()` multiple times or adding handlers in a loop). Fix: (1) Check `if not logger.handlers:` before adding. (2) Set `disable_existing_loggers: false` in `dictConfig`. (3) Use `logging.config.dictConfig()` instead of `basicConfig()` for one-time setup. (4) Call setup only once at application startup. In FastAPI: configure in the `lifespan` startup event or in `main.py` before `uvicorn.run()`.

Q4: How do you configure different log levels for different modules?
A4: Get the specific module's logger and set its level: `logging.getLogger("sqlalchemy").setLevel(logging.WARNING)` — suppresses SQLAlchemy DEBUG/INFO while root logger shows them for your code. In `dictConfig`: `"loggers": {"sqlalchemy": {"level": "WARNING", "propagate": False}}`. Setting `propagate=False` prevents SQLAlchemy logs from bubbling to root logger's handlers at all — use this when you want to completely silence a noisy library.

Q5: What is `RotatingFileHandler` and why use it in production?
A5: `RotatingFileHandler(filename, maxBytes=10MB, backupCount=5)`: when log file reaches `maxBytes`, it renames `app.log` → `app.log.1`, `app.log.1` → `app.log.2`, etc., up to `backupCount` files, then starts fresh. Prevents single log file from growing unbounded and filling disk. Alternative: `TimedRotatingFileHandler` — rotates at midnight or weekly intervals. In containerized apps (Docker/Kubernetes), often log to stdout (StreamHandler) and let the orchestrator handle rotation/collection.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Logger | Entry point for log calls | Log calls का entry point |
| Handler | Where logs go (file/console) | Logs कहाँ जाएं |
| Formatter | Log message format | Log message का format |
| Level | DEBUG/INFO/WARNING/ERROR/CRITICAL | Severity level |
| propagate | Pass to parent logger | Parent logger को pass करें |
| exc_info | Include traceback | Traceback include करें |
| RotatingFileHandler | Auto-rotate log files | Log files automatically rotate |

---

## ⚡ 3-Line Summary
English: Use `logging.getLogger(__name__)` in every module — never `print()` in production. Set up handlers and formatters once at app startup with `dictConfig` or `basicConfig`. Use `logger.exception()` inside `except` blocks to automatically include tracebacks in the log.
Hindi: हर module में `logging.getLogger(__name__)` use करो — `print()` नहीं। Startup पर एक बार handlers setup करो। `except` blocks में `logger.exception()` से traceback automatically log होती है।

---

## ➡️ Next Topic
**200. Logging Best Practices** — structured logging, correlation IDs, log aggregation. Back to **196. sys Module** — sys.argv, sys.exit, sys.path.
