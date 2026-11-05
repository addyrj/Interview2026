# 52. Docker Container — What it is
# हिंदी में: Docker Container क्या है

---

## 🔵 Simple Definition (English)
A **Docker container** is a running (or stopped) instance of an image: an isolated Linux process with its own filesystem view (image layers + a thin writable layer), network, process tree and resource limits. Containers are meant to be **ephemeral**: start, stop, delete and recreate them freely, keeping data in volumes.

## 🔵 सरल परिभाषा (Hindi)
**Docker container** किसी image का चलता (या रुका हुआ) instance है: एक isolated Linux process जिसका अपना filesystem दृश्य (image layers + पतली writable layer), network, process tree और resource limits होते हैं। Containers **अस्थायी (ephemeral)** होने के लिए बने हैं: जब चाहो शुरू, बंद, हटाओ और दोबारा बनाओ, और data volumes में रखो।

---

## 🔴 Problem it Solves
Running apps directly on the host makes them share libraries, ports, and failures: one app's memory leak or dependency upgrade can break another. Containers give each app its own sandbox with a predictable start/stop lifecycle, resource caps, and a standard way to run (`docker run`), so operations become uniform no matter whether the app is Node.js, Python, or Nginx.

## 🔴 यह क्यों बना? (Hindi)
Apps को सीधे host पर चलाने से वे libraries, ports और failures share करते हैं: एक का memory leak या dependency upgrade दूसरे को तोड़ सकता है। Containers हर app को अपना sandbox, अनुमानित start/stop life-cycle, resource limits और चलाने का standard तरीका (`docker run`) देते हैं, इसलिए app Node.js, Python या Nginx कुछ भी हो, operations एक जैसे रहते हैं।

---

## 🟢 How it Works — Step by Step

```
Lifecycle states:
  created --start--> running --pause--> paused --unpause--> running
  running --stop (SIGTERM, then SIGKILL after 10s)--> exited --start--> running
  running --crash/exit--> exited (restart policy may bring it back) --rm--> deleted

Step 1 → docker create/run: daemon creates the container from the image (config + writable layer)
Step 2 → Network is attached; port mappings (-p) are set; volumes mounted
Step 3 → start: runc launches the ENTRYPOINT/CMD process as PID 1 inside namespaces + cgroups
Step 4 → Container lives only while PID 1 lives. PID 1 exits -> container exits
Step 5 → stdout/stderr of PID 1 are captured by the logging driver (docker logs)
Step 6 → stop: SIGTERM to PID 1, wait (default 10s), then SIGKILL
Step 7 → rm: writable layer deleted. Image + named volumes remain
```

## 🟢 कैसे काम करता है? (Hindi)
```
Life-cycle states:
  created --start--> running --pause--> paused --unpause--> running
  running --stop (SIGTERM, फिर 10s बाद SIGKILL)--> exited --start--> running
  running --crash/exit--> exited (restart policy वापस ला सकती है) --rm--> deleted

Step 1 → docker create/run: daemon image से container बनाता है (config + writable layer)
Step 2 → Network जुड़ता है; port mappings (-p) लगते हैं; volumes mount होते हैं
Step 3 → start: runc ENTRYPOINT/CMD process को namespaces + cgroups में PID 1 की तरह चलाता है
Step 4 → Container तभी तक ज़िंदा है जब तक PID 1 ज़िंदा है। PID 1 खत्म -> container खत्म
Step 5 → PID 1 का stdout/stderr logging driver पकड़ता है (docker logs)
Step 6 → stop: PID 1 को SIGTERM, इंतज़ार (default 10s), फिर SIGKILL
Step 7 → rm: writable layer हटती है। Image + named volumes बचते हैं
```

---

## 🟡 Real World Example
During a deploy of a Node.js API on a VPS, `docker compose up -d` starts the new container, then stops the old one: Docker sends SIGTERM, the Node app closes its HTTP server and finishes in-flight requests, then exits cleanly. An app that ignores SIGTERM gets SIGKILLed after 10 seconds, dropping live requests (visible as 502 from Nginx). Another classic: a container exits immediately with code 0 because the CMD is a shell script that ends, or with 137 because it was OOM-killed.

## 🟡 Real Example Hindi mein
VPS पर Node.js API deploy में `docker compose up -d` नया container शुरू करके पुराना रोकता है: Docker SIGTERM भेजता है, Node app अपना HTTP server बंद करके चल रही requests पूरी करता है, फिर साफ़ exit। जो app SIGTERM ignore करे उसे 10 सेकंड बाद SIGKILL मिलता है और चलती requests गिर जाती हैं (Nginx पर 502)। दूसरा classic केस: container तुरंत code 0 से exit हो जाता है क्योंकि CMD shell script है जो खत्म हो गई, या 137 से क्योंकि OOM-kill हुआ।

