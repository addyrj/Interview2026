# 185. networks Field
# हिंदी में: Compose का `networks` Field

---

## 🔵 Simple Definition (English)
The top-level `networks:` key declares the virtual networks that Compose creates for your project. Services join them with a service-level `networks:` list. Containers on the same network can reach each other by service name; containers on different networks cannot.

## 🔵 सरल परिभाषा (Hindi)
Top-level `networks:` key उन virtual networks को declare करती है जो Compose आपके project के लिए बनाता है। Services अपने `networks:` list से इनमें join होती हैं। एक ही network के containers service नाम से एक-दूसरे तक पहुँच सकते हैं; अलग networks के containers नहीं।

---

## 🔴 Problem it Solves
By default Compose puts ALL services on one `<project>_default` network, so your public nginx can talk to the database directly. If nginx gets compromised, the attacker is one hop away from Postgres. Also, you may need to attach to an existing network created by another stack (for example a shared Traefik or monitoring network). `networks:` gives you isolation (frontend vs backend), custom drivers/subnets, and the ability to join external networks.

## 🔴 यह क्यों बना? (Hindi)
Default रूप से Compose सभी services को एक ही `<project>_default` network पर रखता है, इसलिए public nginx सीधे database तक पहुँच सकता है। nginx compromise हुआ तो attacker Postgres से सिर्फ एक hop दूर है। कभी किसी दूसरे stack का बनाया network (जैसे shared Traefik या monitoring network) भी जोड़ना पड़ता है। `networks:` isolation (frontend बनाम backend), custom driver/subnet और external networks से जुड़ने की सुविधा देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Declare networks at top level: networks: { frontend: {}, backend: {} }.
Step 2 → Under each service list which networks it joins.
Step 3 → `docker compose up` creates them as <project>_<name> (shop_backend).
Step 4 → Docker's embedded DNS (127.0.0.11) resolves service names per network.
Step 5 → A service on two networks (api) bridges them; others stay isolated.
Step 6 → `docker compose down` removes the networks (unless external: true).
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Top level पर networks declare करें: networks: { frontend: {}, backend: {} }।
Step 2 → हर service के नीचे लिखें कि वह किन networks में है।
Step 3 → `docker compose up` उन्हें <project>_<name> नाम से बनाता है (shop_backend)।
Step 4 → Docker का embedded DNS (127.0.0.11) हर network में service नाम resolve करता है।
Step 5 → जो service दो networks में है (api) वह पुल बनती है; बाकी isolated रहते हैं।
Step 6 → `docker compose down` networks हटा देता है (external: true हों तो नहीं)।
```

---

## 🟡 Real World Example
A fintech-style dashboard on an EC2 instance: `nginx` is on `frontend` only; `api` is on `frontend` and `backend`; `postgres` and `redis` are on `backend` with `internal: true` so they cannot even reach the internet. A pen-test shows that a compromised nginx container cannot connect to `postgres:5432` because it does not share a network with it.

## 🟡 Real Example Hindi mein
EC2 instance पर fintech-style dashboard: `nginx` सिर्फ `frontend` पर; `api` `frontend` और `backend` दोनों पर; `postgres` और `redis` `backend` पर `internal: true` के साथ ताकि इंटरनेट तक भी न पहुँचें। Pen-test में दिखा कि compromised nginx container `postgres:5432` से connect नहीं कर सकता क्योंकि उनके बीच कोई साझा network नहीं।

---

## 💻 Code / Config Example — Basic

```yaml
services:                      # containers
  web:                         # frontend proxy
    image: nginx:1.27-alpine   # example tag
    networks:                  # networks this service joins
      - frontend               # only frontend
  api:                         # backend API
    image: node:20-alpine      # example tag
    command: node -e "setInterval(()=>{},1000)"   # placeholder process for demo
    networks:                  # joins both so it can bridge
      - frontend               # reachable from web
      - backend                # can reach db
  db:                          # database
    image: postgres:16-alpine  # example tag
    environment:               # required by postgres image
      POSTGRES_PASSWORD: example   # DEV ONLY
    networks:                  # only backend
      - backend                # web cannot reach it
networks:                      # declare networks
  frontend:                    # name
    driver: bridge             # single-host network driver (default)
  backend:                     # name
    driver: bridge             # same driver
```

## 💻 Code / Config Example — Advanced

```yaml
name: shop                     # project name
services:                      # containers
  nginx:                       # public entry
    image: nginx:1.27-alpine   # example tag
    ports: ["80:80"]           # only published port
    networks:                  # join frontend and shared proxy net
      frontend:                # long syntax lets us add options
        aliases:               # extra DNS names on this network
          - web.local          # nginx also answers to web.local
  api:                         # backend
    image: shop/api:2.1.0      # example image
    networks:                  # api bridges two networks
      frontend: {}             # reachable from nginx
      backend:                 # private network
        ipv4_address: 172.28.0.10   # fixed IP (needs ipam subnet below)
  db:                          # database
    image: postgres:16-alpine  # example tag
    environment:               # db config
      POSTGRES_PASSWORD: ${DB_PASSWORD:?required}   # fail if missing
    networks:                  # only backend
      - backend                # isolated
  monitor:                     # joins existing monitoring network
    image: prom/node-exporter:v1.8.1   # example tag
    networks:                  # external network
      - monitoring             # created outside this file
