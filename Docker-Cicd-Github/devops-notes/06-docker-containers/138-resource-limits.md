---

# 138. Resource Limits (--memory, --cpus)
# हिंदी में: Resource Limits (Memory और CPU की सीमा)

---

## 🔵 Simple Definition (English)
Resource limits cap how much memory, CPU and processes a container may use, enforced by Linux cgroups. Key flags: `--memory`, `--memory-swap`, `--cpus`, `--cpu-shares`, `--pids-limit`.

## 🔵 सरल परिभाषा (Hindi)
Resource limits तय करती हैं कि container कितनी memory, CPU और processes इस्तेमाल कर सकता है; Linux cgroups इन्हें लागू करते हैं। मुख्य flags: `--memory`, `--memory-swap`, `--cpus`, `--cpu-shares`, `--pids-limit`।

---

## 🔴 Problem it Solves
By default a container can use all host RAM and CPU. One Node.js memory leak or a runaway Python loop then starves Nginx, Postgres and even SSH on the same VPS, and the kernel OOM killer may kill the wrong process. Limits create a "blast radius": the misbehaving container is throttled or killed, the rest survive.

## 🔴 यह क्यों बना? (Hindi)
Default में container पूरे host की RAM और CPU ले सकता है। एक Node.js memory leak या बेकाबू Python loop उसी VPS पर Nginx, Postgres और SSH तक को भूखा कर देता है, और kernel का OOM killer गलत process मार सकता है। Limits "blast radius" बनाती हैं: खराब container throttle या kill होता है, बाकी बचे रहते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You pass --memory 512m --cpus 1.0
Step 2 → dockerd creates a cgroup for the container and writes the limits into it
Step 3 → CPU: kernel scheduler throttles the container once it uses its quota (--cpus 1.0 = 100ms per 100ms period)
Step 4 → Memory: if usage hits the limit the kernel reclaims cache/swap; if it cannot, OOM killer kills a process
Step 5 → PID 1 killed => container exits with code 137 and State.OOMKilled=true
Step 6 → Observe usage live with `docker stats`
```
CPU is "compressible" (slowdown), memory is "incompressible" (kill).

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → आप देते हैं --memory 512m --cpus 1.0
Step 2 → dockerd container के लिए cgroup बनाकर limits उसमें लिखता है
Step 3 → CPU: quota पूरा होते ही kernel scheduler throttle करता है (--cpus 1.0 = हर 100ms में 100ms)
Step 4 → Memory: limit छूने पर kernel cache/swap खाली करता है; न हो सके तो OOM killer process मारता है
Step 5 → PID 1 मरा => container exit code 137 और State.OOMKilled=true
Step 6 → `docker stats` से live usage देखें
```
CPU "compressible" है (धीमा होता है), memory "incompressible" है (kill होती है)।

---

## 🟡 Real World Example
A 2 GB t3.small EC2 hosts Nginx, a FastAPI image-resizing API and Postgres. A bad upload makes the resizer allocate 3 GB; with no limits the host swaps, SSH freezes and Postgres is OOM-killed. With `--memory 600m` on the resizer, only the resizer dies (exit 137, restart policy brings it back) and the site keeps serving. Peak hours: Black Friday style load pins one worker at 100% CPU; `--cpus 0.5` keeps it from stealing from the database.

## 🟡 Real Example Hindi mein
2 GB वाले t3.small EC2 पर Nginx, FastAPI image-resize API और Postgres हैं। एक खराब upload से resizer 3 GB माँगता है; limits न हों तो host swap करता है, SSH अटकता है और Postgres OOM-kill हो जाता है। Resizer पर `--memory 600m` हो तो सिर्फ़ resizer मरता है (exit 137, restart policy उसे वापस लाती है) और साइट चलती रहती है। भारी load में एक worker 100% CPU पकड़ ले तो `--cpus 0.5` उसे database से CPU छीनने से रोकता है।

---

