---

# 225. Lock + RLock
# हिंदी में: Lock और RLock (thread locks)

---

## 🔵 Simple Definition (English)
A `Lock` lets only one thread into a protected section at a time. An `RLock` (re-entrant lock) does the same, but the thread that already holds it can acquire it again without blocking, as long as it releases it the same number of times.

## 🔵 सरल परिभाषा (Hindi)
`Lock` एक समय में सिर्फ एक thread को protected हिस्से में आने देता है। `RLock` (re-entrant lock) भी यही करता है, पर जो thread उसे पहले से पकड़े है वह बिना block हुए उसे दोबारा acquire कर सकता है, बशर्ते उतनी ही बार release करे।

---

## 🔴 Problem it Solves
Shared data needs exclusive access. A plain `Lock` has a trap: if a method that holds the lock calls another method that needs the same lock, the thread waits for itself forever (self-deadlock). `RLock` solves this for classes whose methods call each other.

## 🔴 यह क्यों बना? (Hindi)
Shared data को exclusive access चाहिए। सादे `Lock` में एक जाल है: अगर lock पकड़े हुए method किसी दूसरे method को call करे जिसे वही lock चाहिए, तो thread खुद का इंतज़ार हमेशा करता रहता है (self-deadlock)। `RLock` उन classes के लिए यह हल करता है जिनके methods आपस में call होते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → lock.acquire() : free -> owner = this thread; else the caller blocks
Step 2 → Critical section runs
Step 3 → lock.release() : lock becomes free, one waiter wakes up
Step 4 → RLock extra: remembers owner + a counter
         same thread acquire again -> counter + 1 (no blocking)
         release -> counter - 1; at 0 the lock is really free
Step 5 → Prefer "with lock:" so release happens even on exceptions
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → lock.acquire() : खाली हो तो owner = यह thread; नहीं तो caller block
Step 2 → Critical section चलता है
Step 3 → lock.release() : lock खाली, एक इंतज़ार करने वाला जागता है
Step 4 → RLock अतिरिक्त: owner + counter याद रखता है
         वही thread फिर acquire करे -> counter + 1 (block नहीं)
         release -> counter - 1; 0 होने पर lock सच में खाली
Step 5 → "with lock:" इस्तेमाल करें ताकि exception पर भी release हो
```

---

## 🟡 Real World Example
A wallet service (Paytm-style): `Account.withdraw()` locks the account, and `Account.transfer()` also locks and calls `withdraw()`. With a plain `Lock` that deadlocks; with an `RLock` it works. A shared in-memory cache uses a `Lock` around `get_or_set` so two threads never compute the same value twice.

## 🟡 Real Example Hindi mein
Wallet service (Paytm जैसी): `Account.withdraw()` account को lock करता है, और `Account.transfer()` भी lock करके `withdraw()` call करता है। सादे `Lock` से deadlock होता है; `RLock` से चलता है। Shared in-memory cache `get_or_set` के आसपास `Lock` लगाता है ताकि दो threads एक ही value दो बार न निकालें।

---

## 💻 Code Example — Basic
```python
# Basic Lock and RLock behaviour - every line commented
import threading  # locks

lock = threading.Lock()  # a plain, non re-entrant lock
lock.acquire()  # take it
print(lock.locked(), lock.acquire(blocking=False))  # 2nd try without waiting fails
# Output: True False
lock.release()  # give it back
try:  # releasing a free lock is a bug
    lock.release()  # release again
except RuntimeError as e:  # Python tells us
    print("RuntimeError:", e)  # message
# Output: RuntimeError: release unlocked lock

rlock = threading.RLock()  # re-entrant lock


def outer() -> str:  # takes the lock, then calls inner
    with rlock:  # first acquire
        return inner()  # inner needs the same lock


def inner() -> str:  # takes the same lock again
    with rlock:  # same thread: allowed with RLock
        return "ok-reentrant"  # no deadlock


print(outer())  # works
# Output: ok-reentrant

