---

# 144. Container Debugging
# हिंदी में: Container Debugging (Container में गड़बड़ी ढूँढना)

---

## 🔵 Simple Definition (English)
Container debugging is the habit of finding **why a container is crashing, restarting, slow, or unreachable**. You use a fixed order of tools: `docker ps -a`, `docker logs`, `docker inspect`, `docker exec`, `docker events`, `docker stats`, and a "debug container" that shares the broken container's namespaces.

## 🔵 सरल परिभाषा (Hindi)
Container debugging का मतलब है यह पता लगाना कि container **क्यों crash, restart, slow या unreachable** है। इसके लिए tools का एक fixed क्रम होता है: `docker ps -a`, `docker logs`, `docker inspect`, `docker exec`, `docker events`, `docker stats`, और एक "debug container" जो टूटे हुए container के namespaces share करता है।

---

## 🔴 Problem it Solves
Containers are small and disposable. Production images often have **no shell, no curl, no ps** (distroless or alpine). When the Node.js API on your VPS exits with code 137 at 3 AM, you cannot just "SSH in and look around". Without a method, people restart the container and lose the evidence (logs, state, exit code). A structured debugging flow finds the root cause: app bug, OOM kill, bad env var, port clash, failed healthcheck, or network/DNS problem.

## 🔴 यह क्यों बना? (Hindi)
Containers छोटे और disposable होते हैं। Production images में अक्सर **shell, curl, ps कुछ नहीं** होता (distroless या alpine)। जब VPS पर Node.js API रात 3 बजे exit code 137 के साथ बंद हो जाए, तो आप बस "SSH करके देख लो" नहीं कर सकते। Method के बिना लोग container restart कर देते हैं और सबूत (logs, state, exit code) खो देते हैं। Structured flow से root cause मिलता है: app bug, OOM kill, गलत env var, port clash, failed healthcheck या network/DNS problem।

---

## 🟢 How it Works — Step by Step

```
Step 1 → docker ps -a            : is it Up, Exited, Restarting? note exit code
Step 2 → docker logs --tail 100  : read the last app output (stdout/stderr)
Step 3 → docker inspect          : State.ExitCode, OOMKilled, Env, Mounts, Health
Step 4 → docker exec -it ... sh  : look inside (only if container is running)
Step 5 → docker events / stats   : what did the daemon do? CPU/mem spikes?
Step 6 → docker run --entrypoint : start the same image with a shell to test
Step 7 → docker run --network container:<id> nicolaka/netshoot : debug sidecar
```

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `docker ps -a`: container Up, Exited या Restarting है? Exit code note करो।
Step 2 → `docker logs --tail 100`: app का आखिरी output (stdout/stderr) पढ़ो।
Step 3 → `docker inspect`: `State.ExitCode`, `OOMKilled`, Env, Mounts, Health देखो।
Step 4 → `docker exec -it ... sh`: अंदर जाकर देखो (सिर्फ तब जब container चल रहा हो)।
Step 5 → `docker events` / `docker stats`: daemon ने क्या किया? CPU/memory spike?
Step 6 → `docker run --entrypoint sh`: उसी image को shell के साथ चलाकर test करो।
Step 7 → `docker run --network container:<id> nicolaka/netshoot`: network debug के लिए sidecar।

Common exit codes: **0** = normal exit, **1** = app error, **125** = docker run itself failed, **126** = command not executable, **127** = command not found, **137** = SIGKILL (usually OOM or `docker kill`), **139** = segfault, **143** = SIGTERM (graceful stop).

---

## 🟡 Real World Example
Your FastAPI container on the AWS EC2 box keeps showing `Restarting (1)`. You run `docker logs --tail 50 api` and see `KeyError: 'DATABASE_URL'`. You forgot the `.env` file in the compose file. Another day the Node.js container shows `Exited (137)`; `docker inspect -f '{{.State.OOMKilled}}' api` prints `true`, so the 256 MB memory limit was too small, not an app bug. Without checking `OOMKilled` you would waste hours reading code.

## 🟡 Real Example Hindi mein
AWS EC2 पर आपका FastAPI container बार-बार `Restarting (1)` दिखाता है। `docker logs --tail 50 api` से दिखता है `KeyError: 'DATABASE_URL'` - compose file में `.env` देना भूल गए थे। दूसरे दिन Node.js container `Exited (137)` दिखाता है; `docker inspect -f '{{.State.OOMKilled}}' api` का output `true` आता है, यानी 256 MB memory limit छोटी थी, app bug नहीं। `OOMKilled` देखे बिना आप घंटों code पढ़ते रहते।

