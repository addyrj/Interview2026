---

# 060. docker stop + docker kill
# हिंदी में: docker stop और docker kill

---

## 🔵 Simple Definition (English)
`docker stop` sends **SIGTERM** to the container's main process, waits (default 10 seconds), then sends **SIGKILL** if it is still alive. `docker kill` sends **SIGKILL** immediately (or any signal you choose with `-s`). Stop is graceful, kill is forceful.

## 🔵 सरल परिभाषा (Hindi)
`docker stop` container के main process को **SIGTERM** भेजता है, इंतज़ार करता है (default 10 सेकंड), और फिर भी process ज़िंदा हो तो **SIGKILL** भेजता है। `docker kill` तुरंत **SIGKILL** भेजता है (या `-s` से आपका चुना signal)। Stop नरमी से, kill ज़बरदस्ती।

---

## 🔴 Problem it Solves
Killing a process abruptly can corrupt data: half-written files, open DB transactions, lost in-flight HTTP requests, unflushed logs. Containers need a graceful shutdown window so apps can finish work and close connections. But sometimes an app is hung and must be force-killed. These two commands cover both cases.

## 🔴 यह क्यों बना? (Hindi)
Process को अचानक मारने से data corrupt हो सकता है: आधी लिखी files, खुले DB transactions, बीच में कटी HTTP requests, flush न हुए logs। Containers को graceful shutdown की window चाहिए ताकि apps काम पूरा करें और connections बंद करें। पर कभी app hang हो जाता है और force-kill ज़रूरी होता है। ये दो commands दोनों स्थितियाँ संभालते हैं।

---

## 🟢 How it Works — Step by Step

```
docker stop api
Step 1 → Daemon sends SIGTERM (or the image's STOPSIGNAL) to PID 1 of the container
Step 2 → App catches it: stops accepting new requests, finishes current ones, closes DB, exits 0
Step 3 → Daemon waits up to the timeout (default 10s, change with -t / --time or stop_grace_period)
Step 4 → If still running -> daemon sends SIGKILL (cannot be caught) -> exit code 137
Step 5 → Container state becomes Exited; restart policy "always/on-failure" may restart it

docker kill api
Step 1 → Daemon sends SIGKILL (default) immediately; no cleanup possible
Step 2 → docker kill -s SIGHUP api sends another signal (useful to ask nginx/gunicorn to reload)
```

## 🟢 कैसे काम करता है? (Hindi)

```
docker stop api
Step 1 → Daemon container के PID 1 को SIGTERM (या image का STOPSIGNAL) भेजता है
Step 2 → App इसे पकड़ता है: नई requests लेना बंद, चल रही requests पूरी, DB बंद, exit 0
Step 3 → Daemon timeout तक इंतज़ार करता है (default 10s, -t / --time या stop_grace_period से बदलें)
Step 4 → अगर अब भी चल रहा है -> daemon SIGKILL भेजता है (पकड़ा नहीं जा सकता) -> exit code 137
Step 5 → Container Exited हो जाता है; restart policy "always/on-failure" दोबारा चला सकती है

docker kill api
Step 1 → Daemon तुरंत SIGKILL भेजता है (default); cleanup संभव नहीं
Step 2 → docker kill -s SIGHUP api दूसरा signal भेजता है (nginx/gunicorn को reload कहने के लिए उपयोगी)
```

---

## 🟡 Real World Example
Your payment webhook API handles long requests. During a deploy, `docker compose up -d` stops the old container. If your app ignores SIGTERM, Docker waits 10 seconds and kills it, dropping in-flight payments. After you add a SIGTERM handler and set `stop_grace_period: 30s`, requests finish and the order service sees no failed webhooks. Swiggy-style order flows depend on this kind of graceful shutdown during rolling deploys.

## 🟡 Real Example Hindi mein
आपका payment webhook API लंबी requests संभालता है। Deploy के दौरान `docker compose up -d` पुराने container को stop करता है। अगर आपका app SIGTERM ignore करता है, Docker 10 सेकंड रुककर kill कर देता है और in-flight payments गिर जाते हैं। SIGTERM handler जोड़ने और `stop_grace_period: 30s` सेट करने के बाद requests पूरी हो जाती हैं और order service को कोई failed webhook नहीं दिखता। Swiggy जैसे order flows rolling deploys में ऐसे ही graceful shutdown पर निर्भर करते हैं।

---

## 💻 Code / Config Example — Basic

