---

# 064. docker inspect
# हिंदी में: docker inspect

---

## 🔵 Simple Definition (English)
`docker inspect` returns detailed low-level information as JSON for Docker objects: containers, images, volumes, networks and more. It shows config, state, IP address, mounts, environment variables, health status, restart count and exit code. `--format` (`-f`) extracts exactly the field you need.

## 🔵 सरल परिभाषा (Hindi)
`docker inspect` Docker objects (containers, images, volumes, networks आदि) की विस्तृत low-level जानकारी JSON में देता है। इसमें config, state, IP address, mounts, environment variables, health status, restart count और exit code होते हैं। `--format` (`-f`) से आप सिर्फ वही field निकाल सकते हैं जो चाहिए।

---

## 🔴 Problem it Solves
`docker ps` shows a summary only. To answer "why was it killed?", "what IP does it have?", "which volume is mounted where?", "which env vars did Compose really pass?" or "what is the image digest?" you need the full truth. `inspect` is the source of that truth, usable both by humans and scripts.

## 🔴 यह क्यों बना? (Hindi)
`docker ps` सिर्फ summary दिखाता है। "यह क्यों kill हुआ?", "इसका IP क्या है?", "कौन सा volume कहाँ mount है?", "Compose ने असल में कौन से env vars दिए?" या "image का digest क्या है?" जैसे सवालों के लिए पूरी सच्चाई चाहिए। `inspect` उस सच्चाई का स्रोत है, जिसे इंसान और scripts दोनों इस्तेमाल कर सकते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You run: docker inspect api   (name, ID or ID prefix; works for several objects at once)
Step 2 → CLI asks the daemon for the object's JSON from its metadata store
Step 3 → Docker looks in containers first, then images, networks, volumes (use --type to be explicit)
Step 4 → Output is a JSON array; each object has sections: State, Config, HostConfig, NetworkSettings, Mounts
Step 5 → -f '{{...}}' applies a Go template, so you print only one field (or use '{{json .X}}' and pipe to jq)
Step 6 → Scripts use the result for health checks, IP lookup, exit-code decisions, audits
```

Key fields:
- `.State.Status`, `.State.ExitCode`, `.State.OOMKilled`, `.State.Health.Status`, `.State.StartedAt`
- `.RestartCount`, `.HostConfig.RestartPolicy`, `.HostConfig.Memory`
- `.Config.Env`, `.Config.Image`, `.Config.Cmd`, `.Config.Labels`
- `.NetworkSettings.Networks.<net>.IPAddress`, `.NetworkSettings.Ports`
- `.Mounts` (type, source, destination, mode)

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → आप चलाते हैं: docker inspect api   (name, ID या ID prefix; एक साथ कई objects भी)
Step 2 → CLI daemon से object का JSON उसके metadata store से माँगता है
Step 3 → Docker पहले containers, फिर images, networks, volumes में खोजता है (साफ़ बताने के लिए --type)
Step 4 → Output JSON array है; हर object में sections: State, Config, HostConfig, NetworkSettings, Mounts
Step 5 → -f '{{...}}' Go template लगाता है, ताकि सिर्फ एक field print हो (या '{{json .X}}' को jq में pipe करें)
Step 6 → Scripts नतीजा health checks, IP lookup, exit-code फैसलों, audits के लिए इस्तेमाल करते हैं
```

मुख्य fields:
- `.State.Status`, `.State.ExitCode`, `.State.OOMKilled`, `.State.Health.Status`, `.State.StartedAt`
- `.RestartCount`, `.HostConfig.RestartPolicy`, `.HostConfig.Memory`
- `.Config.Env`, `.Config.Image`, `.Config.Cmd`, `.Config.Labels`
- `.NetworkSettings.Networks.<net>.IPAddress`, `.NetworkSettings.Ports`
- `.Mounts` (type, source, destination, mode)

---

## 🟡 Real World Example
Your API container keeps restarting. `docker inspect -f '{{.RestartCount}} {{.State.ExitCode}} {{.State.OOMKilled}}' api` prints `14 137 true`: restarted 14 times, OOM-killed. You also check `.HostConfig.Memory` (536870912 = 512 MB) and decide to raise the limit to 1 GB. In another case, a Postgres volume seems empty: `docker inspect -f '{{json .Mounts}}' db` shows it mounted from a different volume name because someone renamed the Compose project, so a new empty volume was created.

## 🟡 Real Example Hindi mein
आपका API container बार-बार restart हो रहा है। `docker inspect -f '{{.RestartCount}} {{.State.ExitCode}} {{.State.OOMKilled}}' api` print करता है `14 137 true`: 14 बार restart, OOM-kill। आप `.HostConfig.Memory` (536870912 = 512 MB) भी देखते हैं और limit 1 GB करने का फैसला करते हैं। दूसरे मामले में Postgres volume खाली लगता है: `docker inspect -f '{{json .Mounts}}' db` दिखाता है कि वह दूसरे नाम के volume से mount है, क्योंकि किसी ने Compose project का नाम बदला और नया खाली volume बन गया।

