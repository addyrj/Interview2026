# 219. Resource Limits in Production
# हिंदी में: Production में Resource Limits

---

## 🔵 Simple Definition (English)
**Resource limits** cap how much CPU, memory, processes (PIDs) and disk I/O a container may use. Docker enforces them with Linux **cgroups**. Without limits, a single container can eat the whole server. With limits, a misbehaving container is throttled (CPU) or killed by the OOM killer (memory) while others keep running.

## 🔵 सरल परिभाषा (Hindi)
**Resource limits** तय करते हैं कि एक container कितनी CPU, memory, processes (PIDs) और disk I/O use कर सकता है। Docker इन्हें Linux **cgroups** से लागू करता है। Limits के बिना एक container पूरा server खा सकता है। Limits के साथ गलत चल रहा container throttle (CPU) या OOM killer से kill (memory) हो जाता है और बाकी चलते रहते हैं।

---

## 🔴 Problem it Solves
The "noisy neighbour" problem: a Node.js memory leak grows to 6 GB on an 8 GB VPS, the kernel OOM killer picks a random process (maybe PostgreSQL or sshd), the site is down and you cannot even SSH in. A fork bomb or a runaway regex can pin all CPU cores. Limits give predictable behaviour, protect the host, allow safe packing of many services on one box, and make capacity planning possible.

## 🔴 यह क्यों बना? (Hindi)
"Noisy neighbour" problem: 8 GB VPS पर Node.js memory leak 6 GB तक बढ़ता है, kernel का OOM killer कोई भी process चुन लेता है (शायद PostgreSQL या sshd), site down हो जाती है और आप SSH भी नहीं कर पाते। Fork bomb या बेकाबू regex सारे CPU cores घेर सकता है। Limits predictable behaviour देते हैं, host को बचाते हैं, एक box पर कई services safely रखने देते हैं और capacity planning संभव बनाते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You set limits: --memory 512m --cpus 1.0 --pids-limit 200 (or in Compose).
Step 2 → Docker creates a cgroup for the container and writes the limits into it.
Step 3 → CPU: kernel scheduler throttles the container when it uses more than its quota (it slows, not dies).
Step 4 → Memory: if usage reaches the limit, kernel OOM killer kills a process in that cgroup.
         Container exits with code 137 and State.OOMKilled=true. Restart policy may bring it back.
Step 5 → PIDs: when the process count hits the limit, fork() fails (stops fork bombs).
Step 6 → You watch usage with `docker stats` and tune: limit = peak usage + 20-30% headroom.
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → आप limits देते हो: --memory 512m --cpus 1.0 --pids-limit 200 (या Compose में)।
Step 2 → Docker container के लिए cgroup बनाता है और limits उसमें लिखता है।
Step 3 → CPU: quota से ज़्यादा use करने पर kernel scheduler throttle करता है (धीमा होता है, मरता नहीं)।
Step 4 → Memory: limit तक पहुँचने पर OOM killer उस cgroup का process kill करता है।
         Container exit code 137 और State.OOMKilled=true के साथ बंद। Restart policy वापस ला सकती है।
Step 5 → PIDs: process count limit छूते ही fork() fail होता है (fork bomb रुकता है)।
Step 6 → `docker stats` से usage देखो और tune करो: limit = peak usage + 20-30% headroom।
```

Key flags / मुख्य flags:

| Flag | Meaning | Hindi |
|------|---------|-------|
| `--memory` / `-m` | Hard memory cap | Memory की hard limit |
| `--memory-reservation` | Soft limit (hint under pressure) | Soft limit |
| `--memory-swap` | RAM + swap total (equal to memory = no swap) | RAM+swap कुल |
| `--cpus` | CPU count (1.5 = one and half cores) | CPU cores की संख्या |
| `--cpu-shares` | Relative weight when CPUs are busy | Relative weight |
| `--pids-limit` | Max processes/threads | Max processes |
| `--ulimit nofile=` | Open file descriptors | Open files limit |

---

## 🟡 Real World Example
An e-commerce site on one 4 vCPU / 8 GB EC2 instance runs Nginx, a Node.js API, a FastAPI image-resizer, Redis and PostgreSQL. During a sale, the image-resizer processes giant uploads and uses all RAM. Without limits, Linux kills PostgreSQL and the shop goes down. After adding `memory: 1g` and `cpus: 1.0` to the resizer, a spike only restarts the resizer (OOMKilled), the checkout keeps working, and a CloudWatch alarm on restart count tells the team.

## 🟡 Real Example Hindi mein
एक e-commerce site एक 4 vCPU / 8 GB EC2 पर Nginx, Node.js API, FastAPI image-resizer, Redis और PostgreSQL चलाती है। Sale के दौरान image-resizer बड़े uploads process करके सारी RAM खा गया। Limits के बिना Linux ने PostgreSQL kill कर दिया और shop बंद हो गई। Resizer पर `memory: 1g` और `cpus: 1.0` लगाने के बाद spike सिर्फ resizer को restart करता है (OOMKilled), checkout चलता रहता है, और restart count पर CloudWatch alarm team को बता देता है।

---

## 💻 Code / Config Example — Basic

```bash
# Run a Node.js container with basic limits
docker run -d --name api \
  --memory 512m \
  --cpus 1.0 \
  --pids-limit 200 \
  myorg/api:1.4.2                       # hard cap 512MB RAM, 1 CPU, 200 processes
