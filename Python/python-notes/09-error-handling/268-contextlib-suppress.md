---

# 268. contextlib.suppress
# हिंदी में: contextlib.suppress (चुनी हुई errors को चुपचाप छोड़ना)

---

## 🔵 Simple Definition (English)
`contextlib.suppress(*exceptions)` is a context manager that silently ignores the listed exceptions inside a `with` block. It replaces a `try/except X: pass` and makes the intent clear.

## 🔵 सरल परिभाषा (Hindi)
`contextlib.suppress(*exceptions)` एक context manager है जो `with` block के अंदर बताई गई exceptions को चुपचाप ignore कर देता है। यह `try/except X: pass` की जगह लेता है और इरादा साफ़ दिखाता है।

---

## 🔴 Problem it Solves
Cleanup code often has an error you truly do not care about, like deleting a file that is already gone. Writing four lines of `try/except/pass` everywhere is noisy. `suppress` states "this error is expected and fine" in two lines, and only for the types you name.

## 🔴 यह क्यों बना? (Hindi)
Cleanup code में अक्सर ऐसी error होती है जिसकी परवाह नहीं, जैसे पहले से हटी file को delete करना। हर जगह चार line का `try/except/pass` शोर बढ़ाता है। `suppress` दो line में कहता है "यह error अपेक्षित है और ठीक है", और सिर्फ़ उन्हीं types के लिए जिनका नाम दिया हो।

---

## 🟢 How it Works — Step by Step

```
Step 1 → with suppress(ErrorType): starts the block
Step 2 → Code inside runs normally line by line
Step 3 → If a listed exception is raised, the rest of the block is skipped
Step 4 → Python leaves the with block and continues AFTER it
Step 5 → Exceptions not in the list propagate as usual
Step 6 → Internally __exit__ returns True only when isinstance(exc, listed types)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → with suppress(ErrorType): से block शुरू होता है
Step 2 → अंदर का code सामान्य रूप से चलता है
Step 3 → listed exception आते ही block का बाकी हिस्सा छूट जाता है
Step 4 → Python with block से निकलकर उसके बाद वाले code पर चलता है
Step 5 → list में न होने वाली exceptions सामान्य रूप से ऊपर जाती हैं
Step 6 → अंदर से __exit__ तभी True लौटाता है जब exception listed types की हो
```

---

## 🟡 Real World Example
A Razorpay cleanup job deletes temp invoices with `suppress(FileNotFoundError)` so a rerun never crashes. An idempotent `DELETE /cart/{id}` endpoint in FastAPI ignores a missing item. An asyncio worker uses `suppress(asyncio.CancelledError)` at shutdown.

## 🟡 Real Example Hindi mein
Razorpay cleanup job temp invoices को `suppress(FileNotFoundError)` से delete करता है ताकि दोबारा चलाने पर crash न हो। FastAPI का idempotent `DELETE /cart/{id}` missing item को ignore करता है। asyncio worker shutdown पर `suppress(asyncio.CancelledError)` इस्तेमाल करता है।

---

## 💻 Code Example — Basic
```python
# Basic contextlib.suppress - every line commented
import os  # for file removal
from contextlib import suppress  # the context manager

with suppress(FileNotFoundError):  # ignore ONLY this error
    os.remove("does_not_exist.tmp")  # would raise FileNotFoundError
print("continues after suppressed error")  # execution moves on

d: dict[str, int] = {"a": 1}  # sample dict
with suppress(KeyError):  # ignore missing key
    del d["zzz"]  # KeyError suppressed
print(d)  # dict unchanged

with suppress(ValueError, TypeError):  # several types allowed
    int(None)  # type: ignore[arg-type]  # TypeError suppressed
print("multiple types ok")  # reached

try:  # other errors are NOT suppressed
    with suppress(KeyError):  # only KeyError
        1 / 0  # ZeroDivisionError escapes
except ZeroDivisionError:  # caught outside
    print("ZeroDivisionError escaped suppress")  # proof

# --- Real output (run on Python 3.13; ids/timings may vary) ---
# continues after suppressed error
# {'a': 1}
# multiple types ok
# ZeroDivisionError escaped suppress
```

