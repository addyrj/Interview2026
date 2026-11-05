# 183. version Field
# हिंदी में: Compose File का `version` Field

---

## 🔵 Simple Definition (English)
`version` was the first line of old `docker-compose.yml` files (`version: "3.8"`). It told the old Compose tool which file-format schema to use. In modern Docker Compose (v2, the Compose Specification) this field is **obsolete**: it is ignored and Compose prints a warning if you keep it.

## 🔵 सरल परिभाषा (Hindi)
`version` पुरानी `docker-compose.yml` files की पहली line होती थी (`version: "3.8"`)। यह पुराने Compose tool को बताती थी कि file का format कौन सा schema follow करेगा। आज के Docker Compose (v2, Compose Specification) में यह field **obsolete** है: इसे ignore किया जाता है और रखने पर warning आती है।

---

## 🔴 Problem it Solves
Earlier, Compose file formats were versioned: v1 (no `services:` key), v2.x (for single host) and v3.x (for Swarm). Each version supported different keys, so a file written for 3.8 could fail on an older Docker Engine. You had to match `version` to your Docker Engine version table. This was confusing: the same key (`depends_on` conditions, `mem_limit`, `deploy`) existed in one version but not another.

The Compose Specification merged all of this into ONE schema that always uses the latest rules, so a version number is no longer needed.

## 🔴 यह क्यों बना? (Hindi)
पहले Compose file के formats version में बँटे थे: v1 (बिना `services:` key), v2.x (single host के लिए) और v3.x (Swarm के लिए)। हर version में अलग keys चलती थीं, इसलिए 3.8 के लिए लिखी file पुराने Docker Engine पर fail हो सकती थी। आपको Docker Engine की compatibility table देखकर `version` मिलाना पड़ता था। Compose Specification ने सब कुछ एक ही schema में merge कर दिया जो हमेशा latest rules follow करता है, इसलिए अब version number की ज़रूरत नहीं रही।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You run `docker compose up` (Compose v2 plugin).
Step 2 → Compose reads docker-compose.yml / compose.yaml.
Step 3 → It validates the file against the latest Compose Specification schema.
Step 4 → If a top-level `version:` exists, it is parsed but IGNORED.
Step 5 → Compose prints: "the attribute `version` is obsolete, it will be ignored".
Step 6 → Containers are created exactly the same with or without the field.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → आप `docker compose up` चलाते हैं (Compose v2 plugin)।
Step 2 → Compose docker-compose.yml / compose.yaml पढ़ता है।
Step 3 → वह file को latest Compose Specification schema से validate करता है।
Step 4 → अगर top-level `version:` है, तो वह parse होती है पर IGNORE कर दी जाती है।
Step 5 → Compose warning देता है: "the attribute `version` is obsolete".
Step 6 → Containers version के साथ या बिना, बिल्कुल एक जैसे बनते हैं।
```

---

## 🟡 Real World Example
A team at a startup copied a 2019 blog's `docker-compose.yml` with `version: "2.4"` to get `mem_limit`, and `version: "3.8"` in another repo for `deploy:`. On the VPS with Docker Compose v2 every `docker compose up` printed a warning in CI logs, and the junior dev thought the deploy failed. Removing the line made logs clean. The team also added a `name:` key so the project name stopped depending on the folder name on the VPS (`/home/ubuntu/app` vs `/srv/shop`).

## 🟡 Real Example Hindi mein
एक startup team ने 2019 के blog से `version: "2.4"` वाली file copy की (`mem_limit` के लिए), और दूसरे repo में `version: "3.8"` (`deploy:` के लिए)। VPS पर Compose v2 में हर `docker compose up` पर warning आती थी और junior dev को लगा deploy fail हुआ। line हटाने पर logs साफ हो गए। टीम ने `name:` key भी जोड़ी ताकि project का नाम folder के नाम (`/home/ubuntu/app` बनाम `/srv/shop`) पर निर्भर न रहे।

---

## 💻 Code / Config Example — Basic

```yaml
# OLD style (legacy) - works but prints a warning on Compose v2
version: "3.8"                 # obsolete: ignored by modern Compose
services:                      # all containers are defined under services
  web:                         # service name (also its DNS name)
    image: nginx:1.27-alpine   # example tag, update to latest stable
    ports:                     # publish container port to host
      - "8080:80"              # host 8080 -> container 80
```

## 💻 Code / Config Example — Advanced

```yaml
# MODERN style: no `version`, but with the optional top-level `name`
name: shop-prod                # project name; containers become shop-prod-api-1 etc.
services:                      # list of services
  api:                         # Node.js backend
    build:                     # build the image locally
      context: ./api           # folder containing the Dockerfile
      dockerfile: Dockerfile   # Dockerfile name inside the context
    image: shop/api:1.0.0      # tag given to the built image
    restart: unless-stopped    # survive reboots of the VPS
    environment:               # simple env vars
      NODE_ENV: production     # run Node in production mode
      PORT: "3000"             # app listens here (string avoids YAML int confusion)
    networks:                  # attach to our private network
      - backend                # service-to-service traffic
    healthcheck:               # tell Docker how to test the app
      test: ["CMD", "node", "-e", "fetch('http://localhost:3000/health').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"]  # exits 0 when healthy
      interval: 30s            # run check every 30s
      timeout: 5s              # fail if check takes more than 5s
      retries: 3               # 3 failures => unhealthy
  nginx:                       # reverse proxy in front of the API
    image: nginx:1.27-alpine   # example tag
    ports:                     # only nginx is public
      - "80:80"                # HTTP
    depends_on:                # start after api is healthy
      api:                     # target service
        condition: service_healthy  # wait for healthcheck success
    networks:                  # same network as api
      - backend                # so nginx can reach http://api:3000
