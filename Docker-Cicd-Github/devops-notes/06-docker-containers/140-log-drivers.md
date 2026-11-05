---

# 140. Log Drivers
# हिंदी में: Log Drivers (Logs कहाँ और कैसे जाएँ)

---

## 🔵 Simple Definition (English)
A **log driver** is the Docker plugin that decides where a container's stdout/stderr lines go: a local JSON file (`json-file`, the default), the efficient `local` format, `syslog`, `journald`, `fluentd`, `gelf`, `awslogs` (CloudWatch), `splunk`, or `none`. It is set per container with `--log-driver` or globally in `daemon.json`.

## 🔵 सरल परिभाषा (Hindi)
**Log driver** वह Docker plugin है जो तय करता है कि container के stdout/stderr की lines कहाँ जाएँगी: local JSON file (`json-file`, default), कम जगह लेने वाला `local` format, `syslog`, `journald`, `fluentd`, `gelf`, `awslogs` (CloudWatch), `splunk`, या `none`। यह हर container पर `--log-driver` से या पूरे host पर `daemon.json` में set होता है।

---

## 🔴 Problem it Solves
The default `json-file` driver has **no size limit**. A chatty Node.js API can write tens of GB to `/var/lib/docker/containers/<id>/<id>-json.log` and fill the VPS disk, taking every service down. Also, logs stuck on one host are hard to search across ten servers, and `docker logs` cannot read some drivers. Log drivers let you rotate, compress or ship logs to a central system.

## 🔴 यह क्यों बना? (Hindi)
Default `json-file` driver पर **कोई size limit नहीं** होती। बहुत log करने वाला Node.js API `/var/lib/docker/containers/<id>/<id>-json.log` में दसों GB लिख सकता है और VPS की disk भर देता है, जिससे सारी services गिर जाती हैं। साथ ही एक host पर अटके logs को दस servers में खोजना मुश्किल है। Log drivers rotation, compression या central system में भेजने की सुविधा देते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → App writes to stdout/stderr (console.log, uvicorn access log)
Step 2 → containerd-shim reads the pipe and hands lines to dockerd
Step 3 → dockerd sends every line to the configured log driver
Step 4 → Driver acts: json-file/local write to disk (with rotation options),
         syslog/fluentd/gelf/awslogs ship over network, none drops them
Step 5 → docker logs works for json-file, local and journald (dual logging in
         newer engines also caches logs for remote drivers)
Step 6 → Mode: blocking (default, app waits if driver is slow) or
         non-blocking (ring buffer, may drop lines) via --log-opt mode=non-blocking
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → App stdout/stderr पर लिखता है (console.log, uvicorn access log)
Step 2 → containerd-shim pipe पढ़कर lines dockerd को देता है
Step 3 → dockerd हर line configured log driver को भेजता है
Step 4 → Driver काम करता है: json-file/local disk पर लिखते हैं (rotation options के साथ),
         syslog/fluentd/gelf/awslogs network पर भेजते हैं, none lines फेंक देता है
Step 5 → docker logs json-file, local और journald के लिए चलता है (नए engines में
         dual logging remote drivers के लिए भी local cache रखती है)
Step 6 → Mode: blocking (default, driver धीमा हो तो app रुकता है) या
         non-blocking (ring buffer, lines drop हो सकती हैं) --log-opt mode=non-blocking से
```

---

## 🟡 Real World Example
A ride-booking startup ran 14 containers on a 40 GB VPS. At 2 AM the disk hit 100%, Postgres crashed, and bookings stopped. `du` showed one API container's json log at 31 GB because a retry loop printed an error every millisecond. They set a global default of `max-size=10m, max-file=3` (30 MB cap per container), moved production logs to `awslogs` into CloudWatch for search and alerts, and added a disk-usage alarm.

## 🟡 Real Example Hindi mein
एक ride-booking startup 40 GB VPS पर 14 containers चलाता था। रात 2 बजे disk 100% हो गई, Postgres crash हुआ और bookings रुक गईं। `du` से पता चला एक API container की json log 31 GB थी क्योंकि retry loop हर millisecond में error print कर रहा था। उन्होंने global default `max-size=10m, max-file=3` (हर container पर 30 MB cap) रखा, production logs search और alerts के लिए `awslogs` से CloudWatch में भेजे, और disk-usage alarm लगाया।

---

## 💻 Code / Config Example — Basic

```bash
# Run with the default driver but with rotation (per container)
docker run -d \
  --name api \
  --log-driver json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  -p 3000:3000 \
  node-api:1.0
