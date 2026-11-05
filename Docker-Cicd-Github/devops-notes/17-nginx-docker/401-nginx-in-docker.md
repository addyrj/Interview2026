# 401. Nginx in Docker
# हिंदी में: Docker में Nginx चलाना

---

## 🔵 Simple Definition (English)
Running **Nginx inside a Docker container** means using the official `nginx` image instead of installing Nginx on the VPS with `apt`. Your config (`nginx.conf`, `conf.d/*.conf`) and static files are mounted or baked into the image, so the web server is versioned, portable and reproducible like the rest of your stack.

## 🔵 सरल परिभाषा (Hindi)
**Docker container के अंदर Nginx चलाना** मतलब VPS पर `apt` से Nginx install करने की जगह official `nginx` image इस्तेमाल करना। आपकी config (`nginx.conf`, `conf.d/*.conf`) और static files image में bake या mount होती हैं, इसलिए web server भी बाकी stack की तरह versioned, portable और reproducible हो जाता है।

---

## 🔴 Problem it Solves
- Host-installed Nginx is a "snowflake": someone edits `/etc/nginx/sites-enabled` by hand, nobody remembers what changed, and a new VPS cannot be rebuilt identically.
- Different servers run different Nginx versions and modules, so "works on staging, breaks on prod".
- Upgrading Nginx via `apt` touches the whole host; rollback is painful.
- Config is not in Git, so there is no review, no history, no CI check.

## 🔴 यह क्यों बना? (Hindi)
- Host पर install किया Nginx "snowflake" बन जाता है: कोई `/etc/nginx/sites-enabled` हाथ से edit करता है, किसी को याद नहीं क्या बदला, और नया VPS वैसा ही दोबारा नहीं बनता।
- अलग servers पर अलग Nginx version/modules, तो "staging में चलता है, prod में टूटता है"।
- `apt` से upgrade पूरे host को छूता है; rollback मुश्किल।
- Config Git में नहीं, इसलिए review, history या CI check कुछ नहीं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Pull official image:  docker pull nginx:1.27-alpine
Step 2 → Put your config in ./nginx/conf.d/default.conf (in Git)
Step 3 → docker run -p 80:80 -v ./nginx/conf.d:/etc/nginx/conf.d:ro nginx
Step 4 → Nginx master process starts as PID 1, runs in foreground
         (daemon off;) so the container stays alive
Step 5 → Worker processes serve requests; logs go to stdout/stderr
         (docker logs shows them)
Step 6 → Change config -> nginx -t (test) -> nginx -s reload (no downtime)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Official image pull करो: docker pull nginx:1.27-alpine
Step 2 → अपनी config ./nginx/conf.d/default.conf में रखो (Git में)
Step 3 → docker run -p 80:80 -v ./nginx/conf.d:/etc/nginx/conf.d:ro nginx
Step 4 → Nginx master process PID 1 बनकर foreground में चलता है
         (daemon off;) ताकि container ज़िंदा रहे
Step 5 → Worker processes requests serve करते हैं; logs stdout/stderr में
         जाते हैं (docker logs से दिखते हैं)
Step 6 → Config बदलो -> nginx -t (test) -> nginx -s reload (बिना downtime)
```

---

## 🟡 Real World Example
Your Hostinger VPS currently has Nginx installed by `apt`, with files edited over SSH. After a disk crash you must rebuild it from memory. A team moves Nginx into Docker: the `nginx/` folder lives in the same Git repo as the app, a pull request reviews every config change, and rebuilding the whole server takes `git clone && docker compose up -d`. Swiggy-style teams do the same so that every environment (dev laptop, staging, prod) runs the identical Nginx 1.27 binary.

## 🟡 Real Example Hindi mein
आपके Hostinger VPS पर अभी Nginx `apt` से install है और files SSH पर हाथ से edit होती हैं। Disk crash हो जाए तो सब याद से दोबारा बनाना पड़ेगा। Team Nginx को Docker में ले जाती है: `nginx/` folder app वाले Git repo में ही रहता है, हर config बदलाव का pull request review होता है, और पूरा server दोबारा बनाना सिर्फ `git clone && docker compose up -d`। Swiggy जैसी teams यही करती हैं ताकि dev, staging, prod तीनों में बिल्कुल वही Nginx 1.27 binary चले।

---

## 💻 Code / Config Example — Basic

```bash
# Quick start: run the official image and serve a local folder.
# (examples: update the tag to the current stable release)

# 1) create a tiny site on the host
mkdir -p site                                   # folder for static files
echo '<h1>Hello from Nginx in Docker</h1>' > site/index.html   # test page

