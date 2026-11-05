# 177. Network Security
# हिंदी में: Docker Network Security (नेटवर्क सुरक्षा)

---

## 🔵 Simple Definition (English)
**Docker network security** means limiting who can talk to your containers and what they can talk to: publish as few ports as possible, segment networks, block outbound access where not needed, encrypt traffic, run non-root with minimal capabilities, and keep the Docker daemon socket private.

## 🔵 सरल परिभाषा (Hindi)
**Docker network security** का मतलब है यह सीमित करना कि आपके containers से कौन बात कर सकता है और वे किससे बात कर सकते हैं: कम से कम ports publish करो, networks अलग करो, ज़रूरत न हो तो outbound बंद करो, traffic encrypt करो, non-root और minimal capabilities से चलाओ, और Docker daemon socket को private रखो।

---

## 🔴 Problem it Solves
Defaults favour convenience: published ports are open to the world (bypassing UFW), all containers on the default bridge can reach each other, and containers can call the internet freely. One vulnerable web container then becomes a pivot to databases, cloud metadata (`169.254.169.254`) and attacker command servers. Real breaches (exposed Redis/Mongo, cryptominers, leaked IAM role credentials) come from these defaults.

## 🔴 यह क्यों बना? (Hindi)
Defaults सुविधा की तरफ झुके होते हैं: published ports पूरी दुनिया के लिए खुले (UFW को bypass करके), default bridge के सभी containers आपस में पहुँच सकते हैं, और containers internet को खुलकर call कर सकते हैं। एक कमज़ोर web container फिर databases, cloud metadata (`169.254.169.254`) और attacker के command server तक पहुँचने का रास्ता बन जाता है। असली breaches (खुले Redis/Mongo, cryptominers, leak हुए IAM role credentials) इन्हीं defaults से होते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Minimise surface: publish only 80/443; bind everything else to 127.0.0.1 or none
Step 2 → Segment: frontend / backend / data networks; DB network gets internal: true
Step 3 → Control egress: internal networks, or DOCKER-USER iptables rules, block 169.254.169.254
Step 4 → Encrypt: TLS at Nginx; TLS/mTLS between services if crossing hosts; overlay encrypted: "true"
Step 5 → Harden containers: non-root, cap_drop ALL, no-new-privileges, read_only rootfs
Step 6 → Protect the daemon: never expose tcp://2375, never mount /var/run/docker.sock into app containers
Step 7 → Audit: docker ps ports, ss -tlnp, trivy/network scans, cloud security-group review
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → सतह घटाओ: सिर्फ 80/443 publish करो; बाकी सब 127.0.0.1 पर या बिल्कुल नहीं
Step 2 → अलग करो: frontend / backend / data networks; DB network में internal: true
Step 3 → Egress नियंत्रित करो: internal networks, या DOCKER-USER iptables rules, 169.254.169.254 block करो
Step 4 → Encrypt करो: Nginx पर TLS; hosts के बीच TLS/mTLS; overlay में encrypted: "true"
Step 5 → Containers harden करो: non-root, cap_drop ALL, no-new-privileges, read_only rootfs
Step 6 → Daemon बचाओ: tcp://2375 कभी expose न करो, /var/run/docker.sock को app containers में mount न करो
Step 7 → Audit करो: docker ps ports, ss -tlnp, trivy/network scans, cloud security-group review
```

---

## 🟡 Real World Example
A startup runs Redis with `-p 6379:6379` and no password on an EC2 box. Within hours an attacker writes an SSH key through Redis `CONFIG SET dir` and gets a shell, then uses the instance's IAM role via the metadata service to read S3 buckets. Fixes: no published Redis port, `internal` data network, `requirepass`, IMDSv2 with hop limit 1, and an egress block on 169.254.169.254 from containers.

## 🟡 Real Example Hindi mein
एक startup EC2 पर Redis `-p 6379:6379` और बिना password के चलाता है। कुछ घंटों में attacker Redis `CONFIG SET dir` से SSH key लिख देता है और shell पा लेता है, फिर metadata service से instance का IAM role इस्तेमाल करके S3 buckets पढ़ता है। समाधान: Redis port publish नहीं, `internal` data network, `requirepass`, IMDSv2 hop limit 1, और containers से 169.254.169.254 का egress block।

---

## 💻 Code / Config Example — Basic
```bash
# Segmented networks: db network has no route outside
docker network create frontend                     # nginx <-> api
docker network create --internal backend           # api <-> db only, no internet