---

## 💻 Code / Config Example — Basic

```bash
# --- docker inspect basics ---
docker inspect api                               # full JSON for container "api"
docker inspect --type image nginx:1.27-alpine    # force image lookup (example tag)
docker inspect -f '{{.State.Status}}' api        # running / exited / restarting
docker inspect -f '{{.State.ExitCode}}' api      # exit code of last run
docker inspect -f '{{.State.OOMKilled}}' api     # true if killed for memory
docker inspect -f '{{.RestartCount}}' api        # how many times Docker restarted it
docker inspect -f '{{.NetworkSettings.Networks.backend.IPAddress}}' api   # IP on network "backend"
docker inspect -f '{{range .Config.Env}}{{println .}}{{end}}' api   # env vars one per line
docker inspect -f '{{json .Mounts}}' api         # mounts as one JSON line
docker inspect -f '{{.State.Health.Status}}' api # healthy / unhealthy / starting (needs HEALTHCHECK)
docker volume inspect pgdata                     # volume details (Mountpoint)
docker network inspect backend                   # network subnet and attached containers
```

## 💻 Code / Config Example — Advanced

```bash
#!/usr/bin/env bash
# inspect-audit.sh - audit running containers with docker inspect (real fields, Docker 20.10+)
# Optional: jq for JSON processing (apt-get install -y jq)
set -euo pipefail                                # strict shell mode

for c in $(docker ps -q); do                      # every running container ID
  name=$(docker inspect -f '{{.Name}}' "$c" | sed 's#^/##')   # container name without leading slash
  image=$(docker inspect -f '{{.Config.Image}}' "$c")         # image reference
  user=$(docker inspect -f '{{if .Config.User}}{{.Config.User}}{{else}}root{{end}}' "$c")   # user (root if empty)
  priv=$(docker inspect -f '{{.HostConfig.Privileged}}' "$c") # privileged mode?
  mem=$(docker inspect -f '{{.HostConfig.Memory}}' "$c")      # memory limit in bytes (0 = unlimited)
  restart=$(docker inspect -f '{{.HostConfig.RestartPolicy.Name}}' "$c")   # restart policy
  health=$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' "$c")  # health
  printf '%-20s image=%-28s user=%-8s privileged=%s mem=%s restart=%s health=%s\n' \
    "$name" "$image" "$user" "$priv" "$mem" "$restart" "$health"   # one audit line per container
  [ "$mem" = "0" ] && echo "  WARN: $name has no memory limit"   # flag missing limits
  [ "$priv" = "true" ] && echo "  WARN: $name is privileged"      # flag privileged containers
  docker inspect -f '{{range .Mounts}}{{if eq .Source "/var/run/docker.sock"}}WARN: docker.sock mounted{{println}}{{end}}{{end}}' "$c"
done

# Find containers that mount a particular volume (jq version)
docker inspect $(docker ps -aq) | jq -r '.[] | select(.Mounts[]?.Name=="pgdata") | .Name'   # who uses pgdata

# Get the image digest of the running image (for exact rollback records)
docker inspect -f '{{index .RepoDigests 0}}' ghcr.io/example/api:1.4.2   # works if image was pulled from a registry
```

```yaml
# docker-compose.yml - labels you can read back with inspect to track deployments
services:
  api:
    image: ghcr.io/example/api:${APP_VERSION:-1.4.2}   # version from env, default example
    restart: unless-stopped                      # visible in HostConfig.RestartPolicy
    labels:
      app.version: "${APP_VERSION:-1.4.2}"       # custom label (read: docker inspect -f '{{index .Config.Labels "app.version"}}' api)
      app.git_sha: "${GIT_SHA:-unknown}"         # commit that was deployed
    mem_limit: 512m                              # visible in HostConfig.Memory
    healthcheck:
      test: ["CMD-SHELL", "curl -fsS http://localhost:8000/health || exit 1"]   # image must contain curl
      interval: 30s                              # probe every 30s
      timeout: 5s                                # probe timeout
      retries: 3                                 # failures before unhealthy
```

---

## 🟠 My Stack Integration
- **FastAPI/Node.js**: verify env vars really passed by Compose: `docker inspect -f '{{json .Config.Env}}' api`.
- **Nginx**: find its IP or mounts: `docker inspect nginx -f '{{json .Mounts}}'` to confirm the config file is mounted from the right path.
- **VPS deploy script**: after `docker compose up -d`, loop until `.State.Health.Status` is `healthy`, else fail the pipeline.
- **Rollback**: record `app.git_sha` labels and image digests per release.
- **AWS**: ECS `describe-tasks` gives similar state; on EC2 use `inspect`.

