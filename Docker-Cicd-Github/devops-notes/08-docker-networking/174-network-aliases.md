# 174. Network Aliases
# हिंदी में: Network Aliases (container के अतिरिक्त DNS नाम)

---

## 🔵 Simple Definition (English)
A **network alias** is an extra DNS name for a container, valid **only on one specific network**. The same container can have different aliases on different networks, and several containers may share an alias so DNS returns all of them.

## 🔵 सरल परिभाषा (Hindi)
**Network alias** container का अतिरिक्त DNS नाम है जो **सिर्फ एक खास network पर** मान्य होता है। एक ही container के अलग networks पर अलग aliases हो सकते हैं, और कई containers एक ही alias साझा कर सकते हैं ताकि DNS सबको लौटाए।

---

## 🔴 Problem it Solves
Applications are configured with fixed hostnames (`mysql.internal`, `cache`, `api.local`) that differ from your container names. Renaming containers or editing app config for each environment is painful. Also during migrations you want `db` to point to the new Postgres without touching clients, or want a blue/green switch. Aliases decouple the **name clients use** from the **container's real name**.

## 🔴 यह क्यों बना? (Hindi)
Applications में fixed hostnames (`mysql.internal`, `cache`, `api.local`) configure होते हैं जो आपके container नामों से अलग हैं। हर environment के लिए container rename करना या app config बदलना दर्दनाक है। Migration में आप चाहते हैं कि `db` नया Postgres point करे और clients को छूना न पड़े, या blue/green switch करना हो। Alias **clients का इस्तेमाल किया नाम** और **container का असली नाम** अलग कर देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Attach container to a user-defined network with --network-alias (or aliases: in Compose)
Step 2 → Docker registers alias -> container IP in that network's embedded DNS
Step 3 → Any container on the SAME network resolving the alias gets the IP
Step 4 → If 2+ containers share the alias, DNS returns all IPs (round-robin order)
Step 5 → Container on another network does not see the alias (alias is per-network)
Step 6 → Remove/recreate container -> alias disappears with it; no stale config
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Container को user-defined network से --network-alias (या Compose में aliases:) के साथ जोड़ो
Step 2 → Docker उस network के embedded DNS में alias -> container IP दर्ज करता है
Step 3 → उसी network का कोई भी container alias resolve करे तो IP मिलता है
Step 4 → 2+ containers एक alias साझा करें तो DNS सभी IPs लौटाता है (round-robin क्रम)
Step 5 → दूसरे network का container alias नहीं देखता (alias per-network है)
Step 6 → Container हटाओ/दोबारा बनाओ -> alias उसके साथ चला जाता है; पुराना config नहीं बचता
```

---

## 🟡 Real World Example
A legacy PHP billing app has `DB_HOST=mysql-primary` baked in. You are moving from a MySQL container named `mysql57` to `mysql80`. Give the new container `--network-alias mysql-primary`, stop the old one, and the app keeps working with no code change. In Compose-based stacks the same trick gives you `api` as alias on the `frontend` net and `backend-api` on the `internal` net for the same container.

## 🟡 Real Example Hindi mein
एक पुरानी PHP billing app में `DB_HOST=mysql-primary` बना हुआ है। आप MySQL container `mysql57` से `mysql80` पर जा रहे हैं। नए container को `--network-alias mysql-primary` दो, पुराना बंद करो, और app बिना code बदले चलती रहती है। Compose stacks में यही trick एक container को `frontend` net पर `api` और `internal` net पर `backend-api` alias देती है।

---

## 💻 Code / Config Example — Basic
```bash
docker network create app-net                                   # user-defined bridge

# Container named mysql80 but reachable as "mysql-primary" and "db"
docker run -d --name mysql80 --network app-net \
  --network-alias mysql-primary \
  --network-alias db \
  -e MYSQL_ROOT_PASSWORD=change-me \
  mysql:8.0                                                     # example tag

# Both names resolve to the same IP
docker run --rm --network app-net alpine:3.20 nslookup mysql-primary
docker run --rm --network app-net alpine:3.20 nslookup db

# Aliases when connecting an existing container to another network
docker network create admin-net
docker network connect --alias dbadmin admin-net mysql80        # alias only on admin-net

# See aliases for the container on each network
docker inspect -f '{{json .NetworkSettings.Networks}}' mysql80
```

## 💻 Code / Config Example — Advanced
```yaml
# docker-compose.yml - per-network aliases + shared alias for blue/green switch
services:
  api-blue:
    image: myrepo/api:1.4.0               # currently serving version (example)
    networks:
      edge:
        aliases:
          - api                           # nginx proxies to http://api:3000
      internal:
        aliases:
          - backend-api                   # worker calls http://backend-api:3000
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:3000/health"]   # container health
      interval: 10s                       # check every 10 seconds
      timeout: 3s                         # fail if no reply in 3s
      retries: 3                          # unhealthy after 3 failures

  api-green:
    image: myrepo/api:1.5.0               # new version being validated
    profiles: ["green"]                   # only started with --profile green
    networks:
      edge:
        aliases:
          - api-next                      # test route: http://api-next:3000
      internal: {}                        # no alias yet

  nginx:
    image: nginx:1.27-alpine              # example tag
    ports: ["80:80"]                      # public port
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro   # mounted read-only
    networks: [edge]                      # sees alias "api" only through edge

  worker:
    image: myrepo/worker:1.4.0
    environment:
      API_URL: http://backend-api:3000    # uses the internal-only alias
    networks: [internal]