plain = threading.Lock()  # a plain lock again
print(plain.acquire(), plain.acquire(timeout=0.1))  # same thread twice: 2nd times out
# Output: True False   (with no timeout this second acquire would hang forever)
```

## 💻 Code Example — Advanced
```python
# Production style: thread-safe account, safe transfers (no deadlock), ownership rules
import threading  # locks and threads
from typing import Dict  # type hints


class Account:  # a bank-style account
    def __init__(self, bal: int) -> None:  # constructor
        self.bal: int = bal  # balance
        self._lock: threading.RLock = threading.RLock()  # re-entrant: methods may call each other

    def withdraw(self, amt: int) -> bool:  # take money out
        with self._lock:  # exclusive access
            if self.bal < amt:  # not enough money
                return False  # refuse
            self.bal -= amt  # update
            return True  # success

    def transfer(self, to: "Account", amt: int) -> bool:  # move money
        first, second = sorted((self, to), key=id)  # fixed global order prevents A<->B deadlock
        with first._lock, second._lock:  # take both locks in that order
            if not self.withdraw(amt):  # re-enters self._lock: only OK because it is an RLock
                return False  # insufficient funds
            to.bal += amt  # deposit
            return True  # success


a, b = Account(100), Account(0)  # two accounts
ts = [threading.Thread(target=a.transfer, args=(b, 10)) for _ in range(5)]  # 5 parallel transfers
[t.start() for t in ts]  # start all
[t.join() for t in ts]  # wait all
print(a.bal, b.bal)  # money is conserved
# Output: 50 50

# A lock must be released by the thread that owns an RLock
rl = threading.RLock()  # new RLock
rl.acquire()  # main thread owns it
errors = []  # collected errors


def other() -> None:  # another thread tries to release
    try:  # attempt
        rl.release()  # not the owner
    except RuntimeError as e:  # refused
        errors.append(str(e))  # remember message


t = threading.Thread(target=other)  # thread
t.start(); t.join()  # run
print(errors)  # only the owner may release an RLock
# Output: ['cannot release un-acquired lock']
rl.release()  # owner releases (count was 1)


class Cache:  # simple get-or-set with a Lock
    def __init__(self) -> None:  # constructor
        self._d: Dict[str, int] = {}  # storage
        self._l: threading.Lock = threading.Lock()  # a plain Lock is enough (no nested calls)

    def get_or_set(self, k: str, v: int) -> int:  # atomic check-then-set
        with self._l:  # exclusive
            return self._d.setdefault(k, v)  # first writer wins


c = Cache()  # create
print(c.get_or_set("a", 1), c.get_or_set("a", 2))  # second call keeps the first value
# Output: 1 1
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
lock = threading.Lock()
with lock:               # acquire + auto release
    do_work()
```

```javascript
// JavaScript: no locks for normal code. For async critical sections people use a mutex library
import { Mutex } from "async-mutex";
const mutex = new Mutex();
const release = await mutex.acquire();
try { await doWork(); } finally { release(); }
// Or Atomics.wait/notify with SharedArrayBuffer between worker threads
```

Key differences: Python threads preempt each other so locks are routine. In JS the event loop makes sync code atomic; you only need a mutex when an `await` happens in the middle of a critical section. Note that Python's `asyncio.Lock` is a different class for coroutines, never mix it with `threading.Lock`.

---

## 🟠 FastAPI Connection
A shared service object injected with `Depends` is used by many threadpool threads. An `RLock` lets its methods call each other safely.

```python
import threading  # lock
from typing import Dict  # type hints
from fastapi import Depends, FastAPI  # framework
from fastapi.testclient import TestClient  # in-process client

app: FastAPI = FastAPI()  # create app

class Counter:  # shared service
    def __init__(self) -> None:
        self._n: int = 0  # value
        self._lock = threading.RLock()  # re-entrant so methods can call each other
    def incr(self) -> int:
        with self._lock:  # take lock
            self._n += 1  # change
            return self.value()  # re-enters the same lock safely
    def value(self) -> int:
        with self._lock:  # RLock lets the same thread enter again
            return self._n  # read

counter: Counter = Counter()  # one instance per process

def get_counter() -> Counter:  # dependency
    return counter  # same object each request

