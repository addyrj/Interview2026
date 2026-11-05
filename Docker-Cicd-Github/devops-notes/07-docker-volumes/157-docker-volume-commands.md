# 157. docker volume Commands
# हिंदी में: docker volume कमांड्स

---

## 🔵 Simple Definition (English)
`docker volume` is the CLI group used to create, list, inspect, remove and clean up Docker volumes. A volume is storage managed by Docker that lives outside a container's writable layer, so data survives when the container is deleted.
The main subcommands are: `create`, `ls`, `inspect`, `rm`, `prune`.

## 🔵 सरल परिभाषा (Hindi)
`docker volume` एक CLI group है जिससे Docker volumes बनाए, list, inspect, delete और साफ़ किए जाते हैं। Volume वो storage है जिसे Docker manage करता है और जो container की writable layer के बाहर रहता है, इसलिए container delete होने पर भी data बचा रहता है।
मुख्य subcommands: `create`, `ls`, `inspect`, `rm`, `prune`।

---

## 🔴 Problem it Solves
- Without volume commands you would only see volumes as random 64-character hash folders under `/var/lib/docker/volumes`, with no way to know which one belongs to which app.
- Teams need to answer: "Which volume holds the Postgres data?", "Which volumes are unused and eating disk?", "Where on the host is it stored?". The `docker volume` commands answer all of these.
- They also let you create a volume in advance (with labels, driver and options) rather than letting `docker run` create anonymous ones by accident.

## 🔴 यह क्यों बना? (Hindi)
- Volume commands के बिना volumes सिर्फ `/var/lib/docker/volumes` में 64-अक्षर के hash folders दिखते, और पता नहीं चलता कि कौन सा किस app का है।
- Teams को जानना होता है: "Postgres का data किस volume में है?", "कौन से volumes unused हैं और disk खा रहे हैं?", "host पर कहाँ stored है?"। `docker volume` commands इन सबका जवाब देते हैं।
- इनसे आप volume को पहले से (labels, driver, options के साथ) बना सकते हैं, `docker run` के बनाए anonymous volumes पर निर्भर नहीं रहना पड़ता।

---

## 🟢 How it Works — Step by Step

```
Step 1 → docker volume create pgdata        (Docker makes a folder under /var/lib/docker/volumes/pgdata/_data)
Step 2 → docker volume ls                   (lists name + driver of every volume)
Step 3 → docker run -v pgdata:/var/lib/postgresql/data postgres:16   (container mounts the volume)
Step 4 → docker volume inspect pgdata       (shows Mountpoint, Driver, Labels, CreatedAt)
Step 5 → docker rm -f container             (container gone, volume still there)
Step 6 → docker volume rm pgdata            (only works if NO container, running or stopped, uses it)
Step 7 → docker volume prune                (removes all volumes not used by any container)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → docker volume create pgdata   (Docker /var/lib/docker/volumes/pgdata/_data में folder बनाता है)
Step 2 → docker volume ls              (सभी volumes का name + driver दिखाता है)
Step 3 → docker run -v pgdata:/var/lib/postgresql/data postgres:16   (container volume mount करता है)
Step 4 → docker volume inspect pgdata  (Mountpoint, Driver, Labels, CreatedAt दिखाता है)
Step 5 → docker rm -f container        (container गया, volume बचा)
Step 6 → docker volume rm pgdata       (तभी चलेगा जब कोई container, running या stopped, इसे use न कर रहा हो)
Step 7 → docker volume prune           (जो volumes किसी container से जुड़े नहीं, सब हटा देता है)
```

---

## 🟡 Real World Example
On your VPS you run a Node.js API plus Postgres. One morning disk is 95% full. You SSH in and run `docker system df -v`, see 14 anonymous volumes from old test containers, filter with `docker volume ls -f dangling=true`, and prune them after confirming that `pgdata` (named, in use) is safe. This is a routine on-call task, and the exact reason interviewers ask about these commands.

