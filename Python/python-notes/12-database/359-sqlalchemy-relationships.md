---

# 359. SQLAlchemy Relationships
# हिंदी में: SQLAlchemy Relationships (Tables को आपस में जोड़ना)

---

## 🔵 Simple Definition (English)
A relationship connects two models so you can move between them as Python attributes: `user.orders` gives all orders, `order.user` gives the owner. The database stores this with a `ForeignKey`; `relationship()` adds the Python convenience on top. Types: one-to-many, many-to-one, one-to-one, many-to-many.

## 🔵 सरल परिभाषा (Hindi)
Relationship दो models को जोड़ती है ताकि आप Python attributes से एक से दूसरे तक जा सकें: `user.orders` सारे orders देता है, `order.user` मालिक देता है। Database इसे `ForeignKey` से रखता है; `relationship()` ऊपर से Python की सुविधा जोड़ता है। प्रकार: one-to-many, many-to-one, one-to-one, many-to-many।

---

## 🔴 Problem it Solves
Without relationships you write JOINs by hand and glue results together, and you must copy foreign-key ids around (`Order(user_id=user.id)`). Deleting a parent can leave orphan rows. Relationships let you write `user.orders.append(order)`, cascade deletes, and load related data efficiently in one or two queries instead of hundreds.

## 🔴 यह क्यों बना? (Hindi)
Relationships के बिना आपको JOIN हाथ से लिखने और results जोड़ने पड़ते हैं, और foreign-key ids खुद कॉपी करने पड़ते हैं (`Order(user_id=user.id)`)। Parent delete करने पर अनाथ rows बच सकती हैं। Relationships से आप `user.orders.append(order)` लिख सकते हैं, cascade delete कर सकते हैं और related data सैकड़ों queries की जगह एक-दो queries में load कर सकते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Child table gets a ForeignKey column: orders.user_id -> users.id
Step 2 → Parent: orders: Mapped[list["Order"]] = relationship(back_populates="user")
Step 3 → Child:  user: Mapped["User"] = relationship(back_populates="orders")
Step 4 → back_populates keeps both sides in sync in Python memory
Step 5 → cascade="all, delete-orphan" copies save/delete actions to children
Step 6 → Loading strategy decides when related rows are fetched:
         lazy (on access, default) | selectinload (2nd query IN) | joinedload (JOIN)
Step 7 → Many-to-many uses an association table (two foreign keys)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Child table में ForeignKey column: orders.user_id -> users.id
Step 2 → Parent: orders: Mapped[list["Order"]] = relationship(back_populates="user")
Step 3 → Child:  user: Mapped["User"] = relationship(back_populates="orders")
Step 4 → back_populates Python memory में दोनों तरफ sync रखता है
Step 5 → cascade="all, delete-orphan" save/delete actions को children तक पहुंचाता है
Step 6 → Loading strategy तय करती है related rows कब आएं:
         lazy (access पर, डिफ़ॉल्ट) | selectinload (दूसरी IN query) | joinedload (JOIN)
Step 7 → Many-to-many में association table (दो foreign keys) होती है
```

---

## 🟡 Real World Example
Swiggy-style data: `Restaurant` has many `MenuItem`s (one-to-many), each `Order` belongs to one `User`, and an `Order` has many `Dish`es while a `Dish` appears in many orders (many-to-many through `order_items`). The "my orders" screen must show 20 orders with their items; with `selectinload` this costs 2 queries instead of 21.

## 🟡 Real Example Hindi mein
Swiggy जैसा data: `Restaurant` के कई `MenuItem` (one-to-many), हर `Order` एक `User` का, और एक `Order` में कई `Dish` जबकि एक `Dish` कई orders में (`order_items` से many-to-many)। "मेरे orders" screen को 20 orders उनके items के साथ दिखाने हैं; `selectinload` से 21 की जगह 2 queries लगती हैं।

---

## 💻 Code Example — Basic
```python
# Basic one-to-many with back_populates and cascade
from sqlalchemy import ForeignKey, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Author(Base):
    __tablename__ = "authors"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    books: Mapped[list["Book"]] = relationship(back_populates="author", cascade="all, delete-orphan")  # parent side


class Book(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))   # the real DB link
    author: Mapped["Author"] = relationship(back_populates="books")    # child side


engine = create_engine("sqlite://")
Base.metadata.create_all(engine)

with Session(engine) as s:
    a = Author(name="Premchand")                          # parent
    a.books.append(Book(title="Godaan"))                  # no ids needed
    a.books.append(Book(title="Gaban"))                   # second child
    s.add(a)                                              # cascade saves the books too
    s.commit()

    book = s.scalars(select(Book).where(Book.title == "Gaban")).one()
    print(book.author.name)                               # Premchand (many-to-one)
    print([b.title for b in a.books])                     # ['Godaan', 'Gaban'] (one-to-many)

    a.books.remove(book)                                  # delete-orphan: removed from list -> DELETE
    s.commit()
    print(s.scalars(select(Book.title)).all())            # ['Godaan']

    s.delete(a)                                           # cascade deletes remaining books
    s.commit()
    print(s.scalars(select(Book)).all())                  # []

