# 194. deploy (resource limits)
# हिंदी में: Compose में deploy और Resource Limits (CPU / Memory की सीमा)

---

## 🔵 Simple Definition (English)
The `deploy.resources` section in a Compose service sets hard limits (and optional reservations) for CPU and memory. `docker compose up` (Compose v2) honours `deploy.resources.limits`, so one greedy container cannot starve the whole server.

## 🔵 सरल परिभाषा (Hindi)
Compose service में `deploy.resources` section CPU और memory की hard limits (और optional reservations) तय करता है। Compose v2 का `docker compose up` `deploy.resources.limits` को मानता है, जिससे एक लालची container पूरे server को भूखा नहीं रख सकता।

---

## 🔴 Problem it Solves
By default a container may use all CPU cores and all RAM of the host. A Node.js memory leak or a heavy FastAPI report job can eat 100% of a 2 GB VPS, the Linux OOM killer then kills random processes (maybe Postgres or sshd), and the whole box becomes unreachable. Limits make one service fail alone instead of taking everything down.

## 🔴 यह क्यों बना? (Hindi)
Default में container host की सारी CPU cores और पूरी RAM इस्तेमाल कर सकता है। Node.js का memory leak या FastAPI का भारी report job 2 GB VPS की 100% RAM खा सकता है, फिर Linux OOM killer कोई भी process मार देता है (शायद Postgres या sshd), और पूरा box unreachable हो जाता है। Limits से एक service अकेली fail होती है, सब कुछ नहीं गिरता।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You write deploy.resources.limits (cpus, memory) under a service
Step 2 → Compose v2 translates them into container settings (like --cpus and --memory)
Step 3 → The Linux kernel enforces them with cgroups
Step 4 → CPU over the limit: the container is throttled (slowed), not killed
Step 5 → Memory over the limit: the kernel OOM-kills the container process (exit 137)
Step 6 → restart policy (topic 193) may bring it back
Step 7 → reservations are a soft minimum used for scheduling (mainly Swarm)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → आप service के नीचे deploy.resources.limits (cpus, memory) लिखते हैं
Step 2 → Compose v2 इन्हें container settings में बदलता है (जैसे --cpus और --memory)
Step 3 → Linux kernel cgroups से इन्हें लागू करता है
Step 4 → CPU limit पार हो तो container throttle (धीमा) होता है, मरता नहीं
Step 5 → Memory limit पार हो तो kernel OOM-kill करता है (exit code 137)
Step 6 → restart policy (topic 193) उसे वापस ला सकती है
Step 7 → reservations एक soft minimum हैं, ज़्यादातर Swarm scheduling में काम आती हैं
```

---

## 🟡 Real World Example
A Zomato-like analytics API shares a 4 GB EC2 box with Postgres and Redis. A bad query in the Node service balloons its memory to 3.5 GB. With `memory: 512M` on the API, only the API container is OOM-killed and restarted; Postgres and Redis stay healthy. Without it, the kernel could kill Postgres and corrupt in-flight work.

## 🟡 Real Example Hindi mein
Zomato जैसी analytics API 4 GB EC2 box पर Postgres और Redis के साथ चल रही है। Node service में एक खराब query उसकी memory 3.5 GB तक फुला देती है। API पर `memory: 512M` हो तो सिर्फ API container OOM-kill होकर restart होता है; Postgres और Redis ठीक रहते हैं। इसके बिना kernel Postgres को मार सकता है।

---

## 💻 Code / Config Example — Basic
```yaml
# docker-compose.yml  (Basic: cap one service)
services:
  api:
    image: node:20-alpine           # example tag
    command: ["node", "server.js"]  # run the server
    working_dir: /app               # app folder in container
    volumes:
      - ./:/app                     # mount code
    deploy:                         # deployment-related settings
      resources:                    # resource section
        limits:                     # hard ceiling, cannot exceed
          cpus: "0.50"              # half of one CPU core (string, quote it)
          memory: 512M              # 512 megabytes of RAM
```

## 💻 Code / Config Example — Advanced
```yaml
# docker-compose.yml  (Advanced: whole stack budgeted for a 4 GB / 2 vCPU VPS)
services:
  nginx:
    image: nginx:1.27-alpine         # example tag
    restart: unless-stopped          # revive after crash
    ports: ["80:80"]                 # public HTTP
    deploy:
      resources:
        limits: { cpus: "0.25", memory: 128M }   # proxy is light
        reservations: { cpus: "0.10", memory: 64M } # soft minimum

  api:
    build: ./api                     # Node.js image
    restart: unless-stopped
    environment:
      NODE_OPTIONS: "--max-old-space-size=384"   # V8 heap below the container limit (leave headroom)
    deploy:
      resources:
        limits: { cpus: "0.75", memory: 512M }   # hard cap
        reservations: { memory: 256M }           # expected normal usage
    pids_limit: 200                  # stops fork bombs (service-level key, not under deploy)

  postgres:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_pass   # secret file path
    secrets: [db_pass]               # attach secret
    shm_size: 128mb                  # Postgres needs shared memory
    deploy:
      resources:
        limits: { cpus: "1.00", memory: 1G }     # biggest consumer gets most
        reservations: { memory: 512M }

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    command: ["redis-server", "--maxmemory", "200mb", "--maxmemory-policy", "allkeys-lru"] # Redis self-limit below container cap
    deploy:
      resources:
        limits: { cpus: "0.25", memory: 256M }   # a little above maxmemory

