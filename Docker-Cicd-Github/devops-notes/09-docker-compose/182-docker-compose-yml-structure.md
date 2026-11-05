# 182. docker-compose.yml Structure
# हिंदी में: docker-compose.yml की संरचना

---

## 🔵 Simple Definition (English)
A Compose file is a YAML document with a few **top-level keys**: `name`, `services` (required), `networks`, `volumes`, `configs`, `secrets`. Each service has its own keys such as `image`, `build`, `ports`, `environment`, `volumes`, `depends_on`, `healthcheck`, `restart`.

## 🔵 सरल परिभाषा (Hindi)
Compose file एक YAML document है जिसमें कुछ **top-level keys** होती हैं: `name`, `services` (ज़रूरी), `networks`, `volumes`, `configs`, `secrets`। हर service की अपनी keys होती हैं जैसे `image`, `build`, `ports`, `environment`, `volumes`, `depends_on`, `healthcheck`, `restart`।

---

## 🔴 Problem it Solves
Beginners paste snippets from the internet and hit errors: wrong indentation, a `volumes` key at the wrong level, mixing list and map syntax, or declaring a named volume but forgetting the top-level `volumes:` block. Knowing the skeleton lets you read, write and debug any Compose file quickly.

## 🔴 यह क्यों बना? (Hindi)
Beginners internet से snippets paste करते हैं और errors पाते हैं: गलत indentation, `volumes` key गलत level पर, list और map syntax का मिश्रण, या named volume use करके top-level `volumes:` block भूल जाना। Skeleton समझ लो तो कोई भी Compose file जल्दी पढ़, लिख और debug कर सकते हो।

---

## 🟢 How it Works — Step by Step

```
Step 1 → name:      (optional) project name, prefix for resources
Step 2 → services:  (required) map of service-name -> definition
Step 3 → networks:  (optional) declare custom networks used by services
Step 4 → volumes:   (optional) declare named volumes used by services
Step 5 → configs:/secrets: (optional) injected files, read-only in containers
Step 6 → Compose validates the file, interpolates ${VARS}, merges override files
Step 7 → `docker compose config` prints the final merged, validated result
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → name:      (optional) project का नाम, resources का prefix
Step 2 → services:  (ज़रूरी) service-name -> definition का map
Step 3 → networks:  (optional) services द्वारा use होने वाले custom networks declare करो
Step 4 → volumes:   (optional) services द्वारा use होने वाली named volumes declare करो
Step 5 → configs:/secrets: (optional) containers में read-only files के रूप में inject
Step 6 → Compose file validate करता है, ${VARS} भरता है, override files merge करता है
Step 7 → `docker compose config` final merged, validated result दिखाता है
```

---

## 🟡 Real World Example
A new developer joins and sees a 150-line `compose.yaml`. Because she knows the structure, she reads it top-down in 2 minutes: three services (nginx, api, postgres), two networks (edge, backend), one volume (pgdata), one secret (db password). She spots a bug immediately: `api` references the volume `uploads` that is never declared at the top level, so Compose would fail with "undefined volume".

## 🟡 Real Example Hindi mein
नया developer join करती है और 150-line का `compose.yaml` देखती है। Structure जानती है, इसलिए 2 मिनट में ऊपर से नीचे पढ़ लेती है: तीन services (nginx, api, postgres), दो networks (edge, backend), एक volume (pgdata), एक secret (db password)। उसे bug तुरंत दिखता है: `api` volume `uploads` use करता है जो top-level पर declare ही नहीं, इसलिए Compose "undefined volume" error देगा।

---

## 💻 Code / Config Example — Basic
```yaml
# compose.yaml - the skeleton with every top-level key annotated
name: myapp                            # optional: project name (prefix for networks/volumes)

services:                              # REQUIRED: all containers live under here
  web:                                 # service name = hostname on the network
    image: nginx:1.27-alpine           # ready-made image from a registry (example tag)
    ports:
      - "8080:80"                      # host_port:container_port (quote it!)
    volumes:
      - web_data:/usr/share/nginx/html # named volume : path inside container
    networks:
      - front                          # attach to the network declared below

networks:                              # optional: custom networks
  front: {}                            # default bridge driver, empty options

volumes:                               # optional: named volumes
  web_data: {}                         # Docker-managed volume
```

```bash
docker compose config            # validate + print the merged file (catches indentation/typos)
docker compose config --services # list service names only
docker compose config -q         # quiet: exit code 0 if valid, non-zero if broken
```

## 💻 Code / Config Example — Advanced
```yaml
# compose.yaml - all major keys in one realistic stack
name: shop                                     # project name

x-common: &common                              # YAML anchor: reusable block (x- keys are ignored by Compose)
  restart: unless-stopped                      # restart policy shared by services
  logging:
    driver: json-file                          # default Docker log driver
    options:
      max-size: "10m"                          # rotate logs at 10 MB
      max-file: "3"                            # keep three files

services:
  api:
    <<: *common                                # merge the shared block here
    build:
      context: ./api                           # folder containing Dockerfile
      dockerfile: Dockerfile                   # file name (default shown for clarity)
      args:
        NODE_VERSION: "20"                     # build-time ARG
    image: myorg/shop-api:1.4.2                # name for the built image
    command: ["node", "dist/server.js"]        # override CMD (exec form)
    environment:
      NODE_ENV: production                     # inline env var
      DB_HOST: db                              # service-name DNS
    env_file:
      - .env                                   # more variables, kept out of git
    ports:
      - "127.0.0.1:3000:3000"                  # loopback only (nginx on host proxies)
    volumes:
      - uploads:/app/uploads                   # named volume
      - ./config/app.json:/app/config.json:ro  # bind mount, read-only
    depends_on:
      db:
        condition: service_healthy             # wait for healthcheck success
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:3000/health"]  # readiness probe
      interval: 10s
      timeout: 3s
      retries: 5
    networks: [backend]
    secrets:
      - db_password                            # mounted at /run/secrets/db_password

  db:
    <<: *common
    image: postgres:16-alpine                  # example tag
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password   # read password from the secret file
    volumes:
      - pgdata:/var/lib/postgresql/data        # persistent data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]      # db readiness
      interval: 5s
      timeout: 3s
      retries: 10
    networks: [backend]
    secrets:
      - db_password

networks:
  backend:
    driver: bridge                             # explicit driver
    internal: true                             # no internet access

volumes:
  pgdata: {}
  uploads: {}

secrets:
  db_password:
    file: ./secrets/db_password.txt            # file on host (gitignored); mounted into containers
```

