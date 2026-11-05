# 74. CMD vs ENTRYPOINT
# हिंदी में: CMD बनाम ENTRYPOINT (Container start पर क्या चलेगा)

---

## 🔵 Simple Definition (English)
Both `CMD` and `ENTRYPOINT` define what runs when a container starts. `ENTRYPOINT` is the fixed executable of the container; `CMD` provides default arguments (or a default command) that are easy to override with `docker run IMAGE <args>`. Together: `ENTRYPOINT ["node"]` + `CMD ["server.js"]`.

## 🔵 सरल परिभाषा (Hindi)
`CMD` और `ENTRYPOINT` दोनों तय करते हैं कि container start होने पर क्या चलेगा। `ENTRYPOINT` container का fixed executable है; `CMD` default arguments (या default command) देता है जिन्हें `docker run IMAGE <args>` से आसानी से बदला जा सकता है। साथ में: `ENTRYPOINT ["node"]` + `CMD ["server.js"]`।

---

## 🔴 Problem it Solves
An image needs a default behaviour at start, but users also need flexibility: sometimes run a shell for debugging, sometimes run a migration, sometimes pass flags. `CMD` gives an overridable default; `ENTRYPOINT` makes the image behave like a command-line tool or runs a setup script before the main process. Getting the form wrong also breaks signal handling (graceful shutdown).

## 🔴 यह क्यों बना? (Hindi)
Image को start पर default behaviour चाहिए, पर users को flexibility भी: कभी debugging के लिए shell, कभी migration, कभी flags। `CMD` overridable default देता है; `ENTRYPOINT` image को command-line tool की तरह चलाता है या मुख्य process से पहले setup script चलाता है। Form गलत हो तो signal handling (graceful shutdown) भी टूटता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Dockerfile stores ENTRYPOINT and CMD as image metadata (not run at build)
Step 2 → docker run IMAGE            -> runs ENTRYPOINT + CMD together
Step 3 → docker run IMAGE extra args -> args REPLACE CMD, ENTRYPOINT stays
Step 4 → docker run --entrypoint sh IMAGE -> replaces ENTRYPOINT explicitly
Step 5 → Exec form ["a","b"] runs the process as PID 1 and receives SIGTERM
Step 6 → Shell form "a b" runs /bin/sh -c "a b": shell is PID 1 and may swallow signals
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Dockerfile ENTRYPOINT और CMD को image metadata में रखती है (build में नहीं चलते)
Step 2 → docker run IMAGE            -> ENTRYPOINT + CMD साथ चलते हैं
Step 3 → docker run IMAGE extra args -> args CMD को REPLACE करते हैं, ENTRYPOINT वही रहता है
Step 4 → docker run --entrypoint sh IMAGE -> ENTRYPOINT को साफ़ बदलता है
Step 5 → Exec form ["a","b"] process को PID 1 बनाता है और SIGTERM पाता है
Step 6 → Shell form "a b" /bin/sh -c "a b" चलाता है: shell PID 1 बनता है और signals निगल सकता है
```

---

## 🟡 Real World Example
Your FastAPI image uses `ENTRYPOINT ["./entrypoint.sh"]` which waits for Postgres, runs `alembic upgrade head`, then does `exec "$@"`. The `CMD ["uvicorn","app.main:app","--host","0.0.0.0"]` is the default server. For a one-off task, ops run `docker run api python scripts/backfill.py`, so CMD is replaced but the wait-for-DB step still runs. Without `exec`, uvicorn would not get SIGTERM on `docker stop` and would be killed after 10 seconds.

## 🟡 Real Example Hindi mein
आपकी FastAPI image में `ENTRYPOINT ["./entrypoint.sh"]` है जो Postgres का इंतज़ार करता है, `alembic upgrade head` चलाता है, फिर `exec "$@"` करता है। `CMD ["uvicorn","app.main:app","--host","0.0.0.0"]` default server है। एक बार के task के लिए ops `docker run api python scripts/backfill.py` चलाते हैं: CMD बदल जाता है पर DB-wait step फिर भी चलता है। `exec` के बिना uvicorn को `docker stop` पर SIGTERM नहीं मिलता और 10 seconds बाद kill हो जाता है।

---

## 💻 Code / Config Example — Basic
```dockerfile
# Dockerfile -- CMD only: simple overridable default
# base image (example tag)
FROM node:20-alpine
# app directory
WORKDIR /app
# copy source
COPY . .
# exec form: default command; `docker run img sh` replaces it
CMD ["node", "server.js"]
```
```dockerfile
# Dockerfile -- ENTRYPOINT + CMD: image acts like a tool with default args
# tiny base (example tag)
FROM alpine:3.20
# install curl at build time
RUN apk add --no-cache curl
# fixed executable with silent-but-show-errors flags
ENTRYPOINT ["curl", "-sS"]
# default arg; `docker run img https://example.com` replaces it
CMD ["--help"]
```

## 💻 Code / Config Example — Advanced
```dockerfile
# Dockerfile -- production FastAPI: entrypoint script + default server command
# base image (example tag)
FROM python:3.12-slim
# app dir
WORKDIR /app
# deps manifest
COPY requirements.txt .
# install deps
RUN pip install --no-cache-dir -r requirements.txt
# app source
COPY . .
# script must be executable
RUN chmod +x /app/entrypoint.sh
# always runs first; exec form
ENTRYPOINT ["/app/entrypoint.sh"]
# default process, overridable
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```
```bash
#!/bin/sh
# entrypoint.sh -- prepare environment, then hand over PID 1 to the real command
set -e                                          # stop on any error
echo "waiting for database..."                  # log progress for docker logs
until python -c "import socket,os;socket.create_connection((os.environ.get('DB_HOST','db'),5432),2)"; do   # try TCP connect
  sleep 1                                       # retry every second
