# 193. restart Policy
# हिंदी में: Compose में restart Policy (container अपने-आप दोबारा चालू होना)

---

## 🔵 Simple Definition (English)
The `restart` key in a Compose service tells Docker what to do when a container stops: never restart it, always restart it, restart only on failure, or restart unless you stopped it by hand. It is the simplest self-healing tool for a single server.

## 🔵 सरल परिभाषा (Hindi)
Compose service में `restart` key Docker को बताती है कि container बंद होने पर क्या करना है: कभी restart नहीं, हमेशा restart, सिर्फ failure पर restart, या तब तक restart जब तक आपने खुद हाथ से stop न किया हो। Single server पर यह सबसे आसान self-healing तरीका है।

---

## 🔴 Problem it Solves
Without a restart policy, a Node.js process that crashes at 3 AM (out-of-memory, an unhandled promise rejection) stays dead until someone logs in to the VPS. A server reboot after a kernel update also leaves every container stopped. The app is down for hours and nobody knows.

## 🔴 यह क्यों बना? (Hindi)
Restart policy के बिना अगर रात 3 बजे Node.js process crash हो जाए (out-of-memory, unhandled promise rejection), तो वह तब तक बंद रहता है जब तक कोई VPS में login न करे। Kernel update के बाद server reboot हो तो भी सारे containers बंद रह जाते हैं। App घंटों down रहता है और किसी को पता नहीं चलता।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You add `restart: unless-stopped` to a service in docker-compose.yml
Step 2 → `docker compose up -d` creates the container with that policy stored in its config
Step 3 → The main process (PID 1) exits (crash, OOM kill, or normal exit)
Step 4 → The Docker daemon checks the policy and the exit code
Step 5 → If the policy allows, the daemon waits (delay doubles: 100ms, 200ms, 400ms ... up to 1 minute) and starts it again
Step 6 → After a host reboot, the daemon starts and revives containers whose policy says so
Step 7 → `docker stop` / `docker compose stop` by the user prevents restart for `unless-stopped`
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → आप service में `restart: unless-stopped` लिखते हैं
Step 2 → `docker compose up -d` container बनाता है और policy उसके config में save हो जाती है
Step 3 → Main process (PID 1) exit होता है (crash, OOM kill, या normal exit)
Step 4 → Docker daemon policy और exit code देखता है
Step 5 → Policy allow करे तो daemon थोड़ा रुकता है (delay दोगुना होता है: 100ms, 200ms, 400ms ... max 1 मिनट) और फिर start करता है
Step 6 → Host reboot के बाद daemon चालू होकर उन containers को वापस उठाता है जिनकी policy यही कहती है
Step 7 → User के `docker stop` करने पर `unless-stopped` वाला container दोबारा नहीं उठता
```

---

## 🟡 Real World Example
A Swiggy-style order API runs on one EC2 instance. A memory leak makes the Node.js process get OOM-killed once a day. With `restart: unless-stopped` the API is back in about a second, and users only see one failed request instead of a long outage. The real fix (the leak) is still needed, but the policy buys time. On the user's own VPS, after `apt upgrade` and a reboot, all containers (api, redis, postgres) come back with no manual step.

## 🟡 Real Example Hindi mein
Swiggy जैसी order API एक EC2 instance पर चल रही है। Memory leak की वजह से Node.js process दिन में एक बार OOM-kill हो जाता है। `restart: unless-stopped` होने से API करीब एक second में वापस आ जाती है, users को सिर्फ एक failed request दिखती है, लंबा outage नहीं। असली fix (leak ठीक करना) फिर भी चाहिए, पर policy समय देती है। आपके अपने VPS पर `apt upgrade` और reboot के बाद सारे containers (api, redis, postgres) बिना किसी manual step के वापस आ जाते हैं।

---

## 💻 Code / Config Example — Basic
```yaml
# docker-compose.yml  (Basic: restart on crash and after reboot)
services:                          # all containers of the app live under this key
  api:                             # service name, also its DNS name inside the network
    image: node:20-alpine          # example image tag, update to your pinned version
    working_dir: /app              # run commands from /app inside the container
    volumes:
      - ./:/app                    # mount source code (development style, simple demo)
    command: ["node", "server.js"] # start the Node.js server as PID 1
    ports:
      - "3000:3000"                # host 3000 -> container 3000
    restart: unless-stopped        # restart on crash/reboot, but not if I ran `docker stop`
