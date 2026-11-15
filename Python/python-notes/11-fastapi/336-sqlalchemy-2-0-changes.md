---

# 336. SQLAlchemy 2.0 Changes
# हिंदी में: SQLAlchemy 2.0 के बदलाव (Typed Models, select(), No Autocommit)

---

## 🔵 Simple Definition (English)
SQLAlchemy 2.0 modernized the API. Models use `DeclarativeBase` and `Mapped[type]` annotations, queries use `select()` for everything (not `session.query()`), and connections never autocommit: you commit explicitly. Old 1.x habits such as `engine.execute()` were removed.

## 🔵 सरल परिभाषा (Hindi)
SQLAlchemy 2.0 ने API को आधुनिक बनाया। Models में `DeclarativeBase` और `Mapped[type]` annotations उपयोग होते हैं, queries में हर जगह `select()` (न कि `session.query()`), और connections कभी autocommit नहीं करते: आप खुद commit करते हैं। `engine.execute()` जैसी पुरानी 1.x आदतें हटा दी गईं।

---

## 🔴 Problem it Solves
SQLAlchemy 1.x had two query systems (`Query` and `select()`), implicit autocommit that hid transaction bugs, models without type information, and `engine.execute()` that mixed up connection lifetime. Editors and type checkers (mypy, Pyright) could not understand model attributes. 2.0 unified everything: one query style, explicit transactions, and real type hints so `user.name` is a `str` for your IDE.

## 🔴 यह क्यों बना? (Hindi)
SQLAlchemy 1.x में दो query सिस्टम (`Query` और `select()`) थे, implicit autocommit जो transaction bugs छिपाता था, type जानकारी के बिना models, और `engine.execute()` जो connection की उम्र उलझा देता था। Editors और type checkers (mypy, Pyright) model attributes को समझ नहीं पाते थे। 2.0 ने सब एकीकृत किया: एक query style, explicit transactions, और असली type hints ताकि IDE को पता हो `user.name` एक `str` है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → class Base(DeclarativeBase): pass       (replaces declarative_base())
Step 2 → Columns: name: Mapped[str] = mapped_column(String(30))
Step 3 → Nullability comes from the type: Mapped[int | None] => NULL allowed
Step 4 → Queries: session.scalars(select(User).where(...)).all()
Step 5 → Connection: with engine.connect() as conn: ... conn.commit()  (explicit)
Step 6 → Shortcut: with engine.begin() as conn: (auto commit at block end)
Step 7 → Strings must be wrapped: conn.execute(text("SELECT 1"))
Step 8 → Removed: engine.execute(), autocommit=True, Query is "legacy"
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → class Base(DeclarativeBase): pass       (declarative_base() की जगह)
Step 2 → Columns: name: Mapped[str] = mapped_column(String(30))
Step 3 → Nullability type से आती है: Mapped[int | None] => NULL allowed
Step 4 → Queries: session.scalars(select(User).where(...)).all()
Step 5 → Connection: with engine.connect() as conn: ... conn.commit()  (स्पष्ट)
Step 6 → Shortcut: with engine.begin() as conn: (block खत्म होने पर auto commit)
Step 7 → Strings को लपेटना पड़ता है: conn.execute(text("SELECT 1"))
Step 8 → हटाया गया: engine.execute(), autocommit=True, Query अब "legacy"
```

---

## 🟡 Real World Example
A startup upgrades its FastAPI backend from SQLAlchemy 1.4 to 2.x. The type checker in CI immediately finds a bug (a column assumed non-null is actually `Optional`). Scripts that relied on autocommit silently stopped saving data (no `commit()`), which was caught in staging. After migration, every model is typed and the team gets autocomplete on all query results.

## 🟡 Real Example Hindi mein
एक startup अपना FastAPI backend SQLAlchemy 1.4 से 2.x में upgrade करता है। CI का type checker तुरंत एक bug पकड़ता है (जिस column को non-null माना गया वह असल में `Optional` है)। जो scripts autocommit पर निर्भर थीं, उन्होंने चुपचाप डेटा save करना बंद कर दिया (`commit()` नहीं था), जो staging में पकड़ा गया। Migration के बाद हर model typed है और सभी query results पर autocomplete मिलता है।

---

## 💻 Code Example — Basic
```python
# Basic: typed models + select() + what was removed (verified on SQLAlchemy 2.x)
from typing import Optional                                  # old-style optional (still supported)
from sqlalchemy import String, create_engine, select, text   # core imports
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column   # 2.0 ORM imports


class Base(DeclarativeBase):                                 # 2.0 base class (no declarative_base())
    pass                                                     # empty


class User(Base):                                            # model
    __tablename__ = "users"                                  # table name
    id: Mapped[int] = mapped_column(primary_key=True)        # int, PK, NOT NULL
    name: Mapped[str] = mapped_column(String(30))            # str => NOT NULL
    nick: Mapped[Optional[str]]                              # Optional => NULL allowed
    age: Mapped[int | None]                                  # same with 3.10+ union syntax


