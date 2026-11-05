# 167. Bridge Network (default)
# हिंदी में: Bridge Network (डिफ़ॉल्ट)

---

## 🔵 Simple Definition (English)
A **bridge network** is a virtual switch on the Docker host. Containers attached to it get private IPs and can talk to each other. The built-in one is called `bridge` (interface `docker0`); you can also create **user-defined bridges** that add automatic DNS names and better isolation.

## 🔵 सरल परिभाषा (Hindi)
**Bridge network** Docker host पर एक virtual switch है। इससे जुड़े containers को private IPs मिलती हैं और वे आपस में बात कर सकते हैं। Built-in वाले का नाम `bridge` (interface `docker0`) है; तुम **user-defined bridges** भी बना सकते हो जिनमें automatic DNS नाम और बेहतर isolation मिलता है।

---

## 🔴 Problem it Solves
Without a bridge, each container would have an isolated network stack with no way to reach other containers or the internet. The bridge connects them through one virtual switch and uses NAT for outbound internet. The default bridge, however, has weaknesses (no DNS by name, all containers share it), which is why user-defined bridges exist.

## 🔴 यह क्यों बना? (Hindi)
Bridge के बिना हर container का network stack अलग होता और वो न दूसरे containers तक पहुँचता, न internet तक। Bridge सबको एक virtual switch से जोड़ता है और बाहर जाने के लिए NAT use करता है। लेकिन default bridge की कमज़ोरियाँ हैं (नाम से DNS नहीं, सब containers एक ही network में), इसीलिए user-defined bridges बने।

---

## 🟢 How it Works — Step by Step

```
Step 1 → docker run (no --network flag) attaches the container to default "bridge"
Step 2 → Docker creates veth pair: eth0 inside container <-> vethXXXX on docker0
Step 3 → docker0 (172.17.0.1) is the gateway; container gets 172.17.0.x
Step 4 → Container-to-container: switched at layer 2 on the bridge (same subnet)
Step 5 → Container-to-internet: iptables MASQUERADE rewrites source to host IP
Step 6 → Host-to-container: only via published ports (-p) or the container IP
Step 7 → User-defined bridge: same mechanics + DNS names + own subnet + own isolation
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → docker run (बिना --network) container को default "bridge" से जोड़ता है
Step 2 → Docker veth pair बनाता है: container में eth0 <-> docker0 पर vethXXXX
Step 3 → docker0 (172.17.0.1) gateway है; container को 172.17.0.x मिलती है
Step 4 → Container-to-container: bridge पर layer 2 में switch होता है (एक subnet)
Step 5 → Container-to-internet: iptables MASQUERADE source को host IP कर देता है
Step 6 → Host-to-container: सिर्फ published ports (-p) या container IP से
Step 7 → User-defined bridge: वही mechanics + DNS नाम + अपना subnet + अपना isolation
```

---

## 🟡 Real World Example
A freelancer hosts three client sites on one VPS. Each client gets its own Compose project, and Compose automatically creates one bridge network per project (`clienta_default`, `clientb_default`). Client A's Node.js app cannot reach Client B's database even though they sit on the same machine, because they are on different bridges. A single shared Nginx joins all three networks to route by domain.

## 🟡 Real Example Hindi mein
एक freelancer एक VPS पर तीन clients की sites host करता है। हर client का अपना Compose project है और Compose हर project के लिए अपना bridge network (`clienta_default`, `clientb_default`) बनाता है। Client A का Node.js app Client B के database तक नहीं पहुँच सकता, भले एक ही machine हो, क्योंकि अलग bridges पर हैं। एक shared Nginx तीनों networks से जुड़कर domain के हिसाब से route करता है।

---

## 💻 Code / Config Example — Basic
```bash
# --- default bridge ---
docker run -d --name a1 alpine sleep 3600          # lands on default bridge
docker run -d --name a2 alpine sleep 3600          # also default bridge
docker inspect -f '{{.NetworkSettings.IPAddress}}' a2   # prints e.g. 172.17.0.3
docker exec a1 ping -c1 172.17.0.3                 # works: IP reachability
docker exec a1 ping -c1 a2                         # FAILS: no DNS by name on default bridge

# --- user-defined bridge ---
docker network create mynet                        # creates bridge named mynet
docker run -d --name b1 --network mynet alpine sleep 3600   # attach at start
docker run -d --name b2 --network mynet alpine sleep 3600   # second container
docker exec b1 ping -c1 b2                         # WORKS: name resolved by embedded DNS

# cleanup
docker rm -f a1 a2 b1 b2 && docker network rm mynet   # remove test resources
```

## 💻 Code / Config Example — Advanced
```bash
# user-defined bridge with explicit subnet, gateway and options
docker network create \
  --driver bridge \
  --subnet 172.30.0.0/24 \
  --gateway 172.30.0.1 \
  --opt com.docker.network.bridge.name=br-app \
  --opt com.docker.network.bridge.enable_icc=true \
  appnet
# --driver bridge : explicit driver (default anyway)
# --subnet/--gateway : avoid clashes with your company VPN or AWS VPC ranges
# bridge.name : readable Linux interface name br-app (instead of br-<hash>)
# enable_icc : allow container-to-container traffic (true by default)
```

