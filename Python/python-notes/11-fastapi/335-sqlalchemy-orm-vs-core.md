---

# 335. SQLAlchemy ORM vs Core
# हिंदी में: SQLAlchemy ORM बनाम Core

---

## 🔵 Simple Definition (English)
SQLAlchemy has two layers. Core works with tables, columns and SQL expressions and returns rows. ORM sits on top of Core: it maps Python classes to tables, tracks object changes in a Session, and manages relationships. Core is closer to SQL and faster; ORM is more convenient.

## 🔵 सरल परिभाषा (Hindi)
SQLAlchemy की दो परतें हैं। Core tables, columns और SQL expressions के साथ काम करता है और rows लौटाता है। ORM, Core के ऊपर बैठता है: यह Python classes को tables से map करता है, Session में object बदलाव track करता है, और relationships संभालता है। Core SQL के ज्यादा करीब और तेज है; ORM ज्यादा सुविधाजनक है।

---

## 🔴 Problem it Solves
One tool does not fit every job. For normal CRUD, objects and relationships make code short and readable (ORM). For bulk inserts, reports with complex joins, or when you do not need objects, the ORM's change tracking and object creation add overhead (Core). SQLAlchemy lets you use both in the same project, even the same transaction.

## 🔴 यह क्यों बना? (Hindi)
हर काम के लिए एक ही tool फिट नहीं होता। सामान्य CRUD में objects और relationships code को छोटा और पठनीय बनाते हैं (ORM)। Bulk insert, जटिल joins वाली reports, या जहाँ objects चाहिए ही नहीं, वहाँ ORM का change tracking और object बनाना अतिरिक्त बोझ है (Core)। SQLAlchemy दोनों को एक ही project में, यहाँ तक कि एक ही transaction में, उपयोग करने देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Core: Table(...) objects live in a MetaData; columns via table.c.name
Step 2 → Core: select()/insert() build SQL expressions (no database call yet)
Step 3 → Core: conn.execute(stmt) sends SQL; you get Row objects (tuple-like)
Step 4 → ORM: a class is mapped onto a Table (declarative or __table__)
Step 5 → ORM: Session.execute(select(Model)) returns Model instances
Step 6 → ORM: instances go into the identity map; changes tracked; flush on commit
Step 7 → The ORM itself uses Core underneath to emit the real SQL
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Core: Table(...) objects MetaData में रहते हैं; columns table.c.name से
Step 2 → Core: select()/insert() SQL expressions बनाते हैं (अभी database call नहीं)
Step 3 → Core: conn.execute(stmt) SQL भेजता है; आपको Row objects (tuple जैसे) मिलते हैं
Step 4 → ORM: class को Table पर map किया जाता है (declarative या __table__)
Step 5 → ORM: Session.execute(select(Model)) Model instances लौटाता है
Step 6 → ORM: instances identity map में जाते हैं; बदलाव track; commit पर flush
Step 7 → असली SQL बनाने के लिए ORM अंदर से Core ही उपयोग करता है
```

---

## 🟡 Real World Example
An e-commerce app uses the ORM for the main API: create an order, update the address, load a customer with orders. A nightly job that imports 2 million price updates from a supplier uses Core `insert()` with executemany, and the admin analytics dashboard uses Core `select()` with `group_by` to return plain rows without building objects.

## 🟡 Real Example Hindi mein
E-commerce app मुख्य API के लिए ORM उपयोग करता है: order बनाना, address update करना, orders के साथ customer load करना। Supplier से 20 लाख price updates import करने वाला nightly job Core `insert()` (executemany) उपयोग करता है, और admin analytics dashboard objects बनाए बिना plain rows लौटाने के लिए Core `select()` और `group_by` उपयोग करता है।

---

## 💻 Code Example — Basic
```python
# Basic: the same data with Core (tables + connection) and then the ORM on the same table
from sqlalchemy import Column, Integer, MetaData, String, Table, create_engine, func, insert, select, text
from sqlalchemy.orm import DeclarativeBase, Session       # ORM pieces

engine = create_engine("sqlite://")                       # in-memory DB
metadata = MetaData()                                     # catalog of Core tables
items = Table(                                            # Core table definition
    "items", metadata,                                    # name + catalog
    Column("id", Integer, primary_key=True),              # PK column
    Column("name", String(30)),                           # name column
    Column("qty", Integer),                               # quantity column
)
metadata.create_all(engine)                               # CREATE TABLE

with engine.begin() as conn:                              # Core connection, commits at block end
    conn.execute(insert(items), [                         # executemany: list of dicts
        {"name": "pen", "qty": 5}, {"name": "ink", "qty": 0}, {"name": "pad", "qty": 9},
    ])
    print(conn.execute(select(items.c.name, items.c.qty).where(items.c.qty > 0)).all())   # list of Rows
    row = conn.execute(select(func.sum(items.c.qty).label("total"))).one()   # exactly one row
    print(row.total, row._mapping)                        # attribute access / dict-like mapping
    print(conn.execute(text("SELECT count(*) FROM items WHERE qty > :q"), {"q": 1}).scalar_one())   # raw SQL
    print(str(select(items.c.name).where(items.c.qty > 1)))   # the expression IS the SQL text


