---

# 358. SQLAlchemy Sessions
# हिंदी में: SQLAlchemy Sessions (Unit of Work और Transactions)

---

## 🔵 Simple Definition (English)
A `Session` is the workspace between your Python objects and the database. It remembers which objects you loaded, added or changed, and when you call `commit()` it writes all changes in one transaction. One session should live for one request or one job, not forever.

## 🔵 सरल परिभाषा (Hindi)
`Session` आपके Python objects और database के बीच का workspace है। यह याद रखता है कि आपने कौन से objects load, add या change किए, और `commit()` पर सारे changes एक transaction में लिख देता है। एक session एक request या एक job के लिए होना चाहिए, हमेशा के लिए नहीं।

---

## 🔴 Problem it Solves
Without a session you would track every changed object yourself and write each UPDATE by hand. Two queries for the same row would give two different Python objects, and half-finished work could be saved if an error happens in the middle. The session gives: an identity map (one object per row), automatic change tracking, atomic commit/rollback, and lazy loading.

## 🔴 यह क्यों बना? (Hindi)
Session के बिना आपको हर बदले हुए object को खुद track करना और हर UPDATE हाथ से लिखना पड़ता। एक ही row की दो queries दो अलग Python objects देतीं, और बीच में error आने पर अधूरा काम save हो सकता था। Session देता है: identity map (एक row = एक object), अपने आप change tracking, atomic commit/rollback और lazy loading।

---

## 🟢 How it Works — Step by Step

```
Step 1 → sessionmaker(engine) is a factory; Session() is created per request/job
Step 2 → Object states: transient (new) -> pending (add) -> persistent (in DB) -> detached (session closed)
Step 3 → autoflush: before every query the session flushes pending changes so the query sees them
Step 4 → flush() sends SQL inside the open transaction (ids assigned) but nothing is final
Step 5 → commit() = flush + COMMIT; by default all loaded objects are expired afterwards
Step 6 → rollback() discards the transaction; objects are expired and reloaded on next access
Step 7 → close() returns the connection to the pool; objects become detached
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → sessionmaker(engine) एक factory है; Session() हर request/job के लिए बनता है
Step 2 → Object states: transient (नया) -> pending (add) -> persistent (DB में) -> detached (session बंद)
Step 3 → autoflush: हर query से पहले session pending changes flush करता है ताकि query उन्हें देखे
Step 4 → flush() खुले transaction में SQL भेजता है (ids मिल जाते हैं) पर कुछ final नहीं होता
Step 5 → commit() = flush + COMMIT; डिफ़ॉल्ट में बाद में सभी loaded objects expire हो जाते हैं
Step 6 → rollback() transaction रद्द करता है; objects अगली access पर दोबारा load होते हैं
Step 7 → close() connection को pool में लौटाता है; objects detached हो जाते हैं
```

---

## 🟡 Real World Example
In a Razorpay-like order flow, one request creates an `Order`, reduces `Stock`, and writes a `Payment` row. All three must succeed together. The service opens one session with `session.begin()`; if the payment insert fails, the whole transaction rolls back and no stock is lost. For an optional "send welcome coupon" step, a SAVEPOINT (`begin_nested`) lets that step fail without losing the order.

## 🟡 Real Example Hindi mein
Razorpay जैसे order flow में एक request `Order` बनाती है, `Stock` घटाती है और `Payment` row लिखती है। तीनों साथ सफल होने चाहिए। Service एक session `session.begin()` से खोलती है; payment insert fail हो तो पूरा transaction rollback होता है और stock नहीं घटता। वैकल्पिक "welcome coupon भेजो" step के लिए SAVEPOINT (`begin_nested`) उस step को fail होने देता है बिना order खोए।

---

