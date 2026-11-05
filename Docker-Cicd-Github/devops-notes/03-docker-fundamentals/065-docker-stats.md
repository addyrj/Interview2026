---

# 065. docker stats
# हिंदी में: docker stats

---

## 🔵 Simple Definition (English)
`docker stats` shows a **live stream** of resource usage for running containers: CPU %, memory usage / limit, memory %, network I/O, block I/O and number of processes (PIDs). Use `--no-stream` for a single snapshot and `--format` for custom output.

## 🔵 सरल परिभाषा (Hindi)
`docker stats` चल रहे containers के resource usage की **live stream** दिखाता है: CPU %, memory usage / limit, memory %, network I/O, block I/O और processes (PIDs) की संख्या। एक snapshot के लिए `--no-stream` और custom output के लिए `--format` इस्तेमाल करें।

---

## 🔴 Problem it Solves
A VPS has limited CPU and RAM shared by all containers. One leaking or busy container can starve the others or get OOM-killed. Without numbers you guess. `docker stats` gives per-container usage instantly, with no extra tooling, so you can find the noisy neighbour and size memory limits correctly.

## 🔴 यह क्यों बना? (Hindi)
VPS की CPU और RAM सीमित होती है और सब containers में बँटती है। एक leak करने वाला या busy container दूसरों को भूखा रख सकता है या OOM-kill हो सकता है। Numbers के बिना आप अंदाज़ा लगाते हैं। `docker stats` बिना किसी अतिरिक्त tool के हर container का usage तुरंत दिखाता है, ताकि आप शोर करने वाले पड़ोसी को पहचानें और memory limits सही रखें।

---

## 🟢 How it Works — Step by Step

```
Step 1 → CLI opens a streaming call to the daemon: GET /containers/{id}/stats for each running container
Step 2 → Daemon reads cgroup counters from the Linux kernel (cpuacct, memory, blkio, pids) and network counters
Step 3 → Every ~1-2 seconds it sends a new sample; CLI computes CPU % from the delta between samples
Step 4 → CLI refreshes the table in place (like top); Ctrl+C exits
Step 5 → --no-stream prints one sample and exits (good for scripts); --format uses Go templates
Step 6 → You compare MEM USAGE against LIMIT: near 100% means OOM-kill risk (exit 137)
```

Columns:
- `CPU %`: 100% = one full core; on a 2-core VPS the maximum is 200%.
- `MEM USAGE / LIMIT`: container memory (without page cache in recent Docker) against its limit (host RAM if none set).
- `NET I/O`, `BLOCK I/O`: cumulative bytes since start. `PIDS`: process/thread count.

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → CLI daemon से streaming call खोलता है: हर चलते container के लिए GET /containers/{id}/stats
Step 2 → Daemon Linux kernel से cgroup counters (cpuacct, memory, blkio, pids) और network counters पढ़ता है
Step 3 → हर ~1-2 सेकंड में नया sample आता है; CLI दो samples के अंतर से CPU % निकालता है
Step 4 → CLI table को वहीं refresh करता है (top जैसा); Ctrl+C से बाहर
Step 5 → --no-stream एक sample print करके बाहर आता है (scripts के लिए अच्छा); --format Go templates लेता है
Step 6 → MEM USAGE की तुलना LIMIT से करें: 100% के पास मतलब OOM-kill का खतरा (exit 137)
```

Columns:
- `CPU %`: 100% = एक पूरा core; 2-core VPS पर अधिकतम 200%।
- `MEM USAGE / LIMIT`: container की memory (नए Docker में page cache के बिना) और उसकी limit (limit न हो तो host RAM)।
- `NET I/O`, `BLOCK I/O`: शुरू से अब तक के कुल bytes। `PIDS`: process/thread संख्या।

---

## 🟡 Real World Example
On a 2 GB VPS the site slows down every evening. `docker stats --no-stream` shows `api 2.3%  1.2GiB / 1.9GiB (63%)` and climbing over days, while `db` stays at 300 MB. The API leaks memory (an unbounded in-memory cache). You set `mem_limit: 768m` plus `restart: unless-stopped` as a short-term safety net, then fix the leak. At Zomato scale the same signals come from cAdvisor/Prometheus, but on a single VPS `docker stats` is the fastest first check.

## 🟡 Real Example Hindi mein
2 GB VPS पर हर शाम site धीमी हो जाती है। `docker stats --no-stream` दिखाता है `api 2.3%  1.2GiB / 1.9GiB (63%)` जो कई दिनों में बढ़ रहा है, जबकि `db` 300 MB पर है। API में memory leak है (असीमित in-memory cache)। आप तात्कालिक सुरक्षा के लिए `mem_limit: 768m` और `restart: unless-stopped` लगाते हैं, फिर leak ठीक करते हैं। Zomato जैसे scale पर यही संकेत cAdvisor/Prometheus से आते हैं, पर single VPS पर `docker stats` सबसे तेज़ पहला check है।

---

## 💻 Code / Config Example — Basic

```bash
# --- docker stats basics ---
docker stats                                     # live table for all running containers (Ctrl+C to quit)
docker stats api db                              # only these containers
docker stats --no-stream                         # one snapshot, then exit
docker stats --no-stream --no-trunc              # full container IDs
docker stats -a                                  # include stopped containers (they show zeros)
docker stats --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}'   # chosen columns
docker stats --no-stream --format '{{.Name}} {{.MemPerc}}'   # script-friendly lines
docker system df                                 # disk usage (stats does not show disk space)
docker top api                                   # processes inside a container (companion command)
```

## 💻 Code / Config Example — Advanced

```bash
#!/usr/bin/env bash
# stats-alert.sh - warn when any container uses too much memory/CPU; run from cron every minute
# Cron: * * * * * /srv/scripts/stats-alert.sh >> /var/log/stats-alert.log 2>&1
set -euo pipefail                                # strict shell mode

