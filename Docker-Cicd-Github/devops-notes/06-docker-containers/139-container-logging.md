---

# 139. Container Logging
# हिंदी में: Container Logging

---

## 🔵 Simple Definition (English)
Docker captures everything a container's main process writes to **stdout and stderr** and stores or ships it through a logging driver. The rule: containers should log to stdout/stderr, not to files inside the container.

## 🔵 सरल परिभाषा (Hindi)
Container का main process जो कुछ **stdout और stderr** पर लिखता है, Docker उसे पकड़कर logging driver से store या ship करता है। नियम: containers को stdout/stderr पर log करना चाहिए, container के अंदर files में नहीं।

---

## 🔴 Problem it Solves
Log files inside a container vanish with `docker rm`, fill the writable layer, and need per-app log rotation. On a VPS with 10 services you would need to SSH into 10 containers. Docker's model gives one uniform, central stream per container that tools (`docker logs`, Loki, CloudWatch, ELK) can collect.

## 🔴 यह क्यों बना? (Hindi)
Container के अंदर की log files `docker rm` के साथ ग़ायब हो जाती हैं, writable layer भर देती हैं, और हर app के लिए अलग log rotation चाहिए। 10 services वाले VPS पर 10 containers में SSH करना पड़ता। Docker का मॉडल हर container के लिए एक समान, central stream देता है जिसे `docker logs`, Loki, CloudWatch, ELK जैसे tools collect करते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → App writes a line to stdout/stderr (console.log, print, uvicorn access log)
Step 2 → containerd-shim captures the pipe output of PID 1
Step 3 → dockerd passes each line to the configured log driver (default: json-file)
Step 4 → json-file writes {"log": "...", "stream": "stdout", "time": "..."} to
         /var/lib/docker/containers/<id>/<id>-json.log
Step 5 → `docker logs` reads that file back; other drivers send it elsewhere
Step 6 → Without rotation the file grows forever => disk full
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → App stdout/stderr पर line लिखती है (console.log, print, uvicorn access log)
Step 2 → containerd-shim PID 1 का pipe output पकड़ता है
Step 3 → dockerd हर line configured log driver को देता है (default: json-file)
Step 4 → json-file {"log": "...", "stream": "stdout", "time": "..."} को
         /var/lib/docker/containers/<id>/<id>-json.log में लिखता है
