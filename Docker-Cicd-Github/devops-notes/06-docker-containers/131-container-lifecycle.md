---

# 131. Container Lifecycle
# हिंदी में: Container का Lifecycle (जन्म से मृत्यु तक)

---

## 🔵 Simple Definition (English)
The container lifecycle is the path a container follows: it is **created** from an image, **started**, may be **paused/stopped/restarted**, and finally **removed**. Each step is a separate Docker command, and the container's writable layer lives until it is removed.

## 🔵 सरल परिभाषा (Hindi)
Container lifecycle वह रास्ता है जो container follow करता है: image से **create** होना, **start** होना, फिर **pause/stop/restart** होना, और आखिर में **remove** होना। हर step का अलग Docker command है, और container की writable layer तब तक रहती है जब तक container remove नहीं होता।

---

## 🔴 Problem it Solves
Before containers, a "process on a server" had no clean start/stop/cleanup contract. Deploying a Node.js app on a VPS meant `node app.js &`, a hand-edited systemd unit, leftover temp files, and "who killed my process?" mysteries. Without a defined lifecycle you cannot automate deploys, roll back, or clean up. Docker gives every workload the same predictable steps: create, start, stop, remove, so CI/CD and orchestrators (Compose, Kubernetes) can drive them.

## 🔴 यह क्यों बना? (Hindi)
Containers से पहले server पर "process" का कोई साफ start/stop/cleanup नियम नहीं था। VPS पर Node.js app चलाने का मतलब था `node app.js &`, हाथ से बनी systemd file, बचे हुए temp files, और "मेरा process किसने मारा?" जैसी उलझन। Lifecycle न हो तो deploy automate, rollback और cleanup मुश्किल है। Docker हर workload को वही predictable steps देता है: create, start, stop, remove, ताकि CI/CD और Compose/Kubernetes उन्हें चला सकें।

---

## 🟢 How it Works — Step by Step

```
Step 1 → docker create   : Docker makes a container from the image (writable layer + config), NOT running yet
Step 2 → docker start    : Docker starts PID 1 (the image's CMD/ENTRYPOINT) inside new namespaces + cgroups
Step 3 → (running)       : app serves traffic; logs go to the log driver; you can exec, stats, inspect
Step 4 → docker pause / unpause : (optional) freeze all processes using the cgroup freezer, no signal sent
Step 5 → docker stop     : SIGTERM to PID 1, wait grace period (default 10s), then SIGKILL
Step 6 → docker start    : (optional) restart the same container; its writable layer data is still there
Step 7 → docker rm       : delete the container + its writable layer (anonymous volumes only with -v)
```
`docker run` = `create` + `start` (+ `attach` if you do not use `-d`).

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → docker create : image से container बनता है (writable layer + config), अभी चल नहीं रहा
Step 2 → docker start  : PID 1 (image का CMD/ENTRYPOINT) नए namespaces + cgroups में शुरू होता है
Step 3 → (running)     : app traffic serve करती है; logs log driver में जाते हैं; exec, stats, inspect कर सकते हैं
Step 4 → docker pause  : (optional) cgroup freezer से सभी processes freeze, कोई signal नहीं जाता
Step 5 → docker stop   : PID 1 को SIGTERM, grace period (default 10s) इंतज़ार, फिर SIGKILL
Step 6 → docker start  : (optional) वही container दोबारा; उसकी writable layer का data बचा रहता है
Step 7 → docker rm     : container + writable layer delete (anonymous volumes सिर्फ -v से)
```
`docker run` = `create` + `start` (और `-d` न हो तो `attach`)।

---

## 🟡 Real World Example
Swiggy-style order API on your VPS: the CI pipeline SSHs in and runs `docker pull`, `docker stop api` (Node.js gets SIGTERM, finishes in-flight orders, closes DB pool), `docker rm api`, then `docker run -d --name api ...` with the new image tag. The old container is gone cleanly, the new one is created from a fresh image. If the new version is bad, you `docker run` the previous tag again. That repeatable create-stop-remove loop is the entire "deployment".

## 🟡 Real Example Hindi mein
Swiggy जैसी order API आपके VPS पर: CI pipeline SSH करके `docker pull`, `docker stop api` (Node.js को SIGTERM मिलता है, चल रहे orders पूरे करता है, DB pool बंद करता है), `docker rm api`, फिर नए image tag से `docker run -d --name api ...` चलाती है। पुराना container साफ़ हट जाता है, नया fresh image से बनता है। नया version खराब हो तो पिछला tag दोबारा `docker run` कर दो। यही create-stop-remove loop पूरा "deployment" है।

---

## 💻 Code / Config Example — Basic
```bash
#!/usr/bin/env bash
# lifecycle-basic.sh - walk one container through its whole life
set -euo pipefail                                  # stop on first error, unset var, or pipe failure

