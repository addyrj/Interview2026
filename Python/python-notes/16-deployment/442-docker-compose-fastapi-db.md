---

# 442. Docker Compose + FastAPI + DB
# हिंदी में: Docker Compose + FastAPI + Database

---

## 🔵 Simple Definition (English)
Docker Compose describes a multi-container app in one `docker-compose.yml` file: the FastAPI service, PostgreSQL, Redis and so on. One command (`docker compose up`) builds, networks and starts them all. Services reach each other by service name, like `db:5432`.

## 🔵 सरल परिभाषा (Hindi)
Docker Compose multi-container app को एक `docker-compose.yml` file में बताता है: FastAPI service, PostgreSQL, Redis आदि। एक command (`docker compose up`) सबको build, network से जोड़ना और चालू करना कर देती है। Services एक-दूसरे को service के नाम से पाती हैं, जैसे `db:5432`।

---

## 🔴 Problem it Solves
A real FastAPI app needs a database, a cache and maybe a worker. Starting each with long `docker run` commands, creating networks, remembering port numbers and volumes, and waiting for the database to be ready is error-prone. New developers need a README of 20 steps. Compose turns that into one declarative file that everybody (and CI) runs the same way.

## 🔴 यह क्यों बना? (Hindi)
असली FastAPI app को database, cache और शायद worker चाहिए। हर एक को लंबे `docker run` commands से चलाना, networks बनाना, ports और volumes याद रखना और database तैयार होने का इंतज़ार करना गलतियों का घर है। नए developers को 20 steps का README चाहिए। Compose इसे एक declarative file बना देता है जिसे सब (और CI) एक जैसे चलाते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Write docker-compose.yml: services (api, db), volumes, env
Step 2 → docker compose up --build  creates a private network automatically
Step 3 → Each service gets a DNS name = its service name (api reaches Postgres at host "db")
Step 4 → db has a healthcheck (pg_isready); api uses depends_on: condition: service_healthy
Step 5 → Named volume "pgdata" stores database files so data survives container removal
Step 6 → Only api publishes a host port (8000:8000); db stays private to the network
Step 7 → Secrets come from a .env file next to the compose file (${DB_PASSWORD})
Step 8 → docker compose down (keeps volume)  /  down -v (deletes data!)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → docker-compose.yml लिखो: services (api, db), volumes, env
Step 2 → docker compose up --build अपने आप private network बनाता है
Step 3 → हर service को DNS नाम = service का नाम मिलता है (api, Postgres को host "db" से पाता है)
Step 4 → db में healthcheck (pg_isready); api में depends_on: condition: service_healthy
Step 5 → Named volume "pgdata" database files रखता है ताकि container हटने पर भी data बचे
Step 6 → सिर्फ api host port publish करता है (8000:8000); db network के अंदर निजी रहता है
Step 7 → Secrets .env file से आते हैं (${DB_PASSWORD})
Step 8 → docker compose down (volume रहता है) / down -v (data मिट जाता है!)
```

---

## 🟡 Real World Example
A Swiggy-style order service has `api` (FastAPI), `db` (PostgreSQL), `redis` (cache and Celery broker) and `worker` (Celery). A new developer clones the repo, copies `.env.example` to `.env`, runs `docker compose up` and has the whole stack, including migrations, in two minutes. The same file starts the stack in GitHub Actions for integration tests.

## 🟡 Real Example Hindi mein
Swiggy जैसी order service में `api` (FastAPI), `db` (PostgreSQL), `redis` (cache और Celery broker) और `worker` (Celery) हैं। नया developer repo clone करता है, `.env.example` को `.env` में copy करता है, `docker compose up` चलाता है और दो मिनट में migrations समेत पूरा stack तैयार। वही file GitHub Actions में integration tests के लिए stack चालू करती है।

---

## 💻 Code Example — Basic
The FastAPI side: it reads `DATABASE_URL` from the environment (Compose sets it to `...@db:5432/...`). For this demo it falls back to in-memory SQLite so it runs anywhere:

```python
# Basic: FastAPI + SQLAlchemy reading DATABASE_URL (Compose injects the Postgres URL)
import os                                         # env vars
from fastapi import Depends, FastAPI              # framework
from fastapi.testclient import TestClient         # test client
from sqlalchemy import String, create_engine, select   # engine + query
from sqlalchemy.pool import StaticPool         # shared in-memory SQLite
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column   # ORM

# In Compose: postgresql+psycopg://app:secret@db:5432/appdb   ("db" = the service name)
DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite://")    # sqlite fallback for local demo
if DATABASE_URL.startswith("sqlite"):             # SQLite needs two special settings for threads
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
else:                                             # Postgres: normal pooled engine
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)   # pre_ping drops dead connections


class Base(DeclarativeBase):
    pass


class Todo(Base):
    __tablename__ = "todos"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))


Base.metadata.create_all(engine)                  # demo only; use Alembic in production
app = FastAPI()


def get_db():
    with Session(engine) as s:                    # one session per request
        yield s


