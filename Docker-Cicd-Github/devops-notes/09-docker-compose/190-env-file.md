# 190. env_file
# हिंदी में: `env_file`

---

## 🔵 Simple Definition (English)
`env_file:` loads environment variables for a container from one or more files (`KEY=value` per line). It keeps long variable lists out of `compose.yaml` and lets you keep secrets in a file that is not in Git.

## 🔵 सरल परिभाषा (Hindi)
`env_file:` एक या ज़्यादा files (हर line में `KEY=value`) से container के environment variables लोड करता है। इससे लंबी variable lists `compose.yaml` से बाहर रहती हैं और secrets ऐसी file में रखे जा सकते हैं जो Git में नहीं है।

---

## 🔴 Problem it Solves
A real backend has 30+ variables (DB, Redis, JWT, SMTP, S3, Stripe). Listing all under `environment:` makes the compose file noisy, and putting the real values there means committing secrets. Different environments need different sets. `env_file` separates config from the YAML structure: `api.env`, `db.env`, `prod.env`.

## 🔴 यह क्यों बना? (Hindi)
असली backend में 30+ variables होते हैं (DB, Redis, JWT, SMTP, S3, Stripe)। सब `environment:` में लिखने से compose file भर जाती है, और असली values वहाँ रखने का मतलब secrets commit करना। अलग environments को अलग sets चाहिए। `env_file` configuration को YAML structure से अलग करता है: `api.env`, `db.env`, `prod.env`।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create a file such as api.env with KEY=value lines (no export, no quotes needed).
Step 2 → Reference it: env_file: [./api.env] (path is relative to the compose file).
Step 3 → Compose reads files in order; later files override earlier ones.
Step 4 → Values from `environment:` override values from env_file.
Step 5 → Final variables are injected into the container, not into compose interpolation.
Step 6 → Missing file => error, unless you use `required: false`.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → api.env जैसी file बनाएँ जिसमें KEY=value lines हों (export या ज़रूरी quotes नहीं)।
Step 2 → उसे लिखें: env_file: [./api.env] (path compose file के सापेक्ष)।
Step 3 → Compose files क्रम से पढ़ता है; बाद वाली file पहले वाली को override करती है।
Step 4 → `environment:` की values env_file की values को override करती हैं।
Step 5 → अंतिम variables container में inject होते हैं, compose interpolation में नहीं।
Step 6 → File न मिले तो error, जब तक `required: false` न हो।
```

---

## 🟡 Real World Example
A team has `common.env` (LOG_LEVEL, TZ), `api.env` (DB and JWT) and `local.env` (developer overrides, ignored by Git). The api service lists all three: common first, then api, then optional local. Developers just copy `api.env.example` to `api.env`. On the VPS the deploy pipeline writes `api.env` from GitHub Secrets and sets `chmod 600`.

## 🟡 Real Example Hindi mein
एक टीम के पास `common.env` (LOG_LEVEL, TZ), `api.env` (DB और JWT) और `local.env` (developer overrides, Git में ignored) हैं। api service तीनों लिखती है: पहले common, फिर api, फिर optional local। Developers बस `api.env.example` को `api.env` में copy कर लेते हैं। VPS पर deploy pipeline GitHub Secrets से `api.env` बनाती है और `chmod 600` लगाती है।

---

## 💻 Code / Config Example — Basic

```yaml
services:                       # containers
  api:                          # Node.js API
    image: node:20-alpine       # example tag
    command: node -e "console.log(process.env.DB_HOST, process.env.PORT)"   # prints loaded vars
    env_file: .env.api          # single file, string form (path relative to compose file)
```

Matching `.env.api` file:

```bash
# .env.api - one KEY=value per line, # starts a comment
DB_HOST=db
PORT=3000
```

## 💻 Code / Config Example — Advanced

```yaml
services:                                 # containers
  api:                                    # FastAPI
    image: ghcr.io/addyrj/fastapi-app:1.4.2   # example image
    env_file:                             # list: later entries override earlier ones
      - ./env/common.env                  # shared values (TZ, LOG_LEVEL)
      - path: ./env/api.env               # long syntax entry
        required: true                    # fail if missing (this is the default)
      - path: ./env/local.env             # developer-only overrides
        required: false                   # ignore if missing (Compose 2.24+; check your version)
    environment:                          # these WIN over env_file values
      APP_ENV: production                 # forced to production
  worker:                                 # background worker
    image: ghcr.io/addyrj/fastapi-app:1.4.2   # same image
    command: ["python", "-m", "app.worker"]   # worker entrypoint
    env_file:                             # shares the same files
      - ./env/common.env                  # shared values
      - ./env/api.env                     # same secrets
  db:                                     # PostgreSQL
    image: postgres:16-alpine             # example tag
    env_file:                             # separate file so api never sees db superuser vars
      - ./env/db.env                      # POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB
```

Example `env/api.env`:

```bash
# env/api.env - NOT committed to Git
DATABASE_URL=postgresql://app:strong-password@db:5432/shop
JWT_SECRET=very-long-random-string
SMTP_HOST=email-smtp.ap-south-1.amazonaws.com
```

---

## 🟠 My Stack Integration
Use one `.env` for Compose interpolation (TAG, ports) and per-service files for runtime (`api.env`, `db.env`). In GitHub Actions deploy, create the file on the VPS over SSH and then run compose.

```yaml
services:                                 # VPS stack
  api:                                    # Node.js API
    image: ghcr.io/addyrj/node-api:${TAG:?set TAG}   # TAG from .env or shell
    env_file: [./env/api.env]             # runtime secrets
    restart: unless-stopped               # restart policy
  nginx:                                  # proxy
    image: nginx:1.27-alpine              # example tag
    ports: ["80:80", "443:443"]           # public
```

```bash
# deploy step run on the VPS via ssh (example, bash -n checked)
set -euo pipefail                         # stop on first error
umask 077                                 # new files readable only by owner
printf '%s\n' "$API_ENV_CONTENT" > env/api.env   # secret content passed from GitHub Secrets
docker compose pull                       # fetch new images
docker compose up -d                      # recreate changed services
```

Security: restrict file permission (`chmod 600`), add `*.env` to `.gitignore` and `.dockerignore` (so it never gets COPY'd into an image), and rotate secrets when a teammate leaves.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Confusing `.env` and `env_file`; expecting `.env` values inside containers.
✅ Correct: `.env` is for compose interpolation. Use `env_file:` or `environment:` to pass into containers.

❌ Mistake 2: Quoting values: `KEY="value"` and getting literal quotes in older parsers.
✅ Correct: Modern Compose strips matching quotes, but safest is `KEY=value` without quotes unless spaces.

❌ Mistake 3: `export KEY=value` lines in the file.
✅ Correct: Plain `KEY=value`.

❌ Mistake 4: Forgetting that `environment:` overrides `env_file:`.
✅ Correct: Keep each variable in one place.

❌ Mistake 5: Committing the real file or baking it into the image.
✅ Correct: `.gitignore` + `.dockerignore`, ship only `.example`.

---

## 🧠 Tricky Interview Question
"You edit `api.env` and run `docker compose restart api`. The app still uses old values. Why?"

Answer: `restart` only restarts the existing container, whose environment was fixed when it was created. env_file is read at container creation. Use `docker compose up -d` (it detects config changes and recreates) or `docker compose up -d --force-recreate api`. Note Compose may not detect changes in the file's content in all versions, so use `--force-recreate` to be safe.

---

## ⚫ Interview Questions + Answers

Q1: What file format does env_file accept?
A1: `KEY=value` lines (dotenv style), `#` comments, blank lines allowed.

Q2: Order of precedence?
A2: Later env_file entries override earlier ones; `environment:` overrides all env_file values.

Q3: Can env_file values be used in `${}` interpolation of compose.yaml?
A3: No; for that use `.env` or `--env-file` on the CLI.

Q4: How to make a file optional?
A4: `path: ./x.env` with `required: false` (Compose 2.24+).

Q5: How do I keep secrets out of Git but available on server?
A5: Keep `*.env` ignored, create it during deployment from a secrets store (GitHub Secrets/SSM), restrict permission.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Many variables or per-environment values.
- Separate files per service to limit exposure.

❌ Avoid when:
- Few harmless variables (inline `environment:` is clearer).
- Very sensitive secrets where file-based `secrets:` or a manager is available.

---

## 📊 Visual Diagram
```
 env/common.env --+
 env/api.env -----+--> merged in order (later wins) --+
 env/local.env ---+   (optional)                     |
                                                      v
 environment: { APP_ENV: production } --(overrides)--> container ENV
                                                      |
 .env (separate) --> only ${VAR} substitution in compose.yaml
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| env_file | File of variables loaded into container | container में लोड होने वाली variables file |
| dotenv | KEY=value file format | KEY=value format |
| override | Later value replaces earlier | बाद की value पहले को बदलती है |
| required | Fail when file missing | file न हो तो fail |
| .dockerignore | Excludes files from build context | build context से files बाहर रखता है |

---

## ⚡ 3-Line Summary
English: `env_file:` loads many variables from files into a container.
English: `environment:` overrides it; `.env` is a different thing used only for interpolation.
English: Ignore real files in Git/Docker builds and lock permissions.
Hindi: `env_file:` files से कई variables को container में लोड करता है।
Hindi: `environment:` इसे override करता है; `.env` अलग चीज़ है जो सिर्फ interpolation के लिए है।
Hindi: असली files को Git/Docker build से बाहर रखें और permission सख्त रखें।

---

## ➡️ Next Topic
191. depends_on - after config is loaded, control the start order between services.
