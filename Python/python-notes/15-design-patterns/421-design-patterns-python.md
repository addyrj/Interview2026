---

# 421. Design Patterns in Python — Complete Guide
# हिंदी में: Design Patterns in Python — पूरी Guide

---

## 🔵 Simple Definition (English)
Design patterns are reusable solutions to common software design problems. Python makes many patterns simpler than in Java/C++ because of its dynamic nature, first-class functions, and duck typing. Key patterns for interviews: Singleton (one instance), Factory (create objects), Observer (event system), Strategy (swap algorithms), Repository (data access layer), Dependency Injection (decouple dependencies).

## 🔵 सरल परिभाषा (Hindi)
Design patterns = common software design problems के reusable solutions। Python में Java/C++ से simpler — dynamic nature, first-class functions, duck typing की वजह से। Interview के लिए key: Singleton, Factory, Observer, Strategy, Repository, Dependency Injection।

---

## 💻 Code Example — Basic (Singleton + Factory)
```python
# ─── Singleton — only one instance of a class ────────────────────
# Python pattern 1: Module-level (easiest, most Pythonic):
# database.py
class Database:
    def __init__(self, url: str):
        self.url = url
        self.connection = None

    def connect(self):
        self.connection = create_connection(self.url)

# Module-level singleton — created once when module imported:
_db = Database(url="postgresql://localhost/myapp")
def get_db() -> Database:
    return _db

# Python pattern 2: Metaclass singleton:
class SingletonMeta(type):
    _instances: dict = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class Config(metaclass=SingletonMeta):
    def __init__(self):
        self.db_url = "postgresql://..."
        self.redis_url = "redis://..."

c1 = Config()
c2 = Config()
print(c1 is c2)   # True — same instance

# ─── Factory — create objects without specifying exact class ──────
from abc import ABC, abstractmethod
from typing import Type

class Storage(ABC):
    @abstractmethod
    async def save(self, key: str, data: bytes) -> str: ...
    
    @abstractmethod
    async def load(self, key: str) -> bytes: ...

class S3Storage(Storage):
    async def save(self, key: str, data: bytes) -> str:
        # upload to S3...
        return f"s3://bucket/{key}"
    
    async def load(self, key: str) -> bytes:
        # download from S3...
        return b""

class LocalStorage(Storage):
    async def save(self, key: str, data: bytes) -> str:
        with open(f"./uploads/{key}", "wb") as f:
            f.write(data)
        return f"./uploads/{key}"
    
    async def load(self, key: str) -> bytes:
        with open(f"./uploads/{key}", "rb") as f:
            return f.read()

# Factory function (Pythonic — no factory class needed):
def create_storage(storage_type: str) -> Storage:
    registry = {
        "s3": S3Storage,
        "local": LocalStorage,
    }
    cls = registry.get(storage_type)
    if cls is None:
        raise ValueError(f"Unknown storage type: {storage_type}")
    return cls()

# Usage:
storage = create_storage(os.getenv("STORAGE_TYPE", "local"))
await storage.save("file.pdf", data)
```

