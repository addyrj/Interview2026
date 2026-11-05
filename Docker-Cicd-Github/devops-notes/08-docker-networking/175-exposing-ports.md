# 175. Exposing Ports
# हिंदी में: Ports Expose करना (EXPOSE बनाम publish)

---

## 🔵 Simple Definition (English)
**Exposing a port** has two meanings in Docker. `EXPOSE 3000` in a Dockerfile (or `expose:` in Compose) is only **documentation/metadata**: "this app listens on 3000". **Publishing** (`-p` / `ports:`) is what actually maps a host port to a container port so the outside world can reach it.

## 🔵 सरल परिभाषा (Hindi)
Docker में **Port expose करने** के दो मतलब हैं। Dockerfile में `EXPOSE 3000` (या Compose का `expose:`) सिर्फ **documentation/metadata** है: "यह app 3000 पर सुनती है"। **Publish** (`-p` / `ports:`) असल में host port को container port से जोड़ता है ताकि बाहर की दुनिया पहुँच सके।

---

## 🔴 Problem it Solves
Containers are isolated by default: nothing outside the host can reach a process inside. Developers need a clear, controlled way to say which services are public and which stay private. Without the EXPOSE/publish distinction people either open everything (insecure) or cannot tell what port an image uses without reading its code.

## 🔴 यह क्यों बना? (Hindi)
Containers by default isolated होते हैं: host के बाहर से कोई अंदर के process तक नहीं पहुँचता। Developers को साफ़ और नियंत्रित तरीका चाहिए कि कौन-सी services public हैं और कौन-सी private। EXPOSE/publish के फर्क के बिना लोग या तो सब खोल देते (असुरक्षित) या image का port जानने के लिए code पढ़ना पड़ता।

---

## 🟢 How it Works — Step by Step

```
Step 1 → App inside container listens on 0.0.0.0:3000 (NOT 127.0.0.1, or nothing can reach it)
Step 2 → Dockerfile EXPOSE 3000 records metadata (visible in docker inspect / docker ps); opens nothing
Step 3 → docker run -p 8080:3000 adds iptables DNAT: host:8080 -> container:3000
Step 4 → docker run -P publishes every EXPOSEd port on random high host ports
Step 5 → Containers on the same user-defined network reach each other on ANY listening port, EXPOSE not needed
Step 6 → Verify: docker port <name>, ss -tlnp on host, curl from outside
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Container के अंदर app 0.0.0.0:3000 पर सुने (127.0.0.1 नहीं, वरना कोई नहीं पहुँचेगा)
Step 2 → Dockerfile EXPOSE 3000 सिर्फ metadata लिखता है (docker inspect / docker ps में दिखता है); कुछ खोलता नहीं
Step 3 → docker run -p 8080:3000 iptables DNAT जोड़ता है: host:8080 -> container:3000
Step 4 → docker run -P हर EXPOSE किए port को random ऊँचे host ports पर publish करता है
Step 5 → उसी user-defined network के containers किसी भी listening port पर पहुँच सकते हैं, EXPOSE ज़रूरी नहीं
Step 6 → जाँच: docker port <name>, host पर ss -tlnp, बाहर से curl
```

---

## 🟡 Real World Example
Your React build is served by Nginx container (listens on 80) and the Node API listens on 3000. Only Nginx is published: `-p 80:80 -p 443:443`. The API has `EXPOSE 3000` so teammates know its port, but it is never published. A new developer wrongly adds `-p 3000:3000` and `-p 27017:27017` for Mongo on the VPS; within hours bots find the open MongoDB port. This exact mistake has led to many real data-ransom incidents.

## 🟡 Real Example Hindi mein
आपका React build Nginx container (port 80) से serve होता है और Node API 3000 पर सुनती है। सिर्फ Nginx publish है: `-p 80:80 -p 443:443`। API में `EXPOSE 3000` है ताकि teammates को port पता रहे, पर वह कभी publish नहीं होता। नया developer VPS पर गलती से `-p 3000:3000` और Mongo के लिए `-p 27017:27017` जोड़ देता है; कुछ घंटों में bots खुला MongoDB port ढूँढ लेते हैं। इसी गलती से कई असली data-ransom घटनाएँ हुई हैं।