# 2) run nginx
docker run -d \
  --name web \
  -p 8080:80 \
  -v "$PWD/site:/usr/share/nginx/html:ro" \
  nginx:1.27-alpine
# -d              : detached (background)
# --name web      : easy name to use in later commands
# -p 8080:80      : host port 8080 -> container port 80
# -v ...:ro       : mount site folder READ-ONLY at nginx's web root
# nginx:1.27-alpine: small pinned image (example tag, update regularly)

# 3) test
curl -i http://localhost:8080/                  # should return 200 + our HTML

# 4) look at logs (they go to stdout, so docker captures them)
docker logs web

# 5) validate and reload config without stopping the container
docker exec web nginx -t                        # syntax check
docker exec web nginx -s reload                 # graceful reload

# 6) cleanup
docker rm -f web                                # stop and remove container
```

## 💻 Code / Config Example — Advanced

```yaml
# docker-compose.yml  (production-style Nginx service)
services:
  nginx:                                    # service name = DNS name on the network
    image: nginx:1.27-alpine                # pinned tag; example, bump after testing
    container_name: edge-nginx              # fixed name for ops commands
    restart: unless-stopped                 # auto-start after VPS reboot / crash
    ports:
      - "80:80"                             # HTTP on host
      - "443:443"                           # HTTPS on host (cert setup in 404)
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro        # main config, read-only
      - ./nginx/conf.d:/etc/nginx/conf.d:ro                # per-site configs, read-only
      - ./site:/usr/share/nginx/html:ro                    # static files, read-only
    read_only: true                         # root filesystem is immutable (hardening)
    tmpfs:                                  # nginx needs writable temp/pid locations
      - /var/cache/nginx                    # proxy/body temp files in RAM
      - /var/run                            # pid file in RAM
    cap_drop:
      - ALL                                 # drop all Linux capabilities...
    cap_add:
      - NET_BIND_SERVICE                    # ...keep only binding ports < 1024
      - CHOWN                               # cache dir ownership at startup
      - SETUID                              # master drops to nginx user
      - SETGID                              # same for group
    security_opt:
      - no-new-privileges:true              # block privilege escalation
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://127.0.0.1/healthz"]   # alpine has wget
      interval: 30s                         # run every 30 seconds
      timeout: 3s                           # fail if no answer in 3 seconds
      retries: 3                            # unhealthy after 3 failures
    logging:
      driver: json-file                     # default docker log driver
      options:
        max-size: "10m"                     # rotate at 10 MB
        max-file: "5"                       # keep 5 files -> disk never fills
```

```nginx
# nginx/conf.d/default.conf  (matches the compose file above)
server {
    listen 80;                                  # accept HTTP on container port 80
    server_name _;                              # catch-all host name
    server_tokens off;                          # hide nginx version in headers

    root /usr/share/nginx/html;                 # where static files live
    index index.html;                           # default file

    location = /healthz {                       # tiny endpoint for healthcheck
        access_log off;                         # do not spam logs with probes
        return 200 "ok\n";                      # always OK if nginx is alive
        add_header Content-Type text/plain;     # plain-text response
    }

    location / {
        try_files $uri $uri/ =404;              # serve file, else 404
    }
}
```

Note: configs and compose YAML above were syntax-checked as YAML; the `nginx` config was not run through `nginx -t` on this machine (nginx not installed), so test it with `docker run --rm -v "$PWD/nginx:/etc/nginx:ro" nginx:1.27-alpine nginx -t` before relying on it. With `read_only: true` and a custom `nginx.conf`, make sure the `pid` path is in a tmpfs directory.

---

## 🟠 My Stack Integration
Your Node.js API, FastAPI service and React build are already containers. Nginx joins the same Compose network and becomes the only service that publishes ports to the internet; everything else is reachable by service name only. On the Hostinger VPS, this replaces `apt install nginx` with one service in the existing `docker-compose.yml`. In GitHub Actions you can run `nginx -t` in CI against the same image before deploy.

```yaml
# Slice of the stack: only nginx exposes ports
services:
  nginx:
    image: nginx:1.27-alpine               # edge proxy
    ports: ["80:80", "443:443"]            # the ONLY published ports
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d:ro  # config from Git
    depends_on:
      - api                                # start after Node API
      - ml                                 # start after FastAPI
  api:
    build: ./api                           # Node.js, listens on 3000 (no ports: here)
  ml:
    build: ./fastapi                       # FastAPI, listens on 8000 (no ports: here)
