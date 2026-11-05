---

# 141. docker logs Options
# हिंदी में: docker logs के Options

---

## 🔵 Simple Definition (English)
`docker logs` prints what a container wrote to stdout and stderr. Its options control how much and which part you see: `-f` (follow), `--tail N`, `--since`, `--until`, `-t` (timestamps), and `--details`. In Compose the equivalent is `docker compose logs`.

## 🔵 सरल परिभाषा (Hindi)
`docker logs` वह print करता है जो container ने stdout और stderr पर लिखा। इसके options तय करते हैं कि कितना और कौन सा हिस्सा दिखे: `-f` (follow), `--tail N`, `--since`, `--until`, `-t` (timestamps), और `--details`। Compose में इसका बराबर `docker compose logs` है।

---

## 🔴 Problem it Solves
Without options, `docker logs api` dumps the entire history: millions of lines scroll past and you cannot see the error that just happened. During an incident you need "the last 100 lines", "everything in the last 10 minutes" or "live stream while I reproduce the bug", not a flood.

## 🔴 यह क्यों बना? (Hindi)
Options के बिना `docker logs api` पूरा history उगल देता है: लाखों lines निकल जाती हैं और अभी हुआ error दिखता ही नहीं। Incident के समय आपको "आखिरी 100 lines", "पिछले 10 मिनट का सब कुछ" या "bug reproduce करते समय live stream" चाहिए, बाढ़ नहीं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → docker logs asks dockerd to read the container's log via its driver
Step 2 → Driver must be readable (json-file, local, journald, or dual-logging cache)
Step 3 → Filters apply: --since/--until by timestamp, --tail by line count
Step 4 → Output: stdout lines go to your stdout, stderr lines go to your stderr
Step 5 → With -f the command keeps the stream open until Ctrl+C or container exit
Step 6 → Pipe through grep/jq/less, or redirect 2>&1 to combine both streams
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → docker logs, dockerd से container का log उसके driver के ज़रिए पढ़ने को कहता है
Step 2 → Driver readable होना चाहिए (json-file, local, journald, या dual-logging cache)
Step 3 → Filters लगते हैं: --since/--until timestamp से, --tail line count से
Step 4 → Output: stdout lines आपके stdout पर, stderr lines आपके stderr पर
Step 5 → -f के साथ command stream खुला रखता है जब तक Ctrl+C या container exit
Step 6 → grep/jq/less में pipe करो, या दोनों streams मिलाने को 2>&1 से redirect करो
```

---

## 🟡 Real World Example
At 9:12 PM a food-ordering app gets "payment failed" complaints. The on-call engineer runs `docker logs --since 15m -t api 2>&1 | grep -i "payment"` and finds `ECONNRESET` to the gateway starting at 9:03 PM. Then `docker logs -f --tail 0 api` shows live traffic while a test order is placed, confirming the retries. Total time to cause: 2 minutes, because options narrowed millions of lines to a handful.

## 🟡 Real Example Hindi mein
रात 9:12 बजे एक food-ordering app पर "payment failed" की शिकायतें आती हैं। On-call engineer `docker logs --since 15m -t api 2>&1 | grep -i "payment"` चलाता है और 9:03 बजे से gateway पर `ECONNRESET` मिलता है। फिर `docker logs -f --tail 0 api` से test order के समय live traffic देखता है और retries confirm होते हैं। कारण तक 2 मिनट, क्योंकि options ने लाखों lines को मुट्ठी भर में बदल दिया।

---

## 💻 Code / Config Example — Basic

```bash
# Last 100 lines only (most common command in an incident)
docker logs --tail 100 api
# --tail N prints the last N lines; "all" is the default

# Follow new lines live, starting from now
docker logs -f --tail 0 api
# -f keeps streaming; --tail 0 skips the old history; Ctrl+C stops

# Add timestamps (RFC3339 nano) to every line
docker logs -t --tail 20 api
# -t prefixes UTC time, useful when the app itself prints no time

