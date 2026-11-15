---

# 156. Reference Counting
# हिंदी में: Reference Counting (Reference गिनती)

---

## 🔵 Simple Definition (English)
Every CPython object keeps a number called its reference count: how many names, containers or other objects currently point to it. When a new reference is created the count goes up; when one disappears it goes down. The moment the count reaches zero, the object is destroyed and its memory is released immediately.

## 🔵 सरल परिभाषा (Hindi)
CPython का हर object एक संख्या रखता है जिसे reference count कहते हैं: अभी कितने नाम, containers या दूसरे objects उसकी ओर इशारा कर रहे हैं। नया reference बनने पर count बढ़ता है; कोई reference हटने पर घटता है। जैसे ही count शून्य होता है, object नष्ट हो जाता है और उसकी memory तुरंत मुक्त हो जाती है।

---

## 🔴 Problem it Solves
Manual memory management is error-prone: forget to free and memory leaks, free too early and the program crashes. Reference counting lets Python decide automatically and predictably when an object is no longer needed. Unlike a tracing garbage collector, cleanup happens at a known moment (when the last reference goes), so files, sockets and locks owned by objects are released promptly.

## 🔴 यह क्यों बना? (Hindi)
Manual memory management में गलती आसान है: free भूलने पर leak, जल्दी free करने पर crash। Reference counting से Python अपने आप और अनुमानित समय पर तय करता है कि object की अब जरूरत नहीं है। Tracing garbage collector के विपरीत, cleanup एक तय पल पर होता है (जब आखिरी reference हटता है), इसलिए objects के files, sockets और locks जल्दी release होते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → An object is created: refcount = 1 (the name that received it)
Step 2 → Increase (+1): assignment (b = a), appending to a list/dict, passing to a function,
         storing as attribute, closure capture
Step 3 → Decrease (-1): del name, name rebinding, leaving a function scope, removing from a
         container, container itself destroyed
Step 4 → sys.getrefcount(obj) shows count + 1, because the argument itself is a temporary reference
Step 5 → Count reaches 0 → __del__ (if any) runs → memory is freed instantly (deterministic)
Step 6 → Freeing an object decrements everything IT referenced, so cleanup cascades
Step 7 → Weak references (weakref) do NOT increase the count
Step 8 → Limit: cycles (A -> B -> A) never reach 0 → handled by the cyclic GC (next topics)
Step 9 → Python 3.12+: "immortal" objects (None, True, small ints...) have a fixed huge count
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Object बनता है: refcount = 1 (जिस नाम को मिला)
Step 2 → बढ़ता है (+1): assignment (b = a), list/dict में जोड़ना, function को देना,
         attribute में रखना, closure में पकड़ना
Step 3 → घटता है (-1): del name, नाम का दोबारा bind होना, function scope छोड़ना,
         container से हटाना, container का खुद नष्ट होना
Step 4 → sys.getrefcount(obj) असली count + 1 दिखाता है, क्योंकि argument खुद एक temporary reference है
Step 5 → Count 0 होते ही → __del__ (अगर है) चलता है → memory तुरंत free होती है (deterministic)
Step 6 → किसी object के free होने पर उसके द्वारा पकड़े गए सभी objects का count घटता है, यानी cleanup श्रृंखला में चलता है
Step 7 → Weak references (weakref) count नहीं बढ़ाते
Step 8 → सीमा: cycles (A -> B -> A) कभी 0 नहीं होते → cyclic GC संभालता है (अगले topics)
Step 9 → Python 3.12+: "immortal" objects (None, True, छोटे ints...) का count fixed और बहुत बड़ा होता है
```

---

## 🟡 Real World Example
A request handler opens a database connection object. When the function returns, the local variable disappears, the count reaches zero, and the connection is closed right away, before the next request arrives. A cache keeps a `WeakValueDictionary` of heavy sessions: entries vanish automatically when no request uses a session, without the cache keeping it alive. That is why reference counting is good for resources like files and sockets.

## 🟡 Real Example Hindi mein
Request handler एक database connection object खोलता है। Function लौटते ही local variable खत्म होता है, count शून्य होता है और connection तुरंत बंद हो जाता है, अगली request आने से पहले। Cache भारी sessions का `WeakValueDictionary` रखता है: जब कोई request session इस्तेमाल नहीं करती तो entry अपने आप गायब हो जाती है, cache उसे जिंदा नहीं रखता। इसी कारण reference counting files और sockets जैसे resources के लिए अच्छा है।

---

## 💻 Code Example — Basic
```python
# Reference counting: watch the count change
import sys                                                # getrefcount


class Resource:
    def __init__(self, name: str) -> None:
        self.name: str = name
        print(f"{name} created")

    def __del__(self) -> None:
        print(f"{self.name} destroyed")                   # runs when refcount hits 0