## 💻 Code Example — Advanced (Observer, Strategy, Repository, DI)
```python
from typing import Callable, Any
from dataclasses import dataclass

# ─── Observer — event-driven notification ─────────────────────────
class EventBus:
    """Simple pub/sub event bus."""
    
    def __init__(self):
        self._handlers: dict[str, list[Callable]] = {}
    
    def subscribe(self, event: str, handler: Callable) -> None:
        self._handlers.setdefault(event, []).append(handler)
    
    def unsubscribe(self, event: str, handler: Callable) -> None:
        if event in self._handlers:
            self._handlers[event].remove(handler)
    
    async def publish(self, event: str, **data) -> None:
        for handler in self._handlers.get(event, []):
            await handler(**data)

# Usage:
bus = EventBus()

async def send_welcome_email(user_id: int, email: str):
    # send email...
    pass

async def create_user_profile(user_id: int, **kwargs):
    # create profile...
    pass

bus.subscribe("user.registered", send_welcome_email)
bus.subscribe("user.registered", create_user_profile)

# When user registers:
await bus.publish("user.registered", user_id=42, email="user@example.com")
# Both handlers called automatically

# ─── Strategy — swap algorithms at runtime ────────────────────────
from abc import ABC, abstractmethod

class ClassificationStrategy(ABC):
    @abstractmethod
    async def classify(self, product: str) -> dict: ...

class GPT4Strategy(ClassificationStrategy):
    async def classify(self, product: str) -> dict:
        # use GPT-4o for high accuracy
        return {"code": "8517.12.00", "confidence": 0.95}

class GPT4MiniStrategy(ClassificationStrategy):
    async def classify(self, product: str) -> dict:
        # use gpt-4o-mini for low cost
        return {"code": "8517.12.00", "confidence": 0.85}

class RuleBasedStrategy(ClassificationStrategy):
    async def classify(self, product: str) -> dict:
        # regex + keyword matching
        return {"code": "unknown", "confidence": 0.50}

class TariffClassifier:
    def __init__(self, strategy: ClassificationStrategy):
        self._strategy = strategy
    
    def set_strategy(self, strategy: ClassificationStrategy) -> None:
        self._strategy = strategy
    
    async def classify(self, product: str) -> dict:
        return await self._strategy.classify(product)

# Swap strategy based on priority:
classifier = TariffClassifier(strategy=GPT4MiniStrategy())  # default: cheap
if high_value_shipment:
    classifier.set_strategy(GPT4Strategy())  # upgrade for accuracy

# ─── Repository — abstract data access ────────────────────────────
from abc import ABC, abstractmethod

class TariffRepository(ABC):
    @abstractmethod
    async def get_by_code(self, code: str) -> dict | None: ...
    
    @abstractmethod
    async def search(self, query: str, limit: int = 10) -> list[dict]: ...
    
    @abstractmethod
    async def save(self, tariff: dict) -> dict: ...

class PostgresTariffRepository(TariffRepository):
    def __init__(self, session):
        self._session = session
    
    async def get_by_code(self, code: str) -> dict | None:
        result = await self._session.execute(
            "SELECT * FROM tariffs WHERE code = :code", {"code": code}
        )
        return result.fetchone()
    
    async def search(self, query: str, limit: int = 10) -> list[dict]:
        # full-text search implementation
        ...
    
    async def save(self, tariff: dict) -> dict:
        ...

class InMemoryTariffRepository(TariffRepository):
    """For testing — no DB required."""
    
    def __init__(self):
        self._data: dict[str, dict] = {}
    
    async def get_by_code(self, code: str) -> dict | None:
        return self._data.get(code)
    
    async def search(self, query: str, limit: int = 10) -> list[dict]:
        return [t for t in self._data.values() if query.lower() in str(t).lower()][:limit]
    
    async def save(self, tariff: dict) -> dict:
        self._data[tariff["code"]] = tariff
        return tariff

# ─── Dependency Injection with FastAPI ────────────────────────────
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI()

async def get_db_session():
    async with AsyncSessionLocal() as session:
        yield session

def get_tariff_repo(session: AsyncSession = Depends(get_db_session)) -> TariffRepository:
    return PostgresTariffRepository(session)

@app.get("/tariffs/{code}")
async def get_tariff(
    code: str,
    repo: TariffRepository = Depends(get_tariff_repo)
):
    tariff = await repo.get_by_code(code)
    if not tariff:
        raise HTTPException(404, f"Tariff {code} not found")
    return tariff

# Test with InMemory repo — no DB needed:
async def test_get_tariff():
    fake_repo = InMemoryTariffRepository()
    await fake_repo.save({"code": "8517.12.00", "description": "iPhones"})
    
    app.dependency_overrides[get_tariff_repo] = lambda: fake_repo
    # run test...
    app.dependency_overrides.clear()
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python Singleton via module:
# config.py
config = {"db_url": "postgresql://...", "debug": True}
# Import and it's the same object everywhere

# Python DI via function default:
def get_service(repo: Repository = Depends(get_repo)) -> Service:
    return Service(repo)
```

```javascript
// JavaScript Singleton:
let _instance = null;
class Config {
    static getInstance() {
        if (!_instance) _instance = new Config();
        return _instance;
    }
}

// JavaScript DI (NestJS):
@Injectable()
class TariffService {
    constructor(
        @InjectRepository(Tariff)
        private tariffRepo: Repository<Tariff>
    ) {}
}
```

Key differences:
- Python modules ARE singletons naturally — importing same module returns cached object.
- FastAPI uses function-based DI (`Depends`). NestJS uses decorator-based DI.
- Python's duck typing means `isinstance()` checks are rarely needed — just call the method.
- Python Strategy pattern: often just pass a function (not a class) since functions are first-class.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Thread-unsafe Singleton
```python
# Wrong — race condition in multithreaded code:
class Singleton:
    _instance = None
    def __new__(cls):
        if cls._instance is None:      # two threads can both pass this check!
            cls._instance = super().__new__(cls)
        return cls._instance

# Correct — use threading.Lock or module-level singleton:
import threading
class ThreadSafeSingleton:
    _instance = None
    _lock = threading.Lock()
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance
```

---

