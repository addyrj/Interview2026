# 178. Network Isolation
# हिंदी में: Network Isolation (नेटवर्क अलगाव)

---

## 🔵 Simple Definition (English)
**Network isolation** means placing containers on separate Docker networks so that only the containers that must talk to each other can do so. Everything else is blocked by default. It limits what an attacker can reach after compromising one container.

## 🔵 सरल परिभाषा (Hindi)
**Network isolation** का मतलब है containers को अलग-अलग Docker networks पर रखना ताकि सिर्फ वही containers बात कर सकें जिन्हें करनी है। बाकी सब default में blocked। अगर एक container compromise हो जाए तो attacker कितना आगे पहुँच सकता है, यह इससे सीमित होता है।

---

## 🔴 Problem it Solves
If all containers share one flat network, a vulnerability in your public web server gives the attacker a straight line to your database, Redis (often without password) and admin tools. This "flat network" design caused many real breaches (exposed Redis/Mongo instances). Isolation applies the principle of least privilege to networking.

## 🔴 यह क्यों बना? (Hindi)
अगर सारे containers एक ही flat network पर हों, तो public web server की एक कमज़ोरी attacker को सीधे database, Redis (अक्सर बिना password) और admin tools तक पहुँचा देती है। इसी "flat network" design से कई real breaches हुए (खुले Redis/Mongo instances)। Isolation networking में least privilege लागू करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Draw the allowed communication graph (who must talk to whom)
Step 2 → Create one network per trust zone: frontend, backend, data
Step 3 → Attach each service ONLY to the zones it needs (api joins two, db joins one)
Step 4 → Docker iptables rules drop traffic between different networks
Step 5 → Mark sensitive networks internal: true (no internet egress, no host access)
Step 6 → Publish ports only on the edge service (nginx), bind others to 127.0.0.1
Step 7 → Verify with docker exec ... nc/curl that blocked paths really fail
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Allowed communication का graph बनाओ (किसे किससे बात करनी है)
Step 2 → हर trust zone के लिए एक network: frontend, backend, data
Step 3 → हर service को सिर्फ ज़रूरी zones से जोड़ो (api दो में, db एक में)
Step 4 → Docker iptables rules अलग networks के बीच traffic drop करते हैं
Step 5 → Sensitive networks को internal: true करो (internet egress नहीं, host access नहीं)
Step 6 → Port सिर्फ edge service (nginx) पर publish करो, बाकी 127.0.0.1 पर bind
Step 7 → docker exec ... nc/curl से जाँचो कि blocked paths सच में fail होते हैं
```

---

## 🟡 Real World Example
A fintech startup runs a payments API and a marketing blog on the same AWS EC2 instance. The WordPress blog gets hacked through an outdated plugin. Because the blog is on `public_net` only and the payments DB lives on an `internal` `data_net` joined only by the payments API, the attacker cannot reach the DB or the payment service. Without isolation the same hack would have leaked card tokens.

## 🟡 Real Example Hindi mein
एक fintech startup एक ही AWS EC2 पर payments API और marketing blog चलाती है। पुराने plugin से WordPress blog hack हो जाता है। क्योंकि blog सिर्फ `public_net` पर है और payments DB `internal` `data_net` पर है जिससे सिर्फ payments API जुड़ा है, attacker DB या payment service तक नहीं पहुँच पाया। Isolation न होता तो वही hack card tokens leak कर देता।

---

## 💻 Code / Config Example — Basic
```yaml
# docker-compose.yml - two projects' worth of services, isolated by networks
services:
  web:
    image: nginx:1.27-alpine           # example tag; public edge
    ports:
      - "80:80"                        # only published port
    networks:
      - public_net                     # can talk to api only
  api:
    image: myorg/api:1.4.2             # Node.js / FastAPI
    networks:
      - public_net                     # reachable by web
      - data_net                       # can reach db
  db:
    image: postgres:16-alpine          # example tag
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}  # injected from .env
    networks:
      - data_net                       # ONLY here: web cannot reach it
networks:
  public_net: {}                       # edge zone
  data_net:
    internal: true                     # no internet, no host route
```

## 💻 Code / Config Example — Advanced
```yaml
# docker-compose.prod.yml - three zones, least privilege, hardened
services:
  nginx:
    image: nginx:1.27-alpine
    ports:
      - "80:80"
      - "443:443"                      # TLS terminated here
    networks: [edge]                   # edge zone only
    read_only: true                    # immutable FS
    tmpfs: [/var/cache/nginx, /var/run]  # nginx needs writable cache/pid
    cap_drop: [ALL]                    # drop all capabilities
    cap_add: [NET_BIND_SERVICE, CHOWN, SETUID, SETGID]  # minimum nginx needs; test in staging
    security_opt: ["no-new-privileges:true"]
  api:
    image: myorg/api:1.4.2
    networks: [edge, app]              # bridge between zones
    environment:
      DATABASE_URL: postgres://app:${DB_PASSWORD}@db:5432/app
      REDIS_URL: redis://:${REDIS_PASSWORD}@cache:6379
  worker:
    image: myorg/worker:1.4.2          # background jobs
    networks: [app]                    # never exposed to edge
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes: [pgdata:/var/lib/postgresql/data]
    networks: [app]                    # internal zone
  cache:
    image: redis:7-alpine
    command: ["redis-server", "--requirepass", "${REDIS_PASSWORD}"]  # auth even inside the network
    networks: [app]
