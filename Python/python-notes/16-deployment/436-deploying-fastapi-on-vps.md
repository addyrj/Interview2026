---

# 436. Deploying FastAPI on VPS
# हिंदी में: VPS पर FastAPI Deploy करना

---

## 🔵 Simple Definition (English)
A VPS (Virtual Private Server) is a rented Linux machine (DigitalOcean, Hetzner, Linode, AWS Lightsail). Deploying FastAPI there means: create a safe user, copy the code, install dependencies in a virtualenv, run the app with a process manager (systemd) and put a reverse proxy (Nginx) in front.

## 🔵 सरल परिभाषा (Hindi)
VPS (Virtual Private Server) किराए की Linux machine है (DigitalOcean, Hetzner, Linode, AWS Lightsail)। FastAPI को वहाँ deploy करने का मतलब: एक सुरक्षित user बनाओ, code copy करो, virtualenv में dependencies install करो, app को process manager (systemd) से चलाओ और उसके आगे reverse proxy (Nginx) लगाओ।

---

## 🔴 Problem it Solves
`uvicorn main:app --reload` in a terminal dies when you close SSH, does not restart after a crash or reboot, runs as root, listens on a raw port with no HTTPS, and gives you no logs. A proper VPS deployment fixes all of that: the app survives reboots, restarts on failure, runs with least privilege and is reachable through your domain over HTTPS.

## 🔴 यह क्यों बना? (Hindi)
Terminal में `uvicorn main:app --reload` SSH बंद करते ही मर जाता है, crash या reboot के बाद restart नहीं होता, root से चलता है, बिना HTTPS के raw port पर सुनता है और logs नहीं देता। सही VPS deployment इन सबको ठीक करता है: app reboot में भी चलती है, fail होने पर restart होती है, कम से कम permission से चलती है और domain पर HTTPS से मिलती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create VPS (Ubuntu 24.04), add SSH key, disable password login + root login
Step 2 → Firewall: ufw allow OpenSSH, 80, 443; ufw enable (block everything else, incl. 8000)
Step 3 → Create non-root user "deploy"; clone repo to /srv/app
Step 4 → python3 -m venv .venv ; .venv/bin/pip install -r requirements.txt
Step 5 → Put secrets in /etc/orders-api.env (chmod 600), NOT in git
Step 6 → systemd unit runs gunicorn+uvicorn on 127.0.0.1:8000, restarts on failure
Step 7 → Nginx proxies domain:443 -> 127.0.0.1:8000; certbot adds free HTTPS
Step 8 → Smoke test /health + /version; keep previous release for rollback
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → VPS बनाओ (Ubuntu 24.04), SSH key जोड़ो, password login और root login बंद करो
Step 2 → Firewall: ufw allow OpenSSH, 80, 443; ufw enable (बाकी सब, 8000 भी, बंद)
Step 3 → non-root user "deploy" बनाओ; repo को /srv/app में clone करो
Step 4 → python3 -m venv .venv ; .venv/bin/pip install -r requirements.txt
Step 5 → Secrets /etc/orders-api.env में (chmod 600), git में नहीं
Step 6 → systemd unit gunicorn+uvicorn को 127.0.0.1:8000 पर चलाती है, fail पर restart
Step 7 → Nginx domain:443 को 127.0.0.1:8000 पर proxy करता है; certbot मुफ्त HTTPS देता है
Step 8 → /health + /version smoke test; rollback के लिए पिछला release रखो
```

---

## 🟡 Real World Example
A startup hosts its FastAPI backend on a 2 GB Hetzner/DigitalOcean droplet (about 500-1000 INR per month) instead of an expensive managed platform. A GitHub Actions job SSHes in, pulls the new commit, installs requirements, runs `systemctl restart orders-api`, then calls `/version` to confirm the new release is live, and rolls back if it is not.

## 🟡 Real Example Hindi mein
एक startup अपना FastAPI backend महंगे managed platform की जगह 2 GB Hetzner/DigitalOcean droplet (लगभग 500-1000 रुपये महीना) पर चलाता है। GitHub Actions job SSH करके नया commit pull करती है, requirements install करती है, `systemctl restart orders-api` चलाती है, फिर `/version` call करके देखती है कि नया release live है या नहीं, और नहीं हो तो rollback करती है।

---

## 💻 Code Example — Basic
```python
# Basic: the app you deploy to a VPS - config from env vars, /health, /version
import os                                         # read environment variables
from fastapi import FastAPI                       # web framework
from fastapi.testclient import TestClient         # local test client (no server needed)