@app.post("/todos")
def add(title: str, db: Session = Depends(get_db)) -> dict[str, int]:
    t = Todo(title=title)
    db.add(t); db.commit()                        # save
    return {"id": t.id}


@app.get("/todos")
def all_todos(db: Session = Depends(get_db)) -> list[str]:
    return list(db.scalars(select(Todo.title)))   # titles only


c = TestClient(app)
print(c.post("/todos", params={"title": "buy milk"}).json())
print(c.get("/todos").json())

# Output (real run, Python 3.13):
# {'id': 1}
# ['buy milk']
```

The compose file (**not run**: no Docker daemon here; the YAML itself was parsed and checked by the validator in the advanced example):

```yaml
# docker-compose.yml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      # "db" is the service name below; Docker DNS resolves it
      DATABASE_URL: postgresql+psycopg://app:${DB_PASSWORD}@db:5432/appdb
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped

  db:
    image: postgres:17
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: appdb
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d appdb"]
      interval: 5s
      timeout: 3s
      retries: 10

volumes:
  pgdata:
```

```bash
# .env (never commit)  ->  DB_PASSWORD=change-me
docker compose up --build -d      # start in background
docker compose logs -f api        # follow API logs
docker compose exec db psql -U app appdb
docker compose down               # stop, keep data
```

## 💻 Code Example — Advanced
A validator for the compose file. It checks `depends_on` conditions, healthchecks, declared volumes and that the DB port is not published. It ran on the file above and on a deliberately broken copy:

```python
# Advanced: validate docker-compose.yml (healthchecks, depends_on, volumes, secrets)
import yaml                                       # PyYAML

COMPOSE = """
services:
  api:
    build: .
    ports: ["8000:8000"]
    environment:
      DATABASE_URL: postgresql+psycopg://app:${DB_PASSWORD}@db:5432/appdb
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped
  db:
    image: postgres:17
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: appdb
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d appdb"]
      interval: 5s
      timeout: 3s
      retries: 10
volumes:
  pgdata:
"""


def validate(text: str) -> list[str]:
    cfg = yaml.safe_load(text)                    # parse YAML to dict (raises on bad syntax)
    svcs: dict = cfg["services"]
    problems: list[str] = []
    for name, svc in svcs.items():
        for dep, opts in (svc.get("depends_on") or {}).items():
            if dep not in svcs:
                problems.append(f"{name}: depends_on unknown service {dep}")
            elif not isinstance(opts, dict) or opts.get("condition") != "service_healthy":
                problems.append(f"{name}: wait for {dep} to be HEALTHY, not just started")
            elif "healthcheck" not in svcs[dep]:
                problems.append(f"{dep}: no healthcheck defined")
        for v in svc.get("volumes", []):
            src = v.split(":")[0]
            if not src.startswith((".", "/")) and src not in cfg.get("volumes", {}):
                problems.append(f"{name}: named volume {src} not declared")
        if "ports" in svc and name == "db":
            problems.append("db: do not publish the database port")
    return problems


print(validate(COMPOSE) or "compose OK")          # compose OK
print(validate(COMPOSE.replace("condition: service_healthy", "condition: service_started")))

# Output (real run, Python 3.13):
# compose OK
# ['api: wait for db to be HEALTHY, not just started']
```

For a PostgreSQL-ready app, add `psycopg[binary]` to `requirements.txt` and run migrations with Alembic as a one-shot service (**not run**):

```yaml
  migrate:
    build: .
    command: alembic upgrade head
    environment:
      DATABASE_URL: postgresql+psycopg://app:${DB_PASSWORD}@db:5432/appdb
    depends_on:
      db:
        condition: service_healthy
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python stack | Node stack |
|---------|-------------|-----------|
| App service | FastAPI + uvicorn | Express/Nest + node |
| DB URL | `postgresql+psycopg://app:pw@db:5432/appdb` | `postgres://app:pw@db:5432/appdb` |
| Migrations | Alembic | Prisma / Knex / TypeORM |
| Hot reload in dev | `--reload` + bind mount | `nodemon` + bind mount |
| Compose file | identical | identical |

```python
# Python way — read the URL Compose injects
import os
url: str = os.environ["DATABASE_URL"]      # KeyError if Compose forgot it: fail fast
```
```javascript
// JavaScript way — same idea
const url = process.env.DATABASE_URL;      // undefined if missing - add your own check
if (!url) throw new Error("DATABASE_URL missing");
```

Key difference: the Compose file does not care about the language; only the connection string format and the migration tool change. In Python, SQLAlchemy needs the driver in the URL scheme (`postgresql+psycopg://`), while Node drivers usually accept `postgres://`.

---

## 🟠 FastAPI Connection
In Compose, "localhost" inside the `api` container is the container itself, not the database, so you must use the service name `db`. `depends_on` with `service_healthy` waits for Postgres to accept connections, but production code should still retry on startup (the DB can restart later). Use `pool_pre_ping=True` so SQLAlchemy discards dead pooled connections after a DB restart. For development add a bind mount and `--reload` in a `docker-compose.override.yml`.

