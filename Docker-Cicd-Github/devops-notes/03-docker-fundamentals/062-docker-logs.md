---

# 062. docker logs
# हिंदी में: docker logs

---

## 🔵 Simple Definition (English)
`docker logs` prints what a container wrote to **stdout and stderr**. You can follow it live (`-f`), show only recent lines (`--tail`), add timestamps (`-t`) and filter by time (`--since`, `--until`). It works with the default `json-file` driver (and `local`, `journald`).

## 🔵 सरल परिभाषा (Hindi)
`docker logs` वह print करता है जो container ने **stdout और stderr** पर लिखा। आप इसे live follow कर सकते हैं (`-f`), सिर्फ हाल की lines देख सकते हैं (`--tail`), timestamps जोड़ सकते हैं (`-t`), और समय से filter कर सकते हैं (`--since`, `--until`)। यह default `json-file` driver (और `local`, `journald`) के साथ काम करता है।

---

## 🔴 Problem it Solves
Containers are isolated, so you cannot just `tail -f /var/log/app.log` on the host. Docker captures the main process's stdout/stderr and stores it, giving one standard way to read logs for any container, even one that has already crashed.

## 🔴 यह क्यों बना? (Hindi)
Containers isolated होते हैं, इसलिए host पर सीधे `tail -f /var/log/app.log` नहीं कर सकते। Docker main process का stdout/stderr पकड़कर store करता है, जिससे किसी भी container के, यहाँ तक कि crash हो चुके के भी, logs पढ़ने का एक standard तरीका मिलता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Your app writes to stdout/stderr (console.log, print, uvicorn access log, nginx access_log /dev/stdout)
Step 2 → The Docker logging driver captures each line (default: json-file)
Step 3 → Driver writes JSON lines to /var/lib/docker/containers/<id>/<id>-json.log with stream + timestamp
Step 4 → docker logs reads that file through the daemon and prints it
Step 5 → -f keeps the stream open; --tail N limits output; --since 10m limits by time
Step 6 → Log rotation (max-size/max-file) deletes the oldest data; removing the container deletes its logs
```

Important: logs written to a **file inside the container** (e.g. `/app/app.log`) are NOT shown. Official nginx image links `/var/log/nginx/access.log` to `/dev/stdout` and `error.log` to `/dev/stderr` for this reason.

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → आपका app stdout/stderr पर लिखता है (console.log, print, uvicorn access log, nginx access_log /dev/stdout)
Step 2 → Docker logging driver हर line पकड़ता है (default: json-file)
Step 3 → Driver /var/lib/docker/containers/<id>/<id>-json.log में stream + timestamp के साथ JSON lines लिखता है
Step 4 → docker logs daemon के ज़रिए वही file पढ़कर print करता है
Step 5 → -f stream खुली रखता है; --tail N output सीमित करता है; --since 10m समय से सीमित करता है
Step 6 → Log rotation (max-size/max-file) सबसे पुराना data हटाता है; container remove होने पर उसके logs भी हट जाते हैं
```

ज़रूरी: **container के अंदर file** में लिखे logs (जैसे `/app/app.log`) नहीं दिखते। इसीलिए official nginx image `/var/log/nginx/access.log` को `/dev/stdout` और `error.log` को `/dev/stderr` से link करती है।

---

## 🟡 Real World Example
A user reports checkout failures at 14:05. On the VPS you run `docker logs --since 14:00 --until 14:10 api | grep -i error` and see `sqlalchemy.exc.OperationalError: too many connections`. The DB connection pool was misconfigured. For a fleet, Swiggy-like teams ship these same stdout logs to ELK/Loki/CloudWatch so nobody has to SSH into servers.

## 🟡 Real Example Hindi mein
एक user बताता है कि 14:05 पर checkout fail हुआ। VPS पर आप `docker logs --since 14:00 --until 14:10 api | grep -i error` चलाते हैं और `sqlalchemy.exc.OperationalError: too many connections` दिखता है। DB connection pool गलत configured था। बड़े fleet में Swiggy जैसी teams यही stdout logs ELK/Loki/CloudWatch में भेजती हैं ताकि किसी को server पर SSH न करना पड़े।

