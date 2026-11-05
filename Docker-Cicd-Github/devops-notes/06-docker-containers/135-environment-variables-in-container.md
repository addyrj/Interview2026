---

# 135. Environment Variables in Container
# हिंदी में: Container में Environment Variables

---

## 🔵 Simple Definition (English)
Environment variables are key-value settings passed into a container at run time (`-e`, `--env-file`, Compose `environment:`), so the same image can run with different configuration (database URL, mode, API keys) without rebuilding.

## 🔵 सरल परिभाषा (Hindi)
Environment variables run time पर container को दिए गए key-value settings हैं (`-e`, `--env-file`, Compose `environment:`), ताकि एक ही image अलग configuration (database URL, mode, API keys) के साथ बिना rebuild के चले।

---

## 🔴 Problem it Solves
Hardcoding `DB_URL=localhost` or secrets inside code or the image forces a rebuild per environment and leaks passwords into Git and image layers. The twelve-factor approach says: config lives in the environment. One image, many environments, secrets injected only where needed.

## 🔴 यह क्यों बना? (Hindi)
Code या image में `DB_URL=localhost` या secrets hardcode करने से हर environment के लिए rebuild करना पड़ता है और passwords Git व image layers में leak होते हैं। Twelve-factor का नियम: config environment में रहे। एक image, कई environments, secrets सिर्फ़ वहीं inject जहाँ चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Image may define defaults:       ENV NODE_ENV=production   (in Dockerfile)
Step 2 → At run time you override/add:    -e KEY=VAL  or  --env-file file
Step 3 → dockerd stores them in container config (visible in `docker inspect`)
Step 4 → PID 1 starts with these in its process environment
Step 5 → App reads them:  process.env.KEY (Node)  /  os.environ["KEY"] (Python)
```
Precedence (Docker run): `-e` wins over `--env-file`, which wins over Dockerfile `ENV`.

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Image defaults दे सकती है:       ENV NODE_ENV=production   (Dockerfile में)
Step 2 → Run time पर override/add:        -e KEY=VAL  या  --env-file file
Step 3 → dockerd इन्हें container config में रखता है (`docker inspect` में दिखते हैं)
Step 4 → PID 1 इन्हीं environment के साथ शुरू होता है
Step 5 → App पढ़ती है:  process.env.KEY (Node)  /  os.environ["KEY"] (Python)
```
Precedence: `-e` > `--env-file` > Dockerfile `ENV`।

---

## 🟡 Real World Example
A Razorpay-style payment service: staging uses `PAYMENT_KEY=test_...` and `DB_HOST=staging-db`; production uses live keys and an RDS endpoint. The CI builds one image `pay-api:1.9.0`. Staging VPS has `/opt/pay/.env.staging`, production has `/opt/pay/.env.production` (chmod 600). Same bits, different behaviour, nothing secret ever in Git.

## 🟡 Real Example Hindi mein
Razorpay जैसी payment service: staging में `PAYMENT_KEY=test_...` और `DB_HOST=staging-db`; production में live keys और RDS endpoint। CI एक ही image `pay-api:1.9.0` बनाता है। Staging VPS पर `/opt/pay/.env.staging`, production पर `/opt/pay/.env.production` (chmod 600)। वही bits, अलग व्यवहार, और Git में कोई secret नहीं।

---

## 💻 Code / Config Example — Basic
```bash
#!/usr/bin/env bash
# env-basic.sh - ways to pass variables
docker run --rm -e GREETING=hello alpine:3.20 sh -c 'echo $GREETING'     # explicit value -> prints hello
export APP_MODE=staging                                                   # set in YOUR shell
docker run --rm -e APP_MODE alpine:3.20 sh -c 'echo $APP_MODE'           # no "=": copies value from host shell

cat > /tmp/demo.env <<'EOF'
# comments are allowed in env files
DB_HOST=db
DB_PORT=5432
EOF
docker run --rm --env-file /tmp/demo.env alpine:3.20 env | grep DB_      # loads all lines from file
# env-file rules: KEY=VAL per line, no quotes processing, no "export", no spaces around "="

docker run -d --name e1 -e SECRET=abc alpine:3.20 sleep 60               # see how visible it is...
docker inspect -f '{{.Config.Env}}' e1                                    # ...anyone with docker access can read it
docker rm -f e1                                                           # cleanup
```

## 💻 Code / Config Example — Advanced
```yaml
# docker-compose.yml - layered configuration for a Node.js + Postgres stack
services:
  api:
    image: myorg/orders-api:1.4.2           # example pinned tag
    env_file:
      - ./config/common.env                 # shared non-secret settings (committed to Git)
      - ./secrets/api.env                   # secrets (in .gitignore, chmod 600, created by CI/ops)
    environment:
      NODE_ENV: production                  # explicit value; overrides same key in env_file
      PORT: "3000"                          # app port (quoted: env values are strings)
      DB_HOST: db                           # Compose service name used as hostname
      DB_PASSWORD_FILE: /run/secrets/db_password   # pattern: pass a FILE path, not the secret
      LOG_LEVEL: ${LOG_LEVEL:-info}         # ${VAR:-default}: taken from shell/.env of compose, default info
    secrets:
      - db_password                         # mounts file at /run/secrets/db_password
    depends_on:
      db:
        condition: service_healthy          # wait until DB healthcheck passes

  db:
    image: postgres:16-alpine               # example tag
    environment:
      POSTGRES_USER: app                    # DB user created on first init
      POSTGRES_DB: orders                   # DB name created on first init
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password   # official image supports *_FILE variables
    secrets:
      - db_password                         # same secret mounted for DB
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d orders"]   # ready check
      interval: 5s                          # every 5 seconds
      timeout: 3s                           # per check timeout
      retries: 10                           # allow slow first boot

secrets:
  db_password:
    file: ./secrets/db_password.txt         # local file (dev/VPS); use AWS Secrets Manager in AWS
```
```js
// config.js - read a secret from env or from a *_FILE path (Node.js)
const fs = require('fs');                                      // file reading
function secret(name) {                                        // helper
  const file = process.env[name + '_FILE'];                    // e.g. DB_PASSWORD_FILE
  if (file) return fs.readFileSync(file, 'utf8').trim();       // Docker secret file wins
  return process.env[name];                                    // fallback to plain env var
}
module.exports = { dbPassword: secret('DB_PASSWORD') };        // export config
```