```bash
# --- stop and kill basics ---
docker stop web                                  # graceful: SIGTERM, wait 10s, then SIGKILL
docker stop -t 30 web                            # wait up to 30 seconds before SIGKILL
docker stop -t 0 web                             # no grace period (same effect as a kill)
docker stop web db cache                         # stop several containers (stopped one after another)
docker stop $(docker ps -q)                      # stop every running container (careful on servers)
docker kill web                                  # immediate SIGKILL
docker kill -s SIGHUP web                        # send another signal (e.g. config reload)
docker kill -s SIGUSR1 web                       # app-specific signal if your app handles it
docker start web                                 # start a stopped container again
docker restart -t 20 web                         # stop (20s grace) then start
```

## 💻 Code / Config Example — Advanced

```javascript
// server.js - Node.js (Express) graceful shutdown for docker stop
// Run: npm install express ; node server.js   (syntax checked with node --check)
const express = require('express');             // web framework
const app = express();                          // create app

app.get('/health', (req, res) => res.send('ok'));   // simple health endpoint
app.get('/slow', (req, res) => {                // simulate long request
  setTimeout(() => res.send('done'), 5000);     // finishes after 5 seconds
});

const server = app.listen(3000, '0.0.0.0', () => console.log('listening on 3000'));   // bind all interfaces

let shuttingDown = false;                       // avoid double handling
function shutdown(signal) {                     // called on SIGTERM / SIGINT
  if (shuttingDown) return;                     // ignore repeated signals
  shuttingDown = true;                          // mark
  console.log(`${signal} received, draining`);  // log for docker logs
  server.close(() => {                          // stop accepting, wait for in-flight requests
    console.log('closed cleanly');              // all requests finished
    process.exit(0);                            // exit code 0 = clean
  });
  setTimeout(() => {                            // safety net before Docker's SIGKILL
    console.error('forced exit');
    process.exit(1);                            // non-zero exit
  }, 25000).unref();                            // must be shorter than stop_grace_period
}
process.on('SIGTERM', shutdown);                // docker stop sends this
process.on('SIGINT', shutdown);                 // Ctrl+C in foreground
```

```dockerfile
# Dockerfile - exec-form CMD so node is PID 1 and receives SIGTERM directly
# small base image (example tag)
FROM node:20-alpine
# working directory
WORKDIR /app
# dependency manifests first for caching
COPY package*.json ./
# install production dependencies only
RUN npm ci --omit=dev
# application code
COPY server.js ./
# run as non-root user provided by the image
USER node
# documentation of the port
EXPOSE 3000
# signal sent by docker stop (this is the default)
STOPSIGNAL SIGTERM
# exec form: no shell wrapper swallowing signals
CMD ["node", "server.js"]
```

```yaml
# docker-compose.yml - give the app time to drain before SIGKILL
services:
  api:
    build: .                                     # build from Dockerfile above
    init: true                                   # tiny init (tini) as PID 1: forwards signals, reaps zombies
    stop_signal: SIGTERM                         # signal used on stop (default)
    stop_grace_period: 30s                       # wait 30s before SIGKILL (default 10s)
    restart: unless-stopped                      # restart on crash, not after manual stop
    ports:
      - "127.0.0.1:3000:3000"                    # only host Nginx can reach it
```

---

## 🟠 My Stack Integration
- **Node.js**: handle `SIGTERM` as in the example; **FastAPI/Uvicorn**: Uvicorn handles SIGTERM gracefully by default and finishes requests; with Gunicorn, SIGTERM triggers graceful worker shutdown (`--graceful-timeout`).
- **Nginx**: `docker stop nginx` uses SIGQUIT (graceful) because the official image sets `STOPSIGNAL SIGQUIT`; `docker kill -s HUP nginx` reloads config (or `docker exec nginx nginx -s reload`).
- **React (static via Nginx)**: nothing special, stops instantly.
- **VPS deploys**: `stop_grace_period` must exceed your longest request; GitHub Actions SSH deploy then waits for it.
- **AWS ECS**: the equivalent is `stopTimeout` in the container definition; ALB deregistration delay should match.

Security: a container that ignores SIGTERM forces a SIGKILL after the timeout; this is a reliability and data-integrity risk. `docker kill` can be abused by anyone with docker group access, so restrict that group. Do not rely on `kill` as a normal workflow: data may be left inconsistent.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Shell-form `CMD node server.js` or `CMD ./start.sh` so `sh` is PID 1 and never forwards SIGTERM; every stop takes 10s and ends in SIGKILL.
✅ Correct: Use exec form `CMD ["node","server.js"]`, or `exec node server.js` inside scripts, or `init: true`.