# Logs from the last 10 minutes
docker logs --since 10m api
# --since accepts durations (10m, 2h) or timestamps (2025-01-31T09:00:00)

# Logs inside a window
docker logs --since 2025-01-31T09:00:00 --until 2025-01-31T09:30:00 api
# --until sets the end of the window; both use the daemon's timezone rules

# Search errors (stderr merged into stdout first)
docker logs api 2>&1 | grep -i error
# 2>&1 sends stderr into the pipe, otherwise grep misses error output

# Only stderr (errors) visible, hide normal output
docker logs api 1>/dev/null
# discards stdout, leaving only what the app wrote to stderr
```

## 💻 Code / Config Example — Advanced

```bash
#!/usr/bin/env bash
# incident-logs.sh: collect evidence from a container for the last N minutes
set -euo pipefail                                   # stop on any error or unset variable

CONTAINER="${1:?usage: incident-logs.sh <container> [minutes]}"   # required first argument
MINUTES="${2:-15}"                                  # default window is 15 minutes
OUT="/tmp/${CONTAINER}-$(date +%Y%m%d-%H%M%S).log"  # unique output filename

# Fail early if the container does not exist
docker inspect "$CONTAINER" > /dev/null             # non-zero exit if missing

# Check that the driver can be read, otherwise explain
DRIVER=$(docker inspect --format '{{.HostConfig.LogConfig.Type}}' "$CONTAINER")   # read driver name
echo "log driver: $DRIVER" >&2                      # print info on stderr

# Save timestamped logs of the window, stdout and stderr merged
docker logs --timestamps --since "${MINUTES}m" "$CONTAINER" > "$OUT" 2>&1   # write to file

# Show a quick summary: count of lines and top error messages
echo "lines: $(wc -l < "$OUT")" >&2                # total lines saved
grep -iE 'error|fatal|exception' "$OUT" \
  | sed -E 's/^[^ ]+ //' \
  | sort | uniq -c | sort -rn | head -5 >&2         # top 5 repeated error lines
echo "saved to $OUT" >&2                            # tell the user where the file is
```

```bash
# Structured JSON logs (pino for Node.js, structlog for FastAPI): query with jq
docker logs --since 5m api 2>&1 \
  | jq -R 'fromjson? | select(.level >= 50) | {time, msg, reqId}'
# -R reads raw lines; fromjson? ignores non-JSON lines; level >= 50 is pino "error" and above

# Docker Compose: all services, merged, with service name prefix
docker compose logs -f --tail 50 --timestamps api web worker
# compose logs shows multiple services; -f follows; list services to filter

# Raw log file on the host (json-file driver, needs root); fastest for huge files
sudo tail -n 200 "$(docker inspect --format '{{.LogPath}}' api)"
# reads the file directly, bypassing the daemon
```

Both scripts passed `bash -n`. They were not run against a live container here.

---

## 🟠 My Stack Integration
Node.js: log JSON with `pino`; FastAPI: `uvicorn --log-config` or structlog to stdout. Nginx container: access and error logs are linked to stdout/stderr, so `docker logs web` shows both. On the VPS the incident routine becomes: `docker compose ps`, `docker compose logs --since 15m api web`, then `docker logs -f` while retrying the request.

```yaml
# docker-compose.yml: keep logs readable and bounded for the commands above
services:
  api:
    image: ghcr.io/acme/node-api:1.8.3     # Node.js API (example tag)
    environment:
      LOG_LEVEL: info                      # pino level; use debug temporarily
    logging:
      driver: json-file                    # a driver that docker logs can read
      options:
        max-size: "10m"                    # rotation size
        max-file: "3"                      # rotation count
  web:
    image: nginx:1.27-alpine               # React static files + reverse proxy
    logging:
      driver: json-file                    # same driver for consistency
      options:
        max-size: "10m"                    # rotation size
        max-file: "3"                      # rotation count
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `docker logs api | grep error` finds nothing though errors exist.
✅ Correct: Errors are on stderr. Use `docker logs api 2>&1 | grep error`.