---

## 🟠 My Stack Integration
**Node.js**: read via `process.env`; fail fast at boot if a required variable is missing. For React builds, `REACT_APP_*`/`VITE_*` variables are baked at build time and public in the browser bundle, so never put secrets there.
**FastAPI**: use `pydantic-settings` (`BaseSettings`) to load and validate env vars.
**Nginx**: the official image can template configs with `envsubst` (files in `/etc/nginx/templates/*.template`), a handy way to inject `API_HOST`.
**VPS**: `/opt/app/.env` with `chmod 600`, owned by the deploy user. **AWS**: ECS task definition `secrets` pulls from Secrets Manager/SSM Parameter Store into env vars at launch.

```yaml
# GitHub Actions step: write env file on the VPS from GitHub Secrets (example)
- name: Deploy env file
  run: |
    ssh deploy@$HOST "umask 077 && cat > /opt/app/.env" <<EOF   # umask 077 => file readable by owner only
    DB_URL=${{ secrets.DB_URL }}
    JWT_SECRET=${{ secrets.JWT_SECRET }}
    EOF
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `ENV API_KEY=...` or `ARG` secrets in the Dockerfile.
✅ Correct: they stay in image layers/history forever. Inject at run time or use BuildKit secret mounts.

❌ Mistake 2: Committing `.env` to Git.
✅ Correct: commit `.env.example` only; add `.env` to `.gitignore` and `.dockerignore`.

❌ Mistake 3: Quotes in env-file, like `KEY="value"`.
✅ Correct: `docker run --env-file` keeps quotes literally (Compose handles them differently). Write `KEY=value`.

❌ Mistake 4: Expecting changed `.env` to apply to a running container.
✅ Correct: env is fixed at creation. Recreate the container (`docker compose up -d --force-recreate`).

❌ Mistake 5: Logging `process.env` on startup.
✅ Correct: log only non-secret keys.

**Security**: env vars are visible via `docker inspect`, `/proc/<pid>/environ` and crash dumps; for high-value secrets prefer mounted secret files or a secret manager.

---

## 🧠 Tricky Interview Question
You changed `DB_HOST` in `.env`, ran `docker compose restart api`, and the app still uses the old value. Why?

Answer: `restart` stops and starts the same container, whose environment was set at creation. Compose reads `.env` only when creating containers. Run `docker compose up -d` (it recreates when config changed) or `--force-recreate`. Also check precedence: a value in `environment:` overrides `env_file:`, and a variable exported in your shell overrides the `.env` file used for `${}` substitution.

---

## ⚫ Interview Questions + Answers

Q1: How do you pass env variables to a container?
A1: `-e KEY=VAL`, `--env-file file`, Dockerfile `ENV` defaults, or Compose `environment:`/`env_file:`.

Q2: `ENV` vs `ARG` in a Dockerfile?
A2: `ENV` persists into the running container; `ARG` exists only at build time (but still appears in image history, so not for secrets).

Q3: Are env variables a safe place for secrets?
A3: Acceptable for small setups but visible via inspect and /proc. Better: Docker/Compose secrets, Kubernetes secrets, or AWS Secrets Manager.

Q4: How do you inspect the env of a running container?
A4: `docker exec NAME env` or `docker inspect -f '{{.Config.Env}}' NAME`.

Q5: Why do React env vars not hide secrets?
A5: They are substituted into static JS at build time and shipped to every browser.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Environment-specific config (URLs, flags, modes, ports).
- Twelve-factor style apps on VPS/ECS.

❌ Avoid when:
- Very sensitive secrets in shared hosts: use secret files/managers.
- Large structured config: mount a config file.

---

## 📊 Visual Diagram
```
 Dockerfile ENV (defaults)
        |   overridden by
 --env-file prod.env
        |   overridden by
 -e KEY=VAL  (highest)
        v
 +-------------------------+
 | container process env   |--> process.env.DB_URL / os.environ["DB_URL"]
 +-------------------------+
   visible via: docker inspect, /proc/PID/environ
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ENV | Dockerfile default variable | Dockerfile का default variable |
| ARG | Build-time only variable | सिर्फ़ build के समय का variable |
| env-file | File of KEY=VAL lines | KEY=VAL वाली file |
| Twelve-factor | Config lives in environment | Config environment में रहे |
| Secret | Sensitive value | संवेदनशील मान |

---

## ⚡ 3-Line Summary
English: Environment variables configure one image for many environments at run time.
Precedence is `-e` over `--env-file` over Dockerfile `ENV`; changes need container recreation.
Never bake secrets into images or Git; prefer secret files or managers.

Hindi: Environment variables एक image को run time पर कई environments के लिए configure करते हैं।
Precedence `-e`, फिर `--env-file`, फिर Dockerfile `ENV`; बदलाव के लिए container दोबारा बनाना पड़ता है।
Secrets को image या Git में कभी न रखें; secret files या managers इस्तेमाल करें।

---

## ➡️ Next Topic
**136. Container Naming**: how Docker names containers, why fixed names matter for scripts and DNS, and the pitfalls of `container_name`.
