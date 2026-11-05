# 204. Compose for Development
# हिंदी में: Development के लिए Compose

---

## 🔵 Simple Definition (English)
Compose for development means using `docker compose` to start the whole app (API, database, cache) on your laptop with live code reload, debugger ports, seed data and easy logs, so a new developer is productive after one command.

## 🔵 सरल परिभाषा (Hindi)
Development के लिए Compose का मतलब है अपने laptop पर पूरी app (API, database, cache) `docker compose` से चलाना, live code reload, debugger ports, seed data और आसान logs के साथ, ताकि नया developer एक command के बाद काम शुरू कर सके।

---

## 🔴 Problem it Solves
"Works on my machine": one developer has Postgres 14, another 16, one has Node 18, another 22, and onboarding takes a day of installing tools. Compose pins the exact versions and removes local installs, while bind mounts keep the edit-run loop fast.

## 🔴 यह क्यों बना? (Hindi)
"मेरी machine पर चल रहा है": एक developer के पास Postgres 14 है, दूसरे के पास 16, किसी के पास Node 18 तो किसी के पास 22, और onboarding में पूरा दिन tools install करने में जाता है। Compose सही versions pin कर देता है और local install हटा देता है, जबकि bind mounts edit-run loop को तेज़ रखते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Clone repo, copy .env.example to .env
Step 2 → `docker compose up --build` builds the dev image (dev stage) and starts all services
Step 3 → Source folder is bind-mounted, so edits appear inside the container
Step 4 → nodemon / `--watch` / uvicorn --reload restarts the process on change
Step 5 → DB port is exposed on localhost so GUI tools (DBeaver, psql) connect
Step 6 → Debugger port (9229 for Node, 5678 for debugpy) lets VS Code attach
Step 7 → `docker compose down -v` gives a clean slate when data is messy
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Repo clone करें, .env.example को .env में copy करें
Step 2 → `docker compose up --build` dev image (dev stage) बनाकर सारी services चालू करता है
Step 3 → Source folder bind-mount होता है, इसलिए edits container के अंदर दिखते हैं
Step 4 → nodemon / `--watch` / uvicorn --reload बदलाव पर process restart करता है
Step 5 → DB port localhost पर खुला रहता है ताकि GUI tools (DBeaver, psql) जुड़ सकें
Step 6 → Debugger port (Node के लिए 9229, debugpy के लिए 5678) से VS Code attach होता है
Step 7 → डेटा गंदा हो जाए तो `docker compose down -v` से साफ़ शुरुआत मिलती है
```

---

## 🟡 Real World Example
A Zomato-like team of 12 engineers: a new hire runs `git clone`, `cp .env.example .env`, `docker compose up`. Within minutes they have the API at localhost:3000, Postgres seeded with 50 sample restaurants, Redis, and Mailpit (a fake SMTP inbox at localhost:8025). No local Node, Postgres or Redis installed.

## 🟡 Real Example Hindi mein
Zomato जैसी 12 engineers की team: नया hire `git clone`, `cp .env.example .env`, `docker compose up` चलाता है। कुछ मिनटों में localhost:3000 पर API, 50 sample restaurants वाला seeded Postgres, Redis, और Mailpit (localhost:8025 पर fake SMTP inbox) तैयार। Local में Node, Postgres या Redis install नहीं करना पड़ा।

---

## 💻 Code / Config Example — Basic
```yaml
# compose.yaml  (Basic dev: Node API + Postgres)
services:
  api:
    build:
      context: .                      # build from repo root
      target: dev                     # use the "dev" stage of the Dockerfile
    ports:
      - "3000:3000"                   # open the app at http://localhost:3000
    volumes:
      - ./src:/app/src                # live source code
    environment:
      DATABASE_URL: postgres://app:app@db:5432/app   # "db" is the service name = hostname
    depends_on:
      - db                            # start db first
  db:
    image: postgres:16-alpine         # example tag
    environment:
      POSTGRES_USER: app              # dev only credentials
      POSTGRES_PASSWORD: app
      POSTGRES_DB: app
    ports:
      - "127.0.0.1:5432:5432"         # reachable only from my machine
```

## 💻 Code / Config Example — Advanced
```dockerfile
# Dockerfile  (multi-stage: dev stage keeps dev tools, runtime stage is lean)
FROM node:20-alpine AS base          # shared base, example tag
WORKDIR /app                         # working directory
COPY package*.json ./                # copy manifests first for layer cache
FROM base AS dev                     # development stage
RUN npm ci                           # install ALL deps including dev
COPY . .                             # copy source (bind mount overrides it at runtime)
CMD ["npx", "nodemon", "--inspect=0.0.0.0:9229", "src/index.js"]  # reload + debugger
FROM base AS runtime                 # production stage
ENV NODE_ENV=production              # production mode
RUN npm ci --omit=dev                # only runtime deps
COPY . .                             # app code
USER node                            # non-root
CMD ["node", "src/index.js"]         # start server
```
```yaml
# compose.yaml  (Advanced dev stack)
name: myapp-dev                       # stable project name
services:
  api:
    build: { context: ., target: dev }   # dev stage
    env_file: .env                    # load variables from .env
    ports:
      - "3000:3000"                   # app
      - "9229:9229"                   # Node inspector for VS Code attach
    volumes:
      - ./src:/app/src                # source hot reload
      - node_modules:/app/node_modules  # keep container-built modules
    develop:                          # Compose Watch (Compose 2.22+): see topic 200
      watch:
        - action: rebuild             # rebuild image when dependencies change
          path: ./package.json
    depends_on:
      db: { condition: service_healthy }     # wait until DB accepts connections
      redis: { condition: service_started }  # redis starts fast
  db:
    image: postgres:16-alpine
    environment: { POSTGRES_USER: app, POSTGRES_PASSWORD: app, POSTGRES_DB: app }
    ports: ["127.0.0.1:5432:5432"]    # GUI access, localhost only
    volumes:
      - pgdata:/var/lib/postgresql/data           # keep data between runs
      - ./db/seed.sql:/docker-entrypoint-initdb.d/seed.sql:ro  # runs ONLY on first init of empty volume
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app"]
      interval: 5s
      timeout: 3s
      retries: 10
  redis:
    image: redis:7-alpine             # cache
  mailpit:
    image: axllent/mailpit:latest     # fake mail server; pin a version in real use
    ports: ["127.0.0.1:8025:8025"]    # web UI to see sent emails
