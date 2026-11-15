---

# 434. Clean Architecture Python
# हिंदी में: Clean Architecture (साफ-सुथरा Architecture) Python में

---

## 🔵 Simple Definition (English)
Clean Architecture splits your app into layers (entities, use cases, adapters, frameworks). The rule: source-code dependencies point only inward. Business rules never import FastAPI, SQLAlchemy or any other tool, so those tools can be swapped without touching the business logic.

## 🔵 सरल परिभाषा (Hindi)
Clean Architecture आपके app को layers में बाँटता है (entities, use cases, adapters, frameworks)। Rule यह है कि dependencies सिर्फ अंदर की तरफ जाती हैं। Business rules कभी FastAPI या SQLAlchemy को import नहीं करते, इसलिए tools बदलने पर business logic को हाथ नहीं लगाना पड़ता।

---

## 🔴 Problem it Solves
In many FastAPI projects the route function does everything: validates input, runs SQL, applies business rules and builds the response. Then:
- You cannot test a rule without a database and an HTTP server.
- Moving from SQLAlchemy to MongoDB, or from REST to a queue consumer, means rewriting everything.
- Business rules are scattered over routes, so nobody knows where "an order cannot be paid twice" really lives.

## 🔴 यह क्यों बना? (Hindi)
बहुत से FastAPI projects में route function सब कुछ करता है: input validate, SQL चलाना, business rules और response बनाना। तब:
- बिना database और HTTP server के कोई rule test नहीं हो सकता।
- SQLAlchemy से MongoDB, या REST से queue consumer पर जाने का मतलब सब दोबारा लिखना।
- Business rules routes में बिखरे रहते हैं, किसी को नहीं पता "order दो बार pay नहीं हो सकता" का असली घर कहाँ है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Entities (innermost): pure Python objects + rules ("Order.pay()")
Step 2 → Use cases: one class/function per user goal ("PayOrder"), orchestrates entities
Step 3 → Ports: small interfaces the use case needs (Protocol "OrderRepo")
Step 4 → Adapters: real implementations (SqlOrderRepo, StripeGateway, FakeRepo for tests)
Step 5 → Frameworks (outermost): FastAPI routes, SQLAlchemy models, CLI, Celery tasks
Step 6 → Route builds the use case with Depends(), calls it, maps domain errors to HTTP codes
Step 7 → Tests call the use case with a fake repo: no DB, no web, milliseconds
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Entities (सबसे अंदर): साधारण Python objects + rules ("Order.pay()")
Step 2 → Use cases: हर user goal के लिए एक class/function ("PayOrder"), entities को चलाता है
Step 3 → Ports: use case को चाहिए छोटे interfaces (Protocol "OrderRepo")
Step 4 → Adapters: असली implementations (SqlOrderRepo, StripeGateway, tests के लिए FakeRepo)
Step 5 → Frameworks (सबसे बाहर): FastAPI routes, SQLAlchemy models, CLI, Celery tasks
Step 6 → Route, Depends() से use case बनाता है, call करता है, domain errors को HTTP codes में बदलता है
Step 7 → Tests में use case को fake repo दो: न DB, न web, milliseconds में चलता है
```

---

## 🟡 Real World Example
A Razorpay-like payments service: the rule "a captured payment cannot be captured again" is an entity method. `CapturePayment` is a use case. Today the data is in PostgreSQL via `SqlPaymentRepo`; next year the team moves hot data to DynamoDB by writing `DynamoPaymentRepo`. The same use case also runs from a REST route, a Kafka consumer and a nightly reconciliation script, and none of them changes.

## 🟡 Real Example Hindi mein
Razorpay जैसी payments service: rule "captured payment दोबारा capture नहीं हो सकता" entity की method है। `CapturePayment` use case है। आज data PostgreSQL में `SqlPaymentRepo` से है; अगले साल team hot data DynamoDB में ले जाती है और `DynamoPaymentRepo` लिख देती है। वही use case REST route, Kafka consumer और रात की reconciliation script से भी चलता है, और किसी में बदलाव नहीं होता।

---

## 💻 Code Example — Basic
```python
# Basic: Clean Architecture in one file (4 layers, dependencies point inward)
from dataclasses import dataclass                 # simple data holder
from typing import Protocol                       # interface without inheritance


@dataclass
class User:                                       # LAYER 1: Entity (pure business object)
    id: int                                       # unique id
    email: str                                    # email address

    def is_corporate(self) -> bool:               # business rule lives on the entity
        return self.email.endswith("@company.com")   # True for company mail


class UserRepository(Protocol):                   # LAYER 2: port (interface the use case needs)
    def add(self, user: User) -> None: ...        # save a user
    def get(self, user_id: int) -> User | None: ...   # load a user or None