APP_ENV: str = os.getenv("APP_ENV", "development")   # set to "production" in the systemd unit
VERSION: str = os.getenv("APP_VERSION", "0.1.0")     # deploy script can stamp a git sha here

app: FastAPI = FastAPI(
    title="orders-api",                           # shown in /docs
    docs_url=None if APP_ENV == "production" else "/docs",   # hide Swagger on the public internet
)


@app.get("/health")                               # Nginx / uptime monitor hits this
def health() -> dict[str, str]:
    return {"status": "ok"}                       # keep it dependency-free and fast


@app.get("/version")                              # tells you WHICH release is live
def version() -> dict[str, str]:
    return {"version": VERSION, "env": APP_ENV}   # handy after every deploy


client = TestClient(app)                          # simulate the VPS requests locally
print(client.get("/health").json())               # {'status': 'ok'}
print(client.get("/version").json())              # version + env
print(client.get("/docs").status_code)            # 200 in dev (would be 404 in production)

# Output (real run, Python 3.13):
# {'status': 'ok'}
# {'version': '0.1.0', 'env': 'development'}
# 200
```

The server side files (shown here, **not run**: no VPS or systemd in this environment; I checked only that the unit parses as INI-style text):

```ini
# /etc/systemd/system/orders-api.service
[Unit]
Description=Orders API (FastAPI)
After=network.target

[Service]
User=deploy
Group=deploy
WorkingDirectory=/srv/app
EnvironmentFile=/etc/orders-api.env
ExecStart=/srv/app/.venv/bin/gunicorn main:app -k uvicorn.workers.UvicornWorker -w 2 -b 127.0.0.1:8000
Restart=on-failure
RestartSec=3
KillSignal=SIGTERM
TimeoutStopSec=30

[Install]
WantedBy=multi-user.target
```

```bash
# one-time server setup (run as root or with sudo) - not run here
ufw allow OpenSSH && ufw allow 80 && ufw allow 443 && ufw --force enable
adduser --disabled-password --gecos "" deploy
systemctl daemon-reload && systemctl enable --now orders-api
journalctl -u orders-api -f          # live logs
```

## 💻 Code Example — Advanced
```python
# Advanced: post-deploy smoke test with retries - run this in your deploy script / CI
import time                                       # sleep between retries
from dataclasses import dataclass                 # result object

import httpx                                      # HTTP client
from fastapi import FastAPI                       # demo app
from fastapi.testclient import TestClient         # demo client


@dataclass
class SmokeResult:
    ok: bool                                      # did all checks pass
    attempts: int                                 # how many tries were needed
    detail: str                                   # last message


def smoke_test(client: httpx.Client, expected_version: str,
               retries: int = 5, delay: float = 0.0) -> SmokeResult:
    """Wait for the new release to answer /health and report the expected version."""
    detail = "not started"                        # default message
    for attempt in range(1, retries + 1):         # service may need seconds to boot
        try:
            r = client.get("/health", timeout=3)  # never wait forever
            if r.status_code == 200:              # process is up
                v = client.get("/version", timeout=3).json()["version"]
                if v == expected_version:         # correct release is live
                    return SmokeResult(True, attempt, "healthy")
                detail = f"old version {v} still serving"
            else:
                detail = f"health returned {r.status_code}"
        except httpx.HTTPError as exc:            # connection refused while restarting
            detail = f"{type(exc).__name__}"
        time.sleep(delay)                         # back off before the next try
    return SmokeResult(False, retries, detail)    # tell the deploy script to roll back


