# 081. EXPOSE Instruction
# हिंदी में: EXPOSE इंस्ट्रक्शन (Port Documentation)

---

## 🔵 Simple Definition (English)
`EXPOSE` documents which network port(s) the containerised app listens on. It is **metadata only**: it does not open or publish the port to the host. To reach the app from outside, you must publish it with `-p` (or `ports:` in Compose).

## 🔵 सरल परिभाषा (Hindi)
`EXPOSE` बताता है कि container के अंदर app कौन-से port पर सुनती है। यह सिर्फ **metadata/documentation** है: यह port को host पर खोलता या publish नहीं करता। बाहर से app तक पहुँचने के लिए `-p` (या Compose में `ports:`) से publish करना पड़ता है।

---

## 🔴 Problem it Solves
A new teammate gets an image and has no idea whether the app listens on 3000, 8000 or 80. Reading source code is slow. `EXPOSE` records the intended port inside the image, so `docker inspect`, `docker ps`, and tools like `docker run -P` and Compose can discover it. It is documentation that travels with the artifact.

## 🔴 यह क्यों बना? (Hindi)
नए teammate को image मिलती है और पता नहीं कि app 3000, 8000 या 80 में से किस port पर सुनती है। Source code पढ़ना धीमा है। `EXPOSE` image के अंदर intended port लिख देता है ताकि `docker inspect`, `docker ps`, और `docker run -P` जैसे tools उसे पा सकें। यह documentation है जो artifact के साथ चलती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Dockerfile has: EXPOSE 8000/tcp  (protocol optional, default tcp)
Step 2 → Build stores it in image config (ExposedPorts)
Step 3 → docker run WITHOUT -p: port reachable only from other containers on the same network
Step 4 → docker run -p 8080:8000: host 8080 -> container 8000 (the real publish)
Step 5 → docker run -P: Docker publishes ALL exposed ports to random high host ports
```

Key point: containers on the same user-defined Docker network can already reach each other on any listening port, even without EXPOSE.

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Dockerfile में: EXPOSE 8000/tcp  (protocol optional, default tcp)
Step 2 → Build इसे image config (ExposedPorts) में रख देता है
Step 3 → -p के बिना docker run: port सिर्फ उसी network के दूसरे containers से पहुँचने लायक
Step 4 → docker run -p 8080:8000: host 8080 -> container 8000 (असली publish)
Step 5 → docker run -P: सभी exposed ports को random high host ports पर publish करता है
```

मुख्य बात: एक ही user-defined Docker network पर containers EXPOSE के बिना भी एक-दूसरे के listening port तक पहुँच सकते हैं।

---

## 🟡 Real World Example
On your VPS, Nginx (container) proxies to the Node.js API (container). The API image says `EXPOSE 3000`. In Compose, the API has **no** `ports:` entry, so port 3000 is never open on the public internet; only Nginx publishes 80/443. A teammate runs `docker inspect api` and sees 3000. A pen-tester scanning the VPS finds only 80 and 443. That is exactly the design: document with EXPOSE, publish only the edge.

## 🟡 Real Example Hindi mein
आपके VPS पर Nginx (container) Node.js API (container) को proxy करता है। API image में `EXPOSE 3000` है। Compose में API के लिए **कोई** `ports:` नहीं है, इसलिए 3000 public internet पर कभी खुला नहीं होता; सिर्फ Nginx 80/443 publish करता है। Teammate `docker inspect api` से 3000 देखता है। VPS scan करने वाला pen-tester को सिर्फ 80 और 443 मिलते हैं। यही सही design है: EXPOSE से document करो, सिर्फ edge को publish करो।

---

## 💻 Code / Config Example — Basic

```dockerfile
# Basic EXPOSE example (Node.js)
# Base image (example tag)
FROM node:20-alpine
# Working directory
WORKDIR /app
# Copy source
COPY . .
# Install dependencies
RUN npm ci --omit=dev
# Tell readers/tools the app listens on TCP 3000 (does NOT publish it)
EXPOSE 3000
# Start the app (server must listen on 0.0.0.0, not 127.0.0.1)
CMD ["node", "server.js"]
```

```bash
# Build the image
docker build -t demo-api .
# Publish container port 3000 on host port 8080 (this is what actually opens it)
docker run -d --name demo -p 8080:3000 demo-api
# Show the port mapping
docker port demo
# Bind to localhost only on the host (safer on a VPS)
docker run -d --name demo2 -p 127.0.0.1:8081:3000 demo-api
```

## 💻 Code / Config Example — Advanced

```dockerfile
# syntax=docker/dockerfile:1
# Advanced: FastAPI service exposing app port + metrics port, with a healthcheck
# Python slim base (example tag)
FROM python:3.12-slim
# Logs unbuffered, no .pyc files
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
# Working directory
WORKDIR /app
# Dependencies first (cache friendly)
COPY requirements.txt .
# Install dependencies without keeping the pip cache
RUN pip install --no-cache-dir -r requirements.txt
# Application code
COPY app ./app
# Non-root user
RUN useradd --system --no-create-home appuser
# Drop privileges
USER appuser
# Main HTTP API port (TCP is the default; stated explicitly for clarity)
EXPOSE 8000/tcp
# Prometheus metrics port (separate so Nginx does not expose it publicly)
EXPOSE 9100/tcp
# Healthcheck uses python (slim has no curl) against the app port
HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
  CMD ["python", "-c", "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health').status==200 else 1)"]
# Start uvicorn listening on all interfaces
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml: publish ONLY the edge, keep the rest internal
services:
  # Reverse proxy, the only public entry point
  nginx:
    # Official nginx image (example tag)
    image: nginx:1.27-alpine
    # Publish HTTP and HTTPS to the world
    ports:
      - "80:80"
      - "443:443"
    # Start after the API container is up
    depends_on:
      - api
  # FastAPI app
  api:
    # Built from the Dockerfile above
    build: ./backend
    # "expose" in Compose = internal only (like EXPOSE), no host binding
    expose:
      - "8000"
    # Debug access, only on the VPS loopback (reach it via SSH tunnel)
    # ports:
    #   - "127.0.0.1:8000:8000"
```

