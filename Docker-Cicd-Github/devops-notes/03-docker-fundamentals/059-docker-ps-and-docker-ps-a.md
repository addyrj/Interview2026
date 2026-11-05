---

# 059. docker ps + docker ps -a
# हिंदी में: docker ps और docker ps -a

---

## 🔵 Simple Definition (English)
`docker ps` lists **running** containers. `docker ps -a` (all) lists running **and** stopped/exited containers. It shows ID, image, command, age, status, published ports and name, and supports filters and custom formats.

## 🔵 सरल परिभाषा (Hindi)
`docker ps` सिर्फ **चल रहे** containers दिखाता है। `docker ps -a` (all) चल रहे **और** रुके/exit हुए containers दोनों दिखाता है। यह ID, image, command, उम्र, status, published ports और name दिखाता है, और filters और custom format support करता है।

---

## 🔴 Problem it Solves
After starting containers you need to know what exists, what is healthy and what crashed. A crashed container vanishes from plain `docker ps`, so people think it never started. `docker ps -a` shows the corpse with its exit code, which is the first clue in debugging.

## 🔴 यह क्यों बना? (Hindi)
Containers चलाने के बाद जानना होता है कि क्या मौजूद है, क्या healthy है और क्या crash हुआ। Crash हुआ container साधारण `docker ps` से गायब हो जाता है, तो लोग सोचते हैं कि वह कभी चला ही नहीं। `docker ps -a` उसे exit code के साथ दिखाता है, जो debugging का पहला सुराग है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → CLI calls the daemon API: GET /containers/json (add ?all=1 for -a)
Step 2 → Daemon returns container metadata and live state
Step 3 → CLI applies --filter and --format on the result
Step 4 → CLI prints a table (or your template) sorted newest first
Step 5 → You read STATUS: "Up 3 hours", "Up 2 min (healthy)", "Exited (1) 5 min ago", "Restarting (1)"
Step 6 → Use the NAME/ID with logs, inspect, exec, stop, rm
```

Status meanings:
- `Up ...` running; `(healthy)` / `(unhealthy)` / `(health: starting)` from HEALTHCHECK.
- `Exited (0)` finished normally; `Exited (1)` app error; `Exited (137)` killed (OOM or `docker kill`/SIGKILL); `Exited (143)` stopped by SIGTERM.
- `Restarting` crash loop with a restart policy.
- `Created` made but never started; `Paused`; `Dead` (rare, broken removal).

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → CLI daemon API call करता है: GET /containers/json (-a के लिए ?all=1)
Step 2 → Daemon container metadata और live state लौटाता है
Step 3 → CLI result पर --filter और --format लगाता है
Step 4 → CLI table (या आपका template) print करता है, नया सबसे ऊपर
Step 5 → आप STATUS पढ़ते हैं: "Up 3 hours", "Up 2 min (healthy)", "Exited (1) 5 min ago", "Restarting (1)"
Step 6 → NAME/ID को logs, inspect, exec, stop, rm के साथ इस्तेमाल करें
```

Status के मतलब:
- `Up ...` चल रहा है; `(healthy)` / `(unhealthy)` / `(health: starting)` HEALTHCHECK से।
- `Exited (0)` सामान्य रूप से खत्म; `Exited (1)` app error; `Exited (137)` kill हुआ (OOM या `docker kill`/SIGKILL); `Exited (143)` SIGTERM से रुका।
- `Restarting` crash loop जहाँ restart policy है।
- `Created` बना पर कभी start नहीं हुआ; `Paused`; `Dead` (दुर्लभ, remove टूटा)।

---

## 🟡 Real World Example
Monday morning your React site shows 502. `docker ps` shows `nginx` and `db` but no `api`. `docker ps -a` shows `api  Exited (137) 3 hours ago`. Code 137 means SIGKILL, most likely the kernel OOM killer on a 1 GB VPS. You confirm with `docker inspect -f '{{.State.OOMKilled}}' api` (true), then raise the memory limit or add swap. Without `-a` you would have guessed for an hour.

