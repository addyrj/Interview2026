# 199. docker compose vs docker-compose
# हिंदी में: docker compose बनाम docker-compose

---

## 🔵 Simple Definition (English)
`docker-compose` (with a hyphen) is the old **Compose V1**, a standalone Python program. `docker compose` (with a space) is **Compose V2**, a Go rewrite shipped as a plugin of the Docker CLI. V1 reached end-of-life (July 2023) and is no longer shipped in current Docker Desktop; V2 is the supported tool.

## 🔵 सरल परिभाषा (Hindi)
`docker-compose` (hyphen वाला) पुराना **Compose V1** है, एक अलग Python program। `docker compose` (space वाला) **Compose V2** है, Go में दोबारा लिखा गया और Docker CLI के plugin के रूप में आता है। V1 July 2023 में end-of-life हो गया और नए Docker Desktop में नहीं आता; V2 ही supported tool है।

---

## 🔴 Problem it Solves
V1 was slow (Python startup), needed a separate install (`pip install docker-compose`), often broke with new Python/OpenSSL versions and lacked features (profiles in full, `watch`, BuildKit by default, better `depends_on` conditions). V2 ships with Docker, is faster, supports the Compose Specification and gets all new features.

## 🔴 यह क्यों बना? (Hindi)
V1 धीमा था (Python startup), अलग install चाहिए था (`pip install docker-compose`), नए Python/OpenSSL versions पर अक्सर टूटता था और features कम थे (पूरे profiles, `watch`, default BuildKit, बेहतर `depends_on` conditions)। V2 Docker के साथ आता है, तेज़ है, Compose Specification support करता है और सारे नए features इसी में आते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Docker CLI sees `docker compose ...` and looks for a CLI plugin named "compose"
Step 2 → Plugin binary lives in ~/.docker/cli-plugins/ or /usr/libexec/docker/cli-plugins/
Step 3 → It talks to the same Docker Engine API as V1 did
Step 4 → `docker-compose` (old) is a separate executable found in $PATH
Step 5 → Many distros ship a tiny "docker-compose" wrapper that just execs `docker compose`
Step 6 → Check which one you have: `docker compose version` vs `docker-compose --version`
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Docker CLI `docker compose ...` देखकर "compose" नाम का CLI plugin ढूँढता है
Step 2 → Plugin binary ~/.docker/cli-plugins/ या /usr/libexec/docker/cli-plugins/ में होती है
Step 3 → यह V1 की तरह उसी Docker Engine API से बात करता है
Step 4 → `docker-compose` (पुराना) $PATH में अलग executable होता है
Step 5 → कई distros एक छोटा "docker-compose" wrapper देते हैं जो सीधे `docker compose` चलाता है
Step 6 → कौन सा है, देखें: `docker compose version` बनाम `docker-compose --version`
```

---

## 🟡 Real World Example
Your **GitHub Actions** pipeline had `run: docker-compose up -d`. On a newer runner image or a fresh **AWS EC2** Ubuntu with only `docker-ce` installed, the step fails with `docker-compose: command not found`. The fix is a one-word change to `docker compose up -d`, plus installing the `docker-compose-plugin` package on the server.

## 🟡 Real Example Hindi mein
आपकी **GitHub Actions** pipeline में `run: docker-compose up -d` था। नई runner image या सिर्फ `docker-ce` वाले fresh **AWS EC2** Ubuntu पर यह `docker-compose: command not found` से फेल होता है। Fix: `docker compose up -d` (एक शब्द बदलना) और server पर `docker-compose-plugin` package install करना।

---

## 💻 Code / Config Example — Basic

```bash
# Which version do I have?
docker compose version              # V2 plugin: prints "Docker Compose version v2.x.y"
docker-compose --version            # V1 (or compatibility wrapper): may say "command not found"

# Install V2 plugin on Ubuntu/Debian (after adding Docker's official apt repo)
sudo apt-get update                                  # refresh package list
sudo apt-get install -y docker-compose-plugin        # installs the `docker compose` plugin
docker compose version                               # verify

# Same commands, only the verb differs
docker compose up -d                # V2
docker-compose up -d                # V1 (legacy)
```
Package names and repos depend on your OS and Docker's current instructions; check Docker docs. Not run locally here.

## 💻 Code / Config Example — Advanced

```bash
#!/usr/bin/env bash
# compose.sh : wrapper that works on servers with either V2 or legacy V1
set -euo pipefail                                    # strict mode

if docker compose version >/dev/null 2>&1; then      # try the V2 plugin first
  DC="docker compose"                                # use V2
elif command -v docker-compose >/dev/null 2>&1; then  # fall back to V1 binary
  DC="docker-compose"                                # legacy
  echo "WARNING: docker-compose V1 is end-of-life, upgrade to V2" >&2
else
  echo "No Docker Compose found" >&2                 # nothing installed
  exit 1
fi

$DC "$@"                                             # pass all arguments through
# usage: ./compose.sh up -d --build
```

```yaml
# .github/workflows/deploy.yml (excerpt): use V2 syntax in CI
name: deploy                                         # workflow name
on:
  push:
    branches: [main]                                 # run on every push to main