class Base(DeclarativeBase):                              # ORM base
    pass                                                  # empty


class Item(Base):                                         # map a class onto the SAME Core table
    __table__ = items                                     # reuse the Table object


with Session(engine) as s:                                # ORM session
    it = s.get(Item, 1)                                   # returns an Item object
    it.qty += 10                                          # attribute change is tracked
    s.commit()                                            # UPDATE sent
    print(type(it).__name__, it.qty)                      # Item 15

# Output (verified):
# [('pen', 5), ('pad', 9)]
# 14 {'total': 14}
# 2
# SELECT items.name
# FROM items
# WHERE items.qty > :qty_1
# Item 15
```

## 💻 Code Example — Advanced
```python
# Performance comparison: insert 20,000 rows three ways (SQLite in memory)
import time                                               # timing
from sqlalchemy import String, create_engine, insert      # engine + Core insert
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column   # ORM


class Base(DeclarativeBase):                              # base class
    pass                                                  # empty


class Row(Base):                                          # mapped class
    __tablename__ = "rows"                                # table
    id: Mapped[int] = mapped_column(primary_key=True)     # PK
    name: Mapped[str] = mapped_column(String(20))         # name


N: int = 20000                                            # number of rows
data: list[dict[str, str]] = [{"name": f"n{i}"} for i in range(N)]   # sample payload

e1 = create_engine("sqlite://"); Base.metadata.create_all(e1)   # DB 1
t = time.perf_counter()                                   # start timer
with Session(e1) as s:                                    # ORM way
    s.add_all([Row(**d) for d in data])                   # 20,000 Python objects tracked
    s.commit()                                            # flush all
orm_t: float = time.perf_counter() - t                    # elapsed

e2 = create_engine("sqlite://"); Base.metadata.create_all(e2)   # DB 2
t = time.perf_counter()                                   # start timer
with e2.begin() as c:                                     # Core way
    c.execute(insert(Row), data)                          # one executemany, no objects
core_t: float = time.perf_counter() - t                   # elapsed

e3 = create_engine("sqlite://"); Base.metadata.create_all(e3)   # DB 3
t = time.perf_counter()                                   # start timer
with Session(e3) as s:                                    # ORM-enabled bulk insert (2.0 style)
    s.execute(insert(Row), data)                          # uses the model but skips object creation
    s.commit()                                            # commit
bulk_t: float = time.perf_counter() - t                   # elapsed
print(f"ORM add_all: {orm_t:.3f}s | Core insert: {core_t:.3f}s | Session.execute(insert): {bulk_t:.3f}s")
print(round(orm_t / core_t, 1), "x slower")               # ratio

# Output (verified on one run; numbers vary by machine):
# ORM add_all: 0.445s | Core insert: 0.025s | Session.execute(insert): 0.036s
# 18.1 x slower
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python (SQLAlchemy) | JavaScript |
|---------|---------------------|-----------|
| Query builder (no objects) | Core `select()` | Knex, Kysely, Drizzle |
| ORM with objects | SQLAlchemy ORM | TypeORM, Sequelize, Prisma |
| Both in one library | yes | rarely (Drizzle partly) |
| Raw SQL | `text()` | `knex.raw`, `$queryRaw` |

```python
# Python way — Core
rows = conn.execute(select(items.c.name).where(items.c.qty > 0)).all()   # list of Rows
```
```javascript
// JavaScript way — Knex query builder (Core-like)
const rows = await knex("items").select("name").where("qty", ">", 0);    // list of plain objects
```

Key difference: in JS you usually choose a query builder OR an ORM. SQLAlchemy has both in one package, built on the same foundation, so you can drop down to Core inside an ORM project.

---

## 🟠 FastAPI Connection
In a FastAPI service, use the ORM for request/response CRUD, and Core (or `Session.execute(insert(Model), rows)`) for bulk endpoints such as CSV import, and for read-only report endpoints where you return a list of dicts straight into a Pydantic model.