r = Resource("db-conn")                                   # count: 1 (name r)
print(sys.getrefcount(r))                                 # 2 (r + temporary argument inside getrefcount)
alias = r                                                 # count +1
box = [r]                                                 # count +1 (list holds a reference)
print(sys.getrefcount(r))                                 # 4
del alias                                                 # count -1
box.clear()                                               # count -1
print(sys.getrefcount(r))                                 # 2 again
print("deleting last reference")
del r                                                     # count -> 0: __del__ runs RIGHT NOW
print("after del")

# Output:
# db-conn created
# 2
# 4
# 2
# deleting last reference
# db-conn destroyed
# after del
```

## 💻 Code Example — Advanced
```python
# Production style: scope-based release, weakref cache, cycle limits, immortal objects (3.12+)
import gc                                                 # cycle collector
import sys                                                # getrefcount
import weakref                                            # references that do not count


class Session:
    def __init__(self, user: str) -> None:
        self.user: str = user

    def __del__(self) -> None:
        print(f"session({self.user}) released")


def handle_request() -> None:
    s = Session("riya")                                   # count 1 inside the function
    print("handling", s.user)
    # function ends -> local name s disappears -> count 0 -> freed here


handle_request()
print("after request")

registry: "weakref.WeakValueDictionary[str, Session]" = weakref.WeakValueDictionary()
sess = Session("aman")                                    # strong reference
registry["aman"] = sess                                   # weak: does NOT add to the count
print(sys.getrefcount(sess), "aman" in registry)          # 2 True
del sess                                                  # last strong ref gone
print("aman" in registry)                                 # False: entry vanished automatically


class Node:
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.other: "Node | None" = None

    def __del__(self) -> None:
        print(f"node {self.name} freed")


gc.disable()                                              # make the demo deterministic
n1, n2 = Node("A"), Node("B")
n1.other, n2.other = n2, n1                               # reference cycle A <-> B
del n1, n2                                                # counts drop to 1, NOT 0
print("cycle still alive after del")
print("collected:", gc.collect() >= 2)                     # GC finds and frees the cycle
gc.enable()

print(sys.getrefcount(None) > 1000)                       # None is immortal in 3.12+; count is huge

# Output:
# handling riya
# session(riya) released
# after request
# 2 True
# session(aman) released
# False
# cycle still alive after del
# node A freed
# node B freed
# collected: True
# True
```
Both blocks were run on Python 3.13.3 and printed exactly this. Before Python 3.12, `sys.getrefcount(None)` was a normal (large) count and not fixed; the immortal-object behaviour (PEP 683) starts in 3.12. In other interpreters (PyPy, Jython) there is no reference counting, so `__del__` timing differs.

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python (CPython) | JavaScript (V8) |
|---------|------------------|-----------------|
| Freeing | immediately at count 0 | later, when GC runs |
| Cycles | need extra cyclic GC | handled naturally by tracing GC |
| Weak references | `weakref.ref`, `WeakValueDictionary` | `WeakRef`, `WeakMap`, `WeakSet` |
| Observe the count | `sys.getrefcount` | not possible |
| Destructor | `__del__` (prompt in CPython) | `FinalizationRegistry` (not guaranteed to run) |

```python
# Python way
import sys
class Tmp:
    def __del__(self): print("freed now")
t = Tmp()
del t                                  # prints "freed now" immediately (CPython)
print("next line")
```
```javascript
// JavaScript way
let t = { name: "tmp" };
const reg = new FinalizationRegistry(() => console.log("freed sometime"));
reg.register(t, "tmp");
t = null;                              // may be collected much later, or never during a short run
console.log("next line");
```

Key difference: in CPython you can rely on prompt cleanup when the last reference disappears (still, prefer `with` for resources). In JavaScript you can never predict when garbage collection happens.

---

## 🟠 FastAPI Connection
FastAPI dependencies with `yield` rely on scope-based cleanup: the connection is created for one request, then closed in `finally` when the response is done. After that, the last reference disappears and the object is freed. Never rely on `__del__` for closing connections; use `yield`/`finally` or `with`.

```python
# FastAPI example — per-request resource, released after the response
from collections.abc import Iterator                        # generator type
from fastapi import Depends, FastAPI                        # FastAPI parts
from fastapi.testclient import TestClient                   # in-process client


class Conn:
    def __init__(self) -> None:
        print("conn opened")

    def close(self) -> None:
        print("conn closed")

    def __del__(self) -> None:
        print("conn object freed")                          # refcount reached 0


def get_conn() -> Iterator[Conn]:
    conn = Conn()                                           # created for this request
    try:
        yield conn                                          # given to the route
    finally:
        conn.close()                                        # explicit cleanup, always runs


app: FastAPI = FastAPI()


@app.get("/ping")
def ping(conn: Conn = Depends(get_conn)) -> dict[str, str]:
    return {"status": "ok"}


print(TestClient(app).get("/ping").json())

# Output:
# conn opened
# conn closed
# conn object freed
# {'status': 'ok'}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting that `getrefcount` adds one
✅ Correct: subtract 1 (and expect extra counts inside functions)