## 🟡 Real Example Hindi mein
आपके VPS पर Node.js API और Postgres चल रहे हैं। एक सुबह disk 95% भर गई। आप SSH करके `docker system df -v` चलाते हैं, पुराने test containers के 14 anonymous volumes दिखते हैं, `docker volume ls -f dangling=true` से filter करते हैं, और यह पक्का करके कि `pgdata` (named, in use) safe है, बाकी prune कर देते हैं। यह on-call का रोज़ का काम है और interview में इसीलिए पूछा जाता है।

---

## 💻 Code / Config Example — Basic
```bash
# ---- basic volume lifecycle ----
docker volume create pgdata                      # create a named volume called pgdata
docker volume ls                                 # list all volumes (DRIVER and VOLUME NAME columns)
docker volume inspect pgdata                     # print JSON: Mountpoint, Driver, Labels, Scope
docker volume inspect -f '{{ .Mountpoint }}' pgdata   # print only the host path using a Go template

# use it: the container writes Postgres files into the volume
docker run -d --name db \
  -e POSTGRES_PASSWORD=example_pw \
  -v pgdata:/var/lib/postgresql/data \
  postgres:16

docker rm -f db                                  # remove container; the volume is NOT removed
docker volume ls                                 # pgdata is still listed
docker volume rm pgdata                          # delete volume (fails if any container still references it)
```

## 💻 Code / Config Example — Advanced
```bash
#!/usr/bin/env bash
# vol-audit.sh - weekly volume hygiene for a VPS (example script, adjust names)
set -euo pipefail                                # stop on error, unset var, or pipe failure

# 1) create a labelled volume so we can find it later by label
docker volume create \
  --label app=orders-api \
  --label env=prod \
  --label backup=daily \
  orders_pgdata                                  # labels are free-form key=value metadata

# 2) list only volumes with a label (filter syntax is real: -f label=key=value)
docker volume ls -f label=backup=daily

# 3) list dangling volumes (not used by ANY container)
docker volume ls -f dangling=true

# 4) show only names, handy for scripts
docker volume ls -q                              # -q prints only volume names

# 5) see which containers use a volume (running or stopped)
docker ps -a --filter volume=orders_pgdata --format '{{.Names}}'

# 6) show per-volume disk usage
docker system df -v | sed -n '/Local Volumes/,$p'   # print the volumes section only

# 7) preview before deleting: what would prune remove?
docker volume ls -f dangling=true                # always look first, prune has no undo

# 8) delete dangling volumes only after human review
docker volume prune -f --filter label!=keep=true # -f skips the prompt; filter protects labelled volumes
```

---

## 🟠 My Stack Integration
In your docker-compose on the VPS, Compose creates volumes named `<project>_<volume>` (for example `shop_pgdata`). So when you run `docker volume ls` you will see the project prefix. Use `docker compose down` (keeps volumes) and never `docker compose down -v` on production unless you really want to delete data.

```yaml
# docker-compose.yml - volumes managed by Compose, inspected with docker volume commands
services:
  db:                                  # Postgres for the Node.js / FastAPI backends
    image: postgres:16                 # example tag, pin to a version you tested
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/pg_pw   # password from a secret file, not plain text
    volumes:
      - pgdata:/var/lib/postgresql/data            # named volume mounted at Postgres data dir
    secrets:
      - pg_pw                                      # attach the secret to this service
volumes:
  pgdata:                              # Compose will create it as <project>_pgdata
    labels:
      backup: "daily"                  # label lets your backup script find it
secrets:
  pg_pw:
    file: ./secrets/pg_pw.txt          # keep this file out of git (.gitignore)
```
Security note: volume data on the host under `/var/lib/docker/volumes` is readable by root. Restrict SSH/sudo access, and back it up (note 161).

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Running `docker volume prune` blindly on production.
✅ Correct: List with `docker volume ls -f dangling=true` first. A volume of a stopped DB container counts as "in use", but a volume left after `docker rm -v` or compose recreation may be a dangling copy of data you still need.