# Redis only on backend, with a password, NOT published
docker run -d --name redis --network backend \
  redis:7-alpine redis-server --requirepass "$REDIS_PASSWORD"   # password from env of your shell

# API sits on both networks
docker run -d --name api --network frontend myrepo/api:1.0.0
docker network connect backend api                 # now api reaches redis but redis cannot reach internet

# Harden the container itself
docker run -d --name api2 --network frontend \
  --read-only --tmpfs /tmp \                       # immutable filesystem, writable /tmp in memory
  --cap-drop ALL \                                 # drop all Linux capabilities
  --security-opt no-new-privileges:true \          # block setuid privilege escalation
  --user 1000:1000 \                               # non-root user
  myrepo/api:1.0.0
```

## 💻 Code / Config Example — Advanced
```yaml
# docker-compose.yml - hardened production profile
services:
  nginx:
    image: nginx:1.27-alpine                # example tag
    ports: ["80:80", "443:443"]             # only public entry
    read_only: true                         # immutable root filesystem
    tmpfs: [/var/cache/nginx, /var/run]     # writable runtime dirs in memory
    cap_drop: [ALL]                         # remove all capabilities
    cap_add: [NET_BIND_SERVICE, CHOWN, SETUID, SETGID]   # minimum nginx needs to start as root
    security_opt: ["no-new-privileges:true"]
    networks: [frontend]

  api:
    image: myrepo/api:1.0.0
    user: "1000:1000"                       # non-root
    read_only: true
    tmpfs: [/tmp]
    cap_drop: [ALL]                         # API needs no capabilities
    security_opt: ["no-new-privileges:true"]
    environment:
      REDIS_URL: redis://redis:6379         # internal name only
    networks: [frontend, backend]
    deploy:
      resources:
        limits: {cpus: "1.0", memory: 512M} # limit blast radius of abuse / DoS
    sysctls:
      net.ipv4.ip_unprivileged_port_start: "0"   # (optional) not needed above 1024; shown for completeness

  redis:
    image: redis:7-alpine
    command: ["redis-server", "--requirepass", "${REDIS_PASSWORD}", "--protected-mode", "yes"]
    cap_drop: [ALL]
    networks: [backend]                     # internal only

networks:
  frontend: {}                              # public-facing tier
  backend:
    internal: true                          # no egress / no ingress from outside
```
```bash
# Host-level rules in DOCKER-USER (processed before Docker's own rules). Run as root.
# 1) Stop containers reaching the AWS metadata service (credentials theft)
iptables -I DOCKER-USER -d 169.254.169.254 -j DROP
# 2) Only the proxy subnet may reach published port 3000 (example subnet)
iptables -I DOCKER-USER -p tcp --dport 3000 ! -s 172.18.0.0/16 -j DROP
# Persist with iptables-persistent / nftables; verify:
iptables -L DOCKER-USER -n --line-numbers
```

---

## 🟠 My Stack Integration
- **Nginx**: terminate TLS 1.2/1.3, add `limit_req`, hide version (`server_tokens off`), send HSTS.
- **Node.js/FastAPI**: validate input, run as non-root, no `--privileged`, set CORS tightly; talk to DB via internal network.
- **React**: static files only; no secrets in the bundle (everything in it is public).
- **AWS**: security groups as the outermost firewall (22 from your IP only, 80/443), IMDSv2 required with hop limit 1 so containers cannot read role credentials, private subnets for DBs, RDS not publicly accessible.
- **VPS**: SSH keys only, fail2ban, unattended upgrades, daemon not listening on TCP.

```nginx
# nginx security fragment (not tested here; run nginx -t before reload)
server_tokens off;                                       # hide version
limit_req_zone $binary_remote_addr zone=perip:10m rate=10r/s;   # 10 req/s per IP
server {
    listen 443 ssl;                                      # TLS only
    ssl_protocols TLSv1.2 TLSv1.3;                       # disable old protocols
    add_header Strict-Transport-Security "max-age=31536000" always;   # HSTS
    location /api/ {
        limit_req zone=perip burst=20 nodelay;           # absorb small bursts
        proxy_pass http://api:3000;                      # internal upstream
    }
}
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Exposing the Docker daemon on `tcp://0.0.0.0:2375`.
✅ Correct: Use the Unix socket or TLS (2376) with client certs; better SSH (`DOCKER_HOST=ssh://`).

