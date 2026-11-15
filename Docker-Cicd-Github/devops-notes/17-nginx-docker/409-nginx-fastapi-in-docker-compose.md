# 409. Nginx + FastAPI in Docker Compose
# हिंदी में: Docker Compose में Nginx + FastAPI

---

## 🔵 Simple Definition (English)
FastAPI is an ASGI app served by **uvicorn** (or gunicorn with uvicorn workers). In production you put **Nginx** in front of it: Nginx handles public traffic, TLS, buffering of slow clients, static files and limits; uvicorn handles only Python application logic on a private port (8000).

## 🔵 सरल परिभाषा (Hindi)
FastAPI एक ASGI app है जिसे **uvicorn** (या uvicorn workers के साथ gunicorn) चलाता है। Production में उसके आगे **Nginx** लगाते हैं: Nginx public traffic, TLS, slow clients की buffering, static files और limits संभालता है; uvicorn सिर्फ Python application logic private port (8000) पर चलाता है।

---

## 🔴 Problem it Solves
- uvicorn alone is not hardened for the open internet (slow-loris, huge uploads, no TLS).
- No place for rate limiting, caching, gzip or security headers.
- Docs pages (`/docs`, `/openapi.json`) are exposed publicly by default.
- Redirects and generated URLs use `http://` and the internal host name behind a proxy.

## 🔴 यह क्यों बना? (Hindi)
- अकेला uvicorn खुले internet के लिए hardened नहीं (slow-loris, बड़े uploads, TLS नहीं)।
- Rate limiting, caching, gzip, security headers के लिए जगह नहीं।
- Docs pages (`/docs`, `/openapi.json`) default रूप से public होते हैं।
- Proxy के पीछे redirects और बने URLs `http://` और internal host नाम इस्तेमाल करते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Dockerfile: python:3.12-slim, install requirements, non-root user
Step 2 → CMD runs uvicorn main:app --host 0.0.0.0 --port 8000
Step 3 → Compose: service "ml" on private network, healthcheck /health
Step 4 → Nginx location /ml/ (or a dedicated subdomain) proxy_pass to ml:8000
Step 5 → uvicorn --proxy-headers reads X-Forwarded-Proto/For from Nginx
Step 6 → Optional: gunicorn -k uvicorn.workers.UvicornWorker for multi-process
Step 7 → Block or protect /docs in production at the Nginx layer
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Dockerfile: python:3.12-slim, requirements install, non-root user
Step 2 → CMD uvicorn main:app --host 0.0.0.0 --port 8000 चलाता है
Step 3 → Compose: private network पर service "ml", healthcheck /health
Step 4 → Nginx location /ml/ (या अलग subdomain) ml:8000 पर proxy_pass करता है
Step 5 → uvicorn --proxy-headers Nginx के X-Forwarded-Proto/For पढ़ता है
Step 6 → Optional: multi-process के लिए gunicorn -k uvicorn.workers.UvicornWorker
Step 7 → Production में /docs को Nginx layer पर block या protect करो
```

---

## 🟡 Real World Example
An ed-tech platform exposes a FastAPI service that scores student answers using an ML model. The model takes 1-3 seconds, so Nginx sets a 120 s read timeout for `/ml/`, limits uploads to 5 MB, and restricts `/docs` to the office VPN IP. The Node.js backend calls FastAPI over the internal network without going through the internet at all.

## 🟡 Real Example Hindi mein
एक ed-tech platform ML model से student answers score करने वाली FastAPI service चलाता है। Model 1-3 sec लेता है, इसलिए Nginx `/ml/` के लिए 120 sec read timeout रखता है, uploads 5 MB तक सीमित करता है, और `/docs` सिर्फ office VPN IP को देता है। Node.js backend FastAPI को internal network से बुलाता है, internet से नहीं।

---

## 💻 Code / Config Example — Basic

```python
# fastapi/main.py -- minimal FastAPI app
from fastapi import FastAPI, Request          # framework + request type

app = FastAPI()                               # create the ASGI application

@app.get("/health")                           # liveness endpoint
def health():
    return {"ok": True}                       # simple JSON body

@app.get("/whoami")                           # shows what the proxy forwarded
def whoami(request: Request):
    return {
        "client": request.client.host,        # real IP when --proxy-headers is trusted
        "scheme": request.url.scheme,         # https when X-Forwarded-Proto is honoured
    }
