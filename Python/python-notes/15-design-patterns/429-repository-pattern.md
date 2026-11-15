---

# 429. Repository Pattern
# हिंदी में: Repository Pattern (Database को collection जैसे interface के पीछे छिपाना)

---

## 🔵 Simple Definition (English)
A Repository is a class that hides how data is stored and gives you a simple collection-like interface (`add`, `get`, `by_email`). Business code talks to the repository and never writes SQL. You can swap the real database for an in-memory fake in tests.

## 🔵 सरल परिभाषा (Hindi)
Repository ऐसी class है जो data कैसे store होता है यह छिपाती है और collection जैसा सरल interface (`add`, `get`, `by_email`) देती है। Business code repository से बात करता है, SQL कभी नहीं लिखता। Tests में असली database की जगह in-memory fake लगाया जा सकता है।

---

## 🔴 Problem it Solves
When SQL and ORM calls are scattered across routes and services, business logic is tied to one database, queries are duplicated, and tests need a real DB. Changing from SQLite to Postgres or MongoDB means editing everything. A repository gives one place for data access and a clean seam for testing.

## 🔴 यह क्यों बना? (Hindi)
जब SQL और ORM calls routes और services में बिखरे हों तो business logic एक database से बंध जाता है, queries दोहराई जाती हैं और tests को असली DB चाहिए। SQLite से Postgres या MongoDB जाने पर सब कुछ बदलना पड़ता है। Repository data access की एक जगह और testing के लिए साफ जोड़ देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define an abstract UserRepository (add, by_email)
Step 2 → Write SqlRepo(session) using SQLAlchemy: it knows tables and queries
Step 3 → Write FakeRepo using a plain list for fast unit tests
Step 4 → The service function accepts the abstract repo
Step 5 → Routes get the repo via dependency injection
Step 6 → Rows are converted to domain objects, so ORM types do not leak out
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Abstract UserRepository बनाओ (add, by_email)
Step 2 → SQLAlchemy से SqlRepo(session) लिखो: उसे tables और queries पता हैं
Step 3 → तेज unit tests के लिए साधारण list वाली FakeRepo लिखो
Step 4 → Service function abstract repo लेता है
Step 5 → Routes को repo dependency injection से मिलता है
Step 6 → Rows domain objects में बदलती हैं, ORM types बाहर नहीं निकलते
```

---

## 🟡 Real World Example
A fintech onboarding service has `UserRepository`, `OrderRepository` and `PaymentRepository`. Services like `register(repo, email)` run in unit tests with `FakeRepo` in milliseconds, and in production with `SqlRepo` on Postgres. If the team later moves the user store to MongoDB, only the repository class changes.

## 🟡 Real Example Hindi mein
एक fintech onboarding service में `UserRepository`, `OrderRepository` और `PaymentRepository` होती हैं। `register(repo, email)` जैसी services unit tests में `FakeRepo` के साथ milliseconds में चलती हैं और production में Postgres पर `SqlRepo` के साथ। टीम बाद में user store MongoDB पर ले जाए तो सिर्फ repository class बदलेगी।

---

## 💻 Code Example — Basic
```python
# Basic Repository: hide storage behind a collection-like interface
from dataclasses import dataclass             # model


@dataclass
class User:
    id: int
    name: str


class UserRepo:
    def __init__(self) -> None:
        self._data: dict[int, User] = {}      # in-memory store

    def add(self, u: User) -> None:
        self._data[u.id] = u                  # save

    def get(self, id: int) -> User | None:
        return self._data.get(id)             # None when missing


repo: UserRepo = UserRepo()
repo.add(User(1, "Asha"))
print(repo.get(1))
print(repo.get(99))

# Output:
# User(id=1, name='Asha')
# None
```

## 💻 Code Example — Advanced
```python
# Production style: abstract repository, SQLAlchemy 2.0 implementation + in-memory fake, same service code
from abc import ABC, abstractmethod           # interface
from dataclasses import dataclass             # domain model
from sqlalchemy import String, create_engine, select   # SQLAlchemy core
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