## 💻 Code Example — Advanced
```python
# Production style: idempotent cleanup, equivalent try/except, async + ExitStack
import asyncio  # for the async example
import tempfile  # safe temp files
from contextlib import suppress, ExitStack  # tools
from pathlib import Path  # paths


def remove_quietly(path: Path) -> bool:  # idempotent delete
    with suppress(FileNotFoundError):  # missing file is fine
        path.unlink()  # may raise
        return True  # reached only when delete worked
    return False  # file was already gone


tmp = Path(tempfile.mkdtemp()) / "cache.json"  # temp path
tmp.write_text("{}")  # create file
print(remove_quietly(tmp), remove_quietly(tmp))  # True then False


def long_form(path: Path) -> None:  # what suppress replaces
    try:  # long version
        path.unlink()  # delete
    except FileNotFoundError:  # swallow
        pass  # same behaviour


long_form(tmp)  # runs without error
print("long form ok")  # proof


async def worker() -> None:  # task that gets cancelled
    with suppress(asyncio.CancelledError):  # clean shutdown pattern
        await asyncio.sleep(10)  # long wait
    print("worker stopped quietly")  # reached after cancel


async def main() -> None:  # driver
    task = asyncio.create_task(worker())  # start worker
    await asyncio.sleep(0.01)  # let it start
    task.cancel()  # request cancel
    await task  # finishes without raising because of suppress


asyncio.run(main())  # run event loop

with ExitStack() as stack:  # several suppressors dynamically
    stack.enter_context(suppress(KeyError))  # add one
    {}["x"]  # swallowed
print("ExitStack ok")  # reached

# --- Real output (run on Python 3.13; ids/timings may vary) ---
# True False
# long form ok
# worker stopped quietly
# ExitStack ok
```

---

## 🟠 JavaScript vs Python Comparison
JavaScript has no built-in equivalent; you write an empty `catch {}`. Python's `suppress` is explicit, limited to named types and shows intent.

```python
from contextlib import suppress
import os
with suppress(FileNotFoundError):
    os.remove('a.tmp')   # missing file ignored
```
```javascript
const fs = require('fs');
try {
  fs.unlinkSync('a.tmp');
} catch (e) {
  if (e.code !== 'ENOENT') throw e;  // manual filtering
}
```

Key differences: JS needs a manual `if (e.code !== ...) throw e` to avoid swallowing everything. Python's `suppress` filters by type automatically and re-raises other errors.

---

## 🟠 FastAPI Connection
Use `suppress` for idempotent endpoints (delete, logout) and for best-effort cleanup (cache invalidation, temp files) in `yield` dependencies and background tasks. Do not use it to hide errors in your main business logic.

```python
# FastAPI: idempotent DELETE using suppress
from contextlib import suppress  # context manager
from fastapi import FastAPI  # app
from fastapi.testclient import TestClient  # client

app: FastAPI = FastAPI()  # app
CART: dict[int, str] = {1: "pen"}  # fake storage


@app.delete("/cart/{item_id}", status_code=204)  # DELETE is idempotent
def remove_item(item_id: int) -> None:
    with suppress(KeyError):  # deleting twice must not fail
        del CART[item_id]  # may raise KeyError


c = TestClient(app)  # client
print(c.delete("/cart/1").status_code)  # 204 first time
print(c.delete("/cart/1").status_code)  # 204 again, still fine
print(CART)  # empty now

# --- Real output (run on Python 3.13; ids/timings may vary) ---
# 204
# 204
# {}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Suppressing `Exception` (too broad)
```python
# Wrong
with suppress(Exception):
    save_order()  # real bugs vanish

# Right
with suppress(FileNotFoundError):
    path.unlink()  # one expected error