---

## 🟠 My Stack Integration
- **Node.js**: `EXPOSE 3000`; make sure the app binds to `0.0.0.0`.
- **FastAPI**: `EXPOSE 8000`; run uvicorn with `--host 0.0.0.0`.
- **React + Nginx**: the Nginx image serves on 80, so `EXPOSE 80`.
- **VPS**: publish only 80/443 via Nginx; bind debug ports to `127.0.0.1`.
- **AWS**: the Security Group is a second firewall; allow 80/443 only. Note that Docker's `-p` rules bypass `ufw`, so use the AWS Security Group (or bind to 127.0.0.1) as the real gate.
- **ECS/EKS**: port mappings / Service `targetPort` are set separately; EXPOSE is only a hint.

```nginx
# Nginx upstream pointing at the internal (exposed, unpublished) API port
# nginx.conf fragment (not tested locally)
# upstream block names the internal backend
upstream api_backend {
    # service name "api" resolves via Docker DNS; port from EXPOSE
    server api:8000;
}
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Believing `EXPOSE 3000` makes `http://server:3000` reachable.
✅ Correct: Add `-p 3000:3000` (or `ports:` in Compose).

❌ Mistake 2: Publishing databases like `-p 5432:5432` / `-p 27017:27017` on a VPS. Docker edits iptables and bypasses ufw, so the DB is open to the internet.
✅ Correct: Do not publish it; let apps reach it over the Docker network, or use `127.0.0.1:5432:5432`.

❌ Mistake 3: App listens on `127.0.0.1` inside the container, so even `-p` does not work.
✅ Correct: Bind the app to `0.0.0.0`.

❌ Mistake 4: Writing `EXPOSE 3000:3000`.
✅ Correct: `EXPOSE` takes only the container port. Mapping uses `-p HOST:CONTAINER`.

---

## 🧠 Tricky Interview Question
You remove `EXPOSE 3000` from the Dockerfile and rebuild. Will `docker run -p 8080:3000 image` still work? And will Nginx in the same Compose network still reach `api:3000`?

Answer: Yes to both. `EXPOSE` is documentation, not a firewall rule. `-p` publishes the port regardless, and containers on the same network can reach each other's listening ports regardless. What breaks is `docker run -P` (it publishes only exposed ports) and the discoverability for humans/tools.

---

## ⚫ Interview Questions + Answers

Q1: Does EXPOSE publish a port?
A1: No. It is metadata. Use `-p`/`-P` or Compose `ports:`.

Q2: Difference between `EXPOSE` and `-p`?
A2: EXPOSE is build-time documentation of the container port. `-p` is run-time publishing that maps a host port to a container port.

Q3: What does `-P` do?
A3: Publishes all EXPOSEd ports to random ephemeral ports on the host.

Q4: How do you expose UDP?
A4: `EXPOSE 53/udp`. For both: `EXPOSE 53/tcp` and `EXPOSE 53/udp`.

Q5: Compose `expose:` vs `ports:`?
A5: `expose:` makes the port accessible to linked services only (no host binding). `ports:` binds on the host.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Every image that listens on a port (good documentation habit).
- Tools or teammates need to discover the port quickly.
- Using `docker run -P` in quick tests.

❌ Avoid when:
- Expecting it to enforce security. It does not.
- The image does not listen on anything (batch jobs, workers).

---

## 📊 Visual Diagram

```
 Internet
    |  80/443 (published with -p)
    v
+---------+   Docker network (private)   +-------------------+
|  Nginx  | ---------------------------> |  api container    |
| ports:  |       api:8000               |  EXPOSE 8000      |
| 80,443  |                              |  (no host port)   |
+---------+                              +-------------------+
                                                  ^
 Internet --X--> host:8000  (not published, unreachable)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| EXPOSE | Documents container port | container port का documentation |
| Publish (-p) | Map host port to container port | host port को container से जोड़ना |
| -P | Publish all exposed ports randomly | सभी exposed ports random publish |
| Bridge network | Default private Docker network | Docker का private network |
| 0.0.0.0 | Listen on all interfaces | सभी interfaces पर सुनना |
| Security Group | AWS virtual firewall | AWS का virtual firewall |

---

## ⚡ 3-Line Summary
English: EXPOSE only documents the port; it never opens it. Publishing is done by `-p` or Compose `ports:`. Publish only the edge (Nginx) and keep apps and databases internal.
Hindi: EXPOSE सिर्फ port document करता है; खोलता नहीं। Publish `-p` या Compose `ports:` से होता है। सिर्फ edge (Nginx) publish करो, apps और databases internal रखो।

---

## ➡️ Next Topic
**082. VOLUME Instruction**: ports are about network; next is data. Learn how the Dockerfile marks directories for persistent storage.