## 💻 Code Example — Basic
```python
# Basic session behaviour: states, identity map, flush vs commit, rollback
from sqlalchemy import create_engine, inspect, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class Account(Base):
    __tablename__ = "accounts"
    id: Mapped[int] = mapped_column(primary_key=True)
    owner: Mapped[str]
    balance: Mapped[int] = mapped_column(default=0)


engine = create_engine("sqlite://")                       # in-memory DB
Base.metadata.create_all(engine)                          # create the table

with Session(engine) as s:                                # session closes at the end of the block
    a = Account(owner="Asha", balance=100)                # new object
    print(inspect(a).transient)                           # True: not attached to a session
    s.add(a)                                              # attach it
    print(inspect(a).pending)                             # True: waiting for INSERT
    s.flush()                                             # INSERT sent, not committed
    print(inspect(a).persistent, a.id)                    # True 1
    s.commit()                                            # COMMIT (attributes expire now)

    same = s.get(Account, 1)                              # identity map lookup
    again = s.scalars(select(Account).where(Account.owner == "Asha")).one()   # a query
    print(same is again is a)                             # True: ONE object per row

    a.balance += 50                                       # change tracked automatically
    print(inspect(a).modified)                            # True: dirty
    s.rollback()                                          # discard the change
    print(a.balance)                                      # 100 (reloaded from DB)

    a.balance = 999                                       # change again
    print(s.scalar(select(Account.balance)))              # 999 -> autoflush sent the UPDATE before the query
    s.rollback()                                          # still not committed, so undo
    print(s.scalar(select(Account.balance)))              # 100

print(inspect(a).detached)                                # True: session closed

# Output:
# True
# True
# True 1
# True
# True
# 100
# 999
# 100
# True
```

## 💻 Code Example — Advanced
```python
# Production style: session factory, transaction helper, savepoints, error handling
from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker


class Base(DeclarativeBase):
    pass


class Wallet(Base):
    __tablename__ = "wallets"
    id: Mapped[int] = mapped_column(primary_key=True)
    owner: Mapped[str] = mapped_column(unique=True)
    balance: Mapped[int] = mapped_column(default=0)


engine = create_engine("sqlite://")                       # test engine
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(engine, expire_on_commit=False, autoflush=True)   # factory with options


@contextmanager
def transaction() -> Iterator[Session]:
    """One session = one transaction: commit on success, rollback on error, always close."""
    session: Session = SessionLocal()                     # new session
    try:
        yield session                                     # caller works here
        session.commit()                                  # success
    except Exception:
        session.rollback()                                # failure: undo everything
        raise                                             # re-raise for the caller / API layer
    finally:
        session.close()                                   # release connection


def create_wallet(s: Session, owner: str, balance: int = 0) -> Wallet | None:
    """Create wallet; a duplicate owner is tolerated using a SAVEPOINT."""
    try:
        with s.begin_nested():                            # SAVEPOINT
            w = Wallet(owner=owner, balance=balance)
            s.add(w)
            s.flush()                                     # error appears here, inside the savepoint
            return w
    except IntegrityError:
        return None                                       # only the savepoint was rolled back


def transfer(src: str, dst: str, amount: int) -> None:
    with transaction() as s:                              # atomic block
        a = s.scalar(select(Wallet).where(Wallet.owner == src))   # source wallet
        b = s.scalar(select(Wallet).where(Wallet.owner == dst))   # target wallet
        if a is None or b is None:
            raise LookupError("wallet not found")
        a.balance -= amount                               # debit (tracked)
        b.balance += amount                               # credit (tracked)
        if a.balance < 0:                                 # business rule
            raise ValueError("insufficient funds")        # triggers rollback of both changes


with transaction() as s:                                  # setup data
    create_wallet(s, "asha", 100)
    create_wallet(s, "ravi", 0)
    print(create_wallet(s, "asha", 5))                    # None: duplicate ignored, rest of transaction survives

transfer("asha", "ravi", 40)                              # works
try:
    transfer("asha", "ravi", 500)                         # fails
except ValueError as e:
    print("Error:", e)

with SessionLocal() as s:                                 # read result
    print({w.owner: w.balance for w in s.scalars(select(Wallet))})

# Output:
# None
# Error: insufficient funds
# {'asha': 60, 'ravi': 40}
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | SQLAlchemy Session | Prisma / Sequelize (JS) |
|---------|--------------------|--------------------------|
| Tracks objects | yes (identity map) | no (Prisma) / partial |
| Auto UPDATE on attribute change | yes, at flush | no, call `save()`/`update()` |
| Transaction | `session.begin()` | `prisma.$transaction([...])` |
| Savepoint | `begin_nested()` | not built in (Prisma) |

```python
# Python way
with Session(engine) as s, s.begin():          # transaction block
    user = s.get(User, 1)                      # load
    user.name = "New"                          # just change it; UPDATE is automatic