---

## 💻 Code / Config Example — Basic

```bash
# --- docker logs basics ---
docker logs api                                  # all logs from start (can be huge)
docker logs --tail 100 api                       # last 100 lines only
docker logs -f api                               # follow live (Ctrl+C stops following, not the container)
docker logs -f --tail 50 api                     # last 50 lines, then follow
docker logs -t api                               # prefix each line with RFC3339 timestamp
docker logs --since 10m api                      # only last 10 minutes (units: s, m, h)
docker logs --since 2026-01-15T14:00:00 --until 2026-01-15T14:10:00 api   # exact window (example dates)
docker logs api 2>&1 | grep -i error             # stderr is separate: 2>&1 merges it before grep
docker logs api > api.log 2>&1                   # save to a file
docker compose logs -f --tail 100 api nginx      # compose: several services at once
```

## 💻 Code / Config Example — Advanced

```yaml
# docker-compose.yml - production logging: rotation, tags, structured logs from Python
services:
  api:
    build: ./api                                 # FastAPI image
    restart: unless-stopped                      # keep running
    logging:                                     # per-service logging config
      driver: json-file                          # default driver (docker logs works)
      options:
        max-size: "10m"                          # rotate when a file reaches 10 MB
        max-file: "5"                            # keep 5 rotated files (about 50 MB max)
        tag: "{{.Name}}"                         # tag with container name
    environment:
      PYTHONUNBUFFERED: "1"                      # flush print/log output immediately
      LOG_LEVEL: "info"                          # app log level
  nginx:
    image: nginx:1.27-alpine                     # example tag; access/error logs go to stdout/stderr
    restart: unless-stopped
    ports:
      - "80:80"                                  # public HTTP
    logging:
      driver: local                              # Docker's compact rotated driver (docker logs still works)
      options:
        max-size: "10m"                          # rotate at 10 MB
        max-file: "3"                            # keep 3 files
```

```python
# api/logging_setup.py - JSON logs to stdout so docker logs and log shippers can parse them
# Verified syntax with: python3 -m py_compile logging_setup.py
import json                                      # build JSON lines
import logging                                   # standard logging module
import sys                                       # access stdout

class JsonFormatter(logging.Formatter):          # custom formatter producing one JSON object per line
    def format(self, record):                    # called for every log record
        payload = {
            "time": self.formatTime(record),     # timestamp
            "level": record.levelname,           # INFO, ERROR...
            "logger": record.name,               # logger name
            "message": record.getMessage(),      # the log text
        }
        if record.exc_info:                      # include stack trace if present
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload)               # one line = one event

def setup(level: str = "INFO") -> None:          # call once at app startup
    handler = logging.StreamHandler(sys.stdout)  # write to stdout, NOT to a file
    handler.setFormatter(JsonFormatter())        # use JSON format
    root = logging.getLogger()                   # root logger
    root.handlers = [handler]                    # replace default handlers
    root.setLevel(level)                         # set level
```

```bash
# Global daemon default (all containers) in /etc/docker/daemon.json, then: sudo systemctl restart docker
# {
#   "log-driver": "json-file",
#   "log-opts": { "max-size": "10m", "max-file": "3" }
# }
# Applies to newly created containers only; recreate existing ones to apply.
```

---

## 🟠 My Stack Integration
- **FastAPI**: `uvicorn` logs to stdout; set `PYTHONUNBUFFERED=1`; use JSON logs above.
- **Node.js**: `console.log` or pino (JSON) to stdout; never write log files inside the container.
- **React (Nginx)**: access/error logs go to stdout/stderr automatically in the official image.
- **VPS**: `docker compose logs -f` for debugging; ship to Loki/Promtail or CloudWatch agent for retention.
- **AWS**: ECS uses the `awslogs` driver to CloudWatch Logs; on EC2 install the CloudWatch agent or use `--log-driver=awslogs` with IAM permissions.
- **Note**: `docker logs` works only for drivers that support reading (json-file, local, journald); with `awslogs`/`syslog` it may not (newer Docker versions use dual logging cache).