❌ Mistake 2: Running `docker compose down -v` to "restart cleanly".
✅ Correct: Use `docker compose down` or `docker compose restart`. The `-v` flag deletes the named volumes declared in the file, which means your database.

❌ Mistake 3: Expecting `docker volume rm` to work while a stopped container exists.
✅ Correct: Remove the container first (`docker rm`) and then the volume. Find the user with `docker ps -a --filter volume=NAME`.

❌ Mistake 4: Not naming volumes, so anonymous hash volumes pile up.
✅ Correct: Always use `-v name:/path` or declare `volumes:` in Compose.

---

## 🧠 Tricky Interview Question
You run `docker rm -f db` and then `docker volume prune`. Is the Postgres data lost?

Answer: Yes, if the volume is no longer referenced by any container, it is considered unused and prune deletes it. In Docker Engine 23+ `docker volume prune` only removes anonymous (unnamed) volumes by default and needs `--all` (`-a`) to also remove named ones; older versions removed all unused volumes. So the answer depends on version, which is why you must check `docker volume ls` first and keep backups. (Version-dependent: verify with `docker volume prune --help` on your host.)

---

## ⚫ Interview Questions + Answers

Q1: Which commands does `docker volume` have?
A1: `create`, `inspect`, `ls`, `prune`, `rm` (and `update` for cluster volumes in newer versions).

Q2: How do you find where a volume lives on the host?
A2: `docker volume inspect NAME` and read `Mountpoint`, usually `/var/lib/docker/volumes/NAME/_data` on Linux.

Q3: Does removing a container remove its volume?
A3: No, named volumes stay. Anonymous volumes also stay unless you use `docker rm -v` or `--rm` when running.

Q4: What does a "dangling" volume mean?
A4: A volume not referenced by any container. `docker volume ls -f dangling=true` lists them.

Q5: How do you list volumes used by one container?
A5: `docker inspect -f '{{ json .Mounts }}' CONTAINER`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need to audit, clean or script volume management on servers/CI runners.
- You want pre-created volumes with labels or special drivers.
- Debugging "where did my data go" after redeploys.

❌ Avoid when:
- You run Kubernetes: use PersistentVolumes and `kubectl`, not `docker volume`.
- Managing data by touching `/var/lib/docker/volumes` directly. Use the CLI or a helper container.

---

## 📊 Visual Diagram
```
 docker volume create pgdata
            |
            v
 +---------------------------+        +-----------------------+
 | /var/lib/docker/volumes/  |<-mount-| container "db"        |
 |   pgdata/_data            |        | /var/lib/postgresql/  |
 +---------------------------+        |   data                |
            ^                         +-----------+-----------+
            |                                     |
            |        docker rm db  --------------+  (container deleted)
            |
   data stays until: docker volume rm pgdata  /  prune
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Named volume | Volume with a chosen name | नाम वाला volume |
| Anonymous volume | Auto-named hash volume | बिना नाम का (hash) volume |
| Dangling volume | Volume not used by any container | unused/लावारिस volume |
| Mountpoint | Host path of the volume data | volume का host path |
| Label | key=value metadata for filtering | filtering के लिए टैग |
| Prune | Bulk delete of unused objects | unused चीज़ें हटाना |

---

## ⚡ 3-Line Summary
English: `docker volume` has create, ls, inspect, rm and prune.
Volumes outlive containers, so deleting a container never deletes named volumes.
Always inspect and list before prune, and never use `down -v` on production.
Hindi: `docker volume` में create, ls, inspect, rm और prune होते हैं।
Volumes containers से ज़्यादा जीते हैं, इसलिए container delete करने से named volume नहीं हटता।
Prune से पहले हमेशा list और inspect करो, और production पर `down -v` कभी मत चलाओ।

---

## ➡️ Next Topic
158. Data Persistence: now that you can manage volumes, learn the bigger idea of how containers keep data across restarts and redeploys.
