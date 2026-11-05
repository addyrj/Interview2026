# 50. Docker Objects Overview
# हिंदी में: Docker Objects का परिचय

---

## 🔵 Simple Definition (English)
**Docker objects** are the resources the daemon creates and manages: **images** (read-only templates), **containers** (running instances), **networks** (virtual connectivity), **volumes** (persistent data), plus **build cache**, **secrets/configs** (Swarm), and **plugins**. Every Docker command is really "create / list / inspect / remove" on one of these objects.

## 🔵 सरल परिभाषा (Hindi)
**Docker objects** वे resources हैं जिन्हें daemon बनाता और संभालता है: **images** (read-only templates), **containers** (चलते instances), **networks** (virtual connectivity), **volumes** (स्थायी data), साथ में **build cache**, **secrets/configs** (Swarm), और **plugins**। हर Docker command असल में इनमें से किसी object पर "बनाओ / दिखाओ / जाँचो / हटाओ" है।

---

## 🔴 Problem it Solves
Beginners treat Docker as a magic `run` command and get confused: where is my data? why can't container A reach B? why is my disk full of old stuff? Knowing the object model gives a mental map: images are immutable, containers are disposable, data lives in volumes, connectivity in networks. Each has its own lifecycle and cleanup command.

## 🔴 यह क्यों बना? (Hindi)
Beginners Docker को जादुई `run` command समझते हैं और उलझते हैं: मेरा data कहाँ है? container A, B तक क्यों नहीं पहुँच रहा? disk पुरानी चीज़ों से क्यों भरी है? Object model एक मानसिक नक्शा देता है: images अटल हैं, containers disposable हैं, data volumes में रहता है, connectivity networks में। हर object की अपनी life-cycle और cleanup command है।

---

## 🟢 How it Works — Step by Step

```
Object        Create                      List               Remove               Persists after container deleted?
-----------   -------------------------   ----------------   ------------------   ---------------------------------
Image         docker build / pull         docker images      docker rmi           yes (until removed)
Container     docker run / create         docker ps -a       docker rm            n/a (it is the thing deleted)
Volume        docker volume create / -v   docker volume ls   docker volume rm     YES (data survives)
Network       docker network create       docker network ls  docker network rm    yes
Build cache   (automatic by build)        docker buildx du   docker builder prune yes

Step 1 → Image is built/pulled (immutable layers)
Step 2 → Container = image + writable layer + config (ports, env, mounts, network)
Step 3 → Container attaches to a network (default bridge or your custom one)
Step 4 → Container mounts volumes/bind mounts for persistent data
Step 5 → Remove container: writable layer vanishes; image and volume remain
```

## 🟢 कैसे काम करता है? (Hindi)
```
Object        बनाने की command            सूची                हटाना                container हटने के बाद भी रहता है?
-----------   -------------------------   ----------------   ------------------   ---------------------------------
Image         docker build / pull         docker images      docker rmi           हाँ (हटाने तक)
Container     docker run / create         docker ps -a       docker rm            लागू नहीं (यही तो हटता है)
Volume        docker volume create / -v   docker volume ls   docker volume rm     हाँ (data बचा रहता है)
Network       docker network create       docker network ls  docker network rm    हाँ
Build cache   (build में अपने-आप)         docker buildx du   docker builder prune हाँ

Step 1 → Image build/pull होती है (अटल layers)
Step 2 → Container = image + writable layer + config (ports, env, mounts, network)
Step 3 → Container network से जुड़ता है (default bridge या आपका custom)
Step 4 → Container स्थायी data के लिए volumes/bind mounts mount करता है
Step 5 → Container हटाओ: writable layer गायब; image और volume बचते हैं
```

---

## 🟡 Real World Example
A production Postgres on a VPS: the **image** `postgres:16-alpine` (immutable), a **container** `db` (replaceable), a **volume** `pgdata` (the actual database files), and a **network** `backend` (only API containers can reach `db:5432`). On a Postgres minor upgrade you delete the container, pull the new image, create a new container, attach the same volume: the data is intact. Lose the volume and you lose the database, which is why volumes get backups.