```yaml
# docker-compose.yml - custom bridge with fixed subnet and static IP
services:
  api:
    image: myorg/api:1.4.2                  # example tag
    networks:
      appnet:
        ipv4_address: 172.30.0.10           # fixed IP (rarely needed, prefer names)
        aliases:
          - backend                         # extra DNS name for this container
    ports:
      - "127.0.0.1:3000:3000"               # publish to host loopback only
  db:
    image: postgres:16-alpine               # example tag
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}     # supplied via .env
    networks:
      - appnet                              # same private bridge
networks:
  appnet:
    driver: bridge                          # bridge driver
    ipam:
      config:
        - subnet: 172.30.0.0/24             # must match any ipv4_address above
```

---

## 🟠 My Stack Integration
- **Node.js + Mongo:** put both on one user-defined bridge, connect with `mongodb://mongo:27017/app`.
- **FastAPI + Redis:** `REDIS_URL=redis://cache:6379`; no ports published.
- **Nginx on host vs in Docker:** if Nginx runs on the VPS host (not in a container), publish the API as `127.0.0.1:3000:3000` and `proxy_pass http://127.0.0.1:3000`. If Nginx is a container, use `proxy_pass http://api:3000`.
- **AWS VPC clash:** if your VPC uses 172.17.0.0/16 or 172.31.0.0/16, the default docker0 range can conflict. Change `default-address-pools` in `/etc/docker/daemon.json`.

```json
{
  "default-address-pools": [
    { "base": "10.200.0.0/16", "size": 24 }
  ]
}
```
(Restart the Docker daemon after editing `/etc/docker/daemon.json`; example range, choose one free in your network.)

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using the default bridge for real apps and then using `--link`.
✅ Correct: `--link` is legacy. Use a user-defined bridge or Compose.

❌ Mistake 2: Hard-coding container IPs like `172.17.0.3`; IPs change on restart.
✅ Correct: Use names and aliases.

❌ Mistake 3: Subnet overlap with the VPN or VPC, causing "network unreachable" for some hosts.
✅ Correct: Set `default-address-pools` or a custom `--subnet`.

❌ Mistake 4: Thinking a bridge is reachable from other hosts.
✅ Correct: A bridge is single-host. Other machines need a published port or an overlay network.

---

## 🧠 Tricky Interview Question
**Q:** Containers A and B are on different user-defined bridges on the same host. Can A reach B by IP?

**Answer:** No by default. Docker installs iptables isolation rules between different bridge networks, so traffic is dropped. To allow it, attach one container to both networks (`docker network connect`), or put them on one network. This is exactly how you isolate tenants on one machine.

---

## ⚫ Interview Questions + Answers

Q1: Default bridge vs user-defined bridge?
A1: User-defined adds automatic DNS by container name, better isolation, on-the-fly attach/detach, and configurable options. Default bridge has none of these.

Q2: What is docker0?
A2: The Linux bridge interface for the default bridge network, usually 172.17.0.1/16.

Q3: How does a container reach the internet?
A3: Through the bridge gateway; iptables MASQUERADE NATs the source IP to the host's.

Q4: How do you reach a host service from a container?
A4: Use `host.docker.internal` (Docker Desktop; on Linux add `extra_hosts: ["host.docker.internal:host-gateway"]`) or the bridge gateway IP.

Q5: What is ICC?
A5: Inter-container communication; if disabled on a bridge, containers cannot talk to each other.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Multiple containers on a single host need to talk
- You want isolation per project/tenant
- Standard web stacks on a VPS

❌ Avoid when:
- Cross-host networking (use overlay or orchestrator)
- You need the container to appear as a LAN device (macvlan)
- Ultra-low latency (host network)

---

## 📊 Visual Diagram
```
   +---------------------- Host ----------------------+
   |   eth0 (public IP) <---- NAT/MASQUERADE ----+    |
   |                                             |    |
   |   docker0 / br-app  (172.30.0.1)  <---------+    |
   |      |             |                              |
   |   vethA1        vethB2                            |
   |      |             |                              |
   | [api 172.30.0.10] [db 172.30.0.11]                |
   +---------------------------------------------------+
    default bridge: IP only | user-defined: IP + DNS names
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| docker0 | Default Linux bridge | default bridge interface |
| User-defined bridge | Custom bridge with DNS | अपना बनाया bridge |
| Gateway | Exit point of the subnet | बाहर जाने का दरवाज़ा |
| Subnet | IP range of a network | IP की range |
| MASQUERADE | NAT for outbound traffic | outbound NAT |
| ICC | Container-to-container traffic | आपसी बातचीत |

---

## ⚡ 3-Line Summary
English: Bridge is the default single-host network driver using a virtual switch and NAT.
User-defined bridges add DNS names and isolation; default bridge does not.
Always prefer user-defined bridges or Compose networks.
Hindi: Bridge default single-host driver है जो virtual switch और NAT use करता है।
User-defined bridges में DNS नाम और isolation मिलता है; default में नहीं।
हमेशा user-defined bridges या Compose networks चुनो।

---

## ➡️ Next Topic
**168. Host Network** - what happens when a container shares the host's network stack directly, and when that is worth the risk.
