# 196. networks in Compose
# हिंदी में: Compose में Networks

---

## 🔵 Simple Definition (English)
A **network** in Docker Compose is a private virtual LAN that connects containers of your stack. Containers on the same network reach each other by **service name** (built-in DNS). Compose creates a default network per project, and the top-level `networks:` key lets you create custom ones to isolate tiers (frontend / backend / database).

## 🔵 सरल परिभाषा (Hindi)
Docker Compose में **network** एक private virtual LAN है जो आपके stack के containers को जोड़ता है। एक ही network पर containers एक-दूसरे को **service name** से बुला लेते हैं (built-in DNS)। Compose हर project के लिए एक default network बनाता है, और top-level `networks:` key से आप custom networks बना सकते हैं ताकि tiers (frontend / backend / database) अलग-अलग रहें।

---

## 🔴 Problem it Solves
Before networks, people used `--link` or hard-coded container IPs. IPs change on every restart, so configs broke. Also, if every container sits on one flat network, a hacked public web container can directly talk to your database. You need (1) stable name-based discovery and (2) isolation so only the services that must talk to each other can.

## 🔴 यह क्यों बना? (Hindi)
Networks से पहले लोग `--link` या hard-coded container IP इस्तेमाल करते थे। Restart पर IP बदल जाती है, इसलिए config टूट जाता था। और अगर सारे containers एक flat network पर हों तो hack हुआ public web container सीधे database से बात कर सकता है। ज़रूरत थी (1) name-based stable discovery और (2) isolation की ताकि सिर्फ वही services बात करें जिन्हें करनी चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → `docker compose up` reads the file and creates network "<project>_default" (bridge driver)
Step 2 → Every service without a `networks:` key is attached to that default network
Step 3 → Docker's embedded DNS (127.0.0.11) resolves service name -> container IP
Step 4 → If you declare custom networks, a service joins ONLY the networks listed under it
Step 5 → Containers on different networks cannot see each other (no DNS entry, no route)
Step 6 → `ports:` publishes a port to the HOST; container-to-container traffic never needs it
Step 7 → `docker compose down` removes the networks it created
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → `docker compose up` file पढ़कर "<project>_default" नाम का network (bridge driver) बनाता है
Step 2 → जिस service में `networks:` key नहीं है वह इसी default network से जुड़ती है
Step 3 → Docker का embedded DNS (127.0.0.11) service name को container IP में बदलता है
Step 4 → Custom networks declare करने पर service सिर्फ उन्हीं networks से जुड़ती है जो उसके नीचे लिखे हों
Step 5 → अलग networks के containers एक-दूसरे को नहीं देख सकते (न DNS, न route)
Step 6 → `ports:` HOST पर port publish करता है; container-to-container traffic को इसकी ज़रूरत नहीं
Step 7 → `docker compose down` अपने बनाए networks हटा देता है
```

---

## 🟡 Real World Example
Your **VPS** runs Nginx + a Node.js API + PostgreSQL. Only Nginx must be public. You create two networks: `public` (Nginx + API) and `private` (API + Postgres). Postgres is on `private` only, so even if someone exploits Nginx, there is no network path to the DB. Similar to how **Swiggy** keeps its payment DB in a private subnet in AWS VPC; Compose networks are the same idea on one host.

## 🟡 Real Example Hindi mein
आपके **VPS** पर Nginx + Node.js API + PostgreSQL चलते हैं। सिर्फ Nginx public होना चाहिए। आप दो networks बनाते हैं: `public` (Nginx + API) और `private` (API + Postgres)। Postgres सिर्फ `private` पर है, इसलिए Nginx exploit हो भी जाए तो DB तक कोई network path नहीं। जैसे **Swiggy** अपना payment DB AWS VPC के private subnet में रखता है; Compose networks वही idea एक host पर हैं।

---

## 💻 Code / Config Example — Basic

```yaml
# docker-compose.yml  (Compose Specification, no "version:" key needed in v2)
services:                     # all containers of the stack live under this key
  api:                        # service name; also its DNS hostname on the network
    image: node:20-alpine     # example image tag, update to the version you use
    command: ["node", "-e", "require('http').createServer((q,r)=>r.end('ok')).listen(3000)"]  # tiny HTTP server
    ports:
      - "3000:3000"           # publish host:container so you can curl from your laptop
  cache:                      # second service, no `networks:` key
    image: redis:7-alpine     # example tag
    # no ports published: only other containers can reach it
# No top-level `networks:` is declared, so Compose auto-creates "<project>_default"
# and attaches BOTH services to it. Inside api you can reach Redis at host "cache", port 6379.
```

```bash
docker compose up -d                       # start stack (creates the default network)
docker network ls                          # you will see <folder>_default
docker compose exec api sh -c "nc -zv cache 6379"   # DNS lookup of "cache" works from api
```

## 💻 Code / Config Example — Advanced

```yaml
# docker-compose.yml : 3-tier isolation with custom networks
services:
  nginx:
    image: nginx:1.27-alpine            # reverse proxy, the only public entry point
    ports:
      - "80:80"                         # publish HTTP to the VPS
      - "443:443"                       # publish HTTPS
    volumes:
      - ./nginx/default.conf:/etc/nginx/conf.d/default.conf:ro  # proxy_pass http://api:3000
    networks:
      - frontend                        # can talk to api only through this network
    depends_on:
      - api                             # start order hint
  api:
    build: ./api                        # Node.js / FastAPI image built from ./api/Dockerfile
    environment:
      DB_HOST: db                       # service name used as hostname (Docker DNS)
      REDIS_HOST: cache                 # same for Redis
    networks:
      frontend:                         # long syntax lets us add per-network options
        aliases:
          - backend-api                 # extra DNS name usable on THIS network
      backend: {}                       # api bridges both networks (empty map = defaults)
  db:
    image: postgres:16-alpine           # database
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_pw   # read password from a secret file, not env text
    secrets:
      - db_pw
    networks:
      - backend                         # ONLY backend: nginx can never reach it
  cache:
    image: redis:7-alpine
    networks:
      - backend                         # private too