## 💻 Code / Config Example — Basic
```bash
#!/usr/bin/env bash
# limits-basic.sh
docker run -d --name lim \
  --memory 256m \
  --memory-swap 256m \
  --cpus 0.5 \
  --pids-limit 200 \
  nginx:1.27-alpine
# --memory 256m       : hard RAM limit (units b,k,m,g)
# --memory-swap 256m  : total RAM+swap; equal to --memory means NO swap for this container
# --cpus 0.5          : at most half of one CPU core
# --pids-limit 200    : max processes/threads, stops fork bombs

docker stats --no-stream lim                                   # one-shot usage: MEM USAGE / LIMIT, CPU %
docker inspect -f 'mem={{.HostConfig.Memory}} cpus={{.HostConfig.NanoCpus}}' lim   # limits in bytes / nano-CPUs
docker update --memory 512m --memory-swap 512m lim             # change limits live (no restart)
docker rm -f lim                                               # cleanup

# Prove OOM kill (stress with a tiny limit)
docker run --name oom --memory 20m alpine:3.20 sh -c 'tail /dev/zero'   # tries to eat unlimited memory
docker inspect -f 'exit={{.State.ExitCode}} oom={{.State.OOMKilled}}' oom  # exit=137 oom=true
docker rm oom                                                  # cleanup
```

## 💻 Code / Config Example — Advanced
```yaml
# docker-compose.yml - limits and reservations for a 2 GB / 2 vCPU VPS (example numbers)
services:
  api:
    image: myorg/orders-api:1.4.2          # example tag
    restart: unless-stopped                # recover after OOM kill
    environment:
      NODE_OPTIONS: "--max-old-space-size=384"   # Node heap below container limit so Node GCs before OOM
    deploy:
      resources:
        limits:
          cpus: "0.75"                     # hard ceiling: 75% of one core
          memory: 512M                     # hard ceiling: exceeding it => OOM kill
          pids: 256                        # process cap
        reservations:
          cpus: "0.25"                     # guaranteed share used for scheduling
          memory: 256M                     # soft minimum (scheduling hint in Compose, enforced in Swarm)
    ulimits:
      nofile:
        soft: 8192                         # open files limit (soft)
        hard: 16384                        # open files limit (hard)

  db:
    image: postgres:16-alpine              # example tag
    restart: always                        # DB comes back after anything
    deploy:
      resources:
        limits:
          memory: 768M                     # more for DB cache; keep sum of limits below host RAM
          cpus: "1.0"                      # one core max
    oom_score_adj: -500                    # make the kernel less likely to kill the DB first
    shm_size: 128mb                        # Postgres shared memory (default 64mb is small)
```
```bash
# Compose v2 applies deploy.resources.limits with `docker compose up` (non-swarm). Verify:
docker compose up -d                                   # start stack
docker stats --no-stream                               # check MEM LIMIT column shows 512MiB / 768MiB
docker events --filter event=oom                       # watch OOM events live
free -m && docker system df                            # host memory and Docker disk usage
```

---

## 🟠 My Stack Integration
**Node.js**: V8 does not know about the cgroup limit in old versions; set `--max-old-space-size` (about 75% of the limit). Newer Node versions are cgroup-aware, but setting it explicitly is safe.
**FastAPI**: limit workers (`--workers 2`) so memory = workers x per-worker size; keep it below `--memory`.
**React/Nginx**: static Nginx needs ~64 MB; 128m is generous.
**VPS**: leave ~20% RAM for OS and Docker; sum of container limits should not exceed host RAM, add a swap file if needed.
**AWS**: ECS task definitions have `memory` (hard) and `memoryReservation` (soft), and `cpu` units; Kubernetes uses `requests` and `limits`.

```bash
# Quick sizing loop: observe, then set limits ~ 1.5x of steady-state peak
docker stats --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}'   # live table
```
**Security**: limits are a defence against denial of service and fork bombs (`--pids-limit`); combine with `--read-only`, non-root and `--cap-drop ALL`.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: No limits on production containers.
✅ Correct: always set at least `--memory`; ideally CPU and pids too.