## 🟡 Real Example Hindi mein
सोमवार सुबह आपकी React site 502 दिखा रही है। `docker ps` में `nginx` और `db` हैं पर `api` नहीं। `docker ps -a` दिखाता है `api  Exited (137) 3 hours ago`। Code 137 मतलब SIGKILL, ज़्यादातर 1 GB VPS पर kernel OOM killer। आप `docker inspect -f '{{.State.OOMKilled}}' api` (true) से confirm करते हैं, फिर memory limit बढ़ाते हैं या swap जोड़ते हैं। `-a` के बिना आप घंटे भर अंदाज़ा लगाते रहते।

---

## 💻 Code / Config Example — Basic

```bash
# --- docker ps basics ---
docker ps                                        # only running containers
docker ps -a                                     # all containers, including exited
docker ps -q                                     # only IDs of running containers (good for scripts)
docker ps -aq                                    # only IDs of all containers
docker ps -l                                     # the latest created container
docker ps -n 3                                   # last 3 created containers
docker ps -s                                     # add SIZE column (writable layer size)
docker ps --no-trunc                             # full IDs and full commands
docker ps -a --filter "status=exited"            # only exited containers
docker ps -a --filter "name=api"                 # names containing "api"
```

## 💻 Code / Config Example — Advanced

```bash
#!/usr/bin/env bash
# ps-report.sh - operational report using docker ps filters and formats (real flags, Docker 20.10+)
set -euo pipefail                                # strict shell mode

echo "== Running containers =="                  # section title
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'   # readable table

echo "== Unhealthy containers =="                # health problems
docker ps --filter "health=unhealthy" --format '{{.Names}}: {{.Status}}'   # only unhealthy ones

echo "== Crashed (non-zero exit) containers =="  # exited with an error
docker ps -a --filter "status=exited" --format '{{.Names}} {{.Status}}' | grep -v "Exited (0)" || true   # hide clean exits

echo "== Containers in restart loop =="          # restart policy keeps failing
docker ps -a --filter "status=restarting" --format '{{.Names}} {{.Status}}'   # status=restarting

echo "== Containers of compose project 'app' =="   # filter by label compose adds automatically
docker ps -a --filter "label=com.docker.compose.project=app" --format '{{.Names}}'   # project name = folder name by default

echo "== Containers started from image ancestor =="   # which containers use this image
docker ps -a --filter "ancestor=nginx:1.27-alpine" --format '{{.Names}}'   # example tag

echo "== Exit codes with OOM flag =="            # explain 137
for c in $(docker ps -aq); do                     # loop over all IDs
  docker inspect -f '{{.Name}} exit={{.State.ExitCode}} oom={{.State.OOMKilled}}' "$c"   # exit code + OOM info
done
```

```bash
# Set a nicer default table format once (writes ~/.docker/config.json psFormat key)
mkdir -p ~/.docker                               # ensure config folder exists
# Add this key manually to ~/.docker/config.json (merge with existing JSON):
# "psFormat": "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"
```

---

## 🟠 My Stack Integration
- **Compose**: `docker compose ps` is project-scoped and shows service names and health; `docker ps -a` shows everything on the host.
- **FastAPI/Node.js**: seeing `(healthy)` requires a `HEALTHCHECK` in the Dockerfile or compose.
- **Nginx**: if `nginx` is `Restarting`, check config with `docker logs nginx` (usually a bad `upstream` or missing cert).
- **VPS monitoring**: a cron or GitHub Actions SSH step can run `docker ps --filter health=unhealthy -q` and alert if the output is non-empty.
- **AWS**: ECS has the equivalent in the console (task status); on EC2 you use this command.

```yaml
# .github/workflows/post-deploy-check.yml - fail the pipeline if any container is unhealthy after deploy
name: post-deploy-check                          # workflow name
on:
  workflow_dispatch:                             # manual trigger
jobs:
  verify:
    runs-on: ubuntu-latest                       # runner
    steps:
      - name: Check containers on VPS            # SSH and inspect
        uses: appleboy/ssh-action@v1.0.3         # example version, update as needed
        with:
          host: ${{ secrets.VPS_HOST }}          # server address from secrets
          username: deploy                       # user in docker group
          key: ${{ secrets.VPS_SSH_KEY }}        # SSH private key from secrets
          script: |                              # commands on the VPS
            if [ -n "$(docker ps -q --filter health=unhealthy)" ]; then
              docker ps --filter health=unhealthy
              exit 1
            fi
            echo "All containers healthy"
```