```

❌ Mistake 2: Expecting code after the failing line to run
```python
# Wrong
with suppress(KeyError):
    del d['a']
    print('deleted')  # skipped if KeyError

# Right
try:
    del d['a']
except KeyError:
    pass
else:
    print('deleted')
```

❌ Mistake 3: Using it when you need to log or count the failure
```python
# Wrong
with suppress(ValueError):
    n = int(raw)  # you lose all information

# Right
try:
    n = int(raw)
except ValueError:
    logger.warning('bad input %r', raw)
    n = 0
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
from contextlib import suppress  # import

def f() -> str:  # what is returned?
    with suppress(ValueError):  # suppress ValueError
        int("x")  # raises
        return "inside"  # skipped because of the error
    return "after"  # reached

print(f())  # after

try:  # outer guard so the script can finish
    with suppress(Exception):  # suppress normal errors only
        raise KeyboardInterrupt  # not an Exception subclass!
except KeyboardInterrupt:  # escapes suppress
    print("KeyboardInterrupt not suppressed")  # proof
```

**Answer**:
```
after
KeyboardInterrupt not suppressed
```
The `return 'inside'` never runs because `int('x')` fails first; `suppress` swallows the error and execution resumes after the `with` block, so `f()` returns `after`. `KeyboardInterrupt` is a `BaseException`, so `suppress(Exception)` does not stop it. (Also: `suppress` can handle `ExceptionGroup` members since Python 3.12.)

---

## ⚫ Interview Questions + Answers

Q1: Is suppress the same as try/except/pass?
A1: Functionally yes for the listed types. It is shorter and states the intent. It is slightly slower to set up, which rarely matters.

Q2: Does code after the failing line continue?
A2: No. The rest of the with block is skipped; execution continues after the block.

Q3: Can suppress be used with async code?
A3: Yes, inside `async def` you can wrap `await` calls in a normal `with suppress(...)`. It is a sync context manager but works around awaits.

Q4: Is it reusable?
A4: Yes. A `suppress` instance is reusable and reentrant (it keeps no per-use state).

Q5: When is `suppress` a bad idea?
A5: When the error matters, needs logging, or the block has many statements. Then use explicit `try/except`.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Deleting something that may already be gone
- Idempotent operations (delete, close, logout)
- Best-effort cleanup where failure is harmless

❌ Avoid when:
- Hiding real bugs with broad types like `Exception`
- Large blocks with many statements
- Cases where you must log or count the failure

---

## 📊 Visual Diagram

```
with suppress(KeyError):
    line 1  ✔
    line 2  ✖ KeyError ─┐ swallowed
    line 3  (skipped)   │
                        ▼
code after the with block continues
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| suppress | Ignore chosen exceptions | चुनी हुई errors ignore करना |
| context manager | Object used with `with` | `with` के साथ इस्तेमाल होने वाला object |
| idempotent | Same result if repeated | दोहराने पर भी वही नतीजा |
| swallow | Hide an exception | exception छुपा देना |
| __exit__ | Method called when leaving with | with छोड़ते समय चलने वाला method |
| best-effort | Try but accept failure | कोशिश करो, fail होने पर ठीक |

---

## ⚡ 3-Line Summary
English: `suppress(ErrorType)` ignores only the named exceptions inside a `with` block and continues after it. It replaces `try/except: pass` for expected, harmless failures. Keep the block tiny and the type specific.
Hindi: `suppress(ErrorType)` `with` block में सिर्फ़ बताई गई exceptions ignore करता है और block के बाद आगे बढ़ता है। यह अपेक्षित और हानिरहित failures के लिए `try/except: pass` की जगह लेता है। Block छोटा और type specific रखें।

---

## ➡️ Next Topic
**269. warnings Module** — soft alerts (deprecations) that do not stop the program.

Verification: all code blocks above were executed on Python 3.13 and the "Real output" comments are the real output.
