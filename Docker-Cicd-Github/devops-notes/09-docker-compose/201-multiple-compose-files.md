# 201. Multiple Compose Files
# हिंदी में: कई Compose Files

---

## 🔵 Simple Definition (English)
Docker Compose can merge **several compose files** into one configuration: `docker compose -f base.yml -f prod.yml up`. Files are applied left to right; later files override or extend earlier ones. Also `include:` (newer) and `extends:` let you split one big file into reusable pieces.

## 🔵 सरल परिभाषा (Hindi)
Docker Compose **कई compose files** को एक configuration में merge कर सकता है: `docker compose -f base.yml -f prod.yml up`। Files बाएँ से दाएँ apply होती हैं; बाद वाली file पहले वाली को override या extend करती है। नए versions में `include:` और `extends:` से बड़ी file को reusable टुकड़ों में बाँटा जा सकता है।

---

## 🔴 Problem it Solves
One file for dev, staging and prod leads to `if` logic you cannot write in YAML, copy-pasted files that drift, and a prod stack that accidentally publishes debug ports. Multiple files let you keep a shared **base** and put only the differences in small environment files.

## 🔴 यह क्यों बना? (Hindi)
Dev, staging और prod के लिए एक ही file में `if` logic लिखना YAML में संभव नहीं, copy-paste की हुई files अलग-अलग हो जाती हैं, और prod में गलती से debug ports publish हो सकते हैं। Multiple files से shared **base** रखकर सिर्फ अंतर छोटी environment files में रखा जाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Write docker-compose.yml with the common parts (services, images)
Step 2 → Write docker-compose.prod.yml with ONLY what differs (replicas, restart, env)
Step 3 → Run: docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
Step 4 → Compose merges: mappings are merged key by key, later wins
Step 5 → Lists: some are appended (ports, volumes, expose), others replaced (command, entrypoint)
Step 6 → Inspect the result with `docker compose -f a.yml -f b.yml config`
Step 7 → Paths in later files are relative to the FIRST file's directory (important!)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → docker-compose.yml में common हिस्सा लिखें (services, images)
Step 2 → docker-compose.prod.yml में सिर्फ अंतर लिखें (replicas, restart, env)
Step 3 → चलाएँ: docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
Step 4 → Compose merge करता है: mappings key-by-key merge, बाद वाली जीतती है
Step 5 → Lists: कुछ जुड़ती हैं (ports, volumes, expose), कुछ replace होती हैं (command, entrypoint)
Step 6 → नतीजा देखें `docker compose -f a.yml -f b.yml config` से
Step 7 → बाद वाली files के relative paths PEHLI file की directory से गिने जाते हैं (ज़रूरी!)
```

---

## 🟡 Real World Example
A **Swiggy**-style team keeps `compose.yml` (api, db, redis), `compose.dev.yml` (bind mounts, debug ports, pgAdmin) and `compose.prod.yml` (restart policies, resource limits, no published DB port, image tags from the registry). The VPS runs `-f compose.yml -f compose.prod.yml`; developers run the dev pair. A third file `compose.monitoring.yml` adds Prometheus and Grafana only on the staging server.

## 🟡 Real Example Hindi mein
**Swiggy** जैसी team `compose.yml` (api, db, redis), `compose.dev.yml` (bind mounts, debug ports, pgAdmin) और `compose.prod.yml` (restart policy, resource limits, DB port publish नहीं, registry से image tags) रखती है। VPS पर `-f compose.yml -f compose.prod.yml` चलता है; developers dev वाली जोड़ी चलाते हैं। तीसरी file `compose.monitoring.yml` सिर्फ staging server पर Prometheus और Grafana जोड़ती है।

---

## 💻 Code / Config Example — Basic

```yaml
# docker-compose.yml  (BASE: shared by all environments)
services:
  api:
    image: myorg/api:1.0.0            # example image; replace with your registry path
    environment:
      NODE_ENV: development           # base default, overridden in prod file
    ports:
      - "3000:3000"                   # base publishes 3000
  redis:
    image: redis:7-alpine             # same in all environments
```

```yaml
# docker-compose.prod.yml  (ONLY the differences)
services:
  api:
    environment:
      NODE_ENV: production            # overrides base value
    restart: unless-stopped           # new key, only in prod
    ports: !override                  # !override REPLACES the list (needs a recent Compose V2; see note)
      - "127.0.0.1:3000:3000"         # prod: bind to loopback, nginx proxies to it
```

```bash
# run base + prod
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
# preview merged result before running
docker compose -f docker-compose.yml -f docker-compose.prod.yml config
```
Without `!override`, the `ports` lists would be APPENDED (both 3000 mappings), which then conflicts. `!override`/`!reset` tags need a recent Compose V2 release; on older versions keep ports out of the base file. YAML was parsed with a custom-tag-tolerant loader; actual merge behaviour was not run locally.

## 💻 Code / Config Example — Advanced

```yaml
# compose.yml : base with reusable fragment
x-api-common: &api-common            # YAML anchor: reuse a block inside this file
  restart: unless-stopped
  logging:
    driver: json-file                # default driver, set explicitly
    options:
      max-size: "10m"                # rotate logs so disk does not fill up
      max-file: "3"
