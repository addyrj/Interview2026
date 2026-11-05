# 189. environment Variables
# हिंदी में: `environment` Variables

---

## 🔵 Simple Definition (English)
`environment:` sets environment variables inside a service's container at runtime. You can write them as a map (`KEY: value`) or a list (`- KEY=value`). Compose also substitutes `${VAR}` placeholders in the YAML itself from your shell or a `.env` file.

## 🔵 सरल परिभाषा (Hindi)
`environment:` service के container के अंदर runtime पर environment variables set करता है। इन्हें map (`KEY: value`) या list (`- KEY=value`) में लिख सकते हैं। Compose YAML के अंदर `${VAR}` placeholders को आपके shell या `.env` file से भी भर देता है।

---

## 🔴 Problem it Solves
Hard-coding DB URLs, API keys and modes in code or images means rebuilding for each environment and leaking secrets in Git. The 12-factor approach: same image everywhere, configuration via env vars. `environment:` lets each environment (dev, staging, prod) supply different values without touching the image.

## 🔴 यह क्यों बना? (Hindi)
DB URL, API keys और modes को code या image में hard-code करने पर हर environment के लिए rebuild करना पड़ता है और secrets Git में leak होते हैं। 12-factor तरीका: हर जगह एक ही image, configuration env vars से। `environment:` हर environment (dev, staging, prod) को image छुए बिना अलग values देने देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Compose loads variables from shell and the project's `.env` file.
Step 2 → It interpolates ${VAR}, ${VAR:-default}, ${VAR:?error} in the YAML.
Step 3 → It merges: env_file values, then `environment:` entries (environment wins).
Step 4 → Final variables are passed to `docker create` as -e flags.
Step 5 → The app reads them: process.env.X (Node) / os.environ["X"] (Python).
Step 6 → `docker compose config` shows the fully resolved result for debugging.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Compose shell और project की `.env` file से variables लोड करता है।
Step 2 → YAML में ${VAR}, ${VAR:-default}, ${VAR:?error} को replace करता है।
Step 3 → Merge: पहले env_file की values, फिर `environment:` की (environment जीतता है)।
Step 4 → अंतिम variables `docker create` को -e flags के रूप में जाते हैं।
Step 5 → App उन्हें पढ़ता है: process.env.X (Node) / os.environ["X"] (Python)।
Step 6 → `docker compose config` पूरा resolved नतीजा दिखाता है, debugging के लिए।
```

---

## 🟡 Real World Example
A Node.js API ran fine locally, but on the VPS it connected to `localhost` for Redis. Root cause: `REDIS_URL` was only in a local `.env` that was never copied to the server. After switching to `REDIS_URL: redis://cache:6379` in `environment:` (a non-secret) and `${DB_PASSWORD:?DB_PASSWORD missing}` for secrets, a missing secret now stops the deployment immediately with a clear message instead of failing at runtime.

## 🟡 Real Example Hindi mein
Node.js API local में ठीक चली, पर VPS पर Redis के लिए `localhost` से connect करने लगी। कारण: `REDIS_URL` सिर्फ local `.env` में था जो server पर कभी copy नहीं हुई। बाद में non-secret के लिए `environment:` में `REDIS_URL: redis://cache:6379` और secrets के लिए `${DB_PASSWORD:?DB_PASSWORD missing}` लगाया; अब secret गायब हो तो deployment तुरंत साफ message के साथ रुकता है, runtime पर fail नहीं होता।

---

## 💻 Code / Config Example — Basic

```yaml
services:                          # containers
  api:                             # Node.js API
    image: node:20-alpine          # example tag
    command: node -e "console.log(process.env.GREETING, process.env.PORT)"  # prints values
    environment:                   # map style (recommended)
      GREETING: "hello"            # plain string
      PORT: "3000"                 # quote numbers to keep them strings
  worker:                          # second service
    image: node:20-alpine          # example tag
    command: node -e "console.log(process.env.MODE)"   # prints value
    environment:                   # list style
      - MODE=worker                # KEY=value
      - HOME_DIR                   # no value: takes it from the host shell if set
```

## 💻 Code / Config Example — Advanced

```yaml
services:                                      # containers
  api:                                         # FastAPI
    image: ghcr.io/addyrj/fastapi-app:${TAG:-dev}   # default tag "dev" when TAG unset
    environment:                               # runtime variables
      APP_ENV: ${APP_ENV:-production}          # default value if unset or empty
      LOG_LEVEL: ${LOG_LEVEL-info}             # default only if UNSET (no colon form)
      DATABASE_URL: postgresql://app:${DB_PASSWORD:?DB_PASSWORD is required}@db:5432/shop   # abort if missing
      REDIS_URL: redis://cache:6379/0          # service-name DNS, not localhost
      JWT_SECRET: ${JWT_SECRET:?JWT_SECRET is required}   # abort if missing
      CORS_ORIGINS: "https://app.example.com,https://admin.example.com"   # example list as CSV
      FEATURE_FLAGS: ${FEATURES:+beta}         # "beta" only if FEATURES is set and non-empty
      DOLLAR_LITERAL: "price is $$5"           # $$ gives a literal $
    depends_on:                                # start order
      - db                                     # db first
      - cache                                  # cache first
  db:                                          # PostgreSQL
    image: postgres:16-alpine                  # example tag
    environment:                               # settings
      POSTGRES_USER: app                       # user
      POSTGRES_DB: shop                        # database
      POSTGRES_PASSWORD: ${DB_PASSWORD:?DB_PASSWORD is required}   # abort if missing
  cache:                                       # Redis
    image: redis:7-alpine                      # example tag
```