```python
# FastAPI example — bulk import endpoint with Core-style insert through the session
from fastapi import APIRouter, Depends                   # routing + DI
from sqlalchemy import insert                            # bulk insert
from sqlalchemy.orm import Session                       # type hint

router = APIRouter()                                     # router


@router.post("/prices/bulk", status_code=201)            # POST many rows at once
def bulk_prices(rows: list[dict[str, int]], db: Session = Depends(get_db)) -> dict[str, int]:
    db.execute(insert(Price), rows)                      # one executemany, no per-row objects
    db.commit()                                          # single commit
    return {"inserted": len(rows)}                       # how many rows
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using the ORM for huge bulk inserts (`add_all` of 1 million objects)
✅ Correct: `session.execute(insert(Model), list_of_dicts)` or Core `insert()` (or PostgreSQL `COPY`)

```python
# Wrong — creates and tracks a million objects
session.add_all([Row(name=n) for n in names])
# Right
session.execute(insert(Row), [{"name": n} for n in names])
```

❌ Mistake 2: Expecting Core results to behave like ORM objects
✅ Correct: Core returns `Row` tuples; use `row.col` or `row._mapping`, not relationships

```python
# Wrong — a Row has no .posts, no change tracking
row = conn.execute(select(items)).first()
row.qty = 5                      # AttributeError: can't set attribute
# Right — use an UPDATE statement
conn.execute(update(items).where(items.c.id == row.id).values(qty=5))
```

❌ Mistake 3: Mixing two separate transactions by accident (Session and Connection)
✅ Correct: use `session.execute(...)` (or `session.connection()`) so everything shares one transaction

```python
# Wrong — engine.begin() is a different connection from the session's transaction
with Session(engine) as s, engine.begin() as c:
    ...
# Right
with Session(engine) as s:
    s.execute(insert(Row), data)     # same transaction as the ORM work
```

---

## 🧠 Tricky Interview Question

```python
# Will this UPDATE be seen by the ORM object without refresh?
with Session(engine) as s:
    it = s.get(Item, 1)            # it.qty == 5 now
    s.execute(update(Item).where(Item.id == 1).values(qty=99))
    print(it.qty)
```
Answer: In SQLAlchemy 2.0 the ORM-enabled `update()` run through the Session uses `synchronize_session="auto"` by default, which tries to update matching objects already in the session ("evaluate" strategy), then falls back to "fetch". So here it usually prints `99`. With a Core `conn.execute(update(items)...)` on a separate connection, the object is NOT touched and still shows 5 until you `s.refresh(it)` or `s.expire(it)`. Moral: Core statements bypass the identity map unless you run them through the Session.

---

## ⚫ Interview Questions + Answers

Q1: What are the two layers of SQLAlchemy?
A1: Core (engine, connection, Table, SQL expression language, returns Rows) and ORM (mapped classes, Session, identity map, relationships). The ORM is built on Core.

Q2: When would you choose Core over the ORM?
A2: Bulk inserts/updates, complex reporting queries, ETL jobs, or when you do not need object tracking. It avoids per-object overhead (about 18x faster for 20,000 inserts in our test).

Q3: Can you use both together?
A3: Yes. You can run Core statements through `session.execute()`, use `session.connection()` to get the Core connection, and map classes onto Core `Table`s with `__table__`.

Q4: What does `Session.execute(select(Model))` return vs `scalars()`?
A4: `execute` returns `Row` objects (a 1-tuple containing the model); `scalars()` unwraps the first column so you get model instances directly. Use `scalars()` for single-entity ORM queries.

Q5: Why is the ORM slower?
A5: For each row it builds instances, registers them in the identity map, sets up change tracking and (on insert) often fetches generated primary keys one by one. Core and "insertmanyvalues" batching skip that.

---

## 🔷 When to Use + When Not to Use
✅ Use ORM when:
- Typical CRUD with relationships and business logic
- You benefit from change tracking and cascades

✅ Use Core when:
- Bulk operations, ETL, reports, read-only dashboards
- You want SQL-like control and maximum speed

❌ Avoid:
- ORM for million-row loops; Core for deeply nested object graphs

---

## 📊 Visual Diagram
```
        Your code
     ┌──────┴───────┐
     ▼              ▼
    ORM            Core (SQL expression language)
 Session +          select / insert / update / Table
 mapped classes          │
     │                   │
     └─────► Core ◄──────┘
                │
            Engine / Connection pool
                │
             DBAPI driver  ──►  Database
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Core | SQL expression layer | SQL expression परत |
| ORM | Object-relational mapper | Object-table mapper |
| `Table` | Core table definition | Core में table की परिभाषा |
| `Row` | Tuple-like result row | Tuple जैसी result row |
| executemany | Run one statement for many param sets | एक statement कई data sets पर |
| `synchronize_session` | Keep session objects in sync after bulk update | Bulk update के बाद objects सिंक रखना |

---

## ⚡ 3-Line Summary
English: Core is the SQL expression layer returning rows; the ORM adds objects, a Session and relationships on top. Use the ORM for normal CRUD and Core for bulk and reporting work. They share one engine, so mix them freely through the same session.
Hindi: Core SQL expression परत है जो rows लौटाती है; ORM उसके ऊपर objects, Session और relationships जोड़ता है। सामान्य CRUD के लिए ORM और bulk/reporting के लिए Core उपयोग करें। दोनों एक ही engine साझा करते हैं, इसलिए एक ही session से मिलाकर चला सकते हैं।

---

## ➡️ Next Topic
**336. SQLAlchemy 2.0 Changes** — the new typed `Mapped[]` style, `select()` everywhere, and the removal of autocommit and `engine.execute`.
