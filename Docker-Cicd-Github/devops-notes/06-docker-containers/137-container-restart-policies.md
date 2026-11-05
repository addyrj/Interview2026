---

# 137. Container Restart Policies
# हिंदी में: Container Restart Policies

---

## 🔵 Simple Definition (English)
A restart policy tells Docker what to do when a container exits or the Docker daemon/host restarts: `no`, `on-failure[:max]`, `always`, or `unless-stopped`. It is Docker's built-in self-healing for single-host setups.

## 🔵 सरल परिभाषा (Hindi)
Restart policy Docker को बताती है कि container exit होने या Docker daemon/host restart होने पर क्या करना है: `no`, `on-failure[:max]`, `always`, या `unless-stopped`। यह single-host setups के लिए Docker की built-in self-healing है।

---

## 🔴 Problem it Solves
At 3 AM your Node.js app hits an unhandled exception, or the EC2 instance reboots for maintenance. Without a policy the container stays down until a human notices. Restart policies bring services back automatically, and with back-off they avoid hammering a broken service.

## 🔴 यह क्यों बना? (Hindi)
रात 3 बजे आपकी Node.js app में unhandled exception आता है, या EC2 maintenance के लिए reboot होता है। Policy न हो तो container तब तक बंद रहता है जब तक कोई इंसान नोटिस न करे। Restart policies service को अपने-आप वापस लाती हैं, और back-off के साथ टूटी service पर बार-बार हमला भी नहीं करतीं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You set:  --restart unless-stopped   (or Compose restart:)
Step 2 → PID 1 exits (crash, OOM kill, exit 0) or the host reboots and dockerd starts again
Step 3 → dockerd checks the policy:
           no             -> do nothing
           on-failure[:N] -> restart only if exit code != 0 (max N times)
           always         -> restart whatever happened (even after manual stop, when daemon restarts)
           unless-stopped -> like always, but NOT if you manually stopped it before
Step 4 → Delay doubles each time: 100ms, 200ms, 400ms ... up to 1 minute (back-off)
Step 5 → Container is considered successfully started after running 10 seconds; back-off resets
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → आप सेट करते हैं:  --restart unless-stopped   (या Compose में restart:)
Step 2 → PID 1 exit होता है (crash, OOM, exit 0) या host reboot होकर dockerd फिर शुरू होता है
Step 3 → dockerd policy देखता है:
           no             -> कुछ नहीं
           on-failure[:N] -> सिर्फ़ exit code != 0 पर restart (अधिकतम N बार)
           always         -> कुछ भी हुआ हो restart (manual stop के बाद भी daemon restart पर)
           unless-stopped -> always जैसा, पर अगर आपने manually stop किया तो नहीं
Step 4 → देरी हर बार दोगुनी: 100ms, 200ms, 400ms ... अधिकतम 1 मिनट (back-off)
Step 5 → 10 सेकंड चलने पर successful माना जाता है; back-off reset
```

---

## 🟡 Real World Example
A Swiggy-style delivery-tracking API runs on one EC2 VPS with `unless-stopped`. A memory leak causes an OOM kill at 2 AM; Docker restarts the container within a second and users barely notice. Later, ops stop the service for maintenance with `docker stop`; after the planned reboot, it stays stopped (as intended), while the always-on Postgres container comes back. A one-off DB migration container uses `on-failure:3`, retrying three times then giving up so the pipeline fails loudly.

## 🟡 Real Example Hindi mein
Swiggy जैसी delivery-tracking API एक EC2 VPS पर `unless-stopped` से चलती है। Memory leak से रात 2 बजे OOM kill होता है; Docker एक सेकंड में restart कर देता है और users को लगभग पता नहीं चलता। बाद में ops maintenance के लिए `docker stop` करते हैं; planned reboot के बाद वह बंद ही रहता है (जैसा चाहा), जबकि हमेशा चालू रहने वाला Postgres वापस आ जाता है। One-off DB migration container `on-failure:3` से तीन बार retry करके हार मानता है ताकि pipeline साफ़ fail हो।

---

## 💻 Code / Config Example — Basic
```bash
#!/usr/bin/env bash
# restart-basic.sh
docker run -d --name r-no   --restart no             alpine:3.20 sh -c 'sleep 2; exit 1'   # never restarted (default)
docker run -d --name r-fail --restart on-failure:3   alpine:3.20 sh -c 'sleep 2; exit 1'   # retried max 3 times, then stays Exited
docker run -d --name r-alw  --restart always         alpine:3.20 sh -c 'sleep 2; exit 0'   # restarted even on exit 0
docker run -d --name r-uns  --restart unless-stopped alpine:3.20 sh -c 'sleep 2; exit 1'   # restarted, except after manual stop