@dataclass
class User:                                   # domain object (no SQLAlchemy inside)
    id: int | None
    email: str


class UserRepository(ABC):
    @abstractmethod
    def add(self, u: User) -> User: ...
    @abstractmethod
    def by_email(self, email: str) -> User | None: ...


class FakeRepo(UserRepository):               # for fast unit tests
    def __init__(self) -> None:
        self.items: list[User] = []
    def add(self, u: User) -> User:
        u.id = len(self.items) + 1
        self.items.append(u)
        return u
    def by_email(self, email: str) -> User | None:
        return next((u for u in self.items if u.email == email), None)


class Base(DeclarativeBase):
    pass


class UserRow(Base):                          # table mapping
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)


class SqlRepo(UserRepository):
    def __init__(self, session: Session) -> None:
        self.s = session
    def add(self, u: User) -> User:
        row = UserRow(email=u.email)
        self.s.add(row); self.s.flush()       # flush to get id
        return User(row.id, row.email)
    def by_email(self, email: str) -> User | None:
        row = self.s.scalars(select(UserRow).where(UserRow.email == email)).first()
        return User(row.id, row.email) if row else None


def register(repo: UserRepository, email: str) -> User:   # service depends on the ABC only
    if repo.by_email(email):
        raise ValueError("email already registered")
    return repo.add(User(None, email))


print(register(FakeRepo(), "a@x.com"))        # works with fake
engine = create_engine("sqlite://")           # in-memory SQLite
Base.metadata.create_all(engine)
with Session(engine) as session:
    repo = SqlRepo(session)
    print(register(repo, "a@x.com"))          # same code, real DB
    try:
        register(repo, "a@x.com")
    except ValueError as e:
        print("Error:", e)

# Output:
# User(id=1, email='a@x.com')
# User(id=1, email='a@x.com')
# Error: email already registered
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Abstraction | `ABC` / `Protocol` | TypeScript `interface` |
| ORM | SQLAlchemy, Django ORM | Prisma, TypeORM, Sequelize |
| Fake for tests | in-memory class | in-memory class / jest mock |
| Common in | DDD-style Python, FastAPI | NestJS (`@InjectRepository`) |

```python
# Python way
class UserRepository(ABC):
    @abstractmethod
    def by_email(self, email: str) -> User | None: ...
```
```javascript
// JavaScript / TypeScript way
interface UserRepository {
  byEmail(email: string): Promise<User | null>;
}
```

Key difference: NestJS bakes the repository idea into the framework. In Python it is a design choice: Django's ORM already behaves like a repository (`User.objects`), so add an extra layer only in larger FastAPI + SQLAlchemy services where you want to isolate the DB.

---

## 🟠 FastAPI Connection
FastAPI + SQLAlchemy is the classic home of repositories. A `get_repo` dependency yields a repository that wraps the request's session. Routes call `repo.get(id)` and translate `None` into `HTTPException(404)`. In tests use `app.dependency_overrides[get_repo] = lambda: FakeRepo()`.