@app.post("/hit")  # POST /hit
def hit(c: Counter = Depends(get_counter)) -> Dict[str, int]:
    return {"hits": c.incr()}  # thread-safe increment

client = TestClient(app)
print(client.post("/hit").json(), client.post("/hit").json())
# Output: {'hits': 1} {'hits': 2}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `Lock` where a method calls another locked method
```python
# Wrong - self-deadlock, program hangs
class A:
    def __init__(self): self.l = threading.Lock()
    def f(self):
        with self.l: self.g()
    def g(self):
        with self.l: ...

# Correct - use RLock, or split into _g_unlocked() that assumes the lock is held
```

❌ Mistake 2: `acquire()` without `release()` on the error path
```python
# Wrong - exception leaves the lock held forever
lock.acquire()
risky()
lock.release()

# Correct
with lock:
    risky()
```

❌ Mistake 3: Creating the lock inside the function
```python
# Wrong - every call gets its own new lock, so nothing is protected
def add():
    lock = threading.Lock()
    with lock:
        counter.append(1)

# Correct - one shared lock created once
lock = threading.Lock()
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
import threading
r = threading.RLock()
r.acquire(); r.acquire()
r.release()
t = threading.Thread(target=lambda: print("got:", r.acquire(timeout=0.1)))
t.start(); t.join()
r.release()
t = threading.Thread(target=lambda: print("got:", r.acquire(timeout=0.1)))
t.start(); t.join()
```

**Answer**:
```
got: False
got: True
```
The main thread acquired the RLock twice but released once, so the count is still 1 and the other thread cannot get it. After the second release the lock is free and the other thread succeeds. An RLock must be released as many times as it was acquired.

---

## ⚫ Interview Questions + Answers

Q1: Lock vs RLock?
A1: `Lock` is not owned by a thread and cannot be re-acquired even by the holder. `RLock` tracks the owner and a count, so the same thread can acquire it repeatedly. Use RLock for methods that call each other; otherwise prefer the simpler, faster Lock.

Q2: Can a different thread release a `Lock`?
A2: Yes for `Lock` (it has no owner), which can be used as a simple signal. For `RLock` only the owner can release.

Q3: What is a deadlock?
A3: Two or more threads each hold a lock the other needs. Fix with a fixed acquisition order, timeouts, or fewer locks.

Q4: What does `acquire(blocking=False)` return?
A4: `True` if it got the lock immediately, otherwise `False` without waiting.

Q5: Why use `with lock`?
A5: It guarantees release even on exceptions, which prevents permanently locked data.

---

## 🔷 When to Use + When Not to Use

✅ Use Lock when:
- Simple, short critical sections with no nested locking

✅ Use RLock when:
- Public methods of one class call each other while holding the lock
- Recursive functions need the lock

❌ Avoid when:
- A Queue or immutable data would remove the need to share
- You use asyncio (use `asyncio.Lock` there)

---

## 📊 Visual Diagram

```
 Lock    :  T1 acquire ─► T1 acquire again ─► (waits for itself FOREVER)

 RLock   :  T1 acquire (count 1) ─► T1 acquire (count 2)
            release (count 1) ─► release (count 0) ─► free for T2
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Mutual exclusion | One thread at a time | एक समय में एक |
| Re-entrant | Same owner may re-acquire | वही owner दोबारा ले सकता है |
| Self-deadlock | Waiting for your own lock | अपने ही lock का इंतज़ार |
| Lock ordering | Fixed acquisition order | lock लेने का तय क्रम |
| Owner | Thread that holds the lock | lock रखने वाला thread |
| Timeout | Stop waiting after N seconds | N सेकंड बाद इंतज़ार छोड़ना |

---

## ⚡ 3-Line Summary
English: `Lock` gives exclusive access; `RLock` lets the owner re-enter and needs matching releases. Use `with`, keep one global lock order, and never create the lock per call.
Hindi: `Lock` exclusive access देता है; `RLock` में owner दोबारा आ सकता है और उतने ही release चाहिए। `with` इस्तेमाल करें, एक global lock order रखें, और lock हर call में न बनाएँ।

---

## ➡️ Next Topic
**226. Semaphore** — allow N threads at a time (connection pools, rate limits).