## 🟡 Real Example Hindi mein
VPS पर production Postgres: **image** `postgres:16-alpine` (अटल), **container** `db` (बदला जा सकता है), **volume** `pgdata` (असली database files), और **network** `backend` (सिर्फ़ API containers `db:5432` तक पहुँच सकते हैं)। Postgres minor upgrade में container हटाओ, नई image pull करो, नया container बनाओ, वही volume जोड़ो: data सुरक्षित। Volume खोया तो database खोया, इसीलिए volumes का backup होता है।

---

## 💻 Code / Config Example — Basic
```bash
# Walk through all four object types (needs a Docker daemon)
docker pull postgres:16-alpine                         # IMAGE: download (example tag)
docker volume create pgdata                            # VOLUME: persistent storage managed by Docker
docker network create backend                          # NETWORK: user-defined bridge (gives DNS by name)

docker run -d --name db \
  --network backend \
  -v pgdata:/var/lib/postgresql/data \
  -e POSTGRES_PASSWORD=change-me-now \
  postgres:16-alpine
# ^ CONTAINER: attached to network "backend", data on volume "pgdata", password via env (use secrets in prod)

docker ps                                              # see the container
docker volume ls                                       # see pgdata
docker network inspect backend                         # see which containers joined and their IPs
docker rm -f db                                        # delete container only...
docker volume ls                                       # ...pgdata still exists: data survived
docker system df                                       # disk usage per object type
```

## 💻 Code / Config Example — Advanced
```yaml
# docker-compose.yml - all object types declared together (Postgres + FastAPI + Redis)
# Compose creates: images (pull/build), containers (services), network, named volumes.
services:
  db:                                          # container 1
    image: postgres:16-alpine                  # IMAGE object (pinned major version)
    environment:
      POSTGRES_USER: app                       # DB user
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password   # read password from a mounted secret file
      POSTGRES_DB: app                         # initial DB
    secrets:
      - db_password                            # mount the secret into /run/secrets/db_password
    volumes:
      - pgdata:/var/lib/postgresql/data        # VOLUME object for persistence
    networks: [backend]                        # NETWORK object (private)
    restart: unless-stopped                    # auto-restart
    healthcheck:                               # health state for dependants
      test: ["CMD-SHELL", "pg_isready -U app -d app"]   # Postgres readiness command
      interval: 10s                            # every 10 seconds
      timeout: 5s                              # 5s per check
      retries: 5                               # unhealthy after 5 fails

  fastapi:                                     # container 2
    build: ./fastapi                           # IMAGE built from local Dockerfile
    environment:
      DB_HOST: db                              # service name = DNS name on the network
    depends_on:
      db:
        condition: service_healthy             # start only after DB reports healthy
    networks: [backend]                        # same private network
    ports:
      - "127.0.0.1:8000:8000"                  # expose to host loopback only (Nginx proxies)

  redis:                                       # container 3
    image: redis:7-alpine                      # IMAGE
    command: ["redis-server", "--appendonly", "yes"]   # persist data with AOF
    volumes:
      - redisdata:/data                        # second VOLUME
    networks: [backend]                        # private network

volumes:
  pgdata:                                      # declare named volume
  redisdata:                                   # declare named volume

networks:
  backend:                                     # declare network (compose names it <project>_backend)

secrets:
  db_password:
    file: ./secrets/db_password.txt            # local file (chmod 600, git-ignored) -> mounted as a secret
```

---