---

## 💻 Code / Config Example — Basic
```bash
#!/usr/bin/env bash
# debug-basic.sh - first 5 minutes of any container incident
set -euo pipefail                                   # stop on error, unset var, pipe failure
NAME="${1:?usage: debug-basic.sh <container-name>}" # container name is required argument

docker ps -a --filter "name=${NAME}"                # status, uptime, ports in one line
docker logs --tail 100 --timestamps "${NAME}"       # last 100 log lines with time
docker inspect -f 'exit={{.State.ExitCode}} oom={{.State.OOMKilled}} restarts={{.RestartCount}}' "${NAME}" # key facts
docker inspect -f '{{json .State.Health}}' "${NAME}" || true  # healthcheck history (if defined)
docker stats --no-stream "${NAME}" || true          # one snapshot of CPU / memory
docker exec "${NAME}" env | sort | head -30         # env vars the app really sees
```

## 💻 Code / Config Example — Advanced
```yaml
# docker-compose.debug.yml - overlay used ONLY on a staging/dev box
# usage: docker compose -f docker-compose.yml -f docker-compose.debug.yml up -d
services:
  api:                                  # same service name as the base compose file
    command: ["node", "--inspect=0.0.0.0:9229", "server.js"] # start Node with inspector enabled
    ports:
      - "127.0.0.1:9229:9229"           # expose debugger ONLY on localhost (never 0.0.0.0 publicly)
    environment:
      LOG_LEVEL: debug                  # more verbose app logs
      NODE_ENV: development             # show stack traces
    stop_grace_period: 5s               # do not wait long when we restart often
  netshoot:                             # debug sidecar with curl, dig, tcpdump, ss
    image: nicolaka/netshoot:latest     # example image; pin a tag in real use
    network_mode: "service:api"         # share api's network namespace (same IP, same ports)
    cap_add:
      - NET_ADMIN                       # needed for tcpdump / iptables inspection
      - NET_RAW                         # needed for raw sockets (ping, tcpdump)
    command: ["sleep", "infinity"]      # keep it alive so we can docker exec into it
    profiles: ["debug"]                 # starts only with: docker compose --profile debug up
```

```bash
# Debug a container that has NO shell (distroless) using a throwaway sidecar
docker run --rm -it \
  --network container:api \
  --pid container:api \
  nicolaka/netshoot                     # sees api's network and its processes (ps, ss, curl localhost)

# Copy files out of a crashed (stopped) container for study
docker cp api:/app/logs ./crash-logs    # works even when container is Exited

# Newer Docker CLI (version dependent): attach an ephemeral debug container
# docker debug api                      # Docker Desktop / subscription feature; may not exist on plain Engine
```

---

## 🟠 My Stack Integration
For Node.js, FastAPI, React and Nginx on one VPS, keep a standard runbook: **Nginx 502** means the upstream container is down or on a different network. Check `docker ps`, then `docker logs api`, then `docker exec nginx wget -qO- http://api:3000/health`. For FastAPI, run `docker exec api python -c "import os;print(os.environ.get('DATABASE_URL'))"`. Always send logs to stdout so `docker logs` works; later ship them to CloudWatch with the `awslogs` driver.

```yaml
# docker-compose.yml fragment - make debugging easy by design
services:
  api:
    image: myorg/api:1.4.2              # pinned tag, so "what is running" is known
    restart: unless-stopped             # survive reboot, but not after manual stop
    healthcheck:                        # lets docker ps show (healthy)/(unhealthy)
      test: ["CMD", "wget", "-qO-", "http://localhost:3000/health"] # simple HTTP probe
      interval: 30s                     # check every 30 s
      timeout: 3s                       # fail if no answer in 3 s
      retries: 3                        # 3 failures => unhealthy
    logging:
      driver: json-file                 # default driver, readable by docker logs
      options:
        max-size: "10m"                 # rotate at 10 MB so disk does not fill
        max-file: "3"                   # keep 3 files
```

Security aspect: a debug sidecar with `NET_ADMIN` or a published `9229` inspector port is a remote-code-execution door. Use it only temporarily, bind to `127.0.0.1`, and remove it after the incident.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Running `docker rm` or `docker compose down` first, then wondering why there are no logs.
✅ Correct: Collect `docker logs`, `docker inspect` and `docker cp` output **before** removing the container.

❌ Mistake 2: Installing curl/vim inside the production image "just to debug" and leaving it there.
✅ Correct: Keep the image slim; use `--network container:` with netshoot, or a debug compose profile.