services:
  api:
    <<: *api-common                  # merge the shared block
    build: ./api                     # Node.js service
    environment:
      DB_HOST: db
  db:
    image: postgres:16-alpine
    volumes:
      - pgdata:/var/lib/postgresql/data   # named volume keeps data
volumes:
  pgdata: {}
```

```yaml
# compose.monitoring.yml : optional add-on file
services:
  prometheus:
    image: prom/prometheus:v2.54.1   # example tag
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro   # config path relative to FIRST file's dir
    ports:
      - "127.0.0.1:9090:9090"        # not public
```

```yaml
# compose.all.yml : composition with include (Compose >= 2.20)
include:
  - path: ./compose.yml              # pull in another file as a self-contained unit
  - path: ./compose.monitoring.yml   # each included file keeps its own relative paths
```

```bash
# environment selection via env var instead of repeating -f
export COMPOSE_FILE=compose.yml:compose.prod.yml   # colon-separated on Linux/macOS (';' on Windows)
docker compose up -d                                # uses both files
docker compose config --services                    # verify which services are active
```

```yaml
# Another merge tool: extends (reuse one service definition from another file)
services:
  worker:
    extends:
      file: ./compose.yml            # file with the base service
      service: api                   # service to inherit
    command: ["node", "worker.js"]   # different command, same image/env
```

---

## 🟠 My Stack Integration
- **Node.js/FastAPI**: base file has build context and env; prod file swaps `build:` for `image: ghcr.io/you/api:${TAG}` pushed by GitHub Actions.
- **Nginx**: base defines nginx; prod adds `443:443` and the cert volume; dev keeps only `80:80`.
- **VPS/AWS**: `COMPOSE_FILE` in the server's `.env` so every `docker compose up -d` automatically uses the prod pair.
- **React**: dev file runs Vite; prod file serves the static build through nginx.

```yaml
# docker-compose.prod.yml : swap build for a registry image
services:
  api:
    build: !reset null                       # remove inherited build (recent Compose; else delete from base)
    image: ghcr.io/youruser/api:${TAG:-latest}   # TAG injected by the CI deploy step (example registry)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Expecting later `ports` or `volumes` to replace earlier ones.
✅ Correct: They are appended; use `!override` or keep them only in one file.

❌ Mistake 2: Wrong file order (`-f prod.yml -f base.yml`), so base overrides prod.
✅ Correct: Base first, specific last.

❌ Mistake 3: Relative paths in later files resolving to the wrong folder.
✅ Correct: Keep all files in one directory, or use `include:` which resolves paths per file. Verify via `config`.

❌ Mistake 4: Never inspecting the merged result.
✅ Correct: Run `docker compose ... config` in CI to catch mistakes.

❌ Mistake 5: Duplicating the whole file into prod "to be safe".
✅ Correct: Put only differences in override files.

---

## 🧠 Tricky Interview Question
Base has `command: ["npm","start"]` and prod has `command: ["node","dist/main.js"]`. What does the merged service run? And if both define `ports`?

Answer: `command` (like `entrypoint`) is replaced, so prod runs `node dist/main.js`. Sequences such as `ports`, `volumes`, `expose`, `dns` are merged by appending (ports are de-duplicated by target), and `environment`/`labels` merge as maps with later values winning. Hence duplicated published ports from both files can cause a bind conflict.

---

## ⚫ Interview Questions + Answers

Q1: How do you combine files?
A1: Repeat `-f`, or set `COMPOSE_FILE` with a path separator.

Q2: Which wins on conflict?
A2: The last file.

Q3: `include` vs `-f`?
A3: `-f` merges everything into one model (overrides). `include` loads other files as separate sub-projects with their own relative paths and conflicts raise errors.

Q4: `extends` vs anchors?
A4: Anchors work inside a single YAML file; `extends` reuses a service from another file.

Q5: How to verify?
A5: `docker compose config`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- dev/staging/prod differ in a few settings.
- Optional stacks (monitoring, tests) add onto a base.

❌ Avoid when:
- Differences are huge (maybe separate projects).
- You can solve it with env vars/profiles, which is simpler.

---

## 📊 Visual Diagram
```
 compose.yml (base)  --+
                       |-- merge (left -> right) --> final config --> docker engine
 compose.prod.yml  ----+
 compose.monitoring.yml +

 mapping keys : merged, later wins
 lists (ports): appended
 command      : replaced
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| -f | Select compose file(s) | compose file चुनना |
| COMPOSE_FILE | Env var listing files | files की सूची वाला env var |
| include | Load another compose file as a module | दूसरी file को module की तरह लोड |
| extends | Inherit a service definition | service definition विरासत में लेना |
| !override / !reset | YAML tags to replace/remove merged values | merge हुई value बदलने/हटाने के tags |

---

## ⚡ 3-Line Summary
English: Use several compose files; later ones override earlier ones.
Keep shared config in a base and only differences in env files.
Always check the merged result with `docker compose config`.
Hindi: कई compose files इस्तेमाल करें; बाद वाली पहले वाली को override करती है।
Shared config base में और सिर्फ अंतर environment files में रखें।
Merge का नतीजा हमेशा `docker compose config` से जाँचें।

---

## ➡️ Next Topic
**202. Override Files (docker-compose.override.yml)**: the special file name Compose loads automatically, ideal for dev settings.