networks:                      # top-level definitions
  frontend:                    # public-facing network
    driver: bridge             # bridge driver
  backend:                     # private network
    driver: bridge             # bridge driver
    internal: true             # no outbound internet, no host access
    ipam:                      # IP address management
      config:                  # subnet list
        - subnet: 172.28.0.0/16   # must contain the fixed IP above
  monitoring:                  # network created by another stack
    external: true             # must already exist: docker network create monitoring
    name: monitoring           # real name on the host
```

Note: with `internal: true`, containers cannot pull data from the internet (for example the API calling Stripe). Put the api on an external-facing network too, as above.

---

## 🟠 My Stack Integration
Use two networks on your VPS: `edge` (nginx and api) and `data` (api, postgres, redis). FastAPI/Node workers sit on `data` only. Certbot or Cloudflare tunnel can use `edge`.

```yaml
services:                      # your VPS stack
  nginx:                       # TLS terminator
    image: nginx:1.27-alpine   # example tag
    ports: ["80:80", "443:443"]   # public
    networks: [edge]           # sees api only
  api:                         # FastAPI
    image: ghcr.io/addyrj/fastapi-app:1.4.2   # example image
    networks: [edge, data]     # talks to nginx and db
  postgres:                    # database
    image: postgres:16-alpine  # example tag
    environment:               # settings
      POSTGRES_PASSWORD_FILE: /run/secrets/db_pw   # read from secret file
    secrets: [db_pw]           # mount secret
    networks: [data]           # not reachable from nginx
networks:                      # networks
  edge: {}                     # public side
  data:                        # private side
    internal: true             # no internet egress
secrets:                       # file-based secret
  db_pw:                       # secret name
    file: ./secrets/db_pw.txt  # keep out of Git (.gitignore)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Everything on the default network, DB reachable from nginx.
✅ Correct: Separate `frontend`/`backend` networks and put the DB only in backend.

❌ Mistake 2: Marking the network `internal: true` and then wondering why `apt`, npm or external API calls fail.
✅ Correct: Keep services that need internet on a non-internal network too.

❌ Mistake 3: `external: true` for a network that does not exist yet.
✅ Correct: Run `docker network create <name>` first, or drop `external`.

❌ Mistake 4: Using container IPs in config.
✅ Correct: Use service names; IPs change on recreate.

---

## 🧠 Tricky Interview Question
"Two Compose projects both have a service named `db`. A container in project A connects to `db` and sometimes hits project B's database. Why?"

Answer: Both projects joined a shared external network (for example `shared`) and each `db` has the alias `db` on it. Docker DNS returns both containers in round-robin. Fix: give unique aliases or keep each stack's `db` only on its own private project network; use the shared network only for services that must be shared (proxy).

---

## ⚫ Interview Questions + Answers

Q1: What network does Compose create when you define none?
A1: A bridge network named `<project>_default`; all services join it.

Q2: How do containers resolve each other?
A2: Docker's embedded DNS server at 127.0.0.11 resolves service names and aliases within shared networks.

Q3: What does `internal: true` do?
A3: Blocks external connectivity: no outbound internet and no route from host to containers via that network.

Q4: `external: true`?
A4: Compose will not create or delete it; it must exist already (for cross-project sharing).

Q5: Do `ports:` matter for service-to-service traffic?
A5: No. Containers on the same network reach any container port directly; `ports:` is only for host access.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Isolating DB/cache from the public proxy.
- Sharing a reverse proxy/monitoring network across several stacks.

❌ Avoid when:
- Quick demo with 2 services (default network is fine).
- You need cross-host networking (needs overlay in Swarm, or Kubernetes).

---

## 📊 Visual Diagram
```
 Internet
    |
 [ nginx ] ---- frontend net ---- [ api ] ---- backend net (internal) ---- [ postgres ]
                                     |                                  \-- [ redis ]
   nginx cannot see postgres/redis   |
   (no shared network)               +-- bridges both networks
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| bridge | Default single-host driver | single host का default driver |
| internal | Network without outside access | बाहरी access बिना network |
| external | Pre-existing network | पहले से बना network |
| alias | Extra DNS name | अतिरिक्त DNS नाम |
| ipam | IP address management | IP पते प्रबंधन |

---

## ⚡ 3-Line Summary
English: `networks:` creates virtual networks and decides which services can talk.
English: Put DB/cache on a private (internal) network away from the public proxy.
English: Use service names, not IPs; use `external` to share networks across stacks.
Hindi: `networks:` virtual networks बनाता है और तय करता है कौन सी services बात कर सकती हैं।
Hindi: DB/cache को public proxy से दूर private (internal) network पर रखें।
Hindi: IP नहीं, service नाम use करें; stacks के बीच साझा करने के लिए `external` use करें।

---

## ➡️ Next Topic
186. volumes Field - networks cover connectivity; the top-level `volumes:` key covers persistent data.
