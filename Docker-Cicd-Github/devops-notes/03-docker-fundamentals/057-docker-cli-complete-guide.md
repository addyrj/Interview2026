---

# 057. Docker CLI — Complete Guide
# हिंदी में: Docker CLI — पूरी गाइड

---

## 🔵 Simple Definition (English)
The **Docker CLI** is the `docker` command-line client that sends requests to the Docker daemon. Commands follow the shape `docker <object> <action>` (e.g. `docker container ls`, `docker image rm`), with short legacy aliases like `docker ps` and `docker rmi`.

## 🔵 सरल परिभाषा (Hindi)
**Docker CLI** `docker` command-line client है जो Docker daemon को requests भेजता है। Commands का pattern `docker <object> <action>` है (जैसे `docker container ls`, `docker image rm`), और छोटे पुराने aliases जैसे `docker ps` और `docker rmi` भी चलते हैं।

---

## 🔴 Problem it Solves
Without a CLI you would have to call the daemon's REST API by hand. The CLI gives a consistent, scriptable interface for images, containers, volumes, networks and builds, which is exactly what CI/CD pipelines and SSH deployments rely on.

## 🔴 यह क्यों बना? (Hindi)
CLI के बिना आपको daemon की REST API हाथ से call करनी पड़ती। CLI images, containers, volumes, networks और builds के लिए एक जैसा, scriptable interface देता है, जिस पर CI/CD pipelines और SSH deployments निर्भर करते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You type: docker run -d -p 80:80 nginx
Step 2 → CLI reads DOCKER_HOST / current context to find the daemon (default unix:///var/run/docker.sock)
Step 3 → CLI sends REST API calls (POST /containers/create, /containers/{id}/start)
Step 4 → dockerd pulls the image if missing, asks containerd/runc to start the process
Step 5 → Daemon returns IDs/status; CLI prints the container ID or streams logs
Step 6 → Exit code of the CLI reflects success (0) or failure, which scripts and CI check
```

Command families:
- **Run/manage**: `run`, `ps`, `stop`, `start`, `restart`, `rm`, `exec`, `logs`, `inspect`, `stats`
- **Images**: `pull`, `push`, `build`, `images`, `rmi`, `tag`, `history`
- **Data/network**: `volume ...`, `network ...`
- **System**: `info`, `version`, `system df`, `system prune`, `login`, `context`
- **Compose**: `docker compose up/down/ps/logs`

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → आप लिखते हैं: docker run -d -p 80:80 nginx
Step 2 → CLI DOCKER_HOST / current context से daemon खोजता है (default unix:///var/run/docker.sock)
Step 3 → CLI REST API calls भेजता है (POST /containers/create, /containers/{id}/start)
Step 4 → dockerd image missing हो तो pull करता है, containerd/runc से process शुरू कराता है
Step 5 → Daemon IDs/status लौटाता है; CLI container ID print करता है या logs stream करता है
Step 6 → CLI का exit code success (0) या failure दिखाता है, जिसे scripts और CI check करते हैं
```

Command families:
- **Run/manage**: `run`, `ps`, `stop`, `start`, `restart`, `rm`, `exec`, `logs`, `inspect`, `stats`
- **Images**: `pull`, `push`, `build`, `images`, `rmi`, `tag`, `history`
- **Data/network**: `volume ...`, `network ...`
- **System**: `info`, `version`, `system df`, `system prune`, `login`, `context`
- **Compose**: `docker compose up/down/ps/logs`

---

## 🟡 Real World Example
At 2 AM your FastAPI API returns 502. You SSH into the VPS and run `docker ps` (is it up?), `docker logs --tail 100 api` (what error?), `docker exec -it api sh` (inspect files), `docker stats --no-stream` (is it out of memory?), and finally `docker compose up -d --force-recreate api`. Those five commands solve most real incidents.

## 🟡 Real Example Hindi mein
रात 2 बजे आपका FastAPI API 502 दे रहा है। आप VPS पर SSH करके `docker ps` (चल रहा है?), `docker logs --tail 100 api` (क्या error?), `docker exec -it api sh` (files देखें), `docker stats --no-stream` (memory खत्म तो नहीं?), और अंत में `docker compose up -d --force-recreate api` चलाते हैं। ये पाँच commands ज़्यादातर real incidents सुलझा देते हैं।

---

## 💻 Code / Config Example — Basic

```bash
# --- Everyday Docker CLI cheat sheet ---
docker --help                                    # list all top-level commands
docker run --help                                # help for one command (every command has it)
docker pull nginx:1.27-alpine                    # download image (example tag)
docker images                                    # list local images
docker run -d --name web -p 8080:80 nginx:1.27-alpine  # start nginx detached on host port 8080
docker ps                                        # running containers
docker logs web                                  # print container output
docker exec -it web sh                           # open a shell inside it (exit to leave)
docker stop web                                  # graceful stop
docker rm web                                    # delete the stopped container
docker rmi nginx:1.27-alpine                     # delete the image
docker system df                                 # see disk usage
```

## 💻 Code / Config Example — Advanced

```bash
#!/usr/bin/env bash
# ops-helpers.sh - source this on the VPS: `source ops-helpers.sh`
# Handy CLI wrappers using real docker flags (Docker Engine 20.10+).
set -euo pipefail                                # strict mode for the script when executed directly

# Pretty running list: name, image, status, ports
dps() {
  docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'   # Go template formatting
}

# Follow logs of one container with timestamps, last 100 lines
dlog() {
  docker logs -f --tail 100 -t "$1"              # $1 is the container name
}

# Shell into a container, falling back from bash to sh
dsh() {
  docker exec -it "$1" bash 2>/dev/null || docker exec -it "$1" sh   # alpine images have no bash
}

# Remove dangling images and stopped containers older than 24h (safe cleanup, keeps volumes)
dclean() {
  docker container prune -f --filter "until=24h"   # stopped containers older than 24h
  docker image prune -f                            # dangling images only
}

# Health summary: container name and health status
dhealth() {
  docker ps -q | xargs -r docker inspect --format '{{.Name}} {{if .State.Health}}{{.State.Health.Status}}{{else}}no-healthcheck{{end}}'
}

# Deploy: pull and recreate only changed services
ddeploy() {
  docker compose pull                              # fetch newer images
  docker compose up -d --remove-orphans            # recreate changed services, remove old ones
}
```

---

## 🟠 My Stack Integration
- **Node.js / FastAPI**: `docker logs -f api` for stack traces; `docker exec api env` to confirm env vars.
- **React**: build is done in a Docker build stage; use `docker build -t web:test ./web` to test locally.
- **Nginx**: `docker exec nginx nginx -t` validates config; `docker exec nginx nginx -s reload` reloads it without downtime.
- **VPS**: use `docker context` to run commands against the server from your laptop.
- **AWS**: `aws ecr get-login-password | docker login --username AWS --password-stdin <account>.dkr.ecr.<region>.amazonaws.com` to authenticate to ECR.

```yaml
# .github/workflows/ci.yml - the same CLI used inside a pipeline
name: ci                                         # workflow name
on:
  pull_request:                                  # run on every PR
jobs:
  docker-smoke:
    runs-on: ubuntu-latest                       # runner with Docker preinstalled
    steps:
      - uses: actions/checkout@v4                # fetch code (example version)
      - name: Build image                        # plain CLI usage
        run: docker build -t api:ci ./api        # tag image as api:ci
      - name: Run and smoke test                 # start container and curl health endpoint
        run: |
          docker run -d --name api -p 8000:8000 api:ci
          sleep 5
          curl -fsS http://localhost:8000/health
      - name: Show logs on failure               # useful debugging output
        if: failure()
        run: docker logs api
```

Security: `docker login` stores credentials in `~/.docker/config.json`; use credential helpers, and in CI use `--password-stdin` with secrets. Do not put secrets in `docker run -e SECRET=...` on shared servers (visible in `docker inspect` and shell history); avoid `--privileged`; the CLI over TCP must use TLS.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `latest` tags everywhere.
✅ Correct: Pin specific version tags or digests so deployments are reproducible.

❌ Mistake 2: Running `docker system prune -a --volumes` on production.
✅ Correct: Prune selectively (`docker image prune`, `docker container prune`) and never prune volumes blindly.

❌ Mistake 3: Using `-it` in scripts/CI (no TTY, errors like "the input device is not a TTY").
✅ Correct: Omit `-t` (and `-i`) in non-interactive scripts, or use `docker exec -i`.

❌ Mistake 4: Putting options after the image name (`docker run nginx -p 80:80`).
✅ Correct: Options go before the image; anything after the image is passed to the container's command.

---

## 🧠 Tricky Interview Question
`docker run -d myapp` prints a container ID, yet `docker ps` shows nothing a second later. What do you check and why?

Answer: The container started and exited immediately. Run `docker ps -a` to see the exit code, then `docker logs <id>`. Typical reasons: the main process crashed (missing env var), the command finished (no long-running foreground process), or the app daemonised itself into the background so PID 1 exited. A container lives only as long as its main process (PID 1).

---

## ⚫ Interview Questions + Answers

Q1: `docker container ls` vs `docker ps`?
A1: Same thing. `docker ps` is the legacy shortcut; the grouped form `docker <object> <verb>` is the modern, consistent syntax.

Q2: How does the CLI know which daemon to use?
A2: From `DOCKER_HOST`, `--host`, or the active context (`docker context use`). Default is the local unix socket.

Q3: How do you format output for scripts?
A3: `--format` with Go templates (e.g. `docker ps --format '{{.Names}}'`) and `-q` for IDs only.

Q4: Difference between `docker compose` and `docker-compose`?
A4: `docker compose` is the v2 plugin written in Go and bundled with Docker; `docker-compose` is the old standalone Python v1, end-of-life.

Q5: How do you see what a command would do without running it?
A5: There is no global dry-run. Use `docker compose config` to validate/render compose files and `docker run --help`; test destructive commands (like prune) with filters or on staging first.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Debugging, one-off tasks, scripts and CI steps.
- Learning how Docker works under the hood.

❌ Avoid when:
- Managing many services manually in production: prefer Compose or an orchestrator.
- Hand-typing long `docker run` commands; keep them in compose files in git.

---

## 📊 Visual Diagram
```
  you: docker run ...                 
        |
   +----v-----+  REST over unix socket  +-----------+   +------------+
   | docker   |------------------------>|  dockerd  |-->| containerd |
   |  CLI     |<------------------------|           |   +-----+------+
   +----------+      JSON / stream      +-----+-----+         |
                                              |            runc
                          images, volumes,    |              |
                          networks            v              v
                                        [ registry ]   [ container ]
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| CLI | Command-line client | Command-line client |
| Daemon | Background service doing the work | Background में काम करने वाली service |
| Context | Target daemon config | Target daemon की config |
| Go template | `--format` syntax | `--format` का syntax |
| TTY | Interactive terminal | Interactive terminal |
| Prune | Remove unused objects | बेकार objects हटाना |

---

## ⚡ 3-Line Summary
English: The docker CLI talks to the daemon with commands shaped as object plus action.
Master run, ps, logs, exec, stop, rm, inspect and stats first.
Use formats and filters for scripts, and never prune blindly.
Hindi: docker CLI daemon से object plus action वाले commands से बात करता है।
पहले run, ps, logs, exec, stop, rm, inspect और stats सीखें।
Scripts के लिए format और filter इस्तेमाल करें, और बिना सोचे prune न करें।

---

## ➡️ Next Topic
**058. docker run — Complete Guide.** The most important and most option-heavy command, in detail.

---