docker pull nginx:1.27-alpine                      # download the image (example tag, update as needed)
docker create --name demo -p 8080:80 nginx:1.27-alpine   # create container, NOT started yet
docker ps -a --filter name=demo                    # shows STATUS "Created"
docker start demo                                  # start PID 1 (nginx) inside the container
docker ps --filter name=demo                       # shows STATUS "Up ..."
docker pause demo                                  # freeze all processes (no signal sent)
docker unpause demo                                # resume them
docker stop demo                                   # SIGTERM, wait 10s, then SIGKILL if still alive
docker ps -a --filter name=demo                    # shows "Exited (0)" or "Exited (137)" if killed
docker start demo                                  # same container comes back (same writable layer)
docker stop -t 30 demo                             # give app 30 seconds to shut down gracefully
docker rm demo                                     # delete the stopped container
docker ps -a --filter name=demo                    # empty now - container is gone
```

## 💻 Code / Config Example — Advanced
```yaml
# docker-compose.yml - lifecycle controls expressed declaratively
services:
  api:
    image: myorg/orders-api:1.4.2         # pinned tag (example), never :latest in production
    container_name: orders-api            # fixed name so scripts can target it
    init: true                            # tiny init (tini) as PID 1: forwards signals, reaps zombies
    stop_signal: SIGTERM                  # signal sent on `docker compose stop` (default already SIGTERM)
    stop_grace_period: 30s                # wait 30s before SIGKILL, so Node can drain connections
    restart: unless-stopped               # lifecycle after crash/reboot (see topic 137)
    read_only: true                       # root filesystem read-only: container cannot mutate itself
    tmpfs:
      - /tmp                              # writable temp space in RAM only
    environment:
      NODE_ENV: production                # runtime mode
    ports:
      - "127.0.0.1:3000:3000"             # bind only on localhost; Nginx on host proxies to it