jobs:
  test:
    runs-on: ubuntu-latest                           # GitHub-hosted runner, V2 is preinstalled
    steps:
      - uses: actions/checkout@v4                    # example version, update as needed
      - name: Start stack
        run: docker compose up -d --build --wait     # --wait: wait for healthchecks (V2 feature)
      - name: Run tests
        run: docker compose exec -T api npm test     # -T: no TTY in CI
      - name: Tear down
        if: always()                                 # run even if tests failed
        run: docker compose down -v                  # CI only: fine to delete volumes
```

Key differences to remember:

```
Feature                 V1 docker-compose            V2 docker compose
Language                Python                       Go
Install                 pip / standalone binary      Docker plugin (docker-compose-plugin)
Status                  End-of-life (2023)           Supported
Default project name    folder name, strips _ and -  folder name, normalised differently
Container names         project_service_1            project-service-1  (hyphens)
`version:` key          needed                       obsolete (ignored with a warning)
Profiles/watch/--wait   partial / none               full
```

---

## 🟠 My Stack Integration
- **VPS / EC2 deploy**: install `docker-compose-plugin`, and use `docker compose` in all scripts.
- **GitHub Actions**: runners ubuntu-latest include the V2 plugin; keep `docker compose` in workflow files.
- **Node.js/FastAPI Dockerfiles** are unaffected; only the orchestration command changes.
- **Nginx upstream names** stay the same, but container names changed from `_` to `-` (`myapp-api-1`), so any script that greps container names must be updated.

```bash
# migrate old scripts safely (review the diff before committing)
grep -rl "docker-compose " .github scripts deploy 2>/dev/null \
  | xargs sed -i.bak 's/docker-compose /docker compose /g'   # replace verb; .bak files kept
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Installing V1 via `pip install docker-compose` on a new server.
✅ Correct: Install the `docker-compose-plugin` from Docker's repo.

❌ Mistake 2: Scripts that hard-code container names like `myapp_api_1`.
✅ Correct: Use `docker compose exec api ...` (service name) or `docker compose ps -q api`.

❌ Mistake 3: Keeping `version: "3.8"` and thinking it selects the engine.
✅ Correct: Delete it. V2 ignores it and warns that it is obsolete.

❌ Mistake 4: Mixing V1 and V2 on the same project, then seeing orphan/duplicate containers because the naming scheme differs.
✅ Correct: Stop with the same tool that started it, then migrate once with `down` and `up`.

---

## 🧠 Tricky Interview Question
After moving a server from V1 to V2 your old containers `app_db_1` keep running and `docker compose up` creates `app-db-1` too, with a new empty volume. Why and how to fix?

Answer: V1 and V2 name containers differently, and Compose finds its containers through labels. The volumes are keyed by project and volume name, so if the project name normalisation differs, a new volume appears. Fix: `docker-compose down` with V1 (without `-v`), set `name:` or `COMPOSE_PROJECT_NAME` to the exact old project name so volumes match (`docker volume ls` to confirm), then `docker compose up -d`. Back up the data first.

---

## ⚫ Interview Questions + Answers

Q1: Is V1 still supported?
A1: No. It reached end-of-life in July 2023; use V2.

Q2: Where does the V2 binary live?
A2: As a Docker CLI plugin, e.g. `/usr/libexec/docker/cli-plugins/docker-compose` or `~/.docker/cli-plugins/docker-compose`.

Q3: Does the compose file format change?
A3: Both read the same file; V2 follows the Compose Specification and treats `version:` as obsolete.

Q4: Why is V2 faster?
A4: It is a compiled Go binary integrated into the Docker CLI, uses BuildKit by default and starts services in parallel.

Q5: Can I keep typing `docker-compose`?
A5: Only if a compatibility alias/wrapper exists; best to switch scripts to `docker compose`.

---

## 🔷 When to Use + When Not to Use
✅ Use V2 when:
- Anything new: servers, CI, local dev.

❌ Use V1 only when:
- A legacy host cannot upgrade Docker (plan the upgrade anyway).

---

## 📊 Visual Diagram
```
 V1:  shell ---> docker-compose (python binary) ---> Docker Engine API
 V2:  shell ---> docker ---> [compose plugin (Go)] ---> Docker Engine API

 names:   V1  myapp_api_1        V2  myapp-api-1
 install: V1  pip/binary         V2  apt install docker-compose-plugin
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Compose V1 | Old Python `docker-compose` | पुराना Python `docker-compose` |
| Compose V2 | Go plugin `docker compose` | Go वाला plugin `docker compose` |
| CLI plugin | Extension loaded by docker CLI | docker CLI का extension |
| EOL | End of life, no updates | समर्थन समाप्त |
| Compose Specification | Open spec of the file format | file format का open standard |

---

## ⚡ 3-Line Summary
English: `docker compose` (V2 plugin) replaces the legacy `docker-compose` (V1).
V1 is end-of-life; V2 is faster, ships with Docker and gets new features.
Update scripts and CI, and watch for the `_` to `-` container name change.
Hindi: `docker compose` (V2 plugin) ने पुराने `docker-compose` (V1) की जगह ले ली है।
V1 end-of-life है; V2 तेज़ है, Docker के साथ आता है और नए features पाता है।
Scripts और CI बदलें और container नाम में `_` से `-` का बदलाव ध्यान रखें।

---

## ➡️ Next Topic
**200. Compose Watch (live reload)**: a V2-only feature that syncs or rebuilds containers when your source files change.
