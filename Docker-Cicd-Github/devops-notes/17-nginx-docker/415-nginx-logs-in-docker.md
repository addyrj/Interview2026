# 415. Nginx Logs in Docker
# हिंदी में: Docker में Nginx Logs

---

## 🔵 Simple Definition (English)
In Docker, Nginx should write its **access log to stdout** and **error log to stderr**. The official image already symlinks `/var/log/nginx/access.log` to `/dev/stdout` and `error.log` to `/dev/stderr`, so `docker logs` works and the Docker logging driver (json-file, local, Loki, CloudWatch) collects and rotates them.

## 🔵 सरल परिभाषा (Hindi)
Docker में Nginx का **access log stdout** पर और **error log stderr** पर लिखना चाहिए। Official image में `/var/log/nginx/access.log`, `/dev/stdout` से और `error.log`, `/dev/stderr` से पहले से symlink है, इसलिए `docker logs` चलता है और Docker logging driver (json-file, local, Loki, CloudWatch) उन्हें इकट्ठा और rotate करता है।

---

## 🔴 Problem it Solves
- Log files inside a container vanish when the container is replaced on every deploy.
- Unrotated log files fill the VPS disk (the classic 3 AM "no space left on device").
- Plain-text logs are hard to search; JSON logs can be filtered by status, latency or request id.
- Several containers log at once; you need one place and one format.

## 🔴 यह क्यों बना? (Hindi)
- Container के अंदर की log files हर deploy पर container बदलते ही खो जाती हैं।
- Rotate न होने वाली logs VPS की disk भर देती हैं (रात 3 बजे "no space left on device")।
- Plain-text logs में search मुश्किल है; JSON logs को status, latency या request id से filter कर सकते हैं।
- कई containers एक साथ log करते हैं; एक जगह और एक format चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Nginx writes access_log to /var/log/nginx/access.log (a symlink to /dev/stdout)
Step 2 → error_log goes to /dev/stderr (symlink)
Step 3 → Docker captures both streams of PID 1 through the logging driver
Step 4 → Driver stores them (json-file) with max-size/max-file rotation
Step 5 → `docker logs -f web` reads them; Promtail/Loki/CloudWatch can ship them (422/423)
Step 6 → Custom log_format (JSON) adds request_time, upstream_response_time, request_id
Step 7 → Use `X-Request-Id` to correlate Nginx log line with app log line
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Nginx access_log को /var/log/nginx/access.log में लिखता है (जो /dev/stdout का symlink है)
Step 2 → error_log /dev/stderr (symlink) पर जाता है
Step 3 → Docker logging driver से PID 1 की दोनों streams पकड़ता है
Step 4 → Driver उन्हें (json-file) max-size/max-file rotation के साथ रखता है
Step 5 → `docker logs -f web` से पढ़ो; Promtail/Loki/CloudWatch उन्हें ship कर सकते हैं (422/423)
Step 6 → Custom log_format (JSON) में request_time, upstream_response_time, request_id जुड़ते हैं
Step 7 → `X-Request-Id` से Nginx की log line और app की log line जोड़ो
```

---

## 🟡 Real World Example
A SaaS on a single VPS filled a 40 GB disk in a week because `json-file` logs had no limit and the access log recorded every 10-second health probe. Fix: `max-size: 10m`, `max-file: 5`, `access_log off` for `/healthz`, JSON format, and shipping to Loki. Disk use became flat, and on-call could grep `status>=500` with latency in seconds.

## 🟡 Real Example Hindi mein
एक SaaS ने single VPS पर हफ्ते भर में 40 GB disk भर दी क्योंकि `json-file` logs पर limit नहीं थी और हर 10 सेकंड का health probe access log में लिखा जा रहा था। Fix: `max-size: 10m`, `max-file: 5`, `/healthz` के लिए `access_log off`, JSON format, और Loki में shipping। Disk use स्थिर हो गया और on-call `status>=500` को latency के साथ तुरंत grep कर सका।

---

## 💻 Code / Config Example — Basic
```yaml
# docker-compose.yml  (basic: default stdout logging + rotation)
services:
  web:
    image: nginx:1.27-alpine               # example tag
    ports:
      - "80:80"                            # HTTP
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro   # our config
    logging:                               # Docker logging driver settings
      driver: json-file                    # default driver
      options:
        max-size: "10m"                    # rotate when file reaches 10 MB
        max-file: "5"                      # keep 5 rotated files (50 MB max)