# Output:
# Premchand
# ['Godaan', 'Gaban']
# ['Godaan']
# []
```

## 💻 Code Example — Advanced
```python
# Production style: many-to-many, loading strategies, N+1 count using SQL event
from sqlalchemy import Column, ForeignKey, Table, create_engine, event, select
from sqlalchemy.orm import (DeclarativeBase, Mapped, Session, joinedload, mapped_column,
                            relationship, selectinload)


class Base(DeclarativeBase):
    pass


order_items = Table(                                      # association table for many-to-many
    "order_items", Base.metadata,
    Column("order_id", ForeignKey("orders.id"), primary_key=True),
    Column("dish_id", ForeignKey("dishes.id"), primary_key=True),
)


class Dish(Base):
    __tablename__ = "dishes"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    orders: Mapped[list["Order"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)   # index FKs!
    user: Mapped[User] = relationship(back_populates="orders")
    dishes: Mapped[list[Dish]] = relationship(secondary=order_items)           # many-to-many


engine = create_engine("sqlite://")
Base.metadata.create_all(engine)

queries: list[str] = []                                   # collect executed SQL
event.listen(engine, "before_cursor_execute", lambda conn, cur, stmt, *a: queries.append(stmt))

with Session(engine) as s:                                # seed: 3 users x 2 orders, each with 2 dishes
    dishes = [Dish(name=n) for n in ("dosa", "idli", "vada")]
    s.add_all(dishes)
    for i in range(3):
        u = User(name=f"user{i}")
        u.orders = [Order(dishes=dishes[:2]), Order(dishes=dishes[1:])]
        s.add(u)
    s.commit()

    def count(label: str, stmt) -> None:
        queries.clear()                                   # reset counter
        users = s.scalars(stmt).unique().all()            # run the query (unique() needed for joinedload collections)
        names = [d.name for u in users for o in u.orders for d in o.dishes]   # touch relationships
        print(f"{label}: {len(queries)} queries, {len(names)} dishes")
        s.expire_all()                                    # forget loaded data for a fair test

    count("lazy (N+1)", select(User))                                              # default
    count("selectinload", select(User).options(selectinload(User.orders).selectinload(Order.dishes)))
    count("joinedload orders", select(User).options(joinedload(User.orders).selectinload(Order.dishes)))

# Output:
# lazy (N+1): 10 queries, 12 dishes
# selectinload: 3 queries, 12 dishes
# joinedload orders: 2 queries, 12 dishes
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | SQLAlchemy | Prisma (JS) |
|---------|-----------|-------------|
| Define link | `ForeignKey` + `relationship()` | `@relation` in schema |
| Load related | `selectinload(User.orders)` | `include: { orders: true }` |
| Lazy load on access | yes (default, silent!) | no (you must `include`) |
| Many-to-many | association `Table` / model | implicit join table |

```python
# Python way
users = session.scalars(select(User).options(selectinload(User.orders))).all()   # 2 queries
print(users[0].orders)                                                          # already loaded
```
```javascript
// JavaScript way (Prisma)
const users = await prisma.user.findMany({ include: { orders: true } });   // related rows included
console.log(users[0].orders);
```

Key difference: Prisma never lazy-loads, so you cannot get hidden N+1 queries by accident. SQLAlchemy lazy-loads on attribute access by default, which is convenient but dangerous in loops. In async SQLAlchemy lazy loading raises an error, which forces you to choose eager loading.

---

## 🟠 FastAPI Connection
Return nested JSON by pairing ORM relationships with nested Pydantic models, and eager-load in the query so the serializer does not trigger extra queries (or errors after the session closes).

```python
# FastAPI: nested response with selectinload
from collections.abc import Iterator
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, ConfigDict
from sqlalchemy import ForeignKey, create_engine, select
from sqlalchemy.orm import (DeclarativeBase, Mapped, Session, mapped_column, relationship,
                            selectinload, sessionmaker)
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    pass


class Team(Base):
    __tablename__ = "teams"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    players: Mapped[list["Player"]] = relationship(back_populates="team")


class Player(Base):
    __tablename__ = "players"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    team: Mapped[Team] = relationship(back_populates="players")


class PlayerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str


class TeamOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    players: list[PlayerOut]                              # nested relationship


engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(engine)
with SessionLocal() as s:                                 # seed data
    s.add(Team(name="CSK", players=[Player(name="Dhoni"), Player(name="Jadeja")]))
    s.commit()

app = FastAPI()


def get_db() -> Iterator[Session]:
    with SessionLocal() as db:
        yield db


@app.get("/teams", response_model=list[TeamOut])
def teams(db: Session = Depends(get_db)) -> list[Team]:
    return list(db.scalars(select(Team).options(selectinload(Team.players))))   # eager load


print(TestClient(app).get("/teams").json())               # [{'name': 'CSK', 'players': [{'name': 'Dhoni'}, {'name': 'Jadeja'}]}]
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: N+1 queries from lazy loading in a loop
✅ Correct: eager load with `selectinload` / `joinedload`

```python
# Wrong: 1 query for users + 1 per user
for u in session.scalars(select(User)):
    print(len(u.orders))
# Right: 2 queries total
for u in session.scalars(select(User).options(selectinload(User.orders))):
    print(len(u.orders))
```

❌ Mistake 2: Missing `back_populates` / using both sides inconsistently
✅ Correct: set `back_populates` on both sides (names must match)

```python
# Wrong: the two relationships are unrelated; changes on one side are not mirrored
orders = relationship("Order")            # in User
user = relationship("User")               # in Order
# Right
orders = relationship("Order", back_populates="user")
user = relationship("User", back_populates="orders")
```

❌ Mistake 3: Forgetting `delete-orphan` / cascade, leaving or failing on children
✅ Correct: choose the cascade deliberately

```python
# Wrong: deleting a user with orders fails (NOT NULL FK) or leaves orphans
orders = relationship("Order", back_populates="user")
# Right
orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
from sqlalchemy import ForeignKey, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship

class Base(DeclarativeBase): pass
class P(Base):
    __tablename__ = "p"
    id: Mapped[int] = mapped_column(primary_key=True)
    kids: Mapped[list["C"]] = relationship(back_populates="parent")
class C(Base):
    __tablename__ = "c"
    id: Mapped[int] = mapped_column(primary_key=True)
    p_id: Mapped[int | None] = mapped_column(ForeignKey("p.id"))
    parent: Mapped[P | None] = relationship(back_populates="kids")

p1, p2 = P(), P()
c = C(parent=p1)
print(len(p1.kids), len(p2.kids))
c.parent = p2
print(len(p1.kids), len(p2.kids), c.p_id)
```
Answer: `1 0`, then `0 1 None`. With `back_populates`, setting `c.parent = p1` immediately appends `c` to `p1.kids` in memory (no database needed). Moving it to `p2` removes it from `p1.kids` and adds it to `p2.kids`. `c.p_id` is still `None` because the foreign key is only filled at flush time, when the objects are saved.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `ForeignKey` and `relationship()`?
A1: `ForeignKey` is a database column constraint. `relationship()` is ORM-only, it does not create a column; it gives Python attribute access and tells the unit of work how to fill the foreign key.

Q2: What is the N+1 problem and how do you fix it?
A2: One query loads N parents, then lazy loading runs one query per parent for its children. Fix with `selectinload` (second query with IN, best for collections) or `joinedload` (single JOIN, best for many-to-one). Detect it by logging SQL (`echo=True`).

Q3: `selectinload` vs `joinedload`?
A3: `joinedload` uses one query with a LEFT JOIN and repeats parent columns per child (needs `.unique()` for collections). `selectinload` runs a second `SELECT ... WHERE parent_id IN (...)`, no duplicated rows. Use selectin for one-to-many, joined for many-to-one.

Q4: How do you model many-to-many?
A4: Use an association table with two foreign keys that form a composite primary key, and `relationship(secondary=table)`. If the link needs extra columns (quantity, date), make it a full model (association object) instead.

Q5: What do cascade options mean?
A5: `save-update` (default) saves children with the parent, `delete` deletes children with the parent, `delete-orphan` deletes a child removed from the parent's collection. `"all, delete-orphan"` is the common choice for owned children. Do not use it where children belong to many parents.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Navigating between related rows as objects
- You need cascades and consistent in-memory graphs
- You can choose eager loading for lists

❌ Avoid when:
- Huge aggregations: write a JOIN/GROUP BY query instead of loading objects
- Loading deep graphs for read-only reports (select only needed columns)
- Async code relying on implicit lazy loads (they raise errors)

---

## 📊 Visual Diagram
```
users                        orders                       order_items        dishes
+----+-------+               +----+---------+             +----------+       +----+------+
| id | name  | 1 ----------< | id | user_id |  1 -------< | order_id |  >--1 | id | name |
+----+-------+  one-to-many  +----+---------+  many-to-many| dish_id  |       +----+------+
   ^   user.orders [list]        order.user (many-to-one)   +----------+
   '-- relationship(back_populates)  |  FK column = real DB link

lazy:        1 + N queries          selectinload: 1 + 1 queries (IN)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ForeignKey | Column pointing to another table's key | दूसरी table की key की ओर इशारा |
| relationship | ORM link between models | Models के बीच ORM कड़ी |
| back_populates | Keeps both sides in sync | दोनों तरफ sync रखना |
| cascade | Pass actions to children | Actions को children तक पहुंचाना |
| N+1 | One query plus one per row | एक query और फिर हर row की एक |
| Association table | Table linking two tables many-to-many | Many-to-many जोड़ने वाली table |

---

## ⚡ 3-Line Summary
English: Relationships link models with `ForeignKey` plus `relationship(back_populates=...)`. Choose cascades on purpose and eager-load collections to avoid N+1 queries. Many-to-many needs an association table.
Hindi: Relationships models को `ForeignKey` और `relationship(back_populates=...)` से जोड़ती हैं। Cascades सोच-समझकर चुनें और N+1 queries से बचने के लिए collections eager-load करें। Many-to-many के लिए association table चाहिए।

---

## ➡️ Next Topic
**360. SQLAlchemy Migrations** — change your schema safely over time with Alembic.
