---

# 497. SQLAlchemy Query Example
# हिंदी में: SQLAlchemy Query का Example (Python से database queries)

Full runnable solution: [main.py](main.py) (SQLAlchemy 2.x ORM on in-memory SQLite: filter, join, group by, outer join, eager loading, subquery, N+1 proof).

---

## 🔵 Simple Definition (English)
SQLAlchemy is a Python toolkit that maps classes to tables (ORM) and builds SQL with Python expressions, so you query a database without hand-writing strings.

## 🔵 सरल परिभाषा (Hindi)
SQLAlchemy एक Python toolkit है जो classes को tables से जोड़ता है (ORM) और Python expressions से SQL बनाता है, ताकि आप strings हाथ से लिखे बिना database query कर सकें।

---

## 🔴 Problem it Solves
Raw SQL strings are error-prone, open to SQL injection and tied to one database. SQLAlchemy gives parameterised, composable, database-portable queries and objects instead of tuples.

## 🔴 यह क्यों बना? (Hindi)
Raw SQL strings में गलतियाँ आसान हैं, SQL injection का खतरा है और वे एक database से बंधी रहती हैं। SQLAlchemy parameterised, जोड़ने योग्य, database-portable queries और tuples की जगह objects देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Declare models: class Order(Base) with Mapped[...] columns
Step 2 → create_engine(url) opens a connection pool; Base.metadata.create_all(engine)
Step 3 → Session(engine) is a unit of work (identity map + transaction)
Step 4 → Build a statement: select(Order).where(...).order_by(...).limit(...)
Step 5 → Run: session.scalars(stmt) -> ORM objects; session.execute(stmt) -> Row tuples
Step 6 → session.commit() writes changes; selectinload()/joinedload() avoid N+1
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → models लिखो: class Order(Base) में Mapped[...] columns
Step 2 → create_engine(url) connection pool खोलता है; Base.metadata.create_all(engine)
Step 3 → Session(engine) एक unit of work है (identity map + transaction)
Step 4 → statement बनाओ: select(Order).where(...).order_by(...).limit(...)
Step 5 → चलाओ: session.scalars(stmt) -> ORM objects; session.execute(stmt) -> Row tuples
Step 6 → session.commit() बदलाव लिखता है; selectinload()/joinedload() N+1 रोकते हैं
```

---

## 🟡 Real World Example
Swiggy-style reports: "customers with more than Rs 500 spent", "customers who never ordered", "orders per city". Each is one `select` with join/group-by/having. The orders screen loads a customer with all orders in two queries using `selectinload`, not one per customer.

## 🟡 Real Example Hindi mein
Swiggy जैसे reports: "500 रुपये से ज़्यादा खर्च करने वाले customers", "जिन्होंने कभी order नहीं किया", "city के हिसाब से orders"। हर एक एक `select` है जिसमें join/group-by/having। Orders screen `selectinload` से customer और उसके सारे orders दो queries में लाती है, हर customer के लिए एक नहीं।

---

## 💻 Code Example — Basic
```python
# Basic SQLAlchemy 2.x query
from sqlalchemy import create_engine, select  # engine + select builder
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column  # ORM pieces

class Base(DeclarativeBase):  # common base for models
    pass

class User(Base):  # maps to table "users"
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)  # primary key
    name: Mapped[str]  # NOT NULL text column

engine = create_engine("sqlite://")  # in-memory database
Base.metadata.create_all(engine)  # create tables
with Session(engine) as s:  # unit of work
    s.add_all([User(name="Asha"), User(name="Ravi")])  # stage inserts
    s.commit()  # write to the DB
    print(s.scalars(select(User).where(User.name == "Ravi")).all()[0].id)  # filtered query
# Output:
# 2
```

## 💻 Code Example — Advanced
```python
# Excerpt from main.py: join + aggregate, outer join, eager load
stmt = (select(Customer.name, func.count(Order.id), func.sum(Order.amount))
        .join(Order).group_by(Customer.id).having(func.sum(Order.amount) > 500)
        .order_by(func.sum(Order.amount).desc()))
print(s.execute(stmt).all())  # list of Row tuples

stmt = select(Customer.name).outerjoin(Order).where(Order.id.is_(None))  # never ordered
print(s.scalars(stmt).all())