```

```bash
# Everyday log commands (run on the VPS)
docker logs web                  # print all stored logs
docker logs -f --tail 100 web    # follow the last 100 lines live
docker logs --since 10m web      # only the last 10 minutes
docker compose logs -f web api   # several services together
docker exec web nginx -T | head  # dump the effective config (also validates it)
```

## 💻 Code / Config Example — Advanced
```nginx
# nginx.conf  (production: JSON access log + request id + per-location control)
events { worker_connections 1024; }
http {
  # map creates $req_id: use client's X-Request-Id if present, else Nginx's own $request_id
  map $http_x_request_id $req_id {
    default   $http_x_request_id;          # keep upstream-supplied id
    ""        $request_id;                 # generate a 32-hex id when missing
  }
  # JSON log format (escape=json makes quotes safe)
  log_format json_combined escape=json
    '{'
      '"time":"$time_iso8601",'            # ISO timestamp
      '"remote_addr":"$remote_addr",'      # client IP (real IP only if realip is set)
      '"request_id":"$req_id",'            # correlation id
      '"method":"$request_method",'        # GET/POST
      '"uri":"$request_uri",'              # path + query (do NOT put tokens in query!)
      '"status":$status,'                  # numeric status
      '"bytes":$body_bytes_sent,'          # response size
      '"req_time":$request_time,'          # total time in seconds
      '"upstream_time":"$upstream_response_time",'  # backend time (string, may be "-")
      '"ua":"$http_user_agent"'            # browser / client
    '}';
  access_log /var/log/nginx/access.log json_combined;  # symlink -> /dev/stdout in the image
  error_log  /var/log/nginx/error.log warn;            # symlink -> /dev/stderr; warn and above
  server_tokens off;                       # hide version in headers and error pages
  server {
    listen 80;
    location = /healthz {
      access_log off;                      # skip noisy probes
      return 200 "ok\n";
    }
    location /api/ {
      proxy_set_header X-Request-Id $req_id;   # pass id to Node.js/FastAPI
      add_header X-Request-Id $req_id always;  # also return it to the client
      proxy_pass http://api:3000;
    }
    location ~* \.(js|css|png|jpg|svg|woff2)$ {
      access_log off;                      # static assets: usually not worth logging
      expires 7d;
    }
  }
}
```

```yaml
# docker-compose.yml  (production logging: local driver, and optional Loki driver)
services:
  web:
    image: nginx:1.27-alpine
    ports: ["80:80"]
    volumes: ["./nginx.conf:/etc/nginx/nginx.conf:ro"]
    logging:
      driver: local                        # compact, rotated by default (20 MB x 5)
      options:
        max-size: "20m"                    # per-file size
        max-file: "5"                      # number of files
        compress: "true"                   # gzip rotated files
    # Alternative (needs the Loki Docker plugin installed, see 422):
    # logging:
    #   driver: loki
    #   options:
    #     loki-url: "http://localhost:3100/loki/api/v1/push"
```
Note: `docker logs` works with `json-file`, `local` and `journald` drivers; with remote-only drivers behaviour depends on the Docker version. Not run locally here.

---

## 🟠 My Stack Integration
- **Node.js / FastAPI**: log JSON to stdout too; log the `X-Request-Id` from the header (pino / `structlog`) so Nginx and app lines match.
- **React**: static files; disable access logs for assets; use browser errors via Sentry (428).
- **VPS**: logrotate is NOT needed for stdout; Docker rotation handles it. For file logs on a bind-mount use `logrotate` + `nginx -s reopen`.
- **AWS**: use `awslogs` / `awsfirelens` driver, or Promtail on EC2 to Loki; CloudWatch Logs Insights for queries.

```yaml
# Log files on a bind mount (only if you must keep files on host)
services:
  web:
    image: nginx:1.27-alpine
    volumes:
      - ./logs:/var/log/nginx              # bind-mount: this REPLACES the stdout symlinks with real files
