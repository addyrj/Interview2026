# 203. Environment Specific Configs
# हिंदी में: Environment के अनुसार अलग Configs (dev / test / staging / prod)

---

## 🔵 Simple Definition (English)
Environment-specific configs mean running the same application with different settings per environment (development, testing, staging, production) by combining a base Compose file, small per-environment files, and per-environment `.env` files, without duplicating the whole setup.

## 🔵 सरल परिभाषा (Hindi)
Environment-specific configs का मतलब है एक ही application को हर environment (development, testing, staging, production) में अलग settings से चलाना: base Compose file + छोटी per-environment files + per-environment `.env` files, पूरा setup duplicate किए बिना।

---

## 🔴 Problem it Solves
One giant compose file with `if dev then ...` comments becomes unreadable, and one wrong setting (a dev password, debug mode on, a published DB port) in production is a security incident. Teams need a repeatable way to say "same app, different settings" and to be sure which settings will be used.

## 🔴 यह क्यों बना? (Hindi)
एक बड़ी compose file जिसमें "dev में ये, prod में वो" comments हों, पढ़ने लायक नहीं रहती, और production में एक गलत setting (dev password, debug mode on, खुला DB port) सीधा security incident है। Teams को "same app, अलग settings" का दोहराने योग्य तरीका और यह यकीन चाहिए कि कौन सी settings इस्तेमाल होंगी।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Base file compose.yaml: services common to all environments
Step 2 → Per-env files: compose.dev.yaml, compose.test.yaml, compose.prod.yaml (only differences)
Step 3 → Per-env variable files: .env.dev, .env.prod (git-ignored, secrets)
Step 4 → Choose at runtime: docker compose --env-file .env.prod -f compose.yaml -f compose.prod.yaml up -d
Step 5 → Compose substitutes ${VARS} from the chosen env file / shell
Step 6 → Optional: set COMPOSE_FILE and COMPOSE_PROJECT_NAME in env to avoid long commands
Step 7 → Verify with `docker compose ... config` before applying
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Base file compose.yaml: सभी environments की common services
Step 2 → Per-env files: compose.dev.yaml, compose.test.yaml, compose.prod.yaml (सिर्फ फर्क)
Step 3 → Per-env variable files: .env.dev, .env.prod (git-ignored, secrets)
Step 4 → Runtime पर चुनें: docker compose --env-file .env.prod -f compose.yaml -f compose.prod.yaml up -d
Step 5 → Compose चुनी हुई env file / shell से ${VARS} भरता है
Step 6 → Optional: लंबी commands से बचने के लिए COMPOSE_FILE और COMPOSE_PROJECT_NAME env में रखें
Step 7 → लागू करने से पहले `docker compose ... config` से जाँचें
```

---

## 🟡 Real World Example
An ed-tech company has 3 targets: laptops (dev), a GitHub Actions runner (test), and an EC2 server (prod). The base file defines `api`, `postgres`, `redis`. Dev adds hot reload; test uses a throwaway DB with tmpfs; prod uses a registry image `ghcr.io/acme/api:1.4.2`, restart policies and resource limits. The CD pipeline simply runs the prod command, nobody edits YAML on the server.

## 🟡 Real Example Hindi mein
एक ed-tech कंपनी के 3 targets हैं: laptops (dev), GitHub Actions runner (test) और EC2 server (prod)। Base file में `api`, `postgres`, `redis` हैं। Dev hot reload जोड़ता है; test tmpfs वाला throwaway DB; prod registry image `ghcr.io/acme/api:1.4.2`, restart policies और resource limits। CD pipeline बस prod command चलाती है, server पर कोई YAML edit नहीं करता।

---

## 💻 Code / Config Example — Basic
```yaml
# compose.yaml  (BASE)
services:
  api:
    image: ${API_IMAGE}              # image name comes from the env file
    environment:
      NODE_ENV: ${NODE_ENV}          # development / production
    ports:
      - "${API_PORT}:3000"           # host port differs per env
```
```bash
# .env.dev  (dev values)
API_IMAGE=myapp-api:dev
NODE_ENV=development
API_PORT=3000
```
```bash
# Run dev (comments: --env-file picks the variable file)
docker compose --env-file .env.dev up -d
```

## 💻 Code / Config Example — Advanced
```yaml
# compose.yaml  (BASE: common to all)
name: myapp                           # fixed project name so volumes/networks are predictable
services:
  api:
    image: ${API_IMAGE:?API_IMAGE is required}   # fail fast if missing
    environment:
      NODE_ENV: ${NODE_ENV:-production}          # default production if unset
      DATABASE_URL: postgres://app:${DB_PASS:?}@postgres:5432/app  # required secret
    depends_on:
      postgres: { condition: service_healthy }   # wait for DB
  postgres:
    image: postgres:16-alpine                    # example tag
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: ${DB_PASS:?}
      POSTGRES_DB: app
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app"]
      interval: 5s
      timeout: 3s
      retries: 10
```
```yaml
# compose.prod.yaml  (PROD differences only)
services:
  api:
    restart: unless-stopped                      # self-heal
    deploy:
      resources:
        limits: { cpus: "1.00", memory: 512M }   # cap resources
    read_only: true                              # immutable root filesystem
    tmpfs: ["/tmp"]                              # writable temp only
    logging:
      driver: json-file                          # default driver
      options: { max-size: "10m", max-file: "3" }  # rotate logs, protect disk
  postgres:
    restart: unless-stopped
    volumes:
      - pgdata:/var/lib/postgresql/data          # persist