---

## 🟠 My Stack Integration
- **Order in your repo:** `compose.yaml` at the root next to `api/`, `web/`, `nginx/`, `.env.example`.
- **React:** `web` service builds with a multi-stage Dockerfile; no volume needed in production.
- **FastAPI:** `command: ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]`.
- **Nginx:** config as a `:ro` bind mount; certs from Let's Encrypt in `/etc/letsencrypt` bind mount.
- **VPS/AWS:** the same file runs on EC2; add `compose.prod.yaml` for prod-only settings (restart, resource limits, no source mounts).
- **Tooling:** run `docker compose config -q` in CI to fail early on broken YAML.

```yaml
# GitHub Actions step: validate compose file on every pull request
- name: Validate compose file            # step name
  run: docker compose -f compose.yaml config -q   # exit non-zero when invalid
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using tabs for indentation.
✅ Correct: YAML allows spaces only; use 2 spaces.

❌ Mistake 2: Unquoted ports like `- 80:80`; YAML 1.1 can parse `xx:yy` below 60 as base-60 numbers.
✅ Correct: Always quote: `- "80:80"`.

❌ Mistake 3: Using a named volume in a service without declaring it under top-level `volumes:`.
✅ Correct: Declare it (bind mounts like `./data:/data` need no declaration).

❌ Mistake 4: Putting `networks:` or `volumes:` indented inside `services:` at the wrong level.
✅ Correct: They are siblings of `services` at top level; per-service ones are inside each service.

❌ Mistake 5: Still writing `version: "3.8"`.
✅ Correct: Not needed in Compose v2; it is ignored with a warning.

---

## 🧠 Tricky Interview Question
**Q:** What is the difference between `environment:` as a list (`- KEY=val`) and as a map (`KEY: val`), and what happens with `KEY:` (no value)?

**Answer:** Both are valid and equivalent for plain values. With no value (`- KEY` or `KEY:`), Compose passes through the variable's value from the shell/`.env` of the host at `up` time; if unset, it stays unset in the container. A gotcha: in map form YAML converts unquoted `yes`, `no`, `on`, `off`, or numbers into booleans or numbers, so quote values like `"true"` or `"0123"` when they must remain strings.

---

## ⚫ Interview Questions + Answers

Q1: Which top-level key is mandatory?
A1: `services`.

Q2: What are `x-` keys?
A2: Extension fields Compose ignores; used with YAML anchors for DRY configuration.

Q3: How do you see the final config after merging files and interpolation?
A3: `docker compose config`.

Q4: Where do named volumes get declared?
A4: Under the top-level `volumes:` key, referenced from each service.

Q5: What decides the service hostname?
A5: The service key name (and optional aliases), not `container_name`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Starting any Compose project; follow the skeleton
- Reviewing teammates' Compose files
- Refactoring with anchors to reduce duplication

❌ Avoid when:
- Over-using anchors and merges so the file becomes unreadable; split into multiple files instead

---

## 📊 Visual Diagram
```
 compose.yaml
 ├── name: shop
 ├── x-common: &common      (reusable fragment)
 ├── services:
 │     ├── api:    image/build, ports, environment, volumes,
 │     │           depends_on, healthcheck, networks, secrets
 │     └── db:     image, volumes, healthcheck, networks
 ├── networks:   backend
 ├── volumes:    pgdata, uploads
 └── secrets:    db_password
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Top-level key | Root section of the file | file का मुख्य भाग |
| Anchor (&) / alias (*) | YAML reuse feature | दोबारा use की सुविधा |
| Interpolation | Replace ${VAR} with values | ${VAR} को मान से बदलना |
| Extension field | `x-` key ignored by Compose | `x-` वाली अनदेखी key |
| Secret | Sensitive file mounted read-only | संवेदनशील file |
| Bind mount | Host folder mounted in container | host folder का mount |

---

## ⚡ 3-Line Summary
English: A Compose file has `services` (required) plus optional `networks`, `volumes`, `secrets`, `configs` and `name`.
Quote ports, use spaces, declare named volumes, and validate with `docker compose config`.
Use anchors to avoid repetition.
Hindi: Compose file में `services` (ज़रूरी) के साथ optional `networks`, `volumes`, `secrets`, `configs` और `name` होते हैं।
Ports quote करो, spaces use करो, named volumes declare करो, और `docker compose config` से validate करो।
दोहराव से बचने के लिए anchors use करो।

---

## ➡️ Next Topic
**183. version Field** - why the old `version:` line is now obsolete and what replaced it.