```yaml
# .github/workflows/deploy.yml - wait for health using inspect after deploy
name: deploy                                     # workflow name
on:
  push:
    branches: [main]                             # deploy on main
jobs:
  deploy:
    runs-on: ubuntu-latest                       # runner
    steps:
      - name: Deploy and wait healthy            # SSH script
        uses: appleboy/ssh-action@v1.0.3         # example version
        with:
          host: ${{ secrets.VPS_HOST }}          # VPS address
          username: deploy                       # docker user
          key: ${{ secrets.VPS_SSH_KEY }}        # SSH key secret
          script: |                              # runs on VPS
            cd /srv/app
            docker compose up -d
            for i in $(seq 1 30); do
              s=$(docker inspect -f '{{.State.Health.Status}}' api)
              [ "$s" = "healthy" ] && echo "healthy" && exit 0
              sleep 2
            done
            echo "api not healthy"; docker logs --tail 50 api; exit 1
```

Security: `inspect` prints environment variables in clear text, including DB passwords and API keys passed by `-e`. Anyone with docker access can read them. Prefer Docker/Compose secrets or mounted files, never paste inspect output into chats or tickets without redaction, and use inspect to audit for privileged containers, docker.sock mounts, missing limits and root users.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Pasting full `docker inspect` output (with secrets) into a public issue.
✅ Correct: Extract only needed fields with `-f`, and redact.

❌ Mistake 2: Using a name that matches both a container and an image, and reading the wrong object.
✅ Correct: Use `--type container` or `--type image`.

❌ Mistake 3: Template error `map has no entry for key "bridge"` because the network name is wrong.
✅ Correct: Check actual names with `docker inspect -f '{{json .NetworkSettings.Networks}}' api`; compose names are `<project>_<network>`; for keys with special characters use `index`.

❌ Mistake 4: Expecting `.State.Health` for a container with no HEALTHCHECK (template error or empty).
✅ Correct: Guard with `{{if .State.Health}}...{{end}}` or define a healthcheck.

---

## 🧠 Tricky Interview Question
`docker inspect -f '{{.NetworkSettings.IPAddress}}' api` prints an empty line, although the container clearly has an IP on your Compose network. Why?

Answer: `.NetworkSettings.IPAddress` is populated only for the default `bridge` network. Containers attached to user-defined networks (which Compose always uses) have their IPs under `.NetworkSettings.Networks.<network-name>.IPAddress`. Use the per-network path, or loop with `{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}`.

---

## ⚫ Interview Questions + Answers

Q1: What does `docker inspect` return and in what format?
A1: A JSON array of low-level details for each requested object. Use `-f` with Go templates to extract specific fields.

Q2: How do you check why a container died?
A2: `docker inspect -f '{{.State.ExitCode}} {{.State.OOMKilled}} {{.State.Error}}' name`, and `docker logs name`.

Q3: How do you list all env vars a container has?
A3: `docker inspect -f '{{range .Config.Env}}{{println .}}{{end}}' name`.

Q4: How do you find which containers are on a network?
A4: `docker network inspect <net>` and read `.Containers`.

Q5: Difference between `docker inspect` and `docker stats`?
A5: `inspect` is static configuration and state metadata; `stats` is live resource usage (CPU, memory, network, I/O).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Debugging exit codes, networking, mounts, env vars, health, restart loops.
- Scripts that need a specific field; audits.

❌ Avoid when:
- Looking for live CPU/memory: use `docker stats`.
- Sharing output externally without redaction.

---

## 📊 Visual Diagram
```
 docker inspect api
   |
   v
 [
  { "Id": "...", "Name": "/api",
    "State":  { Status, ExitCode, OOMKilled, Health{Status} }   <- why / how is it running
    "Config": { Image, Env[], Cmd[], Labels{} }                 <- what was requested
    "HostConfig": { Memory, RestartPolicy, Privileged, PortBindings }
    "NetworkSettings": { Networks{ backend{ IPAddress } }, Ports }
    "Mounts": [ { Type, Name, Source, Destination, Mode } ]
  }
 ]
   -f '{{.State.ExitCode}}'  ->  137
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| inspect | Show low-level JSON details | Low-level JSON जानकारी दिखाना |
| Go template | `{{...}}` format syntax | `{{...}}` वाला format syntax |
| State | Runtime status of container | Container की runtime स्थिति |
| HostConfig | Settings like limits, ports | Limits, ports जैसी settings |
| Mounts | Volumes and bind mounts attached | जुड़े हुए volumes और bind mounts |
| Digest | Content hash of an image | Image का content hash |

---

## ⚡ 3-Line Summary
English: `docker inspect` prints full JSON metadata for any Docker object.
Use `-f` to get single fields such as exit code, IP, mounts, health.
It exposes secrets in env vars, so handle the output carefully.
Hindi: `docker inspect` किसी भी Docker object का पूरा JSON metadata print करता है।
`-f` से exit code, IP, mounts, health जैसे एक-एक field निकालें।
यह env vars में रखे secrets भी दिखाता है, इसलिए output सावधानी से संभालें।

---

## ➡️ Next Topic
**065. docker stats.** Inspect shows configuration; stats shows live CPU, memory, network and disk usage.

---
