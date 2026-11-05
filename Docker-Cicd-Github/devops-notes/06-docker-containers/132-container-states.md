---

# 132. Container States
# हिंदी में: Container की अवस्थाएँ (States)

---

## 🔵 Simple Definition (English)
A container state is the status Docker reports for a container right now: **created, running, paused, restarting, exited, removing, dead**. You read it with `docker ps -a` or `docker inspect`, and it tells you whether the process is alive, frozen, crashed, or finished.

## 🔵 सरल परिभाषा (Hindi)
Container state वह status है जो Docker अभी container के बारे में बताता है: **created, running, paused, restarting, exited, removing, dead**। इसे `docker ps -a` या `docker inspect` से पढ़ते हैं, और यह बताता है कि process ज़िंदा है, freeze है, crash हुआ या पूरा हो गया।

---

## 🔴 Problem it Solves
When a deployment "does not work", the first question is: is the container running, crash-looping, or never started? Without clear states you would guess from logs. States give a fast, scriptable truth: `Exited (137)` means killed (often OOM), `Restarting` means a crash loop, `Created` means it never started. Monitoring and health scripts depend on them.

## 🔴 यह क्यों बना? (Hindi)
Deployment "काम नहीं कर रहा" तो पहला सवाल: container running है, crash-loop में है, या कभी start ही नहीं हुआ? States के बिना logs से अंदाज़ा लगाना पड़ता। States तेज़ और scriptable सच देते हैं: `Exited (137)` मतलब kill (अक्सर OOM), `Restarting` मतलब crash loop, `Created` मतलब कभी start नहीं हुआ। Monitoring scripts इन्हीं पर चलती हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Docker daemon (dockerd) stores a state machine per container in its metadata
Step 2 → create        => "created"    (config + layer exist, no process)
Step 3 → start         => "running"    (PID 1 alive)
Step 4 → pause         => "paused"     (cgroup freezer, process alive but frozen)
Step 5 → process exits => "exited"     (exit code saved: 0 ok, non-zero failure)
Step 6 → restart policy kicks in => "restarting" -> "running"
Step 7 → docker rm in progress => "removing"; broken removal => "dead"
```
Read it: `docker inspect -f '{{.State.Status}}' NAME` and details with `{{json .State}}`.

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → dockerd हर container की state machine metadata में रखता है
Step 2 → create        => "created"    (config + layer हैं, process नहीं)
Step 3 → start         => "running"    (PID 1 ज़िंदा)
Step 4 → pause         => "paused"     (cgroup freezer, process है पर freeze)
Step 5 → process exit  => "exited"     (exit code सेव: 0 सही, non-zero failure)
Step 6 → restart policy => "restarting" -> "running"
Step 7 → docker rm चल रहा => "removing"; remove फेल हुआ => "dead"
```
पढ़ने के लिए: `docker inspect -f '{{.State.Status}}' NAME`, पूरी detail के लिए `{{json .State}}`।

---

## 🟡 Real World Example
Zomato-style checkout service on a VPS: after a release, `docker ps -a` shows `Restarting (1) 5 seconds ago`. State = restarting + exit code 1 = app crashes at boot (wrong DB URL env). Another day it shows `Exited (137)` with `OOMKilled: true` in inspect, meaning the memory limit was too low for a traffic spike. Same tool, two different root causes, found in seconds by reading state and exit code.

## 🟡 Real Example Hindi mein
VPS पर Zomato जैसी checkout service: release के बाद `docker ps -a` में `Restarting (1) 5 seconds ago`। State = restarting + exit code 1 = app boot पर crash (गलत DB URL env)। दूसरे दिन `Exited (137)` और inspect में `OOMKilled: true`, मतलब traffic spike में memory limit कम पड़ी। एक ही tool, दो अलग कारण, state और exit code पढ़कर सेकंडों में मिल गए।

---

## 💻 Code / Config Example — Basic
```bash
#!/usr/bin/env bash
# states-basic.sh - see each state with a real container
docker run -d --name web nginx:1.27-alpine             # running state (example tag)
docker ps                                              # only running containers
docker ps -a                                           # ALL containers incl. exited/created
docker ps -a --filter status=exited                    # only exited ones
docker ps -a --filter status=restarting                # only crash-looping ones
docker inspect -f '{{.State.Status}}' web              # prints: running
docker pause web                                       # freeze it
docker inspect -f '{{.State.Status}} paused={{.State.Paused}}' web   # paused
docker unpause web                                     # back to running
docker stop web                                        # becomes exited
docker inspect -f '{{.State.ExitCode}}' web            # 0 = graceful, 137 = SIGKILL, 143 = SIGTERM unhandled by shell
docker rm web                                          # removed - no state anymore
```

## 💻 Code / Config Example — Advanced
```bash
#!/usr/bin/env bash
# container-state-report.sh - cron-friendly health report for a VPS
set -euo pipefail                                      # fail fast on errors

for name in $(docker ps -a --format '{{.Names}}'); do  # loop over every container name
  # one inspect call gives several fields separated by | for easy parsing
  info=$(docker inspect -f \
    '{{.State.Status}}|{{.State.ExitCode}}|{{.State.OOMKilled}}|{{.RestartCount}}|{{.State.StartedAt}}' "$name")
  IFS='|' read -r status code oom restarts started <<< "$info"   # split into variables
  echo "$name status=$status exit=$code oom=$oom restarts=$restarts since=$started"
  if [[ "$status" == "restarting" || "$oom" == "true" ]]; then   # alert conditions
    echo "ALERT: $name needs attention" >&2                      # send to stderr (cron mails it)
  fi
done
```
```bash
# Useful filters and formats
docker ps -a --format 'table {{.Names}}\t{{.Status}}\t{{.Image}}'   # tidy table
docker ps -a -f 'exited=1'                                           # exited with exit code 1
docker events --filter 'event=die' --filter 'event=oom'              # live stream of crashes/OOM
```