❌ Mistake 2: Mounting `/var/run/docker.sock` into a container.
✅ Correct: Avoid it; the container gets root on the host. If unavoidable, use a socket proxy with read-only API filters.

❌ Mistake 3: `--privileged` or `--network host` for convenience.
✅ Correct: Grant specific `cap_add` and publish required ports only.

❌ Mistake 4: Secrets in environment variables baked into images.
✅ Correct: Use secrets/files or a secrets manager (AWS Secrets Manager / SSM).

---

## 🧠 Tricky Interview Question
You put the DB on an `internal: true` network and the API on both networks. Can a compromised API still exfiltrate data to the internet?

Answer: Yes. The API is also on the non-internal `frontend` network which has egress, so it can send data out. `internal` only protects the DB container itself. To restrict, limit the API's egress with an egress proxy/allow-list, DOCKER-USER rules, VPC security-group egress rules or network policies, and monitor outbound traffic.

---

## ⚫ Interview Questions + Answers

Q1: How do you secure container networking?
A1: Minimal published ports, segmented user-defined networks, internal networks for data tier, TLS, egress control, least-privilege containers, firewall at cloud and host level.

Q2: Why is `docker.sock` dangerous?
A2: Whoever can use it can start a privileged container mounting `/`, so it equals root on the host.

Q3: Why doesn't UFW protect published ports?
A3: Docker's iptables rules in `nat`/`FORWARD` run before UFW's filter rules. Use `DOCKER-USER`.

Q4: What is ICC?
A4: Inter-container communication on a bridge; disable with `com.docker.network.bridge.enable_icc=false` and allow explicitly.

Q5: How to protect AWS credentials from containers?
A5: IMDSv2 required, hop limit 1, block 169.254.169.254, use task/pod-level roles.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any internet-facing deployment (always)
- Multi-tenant or multi-app hosts
- Compliance requirements (PCI, SOC2)

❌ Avoid when:
- Over-engineering a local laptop dev stack (keep it simple, but still don't expose the daemon)
- Relying on one control only (defence in depth is needed)

---

## 📊 Visual Diagram
```
 Internet
    | 80/443 only (Security Group)
    v
 [ host firewall + DOCKER-USER rules ]
    v
 +-- frontend net ----------------+
 |  [nginx] --> [api] ------------+--> egress allowed (HTTPS APIs)
 +--------------|-----------------+
                |
 +-- backend net (internal: true) -+
 |  [api] --> [redis] [postgres]   |   X  no route to internet
 +----------------------------------+
 169.254.169.254 (metadata) : DROP from containers
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Segmentation | Splitting into isolated networks | नेटवर्क को अलग हिस्सों में बाँटना |
| Egress | Outbound traffic | बाहर जाने वाला traffic |
| Capabilities | Fine-grained root powers | root की छोटी शक्तियाँ |
| IMDSv2 | Token-based AWS metadata | AWS metadata का सुरक्षित version |
| docker.sock | Daemon control socket | Daemon नियंत्रण socket |
| Defence in depth | Layered controls | कई परतों की सुरक्षा |

---

## ⚡ 3-Line Summary
English: Publish the minimum, segment networks and block unneeded egress.
English: Harden containers (non-root, cap_drop, read-only) and protect docker.sock and metadata.
English: Use cloud security groups plus DOCKER-USER rules because UFW is bypassed.

Hindi: कम से कम publish करो, networks अलग करो और गैर-ज़रूरी egress रोको।
Hindi: Containers harden करो (non-root, cap_drop, read-only) और docker.sock व metadata बचाओ।
Hindi: Cloud security groups और DOCKER-USER rules लगाओ क्योंकि UFW bypass होता है।

---

## ➡️ Next Topic
**178. Network Isolation** - designing separate networks per app and tier so one breach stays contained.