done                                            # DB is reachable now
alembic upgrade head                            # apply migrations (assumes alembic configured)
exec "$@"                                       # replace shell with CMD so it gets SIGTERM
```
`bash -n`/`sh -n` syntax check passed on the script; behaviour not run here (no DB/daemon). Make sure the script is checked into Git with LF line endings.

---

## 🟠 My Stack Integration
Compose can override either one per service without rebuilding; useful for worker/web split from one image.

```yaml
# docker-compose.yml -- same image, different CMD; entrypoint stays
services:                                       # services
  api:                                          # web process
    image: ghcr.io/addyrj/api:9fceb02           # example pinned image
    # uses Dockerfile ENTRYPOINT + CMD (uvicorn)
  worker:                                       # background worker from same image
    image: ghcr.io/addyrj/api:9fceb02           # same image
    command: ["celery", "-A", "app.worker", "worker", "-l", "info"]   # replaces CMD only
  debug:                                        # ad-hoc debug shell
    image: ghcr.io/addyrj/api:9fceb02           # same image
    entrypoint: ["/bin/sh"]                     # replaces ENTRYPOINT
    profiles: ["debug"]                         # only starts with --profile debug
```
`command:` in Compose overrides CMD; `entrypoint:` overrides ENTRYPOINT (and also resets CMD). Compose file parsed as YAML only.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Shell form `CMD npm start`, so `docker stop` waits 10 s then kills the app (no graceful shutdown).
✅ Correct: Exec form `CMD ["node","server.js"]`, or `exec` in scripts. Add `tini`/`--init` if the app does not reap children.

❌ Mistake 2: Entry script ends with `uvicorn ...` instead of `exec "$@"`.
✅ Correct: Use `exec "$@"` so the app becomes PID 1.

❌ Mistake 3: Multiple `CMD` lines expecting all to run.
✅ Correct: Only the last `CMD` (and last `ENTRYPOINT`) counts; chain in a script.

❌ Mistake 4: Single quotes in JSON form `['node','x.js']`.
✅ Correct: JSON needs double quotes, else Docker treats it as shell form.

---

## 🧠 Tricky Interview Question
Dockerfile has `ENTRYPOINT ["echo","hello"]` and `CMD ["world"]`. What does `docker run img there` print, and what does `docker run img` print?

Answer: `hello there` and `hello world`. Run arguments replace only CMD. If you wrote ENTRYPOINT in shell form (`ENTRYPOINT echo hello`), CMD and run args would be ignored (they are not passed to the shell command).

---

## ⚫ Interview Questions + Answers

Q1: What happens if both are present?
A1: Docker concatenates ENTRYPOINT then CMD (exec forms): CMD acts as default arguments to ENTRYPOINT.

Q2: How do you override each at runtime?
A2: CMD: append args after image name. ENTRYPOINT: `--entrypoint` flag (or Compose `entrypoint:`).

Q3: Why is exec form preferred?
A3: The app is PID 1 and receives signals directly for graceful shutdown; no extra shell, no shell-injection via variable expansion.

Q4: Is there a default if neither is set?
A4: The base image's values are inherited; with none, the container exits immediately (nothing to run).

Q5: What is the PID 1 problem?
A5: PID 1 ignores default signal handlers and must reap zombie processes. Use exec form, `docker run --init`, or `tini`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- CMD: default server command that ops may override.
- ENTRYPOINT: wrapper scripts (wait-for-db, migrations) or tool-like images.
- Both: fixed binary plus default args.

❌ Avoid when:
- Using ENTRYPOINT for something people must replace often (annoying; use CMD).
- Using shell form in production.
- Putting long-running migrations in ENTRYPOINT on multi-replica deployments (race conditions).

---

## 📊 Visual Diagram
```
 Dockerfile:  ENTRYPOINT ["python","app.py"]    CMD ["--port","8000"]

 docker run img                  -> python app.py --port 8000
 docker run img --port 9000      -> python app.py --port 9000   (CMD replaced)
 docker run --entrypoint sh img  -> sh                          (ENTRYPOINT replaced; image CMD is cleared too)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ENTRYPOINT | Fixed start executable | Start पर fixed executable |
| CMD | Default command/args | Default command/arguments |
| Exec form | JSON array form | JSON array form |
| Shell form | String run via sh -c | String form (sh -c) |
| PID 1 | First process in container | Container की पहली process |
| SIGTERM | Graceful stop signal | शांतिपूर्वक रुकने का signal |

---

## ⚡ 3-Line Summary
English: ENTRYPOINT is the fixed executable, CMD is the overridable default argument set. Use exec form so signals reach your app. Use entrypoint scripts ending with `exec "$@"`.
Hindi: ENTRYPOINT fixed executable है, CMD बदलने योग्य default arguments। Exec form इस्तेमाल करो ताकि signals app तक पहुँचें। Entrypoint scripts का अंत `exec "$@"` से करो।

---

## ➡️ Next Topic
**75. CMD vs ENTRYPOINT — Difference** — अब दोनों की तुलना table, override rules और combination matrix के साथ interview-ready तरीके से।