secrets:
  db_pass:
    file: ./secrets/db_pass.txt      # keep out of git
```

Check the limits are applied: `docker stats --no-stream` (shows MEM LIMIT) and `docker inspect api --format '{{.HostConfig.Memory}}'`.

---

## 🟠 My Stack Integration
- **Node.js:** set V8 heap (`--max-old-space-size`) lower than the container limit; otherwise the kernel kills Node before V8 can garbage-collect.
- **FastAPI:** each uvicorn/gunicorn worker uses its own memory; budget `workers x per-worker RAM` inside the limit.
- **React:** build the static files in a CI/multi-stage build, not on the small VPS; runtime is just Nginx (tiny).
- **Nginx:** very small limits are fine.
- **AWS:** match container limits to the instance size (t3.small = 2 GB); leave 20 to 25% for the OS and Docker daemon.
- **Security:** limits are also a denial-of-service defence (a compromised container cannot take the whole host).

```yaml
# docker-compose.yml  (my stack fragment: FastAPI with 2 workers)
services:
  ml:
    build: ./fastapi                        # FastAPI image
    command: ["uvicorn","main:app","--host","0.0.0.0","--workers","2"]  # 2 worker processes
    deploy:
      resources:
        limits: { cpus: "1.00", memory: 768M }  # about 300 MB per worker + headroom
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Setting `cpus: 0.5` as a number in older tooling, causing a type error.
✅ Correct: Quote it: `cpus: "0.50"`.

❌ Mistake 2: Limit equals the app's normal use. The app is OOM-killed on every traffic peak.
✅ Correct: Measure with `docker stats`, then set the limit at about 1.5x the peak.

❌ Mistake 3: Assuming `deploy` is ignored outside Swarm. Old docker-compose v1 ignored it unless `--compatibility` was passed; Compose v2 applies `limits`. (Version-dependent: check `docker compose version`.)
✅ Correct: Use Compose v2 and verify with `docker inspect`.

❌ Mistake 4: Giving Node a heap bigger than the container memory.
✅ Correct: `--max-old-space-size` at about 75% of the limit.

---

## 🧠 Tricky Interview Question
Your API container has `memory: 512M` and keeps restarting with exit code 137, but `docker logs` shows no error. What happened and how do you confirm?

Answer: Exit code 137 = 128 + 9 (SIGKILL). The kernel OOM killer killed it for crossing the cgroup memory limit, so the app had no chance to log. Confirm with `docker inspect api --format '{{.State.OOMKilled}}'` (true) and `dmesg | grep -i oom`. Fix by finding the leak, tuning the heap, or raising the limit.

---

## ⚫ Interview Questions + Answers

Q1: Difference between `limits` and `reservations`?
A1: A limit is a hard maximum enforced by cgroups. A reservation is a guaranteed minimum used by the scheduler (mainly Swarm); on a single host it is mostly informational.

Q2: What happens when CPU limit is exceeded vs memory limit?
A2: CPU is throttled (the process slows down). Memory is not compressible, so the process is OOM-killed.

Q3: Are there older ways to set limits in Compose?
A3: Yes: service-level `mem_limit`, `cpus`, `mem_reservation` (Compose spec still accepts them). `deploy.resources` is the modern, recommended form.

Q4: How do you see live usage?
A4: `docker stats` (CPU %, memory usage / limit, network, PIDs).

Q5: Why also set `pids_limit`?
A5: It caps the number of processes, so a fork bomb inside a container cannot exhaust the host.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Several services share one VPS/EC2.
- You run untrusted or user-triggered heavy work (reports, image processing).
- You want noisy neighbours isolated.

❌ Avoid when:
- You have not measured real usage (limits would be guesses).
- Databases with a tight limit and no tuning (Postgres `shared_buffers` must fit inside).

---

## 📊 Visual Diagram
```
 VPS: 4 GB RAM, 2 vCPU
 +------------------------------------------------------+
 | nginx 128M | api 512M | postgres 1G | redis 256M | OS |
 +------------------------------------------------------+
        cgroups enforce each box
 api leaks ->  [api] hits 512M -> OOM kill (137) -> restart
               others untouched
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| cgroup | Kernel feature that limits resources per process group | resource सीमा का kernel feature |
| limits | Hard max for CPU/memory | अधिकतम सीमा |
| reservations | Soft guaranteed minimum | न्यूनतम गारंटी |
| OOM killer | Kernel kills process when memory is exhausted | memory खत्म होने पर process मारना |
| throttling | Slowing CPU use | CPU धीमा करना |
| exit 137 | Killed by SIGKILL (often OOM) | SIGKILL से मारा गया |

---

## ⚡ 3-Line Summary
English: `deploy.resources.limits` caps CPU and memory per service using cgroups. CPU is throttled, memory overuse means an OOM kill (137). Measure first, then set about 1.5x peak and align Node/Postgres settings.
Hindi: `deploy.resources.limits` cgroups से हर service की CPU और memory सीमित करता है। CPU धीमा होता है, memory ज़्यादा हुई तो OOM kill (137)। पहले measure करें, फिर peak का करीब 1.5 गुना रखें और Node/Postgres settings उसी के मुताबिक रखें।

---

## ➡️ Next Topic
**195. volumes in Compose**: limits protect CPU and RAM; next we protect data with bind mounts and named volumes.