```
```javascript
// JavaScript way (Prisma)
await prisma.$transaction(async (tx) => {      // transaction block
  await tx.user.update({ where: { id: 1 }, data: { name: "New" } });  // explicit update
});
```

Key difference: in SQLAlchemy, plain attribute assignment is enough, because the session notices changes. This is powerful but surprising for JS developers: mutating an object inside a session may write to the DB at the next flush.

---

## 🟠 FastAPI Connection
A request-scoped session via a `yield` dependency is the standard. The dependency can also own the transaction: commit after the endpoint returns, rollback if it raises.

```python
# FastAPI: session per request, transaction handled by the dependency
from collections.abc import Iterator
from fastapi import Depends, FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    pass


class Counter(Base):
    __tablename__ = "counters"
    id: Mapped[int] = mapped_column(primary_key=True)
    hits: Mapped[int] = mapped_column(default=0)


engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(engine, expire_on_commit=False)
app = FastAPI()


def get_session() -> Iterator[Session]:
    with SessionLocal() as session:                       # opened per request
        try:
            yield session                                 # endpoint runs here
            session.commit()                              # success -> commit
        except Exception:
            session.rollback()                            # error -> rollback
            raise


@app.post("/hit")
def hit(s: Session = Depends(get_session)) -> dict[str, int]:
    c = s.scalar(select(Counter)) or Counter(hits=0)      # first call creates the row
    s.add(c)
    c.hits += 1                                           # change tracked
    s.flush()                                             # make sure id/default exist
    return {"hits": c.hits}


@app.post("/boom")
def boom(s: Session = Depends(get_session)) -> None:
    c = s.scalar(select(Counter))
    c.hits += 1000                                        # change...
    raise HTTPException(500, "failed after change")       # ...then fail -> rolled back


c = TestClient(app)
print(c.post("/hit").json(), c.post("/hit").json())       # {'hits': 1} {'hits': 2}
print(c.post("/boom").status_code)                         # 500
print(c.post("/hit").json())                               # {'hits': 3}  (the +1000 was rolled back)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: One global session shared by all requests
✅ Correct: one session per request/task

```python
# Wrong — shared, not thread-safe, accumulates stale objects and failed transactions
session = Session(engine)
# Right
def get_db():
    with SessionLocal() as s:
        yield s
```

❌ Mistake 2: Accessing attributes after the session closed (DetachedInstanceError)
✅ Correct: `expire_on_commit=False`, or read the data before closing

```python
# Wrong
with Session(engine) as s:
    u = s.get(User, 1)
    s.commit()
print(u.name)      # DetachedInstanceError: attributes were expired by commit
# Right
SessionLocal = sessionmaker(engine, expire_on_commit=False)
```

❌ Mistake 3: Not rolling back after an error (PendingRollbackError)
✅ Correct: always `rollback()` (or use `with session.begin()` / the helper above)