---

## 💻 Code / Config Example — Basic
```dockerfile
# Dockerfile - Node.js API
FROM node:20-alpine                  # small official base image (example tag)
WORKDIR /app                         # working directory inside the image
COPY package*.json ./                # copy manifests first for layer caching
RUN npm ci --omit=dev                # install production dependencies only
COPY . .                             # copy application source
EXPOSE 3000                          # METADATA ONLY: documents the listening port
USER node                            # drop root for safety
CMD ["node", "server.js"]            # app must listen on 0.0.0.0:3000
```
```bash
docker build -t myrepo/api:1.0.0 .                    # build the image

docker run -d --name api1 -P myrepo/api:1.0.0         # -P: publish EXPOSEd ports on RANDOM host ports
docker port api1                                      # shows e.g. 3000/tcp -> 0.0.0.0:32768

docker run -d --name api2 -p 8080:3000 myrepo/api:1.0.0   # fixed: host 8080 -> container 3000
docker run -d --name api3 -p 127.0.0.1:8081:3000 myrepo/api:1.0.0   # loopback only (not public)
docker run -d --name api4 -p 5353:53/udp myrepo/api:1.0.0           # UDP mapping example

curl http://localhost:8080/health                     # test from the host
```

## 💻 Code / Config Example — Advanced
```yaml
# docker-compose.yml - production-style exposure rules
services:
  nginx:
    image: nginx:1.27-alpine              # example tag
    ports:
      - "80:80"                           # public HTTP
      - "443:443"                         # public HTTPS
    depends_on:
      api:
        condition: service_healthy        # start only after API reports healthy
    networks: [edge]

  api:
    build: ./api                          # uses Dockerfile above
    expose:
      - "3000"                            # Compose 'expose': internal only, no host binding
    ports:
      - "127.0.0.1:9229:9229"             # Node inspector reachable from the host loopback only
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://127.0.0.1:3000/health"]   # probe app locally
      interval: 15s                       # run every 15 seconds
      timeout: 3s                         # each probe times out at 3 seconds
      retries: 3                          # mark unhealthy after 3 failures
    networks: [edge, data]

  postgres:
    image: postgres:16-alpine
    # NO ports: here -> unreachable from host and internet
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/pg_pw   # secret from file
    secrets: [pg_pw]
    networks: [data]

networks:
  edge: {}
  data:
    internal: true                        # cut off from the internet

secrets:
  pg_pw:
    file: ./secrets/pg_pw.txt             # chmod 600; add to .gitignore
```
```bash
# Audit what is really reachable on the VPS
docker ps --format 'table {{.Names}}\t{{.Ports}}'     # look for 0.0.0.0:PORT entries
sudo ss -tlnp | grep -E ':(3000|5432|27017|6379)\b'   # databases/internal ports must NOT be on 0.0.0.0
```

---

## 🟠 My Stack Integration
- **Node.js / FastAPI**: bind the server to `0.0.0.0` (`app.listen(3000, '0.0.0.0')`, `uvicorn --host 0.0.0.0 --port 8000`), add `EXPOSE`, never publish in prod.
- **React**: build with `npm run build`, serve via Nginx image on 80 inside; only Nginx publishes.
- **Nginx on VPS host**: if Nginx runs on the host (not Docker), publish the API on loopback: `127.0.0.1:3000:3000` and `proxy_pass http://127.0.0.1:3000;`.
- **AWS**: security group allows 80/443 (and 22 from your IP). Docker's published ports **bypass UFW** because Docker edits iptables directly, so rely on the security group or the `DOCKER-USER` chain.