```python
# FastAPI example — wait for the database on startup with retries
import time
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

def wait_for_db(url: str, attempts: int = 5, delay: float = 0.0) -> bool:
    engine = create_engine(url, pool_pre_ping=True)     # drops dead connections
    for i in range(1, attempts + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))          # cheapest possible query
            return True
        except OperationalError:
            time.sleep(delay)                           # database not ready yet
    return False

print(wait_for_db("sqlite://"))                         # True (SQLite is always ready)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `localhost` as the database host inside a container
✅ Correct: use the service name

```python
# Wrong: connects to the api container itself
url = "postgresql+psycopg://app:pw@localhost:5432/appdb"
# Right: Docker DNS resolves "db" to the Postgres container
url = "postgresql+psycopg://app:pw@db:5432/appdb"
```

❌ Mistake 2: `depends_on: [db]` only (waits for start, not readiness)
✅ Correct: add a healthcheck and `condition: service_healthy`

```yaml
# Wrong
depends_on: [db]
# Right
depends_on:
  db:
    condition: service_healthy
```

❌ Mistake 3: Publishing the DB port and running `down -v` carelessly
✅ Correct: keep the DB private; remember `-v` deletes the named volume (all data)

```yaml
# Wrong (db anyone can reach on the host's public IP)
ports: ["5432:5432"]
# Right: no ports on db. For local admin use: docker compose exec db psql ...
```

---

## 🧠 Tricky Interview Question

```yaml
services:
  db:
    image: postgres:17
    environment:
      POSTGRES_PASSWORD: old
    volumes:
      - pgdata:/var/lib/postgresql/data
volumes:
  pgdata:
```
Question: you start the stack, then change `POSTGRES_PASSWORD` to `new` and run `docker compose up -d` again. Can you now log in with `new`?

Answer: No: you still need `old`. The `POSTGRES_*` variables are used only when the data directory is empty (first initialization). Once the `pgdata` volume contains a database, Postgres ignores them. Recreating the container (even with a new env value) keeps the same volume and the same password. To change it, run `ALTER USER app PASSWORD 'new'` inside the database, or (development only) delete the volume with `docker compose down -v` so initialization happens again, losing all data.

---

## ⚫ Interview Questions + Answers

Q1: How do containers in Compose find each other?
A1: Compose creates a default bridge network for the project. Each service gets a DNS name equal to its service name, and containers on that network reach each other on the container port (e.g. `db:5432`), not the host-published port.

Q2: `ports` vs `expose`?
A2: `ports: "8000:8000"` publishes a container port on the host. `expose` only documents/opens a port to other containers and is mostly informational, since services on the same network can already reach each other's ports.

Q3: How do you handle secrets in Compose?
A3: Use a `.env` file kept out of git for dev. For production use Docker/Swarm secrets, or a platform secret manager (AWS Secrets Manager, Vault) and inject values at deploy time. Never bake them into the image or commit them.

Q4: `volumes` vs bind mounts?
A4: A named volume is managed by Docker and is best for database data. A bind mount (`./app:/app`) maps a host folder, great for live code reload in development but not for production data.

Q5: Is Compose good for production?
A5: Fine for a single server or small projects (with `restart: unless-stopped`). For multi-node, rolling updates and autoscaling use Kubernetes, ECS or Nomad. Compose files are still useful for local development and CI in those cases.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Local development with a DB, cache and worker
- Integration tests in CI
- A small production deployment on one VPS

❌ Avoid when:
- You need autoscaling, multi-node scheduling or self-healing across machines
- The database holds critical data and you have no backups (prefer managed RDS)
- You want zero-downtime rolling deploys out of the box

---

## 📊 Visual Diagram
```
 docker compose up
   |
   +--> network "app_default"
         |
   [ api :8000 ] ----(db:5432)----> [ db (postgres:17) ] -- volume pgdata
        ^                                  ^ healthcheck pg_isready
   host:8000 (published)             not published to host
        ^
   Browser / curl
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Service | One container definition | एक container की परिभाषा |
| Named volume | Docker-managed persistent storage | Docker का स्थायी storage |
| Bind mount | Host folder mapped in | host का folder जोड़ना |
| healthcheck | Command that tells if the service is ready | service तैयार है या नहीं बताने वाला command |
| depends_on | Start order and conditions | शुरू होने का क्रम |
| `.env` | File with variables for Compose | Compose के variables की file |

---

## ⚡ 3-Line Summary
English: Compose runs your API, database and helpers as one stack from one YAML file. Use service names as hostnames, healthchecks for readiness and named volumes for data. Keep the database private and secrets out of git.
Hindi: Compose आपके API, database और helpers को एक YAML file से एक stack की तरह चलाता है। Hostname के लिए service नाम, readiness के लिए healthcheck और data के लिए named volumes इस्तेमाल करो। Database को निजी और secrets को git से बाहर रखो।

---

## ➡️ Next Topic
**443. Deploy on AWS EC2** — move from your laptop or a generic VPS to a real cloud virtual machine on AWS.
