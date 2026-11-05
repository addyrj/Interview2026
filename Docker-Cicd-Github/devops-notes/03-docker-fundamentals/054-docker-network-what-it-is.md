---

# 054. Docker Network — What it is
# हिंदी में: Docker Network — यह क्या है

---

## 🔵 Simple Definition (English)
A **Docker network** is a virtual network that connects containers to each other and to the outside world. Containers on the same user-defined network can reach each other by container or service name, and Docker controls which ports are visible outside.

## 🔵 सरल परिभाषा (Hindi)
**Docker network** एक virtual network है जो containers को आपस में और बाहरी दुनिया से जोड़ता है। एक ही user-defined network के containers एक-दूसरे को container या service के नाम से पहुँच सकते हैं, और Docker तय करता है कि कौन से ports बाहर दिखें।

---

## 🔴 Problem it Solves
Containers get private IPs that change on every restart, so hard-coding IPs breaks. Without isolation, every container could reach every other one, including your database from a public-facing service. Docker networks give built-in DNS (service names instead of IPs), isolation between stacks, and a clean way to publish only the ports you want.

## 🔴 यह क्यों बना? (Hindi)
Containers को private IP मिलता है जो हर restart पर बदल सकता है, इसलिए IP hard-code करना टूट जाता है। Isolation के बिना हर container हर दूसरे से बात कर सकता, यहाँ तक कि public-facing service भी आपके database तक। Docker networks built-in DNS (IP की जगह service name), stacks के बीच isolation, और सिर्फ ज़रूरी ports publish करने का साफ तरीका देते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Docker Engine starts and creates default networks: bridge, host, none
Step 2 → You create a user-defined bridge: docker network create appnet
Step 3 → Containers join it: docker run --network appnet --name db ...
Step 4 → Docker's embedded DNS (127.0.0.11) resolves "db" to the container's current IP
Step 5 → api calls postgres://db:5432 -> traffic stays on the virtual bridge
Step 6 → Only ports published with -p 80:80 are reachable from the host/internet (via iptables NAT)
```

Main drivers:
- **bridge** (default): private network on one host. The *default* bridge has no name-based DNS; **user-defined** bridges do.
- **host**: container shares the host's network stack, no isolation, no port mapping (Linux).
- **none**: no networking at all.
- **overlay**: multi-host networks (Swarm). **macvlan**: container gets its own MAC/IP on the LAN.

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Docker Engine शुरू होते ही default networks बनाता है: bridge, host, none
Step 2 → आप user-defined bridge बनाते हैं: docker network create appnet
Step 3 → Containers उसमें जुड़ते हैं: docker run --network appnet --name db ...
Step 4 → Docker का embedded DNS (127.0.0.11) "db" को container के मौजूदा IP में बदल देता है
Step 5 → api postgres://db:5432 को call करता है -> traffic virtual bridge के अंदर रहता है
Step 6 → सिर्फ -p 80:80 से publish किए ports host/internet से पहुँचते हैं (iptables NAT से)
```

मुख्य drivers:
- **bridge** (default): एक host पर private network। *Default* bridge में नाम से DNS नहीं होता, **user-defined** bridge में होता है।
- **host**: container host का network stack share करता है, isolation नहीं, port mapping नहीं (Linux)।
- **none**: कोई networking नहीं।
- **overlay**: multi-host networks (Swarm)। **macvlan**: container को LAN पर अपना MAC/IP मिलता है।

---

## 🟡 Real World Example
On your VPS: Nginx (public, ports 80/443), FastAPI (internal), Postgres (internal), Redis (internal). You create two networks: `frontend` (nginx + api) and `backend` (api + db + redis). Nginx can reach the API but not the database; the DB has no published ports, so nobody on the internet can even try to connect to port 5432. This is how most Swiggy/Zomato-style microservice setups isolate data stores.

## 🟡 Real Example Hindi mein
आपके VPS पर: Nginx (public, ports 80/443), FastAPI (internal), Postgres (internal), Redis (internal)। आप दो networks बनाते हैं: `frontend` (nginx + api) और `backend` (api + db + redis)। Nginx API तक पहुँचता है पर database तक नहीं; DB का कोई port publish नहीं है, इसलिए internet से कोई 5432 पर try भी नहीं कर सकता। Swiggy/Zomato जैसे microservice setups में data stores ऐसे ही isolate होते हैं।