# --log-driver picks the driver; json-file is the default
# max-size rotates the file when it reaches 10 MB
# max-file keeps only 3 rotated files, so cap is about 30 MB
# -p publishes the Node.js port

# Show which driver a container uses
docker inspect api --format '{{.HostConfig.LogConfig.Type}}'
# prints json-file

# Show the log file path on the host (json-file only)
docker inspect api --format '{{.LogPath}}'
# prints /var/lib/docker/containers/<id>/<id>-json.log

# Disable logging entirely for a noisy throwaway container
docker run --rm --log-driver none alpine:3.20 echo "silent"
# none discards output; docker logs will report an error for this container

# The "local" driver: smaller, compressed, rotated by default (20 MB x 5)
docker run -d --name api2 --log-driver local node-api:1.0
# local is recommended by Docker over json-file when you only need docker logs
```

## 💻 Code / Config Example — Advanced

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "5",
    "compress": "true",
    "labels": "service,env",
    "mode": "non-blocking",
    "max-buffer-size": "4m"
  }
}
```

```bash
# Install the global default: /etc/docker/daemon.json holds the JSON above
sudo tee /etc/docker/daemon.json > /dev/null <<'EOF'
{
  "log-driver": "json-file",
  "log-opts": { "max-size": "10m", "max-file": "5", "compress": "true" }
}
EOF
# tee as root writes the file; quoted EOF disables shell expansion

sudo systemctl restart docker
# new defaults apply only to containers CREATED after restart; recreate old ones

docker info --format '{{.LoggingDriver}}'
# confirms the default driver now active
```

```yaml
# docker-compose.yml: different drivers per service
services:
  api:
    image: ghcr.io/acme/node-api:1.8.3        # Node.js API image (example tag)
    logging:
      driver: awslogs                         # ship to CloudWatch Logs
      options:
        awslogs-region: ap-south-1            # AWS region of the log group
        awslogs-group: /prod/node-api         # log group name (must exist or set awslogs-create-group)
        awslogs-stream: api-1                 # stream name per container
        awslogs-create-group: "true"          # create group if missing (needs logs:CreateLogGroup)
    # the host or instance role needs logs:CreateLogStream and logs:PutLogEvents

  worker:
    image: ghcr.io/acme/fastapi-worker:2.3.0  # FastAPI worker image (example tag)
    logging:
      driver: local                           # compact local storage with built-in rotation
      options:
        max-size: "20m"                       # rotate at 20 MB
        max-file: "5"                         # keep 5 files

  nginx:
    image: nginx:1.27-alpine                  # reverse proxy
    logging:
      driver: json-file                       # default driver
      options:
        max-size: "10m"                       # rotation size
        max-file: "3"                         # rotation count
        tag: "{{.Name}}"                      # tag log entries with container name
```

JSON and YAML were parsed and the shell checked with `bash -n`; the awslogs setup was not run against real AWS.

---

## 🟠 My Stack Integration
On your single VPS: set the global `daemon.json` rotation first (protects the disk for Node.js, FastAPI, React/Nginx, Postgres alike). On AWS EC2/ECS: use `awslogs` (ECS has the `awslogs` driver in the task definition `logConfiguration`). Remember Nginx access logs: the official Nginx image symlinks `/var/log/nginx/access.log` to stdout, so they flow through the same driver.