---

## 💻 Code / Config Example — Basic
```bash
# Full container lifecycle (needs a Docker daemon)
docker run -d --name web -p 8080:80 nginx:1.27-alpine   # create + start in background; host 8080 -> container 80
docker ps                                               # running containers
curl -I http://localhost:8080                           # test: expect HTTP/1.1 200 OK
docker logs --tail 20 web                               # last 20 log lines (stdout/stderr of PID 1)
docker exec -it web sh                                  # open a shell inside the running container
docker stats --no-stream web                            # CPU, memory, network, PIDs now
docker stop web                                         # SIGTERM, then SIGKILL after grace period
docker ps -a                                            # stopped container still listed (status Exited)
docker inspect -f '{{.State.ExitCode}}' web             # exit code (0 clean, 137 killed/OOM, 1 error)
docker start web                                        # start the same container again (same writable layer)
docker rm -f web                                        # remove (force stops it first)
```

## 💻 Code / Config Example — Advanced
```yaml
# docker-compose.yml - production-style container settings for a Node.js API behind Nginx
services:
  api:
    image: ghcr.io/myorg/api:1.4.0            # image to instantiate (example tag)
    container_name: api                       # fixed name (omit if you want to scale replicas)
    init: true                                # tini as PID 1: forwards signals, reaps zombie processes
    user: "10001:10001"                       # run as non-root
    read_only: true                           # immutable root filesystem
    tmpfs:
      - /tmp                                  # writable temp directory in RAM only
    environment:
      NODE_ENV: production                    # production mode
      PORT: "3000"                            # app port
    env_file:
      - ./api.env                             # secrets/config file (git-ignored, chmod 600)
    ports:
      - "127.0.0.1:3000:3000"                 # only host-local; Nginx proxies to it
    volumes:
      - uploads:/app/uploads                  # persistent user uploads (named volume)
    mem_limit: 512m                           # memory cap -> OOM-kill inside the limit only
    cpus: 1.0                                 # CPU cap
    restart: unless-stopped                   # restart on crash and after reboot
    stop_signal: SIGTERM                      # signal sent on stop (default)
    stop_grace_period: 30s                    # time to finish requests before SIGKILL
    healthcheck:                              # Docker marks container healthy/unhealthy
      test: ["CMD", "node", "-e", "fetch('http://127.0.0.1:3000/health').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"]   # uses built-in fetch (Node 18+)
      interval: 30s                           # check interval
      timeout: 5s                             # per-check timeout
      retries: 3                              # failures before unhealthy
      start_period: 20s                       # grace time during start-up
    logging:
      driver: json-file                       # default driver
      options: { max-size: "10m", max-file: "3" }   # rotation prevents disk fill
volumes:
  uploads:                                    # declare the named volume
```

---

## 🟠 My Stack Integration
- **Node.js:** handle SIGTERM (`server.close()`) so rolling deploys drop no requests. Example below.
- **FastAPI/uvicorn:** uvicorn handles SIGTERM gracefully; use `--timeout-graceful-shutdown` where supported by your uvicorn version.
- **Nginx:** `proxy_pass http://api:3000;` by service name; `upstream` health matters since Nginx caches DNS at start (restart/reload Nginx after recreating upstream containers or use a `resolver`).
- **VPS/AWS:** `restart: unless-stopped` on a VPS; ECS/Kubernetes replace restart policies with their own health-based restarts.