volumes:
  pgdata: {}
  node_modules: {}
```
Run: `docker compose up --build` then `docker compose logs -f api`.

---

## 🟠 My Stack Integration
- **Node.js:** VS Code `launch.json` attach config to port 9229 with `remoteRoot: /app`.
- **FastAPI:** `uvicorn --reload` plus `debugpy` on 5678; mount `./app`.
- **React:** run Vite dev server in a `web` service on port 5173 with `CHOKIDAR_USEPOLLING=true` if file events do not propagate on Mac/Windows.
- **Nginx:** usually skipped in dev; the browser talks to Vite/API directly. Use Nginx only to reproduce routing problems.
- **Security:** dev passwords are fine but bind ports to `127.0.0.1`, so coworkers on the same Wi-Fi cannot reach your DB.

```yaml
# compose.override.yaml  (my React service in dev)
services:
  web:
    image: node:20-alpine             # example tag
    working_dir: /web                 # app folder
    command: ["npm", "run", "dev", "--", "--host"]  # Vite listens on 0.0.0.0
    volumes: ["./web:/web"]           # live reload
    ports: ["5173:5173"]              # open http://localhost:5173
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `localhost` as DB host inside the API container. That points to the container itself.
✅ Correct: Use the service name (`db`).

❌ Mistake 2: Bind mount hides `node_modules` built in the image, giving "module not found" or wrong-architecture binaries.
✅ Correct: Add a named volume for `/app/node_modules`.

❌ Mistake 3: Expecting `docker-entrypoint-initdb.d/seed.sql` to run every start. It runs only when the data directory is empty.
✅ Correct: `docker compose down -v` to re-seed, or run a seed script command.

❌ Mistake 4: Publishing DB ports on `0.0.0.0` on café Wi-Fi.
✅ Correct: Bind to `127.0.0.1`.

---

## 🧠 Tricky Interview Question
Hot reload works on Linux but not on your teammate's Mac. Same compose file. Why?

Answer: Docker Desktop on Mac runs containers in a VM, and file change events (inotify) from the host often do not reach the container through the file-sharing layer. Fix with polling (`CHOKIDAR_USEPOLLING`, nodemon `--legacy-watch`), or use Compose Watch (`develop.watch` with `sync`), which copies files in rather than relying on events.

---

## ⚫ Interview Questions + Answers

Q1: Why a multi-stage Dockerfile for dev and prod?
A1: One file, two targets: `dev` with dev tools and debugger, `runtime` slim and non-root. Compose picks one using `build.target`.

Q2: How do containers find each other?
A2: Compose creates a default network; service names are DNS names.

Q3: How do you wait for the DB?
A3: Healthcheck + `depends_on.condition: service_healthy`, and retry logic in the app.

Q4: How to debug a Node container from VS Code?
A4: Run with `--inspect=0.0.0.0:9229`, publish the port, and use an attach configuration.

Q5: How to reset the database?
A5: `docker compose down -v` removes volumes; next `up` re-runs init scripts.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Team onboarding and consistent versions.
- Running the full dependency graph locally.

❌ Avoid when:
- Heavy native GUI tooling that is better run on the host.
- Machines too small to run 6+ containers (use a remote dev environment).

---

## 📊 Visual Diagram
```
 Laptop
 +-----------------------------------------------+
 | VS Code --edit--> ./src ===bind mount===> api |--9229--> debugger
 | Browser ---------> localhost:3000 ----------> api
 | DBeaver ---------> 127.0.0.1:5432 ---------> db
 | Browser ---------> localhost:8025 ----------> mailpit
 |            default Compose network (DNS names)|
 +-----------------------------------------------+
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| hot reload | Restart/refresh on code change | code बदलने पर अपने-आप reload |
| bind mount | Host folder inside container | host folder का mount |
| build target | Stage chosen in a multi-stage build | multi-stage का चुना हुआ stage |
| inspector | Node debug protocol port | Node debug port |
| seed data | Sample data for dev | नमूना data |
| Compose Watch | Built-in file sync/rebuild | built-in file sync |

---

## ⚡ 3-Line Summary
English: Dev Compose gives one-command, identical environments with live reload and debuggers. Use a dev build target, bind mounts plus a node_modules volume, and localhost-only ports. Reset with `down -v`.
Hindi: Dev Compose एक command में एक जैसा environment, live reload और debugger देता है। Dev build target, bind mounts के साथ node_modules volume और सिर्फ localhost ports इस्तेमाल करें। Reset के लिए `down -v`।

---

## ➡️ Next Topic
**205. Compose for Testing**: the same trick makes disposable databases for automated tests in CI.