```

## 💻 Code / Config Example — Advanced
```yaml
# docker-compose.yml  (Advanced: different policies per service + healthcheck)
services:
  postgres:
    image: postgres:16-alpine            # example tag, pin and update
    restart: always                      # always revive the DB, even after `docker stop` + daemon restart
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_pass   # read password from a secret file, not plain env
    secrets:
      - db_pass                          # attach the secret declared at the bottom
    volumes:
      - pgdata:/var/lib/postgresql/data  # named volume keeps data across restarts
    healthcheck:                         # lets us know when DB is truly ready
      test: ["CMD-SHELL", "pg_isready -U postgres"]  # returns 0 when ready
      interval: 10s                      # check every 10 seconds
      timeout: 3s                        # a check fails if it takes more than 3s
      retries: 5                         # unhealthy after 5 failures

  api:
    build: ./api                         # build from ./api/Dockerfile
    restart: on-failure:5                # restart only on non-zero exit, max 5 tries (stop crash loops)
    depends_on:
      postgres:
        condition: service_healthy       # start api only after DB is healthy
    ports:
      - "127.0.0.1:3000:3000"            # bind to localhost only, Nginx on host proxies to it

  migrate:                               # one-off job: run migrations then exit
    build: ./api
    command: ["node", "migrate.js"]      # exits with 0 when done
    restart: "no"                        # MUST be quoted: unquoted `no` becomes boolean false in YAML 1.1
    depends_on:
      postgres:
        condition: service_healthy

secrets:
  db_pass:
    file: ./secrets/db_pass.txt          # file on host, never commit it to git

volumes:
  pgdata: {}                             # named volume managed by Docker
```

---

## 🟠 My Stack Integration
- **Node.js API:** `unless-stopped` for the long-running server; Node exits on fatal errors, Docker revives it.
- **FastAPI (uvicorn):** same policy. If you use `--workers`, uvicorn restarts workers itself, Docker only restarts when PID 1 dies.
- **Nginx:** `unless-stopped`, so the reverse proxy returns after VPS reboot. Enable the Docker service at boot: `sudo systemctl enable docker`.
- **React build job:** `restart: "no"`, because it builds static files and exits.
- **AWS/VPS:** Docker policy handles process crashes; use CloudWatch or an uptime monitor to alert when restarts happen too often.

```yaml
# docker-compose.yml  (my stack: nginx + api + fastapi)
services:
  nginx:
    image: nginx:1.27-alpine        # example tag
    restart: unless-stopped         # edge proxy must always come back
    ports:
      - "80:80"                     # public HTTP
      - "443:443"                   # public HTTPS
    depends_on:
      - api                         # start order only, not readiness
  api:
    build: ./api                    # Node.js service
    restart: unless-stopped         # survive crashes and reboots
  ml:
    build: ./fastapi                # FastAPI service
    restart: on-failure:5           # limit loops if a model file is missing
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Writing `restart: no` unquoted. YAML 1.1 parsers read `no` as boolean `false`, and Compose may reject or mis-handle it.
✅ Correct: `restart: "no"` with quotes.

❌ Mistake 2: Using `restart: always` for a crashing app and thinking it is fixed. A bad config creates an endless crash loop that hides the real bug and burns CPU.
✅ Correct: Use `on-failure:5`, read `docker compose logs`, and fix the root cause.

❌ Mistake 3: Expecting `restart` to wait for the database. It only restarts the container; it does not order startup.
✅ Correct: Use `healthcheck` + `depends_on.condition: service_healthy`, and retry connections in app code.