---

## 💻 Code / Config Example — Basic

```bash
# --- Basic network commands ---
docker network ls                                # list networks (bridge, host, none + yours)
docker network create appnet                     # create a user-defined bridge network
docker run -d --name db --network appnet \
  -e POSTGRES_PASSWORD=example_pass postgres:16  # db joins appnet, no ports published
docker run -d --name web --network appnet \
  -p 8080:80 nginx:1.27-alpine                   # publish container port 80 on host 8080
docker exec web getent hosts db                  # DNS check: name "db" resolves to an IP
docker network inspect appnet                    # see subnet, gateway, connected containers
docker network connect appnet other-container    # attach a running container later
docker network disconnect appnet other-container # detach it
docker network rm appnet                         # remove (fails if containers still attached)
docker network prune                             # remove all unused networks
```

## 💻 Code / Config Example — Advanced

```yaml
# docker-compose.yml - segmented networks: public edge, private backend
# Tags are examples; pin and update to your tested versions.
services:
  nginx:                                         # reverse proxy, only public entry point
    image: nginx:1.27-alpine                     # small official image
    restart: unless-stopped                      # survive reboots
    ports:
      - "80:80"                                  # publish HTTP to the world
      - "443:443"                                # publish HTTPS to the world
    volumes:
      - ./nginx/default.conf:/etc/nginx/conf.d/default.conf:ro  # proxy config, read-only
    networks:
      - frontend                                 # can talk to api only
  api:                                           # FastAPI service
    build: ./api                                 # build from local Dockerfile
    restart: unless-stopped
    expose:
      - "8000"                                   # documentation only: port used inside network
    environment:
      DATABASE_URL: postgresql://appuser:${DB_PASSWORD}@db:5432/appdb  # "db" is service DNS name
      REDIS_URL: redis://cache:6379/0            # "cache" resolves through Docker DNS
    networks:
      - frontend                                 # reachable by nginx
      - backend                                  # can reach db and cache
  db:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      POSTGRES_USER: appuser
      POSTGRES_DB: appdb
      POSTGRES_PASSWORD: ${DB_PASSWORD}          # from .env file (not committed to git)
    volumes:
      - pgdata:/var/lib/postgresql/data          # persistent DB files
    networks:
      - backend                                  # NOT on frontend, NOT published
  cache:
    image: redis:7-alpine
    restart: unless-stopped
    networks:
      backend:
        aliases:
          - redis                                # extra DNS name "redis" on backend
networks:
  frontend:                                      # nginx <-> api
    driver: bridge                               # default driver, explicit for clarity
  backend:                                       # api <-> db/cache
    driver: bridge
    internal: true                               # no outbound internet from this network
volumes:
  pgdata:
```

---

## 🟠 My Stack Integration
- **Nginx on VPS (in Docker)**: proxy to `http://api:8000`, using the service name, never `localhost` (localhost inside nginx container is nginx itself).
- **Nginx on the host (not Docker)**: proxy to `127.0.0.1:8000`, so publish the API as `127.0.0.1:8000:8000`, not `8000:8000`.
- **React**: build static files, serve through nginx; the browser calls `https://domain/api`, never the internal `api` name.
- **Node.js / FastAPI**: connect to db/redis by service name.
- **AWS**: Security Groups work on top: allow only 80/443 inbound on EC2. Docker's published ports bypass UFW, so firewall rules at Security Group level matter.

```yaml
# nginx/default.conf is plain nginx syntax (not YAML); this compose snippet binds API to host loopback
services:
  api:
    build: ./api
    ports:
      - "127.0.0.1:8000:8000"                    # reachable only from the VPS itself (host nginx)
    networks:
      - backend
networks:
  backend: {}                                    # default settings
```