```

```dockerfile
# fastapi/Dockerfile -- basic
FROM python:3.12-slim
# small Debian-based Python image (example tag)
WORKDIR /app
# app directory
COPY requirements.txt .
# copy deps list first for cache
RUN pip install --no-cache-dir -r requirements.txt
# install deps (requirements.txt contains: fastapi, uvicorn[standard])
COPY . .
# copy code
EXPOSE 8000
# documented port
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
# run server on all interfaces inside the container
```

```nginx
# nginx/default.conf -- basic proxy
server {
    listen 80;                                     # HTTP
    server_name ml.example.com;                    # dedicated subdomain
    location / {
        proxy_pass http://ml:8000;                 # FastAPI container
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 💻 Code / Config Example — Advanced

```dockerfile
# fastapi/Dockerfile -- production
FROM python:3.12-slim AS base
# slim keeps image small
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
# no .pyc files, unbuffered logs (shown instantly in docker logs), no pip cache
WORKDIR /app
RUN useradd --create-home --uid 10001 appuser
# non-root user
COPY requirements.txt .
RUN pip install -r requirements.txt
# deps layer (cached until requirements change)
COPY --chown=appuser:appuser . .
# code owned by non-root
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=15s --timeout=3s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health',timeout=2).status==200 else 1)"
# python-only healthcheck, no curl needed
CMD ["gunicorn", "main:app", "-k", "uvicorn.workers.UvicornWorker", "-w", "2", "-b", "0.0.0.0:8000", "--timeout", "120", "--graceful-timeout", "30"]
# 2 worker processes, graceful stop (requires gunicorn in requirements.txt)
```

```nginx
# nginx/default.conf -- production FastAPI proxy
limit_req_zone $binary_remote_addr zone=ml_rl:10m rate=5r/s;     # 5 req/s per IP

upstream fastapi_app {
    server ml:8000;                                # container name from Compose
    keepalive 16;                                  # connection reuse
}

server {
    listen 80;
    server_name app.example.com;
    server_tokens off;
    client_max_body_size 5m;                       # upload cap for ML inputs

    location /ml/ {
        limit_req zone=ml_rl burst=10 nodelay;     # throttle abusers
        proxy_pass http://fastapi_app/;            # trailing slash strips /ml/ prefix
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Prefix /ml;   # so FastAPI can build correct URLs
        proxy_read_timeout 120s;                   # slow model inference
    }

    location = /ml/docs     { allow 203.0.113.5; deny all; proxy_pass http://fastapi_app/docs; }          # office IP only (example)
    location = /ml/openapi.json { allow 203.0.113.5; deny all; proxy_pass http://fastapi_app/openapi.json; }
}
```

```yaml
# docker-compose.yml
services:
  nginx:
    image: nginx:1.27-alpine
    restart: unless-stopped
    ports: ["80:80", "443:443"]
    volumes: ["./nginx/default.conf:/etc/nginx/conf.d/default.conf:ro"]
    depends_on:
      ml: { condition: service_healthy }           # start after FastAPI is healthy
    networks: [edge, backend]
  ml:
    build: ./fastapi
    restart: unless-stopped
    command: ["gunicorn","main:app","-k","uvicorn.workers.UvicornWorker","-w","2","-b","0.0.0.0:8000"]  # override if needed
    environment:
      ROOT_PATH: /ml                                # use in code: FastAPI(root_path=os.getenv("ROOT_PATH",""))
    env_file: ./fastapi/.env                        # model keys etc., not in Git
    mem_limit: 1g                                   # ML needs more RAM
    read_only: true
    tmpfs: ["/tmp"]
    cap_drop: [ALL]
    security_opt: ["no-new-privileges:true"]
    networks: [backend]
    healthcheck:
      test: ["CMD","python","-c","import urllib.request;urllib.request.urlopen('http://127.0.0.1:8000/health',timeout=2)"]
      interval: 15s
      timeout: 3s
      retries: 3
networks:
  edge: {}
  backend: {}
```

Verified: `python3 -m py_compile` on main.py, YAML parsed, Dockerfile instruction check. Not built/run. `ROOT_PATH` is read by your own code (shown in comment); FastAPI's `root_path` behaviour with a stripped prefix is version dependent, so test `/ml/docs` loads after deployment. gunicorn must be listed in `requirements.txt`.

---

## 🟠 My Stack Integration
- Node.js calls FastAPI internally: `http://ml:8000/predict` from the `api` container (same `backend` network), skipping Nginx and the internet.
- React calls `/ml/predict` through Nginx for public endpoints only.
- GitHub Actions: `pytest` + `docker build` + push; VPS pulls and restarts `ml` then reloads Nginx.
- AWS: later move `ml` to ECS/Fargate; the Nginx upstream becomes an internal ALB/service-discovery name.

```python
# Node -> FastAPI internal call concept (no Nginx hop)
# const r = await fetch('http://ml:8000/predict', {method:'POST', body: JSON.stringify(data), headers:{'content-type':'application/json'}});
```

Security: hide `/docs` or protect it with auth/IP, validate input with Pydantic models, cap body size at Nginx and in the app, run non-root, keep model files and API keys out of the image, scan dependencies (`pip-audit`).

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Running `uvicorn --reload` in production.
✅ Correct: `--reload` is for dev only; use gunicorn/uvicorn workers.

❌ Mistake 2: Binding to `127.0.0.1`.
✅ Correct: `--host 0.0.0.0` inside the container.

❌ Mistake 3: Using `--forwarded-allow-ips='*'` while port 8000 is also published on the host.
✅ Correct: Do not publish 8000; trust only Nginx's network.

❌ Mistake 4: Default 60 s timeouts killing long ML requests with 504.
✅ Correct: Raise `proxy_read_timeout` and gunicorn `--timeout`, or move long jobs to a queue.

---

## 🧠 Tricky Interview Question
Swagger UI at `/ml/docs` shows a blank page behind Nginx, though `/docs` works directly on the container. Why?

Answer: Swagger builds the OpenAPI URL as `/openapi.json` relative to the server root, but the public path is `/ml/openapi.json`. Because Nginx strips `/ml`, FastAPI does not know the prefix. Pass `root_path="/ml"` (or `uvicorn --root-path /ml`) so docs request `/ml/openapi.json`, and make sure Nginx allows that path.

---

## ⚫ Interview Questions + Answers

Q1: uvicorn vs gunicorn?
A1: uvicorn is the ASGI server; gunicorn is a process manager that can run multiple uvicorn workers for CPU use and restarts. Either is fine behind Nginx; use workers for CPU-bound or multi-core.

Q2: What does `--proxy-headers` do?
A2: Makes uvicorn honour `X-Forwarded-For/Proto` so `request.client` and URL scheme reflect the real client; trust only from known proxies.

Q3: How many workers?
A3: Start with `(2 x cores) + 1` for sync-heavy code; for async I/O-bound apps fewer workers suffice. Each worker loads the model in RAM, so watch memory.

Q4: Sync vs async endpoints?
A4: `async def` must not block; CPU-heavy code goes to threadpool (`def`) or a task queue (Celery/RQ) so the event loop stays responsive.

Q5: How to stream or upload large files?
A5: Raise `client_max_body_size`, consider `proxy_request_buffering off`, and stream to S3 rather than memory.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You run Python APIs on a VPS and need TLS, limits and path routing.
- You host Node and FastAPI side by side under one domain.

❌ Avoid when:
- Using AWS API Gateway/ALB directly in front of Lambda/ECS and no extra proxy is needed.

---

## 📊 Visual Diagram
```
 Browser --> nginx (:443)
              |--- /api/ ---> api (Node :3000)
              |--- /ml/  ---> ml (gunicorn+uvicorn :8000)  [timeout 120s, 5MB cap]
              |--- /ml/docs -> allow office IP, deny others
 api --(internal http)--> ml:8000/predict   (never leaves the VPS)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ASGI | Async Python web interface | async Python interface |
| uvicorn | ASGI server | ASGI server |
| gunicorn | Process manager for workers | workers का manager |
| root_path | URL prefix behind a proxy | proxy के पीछे prefix |
| Pydantic | Input validation library | input validation |
| OpenAPI | Machine-readable API spec | API specification |

---

## ⚡ 3-Line Summary
English: Nginx fronts a private FastAPI container; uvicorn/gunicorn runs the app on 8000.
Set proxy headers, root_path, timeouts and protect /docs.
Never use --reload in production.
Hindi: Nginx private FastAPI container के आगे रहता है; uvicorn/gunicorn app को 8000 पर चलाता है।
Proxy headers, root_path, timeouts सेट करो और /docs को protect करो।
Production में कभी --reload मत चलाओ।

---

## ➡️ Next Topic
410. Nginx + React in Docker - serve the frontend build from Nginx.