networks:                      # top-level networks
  backend: {}                  # default bridge driver, created by Compose
```

---

## 🟠 My Stack Integration
In your Node.js / FastAPI / React / Nginx VPS stack, make the file start with `name:` instead of `version:`. Use the same file on laptop and on the AWS EC2 / VPS machine. Pin the Compose plugin version in your CI (GitHub Actions `ubuntu-latest` already ships Compose v2).

```yaml
# compose.yaml for VPS (no version, explicit name)
name: myapp                    # stable project name on every machine
services:                      # services start here
  fastapi:                     # Python backend
    image: ghcr.io/addyrj/fastapi-app:1.4.2   # example image from GHCR, update tag
    restart: unless-stopped    # auto start after reboot
    expose:                    # visible only inside the compose network
      - "8000"                 # uvicorn port
  react:                       # static React build served by nginx
    image: ghcr.io/addyrj/react-app:1.4.2     # example image
    restart: unless-stopped    # auto start after reboot
  nginx:                       # edge proxy, TLS handled here or by certbot
    image: nginx:1.27-alpine   # example tag
    ports:                     # public ports
      - "80:80"                # HTTP
      - "443:443"              # HTTPS
    depends_on:                # order of start
      - fastapi                # start API first
      - react                  # start frontend first
```

Security: the removed `version` field has no security effect, but old files copied from the internet often also contain `privileged: true` or open DB ports. Review the whole file, not just the first line.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Keeping `version: "3.8"` and believing it selects features.
✅ Correct: Delete it. Features depend on your installed Compose plugin version (`docker compose version`).

❌ Mistake 2: Writing `version: 3.8` (number) and getting a parse error in older tools.
✅ Correct: If you must keep it for legacy `docker-compose` v1, quote it as a string `"3.8"`; otherwise remove it.

❌ Mistake 3: Using `deploy:` limits only because "version 3 needs it" and thinking they are ignored outside Swarm.
✅ Correct: Compose v2 applies `deploy.resources.limits` on a normal `docker compose up` too.

❌ Mistake 4: Running old `docker-compose` (hyphen, Python v1) which needs `version`.
✅ Correct: Use `docker compose` (v2). v1 reached end of life in 2023.

---

## 🧠 Tricky Interview Question
"You remove `version: "3.8"` from your compose file and CI starts failing on the old test server. Why?"

Answer: The old server still runs legacy `docker-compose` v1 (Python). v1 requires the `version` key to decide the schema, so without it, it treats the file as format v1 (no `services:` key) and errors out. The right fix is to upgrade the server to Docker Compose v2 plugin, not to put the line back everywhere. In a mixed environment, you can keep the field temporarily and accept the warning.

---

## ⚫ Interview Questions + Answers

Q1: Is the `version` field required in Compose today?
A1: No. The Compose Specification makes it optional and obsolete. Compose v2 ignores it and only warns.

Q2: What replaced it for naming a stack?
A2: The optional top-level `name:` key sets the project name. Otherwise the project name is the folder name or `-p` flag or `COMPOSE_PROJECT_NAME`.

Q3: What were the main version families?
A3: v1 (no services key), v2.x (single host, `mem_limit`, `depends_on` conditions), v3.x (Swarm focused, `deploy:`). The Specification merged v2 and v3 features.

Q4: How do you check which Compose you have?
A4: `docker compose version` for v2 plugin; `docker-compose --version` for legacy v1.

Q5: Does removing `version` change running containers?
A5: No. The schema is the same; only the warning disappears.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You must support legacy `docker-compose` v1 on an old server (quoted string).
- You are reading an old repo and need to understand which features it assumed.

❌ Avoid when:
- Writing any new project on Compose v2 (use `name:` and no version).
- You expect the number to control feature availability.

---

## 📊 Visual Diagram
```
 OLD (v1 / v2 / v3 schemas)            NEW (Compose Specification)
+---------------------------+         +-----------------------------+
| version: "3.8"            |         | name: myapp   (optional)    |
| services:                 |   -->   | services:                   |
|   web: ...                |         |   web: ...                  |
+---------------------------+         +-----------------------------+
 tool picks schema by number           one schema, always latest
 mismatch => errors                    `version` => warning only
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| version | Old schema selector, now obsolete | पुराना schema चुनने वाला field, अब obsolete |
| Compose Specification | Open, unified file format | एकीकृत open file format |
| name | Top-level project name | project का नाम |
| Compose v2 | `docker compose` Go plugin | Go में बना `docker compose` plugin |
| Compose v1 | `docker-compose` Python tool (EOL) | पुराना Python tool (बंद) |

---

## ⚡ 3-Line Summary
English: `version` was the old schema selector in compose files.
English: In Compose v2 it is obsolete, ignored, and only prints a warning.
English: Remove it, optionally add `name:`, and check your tool with `docker compose version`.
Hindi: `version` पुराने compose files में schema चुनने वाला field था।
Hindi: Compose v2 में यह obsolete है, ignore होता है और सिर्फ warning देता है।
Hindi: इसे हटाइए, चाहें तो `name:` जोड़िए, और `docker compose version` से tool check कीजिए।

---

## ➡️ Next Topic
184. services Field - now that the file header is clean, the `services:` block is where every container (api, db, nginx) is actually defined.