class RegisterUser:                               # LAYER 2: Use case (application logic)
    def __init__(self, repo: UserRepository) -> None:
        self.repo = repo                          # depends on the interface, not on a DB

    def execute(self, user_id: int, email: str) -> User:
        if "@" not in email:                      # validate input
            raise ValueError("invalid email")     # business error
        if self.repo.get(user_id) is not None:    # rule: ids must be unique
            raise ValueError("user exists")       # business error
        user: User = User(user_id, email.lower())   # build the entity
        self.repo.add(user)                       # persist through the port
        return user                               # return result


class InMemoryUserRepo:                           # LAYER 3: adapter (outer layer, swappable)
    def __init__(self) -> None:
        self._data: dict[int, User] = {}          # storage is just a dict here

    def add(self, user: User) -> None:
        self._data[user.id] = user                # store

    def get(self, user_id: int) -> User | None:
        return self._data.get(user_id)            # lookup


use_case: RegisterUser = RegisterUser(InMemoryUserRepo())   # LAYER 4: wire everything together
print(use_case.execute(1, "Asha@Company.com"))    # works
print(use_case.execute(2, "bob@gmail.com").is_corporate())   # business rule
try:                                              # duplicate id
    use_case.execute(1, "x@y.com")                # should fail
except ValueError as e:                           # catch business error
    print("Error:", e)                            # Error: user exists

# Output (real run, Python 3.13):
# User(id=1, email='asha@company.com')
# False
# Error: user exists
```

## 💻 Code Example — Advanced
```python
# Advanced: Clean Architecture + FastAPI + SQLAlchemy adapter, swapped in tests
from dataclasses import dataclass                 # entity
from typing import Annotated, Protocol            # DI typing and ports

from fastapi import Depends, FastAPI, HTTPException   # web framework (outer layer)
from fastapi.testclient import TestClient         # in-process HTTP client
from pydantic import BaseModel                    # request/response schema (outer layer)
from sqlalchemy import create_engine, select      # DB engine and query builder
from sqlalchemy.pool import StaticPool         # keeps in-memory SQLite alive
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column   # ORM


# ---------- domain (no imports from fastapi / sqlalchemy) ----------
@dataclass
class Order:                                      # entity
    id: int | None                                # None until saved
    user_id: int                                  # owner
    amount: int                                   # paise
    status: str = "NEW"                           # NEW or PAID

    def pay(self) -> None:                        # business rule
        if self.status == "PAID":                 # cannot pay twice
            raise ValueError("already paid")      # domain error
        self.status = "PAID"                      # state change


class OrderRepo(Protocol):                        # port
    def save(self, order: Order) -> Order: ...    # insert or update
    def get(self, order_id: int) -> Order | None: ...   # find


class PayOrder:                                   # use case
    def __init__(self, repo: OrderRepo) -> None:
        self.repo = repo                          # injected port

    def __call__(self, order_id: int) -> Order:
        order = self.repo.get(order_id)           # load
        if order is None:                         # missing
            raise LookupError("order not found")  # domain-level error
        order.pay()                               # apply rule
        return self.repo.save(order)              # persist


# ---------- adapters (infrastructure) ----------
class Base(DeclarativeBase):                      # SQLAlchemy base
    pass


class OrderRow(Base):                             # table mapping, separate from entity
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int]
    amount: Mapped[int]
    status: Mapped[str]


class SqlOrderRepo:                               # adapter implementing OrderRepo
    def __init__(self, session: Session) -> None:
        self.s = session                          # DB session

    def save(self, order: Order) -> Order:
        row = self.s.get(OrderRow, order.id) if order.id else None   # existing row?
        if row is None:                           # new order
            row = OrderRow(user_id=order.user_id, amount=order.amount, status=order.status)
            self.s.add(row)                       # stage insert
        else:                                     # existing order
            row.status = order.status             # update
        self.s.commit()                           # write to DB
        return Order(row.id, row.user_id, row.amount, row.status)   # row -> entity

    def get(self, order_id: int) -> Order | None:
        row = self.s.scalar(select(OrderRow).where(OrderRow.id == order_id))   # query
        return Order(row.id, row.user_id, row.amount, row.status) if row else None


# ---------- interface layer (FastAPI) ----------
engine = create_engine("sqlite://", connect_args={"check_same_thread": False},
                       poolclass=StaticPool)      # one shared in-memory DB for all threads
Base.metadata.create_all(engine)                  # create tables (demo only)
app: FastAPI = FastAPI()


def get_repo():                                   # dependency: yields a repo per request
    with Session(engine) as session:              # open and close the session
        yield SqlOrderRepo(session)               # adapter handed to use case