sleep 15                                                                  # give time for a few restart cycles
docker inspect -f '{{.Name}} restarts={{.RestartCount}} state={{.State.Status}}' r-no r-fail r-alw r-uns   # compare counts
docker update --restart unless-stopped r-no              # change policy of an existing container, no recreate
docker rm -f r-no r-fail r-alw r-uns                     # cleanup
```

## 💻 Code / Config Example — Advanced
```yaml
# docker-compose.yml - restart policies per role (example stack)
services:
  api:
    image: myorg/orders-api:1.4.2          # example pinned tag
    restart: unless-stopped                # long-running service: always come back, respect manual stop
    init: true                             # proper signal handling for clean stops
    stop_grace_period: 30s                 # allow graceful shutdown on stop
    healthcheck:
      test: ["CMD", "node", "-e", "fetch('http://localhost:3000/health').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"]
      interval: 15s                        # check every 15s (Node 18+ for fetch)
      timeout: 3s                          # slow check = failure
      retries: 3                           # 3 failures => unhealthy
    deploy:
      resources:
        limits:
          memory: 512M                     # cap memory so a leak OOMs THIS container, not the host

  migrate:
    image: myorg/orders-api:1.4.2          # same image, different command
    command: ["node", "scripts/migrate.js"]   # one-off job (example script path)
    restart: "no"                          # QUOTED "no": unquoted no becomes boolean false in YAML!
    depends_on:
      db:
        condition: service_healthy         # wait for DB readiness

  db:
    image: postgres:16-alpine              # example tag
    restart: always                        # database should return after any daemon restart
    volumes:
      - pgdata:/var/lib/postgresql/data    # persistent data survives restarts
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]   # readiness check
      interval: 5s                         # frequent early checks
      retries: 10                          # tolerate slow boot

volumes:
  pgdata: {}                               # named volume
```
```bash
# Make sure containers return after host reboot
sudo systemctl enable docker                 # start dockerd at boot (on systemd distros)
docker inspect -f '{{.HostConfig.RestartPolicy.Name}}' orders-api   # verify policy
```
Note: restart policies do not restart a container because it is `unhealthy`; healthcheck only marks it. Use an orchestrator or autoheal tool for that.

---

## 🟠 My Stack Integration
**Node.js**: policy handles crashes, but also fix the cause; crash on startup + `always` = silent crash loop. Handle `unhandledRejection` to log and exit.
**FastAPI**: uvicorn/gunicorn with `unless-stopped`; use gunicorn workers for in-process worker restarts.
**React/Nginx**: static Nginx rarely crashes; `unless-stopped` is enough.
**VPS**: `systemctl enable docker` plus `unless-stopped` gives "survives reboot" behaviour without writing systemd units. **AWS**: ECS service scheduler replaces failed tasks (like `always`); Kubernetes `restartPolicy` + liveness probes do the same with probe-based restarts.

```yaml
# GitHub Actions deploy step using a restart policy (example)
- name: Deploy container
  run: |
    ssh deploy@${{ secrets.VPS_HOST }} '
      docker pull myorg/orders-api:${{ github.sha }} &&
      docker rm -f orders-api || true &&
      docker run -d --name orders-api --restart unless-stopped -p 127.0.0.1:3000:3000 myorg/orders-api:${{ github.sha }}
    '
