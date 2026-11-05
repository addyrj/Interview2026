# 202. Override Files (docker-compose.override.yml)
# हिंदी में: Override Files (docker-compose.override.yml)

---

## 🔵 Simple Definition (English)
`docker-compose.override.yml` is a file that Compose reads automatically after `docker-compose.yml` and merges on top of it. You keep shared settings in the base file and put local or environment-specific changes in the override.

## 🔵 सरल परिभाषा (Hindi)
`docker-compose.override.yml` ऐसी file है जिसे Compose `docker-compose.yml` के बाद अपने-आप पढ़ता है और उसके ऊपर merge कर देता है। Shared settings base file में रहती हैं और local या environment-specific बदलाव override में।

---

## 🔴 Problem it Solves
Developers want bind mounts, debug ports and hot reload locally, while production wants pinned images, no source mounts and restart policies. Copying the whole file for each case leads to drift: someone fixes the DB setting in one file and forgets the other.

## 🔴 यह क्यों बना? (Hindi)
Developers को local पर bind mounts, debug ports और hot reload चाहिए, जबकि production को pinned images, बिना source mount और restart policies चाहिए। हर case के लिए पूरी file copy करने से drift होता है: कोई DB setting एक file में ठीक करता है और दूसरी भूल जाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You run `docker compose up` with no -f flags
Step 2 → Compose auto-loads docker-compose.yml (base)
Step 3 → Compose auto-loads docker-compose.override.yml if it exists
Step 4 → Maps are merged key by key; override values win
Step 5 → Single-value keys (image, command) are replaced
Step 6 → Lists like ports, volumes, environment are appended/merged
Step 7 → `docker compose config` prints the final merged result so you can check it
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → आप बिना -f flag के `docker compose up` चलाते हैं
Step 2 → Compose base docker-compose.yml load करता है
Step 3 → docker-compose.override.yml हो तो उसे भी अपने-आप load करता है
Step 4 → Maps key-by-key merge होते हैं; override की values जीतती हैं
Step 5 → Single-value keys (image, command) replace होती हैं
Step 6 → ports, volumes, environment जैसी lists append/merge होती हैं
Step 7 → `docker compose config` final merged result दिखाता है ताकि आप जाँच सकें
```

---

## 🟡 Real World Example
A startup's repo has `docker-compose.yml` (api, postgres, redis) and a git-committed `docker-compose.override.yml` for developers (bind mounts, nodemon, exposed DB port 5432). On the EC2 server, the deploy script runs `docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d`; because `-f` is given explicitly, the dev override is NOT loaded, so no source mounts or DB ports leak to production.

## 🟡 Real Example Hindi mein
एक startup के repo में `docker-compose.yml` (api, postgres, redis) और developers के लिए git में committed `docker-compose.override.yml` (bind mounts, nodemon, DB port 5432 खुला) है। EC2 server पर deploy script `docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d` चलाती है; `-f` देने से dev override load नहीं होता, इसलिए production में source mounts या DB ports leak नहीं होते।

---

## 💻 Code / Config Example — Basic
```yaml
# docker-compose.yml  (BASE: shared by every environment)
services:
  api:
    build: ./api                  # build Node.js image from ./api
    environment:
      NODE_ENV: production        # safe default
    ports:
      - "3000:3000"               # app port
```
```yaml
# docker-compose.override.yml  (auto-merged on top, local development)
services:
  api:
    environment:
      NODE_ENV: development       # replaces the base value
    volumes:
      - ./api:/app                # added: live source code
    command: ["npx", "nodemon", "server.js"]  # replaced: restart on file change
```

## 💻 Code / Config Example — Advanced
```yaml
# docker-compose.yml  (BASE)
services:
  api:
    build:
      context: ./api              # build context folder
      target: runtime             # multi-stage target for the lean image
    environment:
      DATABASE_URL: postgres://app:${DB_PASS}@postgres:5432/app  # DB_PASS comes from .env
    depends_on:
      postgres:
        condition: service_healthy   # wait for DB
  postgres:
    image: postgres:16-alpine     # example tag
    environment:
      POSTGRES_USER: app          # DB user
      POSTGRES_PASSWORD: ${DB_PASS}  # from .env, never hard code
      POSTGRES_DB: app            # DB name
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app"]  # ready check
      interval: 5s                # every 5 seconds
      timeout: 3s                 # fail if slow
      retries: 10                 # up to 10 tries
    volumes:
      - pgdata:/var/lib/postgresql/data  # persistent data
volumes:
  pgdata: {}                      # declare volume