Repo = Annotated[OrderRepo, Depends(get_repo)]    # reusable annotation


class OrderOut(BaseModel):                        # response schema
    id: int
    status: str


@app.post("/orders/{order_id}/pay", response_model=OrderOut)
def pay(order_id: int, repo: Repo) -> Order:
    try:
        return PayOrder(repo)(order_id)           # run use case
    except LookupError as e:                      # map domain error -> HTTP
        raise HTTPException(404, str(e))
    except ValueError as e:
        raise HTTPException(409, str(e))


with Session(engine) as s:                        # seed one order
    SqlOrderRepo(s).save(Order(None, 7, 49900))

client = TestClient(app)                          # test client
print(client.post("/orders/1/pay").json())        # first payment
print(client.post("/orders/1/pay").status_code)   # second payment
print(client.post("/orders/99/pay").json())       # unknown order


# ---------- test the use case with NO database and NO web ----------
class FakeRepo:                                   # in-memory fake adapter
    def __init__(self) -> None:
        self.items = {1: Order(1, 7, 100)}        # one order
    def save(self, order: Order) -> Order:
        self.items[order.id] = order; return order
    def get(self, order_id: int) -> Order | None:
        return self.items.get(order_id)


assert PayOrder(FakeRepo())(1).status == "PAID"   # pure unit test, instant
print("unit test passed")

# Output (real run, Python 3.13):
# {'id': 1, 'status': 'PAID'}
# 409
# {'detail': 'order not found'}
# unit test passed
```

Note: the demo uses SQLite in memory so it runs anywhere. In production use PostgreSQL and Alembic migrations. `TestClient` prints a `StarletteDeprecationWarning` to stderr on very new Starlette versions (it prefers `httpx2`); this does not change the output.

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript / TypeScript |
|---------|--------|------------------------|
| Port (interface) | `typing.Protocol` | `interface` (TS), none in plain JS |
| Dependency injection | constructor args, `Depends()` | constructor args, NestJS `@Injectable`, InversifyJS |
| Entity | `@dataclass` | class / plain object |
| Framework layer | FastAPI | Express / NestJS controller |
| Fake for tests | any object with same methods (duck typing) | jest mock / hand-written fake |

```python
# Python way — Protocol + duck typing, no inheritance needed
from typing import Protocol

class Mailer(Protocol):                       # the port
    def send(self, to: str, text: str) -> None: ...

class Welcome:                                # use case depends on the port only
    def __init__(self, mailer: Mailer) -> None:
        self.mailer = mailer
    def run(self, email: str) -> None:
        self.mailer.send(email, "welcome")
```
```javascript
// JavaScript way — constructor injection, same idea
class Welcome {
  constructor(mailer) { this.mailer = mailer; }   // any object with send()
  run(email) { this.mailer.send(email, "welcome"); }
}
new Welcome({ send: (to, t) => console.log(to, t) }).run("a@b.com"); // fake mailer inline
```

Key difference: TypeScript needs an explicit `interface` and `implements`; Python's `Protocol` checks the shape only for type checkers (mypy/pyright), at runtime it is plain duck typing. NestJS gives you a DI container; in FastAPI `Depends()` is the container.

---

## 🟠 FastAPI Connection
FastAPI is the outermost layer. `Depends()` is the "composition root": it builds the repo, then the use case, per request. Pydantic models are the HTTP schema, separate from domain entities. Tests use `app.dependency_overrides` to swap the SQL repo for a fake without touching any business code.

```python
# FastAPI override example — swap the real repo for a fake in tests
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

app = FastAPI()

class Repo:                                    # "real" adapter
    def name(self) -> str: return "sql"

def get_repo() -> Repo:                        # dependency provider
    return Repo()

@app.get("/who")
def who(repo: Repo = Depends(get_repo)) -> dict[str, str]:
    return {"repo": repo.name()}

class FakeRepo:                                # fake adapter
    def name(self) -> str: return "fake"

app.dependency_overrides[get_repo] = lambda: FakeRepo()   # swap in tests only
print(TestClient(app).get("/who").json())      # {'repo': 'fake'}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Importing the framework inside the domain
✅ Correct: the domain knows only Python; map to HTTP in the route

```python
# Wrong — domain raises an HTTP error, now it depends on FastAPI
from fastapi import HTTPException
class Order:
    def pay(self):
        raise HTTPException(409, "already paid")   # domain tied to web

# Right — domain raises its own error, route translates it
class Order2:
    def pay(self):
        raise ValueError("already paid")           # pure Python
```

❌ Mistake 2: Returning SQLAlchemy rows from use cases
✅ Correct: map rows to entities inside the repository adapter