❌ Mistake 3: Reading only `docker logs` for a container killed by OOM (no error is printed, process is simply killed).
✅ Correct: Always check `State.OOMKilled`, `ExitCode` and `dmesg | grep -i oom` on the host.

❌ Mistake 4: Exposing the Node.js `--inspect` port on `0.0.0.0`.
✅ Correct: Bind to `127.0.0.1` and use an SSH tunnel: `ssh -L 9229:127.0.0.1:9229 user@vps`.

---

## 🧠 Tricky Interview Question
A container shows `Up 2 seconds` again and again, and `docker logs` is empty. What do you check?

Answer: `Up 2 seconds` repeating means a restart loop (check `docker inspect` for `RestartCount` and `restart: always`). Empty logs mean the process died before printing anything or the entrypoint failed: wrong `ENTRYPOINT` path, missing exec bit (exit 126), missing binary (exit 127), or CRLF line endings in `entrypoint.sh` (`bad interpreter`). Override the entrypoint: `docker run --rm -it --entrypoint sh image` and run the command by hand. Also check `docker events` and the host `journalctl -u docker`.

---

## ⚫ Interview Questions + Answers

Q1: What does exit code 137 mean?
A1: The process got SIGKILL (128 + 9). Most often the kernel OOM killer, or `docker kill`/`docker stop` timeout. Confirm with `docker inspect -f '{{.State.OOMKilled}}'`.

Q2: How do you debug a container that has no shell?
A2: Use `docker cp` for files, `docker logs`, and a sidecar: `docker run --network container:app --pid container:app nicolaka/netshoot`. In Kubernetes the equivalent is `kubectl debug` with an ephemeral container.

Q3: Difference between `docker logs` and `docker events`?
A3: `logs` shows the **app's** stdout/stderr. `events` shows **daemon-level** actions (create, start, die, oom, health_status).

Q4: How do you see why a container is slow?
A4: `docker stats` for CPU/mem/IO, `docker top` for processes, check limits in `docker inspect` (`HostConfig.Memory`, `NanoCpus`), and throttling in cgroup `cpu.stat`.

Q5: A container works on your laptop but fails on the server. First step?
A5: Compare environment: image digest (`docker image inspect`), env vars, mounted files, architecture (arm64 vs amd64 gives `exec format error`), and network/DNS from inside the container.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- A container exits, restarts, or shows unhealthy.
- Nginx returns 502/504 and you must find which hop fails.
- Performance suddenly drops (memory leak, CPU throttling).

❌ Avoid when:
- You can fix it faster by reading CI logs of a bad build (image never started).
- Debug tools would run on a production container with customer data without approval; use a staging copy.

---

## 📊 Visual Diagram
```
 Incident: "API is down"
        |
        v
  docker ps -a ----> Up (healthy)? ---yes--> check Nginx / DNS / network
        |no
        v
  Exited / Restarting
        |
        v
  docker logs --tail 100 ---> app error? ---yes--> fix code/env, redeploy
        |no (empty / silent kill)
        v
  docker inspect: ExitCode, OOMKilled
        |
        +-- 137 + OOMKilled=true --> raise memory limit / fix leak
        +-- 126/127              --> entrypoint / binary path problem
        +-- 1                    --> app config error (env, DB, port)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Exit code | Number a process returns when it ends | Process खत्म होने पर लौटाया गया number |
| OOMKilled | Kernel killed process for exceeding memory | Memory सीमा पार करने पर kernel ने process मारा |
| docker inspect | Full JSON details of an object | किसी object की पूरी JSON जानकारी |
| Sidecar | Helper container sharing namespaces | Namespaces share करने वाला सहायक container |
| netshoot | Image full of network tools | Network tools वाली image |
| Restart loop | Container crashes and restarts forever | Container बार-बार crash होकर restart होना |

---

## ⚡ 3-Line Summary
English: Debug in order: `ps -a`, `logs`, `inspect`, `exec`, `events`/`stats`.
Exit code and `OOMKilled` often reveal the cause before you read any code.
For shell-less images use a netshoot sidecar; never leave debug ports open.
Hindi: क्रम से debug करो: `ps -a`, `logs`, `inspect`, `exec`, `events`/`stats`।
Exit code और `OOMKilled` अक्सर code पढ़ने से पहले ही कारण बता देते हैं।
बिना shell वाली image के लिए netshoot sidecar लो; debug ports कभी खुले मत छोड़ो।

---

## ➡️ Next Topic
**145. Container Networking Basics** - most "unreachable" bugs found during debugging are networking bugs, so we learn how container networks work next.
