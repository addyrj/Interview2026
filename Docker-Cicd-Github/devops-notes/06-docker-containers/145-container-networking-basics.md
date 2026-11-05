---

# 145. Container Networking Basics
# हिंदी में: Container Networking की बुनियादी बातें

---

## 🔵 Simple Definition (English)
Container networking decides **how containers talk to each other, to the host, and to the internet**. Each container gets its own network namespace (own IP, own ports). Docker connects it to a virtual network (a **bridge** by default) and uses NAT and `-p` port publishing to let the outside world reach it.

## 🔵 सरल परिभाषा (Hindi)
Container networking तय करती है कि **containers आपस में, host से और internet से कैसे बात करें**। हर container का अपना network namespace होता है (अपना IP, अपने ports)। Docker उसे एक virtual network (default में **bridge**) से जोड़ता है और NAT व `-p` port publishing से बाहर की दुनिया को पहुँच देता है।

---

## 🔴 Problem it Solves
Before this, apps on one server fought over ports (two Node apps cannot both use 3000) and shared one IP. Containers need isolation (the DB must not be open to the internet) but also controlled connectivity (the API must reach the DB). Docker networks give each app its own IP, private networks per project, and explicit publishing of only the ports you want public.

## 🔴 यह क्यों बना? (Hindi)
पहले एक server पर सारे apps ports के लिए लड़ते थे (दो Node apps दोनों 3000 नहीं ले सकते) और एक ही IP share करते थे। Containers को isolation चाहिए (DB internet पर खुला न हो) और साथ में नियंत्रित connectivity भी (API को DB तक पहुँचना है)। Docker networks हर app को अपना IP, हर project को private network और सिर्फ चुने हुए ports को public करने की सुविधा देते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Docker daemon starts, creates default bridge "docker0" (172.17.0.0/16)
Step 2 → docker run creates container + its own network namespace
Step 3 → A veth pair (virtual cable) links container eth0 <-> bridge
Step 4 → Container gets an IP from the network's subnet (e.g. 172.18.0.2)
Step 5 → Outbound traffic: container -> bridge -> iptables MASQUERADE -> internet
Step 6 → Inbound traffic: -p 8080:3000 adds DNAT rule host:8080 -> container:3000
Step 7 → Containers on the SAME user-defined network reach each other by name
```

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Docker daemon शुरू होते ही default bridge "docker0" (172.17.0.0/16) बनाता है।
Step 2 → `docker run` container और उसका अपना network namespace बनाता है।
Step 3 → एक veth pair (virtual cable) container के eth0 को bridge से जोड़ता है।
Step 4 → Container को network की subnet से IP मिलता है (जैसे 172.18.0.2)।
Step 5 → बाहर जाने वाला traffic: container -> bridge -> iptables MASQUERADE -> internet।
Step 6 → अंदर आने वाला traffic: `-p 8080:3000` एक DNAT rule जोड़ता है host:8080 -> container:3000।
Step 7 → **एक ही user-defined network** के containers एक-दूसरे को नाम से पहुँच सकते हैं।

Network drivers: **bridge** (default, single host), **host** (share host network), **none** (no network), **overlay** (multi-host, Swarm), **macvlan** (container gets its own MAC/LAN IP).

---

## 🟡 Real World Example
On your VPS you run Nginx, a Node.js API and PostgreSQL. Only Nginx publishes ports 80/443. The API and DB sit on a private network `backend`. The internet can reach Nginx only; the DB has no published port at all. Swiggy-style systems follow the same idea: public edge, private services.

## 🟡 Real Example Hindi mein
आपके VPS पर Nginx, Node.js API और PostgreSQL चलते हैं। सिर्फ Nginx port 80/443 publish करता है। API और DB एक private network `backend` पर हैं। Internet सिर्फ Nginx तक पहुँचता है; DB का कोई published port ही नहीं है। Swiggy जैसे systems में भी यही idea होता है: public edge, private services।

---

## 💻 Code / Config Example — Basic
```bash
# Create a user-defined bridge network (gives DNS by container name)
docker network create appnet                      # new bridge network called appnet

# Run a database on it, with NO published port (private)
docker run -d --name db --network appnet \
  -e POSTGRES_PASSWORD=example \
  postgres:16-alpine                              # example tag; pin and update yourself

# Run an API on the same network, publish only 3000 to the host
docker run -d --name api --network appnet \
  -p 3000:3000 \
  -e DATABASE_URL=postgres://postgres:example@db:5432/postgres \
  myorg/api:1.0.0                                 # "db" resolves via Docker DNS

# Inspect the network: subnet, gateway, attached containers
docker network inspect appnet

# Show the IP of one container
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' api

# Show published port mappings
docker port api                                   # prints 3000/tcp -> 0.0.0.0:3000
```

## 💻 Code / Config Example — Advanced
```yaml
# docker-compose.yml - two networks: public edge and private backend
services:
  nginx:
    image: nginx:1.27-alpine            # example tag
    ports:
      - "80:80"                         # public HTTP
      - "443:443"                       # public HTTPS
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro  # read-only config
    networks:
      - edge                            # talks to the internet side
      - backend                         # and to the API
    depends_on:
      - api                             # start order only (not readiness)
  api:
    build: ./api                        # Node.js or FastAPI Dockerfile
    expose:
      - "3000"                          # documents the port; NOT published to host
    environment:
      DATABASE_URL: postgres://app:${DB_PASSWORD}@db:5432/app  # "db" is the service name
    networks:
      - backend                         # private network only
  db:
    image: postgres:16-alpine           # example tag
    environment:
      POSTGRES_USER: app                # DB user
      POSTGRES_PASSWORD: ${DB_PASSWORD} # from .env file, never hardcode
      POSTGRES_DB: app                  # DB name
    volumes:
      - dbdata:/var/lib/postgresql/data # persist data
    networks:
      - backend                         # NOT on edge, NOT published