```python
# FastAPI example (run with fastapi.testclient — no server needed)
from fastapi import Depends, FastAPI, HTTPException
from fastapi.testclient import TestClient

app: FastAPI = FastAPI()


class ItemRepo:
    def __init__(self) -> None:
        self.d: dict[int, str] = {1: "pen"}
    def get(self, i: int) -> str | None:
        return self.d.get(i)


_repo = ItemRepo()


def get_repo() -> ItemRepo:                   # dependency provides the repository
    return _repo


@app.get("/items/{item_id}")
def read(item_id: int, repo: ItemRepo = Depends(get_repo)) -> dict[str, str]:
    name = repo.get(item_id)
    if name is None:
        raise HTTPException(404, "item not found")   # route never sees SQL
    return {"name": name}


c = TestClient(app)
print(c.get("/items/1").json(), c.get("/items/2").status_code)

# Output:
# {'name': 'pen'} 404
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Leaking ORM objects or sessions outside the repository
✅ Correct: return domain objects

```python
# Wrong: def by_email(...) -> UserRow      # callers now depend on SQLAlchemy
# Right: def by_email(...) -> User | None  # plain domain dataclass
```

❌ Mistake 2: A generic repository with every possible query method
✅ Correct: add methods that match real use cases

```python
# Wrong: repo.filter(**anything)      # becomes a second ORM
# Right: repo.by_email(email), repo.active_since(date)
```

❌ Mistake 3: Returning the stored mutable object itself (in-memory repos)
✅ Correct: return a copy, change data only through `save()` / `update()`

```python
# Wrong: return self.d[i]             # caller mutates it, storage changes silently
# Right: return dict(self.d[i])       # or a frozen dataclass
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
class Repo:
    def __init__(self): self.d = {1: {"name": "Asha"}}
    def get(self, i): return self.d[i]        # returns the stored object itself
r = Repo()
u = r.get(1)
u["name"] = "HACKED"                          # no save() call
print(r.get(1))
```
Answer: Output: `{'name': 'HACKED'}`. The repository handed out a reference to its internal dict, not a copy. The caller changed it without calling any save method, so the 'database' was modified silently. A real database would not behave this way, so tests using such a fake can pass while production fails. Return copies or immutable objects.

---

## ⚫ Interview Questions + Answers

Q1: What is the Repository pattern?
A1: A class that acts like an in-memory collection of domain objects but persists them in a database. It isolates storage code from business logic.

Q2: Repository vs DAO?
A2: DAO mirrors tables/operations on one table. Repository speaks the domain language (`by_email`, `active_users`) and may combine several tables to return one aggregate.

Q3: Is Repository needed with an ORM like SQLAlchemy?
A3: Not always. A session is already a unit of work. Add repositories when you want to test without a DB, hide queries, or may switch storage. For small CRUD apps it is extra code.

Q4: Where do transactions live?
A4: Not inside each repository method. Use a Unit of Work or the request-scoped session: commit once at the end of the use case so several repository calls succeed or fail together.

Q5: How do you test with it?
A5: Unit tests use `FakeRepo`; a few integration tests run `SqlRepo` against SQLite or a Postgres container to prove the real queries work.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Business logic should not know about SQL or the ORM
- You want fast unit tests without a database
- You may change storage later
- Same queries are repeated across services

❌ Avoid when:
- Tiny CRUD app where the ORM is already enough
- Repository would only forward calls one-to-one
- Reporting queries with many joins: use a dedicated query function

---

## 📊 Visual Diagram
```
route -> service.register(repo, email)
                    |
          UserRepository (abstract)
           /                  \
     SqlRepo(session)       FakeRepo(list)
         |                      |
   SQLite/Postgres        in-memory (tests)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Repository | Collection-like data access class | Collection जैसी data access class |
| Domain object | Plain business object | सादा business object |
| Unit of Work | Group of changes committed together | साथ commit होने वाले बदलाव |
| Fake | Simple in-memory test double | In-memory test replacement |
| Aggregate | Group of related objects | संबंधित objects का समूह |

---

## ⚡ 3-Line Summary
English: A Repository hides storage behind a collection-like interface so business code never touches SQL. Use an abstract class, a real SQL implementation and an in-memory fake for tests. Return domain objects, not ORM rows.
Hindi: Repository storage को collection जैसे interface के पीछे छिपाता है ताकि business code SQL न छुए। Abstract class, असली SQL implementation और tests के लिए in-memory fake रखें। ORM rows नहीं, domain objects लौटाएं।

---

## ➡️ Next Topic
**430. Dependency Injection Pattern** — pass collaborators in instead of creating them inside.