```bash
# Block external access to a published port at the Docker level (example: only allow 10.0.0.0/8 to 8080)
sudo iptables -I DOCKER-USER -p tcp --dport 8080 ! -s 10.0.0.0/8 -j DROP   # evaluated before Docker rules
```
Not run locally (no Docker daemon); Dockerfile and YAML syntax checked.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Thinking `EXPOSE 3000` makes the app reachable.
✅ Correct: Add `-p`/`ports:`; EXPOSE is documentation (except for `-P`).

❌ Mistake 2: Publishing databases (`-p 27017:27017`, `5432:5432`).
✅ Correct: Keep them on an internal network; use SSH tunnel for admin work.

❌ Mistake 3: App binds `127.0.0.1` inside the container, so published port gives "connection reset".
✅ Correct: Bind `0.0.0.0`.

❌ Mistake 4: Trusting UFW to block published ports.
✅ Correct: Use cloud security groups, `127.0.0.1:` bindings or `DOCKER-USER` rules.

---

## 🧠 Tricky Interview Question
You wrote `ufw deny 5432` on your VPS but `docker run -p 5432:5432 postgres` is still reachable from the internet. Why?

Answer: Docker inserts its own DNAT/forwarding rules in the iptables `nat` and `FORWARD` chains, which are processed before UFW's INPUT-chain rules, so UFW never sees the traffic. Fix: don't publish the port, bind to `127.0.0.1`, put rules in the `DOCKER-USER` chain, or use the cloud firewall.

---

## ⚫ Interview Questions + Answers

Q1: EXPOSE vs -p?
A1: EXPOSE is metadata documenting a port; `-p host:container` actually publishes it.

Q2: What does -P do?
A2: Publishes all EXPOSEd ports to random ephemeral host ports.

Q3: Do containers on the same network need EXPOSE or -p to talk?
A3: No. On a user-defined network any listening port is reachable by name.

Q4: How to publish only on localhost?
A4: `-p 127.0.0.1:8080:3000`.

Q5: Compose `expose` vs `ports`?
A5: `expose` makes ports available to linked services only (metadata-like); `ports` binds to the host.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- EXPOSE: always, to document the service port
- Publish: only for edge services (Nginx, public API)
- Loopback publish: debug ports, host-based reverse proxy

❌ Avoid when:
- Publishing DB, cache, queue, admin ports to `0.0.0.0`
- Relying on EXPOSE for security
- Using random `-P` ports in production (hard to firewall)

---

## 📊 Visual Diagram
```
 Internet
    |  :443
    v
 [ Security Group / Firewall ]
    v
 host :80/:443  --DNAT-->  [nginx:80]
                               |  docker network "edge" (no publish needed)
                               v
                          [api:3000]  (EXPOSE 3000 = label only)
                               |  docker network "data" (internal)
                               v
                          [postgres:5432]   <- NOT published
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| EXPOSE | Dockerfile port metadata | Port की जानकारी (metadata) |
| Publish (-p) | Map host port to container | host port को container से जोड़ना |
| DNAT | Destination NAT rule | Destination NAT नियम |
| 0.0.0.0 | All interfaces | सभी interfaces |
| DOCKER-USER | iptables chain for your rules | आपके नियमों की iptables chain |
| Loopback | 127.0.0.1 local only | सिर्फ local पता |

---

## ⚡ 3-Line Summary
English: EXPOSE only documents a port; -p / ports: actually opens it to the host.
English: Publish only edge services and bind sensitive ones to 127.0.0.1.
English: Docker bypasses UFW, so use security groups or DOCKER-USER rules.

Hindi: EXPOSE सिर्फ port document करता है; -p / ports: उसे host के लिए खोलता है।
Hindi: सिर्फ edge services publish करो और संवेदनशील को 127.0.0.1 पर बाँधो।
Hindi: Docker UFW को bypass करता है, इसलिए security groups या DOCKER-USER rules लगाओ।

---

## ➡️ Next Topic
**176. Port Mapping Strategies** - choosing fixed, random, loopback and reverse-proxy port layouts for real deployments.
