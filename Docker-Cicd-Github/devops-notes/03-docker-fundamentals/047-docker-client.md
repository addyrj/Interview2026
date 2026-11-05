# 47. Docker Client
# हिंदी में: Docker Client (क्लाइंट)

---

## 🔵 Simple Definition (English)
The **Docker client** is the program you actually type into: the `docker` CLI (plus tools like `docker compose`, Docker Desktop UI, or SDKs). It does no heavy work itself; it converts commands into REST API calls and sends them to a Docker daemon, local or remote.

## 🔵 सरल परिभाषा (Hindi)
**Docker client** वह program है जिसमें आप असल में command लिखते हैं: `docker` CLI (और `docker compose`, Docker Desktop UI, SDKs जैसे tools)। यह खुद भारी काम नहीं करता; commands को REST API calls में बदलकर local या remote Docker daemon को भेजता है।

---

## 🔴 Problem it Solves
Humans need a friendly interface to a daemon API, and automation needs a scriptable one. The client gives short commands (`docker run`), handles auth to registries (`docker login`), streams logs, and lets one laptop or CI job control many servers via **contexts** without SSH-ing in each time.

## 🔴 यह क्यों बना? (Hindi)
इंसानों को daemon API के लिए आसान interface चाहिए, और automation को scriptable interface। Client छोटे commands (`docker run`) देता है, registry auth (`docker login`) संभालता है, logs stream करता है, और **contexts** से एक laptop या CI job हर बार SSH किए बिना कई servers चला सकता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You run: docker ps -a
Step 2 → Client loads config: ~/.docker/config.json (auths, credential helpers, current context)
Step 3 → Chooses the daemon endpoint: DOCKER_HOST env > --host flag > current context > default unix socket
Step 4 → Builds HTTP request: GET /v1.xx/containers/json?all=1 (API version negotiated)
Step 5 → Sends it (unix socket, ssh://, or tcp+TLS)
Step 6 → Receives JSON/stream, formats a table, prints it
Step 7 → For build/push, the client also sends the build context (tar of files) or auth headers
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → आप चलाते हैं: docker ps -a
Step 2 → Client config लोड करता है: ~/.docker/config.json (auths, credential helpers, current context)
Step 3 → Daemon endpoint चुनता है: DOCKER_HOST env > --host flag > current context > default unix socket
Step 4 → HTTP request बनाता है: GET /v1.xx/containers/json?all=1 (API version तय होती है)
Step 5 → उसे भेजता है (unix socket, ssh://, या tcp+TLS)
Step 6 → JSON/stream पाता है, table बनाकर दिखाता है
Step 7 → build/push में client build context (files का tar) या auth headers भी भेजता है
```

---

## 🟡 Real World Example
A developer on a Mac uses Docker Desktop (client talking to a hidden VM daemon) to run the Node.js stack. The same developer runs `docker --context prod ps` to look at the production VPS safely over SSH. In GitHub Actions the client logs in to GHCR using `GITHUB_TOKEN`, builds, and pushes. The commands are identical; only the endpoint changes.

## 🟡 Real Example Hindi mein
Mac पर developer Docker Desktop (hidden VM के daemon से बात करता client) से Node.js stack चलाता है। वही developer `docker --context prod ps` से SSH के ज़रिये production VPS देखता है। GitHub Actions में client `GITHUB_TOKEN` से GHCR में login करके build और push करता है। Commands वही हैं; सिर्फ़ endpoint बदलता है।

---

## 💻 Code / Config Example — Basic
```bash
# Everyday client commands (needs a daemon to talk to)
docker --version                               # client version only (does not need the daemon)
docker version                                 # client + server versions (needs the daemon)
docker help run                                # built-in help for one command
docker run --rm -it alpine sh                  # run a throwaway interactive container, auto-delete on exit
docker images                                  # list local images
docker ps -a                                   # list all containers, including stopped
docker logs --tail 100 -f myapp                # last 100 lines, then follow
docker exec -it myapp sh                       # shell in a running container
docker inspect myapp                           # full JSON details of an object
docker inspect -f '{{.NetworkSettings.IPAddress}}' myapp   # Go-template filter to pick one field
docker login ghcr.io -u myuser                 # authenticate to a registry (prompts for password/token)
docker context ls                              # show saved daemon endpoints
```

## 💻 Code / Config Example — Advanced
```bash
#!/usr/bin/env bash
# client-multi-env.sh - one client, many daemons, safe defaults
set -euo pipefail                                          # strict mode

# --- Contexts: named endpoints stored in ~/.docker/contexts ---
docker context create staging --docker "host=ssh://deploy@staging.example.com"   # example hostnames
docker context create prod    --docker "host=ssh://deploy@prod.example.com"      # SSH uses your ssh key/agent

# --- Use a context for one command, or export it for the shell ---
docker --context prod ps --format 'table {{.Names}}\t{{.Status}}\t{{.Image}}'    # custom table output
export DOCKER_CONTEXT=staging                              # all following docker commands hit staging
docker compose ps                                          # compose obeys the context too

# --- Safer registry credentials: use a credential helper, not plaintext in config.json ---
# ~/.docker/config.json example (do not store tokens in it directly):
#   { "credsStore": "osxkeychain" }      # macOS keychain; use "pass" or "secretservice" on Linux
# In CI, prefer:  echo "$TOKEN" | docker login ghcr.io -u "$USER" --password-stdin

# --- Pin the API version when the client is newer than an old daemon ---
DOCKER_API_VERSION=1.41 docker ps                          # example version; check `docker version` for the server's value

# --- Machine-readable output for scripts ---
docker ps -q --filter "status=exited"                      # only IDs of exited containers
docker ps --format '{{json .}}'                            # one JSON object per line (jq-friendly)
```

---

## 🟠 My Stack Integration
```yaml
# .github/workflows/ci.yml - CLI client usage in CI for the Node.js API image
name: ci                                           # workflow name
on: { push: { branches: [main] } }                 # run on pushes to main
permissions: { contents: read, packages: write }   # read code, push to GHCR only
jobs:
  build:
    runs-on: ubuntu-latest                         # runner has Docker client + daemon preinstalled
    steps:
      - uses: actions/checkout@v4                  # fetch code
      - name: Login to GHCR                        # client authenticates to the registry
        run: echo "${{ secrets.GITHUB_TOKEN }}" | docker login ghcr.io -u "${{ github.actor }}" --password-stdin   # token via stdin, not argv
      - name: Build and push                       # build with local daemon, push to registry
        run: |
          IMAGE=ghcr.io/${{ github.repository }}/api:${{ github.sha }}   # immutable tag = commit SHA
          docker build -t "$IMAGE" ./api           # build from ./api/Dockerfile
          docker push "$IMAGE"                     # upload layers
```
VPS: `docker --context prod compose pull && docker --context prod compose up -d`. AWS: `aws ecr get-login-password | docker login --username AWS --password-stdin <acct>.dkr.ecr.<region>.amazonaws.com`.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `docker login -p TOKEN` on the command line.
✅ Correct: `--password-stdin`; `-p` leaks the secret into shell history and process lists.

❌ Mistake 2: Running destructive commands against the wrong context (prod instead of staging).
✅ Correct: Show the context in your shell prompt; check `docker context show` before `prune`/`rm`.

❌ Mistake 3: Forgetting `.dockerignore`, so `docker build .` sends gigabytes (node_modules, .git, .env) to the daemon.
✅ Correct: Create `.dockerignore`; faster builds and no secrets in the context.

❌ Mistake 4: Confusing client and server versions on API errors.
✅ Correct: `docker version` shows both; upgrade the old side or pin `DOCKER_API_VERSION`.

---

## 🧠 Tricky Interview Question
"You uninstall Docker Engine on your laptop but keep the `docker` binary. `docker ps` fails, yet `docker --version` works. Why? And how can `docker ps` still work without a local engine?"

Answer: `--version` is answered by the client itself; `ps` needs a daemon. The error is "Cannot connect to the Docker daemon at unix:///var/run/docker.sock". It can work if `DOCKER_HOST` or a `docker context` points to a remote daemon (ssh:// or tcp://), because the client is only an API caller.

---

## ⚫ Interview Questions + Answers

Q1: What is the Docker client?
A1: The CLI (and SDKs/UI) that sends API requests to the daemon; it holds no containers itself.

Q2: How does it know which daemon to use?
A2: Order: `--host`/`-H`, `DOCKER_HOST`, active `docker context` (or `DOCKER_CONTEXT`), then the default unix socket.

Q3: Where are registry credentials stored?
A3: `~/.docker/config.json`, either base64 (plain, weak) or via a credential helper (keychain). Prefer helpers; in CI use short-lived tokens.

Q4: What does `docker build .` send to the daemon?
A4: The build context (the directory as a tar, minus `.dockerignore` entries) and the Dockerfile.

Q5: Name Docker client alternatives.
A5: Docker SDKs (Python `docker`, Node `dockerode`), Portainer, `curl` to the API, Podman CLI (compatible commands).

---

## 🔷 When to Use + When Not to Use
✅ Use contexts when:
- Managing staging/prod VPS from one machine or CI job

❌ Avoid when:
- Everyone shares one over-privileged SSH key; prefer per-user keys and least privilege

---

## 📊 Visual Diagram
```
  laptop / CI runner                              servers
 +--------------------+     context: default  -> unix:///var/run/docker.sock (local daemon)
 | docker CLI         |---- context: staging  -> ssh://deploy@staging  --> dockerd (staging VPS)
 |  ~/.docker/        |---- context: prod     -> ssh://deploy@prod     --> dockerd (prod VPS)
 |   config.json      |
 |   contexts/        |---- docker login/push --> Registry (GHCR / ECR / Docker Hub)
 +--------------------+
   command -> HTTP request -> daemon -> result streamed back
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| CLI | Command-line interface | command-line इंटरफ़ेस |
| Context | Named daemon endpoint | नाम वाला daemon endpoint |
| DOCKER_HOST | Env var selecting daemon | daemon चुनने वाला env variable |
| Build context | Files sent for build | build के लिए भेजी फ़ाइलें |
| Credential helper | Secure secret store | secrets का सुरक्षित भंडार |
| config.json | Client settings file | client की settings file |
| SDK | Library to call API | API बुलाने की library |

---

## ⚡ 3-Line Summary
English: The Docker client is the CLI that turns commands into API calls for a daemon.
English: Contexts and DOCKER_HOST let one client manage local, staging, and prod daemons.
English: Protect registry credentials, use .dockerignore, and double-check the active context.
Hindi: Docker client वह CLI है जो commands को daemon के API calls में बदलता है।
Hindi: Contexts और DOCKER_HOST से एक client local, staging और prod daemons चला सकता है।
Hindi: Registry credentials सुरक्षित रखो, .dockerignore इस्तेमाल करो, और active context दोबारा जाँचो।

---

## ➡️ Next Topic
**48. Docker Registry** - where the client pushes and the daemon pulls images from.