# (explanations: --memory = hard cap, --cpus = CPU quota, --pids-limit = fork-bomb guard)

# Watch live usage (one-shot, no streaming)
docker stats --no-stream api            # shows CPU%, MEM USAGE / LIMIT, PIDS

# Change limits of a running container without recreating it
docker update --memory 768m --memory-swap 768m api   # raise cap; swap = memory means no swap

# Was it killed for memory?
docker inspect -f '{{.State.OOMKilled}} {{.State.ExitCode}}' api   # true 137 means OOM kill
```

## 💻 Code / Config Example — Advanced

```yaml
# docker-compose.prod.yml - limits for a full stack (Compose v2, non-Swarm)
services:
  nginx:
    image: nginx:1.27-alpine               # example tag
    mem_limit: 128m                        # hard memory cap
    cpus: 0.5                              # half a core
    pids_limit: 100                        # process cap
    restart: unless-stopped                # restart policy
  api:
    image: myorg/node-api:1.4.2            # Node.js API
    environment:
      NODE_OPTIONS: "--max-old-space-size=384"   # V8 heap below the 512m container cap (leave headroom)
    deploy:
      resources:
        limits:
          cpus: "1.0"                      # max 1 CPU
          memory: 512M                     # hard memory cap
          pids: 200                        # max processes
        reservations:
          cpus: "0.25"                     # guaranteed share (scheduling hint)
          memory: 256M                     # soft/guaranteed memory
    ulimits:
      nofile:
        soft: 8192                         # open files soft limit (many sockets)
        hard: 16384                        # open files hard limit
    restart: unless-stopped                # come back after OOM kill
  fastapi:
    image: myorg/fastapi:2.0.1             # FastAPI service
    deploy:
      resources:
        limits:
          cpus: "1.5"                      # ML/image work needs more CPU
          memory: 1G                       # hard cap
    memswap_limit: 1g                      # equal to memory -> swap disabled
    restart: unless-stopped
  redis:
    image: redis:7-alpine                  # cache
    command: ["redis-server", "--maxmemory", "200mb", "--maxmemory-policy", "allkeys-lru"]  # app-level cap below container cap
    mem_limit: 256m                        # container cap a bit above Redis maxmemory
    restart: unless-stopped
```

`docker compose` (v2) applies `deploy.resources.limits` outside Swarm; older docker-compose v1 needed `--compatibility`. Parsed as valid YAML locally; not run (no Docker daemon). / Compose v2 में `deploy.resources.limits` Swarm के बाहर भी लागू होता है।

```bash
# Verify applied limits after `docker compose up -d`
docker inspect -f '{{.HostConfig.Memory}} {{.HostConfig.NanoCpus}} {{.HostConfig.PidsLimit}}' \
  $(docker compose ps -q api)            # bytes, nano-CPUs (1e9 = 1 CPU), pids
```

---

## 🟠 My Stack Integration
- **Node.js**: set `--max-old-space-size` to about 75% of the container memory so V8 garbage-collects before the kernel kills it. Node is single-threaded: more than `cpus: 1` helps only with cluster/worker_threads.
- **FastAPI (uvicorn/gunicorn)**: workers = about CPU limit (not host cores!). Many images read `os.cpu_count()` which shows the host's CPUs, not the limit, so set `WEB_CONCURRENCY` explicitly.
- **Nginx**: tiny footprint; 128 MB is enough for a reverse proxy.
- **React**: static build is served by Nginx; no runtime of its own.
- **VPS/EC2**: sum of all limits should be under total RAM (keep 15-20% for the OS and Docker). On ECS set task-level and container-level `memory` and `cpu`.

```yaml
# FastAPI sizing example in compose
services:
  fastapi:
    image: myorg/fastapi:2.0.1
    environment:
      WEB_CONCURRENCY: "2"                 # 2 workers for a 1.5 CPU limit
    deploy:
      resources:
        limits: { cpus: "1.5", memory: 1G }   # inline map style, same meaning
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: No limits at all in production.
✅ Correct: At least memory and PIDs on every service.