Step 5 → `docker logs` वही file पढ़ता है; दूसरे drivers कहीं और भेजते हैं
Step 6 → Rotation के बिना file हमेशा बढ़ती है => disk full
```

---

## 🟡 Real World Example
A startup's EC2 box went down on a Sunday: disk 100%. Cause: one Node.js container logging every request with the default json-file driver and no rotation, 38 GB in `/var/lib/docker/containers/.../*-json.log`. Fix: `max-size=10m, max-file=3` in `daemon.json` (cap about 30 MB per container) and structured JSON logs shipped to CloudWatch. Now on-call searches by request ID across services instead of SSH-ing around.

## 🟡 Real Example Hindi mein
एक startup का EC2 box रविवार को बंद हो गया: disk 100%। कारण: एक Node.js container default json-file driver पर हर request log कर रहा था, rotation नहीं, `/var/lib/docker/containers/.../*-json.log` में 38 GB। Fix: `daemon.json` में `max-size=10m, max-file=3` (हर container का cap लगभग 30 MB) और structured JSON logs CloudWatch को। अब on-call request ID से सारी services में खोजता है, SSH करके घूमता नहीं।

---

## 💻 Code / Config Example — Basic
```bash
#!/usr/bin/env bash
# logging-basic.sh
docker run -d --name hello alpine:3.20 sh -c 'while true; do echo "tick $(date +%T)"; sleep 1; done'   # prints a line per second
docker logs hello                       # everything printed so far
docker logs -f --tail 5 hello           # follow live output, start from last 5 lines (Ctrl+C to stop)
docker inspect -f '{{.HostConfig.LogConfig.Type}}' hello      # which log driver: json-file
docker inspect -f '{{.LogPath}}' hello                        # path of the JSON log file on the host
docker rm -f hello                      # cleanup

# Per-container rotation
docker run -d --name rot \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  nginx:1.27-alpine
# max-size=10m : rotate when a file reaches 10 MB
# max-file=3   : keep at most 3 files (about 30 MB per container)
docker rm -f rot                        # cleanup
```

## 💻 Code / Config Example — Advanced
```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "5",
    "compress": "true",
    "labels": "app,env"
  }
}
```
```bash
# Save the JSON above as /etc/docker/daemon.json, then:
sudo tee /etc/docker/daemon.json >/dev/null <<'EOF'     # write config (global default for NEW containers)
{
  "log-driver": "json-file",
  "log-opts": { "max-size": "10m", "max-file": "5", "compress": "true" }
}
EOF
sudo systemctl restart docker           # needed to apply; existing containers keep old settings until recreated
docker info --format '{{.LoggingDriver}}'   # verify default driver
```
```yaml
# docker-compose.yml - per-service logging with structured app logs
services:
  api:
    image: myorg/orders-api:1.4.2          # example tag
    environment:
      LOG_FORMAT: json                     # app emits one JSON object per line (easy to parse)
    labels:
      app: orders-api                      # label shown in logs when "labels" log-opt is set
      env: prod                            # environment label
    logging:
      driver: json-file                    # default local driver
      options:
        max-size: "10m"                    # rotate at 10 MB
        max-file: "5"                      # keep 5 files
        labels: "app,env"                  # include these labels in each log record
```
```js
// logger.js - JSON logs to stdout in Node.js (no library needed)
function log(level, msg, extra = {}) {                         // tiny structured logger
  process.stdout.write(JSON.stringify({                         // one JSON object per line
    time: new Date().toISOString(),                             // timestamp
    level,                                                      // info / warn / error
    msg,                                                        // message
    ...extra,                                                   // request id, user id, etc.
  }) + '\n');                                                   // newline = one record
}
module.exports = { log };                                       // export for app use
// usage: log('info', 'order created', { orderId: 42 });        // never log passwords or tokens
```

---

## 🟠 My Stack Integration
**Node.js**: log with `console.log`/pino to stdout. Do not use winston file transports in containers.
**FastAPI**: uvicorn already logs to stdout; add `--access-log` as needed and a JSON formatter. Set `PYTHONUNBUFFERED=1` so lines are not delayed by buffering.
**Nginx**: the official image symlinks `/var/log/nginx/access.log` to stdout and `error.log` to stderr, so `docker logs` works; on the host, Nginx logs stay in `/var/log/nginx` (use logrotate).
**VPS**: set the `daemon.json` defaults on every box; **AWS**: use the `awslogs` driver or ship via CloudWatch agent/Fluent Bit; ECS task definitions use `logConfiguration`.
**Security**: never log secrets, tokens, full card numbers or PII; log files are readable by anyone in the `docker` group (root-equivalent), so restrict that group.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: No log rotation with the default json-file driver.
✅ Correct: set `max-size` and `max-file` globally in `daemon.json`.

❌ Mistake 2: Writing logs to `/var/log/app.log` inside the container.
✅ Correct: write to stdout/stderr; let Docker handle collection.

❌ Mistake 3: Python prints delayed or missing in `docker logs`.
✅ Correct: `PYTHONUNBUFFERED=1` or `python -u`.

❌ Mistake 4: Expecting `daemon.json` changes to affect running containers.
✅ Correct: restart Docker and recreate the containers.

❌ Mistake 5: Unstructured multi-line stack traces that break log search.
✅ Correct: emit JSON, one record per line, including the stack as a field.

---

## 🧠 Tricky Interview Question
The app logs to a file `/app/logs/app.log` and `docker logs` is empty. How do you fix it without changing the code?

Answer: Make the file a symlink to the stream: `RUN ln -sf /dev/stdout /app/logs/app.log` (and `/dev/stderr` for errors), exactly what the official Nginx image does. Alternatively mount a volume and ship the file with a sidecar/agent. Long term, change the app to log to stdout.

---

## ⚫ Interview Questions + Answers

Q1: Where does Docker read container logs from?
A1: The stdout and stderr of the container's main process (PID 1 and its children writing to the same streams).

Q2: What is the default log driver and where are logs stored?
A2: `json-file`, in `/var/lib/docker/containers/<id>/<id>-json.log`.

Q3: How do you stop logs from filling the disk?
A3: `max-size` and `max-file` in `daemon.json` or per container; or use a remote driver.

Q4: Why log to stdout instead of files?
A4: It is the twelve-factor way: no files to rotate, works with any driver and orchestrator, and logs survive independent of the container's filesystem (until removal for json-file).

Q5: Are logs preserved after `docker rm`?
A5: With json-file, no, the file is deleted with the container. Remote drivers keep them externally.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Every container, always: stdout/stderr plus rotation.
- Central collection with CloudWatch/Loki/ELK for several services.

❌ Avoid when:
- Heavy audit trails that must never drop: use a dedicated, reliable pipeline, not just json-file.

---

## 📊 Visual Diagram
```
 [Node/FastAPI/Nginx]
     | stdout/stderr
     v
 [containerd-shim] --> [dockerd + log driver]
                          |-- json-file --> /var/lib/docker/containers/<id>/<id>-json.log --> docker logs
                          |-- awslogs   --> CloudWatch
                          |-- fluentd   --> Fluent Bit --> Loki / Elasticsearch
                          '-- none      --> discarded
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| stdout/stderr | Standard output/error streams | मानक output/error धाराएँ |
| Log driver | Plugin deciding where logs go | Logs कहाँ जाएँ यह तय करने वाला plugin |
| Rotation | Replace old log files with new | पुरानी log files बदलना |
| Structured log | JSON per line | हर line में JSON |
| daemon.json | Docker daemon config file | Docker daemon की config |

---

## ⚡ 3-Line Summary
English: Docker collects stdout/stderr from PID 1 and stores it via a log driver (default json-file).
Always set rotation, and log structured JSON to stdout.
Never log secrets; ship logs off the host for real production.

Hindi: Docker PID 1 का stdout/stderr पकड़कर log driver से रखता है (default json-file)।
Rotation हमेशा लगाएँ और structured JSON stdout पर log करें।
Secrets कभी log न करें; असली production में logs host से बाहर भेजें।

---

## ➡️ Next Topic
**140. Log Drivers**: json-file is only the default; next we compare local, syslog, journald, awslogs, fluentd and when to switch.