```

Security: publish only 80/443, run read-only, drop capabilities, hide version with `server_tokens off`, never mount `/var/run/docker.sock` into Nginx.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `nginx:latest` in production, so a surprise upgrade changes behaviour.
✅ Correct: Pin a tag (`nginx:1.27-alpine`) and bump it deliberately via a PR.

❌ Mistake 2: Setting `daemon on;` (or running `service nginx start`) inside the container, so PID 1 exits and the container stops.
✅ Correct: Keep Nginx in the foreground (`daemon off;`, already the default in the official image CMD).

❌ Mistake 3: Editing config inside the running container with `docker exec` and `vi`.
✅ Correct: Edit the file in Git, mount it, then `nginx -t && nginx -s reload`.

❌ Mistake 4: Writing logs to files inside the container so the disk or layer grows forever.
✅ Correct: Log to stdout/stderr and set Docker log rotation (`max-size`, `max-file`).

---

## 🧠 Tricky Interview Question
You mounted a new `default.conf` with a typo and ran `docker restart nginx`. The site is now down. What should you have done differently?

Answer: `restart` stops the container and starts it again; the master process fails to parse the broken config and exits, so every request fails. `docker exec nginx nginx -t` would have caught the error, and `nginx -s reload` is safer: if the new config is invalid, the old workers keep serving traffic and the reload is rejected. Best of all, run `nginx -t` in CI against the exact image tag so a typo never reaches the server.

---

## ⚫ Interview Questions + Answers

Q1: Why does the official Nginx image log to stdout?
A1: It symlinks `/var/log/nginx/access.log` to `/dev/stdout` and `error.log` to `/dev/stderr`. Docker then collects them, so `docker logs`, log drivers and tools like Loki or CloudWatch work without file handling.

Q2: Bake config into the image or mount it?
A2: Mount for flexibility (change config without rebuild), bake (`COPY`) for immutability and for registries/Kubernetes where the image alone must be deployable. Many teams bake in CI and mount only secrets.

Q3: How do you validate config without a running server?
A3: `docker run --rm -v ./nginx:/etc/nginx:ro nginx:1.27-alpine nginx -t`. It parses and exits with a non-zero code on error, perfect for CI.

Q4: Why alpine vs debian variant?
A4: Alpine is much smaller (fewer CVEs, faster pulls) but uses musl libc; the Debian image is larger but more compatible with extra modules. For plain proxy/static serving alpine is fine.

Q5: Can a non-root user run Nginx in Docker?
A5: Yes. Use `nginxinc/nginx-unprivileged`, which listens on 8080 and writes only to writable temp paths. You then map `80:8080` on the host. It is a good hardening option.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You already run the app with Docker/Compose and want one deployment model.
- You want Nginx config reviewed in Git and reproducible across servers.
- You need quick rollbacks (change the image tag).

❌ Avoid when:
- One shared host Nginx already fronts many non-Docker sites and you cannot move them.
- You depend on exotic third-party modules not in the official image (build a custom image instead).

---

## 📊 Visual Diagram
```
 Internet
    |
    v  :80 / :443
+-----------------------------------------------+
| Hostinger VPS (Docker host)                   |
|                                               |
|   +----------------------------------+        |
|   | nginx container (PID 1 = master) |        |
|   |  master -> worker, worker ...    |        |
|   |  /etc/nginx/conf.d  <-- ro mount |        |
|   |  /usr/share/nginx/html <-- ro    |        |
|   |  logs -> stdout/stderr           |        |
|   +----------------------------------+        |
|        |  (docker network, by name)           |
|        v                                      |
|   api:3000 (Node)      ml:8000 (FastAPI)      |
+-----------------------------------------------+
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Official image | Maintained `nginx` image on Docker Hub | आधिकारिक image |
| `daemon off;` | Run in foreground so container lives | foreground में चलाना |
| Bind mount | Host path mapped into container | host path का mapping |
| `nginx -t` | Test config syntax | config जाँच |
| `nginx -s reload` | Graceful config reload | बिना रुके reload |
| Alpine | Tiny Linux base image | छोटा Linux base |
| Healthcheck | Command that reports container health | सेहत की जाँच |

---

## ⚡ 3-Line Summary
English: Nginx in Docker packages the web server and its config as a pinned, reproducible container.
Config lives in Git, is mounted read-only, validated with `nginx -t` and reloaded gracefully.
It becomes the single public entry point of your Compose stack.
Hindi: Docker में Nginx web server और उसकी config को pinned, reproducible container बना देता है।
Config Git में रहती है, read-only mount होती है, `nginx -t` से जाँची जाती है और gracefully reload होती है।
यह आपके Compose stack का अकेला public entry point बनता है।

---

## ➡️ Next Topic
402. Nginx as Reverse Proxy in Docker - now that Nginx runs in a container, we make it forward traffic to the Node.js and FastAPI containers.