networks:
  edge:
    driver: bridge                      # normal bridge network
  backend:
    driver: bridge
    internal: true                      # no route to internet: DB and API cannot call out
volumes:
  dbdata: {}                            # named volume
```
Note: with `internal: true` the API also cannot call external APIs. If your API needs outbound internet (payment gateway), attach it to a non-internal network too. Compose syntax verified by YAML parse only; not run locally.

---

## 🟠 My Stack Integration
- **React**: build static files, serve from Nginx container; browser calls `/api` on the same origin, so no CORS or extra port.
- **Node.js / FastAPI**: never publish 3000/8000 on the VPS public IP. Let Nginx proxy to `http://api:3000`.
- **VPS / AWS**: allow only 80/443 (and SSH from your IP) in the Security Group. Remember Docker edits iptables itself and **bypasses UFW**, so a `-p 5432:5432` is public even if UFW says deny.
- If you must publish something on the host only, use `-p 127.0.0.1:5432:5432`.

```yaml
# Safe publishing patterns
ports:
  - "127.0.0.1:9090:9090"   # only reachable from the VPS itself (use SSH tunnel)
  - "80:80"                 # public on purpose (Nginx)
# "5432:5432" would expose Postgres to the whole internet - avoid
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `localhost` inside a container to reach another container.
✅ Correct: `localhost` is the container itself. Use the service name (`db`) on a shared network.

❌ Mistake 2: Publishing the DB port to "test with a GUI" and forgetting it.
✅ Correct: Bind to `127.0.0.1` and use an SSH tunnel; remove it after.

❌ Mistake 3: Relying on the default `bridge` network for name resolution.
✅ Correct: Default bridge has no DNS by name. Create a user-defined network (Compose does this automatically).

❌ Mistake 4: Trusting UFW to block Docker ports.
✅ Correct: Use the `DOCKER-USER` iptables chain, bind to 127.0.0.1, or use the cloud Security Group.

---

## 🧠 Tricky Interview Question
Two containers run on the same host with `docker run` (no `--network`). `ping db` fails from `api`, but pinging its IP works. Why?

Answer: Both are on the **default bridge**, which has no embedded DNS for container names (only legacy `--link`). Create a user-defined bridge (`docker network create appnet`) and attach both; then Docker's DNS server at 127.0.0.11 resolves names. IPs also change on restart, so never hardcode them.

---

## ⚫ Interview Questions + Answers

Q1: What are Docker's default network drivers?
A1: `bridge`, `host`, `none` exist by default; `overlay` and `macvlan` are created by you. Compose projects get their own bridge.

Q2: `EXPOSE` vs `-p`?
A2: `EXPOSE` is only documentation/metadata. `-p host:container` actually publishes the port via DNAT.

Q3: How does a container reach the internet?
A3: Through the bridge, with iptables MASQUERADE (source NAT) using the host's IP.

Q4: How does a container reach a service running on the host?
A4: Use the bridge gateway IP (e.g. 172.17.0.1) or `host.docker.internal` (Docker Desktop; on Linux add `--add-host=host.docker.internal:host-gateway`).

Q5: What is a veth pair?
A5: A virtual Ethernet cable with two ends: one in the container's namespace (eth0), the other attached to the bridge on the host.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Multiple services in one project need private communication (bridge).
- You want separation of tiers (edge vs backend networks).

❌ Avoid when:
- You need multi-host networking: use overlay (Swarm) or Kubernetes CNI instead of plain bridge.
- You need maximum network speed with zero NAT: consider host network (next topics).

---

## 📊 Visual Diagram
```
 Internet
    |  :443
+---v--------------------- VPS (host) ---------------------+
|  iptables DNAT 443 -> nginx:443                           |
|                                                           |
|   [ edge network 172.18.0.0/16 ]                          |
|        nginx (172.18.0.2)                                 |
|           |                                               |
|   [ backend network 172.19.0.0/16 ]                       |
|        nginx (172.19.0.2)---api (172.19.0.3)---db (.4)    |
|                                                           |
|  db has NO published port => unreachable from internet    |
+-----------------------------------------------------------+
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Bridge | Virtual switch connecting containers on one host | एक host के containers को जोड़ने वाला virtual switch |
| veth | Virtual cable pair between namespaces | Namespaces के बीच virtual cable |
| NAT | Rewriting addresses to share one public IP | Address बदलकर एक public IP share करना |
| Port publishing | Map host port to container port | Host port को container port से जोड़ना |
| Network namespace | Isolated network stack per container | हर container का अलग network stack |
| Overlay | Multi-host virtual network | कई hosts पर फैला virtual network |

---

## ⚡ 3-Line Summary
English: Each container has its own IP; a bridge network connects them on one host.
Use user-defined networks for name-based access and publish only the ports you need.
Docker bypasses UFW, so bind sensitive ports to 127.0.0.1.
Hindi: हर container का अपना IP होता है; bridge network उन्हें एक host पर जोड़ता है।
नाम से access के लिए user-defined network लो और सिर्फ ज़रूरी ports publish करो।
Docker UFW को bypass करता है, इसलिए संवेदनशील ports 127.0.0.1 पर bind करो।

---

## ➡️ Next Topic
**146. Container DNS** - we saw names like `db` resolve magically; next we see exactly how Docker's embedded DNS works.