stmt = select(Customer).options(selectinload(Customer.orders))  # 2 queries total, not N+1
print({c.name: len(c.orders) for c in s.scalars(stmt)})
```
Real output of `python main.py` (Python 3.13.3, SQLAlchemy 2.1.8):
```
[1500, 500]
[('Asha', 2, 2000), ('Ravi', 2, 1000)]
['Zoya']
{'Asha': 2, 'Ravi': 2, 'Zoya': 0}
3000
['Asha']
lazy queries: 4 eager queries: 2
all ok
```

---

## 🟠 JavaScript vs Python Comparison
SQLAlchemy's `select()` builder resembles Knex/Drizzle; the ORM layer resembles Prisma/TypeORM.

```python
stmt = select(User).where(User.age > 18).limit(10)  # builder
rows = session.scalars(stmt).all()
```
```javascript
const rows = await knex("users").where("age", ">", 18).limit(10);  // Knex builder
```

---

## 🟠 FastAPI Connection
FastAPI provides a session per request through a `yield` dependency; the handler receives it via `Depends`.

```python
from collections.abc import Iterator  # type for generator dependency
from fastapi import Depends, FastAPI  # framework
from sqlalchemy import select  # builder
from sqlalchemy.orm import Session  # session type

app = FastAPI()  # app

def get_session() -> Iterator[Session]:  # one session per request
    with Session(engine) as s:  # opened here
        yield s  # handler runs, then session closes

@app.get("/customers")
def customers(s: Session = Depends(get_session)) -> list[str]:  # sync handler runs in threadpool
    return list(s.scalars(select(Customer.name)))  # query and return
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: N+1 queries from lazy relationships inside a loop.
✅ Correct: `selectinload` / `joinedload` (proved above: 4 queries vs 2).

```python
# Wrong
for c in s.scalars(select(Customer)): c.orders
# Right
for c in s.scalars(select(Customer).options(selectinload(Customer.orders))): c.orders
```

❌ Mistake 2: Building SQL with f-strings (injection).
✅ Correct: use `.where(col == value)` or `text("... :id").bindparams(id=1)`.

❌ Mistake 3: Using old 1.x `session.query(...)` style in new code.
✅ Correct: 2.x `select()` with `session.scalars/execute`.

❌ Mistake 4: Forgetting `commit()`, or sharing one Session across threads.
✅ Correct: commit explicitly; one session per request/task.

---

## 🧠 Tricky Interview Question
```python
rows = s.execute(select(Customer.name)).all()
names = s.scalars(select(Customer.name)).all()
print(rows[0], names[0])
```
Answer: `('Asha',) Asha`. `execute` returns `Row` tuples even for one column; `scalars` unwraps the first column. Forgetting this gives `('Asha',)` where a string was expected.

---

## ⚫ Interview Questions + Answers

Q1: What is the N+1 problem?
A1: One query for parents plus one per parent for children. Fix with `selectinload`, `joinedload` or an explicit join.

Q2: Core vs ORM?
A2: Core builds SQL expressions and returns rows; ORM adds mapped classes, identity map and unit of work on top.

Q3: `selectinload` vs `joinedload`?
A3: `joinedload` uses one JOIN (can duplicate parent rows, good for many-to-one); `selectinload` runs a second `IN (...)` query (better for collections).

Q4: What does a Session do?
A4: Tracks objects, batches changes, manages the transaction; `commit` flushes and commits, `rollback` undoes.

Q5: How do you prevent SQL injection?
A5: Always use bound parameters, which SQLAlchemy does for expressions and `text()` with `:name`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Relational data with relationships and migrations (Alembic)
- You want portability across SQLite/Postgres/MySQL

❌ Avoid when:
- Very heavy analytics SQL (raw SQL or `text()` is clearer)
- Tiny scripts where `sqlite3` suffices

---

## 📊 Visual Diagram
```
Python models ──► Base.metadata ──► Engine (pool) ──► Database
        │                                  ▲
   select(...) ──► Session.scalars/execute ┘
        │
   ORM objects (identity map)  ──commit──► INSERT/UPDATE
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ORM | Maps classes to tables | class-table mapping |
| Engine | Connection pool + dialect | database से कनेक्शन |
| Session | Unit of work | काम की इकाई |
| N+1 | Many extra queries | ज़रूरत से ज़्यादा queries |
| Eager loading | Fetch related rows upfront | पहले ही जुड़ा data लाना |
| Subquery | Query inside query | query के अंदर query |

---

## ⚡ 3-Line Summary
English: SQLAlchemy 2.x builds queries with `select()` and runs them via a Session.
English: Use join/group_by/having and eager loading to keep queries few and fast.
English: Always parameterise, commit explicitly, one session per request.
Hindi: SQLAlchemy 2.x `select()` से queries बनाता है और Session से चलाता है।
Hindi: Queries कम और तेज़ रखने के लिए join/group_by/having और eager loading लें।
Hindi: हमेशा parameters इस्तेमाल करें, खुद commit करें, हर request की अपनी session।

---

## ➡️ Next Topic
498. FastAPI Dependency Example: how the session and auth get injected into handlers.

---