## 🟠 My Stack Integration
- **Node.js/FastAPI:** images built in CI; containers replaced on each deploy.
- **React:** build output baked into an Nginx image (no volume needed), or bind-mounted.
- **Nginx:** config as a read-only bind mount; certificates (Let's Encrypt) as a volume so they survive recreation.
- **VPS backups:** back up volumes, not containers: `docker run --rm -v pgdata:/data -v $(pwd):/backup alpine tar czf /backup/pgdata.tgz -C /data .` (for DB consistency prefer `pg_dump`).
- **AWS:** volumes map to EBS (EC2) or EFS; images live in ECR; networks map to VPC + security groups.

```bash
# Nightly Postgres backup from the running container (consistent logical dump)
docker exec db pg_dump -U app -d app | gzip > /backups/app-$(date +%F).sql.gz   # dump compressed to a dated file
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Expecting data to survive `docker rm` without a volume.
✅ Correct: Mount a named volume at the data path.

❌ Mistake 2: Running `docker compose down -v` or `docker system prune --volumes` carelessly.
✅ Correct: `-v` deletes volumes (your database). Use plain `down`; back up before pruning.

❌ Mistake 3: Using the default `bridge` network and `localhost` between containers.
✅ Correct: Use a user-defined network and service names (`db`); `localhost` inside a container is itself.

❌ Mistake 4: Passwords in `environment:` visible via `docker inspect`.
✅ Correct: File-based secrets (`*_FILE`) or a secrets manager; keep secret files out of git.

---

## 🧠 Tricky Interview Question
"You delete a container that used an anonymous volume (`-v /var/lib/mysql`) and recreate it with the same command. The data is gone. The volume still exists in `docker volume ls`. Why?"

Answer: Anonymous volumes get a random name; recreating the container makes a *new* anonymous volume, so the old one is orphaned ("dangling"), still holding the data under a random ID. Use named volumes (`-v mysqldata:/var/lib/mysql`) so the same volume is re-attached. Recover by mounting the orphaned volume by its ID.

---

## ⚫ Interview Questions + Answers

Q1: List Docker objects.
A1: Images, containers, volumes, networks, plus build cache, plugins, and Swarm services/secrets/configs.

Q2: Named volume vs bind mount vs tmpfs?
A2: Named volume: managed by Docker, portable, best for DB data. Bind mount: host path mapped in, good for config/dev code. tmpfs: in-memory, non-persistent, good for secrets/temp.

Q3: Dangling image?
A3: An untagged image layer set (`<none>:<none>`), typically left after rebuilding the same tag; removed by `docker image prune`.

Q4: What is lost when a container is deleted?
A4: Its writable layer, and its anonymous volumes only if removed with `docker rm -v`. Images and named volumes are kept.

Q5: How do containers find each other?
A5: On a user-defined network Docker's embedded DNS resolves service/container names to IPs.

---

## 🔷 When to Use + When Not to Use
✅ Use named volumes when:
- Databases, uploaded files, TLS certs, anything that must outlive containers

❌ Avoid when:
- Using volumes for source code in production (bake code into the image)
- Relying on the container writable layer for important data

---

## 📊 Visual Diagram
```
                 Docker daemon manages
 +----------------------------------------------------------+
 |  IMAGE (read-only)         NETWORK "backend"              |
 |  postgres:16-alpine   +---------------------------+       |
 |        │              |  db <---DNS--- fastapi    |       |
 |        v              +-----^---------------^-----+       |
 |  CONTAINER db  [writable layer]               │            |
 |        │                                 CONTAINER fastapi |
 |        v                                                   |
 |  VOLUME pgdata  ===> /var/lib/postgresql/data (persists)   |
 +----------------------------------------------------------+
 docker rm db  -> container + writable layer gone; image, volume, network stay
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Image | Immutable template | अटल template |
| Container | Running instance | चलता हुआ instance |
| Volume | Persistent data store | स्थायी data भंडार |
| Bind mount | Host folder mounted in | host folder का mount |
| Network | Virtual connectivity | virtual संपर्क जाल |
| Dangling | Unreferenced leftover | बिना संदर्भ का बचा हुआ |
| Build cache | Saved build layers | build की सहेजी layers |

---

## ⚡ 3-Line Summary
English: Docker manages images, containers, networks, and volumes, each with its own lifecycle.
English: Containers are disposable; data belongs in named volumes and connectivity in user-defined networks.
English: Clean up with prune carefully, and never delete volumes you have not backed up.
Hindi: Docker images, containers, networks और volumes संभालता है, हर एक की अपनी life-cycle है।
Hindi: Containers disposable हैं; data named volumes में और connectivity user-defined networks में रखो।
Hindi: Prune सावधानी से करो, और बिना backup वाले volumes कभी मत हटाओ।

---

## ➡️ Next Topic
**51. Docker Image - What it is** - the first object in depth: layers, tags, digests, and how images are built.