```
**Security**: auto-restart can mask an exploited, crashing process; alert on `RestartCount` and keep `--read-only`, non-root user, and limits so a restart does not give attackers a fresh foothold with more rights.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `restart: no` unquoted in Compose.
✅ Correct: write `restart: "no"`; unquoted `no` is YAML boolean false.

❌ Mistake 2: Using `always` and expecting `docker stop` to survive a daemon restart.
✅ Correct: with `always`, a stopped container starts again when the daemon restarts. Use `unless-stopped` to respect manual stops.

❌ Mistake 3: Believing `unhealthy` triggers a restart.
✅ Correct: plain Docker only reports it. Use Swarm/Kubernetes or a watcher.

❌ Mistake 4: Letting a crash-looping container run forever unnoticed.
✅ Correct: monitor `RestartCount` and `docker events`; use `on-failure:5` for jobs.

❌ Mistake 5: Forgetting to enable the Docker service at boot.
✅ Correct: `systemctl enable docker`.

---

## 🧠 Tricky Interview Question
You run `docker stop web` on a container with `--restart always`, then reboot the server. Does `web` come back? And with `unless-stopped`?

Answer: With `always`, yes, it starts again after the daemon starts (manual stop is forgotten on daemon restart). With `unless-stopped`, no, because you explicitly stopped it. (Note: while the daemon keeps running, a manually stopped container is not restarted under either policy.)

---

## ⚫ Interview Questions + Answers

Q1: List the restart policies.
A1: `no` (default), `on-failure[:max-retries]`, `always`, `unless-stopped`.

Q2: Which policy for a production API on one VPS?
A2: `unless-stopped`, since it recovers from crashes and reboots while honouring deliberate stops.

Q3: What is the restart back-off?
A3: Delay starts at 100ms and doubles up to 1 minute; it resets after the container runs for 10 seconds.

Q4: Can you change a policy without recreating the container?
A4: Yes: `docker update --restart=unless-stopped NAME`.

Q5: Does `on-failure` restart on exit code 0?
A5: No, only for non-zero exits (and daemon restarts do not restart it if it exited cleanly).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Single-host production services (API, DB, Nginx).
- Cheap self-healing without an orchestrator.

❌ Avoid when:
- One-off jobs and migrations (`no` or `on-failure:N`).
- Multi-node HA: use Kubernetes/ECS with health-based replacement.

---

## 📊 Visual Diagram
```
 process exits / host reboots
          |
   +------v------+   no             -> stay Exited
   | policy ?    |   on-failure     -> code!=0 ? restart : stay
   +------+------+   always         -> restart
          |          unless-stopped -> manually stopped ? stay : restart
          v
   wait 100ms,200ms,400ms ... 1min  (back-off)
          |
          v
      [running] --(runs 10s)--> back-off reset
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Restart policy | Auto-restart rule | अपने-आप restart का नियम |
| Back-off | Growing delay between retries | बढ़ती हुई देरी |
| Crash loop | Repeated crash and restart | बार-बार crash |
| RestartCount | Number of restarts so far | अब तक restarts की गिनती |
| Self-healing | System recovers automatically | अपने-आप ठीक होना |

---

## ⚡ 3-Line Summary
English: Restart policies auto-recover containers: no, on-failure, always, unless-stopped.
Use `unless-stopped` for long-running services and `on-failure:N` or `no` for jobs.
They do not act on unhealthy status; monitor restart counts.

Hindi: Restart policies containers को अपने-आप वापस लाती हैं: no, on-failure, always, unless-stopped।
लंबे चलने वाले services के लिए `unless-stopped`, jobs के लिए `on-failure:N` या `no`।
ये unhealthy status पर काम नहीं करतीं; restart counts monitor करें।

---

## ➡️ Next Topic
**138. Resource Limits (--memory, --cpus)**: auto-restart plus a memory leak equals a loop; limits keep one bad container from taking the whole host down.