networks:
  frontend:                             # public-facing tier
    driver: bridge                      # default driver on a single host
  backend:
    driver: bridge
    internal: true                      # no outbound internet and no external access at all
    # Caveat: internal:true also blocks the api's outbound calls ONLY on this network;
    # api still reaches the internet through "frontend". Verify with your own tests.
  # shared with another compose project example (must already exist):
  # shared:
  #   external: true                    # created beforehand via `docker network create shared`
  #   name: shared-net                  # actual docker name of the external network
secrets:
  db_pw:
    file: ./secrets/db_pw.txt           # keep this file out of git (.gitignore)
```

---

## 🟠 My Stack Integration
- **Node.js / FastAPI**: connect to Postgres with host `db`, never `localhost` (inside a container `localhost` is the container itself).
- **Nginx**: `proxy_pass http://api:3000;` works only if nginx and api share a network.
- **React**: the built static files are served by nginx; browser calls `/api`, nginx forwards to `api`. The browser never touches the Docker network.
- **VPS / AWS EC2**: open only 80/443 in the security group; DB/Redis have no `ports:` at all.

```yaml
# Snippet for your VPS stack
services:
  fastapi:
    build: ./fastapi
    networks: [frontend, backend]     # talks to nginx and to db
  postgres:
    image: postgres:16-alpine
    networks: [backend]               # invisible to nginx
networks:
  frontend: {}                        # empty map = default bridge settings
  backend:
    internal: true                    # isolated tier
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `localhost` or `127.0.0.1` to reach another service.
✅ Correct: Use the service name (`db`, `cache`). `localhost` is the container itself.

❌ Mistake 2: Publishing DB ports (`5432:5432`) "for convenience" on a public VPS.
✅ Correct: Remove `ports:` for DB; use `docker compose exec db psql` or bind to loopback `127.0.0.1:5432:5432`.

❌ Mistake 3: Putting a service on a custom network and forgetting it also needs `default`.
✅ Correct: Once you set `networks:` on a service, it no longer joins `default`. List every network it needs.

❌ Mistake 4: Hard-coding the generated network name (`myproj_default`) in other tools.
✅ Correct: Use a fixed `name:` on the network, or `external: true` for cross-project sharing.

---

## 🧠 Tricky Interview Question
Your `api` is on `frontend` and `backend`. Nginx (frontend only) resolves `db`. What happens?

Answer: `db` is not resolvable by nginx. Docker DNS answers only for names on a network the asking container is attached to. Nginx gets "host not found". That is by design; it is exactly the isolation you wanted. If nginx needs it, you are leaking the DB tier; route through the api instead.

---

## ⚫ Interview Questions + Answers

Q1: How do containers find each other in Compose?
A1: Embedded DNS at 127.0.0.11 resolves service names (and aliases) to container IPs, only within shared networks.

Q2: Default network driver on one host?
A2: `bridge`. Across multiple hosts you need `overlay` (Swarm) or Kubernetes networking.

Q3: Difference between `ports` and `expose`?
A3: `ports` publishes to the host. `expose` only documents/opens a port between containers; with user-defined networks all ports are already reachable, so `expose` is mostly informational.

Q4: What does `internal: true` do?
A4: Network has no gateway to outside; containers on it cannot reach the internet and the host cannot publish to it.

Q5: What is `external: true`?
A5: Compose will not create the network; it must already exist (`docker network create`). Useful to share one network between several compose projects.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You want DB/Redis hidden from the public tier.
- Multiple compose projects must share one proxy network (Traefik / nginx-proxy).
- You need aliases or static IPAM subnets.

❌ Avoid when:
- A tiny two-container dev stack: the default network is enough.
- You need host-level performance tests (`network_mode: host` is a different thing; Linux only).

---

## 📊 Visual Diagram
```
                Internet
                   |
             [ VPS :80/:443 ]
                   |
   +-------- frontend network --------+
   |   [ nginx ] ----- [ api ] -----+ |
   +--------------------------------|-+
                                    |
   +-------- backend (internal) ----|-+
   |       [ api ] ---- [ db ]        |
   |                 \--- [ cache ]   |
   +----------------------------------+
   nginx --X--> db   (no shared network = no DNS, no route)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| bridge | Default single-host network driver | डिफ़ॉल्ट single-host network driver |
| alias | Extra DNS name for a service on a network | नेटवर्क पर service का अतिरिक्त नाम |
| internal | Network with no outside access | बाहर से कटा हुआ network |
| external | Pre-existing network not managed by Compose | पहले से बना network |
| embedded DNS | Docker's resolver at 127.0.0.11 | Docker का built-in DNS |

---

## ⚡ 3-Line Summary
English: Compose gives every project a private network with name-based DNS.
Custom `networks:` isolate tiers so only needed services can talk.
Never use localhost between containers and never publish DB ports publicly.
Hindi: Compose हर project को name-based DNS वाला private network देता है।
Custom `networks:` से tiers अलग होते हैं ताकि सिर्फ ज़रूरी services बात करें।
Containers के बीच localhost कभी नहीं और DB ports public कभी publish न करें।

---

## ➡️ Next Topic
**197. profiles in Compose**: now that services are wired together, profiles let you start only some of them (debug tools, workers) on demand.