```javascript
// server.js - graceful shutdown for containers (Node.js)
const http = require('http');                         // built-in HTTP module
const server = http.createServer((req, res) => {      // minimal handler
  if (req.url === '/health') { res.end('ok'); return; } // health endpoint for HEALTHCHECK/Nginx
  res.end('hello');                                   // normal response
});
server.listen(process.env.PORT || 3000);              // listen on the configured port

function shutdown(signal) {                           // called on SIGTERM/SIGINT
  console.log(`${signal} received, closing server`);  // visible in docker logs
  server.close(() => process.exit(0));                // stop accepting, finish in-flight, then exit cleanly
  setTimeout(() => process.exit(1), 25000).unref();   // hard-stop before Docker's SIGKILL (grace 30s)
}
process.on('SIGTERM', () => shutdown('SIGTERM'));     // docker stop / compose up recreate
process.on('SIGINT', () => shutdown('SIGINT'));       // Ctrl+C in foreground runs
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Storing uploads/DB files in the container filesystem.
✅ Correct: Named volume or external storage (S3/RDS); the writable layer dies with the container.

❌ Mistake 2: `CMD npm start` (shell form) so SIGTERM never reaches Node.
✅ Correct: `CMD ["node", "server.js"]` exec form, plus `init: true` or `tini`.

❌ Mistake 3: Running several services (Nginx + app + cron) in one container with supervisord by default.
✅ Correct: One main process per container; compose them as separate services.

❌ Mistake 4: Running as root with the Docker socket mounted.
✅ Correct: Non-root `USER`, `no-new-privileges`, dropped caps, no docker.sock mount. A compromised root container with the socket = host takeover.

---

## 🧠 Tricky Interview Question
"A container started with `docker run -d ubuntu` shows `Exited (0)` seconds later. Nothing crashed. Why, and how would you keep it alive correctly?"

Answer: A container runs only as long as its main process (PID 1). The ubuntu image's default CMD is `bash`, which exits immediately without a TTY/stdin, so the container exits with 0. Do not hack with `tail -f /dev/null` for production; run the real foreground service (`nginx -g 'daemon off;'`, `node server.js`). For debugging use `docker run -it ubuntu bash` or `docker exec` into a running container.

---

## ⚫ Interview Questions + Answers

Q1: Container vs image?
A1: Image is the immutable template; container is a runnable instance with a writable layer and runtime config.

Q2: What happens on `docker stop`?
A2: SIGTERM to PID 1, wait `stop_grace_period` (default 10s), then SIGKILL. `docker kill` sends SIGKILL immediately.

Q3: Restart policies?
A3: `no` (default), `on-failure[:max]`, `always`, `unless-stopped`. Difference: `always` also restarts containers you stopped manually after a daemon restart; `unless-stopped` respects the manual stop.

Q4: Exit code 137 and 143?
A4: 137 = 128+9 (SIGKILL, often OOM-kill or grace timeout). 143 = 128+15 (SIGTERM). Check `docker inspect` for `OOMKilled`.

Q5: `docker exec` vs `docker attach`?
A5: `exec` starts a new process inside a running container (shell, debug). `attach` connects to the main process's stdio; Ctrl+C may stop it.

---

## 🔷 When to Use + When Not to Use
✅ Use containers when:
- Stateless services (APIs, workers, web servers) with externalized state

❌ Avoid when:
- Treating them as pets: patching by hand, keeping state inside, SSH servers in the image
- Stateful DBs in production without proper volumes, backups and tuning (consider managed RDS)

---

## 📊 Visual Diagram
```
  created ──start──> RUNNING ──stop/SIGTERM(10s)/SIGKILL──> EXITED ──rm──> (gone)
                       │  ▲                                    │
              crash/OOM│  │ restart policy                     └─start──> RUNNING
                       v  │
                    EXITED ┘

   +-------------------- CONTAINER ---------------------+
   | PID 1: node server.js        (stdout -> docker logs)|
   | writable layer (temporary)                          |
   | image layers (read-only)     volume /app/uploads    |-> persists
   | netns: eth0 172.18.0.3       cgroup: 512M, 1 CPU    |
   +-----------------------------------------------------+
   Nginx(:80) --proxy_pass--> api:3000
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Container | Running instance of image | image का चलता instance |
| PID 1 | Main process of container | container की मुख्य process |
| Ephemeral | Short-lived, replaceable | अस्थायी, बदले जाने योग्य |
| Writable layer | Temporary top layer | ऊपर की अस्थायी परत |
| Restart policy | Auto-restart rule | अपने-आप दोबारा चालू करने का नियम |
| Healthcheck | Liveness test command | स्वास्थ्य जाँच command |
| SIGTERM | Polite stop signal | विनम्र बंद करने का संकेत |

---

## ⚡ 3-Line Summary
English: A container is an isolated process started from an image; it lives only as long as PID 1.
English: Treat containers as disposable: data in volumes, graceful SIGTERM handling, restart policy, health checks.
English: Run non-root with resource limits; one main process per container.
Hindi: Container image से शुरू हुई isolated process है; वह तभी तक जीता है जब तक PID 1 जीता है।
Hindi: Containers को disposable मानो: data volumes में, SIGTERM का graceful handling, restart policy, health checks।
Hindi: Non-root और resource limits के साथ चलाओ; एक container में एक मुख्य process।

---

## ➡️ Next Topic
**53. Docker Volume - What it is** - containers are disposable, so next learn the Docker object that keeps data alive: volumes, bind mounts and persistence.