```
```yaml
# docker-compose.override.yml  (DEV extras; auto-loaded)
services:
  api:
    build:
      target: dev                 # use the dev stage with dev dependencies
    volumes:
      - ./api/src:/app/src        # hot reload source
      - api_node_modules:/app/node_modules  # keep Linux modules
    ports:
      - "9229:9229"               # Node inspector for debugging
    command: ["node", "--inspect=0.0.0.0:9229", "--watch", "src/index.js"]  # debug + auto-restart (Node 18.11+ --watch)
  postgres:
    ports:
      - "127.0.0.1:5432:5432"     # DB reachable from host tools, only on localhost
volumes:
  api_node_modules: {}            # dev-only volume
```
Verify merge: `docker compose config`. Skip override: `docker compose -f docker-compose.yml up -d`.

---

## 🟠 My Stack Integration
- **Node.js:** override adds nodemon/`--watch`, debugger port, source mount.
- **FastAPI:** override sets `command: uvicorn main:app --reload` and mounts `./app`.
- **React:** override can run the Vite/CRA dev server instead of the Nginx static image.
- **Nginx/VPS:** on the server use explicit `-f` files so the dev override can never be applied by accident. Some teams name it `docker-compose.dev.yml` to avoid auto-loading.
- **Security:** dev override often publishes DB ports and debug ports; never let it run on a public VPS.

```yaml
# docker-compose.override.yml  (my FastAPI dev setup)
services:
  ml:
    volumes:
      - ./fastapi/app:/code/app       # live code
    command: ["uvicorn","app.main:app","--host","0.0.0.0","--reload"]  # auto-reload on edits
    environment:
      LOG_LEVEL: debug                # verbose logs in dev
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Deploying with plain `docker compose up -d` on the server while the dev override file is present. Source mounts and open DB ports go live.
✅ Correct: Use explicit `-f docker-compose.yml -f docker-compose.prod.yml` in deploy scripts.

❌ Mistake 2: Expecting list items to be replaced. `ports` and `volumes` are merged, so both base and override entries exist.
✅ Correct: Use `!reset` or `!override` tags (Compose 2.24+; version-dependent) or move the item out of the base file.

❌ Mistake 3: Putting secrets in the committed override file.
✅ Correct: Use `.env` (git-ignored) or Docker secrets.

❌ Mistake 4: Not checking the result.
✅ Correct: Always run `docker compose config` before deploying.

---

## 🧠 Tricky Interview Question
The base file publishes `"80:80"` for nginx; the override adds `"8080:80"`. What ports are open after `docker compose up`?

Answer: Both. Port mappings are lists that get merged, so the container is reachable on 80 and 8080. To replace instead of add, use the `!override` YAML tag (Compose v2.24+) or avoid declaring ports in the base.

---

## ⚫ Interview Questions + Answers

Q1: Which files are auto-loaded?
A1: `compose.yaml` / `docker-compose.yml` and then `compose.override.yaml` / `docker-compose.override.yml` from the working directory.

Q2: Does `-f` disable the automatic override?
A2: Yes. When you pass `-f`, only the files you list are used, in order, later ones winning.

Q3: How are scalars vs lists merged?
A3: Scalars (image, command) from the later file replace earlier ones; mappings merge by key; sequences like ports/volumes are appended (volumes with the same target are replaced).

Q4: How to see the merged file?
A4: `docker compose config` (add `--format json` if needed).

Q5: Should the override be in git?
A5: Often yes for shared dev defaults; machine-specific tweaks go into a git-ignored file and `COMPOSE_FILE` env var.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Dev needs extras (mounts, debug ports) on top of a clean base.
- You want one base shared by dev, test, and prod.

❌ Avoid when:
- The auto-load surprise could hit production; use explicit named files instead.
- Layers are so many that nobody can read the result.

---

## 📊 Visual Diagram
```
 docker-compose.yml  ----\
   (base, shared)         \
                           +--> merge --> final config --> containers
 docker-compose.override.yml /   (override wins)
   (dev extras, auto)

 Server:  -f base.yml -f prod.yml   (override file ignored)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| base file | Main shared Compose file | मुख्य साझा file |
| override | File merged on top | ऊपर से merge होने वाली file |
| merge | Combine two configs | दो configs मिलाना |
| `-f` | Choose explicit compose files | file खुद चुनना |
| `compose config` | Show final merged config | अंतिम config दिखाना |
| `!override` | Tag to replace a list | list को replace करने वाला tag |

---

## ⚡ 3-Line Summary
English: The override file is auto-merged on top of the base file. Keep shared config in base, dev extras in override, and use explicit `-f` on servers. Always check with `docker compose config`.
Hindi: Override file base file के ऊपर अपने-आप merge होती है। Shared config base में, dev extras override में रखें और servers पर explicit `-f` इस्तेमाल करें। हमेशा `docker compose config` से जाँचें।

---

## ➡️ Next Topic
**203. Environment Specific Configs**: override handles one dev layer; next we organize dev, test, staging and prod configs cleanly.