```
```bash
# Cleanup commands used in real pipelines
docker container prune -f                  # remove ALL stopped containers (be careful on shared hosts)
docker rm -f -v old-api                    # force-remove running container AND its anonymous volumes
docker run --rm alpine:3.20 echo hi        # --rm = auto-remove when the container exits (one-off jobs)
```

---

## 🟠 My Stack Integration
**Node.js**: Node as PID 1 ignores SIGTERM by default unless you handle it. Add `process.on('SIGTERM', ...)` to close the HTTP server and DB pool, or use `init: true`.
**FastAPI**: run `uvicorn` (it handles SIGTERM and finishes requests). Avoid shell-form CMD, which makes `sh` PID 1 and swallows the signal.
**React**: build step is a throwaway container (`--rm`); the runtime is Nginx serving static files.
**VPS + Nginx**: host Nginx proxies to `127.0.0.1:3000`; during deploy, start the new container on a second port, switch upstream, then stop the old one (near-zero downtime).
**AWS**: ECS/EKS use the same lifecycle; ECS `stopTimeout` equals `docker stop -t`.

```js
// server.js - graceful shutdown for the Docker lifecycle (Node.js)
const http = require('http');                       // core http module
const server = http.createServer((req, res) => res.end('ok')); // tiny demo handler
server.listen(3000);                                // listen on port 3000
process.on('SIGTERM', () => {                       // docker stop sends SIGTERM first
  console.log('SIGTERM received, draining');        // log so you can see it in docker logs
  server.close(() => process.exit(0));              // stop accepting, finish in-flight, exit 0
  setTimeout(() => process.exit(1), 25000).unref(); // safety: force exit before SIGKILL at 30s
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Thinking `docker stop` and `docker kill` are the same, then losing in-flight requests.
✅ Correct: `stop` = SIGTERM + grace period + SIGKILL; `kill` = immediate SIGKILL by default. Use `stop` and handle SIGTERM.

❌ Mistake 2: Storing database files in the container's writable layer, then running `docker rm`.
✅ Correct: use volumes (or a managed DB like RDS). `rm` deletes the writable layer permanently.

❌ Mistake 3: Piling up stopped containers and dangling data until the VPS disk is full.
✅ Correct: use `--rm` for one-off jobs and schedule `docker system df` checks plus careful `docker container prune`.

❌ Mistake 4: Using shell-form `CMD node app.js` so the signal never reaches Node.
✅ Correct: use exec form `CMD ["node","app.js"]` or `init: true`.

**Security**: removing old containers also removes stale secrets in env vars and old vulnerable images in use; `read_only: true` and `--rm` reduce persistence for attackers.

---

## 🧠 Tricky Interview Question
You run `docker stop api` and it takes exactly 10 seconds every time, and the exit code is 137. Why, and how do you fix it?

Answer: 137 = 128 + 9 (SIGKILL). The app ignores SIGTERM, so Docker waits the full 10s grace period and then kills it. Typical cause: shell-form CMD (sh is PID 1) or Node without a SIGTERM handler. Fix by using exec-form CMD, adding a SIGTERM handler (or `init: true`), and if shutdown legitimately needs longer, raise `-t`/`stop_grace_period`.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `docker create`, `start` and `run`?
A1: `create` builds the container but does not run it; `start` runs an existing container; `run` does create + start (and attaches unless `-d`).

Q2: Does stopping a container delete its data?
A2: No. The writable layer survives `stop` and `start`. It is deleted only on `docker rm`. Volumes survive even `rm` unless removed explicitly.

Q3: What signal does `docker stop` send and what happens after?
A3: SIGTERM to PID 1, waits 10 seconds by default (configurable with `-t`), then SIGKILL.

Q4: What does `docker pause` do differently from `stop`?
A4: It freezes processes with the cgroup freezer; no signal is sent, memory stays allocated, and `unpause` resumes exactly where it was. `stop` terminates the process.

Q5: What does `--rm` do?
A5: Removes the container automatically when it exits, good for one-off tasks like migrations or builds so they do not pile up.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Automating deploys: pull, stop, rm, run is the base of every release script.
- Running one-off jobs (DB migrations, tests) with `--rm`.
- Debugging: `create` then inspect config before starting.

❌ Avoid when:
- You need data to survive: do not rely on container lifecycle, use volumes.
- Hand-managing many containers manually: use Compose or Kubernetes instead.

---

## 📊 Visual Diagram
```
                 docker create
   [Image] ------------------------> [Created]
                                         |
                                  docker start
                                         v
        docker unpause             [Running] <--- docker restart / restart policy
   [Paused] <--- docker pause ---------+ |
        |                              | | docker stop (SIGTERM, then SIGKILL)
        +------------------------------+ v
                                      [Exited]
                                         |
                                   docker rm
                                         v
                                    [Removed]
   docker run = create + start
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Container | Running instance of an image | Image का चलता हुआ instance |
| Writable layer | Top layer where container writes data | Container की लिखने योग्य परत |
| PID 1 | First process, receives signals | Container का पहला process |
| SIGTERM | Polite "please stop" signal | विनम्र बंद करने का signal |
| SIGKILL | Forced kill, cannot be caught | ज़बरदस्ती बंद |
| Grace period | Wait time before SIGKILL | SIGKILL से पहले का इंतज़ार |
| `--rm` | Auto-delete on exit | Exit पर अपने-आप delete |

---

## ⚡ 3-Line Summary
English: A container goes create, start, (pause), stop, remove; `docker run` combines create and start.
`docker stop` sends SIGTERM then SIGKILL, so your app must handle SIGTERM.
Data in the writable layer dies on `rm`, so use volumes for anything important.

Hindi: Container का सफ़र create, start, (pause), stop, remove है; `docker run` create और start दोनों करता है।
`docker stop` पहले SIGTERM फिर SIGKILL भेजता है, इसलिए app को SIGTERM handle करना चाहिए।
Writable layer का data `rm` पर चला जाता है, इसलिए ज़रूरी data के लिए volumes इस्तेमाल करें।

---

## ➡️ Next Topic
**132. Container States**: now that you know the steps, learn the exact states (created, running, paused, restarting, exited, dead) that `docker ps` shows and what each means.