engine = create_engine("sqlite://")                          # demo database
Base.metadata.create_all(engine)                             # create tables
print({c.name: (c.nullable, str(c.type)) for c in User.__table__.columns})   # inferred schema
with Session(engine) as s:                                   # session
    s.add_all([User(name="A", age=30), User(name="B", nick="bee")])   # two users
    s.commit()                                               # explicit commit
    print(s.scalars(select(User.name).order_by(User.id)).all())       # list of str
    print(s.execute(select(User.name, User.age)).all())               # list of Rows
    try:                                                     # raw strings are rejected now
        s.execute("SELECT 1")                                # 1.x allowed this
    except Exception as e:                                   # 2.0 raises
        print(type(e).__name__)                              # ArgumentError
    print(s.execute(text("SELECT 1")).scalar())              # must wrap in text()
    try:                                                     # removed API
        engine.execute                                       # attribute no longer exists
    except AttributeError as e:                              # 2.0 raises
        print("AttributeError:", e)                          # message
    print(s.get(User, 2).name)                               # get by primary key
    s.query(User).count()                                    # still works, but "legacy"
    print("legacy Query still works (but legacy)")           # not removed, just discouraged

# Output (verified):
# {'id': (False, 'INTEGER'), 'name': (False, 'VARCHAR(30)'), 'nick': (True, 'VARCHAR'), 'age': (True, 'INTEGER')}
# ['A', 'B']
# [('A', 30), ('B', None)]
# ArgumentError
# 1
# AttributeError: 'Engine' object has no attribute 'execute'
# B
# legacy Query still works (but legacy)
```

## 💻 Code Example — Advanced
```python
# Advanced: the "no autocommit" rule, shown with a rollback and an explicit commit
from sqlalchemy import create_engine, text                   # engine + text()

engine = create_engine("sqlite://")                          # demo DB (shared connection for :memory:)
with engine.begin() as conn:                                 # begin(): commit at block end
    conn.execute(text("CREATE TABLE t (id INTEGER)"))        # setup in its own committed transaction

with engine.connect() as conn:                               # connect(): transaction starts automatically
    conn.execute(text("INSERT INTO t VALUES (1)"))           # INSERT inside a transaction
    # leaving the block WITHOUT conn.commit() => ROLLBACK (2.0 has no autocommit)
with engine.connect() as conn:                               # a new connection to check
    print(conn.execute(text("SELECT count(*) FROM t")).scalar())   # insert was NOT saved

with engine.connect() as conn:                               # try again
    conn.execute(text("INSERT INTO t VALUES (1)"))           # INSERT
    conn.commit()                                            # explicit commit => saved
with engine.connect() as conn:                               # verify
    print(conn.execute(text("SELECT count(*) FROM t")).scalar())   # now 1

# Output (verified):
# 0
# 1
```

Migration cheat sheet (1.x to 2.0):
```python
# 1.x                                      # 2.0
# declarative_base()                    -> class Base(DeclarativeBase): pass
# Column(String(30))                    -> mapped_column(String(30)) with Mapped[str]
# session.query(User).filter(..).all()  -> session.scalars(select(User).where(..)).all()
# session.query(User).get(1)            -> session.get(User, 1)
# engine.execute("SQL")                 -> with engine.connect() as c: c.execute(text("SQL")); c.commit()
# create_engine(..., future=True)       -> default now (flag no longer needed)
```

---

## 🟠 JavaScript vs Python Comparison

| Idea | Python SQLAlchemy 2.0 | JavaScript/TypeScript |
|------|------------------------|-----------------------|
| Typed model fields | `Mapped[str]` | TypeScript interfaces / Prisma generated types |
| Nullable | `Mapped[int \| None]` | `age: number \| null` |
| Explicit transaction | `conn.commit()` | `await tx.commit()` |
| Raw string SQL | wrap in `text()` | tagged template `sql\`...\`` |

```python
# Python way — type decides NULL / NOT NULL
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)   # required
    age: Mapped[int | None]                             # optional column
```
```typescript
// TypeScript way — type is separate from the database schema
interface User {
  id: number;            // required
  age: number | null;    // optional
}
```

Key difference: in TypeScript the interface and the DB schema can disagree silently. In SQLAlchemy 2.0 the annotation IS the column definition, so the type and the table cannot drift apart.

---

## 🟠 FastAPI Connection
Modern FastAPI tutorials use the 2.0 style everywhere: `DeclarativeBase` models, `select()` queries, and `Session` dependencies. Typed `Mapped[]` attributes pair well with Pydantic: your type checker can verify that a route returning a `User` matches the schema.

```python
# FastAPI example — 2.0 style route
from fastapi import APIRouter, Depends, HTTPException    # FastAPI pieces
from sqlalchemy import select                            # 2.0 query style
from sqlalchemy.orm import Session                       # session type

router = APIRouter()                                     # router


@router.get("/users")                                    # list users by name
def list_users(name: str, db: Session = Depends(get_db)) -> list[str]:
    stmt = select(User.name).where(User.name.ilike(f"%{name}%"))   # a typed statement (bound param)
    return list(db.scalars(stmt).all())                  # execute and return list of str
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Relying on autocommit
✅ Correct: call `commit()` or use `engine.begin()` / `Session.begin()`

```python
# Wrong — rolled back on exit
with engine.connect() as c:
    c.execute(text("INSERT INTO t VALUES (1)"))