```python
# Wrong
try:
    s.add(dup); s.commit()
except IntegrityError:
    pass                     # session is now unusable: PendingRollbackError on next use
# Right
except IntegrityError:
    s.rollback()
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
from sqlalchemy import create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

class Base(DeclarativeBase): pass
class P(Base):
    __tablename__ = "p"
    id: Mapped[int] = mapped_column(primary_key=True)
    n: Mapped[int]

e = create_engine("sqlite://")
Base.metadata.create_all(e)
with Session(e) as s1, Session(e) as s2:
    s1.add(P(n=1)); s1.commit()
    a = s1.get(P, 1)
    b = s2.get(P, 1)
    print(a is b)
    a.n = 5
    s1.flush()
    print(b.n)
    s1.commit()
    s2.refresh(b)
    print(b.n)
```
Answer: `False`, `1`, `5`. The identity map is per session, so two sessions hold two different objects for the same row. `a.n = 5` and `flush` change the DB inside s1's transaction, but `b` already loaded `n=1` and is not refreshed automatically, so it still shows 1. After `commit` and an explicit `refresh`, `b` reads the new value 5.

---

## ⚫ Interview Questions + Answers

Q1: What is the identity map?
A1: A per-session dictionary keyed by (class, primary key). If you load the same row twice in a session, you get the same Python object, so changes are consistent.

Q2: What is autoflush?
A2: Before a query runs, the session first flushes pending changes so the query sees them. It can be turned off (`autoflush=False`) or temporarily with `with session.no_autoflush:`.

Q3: What are the object states?
A3: Transient (not in a session), pending (added, not flushed), persistent (has a row and belongs to a session), deleted, and detached (has a row but no session). Inspect with `sqlalchemy.inspect(obj)`.

Q4: What is `begin_nested()`?
A4: A SAVEPOINT. You can roll back part of a transaction (e.g. one failing insert) while keeping earlier work and continuing the outer transaction.

Q5: Is a Session thread-safe? Is it OK to share between asyncio tasks?
A5: No. Use one session per thread/request/task. For async code use `AsyncSession` (with `create_async_engine`) and do not share it between concurrent tasks.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You want automatic change tracking and atomic commits
- Each request or job needs its own unit of work
- You need savepoints for partial failure

❌ Avoid when:
- Loading millions of rows for read-only processing (use Core / `yield_per` / streaming)
- Sharing one session across threads or concurrent async tasks
- Long-lived sessions (hold DB connections and stale data)

---

## 📊 Visual Diagram
```
 request starts
     |
 Session()  --- identity map { (User,1): <User 1>, ... }
     |
 s.add(obj)           pending
 query -> autoflush   INSERT/UPDATE sent (still in transaction)
 s.flush()            ids assigned
     |
     +-- success --> commit()   -> DB permanent, objects expire
     |
     '-- error   --> rollback() -> DB unchanged
     |
 close()  -> connection back to pool, objects detached
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Unit of work | Collect changes, write together | Changes जमा करके साथ लिखना |
| Identity map | One object per row per session | एक row = एक object |
| Autoflush | Flush before queries | Query से पहले अपने आप flush |
| Savepoint | Partial rollback point inside a transaction | Transaction के अंदर आंशिक rollback बिंदु |
| Detached | Object whose session is closed | Session बंद होने के बाद का object |
| expire_on_commit | Reload attributes after commit | Commit के बाद attributes दोबारा load |

---

## ⚡ 3-Line Summary
English: A Session tracks objects (identity map), flushes changes before queries, and commits or rolls back one transaction. Use one session per request and handle errors with rollback or a context manager. `begin_nested()` gives savepoints for partial failures.
Hindi: Session objects को track करता है (identity map), queries से पहले changes flush करता है और एक transaction को commit या rollback करता है। हर request के लिए एक session रखें और errors में rollback या context manager इस्तेमाल करें। `begin_nested()` आंशिक failures के लिए savepoints देता है।

---

## ➡️ Next Topic
**359. SQLAlchemy Relationships** — connect tables with `relationship()` and `ForeignKey`, and avoid the N+1 query problem.