❌ Mistake 2: Memory limit equals Node's heap size (`--max-old-space-size=512` with `memory: 512M`). Buffers, native memory and stacks are outside the heap, so OOM kill happens.
✅ Correct: Heap about 70-75% of the container limit.

❌ Mistake 3: Setting the limit too low and getting a restart loop.
✅ Correct: Measure with `docker stats` under load, add 20-30% headroom.

❌ Mistake 4: Leaving swap on, which hides leaks and makes the app crawl.
✅ Correct: `memswap_limit` equal to memory to disable swap, and alert on restarts.

❌ Mistake 5: Using gunicorn `workers = cpu_count()*2+1` inside a limited container.
✅ Correct: Set workers by the CPU limit.

---

## 🧠 Tricky Interview Question
**Q:** You set `--cpus 0.5` but `docker stats` shows 100% CPU for the container. Is the limit broken?

**Answer:** No. `docker stats` CPU% is relative to ONE core (can go above 100% on multi-core). With `--cpus 0.5` the maximum shown is about 50%. If you see 100%, you probably have `--cpus 1`. Also, CPU limit uses CFS quota: the container can burst to full speed for part of each 100 ms period and then gets throttled, so check `cpu.stat` throttled_time to see throttling. Memory behaves differently: it is not throttled, it is killed.

---

## ⚫ Interview Questions + Answers

Q1: Difference between CPU limits and memory limits behaviour?
A1: CPU is compressible: exceeding it only slows the container. Memory is incompressible: exceeding it triggers OOM kill.

Q2: What is exit code 137?
A2: 128 + 9 (SIGKILL). It means the process was killed, often by OOM killer or `docker kill` / grace period expiry. Confirm with `OOMKilled=true`.

Q3: `limits` vs `reservations`?
A3: Limits are the maximum allowed. Reservations are the minimum guaranteed or used for scheduling (Swarm/Kubernetes requests). In plain Compose, memory reservation is a soft limit.

Q4: Why does a container sometimes see host memory in `free -m`?
A4: Tools like `free`, `top` read /proc which shows host values. Check `/sys/fs/cgroup/memory.max` (cgroup v2) for the real limit. Modern Node (v12+) and Java detect cgroup limits.

Q5: How do you pick limit values?
A5: Load-test, measure peak with `docker stats` or Prometheus cAdvisor, set limit = peak + 25%, set reservation = typical usage, and review monthly.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Multiple services share one VPS or EC2 host
- Any production workload (memory and PIDs at minimum)
- Services that process user-controlled input (uploads, regex, PDFs)

❌ Avoid when:
- You guess values without measuring (you will get OOM loops)
- Strict CPU caps on latency-critical services that burst (prefer `cpu-shares` or generous quota)
- Databases where an OOM kill risks data (give them reservation and leave them without tight caps, plus monitoring)

---

## 📊 Visual Diagram
```
 Host: 8 GB RAM, 4 CPU
 +----------------------------------------------------------+
 | nginx   128M | api  512M | fastapi 1G | redis 256M | pg 2G |  <- cgroup limits
 +----------------------------------------------------------+
        |                     |
        | usage < limit       | usage hits 1G
        v                     v
     normal             OOM killer kills ONLY fastapi
                        -> exit 137, restart: unless-stopped
 CPU over quota -> throttled (slower), never killed
 Others keep running; host stays alive (sshd safe)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| cgroup | Kernel feature that limits resources | Resource सीमित करने वाला kernel feature |
| OOM killer | Kills processes when memory is out | Memory ख़त्म होने पर process मारता है |
| Throttling | Slowing CPU use | CPU धीमा करना |
| Reservation | Guaranteed/soft amount | Guaranteed/soft मात्रा |
| PIDs limit | Max processes | Max processes |
| Exit 137 | Killed by SIGKILL | SIGKILL से मारा गया |

---

## ⚡ 3-Line Summary
English: Limits (memory, CPU, PIDs) stop one container from taking down the host.
Memory overuse means OOM kill, CPU overuse means throttling; measure, then add headroom.
Align app settings (Node heap, uvicorn workers) with the container limits.

Hindi: Limits (memory, CPU, PIDs) एक container को पूरे host को गिराने से रोकते हैं।
Memory ज़्यादा = OOM kill, CPU ज़्यादा = throttling; पहले measure करो, फिर headroom जोड़ो।
App settings (Node heap, uvicorn workers) को container limits के साथ मिलाओ।

---

## ➡️ Next Topic
**220. Health Checks in Production** - limits keep the host safe; health checks tell Docker and the load balancer when a container is actually ready and alive.