volumes:
  pgdata: {}
```
```yaml
# compose.test.yaml  (TEST differences only)
services:
  postgres:
    tmpfs: ["/var/lib/postgresql/data"]          # RAM database, fast and disposable
  api:
    command: ["npm", "test"]                     # run tests instead of the server
```
```bash
# Commands (all comments: what each does)
docker compose --env-file .env.prod -f compose.yaml -f compose.prod.yaml config   # preview merged result
docker compose --env-file .env.prod -f compose.yaml -f compose.prod.yaml up -d    # deploy prod
docker compose --env-file .env.test -f compose.yaml -f compose.test.yaml up --abort-on-container-exit  # CI test run
```

---

## 🟠 My Stack Integration
- **Node.js:** `NODE_ENV=production` in prod (faster, fewer logs of internals), `development` locally.
- **FastAPI:** pass `ENV`/`LOG_LEVEL` the same way; prod runs without `--reload`.
- **React:** build-time variables are baked into the bundle (`VITE_API_URL`), so they must be build args per environment, not runtime env.
- **Nginx:** mount a different conf per environment (dev: HTTP only; prod: TLS with Let's Encrypt).
- **VPS/AWS:** keep `.env.prod` on the server only (chmod 600) or pull from AWS SSM Parameter Store / Secrets Manager in the deploy step.
- **Security:** `.env.*` files containing secrets must be in `.gitignore`; commit `.env.example` with fake values.

```bash
# deploy.sh  (on the VPS, called by GitHub Actions over SSH)
set -euo pipefail                                   # stop on error, undefined var, pipe failure
cd /opt/myapp                                       # app folder
docker compose --env-file .env.prod -f compose.yaml -f compose.prod.yaml pull   # fetch new images
docker compose --env-file .env.prod -f compose.yaml -f compose.prod.yaml up -d --remove-orphans  # apply
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Committing `.env.prod` with real passwords.
✅ Correct: Git-ignore it, commit `.env.example`, load real values from the server or a secret manager.

❌ Mistake 2: Using `.env` and `--env-file` together and assuming both load. `--env-file` replaces the default `.env` for interpolation.
✅ Correct: Be explicit; put all needed variables in the file you pass.

❌ Mistake 3: Putting React runtime config in container env and expecting the bundle to change.
✅ Correct: Pass as build args, or serve a runtime `config.js` from Nginx.

❌ Mistake 4: Missing variables silently become empty strings.
✅ Correct: Use `${VAR:?message}` for required values.

---

## 🧠 Tricky Interview Question
A variable is set in your shell, in `.env`, and in the `environment:` block of the service with different values. Which wins inside the container?

Answer: For interpolation (`${VAR}` in the YAML) precedence is: shell environment, then `--env-file` / `.env`, then defaults in the expression. For what the container actually receives, the `environment:` key beats `env_file:` entries. So the value written directly in `environment:` wins inside the container, even though the shell value was used to fill any `${}` placeholders in the YAML.

---

## ⚫ Interview Questions + Answers

Q1: How do you pick an environment at deploy time?
A1: Pass `--env-file` and `-f` files, or export `COMPOSE_FILE` and `COMPOSE_PROJECT_NAME`.

Q2: Why a fixed project `name:`?
A2: Project name prefixes networks and volumes. Different folder names would create different volumes and "lose" data; fixing it keeps names stable.

Q3: Difference between `env_file:` and `--env-file`?
A3: `env_file:` (service key) injects variables into the container. `--env-file` (CLI) supplies values for `${}` interpolation in the Compose file.

Q4: How do you keep secrets safer than env vars?
A4: Docker secrets or mounted files (`*_FILE` convention), since env vars show up in `docker inspect`.

Q5: How do you stop prod drifting from the repo?
A5: Deploy only from CI with a pinned image tag and committed compose files, and run `config` in the pipeline.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Same app runs in 2+ environments.
- You want reviewable, minimal per-env diffs.

❌ Avoid when:
- You need multi-node orchestration with per-cluster rollout (use Kubernetes + Helm/Kustomize).
- A single tiny hobby app with one environment.

---

## 📊 Visual Diagram
```
                     compose.yaml (base)
                    /        |         \
      compose.dev.yaml  compose.test.yaml  compose.prod.yaml
            |                 |                  |
        .env.dev          .env.test          .env.prod (server only)
            |                 |                  |
        laptop            CI runner         EC2 / VPS
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| environment | dev/test/staging/prod stage | चरण/वातावरण |
| interpolation | `${VAR}` substitution | ${VAR} की जगह value भरना |
| `--env-file` | Variable file for substitution | variables की file |
| `COMPOSE_FILE` | Env var listing compose files | compose files की सूची |
| project name | Prefix for resources | resources का prefix |
| `.env.example` | Safe template without secrets | बिना secret का template |

---

## ⚡ 3-Line Summary
English: Use one base file plus small per-environment files and env files. Choose them explicitly at runtime and preview with `config`. Keep secrets out of git.
Hindi: एक base file और छोटी per-environment files व env files रखें। Runtime पर उन्हें साफ़ तौर पर चुनें और `config` से preview करें। Secrets को git से बाहर रखें।

---

## ➡️ Next Topic
**204. Compose for Development**: now we build the best dev loop with hot reload, debugger and seed data.