networks:
  edge: {}                             # internet-facing zone
  app:
    internal: true                     # backend zone cannot reach internet or host
volumes:
  pgdata: {}
```

```bash
# verify isolation (from the host, after docker compose up -d)
docker compose exec nginx sh -c 'nc -zv -w2 db 5432' || echo "BLOCKED as expected"   # nginx must NOT reach db
docker compose exec api   sh -c 'nc -zv -w2 db 5432' && echo "api -> db OK"          # api must reach db
```

---

## 🟠 My Stack Integration
- **React + Nginx + Node API + Mongo:** zones `edge` (nginx, api) and `app` (api, mongo). Mongo never joins `edge`.
- **FastAPI + Celery + Redis:** worker and redis on an `internal` network; only the API also joins the edge.
- **Admin tools (pgAdmin, mongo-express):** put them on their own network and bind to `127.0.0.1`, access via SSH tunnel: `ssh -L 5050:127.0.0.1:5050 user@vps`.
- **VPS/AWS:** isolation inside Docker complements security groups; do both. The EC2 metadata IP is blocked from `internal` networks because they have no egress.
- **Egress control:** `internal: true` also blocks the backend from calling external APIs. If your worker must call Stripe, give it a separate non-internal network.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: One default network for everything.
✅ Correct: Split by trust zone, using multiple networks in Compose.

❌ Mistake 2: Marking the network `internal: true` that the API uses for outbound calls (Stripe, SMTP); the API then cannot reach the internet.
✅ Correct: Keep a non-internal network for services needing egress.

❌ Mistake 3: Believing isolation replaces authentication.
✅ Correct: Still set DB/Redis passwords; defence in depth.

❌ Mistake 4: Publishing DB ports for "just debugging" and forgetting.
✅ Correct: Use `127.0.0.1:` binding or `docker compose exec db psql`.

---

## 🧠 Tricky Interview Question
**Q:** You put the DB on an `internal: true` network and attach the API to both `edge` and that network. A user finds the app can still call out to the internet from the API. Is isolation broken?

**Answer:** No. `internal` only affects containers whose ONLY (or relevant) path is that network. The API is also on `edge` (non-internal), so it has a default route and internet access via that network. Isolation is about reachability of the DB, not about the API's egress. If you want the API restricted too, remove it from egress networks and use a proxy or firewall rules in the `DOCKER-USER` chain.

---

## ⚫ Interview Questions + Answers

Q1: How does Docker isolate networks?
A1: Each user-defined bridge has its own subnet and iptables rules that drop forwarding between different bridges.

Q2: What does `internal: true` do?
A2: Removes the gateway/NAT, so the network has no external or host access.

Q3: How can one container be in two networks?
A3: List both under `networks:` in Compose or use `docker network connect`.

Q4: How do you restrict outbound traffic of a container?
A4: Use an internal network plus an egress proxy, or iptables rules in `DOCKER-USER`.

Q5: Is Docker network isolation enough for multi-tenant hosting of untrusted code?
A5: No; containers share a kernel. Use VMs (Firecracker/gVisor) for hostile tenants.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You host a DB, cache and public web tier together
- Several client projects share one VPS
- Compliance asks for segmented networks

❌ Avoid when:
- A single tiny container with nothing to protect (little benefit)
- Over-segmentation that makes debugging impossible without documentation

---

## 📊 Visual Diagram
```
 Internet
    |
 +--v-----------------------------+
 | EDGE net:   [nginx]--[api]     |
 +-------------------|------------+
                     |
 +-------------------v------------+  internal: true
 | APP net:   [api] [worker]      |  (no internet, no host)
 |              |       |         |
 |           [db]    [cache]      |
 +--------------------------------+
 nginx --X--> db   (different networks: dropped)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Trust zone | Group with same trust level | भरोसे का क्षेत्र |
| Internal network | Network without external access | बंद नेटवर्क |
| Flat network | Everything can reach everything | खुला एक-जैसा नेटवर्क |
| Egress | Outbound traffic | बाहर जाने वाला |
| Defence in depth | Multiple security layers | कई परतों की सुरक्षा |
| DOCKER-USER | iptables chain for custom rules | custom firewall chain |

---

## ⚡ 3-Line Summary
English: Isolation = separate networks per trust zone so only needed paths exist.
Use `internal: true` for backend networks and publish only the edge.
It limits damage after a breach but does not replace passwords.
Hindi: Isolation = हर trust zone के लिए अलग network ताकि सिर्फ ज़रूरी रास्ते रहें।
Backend networks पर `internal: true` और सिर्फ edge publish करो।
Breach के बाद नुकसान सीमित होता है, पर passwords की जगह नहीं लेता।

---

## ➡️ Next Topic
**179. Docker Network Commands** - the CLI toolbox to create, inspect, connect and debug all these networks.