```python
import sys
x = []
print(sys.getrefcount(x))      # 2  (not 1): the argument is a temporary reference
def f(a): return sys.getrefcount(a)
print(f(x))                    # 3  (name x + parameter a + temporary)
```

❌ Mistake 2: Relying on `__del__` for important cleanup
✅ Correct: use `with` (context manager) or `try/finally`

```python
# Wrong: closing a file/connection only inside __del__ (timing is not guaranteed,
#        e.g. cycles, exceptions holding frames, other interpreters, interpreter shutdown)
# Right:
with open("data.txt", "w") as fh:      # closed exactly at the end of the block
    fh.write("ok")
```

❌ Mistake 3: Keeping a hidden reference and wondering why memory is not freed
✅ Correct: remove every reference (list, cache, exception traceback, global)

```python
class R:
    def __del__(self): print("freed")
r = R(); lst = [r]; del r
print("still in list")         # the list still holds it
lst.clear()                    # freed printed here; now the count is 0
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
import sys
x = []
print(sys.getrefcount(x))
def f(a):
    return sys.getrefcount(a)
print(f(x))
y = x
print(sys.getrefcount(x))
d = {"k": x}
print(sys.getrefcount(x))
```
Answer: `2`, `3`, `3`, `4`. The first call counts the name `x` plus the temporary argument. Inside `f`, the parameter `a` is one more reference (the exact number can differ between versions). After `y = x` the count of the object is 3 (x, y, argument) and putting it into a dict raises it to 4. Remember: assignment never copies; it adds a reference.

---

## ⚫ Interview Questions + Answers

Q1: How does reference counting work and what are its limits?
A1: Each object stores a counter of references. Creating a reference increments it, removing one decrements it, and at zero the object is freed at once. The limit is cycles: objects referencing each other never reach zero, so Python also has a cyclic garbage collector. Counting also costs a little on every assignment and is a reason for the GIL.

Q2: Why does `sys.getrefcount` return one more than expected?
A2: Passing the object as an argument creates a temporary reference during the call.

Q3: What is an immortal object (Python 3.12+)?
A3: Objects such as `None`, `True`, `False` and small ints get a special fixed refcount; increments and decrements are skipped for them (PEP 683). This helps multi-core scaling and copy-on-write memory sharing after `fork`.

Q4: How can you hold an object without increasing its count?
A4: With `weakref.ref`, `WeakValueDictionary` or `WeakSet`. When the last strong reference disappears, the weak reference becomes dead (`None`) automatically. Useful for caches and observer lists.

Q5: Does `del x` delete the object?
A5: No. It removes the name `x` and decrements the object's count. The object is destroyed only if that was the last reference.

---

## 🔷 When to Use + When Not to Use
✅ Rely on reference counting when:
- You want local temporary objects to be released as soon as a function returns
- You build caches with weak references
- You debug leaks by inspecting who still references an object (`gc.get_referrers`)

❌ Do not depend on it when:
- You need guaranteed resource cleanup (use `with` / `try-finally`)
- You write code that must also run on PyPy or other implementations
- You use reference cycles (parent <-> child links) without weakrefs, since the count never reaches zero

---

## 📊 Visual Diagram
```
 a = Obj()        refcount 1     a ───────►[Obj | rc=1]
 b = a            refcount 2     a ───────►[Obj | rc=2]◄─────── b
 lst = [a]        refcount 3     lst[0] ──►[Obj | rc=3]
 del a            refcount 2
 del b            refcount 1
 lst.clear()      refcount 0  ─► __del__ ─► memory freed immediately

 Cycle:   A ───► B          counts never reach 0 even after you delete your names
          ▲      │          (A.rc=1 from B, B.rc=1 from A)  → cyclic GC needed
          └──────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Reference count | Number of references to an object | Object की ओर references की संख्या |
| `__del__` | Method run just before an object is destroyed | Object नष्ट होने से पहले चलने वाला method |
| Weak reference | Reference that does not keep the object alive | Object को जिंदा न रखने वाला reference |
| Immortal object | Object with a fixed, never-freed count (3.12+) | Fixed count वाला कभी न मरने वाला object |
| Reference cycle | Objects pointing to each other in a loop | आपस में loop में इशारा करने वाले objects |
| Deterministic | Happens at a known, predictable moment | अनुमानित समय पर होने वाला |

---

## ⚡ 3-Line Summary
English: CPython counts references to every object and frees the object the instant the count hits zero. `sys.getrefcount` shows one extra count; weak references do not count; cycles are not solved by counting alone. Use `with` for resources instead of trusting `__del__`.
Hindi: CPython हर object के references गिनता है और count शून्य होते ही object को तुरंत free कर देता है। `sys.getrefcount` एक extra count दिखाता है; weak references नहीं गिने जाते; cycles अकेले counting से हल नहीं होते। Resources के लिए `__del__` की जगह `with` इस्तेमाल करें।

---

## ➡️ Next Topic
**157. Garbage Collection** — the cyclic collector, generations (0, 1, 2), thresholds and how cycles get cleaned.