## 🧠 Tricky Interview Question

**Q**: Why is the Repository pattern valuable in FastAPI apps?

**Answer**: Three reasons: (1) **Testability** — swap `PostgresTariffRepository` with `InMemoryTariffRepository` in tests, no DB setup needed. (2) **Separation of concerns** — endpoint code doesn't know HOW data is fetched (SQL, NoSQL, cache) — just calls `repo.get_by_code()`. (3) **Flexibility** — switch from PostgreSQL to MongoDB by implementing the same interface. With FastAPI's `dependency_overrides`, swapping repos for tests is one line of code.

---

## ⚫ Interview Questions + Answers

Q1: What is the Singleton pattern and when should you avoid it?
A1: Singleton ensures only one instance of a class. In Python: module-level objects ARE singletons (`import config; config.db_url` — same object everywhere). Avoid Singletons when: (1) Testing is hard — global state makes tests depend on each other. (2) Concurrency — shared mutable state needs locking. (3) Violates single responsibility — Singleton is both "create me once" AND the actual class logic. Prefer DI: inject the single instance as a dependency rather than accessing it globally.

Q2: How does Python simplify the Strategy pattern vs Java?
A2: Java requires: Strategy interface + concrete classes. Python: just pass a function (functions are first-class). Instead of `classifier.set_strategy(new GPT4Strategy())`, Python: `classify_fn = gpt4_classify; result = await classify_fn(product)`. Even simpler: `classifier = TariffClassifier(strategy=gpt4_classify)` where `strategy` is just a callable. Type hint: `strategy: Callable[[str], Awaitable[dict]]`. Eliminates the class overhead for simple strategies — use classes when strategies have state.

Q3: What is Dependency Injection and how does FastAPI implement it?
A3: DI means: instead of a class creating its own dependencies, they're provided from outside. FastAPI uses `Depends()`: `def endpoint(service: Service = Depends(get_service))` — FastAPI calls `get_service()` and injects the result. Benefits: (1) Testability — override with `app.dependency_overrides[get_service] = lambda: fake_service`. (2) Lifecycle management — `yield`-based dependencies auto-cleanup. (3) Scoping — `Depends(get_db)` creates one DB session per request automatically. (4) Composability — dependencies can have their own dependencies.

Q4: Explain the Observer pattern and give a FastAPI example.
A4: Observer: subject maintains list of observers; notifies all on state change. FastAPI example: BackgroundTasks is a lightweight observer. Full implementation: `EventBus` class with `subscribe/publish` — user registration publishes `"user.registered"`, email service and analytics service subscribed. More formal: use domain events (`@dataclass UserRegistered(domain_event: True)`), collect events in service layer, dispatch after transaction commits. Libraries: `fastapi-events`, `pydantic-events`, or just a simple dict-based event bus.

Q5: What is the difference between Factory Method and Abstract Factory?
A5: **Factory Method**: one method that creates one product. Override in subclass to change what product is created. `create_storage("s3")` → returns S3Storage. **Abstract Factory**: creates a **family of related products**. Example: `CloudFactory` that creates `S3Storage + CloudQueue + CloudCache` together — all for AWS or all for GCP. Python implementation: `factory = AWSFactory(); storage = factory.create_storage(); queue = factory.create_queue()`. In Python, often a class with multiple factory methods or a module with related creation functions — no need for formal Abstract Factory class hierarchy.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Singleton | One instance only | सिर्फ एक instance |
| Factory | Object creation abstraction | Object create करने का abstraction |
| Observer | Event notification pattern | Event notification pattern |
| Strategy | Swappable algorithms | बदलने योग्य algorithms |
| Repository | Data access abstraction | Data access का abstraction |
| DI | Inject dependencies from outside | बाहर से dependencies inject करना |
| Duck typing | If it has the method, use it | Method है तो use करो |

---

## ⚡ 3-Line Summary
English: Python simplifies many patterns — modules are natural Singletons, functions replace Strategy classes, and duck typing eliminates interface boilerplate. The most valuable patterns in FastAPI: Repository (swap DB for tests), Strategy (swap AI models), and DI with `Depends()` (inject repos/services). Observer pattern powers event-driven architectures (background tasks, webhooks, notifications).
Hindi: Python modules = natural Singletons। Repository pattern = tests में DB swap करने के लिए। FastAPI DI (`Depends()`) से dependencies inject करो — testability और flexibility दोनों।

---

## ➡️ Next Topic
**422. Factory Pattern Deep Dive** — abstract factory, registry pattern. **425. Observer** — domain events, FastAPI background tasks. **430. Dependency Injection** — FastAPI DI system complete guide.