# ---- demo: first 2 calls fail (service restarting), then the new version answers ----
calls = {"n": 0}
app = FastAPI()


@app.get("/health")
def health() -> dict[str, str]:
    calls["n"] += 1
    if calls["n"] <= 2:                           # simulate "502 while restarting"
        from fastapi import HTTPException
        raise HTTPException(status_code=502)
    return {"status": "ok"}


@app.get("/version")
def version() -> dict[str, str]:
    return {"version": "1.4.0"}


c = TestClient(app)
print(smoke_test(c, "1.4.0"))                     # succeeds on attempt 3
print(smoke_test(c, "9.9.9", retries=2))          # wrong version -> fails -> rollback

# Output (real run, Python 3.13):
# SmokeResult(ok=True, attempts=3, detail='healthy')
# SmokeResult(ok=False, attempts=2, detail='old version 1.4.0 still serving')
```

Use it in `deploy.sh`: if the smoke test exits non-zero, run `git checkout <previous-sha> && systemctl restart orders-api`. The first call succeeds on attempt 3 because the first two `/health` calls return 502 (the "service is still restarting" window). In a real run set `delay=2.0` so you wait between tries. httpx may print a `DeprecationWarning` on stderr for the test client; it does not change the output.

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python / FastAPI | Node.js / Express |
|---------|-----------------|-------------------|
| Isolated deps | `venv` + `requirements.txt` | `node_modules` + `package.json` |
| Process manager | systemd / supervisor / gunicorn | systemd / PM2 |
| Server | uvicorn (ASGI) behind gunicorn | node itself (single process) + PM2 cluster |
| Reverse proxy | Nginx | Nginx |
| Restart on deploy | `systemctl restart` | `pm2 reload` |

```python
# Python way — dependencies live in an isolated environment
# python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
# .venv/bin/gunicorn main:app -k uvicorn.workers.UvicornWorker
```
```javascript
// JavaScript way — PM2 keeps Node alive
// npm ci --omit=dev && pm2 start server.js -i max && pm2 save
```

Key difference: Python's GIL means one process uses one CPU core for Python code, so you run several worker processes (gunicorn `-w`). Node.js also needs a cluster/PM2 for multi-core, but its event loop is the default worker model.

---

## 🟠 FastAPI Connection
FastAPI reads everything environment-specific from env vars, so the same code runs on your laptop and the VPS. The `/health` endpoint is for Nginx/uptime monitors; `/version` proves which release is serving. In production disable `/docs` (as `docs_url=None` above) or put it behind auth.

```python
# FastAPI example — typed settings from env, cached once
from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_env: str = "development"          # set APP_ENV=production in /etc/orders-api.env
    database_url: str = "sqlite:///./dev.db"

@lru_cache                                 # build once per process
def get_settings() -> Settings:
    return Settings()

print(get_settings().app_env)              # development (unless the env var is set)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Running with `--reload` and as root, exposing port 8000 publicly
✅ Correct: bind to `127.0.0.1`, let Nginx face the internet, run as `deploy`

```bash
# Wrong
uvicorn main:app --reload --host 0.0.0.0 --port 8000     # as root
# Right
gunicorn main:app -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000   # as deploy via systemd
```

❌ Mistake 2: Committing `.env` / secrets, or hardcoding the DB password
✅ Correct: secrets in `/etc/orders-api.env` with `chmod 600`, loaded by systemd `EnvironmentFile`

```python
# Wrong
DATABASE_URL = "postgresql://admin:Pa55w0rd@localhost/db"
# Right
import os
DATABASE_URL = os.environ["DATABASE_URL"]      # KeyError at boot if missing = fail fast
```

❌ Mistake 3: Forgetting the firewall and automatic restarts
✅ Correct: `ufw` with only 22/80/443, `Restart=on-failure` in the unit

```bash
# Wrong: process dies at 3 AM and stays dead; port 5432 open to the world
# Right: systemctl enable --now orders-api ; ufw deny 5432
```