Security: logs often leak tokens, passwords, emails and card numbers. Never log request bodies or Authorization headers; mask sensitive fields; restrict who can run `docker logs` (docker group) and who can read `/var/lib/docker`. Rotate logs, since unbounded logs are also a denial-of-service via disk.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: No rotation, so a verbose container fills the disk with a multi-GB log file.
✅ Correct: Set `max-size` and `max-file` globally or per service.

❌ Mistake 2: Logging to a file inside the container and then seeing empty `docker logs`.
✅ Correct: Log to stdout/stderr (or symlink the log file to `/dev/stdout`).

❌ Mistake 3: Running `docker logs api` on a 2 GB log, flooding the terminal.
✅ Correct: Use `--tail` and `--since`.

❌ Mistake 4: Python prints missing/delayed because of buffering.
✅ Correct: `PYTHONUNBUFFERED=1` or `python -u`.

❌ Mistake 5: Deleting a crashed container before reading its logs.
✅ Correct: Read `docker logs` first (container must still exist), then remove it.

---

## 🧠 Tricky Interview Question
`docker logs -f api | grep ERROR` shows nothing, though the app is clearly logging errors on screen when you run `docker logs api`. Why?

Answer: Many apps write errors to **stderr**, and `docker logs` replays stderr on the CLI's stderr, not stdout. A pipe only captures stdout, so grep sees nothing. Use `docker logs -f api 2>&1 | grep ERROR`. (In Compose, `docker compose logs` merges both streams.)

---

## ⚫ Interview Questions + Answers

Q1: Where does Docker store container logs by default?
A1: `/var/lib/docker/containers/<container-id>/<container-id>-json.log` using the `json-file` driver.

Q2: What does `docker logs -f` do when the container restarts?
A2: The follow typically ends when the container stops; re-run it after restart (or use `docker compose logs -f`). The history stays until the container is recreated.

Q3: How do you prevent logs from filling the disk?
A3: Configure rotation (`max-size`, `max-file`) in `daemon.json` or per service, or use the `local` driver; ship logs elsewhere for retention.

Q4: Why log to stdout instead of files in containers?
A4: Containers are ephemeral; stdout is captured by the runtime, works with any log driver/orchestrator, and avoids managing log files and volumes (twelve-factor app).

Q5: How do you view logs of a container that already exited?
A5: `docker ps -a` to find it, then `docker logs <name or id>`; it works until the container is removed.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Debugging crashes, startup errors, slow requests.
- Quick checks after a deploy.

❌ Avoid when:
- Long-term analysis and alerting: use a central log system (Loki, ELK, CloudWatch).
- Searching across many hosts or weeks of history.

---

## 📊 Visual Diagram
```
  app process
   | stdout / stderr
   v
 +---------------------+    json-file driver    +--------------------------------+
 | containerd-shim     |----------------------->| /var/lib/docker/containers/    |
 +---------------------+   rotate at max-size   |   <id>/<id>-json.log           |
                                                +---------------+----------------+
                                                                |
                         docker logs -f --tail 100 api  <-------+
                                                                |
                               (optional shipper: Promtail/Fluent Bit -> Loki / CloudWatch)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| stdout/stderr | Standard output and error streams | Standard output और error streams |
| Logging driver | How Docker stores/forwards logs | Docker logs कैसे store/forward करे |
| json-file | Default driver writing JSON lines | JSON lines लिखने वाला default driver |
| Rotation | Delete/rotate old logs by size | Size के हिसाब से पुराने logs हटाना |
| Tail | Last N lines | आखिरी N lines |
| Log shipper | Agent sending logs to a central system | Logs को central system में भेजने वाला agent |

---

## ⚡ 3-Line Summary
English: `docker logs` shows a container's stdout/stderr; use `-f`, `--tail`, `--since`.
Always log to stdout, enable rotation, and never log secrets.
Ship logs to a central system for retention.
Hindi: `docker logs` container का stdout/stderr दिखाता है; `-f`, `--tail`, `--since` इस्तेमाल करें।
हमेशा stdout पर log करें, rotation चालू रखें, और secrets कभी log न करें।
Retention के लिए logs central system में भेजें।

---

## ➡️ Next Topic
**063. docker exec.** Logs tell what happened; exec lets you go inside a running container to investigate.

---