❌ Mistake 2: Memory limit smaller than what the runtime assumes (Node heap default larger than limit).
✅ Correct: align `--max-old-space-size`/worker counts with the limit.

❌ Mistake 3: Treating CPU limit as CPU reservation.
✅ Correct: `--cpus` is a ceiling; use `--cpu-shares` (relative weight) or reservations for priority.

❌ Mistake 4: Setting `--memory-swap` smaller than `--memory`.
✅ Correct: it is total memory+swap and must be >= `--memory`; use the same value to disable swap.

❌ Mistake 5: Assuming `free -m` inside the container shows the limit.
✅ Correct: many tools read host values; check `/sys/fs/cgroup/memory.max` (cgroup v2) or `docker stats`.

---

## 🧠 Tricky Interview Question
Your container is limited to 512 MB, the app uses only 300 MB of heap, yet it is OOM killed. Why?

Answer: Container memory counts more than heap: page cache, native/off-heap buffers, thread stacks, child processes, tmpfs files (`/tmp` in RAM counts too) and memory-mapped files. A 300 MB heap can sit on top of 250 MB of other memory. Also a short spike between `docker stats` samples can hit the limit. Fix: measure RSS via cgroup stats, lower the heap cap, raise the limit, or fix leaks (buffers, unbounded caches).

---

## ⚫ Interview Questions + Answers

Q1: How does Docker enforce limits?
A1: Through Linux cgroups (control groups); Docker just writes the values.

Q2: What happens when a container exceeds its memory limit?
A2: The kernel OOM-kills a process in it; usually PID 1 dies, exit code 137, `OOMKilled=true`.

Q3: What happens when it exceeds its CPU limit?
A3: It is throttled (slowed), not killed.

Q4: `--memory` vs `--memory-reservation`?
A4: `--memory` is the hard limit; `--memory-reservation` is a soft limit that applies under memory pressure.

Q5: What does `--cpus 1.5` mean?
A5: The container may use up to 1.5 CPU cores worth of time in total.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any shared host or production VPS.
- Multi-tenant or untrusted workloads (CI runners).

❌ Avoid when:
- Guessing numbers blindly: measure first; too tight limits cause random OOM kills and throttled latency.

---

## 📊 Visual Diagram
```
 Host: 2 GB RAM, 2 vCPU
 +----------------------------------------------------+
 | OS + Docker (~300MB)                               |
 | +------------+ +------------+ +------------------+ |
 | | nginx      | | api        | | db               | |
 | | mem 128m   | | mem 512m   | | mem 768m         | |
 | | cpus 0.25  | | cpus 0.75  | | cpus 1.0         | |
 | +------------+ +------------+ +------------------+ |
 +----------------------------------------------------+
  api leaks -> hits 512m -> kernel OOM kills api only -> restart policy revives it
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| cgroup | Kernel feature limiting resources | Resources सीमित करने वाला kernel feature |
| OOM killer | Kernel kills process when out of memory | Memory ख़त्म होने पर process मारता है |
| Throttling | Slowing a process on CPU cap | CPU सीमा पर धीमा करना |
| Reservation | Soft/guaranteed minimum | नरम न्यूनतम सीमा |
| pids-limit | Max processes in container | Processes की अधिकतम संख्या |

---

## ⚡ 3-Line Summary
English: Limits use cgroups: `--memory` kills on excess, `--cpus` throttles.
Always set them on shared hosts and size them from `docker stats` measurements.
Align runtime settings (Node heap, worker counts) with the limit.

Hindi: Limits cgroups से लागू होती हैं: `--memory` ज़्यादा होने पर kill करता है, `--cpus` throttle।
Shared hosts पर हमेशा लगाएँ और `docker stats` की माप से तय करें।
Runtime settings (Node heap, workers) को limit के हिसाब से रखें।

---

## ➡️ Next Topic
**139. Container Logging**: when a limit kills your app, the logs are how you find out why; next we see where container logs go.