```yaml
# ECS task definition fragment (JSON shown as YAML for readability)
containerDefinitions:
  - name: node-api                              # container name in the task
    image: 123456789012.dkr.ecr.ap-south-1.amazonaws.com/node-api:1.8.3  # ECR image (example)
    logConfiguration:
      logDriver: awslogs                        # ECS native CloudWatch driver
      options:
        awslogs-group: /ecs/node-api            # CloudWatch log group
        awslogs-region: ap-south-1              # region
        awslogs-stream-prefix: api              # stream prefix, final name api/node-api/<task-id>
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Leaving the default json-file with no `max-size`, then the disk fills.
✅ Correct: Set `log-opts` in `daemon.json`, or use `--log-driver local`.

❌ Mistake 2: Editing `daemon.json` and expecting running containers to change.
✅ Correct: Defaults apply to newly created containers only; run `docker compose up -d --force-recreate`.

❌ Mistake 3: Using a remote driver (fluentd) in blocking mode while the log server is down; the app freezes on `console.log`.
✅ Correct: Use `mode=non-blocking` with a buffer, or `fluentd-async`, and accept possible drops.

❌ Mistake 4: Logging secrets (tokens, passwords) to stdout.
✅ Correct: Mask sensitive fields in the app; logs are stored in plain text and shipped to third parties.

---

## 🧠 Tricky Interview Question
You switched a container to `--log-driver syslog` and `docker logs api` now says "configured logging driver does not support reading". Is it broken?

Answer: No. Older engines can read logs only from `json-file`, `local` and `journald`. With a remote driver the data lives in the external system. Docker 20.10+ added "dual logging": a local cache lets `docker logs` still work for remote drivers (disable with `cache-disabled`). So check the engine version and use the log backend (CloudWatch, Loki) as the source of truth.

---

## ⚫ Interview Questions + Answers

Q1: What is the default log driver and its biggest risk?
A1: `json-file`. It has no rotation by default, so logs can fill the disk.

Q2: json-file vs local?
A2: `local` uses a compact binary format, compresses rotated files and has sane default rotation (20 MB x 5). `json-file` is human-readable JSON per line and easier for external tools to tail.

Q3: How do you change the driver for all containers?
A3: `log-driver` and `log-opts` in `/etc/docker/daemon.json`, then restart the daemon and recreate containers.

Q4: Blocking vs non-blocking mode?
A4: Blocking: the app write waits for the driver, so no loss but possible stalls. Non-blocking: writes go into a memory ring buffer (`max-buffer-size`), the app never stalls but lines can be dropped if the buffer fills.

Q5: Why log to stdout and not a file inside the container?
A5: Files vanish with the container, grow the writable layer, and need extra rotation. stdout is captured uniformly by the driver and fits twelve-factor logging.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- `json-file`/`local` with rotation: single VPS
- `awslogs`/`fluentd`/`gelf`: many hosts, central search, alerts
- `none`: batch jobs whose output is useless

❌ Avoid when:
- `none` for production services (you lose all debugging data)
- Blocking remote drivers without a fallback
- Default unlimited `json-file` anywhere

---

## 📊 Visual Diagram
```
 app (stdout/stderr)
        │
        ▼
  containerd-shim ──► dockerd ──► LOG DRIVER
                                   │
      ┌───────────┬────────────────┼───────────────┬─────────────┐
      ▼           ▼                ▼               ▼             ▼
  json-file     local          syslog/journald  fluentd/gelf   awslogs
  (+rotation)  (compressed)    (host logging)   (to Loki/ELK)  (CloudWatch)
      │           │
      └─► docker logs reads here
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Log driver | Plugin that routes container logs | Logs का रास्ता तय करने वाला plugin |
| json-file | Default driver, JSON lines on disk | Default, disk पर JSON lines |
| local | Compact rotated on-disk format | कम जगह वाला format |
| max-size / max-file | Rotation size and count | Rotation का आकार और गिनती |
| non-blocking | Buffer so app never waits | Buffer ताकि app न रुके |
| Dual logging | Local cache for remote drivers | Remote drivers के लिए local cache |

---

## ⚡ 3-Line Summary
English: A log driver decides where container output goes; the default `json-file` has no size limit. Set rotation in `daemon.json` or use `local`, and ship to CloudWatch or fluentd for multi-host setups. Recreate containers after changing defaults.
Hindi: Log driver तय करता है कि container का output कहाँ जाए; default `json-file` की कोई size limit नहीं होती। `daemon.json` में rotation set करो या `local` इस्तेमाल करो, और कई hosts हों तो CloudWatch या fluentd पर भेजो। Defaults बदलने के बाद containers दोबारा बनाओ।

---

## ➡️ Next Topic
**141. docker logs Options**: now learn to read those logs efficiently with `--tail`, `--since`, `-f`, and timestamps.

---