❌ Mistake 4: Using the `deploy.restart_policy` block and expecting it in plain `docker compose up`. Newer Compose versions read some `deploy` keys, but `restart` is the portable, simple choice. (Version-dependent: check your Compose version.)
✅ Correct: Use top-level service `restart` for single-host setups.

---

## 🧠 Tricky Interview Question
You set `restart: always` and run `docker stop api`. After the VPS reboots, is `api` running or not? What about with `unless-stopped`?

Answer: With `always`, the container is started again when the Docker daemon starts, even though you stopped it manually earlier (a manual stop is ignored after a daemon restart). With `unless-stopped`, Docker remembers you stopped it and keeps it stopped after the reboot. This is why `unless-stopped` is the usual production choice: it respects an operator's intent.

---

## ⚫ Interview Questions + Answers

Q1: What are the four restart policy values?
A1: `"no"` (default, never restart), `always`, `on-failure[:max-retries]` (only non-zero exit codes), and `unless-stopped`.

Q2: Does `on-failure` restart a container that exited with code 0?
A2: No. Exit code 0 means success, so nothing is restarted. It restarts only on non-zero codes (and also when OOM-killed).

Q3: How does Docker avoid hammering the CPU with instant restarts?
A3: It uses an exponential back-off delay, starting at 100 ms and doubling up to a maximum of 1 minute. The delay resets if the container runs successfully for at least 10 seconds.

Q4: Does `restart` replace Kubernetes or a process manager like PM2?
A4: For one host it often replaces PM2 (Docker is the supervisor). For multi-node scaling, health-based rescheduling, and rolling updates you need an orchestrator.

Q5: Why does a container in a restart loop show status `Restarting`?
A5: Because it keeps exiting and the daemon keeps trying. Check `docker inspect --format '{{.RestartCount}}' <c>` and `docker logs` to find the crash reason.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Long-running services (API, Nginx, Redis, Postgres) on a single VPS or EC2.
- You want automatic recovery after reboots and crashes.
- You pair it with a healthcheck and alerting.

❌ Avoid when:
- One-off jobs (migrations, seed scripts, build steps): use `"no"`.
- You are debugging a crash and want the container to stay dead so you can read logs.
- You need smart health-based rescheduling across nodes (use an orchestrator).

---

## 📊 Visual Diagram
```
            +-----------------------+
            |   Docker daemon       |
            +-----------+-----------+
                        | watches PID 1
                        v
   +-----------+  exit  +-------------------+
   | container | -----> | check policy+code |
   +-----------+        +---------+---------+
        ^                         |
        |   wait 100ms,200ms..1m  | allowed?
        +-------------------------+--> yes: start again
                                  +--> no : stay stopped
 Host reboot -> daemon starts -> always / unless-stopped containers revive
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| restart policy | Rule for restarting a stopped container | container दोबारा चालू करने का नियम |
| always | Restart on any exit, also at daemon start | हर exit पर restart |
| unless-stopped | Like always, but respects manual stop | manual stop को मानता है |
| on-failure | Restart only on non-zero exit | सिर्फ failure पर restart |
| crash loop | Container keeps crashing and restarting | बार-बार crash होना |
| back-off | Growing delay between restarts | restart के बीच बढ़ता delay |

---

## ⚡ 3-Line Summary
English: `restart` is Docker's built-in self-healing for one host. Use `unless-stopped` for services, `on-failure:N` for risky ones, and `"no"` for jobs. It restarts containers; it does not fix the bug or order startup.
Hindi: `restart` एक host के लिए Docker का built-in self-healing है। Services के लिए `unless-stopped`, risky ones के लिए `on-failure:N`, और jobs के लिए `"no"` रखें। यह container को दोबारा उठाता है, bug ठीक नहीं करता और startup order नहीं बनाता।

---

## ➡️ Next Topic
**194. deploy (resource limits)**: a restarted container can still eat all RAM and kill the VPS, so next we cap CPU and memory per service.