Companion `.env` file (same folder, auto-loaded for interpolation, never commit it):

```bash
# .env - used by Compose for ${...} substitution
APP_ENV=production
DB_PASSWORD=change-me-long-random
JWT_SECRET=change-me-another-long-random
TAG=1.4.2
```

---

## 🟠 My Stack Integration
Node.js: read `process.env.DATABASE_URL`. FastAPI: use `pydantic-settings` (`BaseSettings`). React: env vars are baked in at BUILD time (`VITE_*` / `REACT_APP_*`), so they are build args, not runtime `environment:`. On the VPS keep `.env` with `chmod 600`, owned by the deploy user; in GitHub Actions write it from Secrets during deploy.

```yaml
services:                                      # VPS stack
  api:                                         # FastAPI
    image: ghcr.io/addyrj/fastapi-app:${TAG:?set TAG}   # pinned tag
    environment:                               # runtime config
      DATABASE_URL: postgresql://app:${DB_PASSWORD:?set}@db:5432/shop   # db password from .env
      ALLOWED_HOSTS: "api.example.com"         # FastAPI trusted host
  web:                                         # React build
    build:                                     # React config is build time
      context: ./web                           # folder
      args:                                    # build args
        VITE_API_URL: ${PUBLIC_API_URL:-https://api.example.com}   # baked into JS (public, no secrets!)
```

Security: variables are visible with `docker inspect` and in `/proc/<pid>/environ`; anyone with Docker access can read them. For high-value secrets use `secrets:` (file mount) and `*_FILE` variables. Never put secrets in `VITE_*` variables: they ship to every browser.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Committing `.env` with real passwords.
✅ Correct: `.gitignore` it; commit `.env.example` with fake values.

❌ Mistake 2: Using `localhost` inside `DATABASE_URL`.
✅ Correct: Use the service name `db`.

❌ Mistake 3: Unquoted values like `yes`, `on`, `1234567e2` converted by YAML.
✅ Correct: Quote them: `FLAG: "yes"`.

❌ Mistake 4: Special characters in password break the URL (`@`, `/`, `#`).
✅ Correct: URL-encode the password or use separate host/user/password variables.

❌ Mistake 5: Changing `.env` and expecting running containers to update.
✅ Correct: `docker compose up -d` recreates the changed services.

---

## 🧠 Tricky Interview Question
"The shell has `DB_HOST=prod.example.com`, `.env` has `DB_HOST=db`, and `environment:` has `DB_HOST: ${DB_HOST}`. Which value does the container get?"

Answer: `prod.example.com`. For interpolation, shell environment variables take precedence over the `.env` file. That is a classic accident where a developer's exported variable overrides project config. Check with `docker compose config`. Run `unset DB_HOST` or use `--env-file`.

---

## ⚫ Interview Questions + Answers

Q1: Difference between `.env` and `env_file`?
A1: `.env` feeds `${VAR}` substitution inside the compose YAML; `env_file:` injects variables directly into the container. The `.env` values are not passed to containers automatically.

Q2: Precedence of container variables?
A2: Compose `run -e` flag > `environment:` > `env_file:` > image `ENV`.

Q3: `${VAR:-x}` vs `${VAR-x}`?
A3: `:-` uses default if unset OR empty; `-` only if unset.

Q4: How to make a missing var an error?
A4: `${VAR:?message}`.

Q5: Are env vars safe for secrets?
A5: Moderately: visible via `docker inspect`. Prefer Docker secrets or a secret manager (AWS Secrets Manager/SSM) for sensitive data.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Non-secret config (URLs, modes, flags) that differ per environment.
- Quick injection of secrets in small VPS setups with a protected `.env`.

❌ Avoid when:
- Highly sensitive secrets in shared hosts (use secrets).
- Frontend (browser) runtime configuration: build-time or served config file instead.

---

## 📊 Visual Diagram
```
 shell env  ----+
                +--> ${VAR} interpolation --> compose.yaml (resolved)
 .env file  ----+                                  |
                                                   v
 env_file: ----------------> merge <---- environment: (wins)
                                |
                                v
                      container ENV (docker inspect shows it)
                                |
                                v
                  process.env.X  /  os.environ["X"]
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| environment | Runtime env vars for container | container के runtime variables |
| interpolation | Replace ${VAR} in YAML | YAML में ${VAR} बदलना |
| .env | Default variable file for Compose | Compose की default variable file |
| ${VAR:?} | Required variable check | ज़रूरी variable जाँच |
| 12-factor | Config via environment | environment से configuration |

---

## ⚡ 3-Line Summary
English: `environment:` passes runtime configuration into containers.
English: `${VAR}` interpolation comes from shell and `.env`; use `:?` for required values.
English: Env vars are readable by anyone with Docker access, so guard real secrets.
Hindi: `environment:` containers को runtime configuration देता है।
Hindi: `${VAR}` interpolation shell और `.env` से आता है; ज़रूरी values के लिए `:?` use करें।
Hindi: Docker access वाला कोई भी env vars पढ़ सकता है, इसलिए असली secrets संभालकर रखें।

---

## ➡️ Next Topic
190. env_file - when you have dozens of variables, load them from a file instead of listing each one.