---

## 🧠 Tricky Interview Question

```python
# What will this output? (APP_ENV is NOT set in the environment)
import os
env = os.getenv("APP_ENV", "dev")
debug = os.getenv("DEBUG", False)
print(env, debug, bool(os.getenv("DEBUG", "False")))
# Now imagine DEBUG=False is set in the systemd EnvironmentFile
```
Answer: With nothing set it prints `dev False True`. The third value is `True` even though the default text says "False": `os.getenv` returns the **string** `"False"`, and `bool("False")` is `True` because any non-empty string is truthy. The same happens if `DEBUG=False` is written in the systemd EnvironmentFile, so debug mode turns ON in production. Always parse booleans explicitly (`value.lower() in {"1","true","yes"}`) or let Pydantic Settings do it, since Pydantic converts `"False"` to the real `False`.

---

## ⚫ Interview Questions + Answers

Q1: Why not run uvicorn directly on port 80/443?
A1: Needs root for ports below 1024, has no TLS management, no buffering of slow clients, no static file serving, no rate limit. Nginx handles those and forwards to uvicorn on localhost. Also you can restart the app without dropping the public port.

Q2: How do you make the app survive reboots and crashes?
A2: Run it as a systemd service with `Restart=on-failure` and `systemctl enable`. systemd starts it at boot and restarts it after a crash; `journalctl -u` gives the logs.

Q3: How many workers?
A3: Start with `2 x CPU cores + 1` for sync-heavy apps; for async FastAPI, `CPU cores` is often enough because each worker handles many concurrent requests. Measure with a load test; memory (each worker loads the whole app) is usually the limit on a small VPS.

Q4: How do you deploy with zero or low downtime?
A4: `gunicorn` reloads workers gracefully on `SIGHUP` (`systemctl reload`). For true zero downtime, run two app instances behind Nginx and restart one at a time, or use blue/green with a symlink switch.

Q5: How do you secure a fresh VPS?
A5: SSH keys only, no root login, `ufw`/security group with 22/80/443, `fail2ban`, automatic security updates (`unattended-upgrades`), non-root app user, secrets outside git, and database port not exposed.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You want full control and low cost for a steady workload
- A small or medium app with one or a few servers
- You need to learn how production really works

❌ Avoid when:
- You need auto-scaling for spiky traffic (use containers/Lambda)
- The team has no one to patch and monitor servers
- You need multi-region high availability on day one

---

## 📊 Visual Diagram
```
 Browser --HTTPS--> [ Cloud firewall: 22,80,443 ]
                          |
                       [ Nginx :443 ]  (TLS, gzip, static)
                          |  proxy_pass
                          v
              [ gunicorn master 127.0.0.1:8000 ]   <-- systemd keeps it alive
                 |         |
          [uvicorn w1] [uvicorn w2]  -> FastAPI app -> PostgreSQL (private)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| VPS | Rented virtual Linux server | किराए का virtual server |
| systemd | Linux service manager | Linux का service manager |
| Reverse proxy | Server in front of your app | app के आगे का server |
| ufw | Simple Linux firewall | आसान Linux firewall |
| venv | Isolated Python environment | अलग Python environment |
| journalctl | Reads systemd logs | systemd logs पढ़ता है |
| Rollback | Return to the previous release | पिछले release पर वापसी |

---

## ⚡ 3-Line Summary
English: Run FastAPI under systemd (gunicorn + uvicorn) as a non-root user on localhost. Put Nginx and a firewall in front and keep secrets in an env file. Smoke-test every release and keep a rollback path.
Hindi: FastAPI को systemd (gunicorn + uvicorn) से non-root user के रूप में localhost पर चलाओ। आगे Nginx और firewall लगाओ और secrets env file में रखो। हर release का smoke test करो और rollback का रास्ता रखो।

---

## ➡️ Next Topic
**437. Gunicorn + Uvicorn** (already covered) then **438. Nginx + FastAPI Setup** — the reverse proxy in front of the app, in detail.
