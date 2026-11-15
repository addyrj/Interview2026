---

# 267. Suppressing Exceptions
# हिंदी में: Exceptions को दबाना (Suppress करना)

---

## 🔵 Simple Definition (English)
Suppressing an exception means catching it on purpose and continuing without raising it again. It is correct only for errors that are expected and harmless, such as deleting a file that is already gone.

## 🔵 सरल परिभाषा (Hindi)
Exception suppress करने का मतलब है उसे जानबूझकर पकड़ लेना और दोबारा raise किए बिना आगे बढ़ना। यह सिर्फ़ उन errors के लिए सही है जो अपेक्षित और बेनुकसान हों, जैसे ऐसी file delete करना जो पहले से नहीं है।

---

## 🔴 Problem it Solves
Some failures are not real problems: "file does not exist" during cleanup, "key already removed" in a cache. Letting them crash the program is noise. But the wrong way (`except: pass`) hides real bugs too. We need a precise, readable way to ignore only specific, expected errors.

## 🔴 यह क्यों बना? (Hindi)
कुछ failures असली problem नहीं होतीं: cleanup में "file नहीं मिली", cache में "key पहले ही हट चुकी"। इन्हें crash होने देना बेकार है। लेकिन गलत तरीका (`except: pass`) असली bugs भी छुपा देता है। हमें सिर्फ़ specific और अपेक्षित errors ignore करने का साफ़ तरीका चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Identify the exact, harmless exception (e.g. FileNotFoundError)
Step 2 → Wrap only the single risky line in try / except SpecificError
Step 3 → Do nothing (pass) or log at debug level
Step 4 → Continue with the program
Step 5 → Everything else still raises normally
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → ठीक वही बेनुकसान exception पहचानिए (जैसे FileNotFoundError)
Step 2 → सिर्फ़ उस एक risky line को try / except SpecificError में रखिए
Step 3 → कुछ मत कीजिए (pass) या debug level पर log कीजिए
Step 4 → Program आगे चलने दीजिए
Step 5 → बाकी सब errors सामान्य रूप से raise होंगी
```

---

## 🟡 Real World Example
A Razorpay report job writes a temp CSV and removes it at the end. If an earlier retry already removed it, `FileNotFoundError` is fine. A Redis cache invalidation that deletes a missing key is the same idea: the goal state ("it is gone") is already true.

## 🟡 Real Example Hindi mein
Razorpay का report job temp CSV बनाकर अंत में हटाता है। अगर पहले retry में हट चुकी है तो `FileNotFoundError` ठीक है। Redis cache में missing key delete करना भी यही है: मनचाही स्थिति ("हट गई") पहले से सही है।

---

## 💻 Code Example — Basic
```python
# Basic suppression - every line commented
import os  # file operations
import tempfile  # create a safe temp file

fd, path = tempfile.mkstemp()  # create a real temp file
os.close(fd)  # close the OS handle, we only need the path
os.remove(path)  # delete it once

try:  # delete it again - this will fail
    os.remove(path)  # file no longer exists
except FileNotFoundError:  # catch ONLY the expected error
    print("already gone, fine")  # harmless, continue
# Output: already gone, fine

try:  # a different error must NOT be hidden
    int("abc")  # ValueError
except FileNotFoundError:  # wrong type, so this does not match
    pass  # never reached
except ValueError as exc:  # real bug surfaces here
    print("real error:", exc)  # shows the problem
# Output: real error: invalid literal for int() with base 10: 'abc'
```

## 💻 Code Example — Advanced
```python
# Production style: targeted suppression with logging, no silent bugs
import logging  # standard logging
import os  # file removal
import tempfile  # temp file
from pathlib import Path  # path object
from typing import Optional  # type hints

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")  # show logs
log: logging.Logger = logging.getLogger("cleanup")  # module logger


def remove_quietly(path: Path) -> bool:  # returns True if we removed it
    """Delete a file; a missing file is not an error."""
    try:  # smallest possible try block
        path.unlink()  # raises FileNotFoundError if missing
    except FileNotFoundError:  # expected case only
        log.debug("not found, skipping: %s", path.name)  # leave a breadcrumb
        return False  # nothing was removed
    except PermissionError:  # a real problem: do not hide it
        log.error("no permission: %s", path)  # record it
        raise  # re-raise unchanged
    return True  # removed successfully


def get_or_none(data: dict[str, int], key: str) -> Optional[int]:  # safe lookup
    try:  # try direct access
        return data[key]  # KeyError if missing
    except KeyError:  # expected: key may be absent
        return None  # convert to a value, not silence


tmp: Path = Path(tempfile.mkdtemp()) / "report.csv"  # a path inside a new temp dir
tmp.write_text("a,b")  # create the file
print(remove_quietly(tmp))  # first call removes it
# Output: True
print(remove_quietly(tmp))  # second call finds nothing (also logs DEBUG line)
# Output: DEBUG not found, skipping: report.csv  (logged to stderr)
#         False
print(get_or_none({"a": 1}, "b"))  # missing key
# Output: None
os.rmdir(tmp.parent)  # clean the temp directory
```

---

## 🟠 JavaScript vs Python Comparison
Both languages can swallow errors. Python's idiom is a narrow `except SomeError`; in JS people often write an empty `catch {}` that hides everything.

```python
# Python way
try:
    os.remove("old.log")          # may not exist