❌ Mistake 2: Using `docker kill` for every restart.
✅ Correct: Use `docker stop` / `docker compose restart`, reserve `kill` for hung containers.

❌ Mistake 3: Stopping a database with a 0 or 1 second timeout.
✅ Correct: Give databases a longer grace period (e.g. `stop_grace_period: 60s`) so they flush and checkpoint.

❌ Mistake 4: Expecting `docker stop` to stop a container that keeps restarting.
✅ Correct: Stopping manually pauses the restart policy for that run; for permanent removal use `docker compose down` or `docker update --restart no`.

---

## 🧠 Tricky Interview Question
Every `docker stop` of your Python container takes exactly 10 seconds and the exit code is 137, even though the app handles SIGTERM when run locally. Why?

Answer: In the container, PID 1 is probably a shell (`CMD python app.py` shell form, or an entrypoint script that does not `exec`). The shell receives SIGTERM but does not pass it to Python, so Docker waits 10 seconds and sends SIGKILL (137). Also PID 1 gets no default signal handlers in Linux, so a process that does not install handlers ignores SIGTERM. Fix: exec-form CMD, `exec "$@"` in the entrypoint script, install handlers, or run with `--init`.

---

## ⚫ Interview Questions + Answers

Q1: Difference between `docker stop` and `docker kill`?
A1: `stop`: SIGTERM, then SIGKILL after the timeout. `kill`: SIGKILL right away (or the signal given with `-s`). Only SIGTERM can be handled by the app for cleanup.

Q2: Why can SIGKILL not be handled?
A2: It is delivered by the kernel and cannot be caught, blocked or ignored; the process is removed immediately.

Q3: How do you change the grace period?
A3: `docker stop -t N`, `docker run --stop-timeout N`, or `stop_grace_period` in Compose.

Q4: What does exit code 143 vs 137 mean?
A4: 143 = 128+15 (terminated by SIGTERM); 137 = 128+9 (killed by SIGKILL).

Q5: What happens to volumes when a container stops?
A5: Nothing; data in volumes and the container's writable layer remain until the container is removed (writable layer) or volumes are explicitly deleted.

---

## 🔷 When to Use + When Not to Use
✅ Use stop when:
- Normal deploys, maintenance, restarts.

✅ Use kill when:
- The container is hung and `stop` timed out, or you want to send a custom signal (reload).

❌ Avoid kill when:
- Databases or anything writing to disk, unless there is no alternative.

---

## 📊 Visual Diagram
```
 docker stop api
   |--SIGTERM--> [ app handler: drain, close DB ] --exit 0--> Exited (0)
   |                         |
   |                  too slow (> timeout)
   |                         v
   +-------- SIGKILL --------X  exit 137

 docker kill api
   |--SIGKILL--> X  (no cleanup) exit 137

 time ----->  0s        10s (default)
              SIGTERM   SIGKILL
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| SIGTERM | Polite request to terminate | नरमी से बंद होने का अनुरोध |
| SIGKILL | Forced kill, cannot be caught | ज़बरदस्ती kill, पकड़ा नहीं जा सकता |
| Grace period | Time allowed to shut down | बंद होने के लिए दिया गया समय |
| Graceful shutdown | Finish work, then exit | काम पूरा करके बंद होना |
| STOPSIGNAL | Signal docker stop sends | docker stop जो signal भेजता है |
| init (tini) | Minimal PID 1 for signals | Signals संभालने वाला छोटा PID 1 |

---

## ⚡ 3-Line Summary
English: `docker stop` sends SIGTERM and then SIGKILL after a timeout; `docker kill` sends SIGKILL at once.
Make your app handle SIGTERM and use exec-form CMD so shutdown is clean.
Tune `stop_grace_period` to your longest request or DB flush.
Hindi: `docker stop` SIGTERM भेजता है और timeout के बाद SIGKILL; `docker kill` तुरंत SIGKILL भेजता है।
App में SIGTERM handle करें और exec-form CMD रखें ताकि shutdown साफ हो।
`stop_grace_period` अपनी सबसे लंबी request या DB flush के हिसाब से रखें।

---

## ➡️ Next Topic
**061. docker rm + docker rmi.** After stopping, learn to delete containers and images safely.

---