Security: never publish DB ports (`5432:5432`) on a public VPS; if needed bind to `127.0.0.1`. Use `internal: true` for backend networks, one network per trust zone, and remember Docker adds iptables rules that bypass UFW for published ports.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `localhost` to reach another container.
✅ Correct: Use the service/container name (`db`, `api`) on a shared network.

❌ Mistake 2: Relying on the default `bridge` network and expecting DNS names.
✅ Correct: Create a user-defined network (Compose does this automatically).

❌ Mistake 3: Publishing `-p 5432:5432` or `-p 6379:6379` on a public server.
✅ Correct: Do not publish; keep it on the internal network, or bind `127.0.0.1:5432:5432` for admin access via SSH tunnel.

❌ Mistake 4: Putting services in different compose projects/networks and wondering why they cannot connect.
✅ Correct: Attach both to a shared `external: true` network.

---

## 🧠 Tricky Interview Question
UFW on your Ubuntu VPS denies port 8000, yet `curl http://VPS_IP:8000` reaches your container started with `-p 8000:8000`. Why?

Answer: Docker inserts its own iptables rules (DNAT in the `nat` table and rules in the `DOCKER` chain) that process traffic before UFW's rules, so UFW does not see it as ordinary INPUT traffic. Fix: bind to loopback (`127.0.0.1:8000:8000`), put filters in the `DOCKER-USER` chain, or block at the cloud Security Group.

---

## ⚫ Interview Questions + Answers

Q1: Difference between `EXPOSE` and `-p`?
A1: `EXPOSE` is only documentation of the port the app listens on. `-p host:container` actually publishes the port to the host. Containers on the same network can reach each other's ports without either.

Q2: How do containers find each other?
A2: Docker's embedded DNS server (127.0.0.11) on user-defined networks resolves container names, service names and network aliases to current IPs.

Q3: When would you use `--network host`?
A3: When you need maximum network performance or many ports without NAT, on Linux only. You lose isolation and port mapping; avoid for public-facing apps.

Q4: How do you let two compose projects talk to each other?
A4: Create a network with `docker network create shared`, then declare it in both files with `external: true` and attach services to it.

Q5: What does `internal: true` do?
A5: The network has no gateway to the outside, so containers on it cannot reach the internet and cannot be reached externally. Good for databases.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- More than one container needs to communicate.
- You want to separate public and private services.
- You want stable name-based service discovery.

❌ Avoid when:
- Host networking looks easier (it removes isolation; use only with a clear reason).
- Multi-host clusters: use overlay/Kubernetes networking instead of manual bridges.

---

## 📊 Visual Diagram
```
 Internet
    |  80/443 (published)
    v
 +---------+      frontend net       +---------+
 |  nginx  |------------------------>|   api   |
 +---------+                         +----+----+
                                          |  backend net (internal)
                          +---------------+---------------+
                          v                               v
                    +-----------+                   +-----------+
                    | db :5432  |                   | cache:6379|
                    | no ports  |                   | no ports  |
                    +-----------+                   +-----------+
 DNS: api -> 172.18.0.3, db -> 172.19.0.2 (Docker embedded DNS)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Bridge | Private virtual switch on one host | एक host पर private virtual switch |
| Host network | Share host network stack | Host का network stack share करना |
| Overlay | Multi-host network | कई hosts को जोड़ने वाला network |
| Embedded DNS | Docker's name resolver | Docker का नाम-से-IP resolver |
| Port publishing | Map host port to container port | Host port को container port से जोड़ना |
| Alias | Extra DNS name for a service | Service का अतिरिक्त DNS नाम |

---

## ⚡ 3-Line Summary
English: Docker networks connect containers with private IPs and built-in DNS names.
Use user-defined bridges and split public and private networks.
Publish only the ports that must be public; keep databases unpublished.
Hindi: Docker networks containers को private IP और built-in DNS नाम से जोड़ते हैं।
User-defined bridge इस्तेमाल करें और public/private networks अलग रखें।
सिर्फ वही ports publish करें जो public होने चाहिए; database को publish न करें।

---

## ➡️ Next Topic
**055. Installing Docker.** Now that you know the core concepts, install Docker Engine on your VPS and Docker on your laptop.

---