MEM_LIMIT_PCT=85                                 # alert above 85% of the container limit
CPU_LIMIT_PCT=150                                # alert above 150% (1.5 cores)
WEBHOOK_URL="${ALERT_WEBHOOK_URL:-}"             # Slack/Discord webhook from environment (never hard-code)

docker stats --no-stream --format '{{.Name}} {{.CPUPerc}} {{.MemPerc}}' | while read -r name cpu mem; do
  cpu_n=${cpu%\%}                                # strip the % sign from CPU value
  mem_n=${mem%\%}                                # strip the % sign from memory value
  cpu_i=${cpu_n%.*}                              # integer part (bash has no floats)
  mem_i=${mem_n%.*}                              # integer part
  if [ "${mem_i:-0}" -ge "$MEM_LIMIT_PCT" ] || [ "${cpu_i:-0}" -ge "$CPU_LIMIT_PCT" ]; then
    msg="ALERT $(hostname): $name cpu=${cpu} mem=${mem}"   # build message
    echo "$msg"                                  # log it
    if [ -n "$WEBHOOK_URL" ]; then               # post to webhook if configured
      curl -fsS -X POST -H 'Content-Type: application/json' \
        -d "{\"text\":\"$msg\"}" "$WEBHOOK_URL" || true   # Slack-style payload; ignore failures
    fi
  fi
done
```

```yaml
# docker-compose.yml - set limits so docker stats percentages are meaningful, plus cAdvisor for history
services:
  api:
    build: ./api                                 # FastAPI image
    restart: unless-stopped                      # restart if OOM-killed
    mem_limit: 512m                              # hard memory limit (stats MEM % is relative to this)
    cpus: 1.0                                    # at most 1 CPU core
    pids_limit: 200                              # protect against fork bombs
  cadvisor:
    image: gcr.io/cadvisor/cadvisor:v0.49.1      # example tag, check the latest release
    restart: unless-stopped                      # keep collecting
    ports:
      - "127.0.0.1:8081:8080"                    # UI/metrics only on localhost (use Nginx auth or SSH tunnel)
    volumes:
      - /:/rootfs:ro                             # read-only host views cAdvisor needs
      - /var/run:/var/run:ro                     # docker socket path (read-only)
      - /sys:/sys:ro                             # kernel cgroup stats
      - /var/lib/docker/:/var/lib/docker:ro      # container metadata
    mem_limit: 256m                              # keep the monitor small
```

---

## 🟠 My Stack Integration
- **FastAPI**: watch MEM growth over hours; Gunicorn/Uvicorn worker count multiplies memory use.
- **Node.js**: heap grows until limit; set `--max-old-space-size` below the container `mem_limit` (e.g. 384 for a 512m limit).
- **Nginx**: usually low CPU/MEM; high PIDS/NET means traffic spike or attack.
- **PostgreSQL**: memory depends on `shared_buffers`; check it is not competing with the API on a small VPS.
- **VPS/AWS**: `docker stats` for a quick check; for history and alerts use Prometheus + cAdvisor + Grafana, or CloudWatch Container Insights on ECS. On EC2 install the CloudWatch agent for host memory metrics (not published by default).

```yaml
# .github/workflows/stats.yml - capture a resource snapshot after deploy (useful in release notes)
name: stats                                      # workflow name
on:
  workflow_dispatch:                             # manual trigger
jobs:
  snapshot:
    runs-on: ubuntu-latest                       # runner
    steps:
      - name: Stats from VPS                     # SSH and collect
        uses: appleboy/ssh-action@v1.0.3         # example version
        with:
          host: ${{ secrets.VPS_HOST }}          # VPS address
          username: deploy                       # docker user
          key: ${{ secrets.VPS_SSH_KEY }}        # key from secrets
          script: |                              # runs on VPS
            docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}'