❌ Mistake 2: Running `docker logs -f api` without `--tail`, so the terminal floods with old history.
✅ Correct: `docker logs -f --tail 50 api` (or `--tail 0` for only new lines).

❌ Mistake 3: Using `--since 1h` on a host with a different timezone and misreading timestamps.
✅ Correct: Prefer relative durations; remember `-t` prints UTC.

❌ Mistake 4: Expecting old logs after `docker rm` or `--rm`.
✅ Correct: Logs belong to the container; once removed they are gone. Ship logs to a central store first.

---

## 🧠 Tricky Interview Question
`docker logs -f api` shows nothing even though the app is running and serving requests. Name three causes.

Answer: (1) The app writes to a file (e.g. `/var/log/app.log`), not stdout/stderr, so Docker captures nothing; (2) the log driver is `none` or a remote driver without a local cache; (3) stdout is block-buffered because it is not a TTY (Python prints appear in bursts, fix with `PYTHONUNBUFFERED=1` or `python -u`). Another cause: the process is a shell wrapper that did not `exec` the app, or logs were rotated away. Diagnose with `docker inspect` for driver and `docker exec api ls -l /proc/1/fd` to see where fd 1 points.

---

## ⚫ Interview Questions + Answers

Q1: How do you see logs of a stopped container?
A1: `docker logs <name>` works as long as the container still exists (not removed). Use `docker ps -a` to find it.

Q2: Difference between `--since` and `--until`?
A2: `--since` returns logs after the given time or relative duration; `--until` returns logs before it. Combine them for a window.

Q3: Why does `docker logs -f` keep running after the container exits?
A3: In many versions, `-f` ends when the container stops; if it restarts (restart policy) the stream may end and need re-running. Use `docker compose logs -f` which reattaches more gracefully, or a log shipper.

Q4: How can you get timestamps if the app does not print them?
A4: `docker logs -t` adds Docker's receive time to each line.

Q5: How do you view logs for multiple services at once?
A5: `docker compose logs -f service1 service2`; the output is prefixed with service names and interleaved.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Quick debugging on a single host
- Verifying a deploy or health-check failure
- Collecting evidence with `--since`

❌ Avoid when:
- You need search over weeks of history (use Loki, ELK, CloudWatch)
- Many hosts are involved (centralize logs)
- Containers are ephemeral and removed after failure

---

## 📊 Visual Diagram
```
 docker logs [OPTIONS] CONTAINER
        │
        ▼
 ┌──────────────── full log stream (oldest ──► newest) ──────────────┐
 │ . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . │
 └───────────────────────────────────────────────────────────────────┘
   │--since 15m ──►│                    │◄── --tail 100
   └───────────────┴─── window you see ─┘
   -t adds time to each line      -f keeps the pipe open for new lines
   stdout ─► your stdout    stderr ─► your stderr (use 2>&1 to merge)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| --tail | Show last N lines | आखिरी N lines |
| -f / --follow | Stream new lines | नई lines live |
| --since / --until | Time window | समय की खिड़की |
| -t | Add timestamps | Timestamp जोड़ना |
| stderr | Error output stream | Error output stream |
| PYTHONUNBUFFERED | Python env that disables buffering | Python का buffering बंद करने वाला env |

---

## ⚡ 3-Line Summary
English: `docker logs` reads container stdout and stderr; use `--tail`, `--since`, `-t` and `-f` to focus. Merge stderr with `2>&1` when piping. It needs a readable log driver and disappears with the container.
Hindi: `docker logs` container का stdout और stderr पढ़ता है; focus करने को `--tail`, `--since`, `-t` और `-f` इस्तेमाल करो। Pipe करते समय stderr को `2>&1` से मिलाओ। इसे readable log driver चाहिए और यह container के साथ मिट जाता है।

---

## ➡️ Next Topic
**142. Container Health Checks**: logs tell you what happened; health checks tell Docker whether the app is actually working right now.

---