```python
# Wrong: use case returns an ORM object, lazy loading breaks after the session closes
# return session.get(OrderRow, 1)
# Right: repo converts to the entity (see SqlOrderRepo above)
# return Order(row.id, row.user_id, row.amount, row.status)
```

❌ Mistake 3: Over-engineering a tiny CRUD app
✅ Correct: use layers when business rules exist; a 5-endpoint CRUD can stay simple

```python
# Wrong: 12 files and 4 interfaces to save a name and an email
# Right: start simple, extract a use case when the rule/duplication appears
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
from typing import Protocol

class Repo(Protocol):
    def get(self, i: int) -> str: ...

class Fake:
    def get(self, i: int) -> str:
        return f"item{i}"

def use(r: Repo) -> str:
    return r.get(1)

print(use(Fake()))
print(isinstance(Fake(), Repo))
```
Answer: The first line prints `item1`: `Fake` never inherits from `Repo`, but it has the right method, so it satisfies the Protocol structurally and runs fine. The second line raises `TypeError: Instance and class checks can only be used with @runtime_checkable protocols`, because a plain `Protocol` cannot be used with `isinstance`. Add `@runtime_checkable` if you need that, but note it only checks that the method names exist, not their signatures.

---

## ⚫ Interview Questions + Answers

Q1: What is the Dependency Rule in Clean Architecture?
A1: Source-code dependencies must point inward only. Inner layers (entities, use cases) know nothing about outer layers (web, DB). Data crosses the boundary through interfaces (ports) that the inner layer defines and the outer layer implements; this is Dependency Inversion.

Q2: Clean Architecture vs Hexagonal vs Onion?
A2: They are the same idea with different names: protect the domain core, talk to the world through ports and adapters. Hexagonal says "ports and adapters", Onion draws rings, Clean adds the named layers (entities, use cases, interface adapters, frameworks).

Q3: Where do FastAPI's Pydantic models belong?
A3: In the outer interface layer as request/response DTOs. Entities stay plain dataclasses. Mapping between them is small but deliberate, so a change to the API does not force a change to domain rules.

Q4: How do you test a use case?
A4: Pass a fake or in-memory repository to the constructor and assert on the result. No database, no TestClient. Then add a few integration tests for the real adapter and the HTTP route.

Q5: What are the costs?
A5: More files, mapping code, and indirection. For simple CRUD it is overkill. It pays off when rules are complex, several delivery channels exist (REST, queue, CLI), or the infrastructure may change.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Real business rules exist (payments, orders, bookings)
- The same logic runs from REST, queue workers and scripts
- You want fast unit tests without a database
- The team is large and long-lived

❌ Avoid when:
- A quick prototype or simple CRUD admin API
- A single developer, a throw-away script
- The "business logic" is just save and fetch

---

## 📊 Visual Diagram
```
 +--------------------------------------------------------+
 |  Frameworks: FastAPI routes | SQLAlchemy | Celery        |
 |   +--------------------------------------------------+  |
 |   |  Adapters: SqlOrderRepo | StripeGateway | FakeRepo |  |
 |   |   +------------------------------------------+   |  |
 |   |   |  Use cases: PayOrder, RegisterUser       |   |  |
 |   |   |   +----------------------------------+   |   |  |
 |   |   |   |  Entities: Order.pay(), User     |   |   |  |
 |   |   |   +----------------------------------+   |   |  |
 |   |   +------------------------------------------+   |  |
 |   +--------------------------------------------------+  |
 +--------------------------------------------------------+
        dependencies point  ───────────►  INWARD only
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Entity | Business object with rules | business object जिसमें rules हों |
| Use case | One application goal | एक application लक्ष्य |
| Port | Interface the core needs | core की ज़रूरत का interface |
| Adapter | Concrete implementation of a port | port का असली implementation |
| Dependency Rule | Dependencies point inward | dependencies अंदर की ओर |
| Composition root | Place where objects are wired | जहाँ objects जोड़े जाते हैं |

---

## ⚡ 3-Line Summary
English: Keep business rules in plain Python objects that import no framework. Define ports for what they need and implement them with adapters. FastAPI only wires and translates, which makes tests fast and tools replaceable.
Hindi: Business rules को ऐसे साधारण Python objects में रखो जो कोई framework import न करें। जो चाहिए उसके लिए ports बनाओ और adapters से implement करो। FastAPI सिर्फ जोड़ता और अनुवाद करता है, इससे tests तेज़ और tools बदलने लायक रहते हैं।

---

## ➡️ Next Topic
**435. Domain Driven Design Python** — Clean Architecture tells you how to layer the app; DDD tells you how to model the business core itself (value objects, aggregates, domain events).