# Right
with engine.begin() as c:
    c.execute(text("INSERT INTO t VALUES (1)"))
```

❌ Mistake 2: Passing a plain string to `execute()`
✅ Correct: `text("...")` with `:named` parameters

```python
# Wrong — ArgumentError in 2.0
session.execute("SELECT 1")
# Right
session.execute(text("SELECT 1"))
```

❌ Mistake 3: Using `Column(...)` without `Mapped[]` and ignoring mypy errors, or forgetting `Optional`
✅ Correct: annotate every attribute; use `Mapped[X | None]` for nullable columns

```python
# Wrong — type says str, but column allows NULL: runtime None surprises
nick: Mapped[str] = mapped_column(String(30), nullable=True)
# Right
nick: Mapped[str | None] = mapped_column(String(30))
```

---

## 🧠 Tricky Interview Question

```python
# What is the nullable value of each column?
class A(Base):
    __tablename__ = "a"
    id: Mapped[int] = mapped_column(primary_key=True)
    x: Mapped[int]
    y: Mapped[int | None]
    z: Mapped[int] = mapped_column(nullable=True)
```
Answer: `x` is NOT NULL (non-Optional annotation). `y` is nullable (`| None` makes it Optional). `z` is nullable too because the explicit `nullable=True` overrides the annotation, but the type hint still claims `int`, so a type checker will wrongly think it is never `None`. Best practice: let the annotation drive nullability and avoid contradicting it.

---

## ⚫ Interview Questions + Answers

Q1: What were the biggest changes in SQLAlchemy 2.0?
A1: Unified `select()` query style, typed declarative mapping (`DeclarativeBase`, `Mapped`, `mapped_column`), no autocommit (explicit commit), removal of `engine.execute()` and bound metadata, and first-class async support.

Q2: Is `session.query()` removed?
A2: No. It still works as "legacy" and gets no new features. New code should use `select()` with `session.scalars()` or `session.execute()`.

Q3: How is nullability decided in 2.0 declarative?
A3: From the annotation: `Mapped[int]` is NOT NULL, `Mapped[int | None]` or `Optional[int]` is nullable. An explicit `nullable=` argument overrides it.

Q4: What does `Session.scalars()` do?
A4: It executes a statement and returns a `ScalarResult` containing the first column of each row, usually ORM instances. Shortcut for `session.execute(stmt).scalars()`.

Q5: Why did they remove autocommit?
A5: Implicit commits made it unclear what was saved and when. "Explicit is better than implicit": every write now needs `commit()`, which matches DBAPI semantics and makes transaction bugs visible.

---

## 🔷 When to Use + When Not to Use
✅ Use 2.0 style when:
- Starting any new project (default since 2023)
- You want mypy/Pyright type checking on models
- You use async SQLAlchemy (it assumes 2.0 patterns)

❌ Avoid / delay when:
- A huge legacy 1.3 codebase with no tests (upgrade in steps through 1.4 and enable `SQLALCHEMY_WARN_20=1` first)

---

## 📊 Visual Diagram
```
 1.x                                  2.0
 ─────────────────────────            ─────────────────────────────
 declarative_base()              ──►  class Base(DeclarativeBase)
 Column(Integer)                 ──►  Mapped[int] = mapped_column()
 session.query(User).filter()    ──►  select(User).where()
 engine.execute("SQL")           ──►  conn.execute(text("SQL"))
 implicit autocommit             ──►  conn.commit() / begin()
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `Mapped[T]` | Typed attribute annotation | Typed attribute annotation |
| `mapped_column` | Column config in 2.0 style | 2.0 style में column कॉन्फ़िग |
| `DeclarativeBase` | New base class for models | Models की नई base class |
| Autocommit | Implicit commit (removed) | अपने आप commit (हटाया गया) |
| Legacy `Query` | Old query API, discouraged | पुरानी query API |
| `text()` | Wrapper for raw SQL strings | Raw SQL strings का wrapper |

---

## ⚡ 3-Line Summary
English: SQLAlchemy 2.0 uses typed `Mapped[]` models, one `select()` query style, and explicit commits with no autocommit. `engine.execute()` is gone and raw SQL needs `text()`. The annotation decides NULL / NOT NULL.
Hindi: SQLAlchemy 2.0 typed `Mapped[]` models, एक `select()` query style, और बिना autocommit के explicit commits उपयोग करता है। `engine.execute()` हट गया और raw SQL के लिए `text()` चाहिए। Annotation तय करता है कि NULL या NOT NULL।

---

## ➡️ Next Topic
**337. Async SQLAlchemy** — `AsyncSession`, `create_async_engine`, and why lazy loading breaks in async code.