Security: `docker ps` output shows commands, which may include secrets if you passed them as arguments; do not paste raw `--no-trunc` output into public tickets. Docker group access is needed to run it, which is root-equivalent.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `docker ps` to look for a crashed container.
✅ Correct: Use `docker ps -a` and read the Exit code.

❌ Mistake 2: Parsing the table with `awk` in scripts.
✅ Correct: Use `--format '{{.Names}}'` or `-q`; the table layout can change.

❌ Mistake 3: Ignoring `Restarting` status because "it is running".
✅ Correct: It is a crash loop; inspect logs immediately.

❌ Mistake 4: Thinking `(healthy)` means the app works for users.
✅ Correct: It only means the healthcheck command passed. Test through Nginx/public URL as well.

---

## 🧠 Tricky Interview Question
`docker ps -a` shows 200 old `Exited` containers and the disk is full, even though you only run 5 services. What happened and how do you fix it safely?

Answer: Containers started with `docker run` without `--rm` (CI jobs, cron tasks, one-off scripts) keep their writable layers and logs after exit. Remove them with `docker container prune` (add `--filter "until=24h"` to be careful) and use `--rm` for one-off commands in future. Also set log rotation, because huge `json-file` logs are another common disk eater. Check with `docker ps -as` and `docker system df`.

---

## ⚫ Interview Questions + Answers

Q1: Difference between `docker ps` and `docker ps -a`?
A1: Without `-a` only running containers; with `-a` also created, exited, paused and dead containers.

Q2: What does exit code 137 mean?
A2: 128 + 9: the process received SIGKILL, commonly from the OOM killer or `docker kill`. Exit 143 is 128 + 15 (SIGTERM).

Q3: How do you list only container names?
A3: `docker ps --format '{{.Names}}'`.

Q4: How do you find containers using a given network, volume or image?
A4: `--filter network=...`, `--filter volume=...`, `--filter ancestor=image`.

Q5: What is the difference between `docker ps` and `docker compose ps`?
A5: `docker compose ps` lists only containers of the current compose project (using compose labels); `docker ps` lists everything on the daemon.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- First step of any incident: what is running, what died.
- Scripts that need container IDs/names.

❌ Avoid when:
- You need live resource numbers: use `docker stats`.
- You need configuration details: use `docker inspect`.

---

## 📊 Visual Diagram
```
 docker ps          -> [ Up ]  [ Up (healthy) ]  [ Restarting ]
 docker ps -a       -> [ Up ]  [ Up (healthy) ]  [ Restarting ]  [ Exited (0) ]  [ Exited (137) ]  [ Created ]

 lifecycle:
 created --start--> running --stop/exit--> exited --rm--> (gone)
                       |  ^
                    pause  unpause
 CONTAINER ID | IMAGE | COMMAND | CREATED | STATUS | PORTS | NAMES
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Status | Current state text | मौजूदा स्थिति |
| Exit code | Number the process returned | Process का लौटाया number |
| Healthcheck | Command Docker runs to test health | Health जाँचने वाला command |
| Filter | Narrow the list | List को छोटा करना |
| Format | Go template for output | Output का template |
| Crash loop | Repeated fail-restart cycle | बार-बार fail और restart |

---

## ⚡ 3-Line Summary
English: `docker ps` shows running containers; `-a` adds stopped ones with exit codes.
Use filters and `--format` for scripts instead of parsing tables.
Exit 137 usually means killed (often OOM); 143 means SIGTERM.
Hindi: `docker ps` चल रहे containers दिखाता है; `-a` रुके हुए भी exit codes के साथ दिखाता है।
Scripts में table parse करने की जगह filters और `--format` इस्तेमाल करें।
Exit 137 का मतलब आमतौर पर kill (अक्सर OOM); 143 मतलब SIGTERM।

---

## ➡️ Next Topic
**060. docker stop + docker kill.** Learn how to stop containers gracefully versus forcefully.

---