---

## 🟠 My Stack Integration
**Node.js**: uncaught exception -> exit code 1 -> `Exited (1)` or `Restarting`. Read `docker logs --tail 50` next.
**FastAPI**: a bad import or missing env makes uvicorn exit immediately with code 1 or 3 (state flips to restarting under `restart: always`).
**React**: Nginx container with a wrong config exits with code 1 right after start; `docker run --rm nginx -t` style checks catch it earlier.
**VPS/AWS**: put the report script above in cron and forward to email/Slack; on AWS the same data appears as ECS task `lastStatus`/`stoppedReason`.

```yaml
# docker-compose.yml - observe states with healthchecks too
services:
  api:
    image: myorg/orders-api:1.4.2        # example pinned tag
    restart: unless-stopped              # state flows exited -> restarting -> running
    healthcheck:                         # adds "(healthy)/(unhealthy)" to the Status column
      test: ["CMD", "node", "-e", "fetch('http://localhost:3000/health').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"]
      interval: 15s                      # check every 15 seconds
      timeout: 3s                        # a check slower than 3s counts as failed
      retries: 3                         # 3 failures in a row => unhealthy
```
(`fetch` needs Node 18+.) **Security**: a container that keeps restarting may be under attack or compromised; alert on restart counts, not only on "down".

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using only `docker ps` and concluding "container is gone".
✅ Correct: `docker ps` hides stopped ones. Use `docker ps -a`.

❌ Mistake 2: Ignoring the exit code.
✅ Correct: 0 = normal, 1 = app error, 125/126/127 = docker/command problems, 137 = SIGKILL/OOM, 143 = SIGTERM.

❌ Mistake 3: Assuming "Up" means healthy.
✅ Correct: running only means PID 1 is alive. Add a HEALTHCHECK to see `healthy`.

❌ Mistake 4: Restarting a crash-looping container blindly.
✅ Correct: read `docker logs` and `inspect` (`OOMKilled`, `Error`) first, then fix the cause.

---

## 🧠 Tricky Interview Question
A container shows `Up 3 minutes` but users get 502 from Nginx. Is the state wrong?

Answer: The state is correct but incomplete. "running" only means PID 1 exists. The app inside may be deadlocked, still booting, or listening on 127.0.0.1 inside the container instead of 0.0.0.0. A HEALTHCHECK distinguishes running from healthy, and you debug with `docker exec`/`docker logs`.

---

## ⚫ Interview Questions + Answers

Q1: List the container states.
A1: created, running, paused, restarting, exited, removing, dead.

Q2: What is the difference between `exited` and `dead`?
A2: Exited = process ended normally or crashed and the container can be started again. Dead = Docker failed to remove it fully (for example a busy mount); it cannot be restarted, only removed.

Q3: What does exit code 137 mean?
A3: 128 + 9, the process got SIGKILL, commonly from `docker kill`, stop timeout, or the kernel OOM killer. Check `.State.OOMKilled`.

Q4: How do you list only crash-looping containers?
A4: `docker ps -a --filter status=restarting`.

Q5: How do you get a container's state in a script?
A5: `docker inspect -f '{{.State.Status}}' NAME`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Writing monitoring/cron checks and CI smoke tests.
- Triaging a failed deploy quickly.
- Building alerts on restart count and OOM.

❌ Avoid when:
- You need app-level health: state alone is not enough, add healthchecks and real metrics (Prometheus).

---

## 📊 Visual Diagram
```
 create --> [created] --start--> [running] --pause--> [paused]
                                   |  ^                  |
                          exit/crash|  |restart policy    | unpause
                                   v  |                  v
                              [exited]-->[restarting]  [running]
                                   |
                              docker rm
                                   v
                    [removing] --(failure)--> [dead]
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| State | Current status of container | अभी की अवस्था |
| Exit code | Number returned when process ends | Process ख़त्म होने पर नंबर |
| OOMKilled | Killed for exceeding memory | Memory ज़्यादा होने पर kill |
| Crash loop | Repeated start-fail-restart | बार-बार crash और restart |
| Healthy | HEALTHCHECK passing | Health check पास |

---

## ⚡ 3-Line Summary
English: Containers move through created, running, paused, restarting, exited, removing, dead.
Always read state together with exit code and OOMKilled.
Running does not mean healthy; add a healthcheck.

Hindi: Container created, running, paused, restarting, exited, removing, dead states से गुज़रता है।
State को हमेशा exit code और OOMKilled के साथ पढ़ें।
Running का मतलब healthy नहीं; healthcheck जोड़ें।

---

## ➡️ Next Topic
**133. docker run Flags (-d, -p, -v, -e, --name, --network)**: states are the output, `docker run` flags are the input that shape how the container starts.