```
**Security**: logs may contain IPs, emails in query strings, and tokens. Never log `Authorization` headers or cookies; redact query secrets; restrict log access; set retention to match your privacy policy.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: No `max-size` on json-file, disk fills.
✅ Correct: Set `max-size`/`max-file` per service or in `/etc/docker/daemon.json` (`log-driver`, `log-opts`).

❌ Mistake 2: Bind-mounting `./logs:/var/log/nginx` and then wondering why `docker logs` is empty.
✅ Correct: Mounting over that path removes the stdout symlinks; either keep stdout or manage files with logrotate.

❌ Mistake 3: Seeing the proxy IP (`172.18.0.1`) as client address.
✅ Correct: Use `set_real_ip_from` + `real_ip_header X-Forwarded-For` behind a load balancer.

❌ Mistake 4: Logging `$upstream_response_time` as a bare number in JSON; it can be `-` or comma-separated.
✅ Correct: Quote it as a string or parse it in the log pipeline.

❌ Mistake 5: `error_log ... debug` left on in production.
✅ Correct: Use `warn`/`error`; enable `debug` briefly only (needs debug build).

---

## 🧠 Tricky Interview Question
After you changed the daemon `log-opts` max-size, existing containers still grow without limit. Why?

Answer: Logging driver settings are fixed at container creation. `daemon.json` changes affect only new containers, and Docker needs a restart to read them. You must recreate containers (`docker compose up -d --force-recreate`). Also `docker logs` shows only what the driver keeps, so rotation deletes old lines.

---

## ⚫ Interview Questions + Answers

Q1: Why log to stdout in containers?
A1: Containers are disposable; stdout lets the platform collect and rotate logs independently, matching the twelve-factor "logs as streams" rule.

Q2: How does the Nginx image make `access.log` go to stdout?
A2: The Dockerfile creates symlinks `/var/log/nginx/access.log -> /dev/stdout` and `error.log -> /dev/stderr`.

Q3: How to find the slowest requests?
A3: Add `$request_time` and `$upstream_response_time` to the log format, then sort or query (jq, Loki `| json | req_time > 2`).

Q4: Difference between `json-file` and `local` driver?
A4: `local` stores in an optimised binary-ish format with default rotation and compression; `json-file` is plain JSON, rotation is off unless configured.

Q5: How to reload log files after rotation with file logs?
A5: Send `USR1`: `docker exec web nginx -s reopen`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any containerised Nginx (default stdout).
- You need central search (Loki / CloudWatch / ELK).
- JSON format for machine parsing.

❌ Avoid when:
- Logging full request bodies or auth headers.
- Debug level in production traffic.
- Keeping logs only inside the container filesystem.

---

## 📊 Visual Diagram
```
 Client ─► [ Nginx container ]
              │ access_log ─► /dev/stdout ┐
              │ error_log  ─► /dev/stderr ┤
                                          ▼
                              Docker logging driver (json-file / local / loki)
                                          │ rotate: 10m x 5
                    ┌─────────────────────┼─────────────────────┐
                    ▼                     ▼                     ▼
              docker logs -f        Promtail ─► Loki       CloudWatch
                                          └──► Grafana (search, alerts)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| access_log | Every request record | हर request का record |
| error_log | Nginx problems | Nginx की समस्याएँ |
| log_format | Line template | log line का template |
| Logging driver | Docker log collector | Docker का log collector |
| Rotation | Delete/compress old logs | पुरानी logs हटाना/compress |
| Request ID | Correlation key | जोड़ने वाली id |

---

## ⚡ 3-Line Summary
English: Let Nginx log to stdout/stderr and let Docker rotate with max-size/max-file.
Use JSON format with request id and timings; skip health probes and assets.
Never log secrets, and ship logs centrally.

Hindi: Nginx को stdout/stderr पर log करने दो और Docker को max-size/max-file से rotate करने दो।
Request id और timings वाला JSON format रखो; health probes और assets skip करो।
Secrets कभी log मत करो और logs को central जगह भेजो।

---

## ➡️ Next Topic
**416. Monitoring in CI/CD**: logs show what happened; next we add monitoring around the pipeline itself (build times, failures, deploy health).

---