networks:
  edge: {}                                # frontend network
  internal:
    internal: true                        # no internet egress
```
```bash
# Cut over: after green is healthy, move the "api" alias by recreating with swapped aliases
docker compose --profile green up -d api-green        # start green
docker network disconnect <proj>_edge <api-green-id>  # detach to re-attach with new alias
docker network connect --alias api <proj>_edge <api-green-id>   # green now answers "api"
docker compose stop api-blue                           # retire blue
```

---

## 🟠 My Stack Integration
- **Nginx upstream**: `proxy_pass http://api:3000;` works whether the real service is `node-api`, `api-v2` or `fastapi`.
- **Node.js / FastAPI**: keep connection strings environment-neutral (`DB_HOST=db`) and let aliases map them in each environment (dev: sqlite-less Postgres container, prod: also alias `db` to a proxy container for RDS).
- **AWS RDS**: run a tiny TCP proxy container with alias `db` pointing to the RDS endpoint, so dev and prod config are identical.

```yaml
services:
  db-proxy:
    image: alpine/socat:1.8.0.0           # example; forwards TCP
    command: tcp-listen:5432,fork,reuseaddr tcp-connect:mydb.xxxx.ap-south-1.rds.amazonaws.com:5432
    networks:
      backend:
        aliases: [db]                     # app uses host "db" in every environment
networks:
  backend:
    internal: false                       # needs egress to reach RDS
```
Security: an alias is only a name; do not treat it as access control. An attacker container on the same network can claim the same alias (it will be added to the round-robin answers), so segment networks and avoid untrusted containers on shared nets. Not run locally; YAML syntax validated only.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `--network-alias` on the default bridge.
✅ Correct: Aliases need a user-defined network.

❌ Mistake 2: Expecting an alias set on network A to work on network B.
✅ Correct: Declare aliases per network under `networks:`.

❌ Mistake 3: Two containers accidentally share an alias, so requests alternate between versions.
✅ Correct: Use unique aliases, or share them intentionally for round-robin.

❌ Mistake 4: Mixing `links:` and aliases in Compose v2.
✅ Correct: `links` is legacy; use `networks.<n>.aliases`.

---

## 🧠 Tricky Interview Question
Two containers both have alias `cache` on the same network. A client resolves `cache` 100 times and gets 50/50 results. Is this a load balancer?

Answer: Not really. It is DNS round-robin: order is rotated but there is no health checking, no weights, and clients that cache the result or hold keep-alive connections stick to one IP. If one container dies, DNS stops returning it only after Docker deregisters it, but clients with cached IPs still fail. Use a proxy (Nginx/HAProxy) or Swarm VIP for real balancing.

---

## ⚫ Interview Questions + Answers

Q1: What is a network alias?
A1: An additional DNS name for a container, scoped to one network, set via `--network-alias` or Compose `aliases`.

Q2: How is it different from container name?
A2: Container name is unique per host and is also a DNS name; aliases are optional, can be many, can repeat across containers and are per network.

Q3: Can aliases be added to a running container?
A3: Yes: `docker network connect --alias X net container` (disconnect first if already connected to that network).

Q4: How do aliases help migrations?
A4: Move the alias to the new container so clients keep the same hostname.

Q5: How does Compose service name relate?
A5: The service name is automatically an alias on every network the service joins.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Legacy apps expect fixed hostnames
- Blue/green or version swaps without client changes
- Same container needs different names per network

❌ Avoid when:
- You need real load balancing or health-based routing
- The default bridge is used (unsupported)
- Simple service names already suffice

---

## 📊 Visual Diagram
```
 network: edge                         network: internal
+-------------------------+          +----------------------------+
| nginx --"api"---------->|          |<---"backend-api"--- worker |
+-------------------------+  [ api-blue container ]  +------------+
                             edge IP 172.20.0.5
                             internal IP 172.21.0.5
 alias "api" exists only on edge; alias "backend-api" only on internal
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Alias | Extra per-network DNS name | अतिरिक्त DNS नाम |
| Round-robin | Rotating answers among IPs | बारी-बारी जवाब |
| Blue/green | Two versions, switch traffic | दो versions, traffic switch |
| --network-alias | docker run flag for alias | alias देने का flag |
| links | Legacy name linking | पुराना नाम जोड़ने का तरीका |
| Cut-over | Moving traffic to new version | नए version पर traffic ले जाना |

---

## ⚡ 3-Line Summary
English: Aliases give a container extra DNS names, scoped per user-defined network.
English: Shared aliases return all IPs (DNS round-robin) but are not a real load balancer.
English: Use them to keep client hostnames stable during migrations.

Hindi: Aliases container को user-defined network पर अतिरिक्त DNS नाम देते हैं।
Hindi: साझा alias सभी IPs लौटाता है (DNS round-robin) पर यह असली load balancer नहीं है।
Hindi: Migration में client hostnames स्थिर रखने के लिए इस्तेमाल करो।

---

## ➡️ Next Topic
**175. Exposing Ports** - EXPOSE vs publishing, and what actually opens a container to the outside.