```

Security: unexpected CPU spikes in a container (for example 400% on an idle app) are a classic sign of cryptomining malware after a compromised image or exposed Docker API. Watch stats, keep Docker TCP closed, limit resources (`mem_limit`, `cpus`, `pids_limit`) to contain damage, and never expose cAdvisor publicly since it leaks container metadata.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Reading MEM % without setting a limit; it is relative to total host RAM, so "10%" may still be a leak.
✅ Correct: Set `mem_limit` so the percentage reflects the container's budget.

❌ Mistake 2: Assuming CPU % is capped at 100%.
✅ Correct: It is per core; 200% on a 2-core host is fully used.

❌ Mistake 3: Using `docker stats` output as long-term monitoring.
✅ Correct: It has no history; use Prometheus/Grafana or CloudWatch.

❌ Mistake 4: Running plain `docker stats` in a script (it never exits).
✅ Correct: `docker stats --no-stream`.

❌ Mistake 5: Confusing container memory with host free memory.
✅ Correct: Check both `docker stats` and `free -h` on the host (plus swap).

---

## 🧠 Tricky Interview Question
`docker stats` shows your container at 480 MiB / 512 MiB, but the app's own memory profiler says it uses only 300 MiB. Is the container about to be OOM-killed?

Answer: Not necessarily. The cgroup counter can include **page cache** and kernel memory (older Docker versions include cache in usage; newer CLIs subtract inactive file cache), which the kernel reclaims under pressure before invoking the OOM killer. Check `docker inspect -f '{{.State.OOMKilled}}'` over time and `/sys/fs/cgroup/memory.stat` (`anon` vs `file`). The real risk is when anonymous (process) memory approaches the limit. Also processes besides the app (shell, workers, tmpfs data counted as memory) add to usage.

---

## ⚫ Interview Questions + Answers

Q1: What metrics does `docker stats` show?
A1: CPU %, memory usage/limit and %, network I/O, block I/O, and PIDs, per running container.

Q2: How is it different from `top`/`htop` on the host?
A2: `stats` aggregates by container through cgroups; `top` shows individual processes (container processes appear as host processes with host PIDs).

Q3: What happens if a container exceeds its memory limit?
A3: The kernel OOM killer terminates a process in it (usually the main one), the container exits with code 137, `OOMKilled=true`, and the restart policy may restart it.

Q4: How do you limit CPU and memory?
A4: `docker run --memory 512m --cpus 1.0` or Compose `mem_limit` / `cpus` (or `deploy.resources.limits`, supported by Compose v2).

Q5: What do you use for long-term container metrics?
A5: cAdvisor + Prometheus + Grafana, Docker's metrics endpoint, Datadog, or CloudWatch Container Insights on AWS.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Quick live check of which container is eating CPU/RAM, sizing limits, post-deploy sanity check.

❌ Avoid when:
- You need history, alerts or per-request tracing: use proper monitoring (Prometheus/Grafana, APM).
- You need disk usage: use `docker system df` and `du`.

---

## 📊 Visual Diagram
```
 Linux kernel cgroups  (one group per container)
   cpu: ####....  memory: #####.. (400M/512M)  pids: 12   net: rx/tx   blkio: r/w
        |
        v  read every ~1-2 s
   dockerd (stats API)
        |
        v  docker stats
 NAME   CPU %   MEM USAGE / LIMIT    MEM %   NET I/O        BLOCK I/O   PIDS
 api    2.3%    400MiB / 512MiB      78.1%   12MB / 8MB     0B / 4MB    12
 db     0.8%    300MiB / 1.9GiB      15.4%   3MB / 5MB      20MB / 80MB 9
 nginx  0.1%    8MiB / 1.9GiB        0.4%    30MB / 40MB    0B / 0B     3
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| cgroup | Kernel feature limiting/measuring resources | Resources सीमित/मापने वाला kernel feature |
| CPU % | Usage relative to one core | एक core के मुकाबले usage |
| Memory limit | Maximum RAM for a container | Container की अधिकतम RAM |
| OOM killer | Kernel kills process over memory | Memory सीमा पार पर kernel process मारता है |
| PIDs | Number of processes/threads | Processes/threads की संख्या |
| cAdvisor | Container metrics exporter | Container metrics exporter |

---

## ⚡ 3-Line Summary
English: `docker stats` shows live CPU, memory, network, disk I/O and PIDs per container.
Set memory/CPU limits so percentages mean something, and use `--no-stream` in scripts.
For history and alerts use Prometheus, Grafana or CloudWatch.
Hindi: `docker stats` हर container की live CPU, memory, network, disk I/O और PIDs दिखाता है।
Memory/CPU limits सेट करें ताकि percentages का मतलब हो, और scripts में `--no-stream` इस्तेमाल करें।
History और alerts के लिए Prometheus, Grafana या CloudWatch इस्तेमाल करें।

---

## ➡️ Next Topic
**066. docker pull + docker push.** Now that you can run and observe containers, learn how images move to and from registries.

---