except FileNotFoundError:         # narrow, explicit
    pass
```
```javascript
// JavaScript way
try {
  fs.unlinkSync("old.log");       // may not exist
} catch (e) {
  if (e.code !== "ENOENT") throw e; // JS has one catch, so re-throw others
}
```

Key differences: Python can filter by class in the `except` clause, so you never need to re-throw. JS has one `catch`, so you check `e.code` or `instanceof` manually.

---

## 🟠 FastAPI Connection
Background cleanup after a request (deleting an uploaded temp file) is a typical safe suppression. Do not suppress errors in the request path itself, because the client needs to know.

```python
# FastAPI: cleanup task that ignores a missing file
from pathlib import Path  # path handling
from fastapi import BackgroundTasks, FastAPI  # app and background tasks

app: FastAPI = FastAPI()  # create app


def cleanup(path: str) -> None:  # runs after the response is sent
    try:
        Path(path).unlink()  # remove the temp upload
    except FileNotFoundError:  # already removed by another worker
        pass  # fine


@app.post("/upload")  # POST /upload
def upload(tasks: BackgroundTasks) -> dict[str, str]:
    tasks.add_task(cleanup, "/tmp/upload.tmp")  # schedule cleanup
    return {"status": "ok"}  # response goes out first
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Bare `except: pass`
```python
# Wrong - hides typos, KeyboardInterrupt, everything
try:
    risky()
except:
    pass

# Right - name the exact error
try:
    risky()
except FileNotFoundError:
    pass
```

❌ Mistake 2: Wrapping too many lines
```python
# Wrong - a bug in parse() is also hidden
try:
    data = load()
    parse(data)
    save(data)
except ValueError:
    pass

# Right - only the harmless line is guarded
data = load()
try:
    parse(data)
except ValueError:
    log.warning("bad row skipped")
save(data)
```

❌ Mistake 3: Suppressing without any trace
```python
# Wrong - nobody will ever know it happened
except KeyError:
    pass

# Right - at least a debug log for investigation
except KeyError:
    log.debug("key missing", exc_info=True)
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
def f() -> str:
    try:
        return "try"
    finally:
        print("cleanup")

def g() -> str:
    for _ in range(1):
        try:
            raise ValueError("x")
        finally:
            return "swallowed"

print(f())
print(g())
```

**Answer**:
```
cleanup
try
swallowed
```
`finally` runs before `f` returns, so "cleanup" prints first. In `g`, a `return` inside `finally` discards the in-flight `ValueError`: the exception is silently suppressed. This is an accidental suppression and a classic trap (Python 3.14 warns about it via PEP 765, but earlier versions stay silent).

---

## ⚫ Interview Questions + Answers

Q1: Is `except Exception: pass` acceptable?
A1: Almost never. It hides real bugs. Catch the narrowest type, keep the try block tiny, and log.

Q2: What is the difference between `except:` and `except Exception:`?
A2: Bare `except:` also catches `KeyboardInterrupt` and `SystemExit` (BaseException). `except Exception` does not.

Q3: How can a `finally` block suppress an exception?
A3: A `return`, `break` or `continue` inside `finally` cancels the active exception. Avoid it.

Q4: Is suppression the same as handling?
A4: No. Handling means recovering (retry, fallback, default). Suppressing means ignoring because the outcome is already acceptable.

Q5: What is the cleaner modern way to suppress?
A5: `contextlib.suppress(FileNotFoundError)` as a context manager (next topic).

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Cleanup of something that may already be gone
- Idempotent operations (delete if exists)
- Optional enrichment where failure is acceptable (with logging)

❌ Avoid when:
- The error means data loss or a wrong result
- You catch a broad class (`Exception`) with no logging
- The client or caller needs to know something failed

---

## 📊 Visual Diagram

```
 risky line
     │
     ├── FileNotFoundError ──► expected ──► log.debug ──► continue
     │
     ├── PermissionError   ──► real issue ─► log.error ──► raise
     │
     └── any other bug     ──► not caught ─► propagates up
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Suppress | Catch and ignore on purpose | जानबूझकर पकड़कर अनदेखा करना |
| Idempotent | Same result if repeated | बार-बार करने पर भी वही नतीजा |
| Bare except | `except:` with no type | बिना type वाला except |
| Swallow | Hide an error silently | error को चुपचाप दबा देना |
| Breadcrumb | Small log hint | debug के लिए छोटा log संकेत |
| Narrow catch | Catch a specific type | खास type पकड़ना |

---

## ⚡ 3-Line Summary
English: Suppress only expected, harmless errors, using the narrowest exception type and the smallest try block. Never use bare `except: pass`. Log a debug line so the event is traceable.
Hindi: सिर्फ़ अपेक्षित और बेनुकसान errors suppress कीजिए, सबसे छोटे exception type और try block के साथ। कभी bare `except: pass` मत लिखिए। Debug log रखिए ताकि घटना trace हो सके।

---

## ➡️ Next Topic
**268. contextlib.suppress** — the clean one-line way to ignore specific exceptions.
