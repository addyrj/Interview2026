# 03. IP Address + Ports
# हिंदी में: IP Address — मशीन का पता; Port — उस मशीन पर चल रहे किसी खास प्रोग्राम का दरवाज़ा

---

## 🔵 Simple Definition (English)
An **IP address** is the unique address of a device on a network (like a building address).
A **port** is a number (0–65535) that identifies a specific program/service on that device (like a flat number in that building).
Together, `IP:Port` (e.g. `13.235.10.20:443`) tells data exactly **which machine** and **which program** to reach.

## 🔵 सरल परिभाषा (Hindi)
IP Address किसी डिवाइस का पता है — जैसे बिल्डिंग का पता।
Port उस डिवाइस पर चल रहे प्रोग्राम का नंबर है — जैसे बिल्डिंग में फ़्लैट नंबर। `IP:Port` से डेटा सही मशीन के सही प्रोग्राम तक पहुँचता है।

---

## 🔴 Problem it Solves
- **IP:** Packets need a destination. Without a unique address, routers can't know where to send data.
- **Ports:** One server runs many programs at once — Nginx, Node.js, PostgreSQL, Redis, SSH. When a packet arrives at the machine, the OS must know **which program** gets it. Ports solve this.
- **IPv4 shortage:** IPv4 has only ~4.3 billion addresses — fewer than the number of devices. **Private IPs + NAT** and **IPv6** were created to solve this.

## 🔴 यह क्यों बना? (Hindi)
पैकेट को मंज़िल चाहिए — इसलिए IP। एक सर्वर पर कई प्रोग्राम (Nginx, Node, Postgres, Redis) चलते हैं — OS को पता होना चाहिए डेटा किसे देना है, इसलिए Port।
IPv4 में सिर्फ़ ~430 करोड़ पते हैं, डिवाइस उससे ज़्यादा हैं — इसलिए Private IP + NAT और IPv6 आए।

---

## 🟢 How it Works — Step by Step

### IP + Port together

```
                 Server  13.235.10.20   (ONE IP)
        ┌───────────────────────────────────────────────┐
        │  :22    SSH         (you, to log in)          │
        │  :80    Nginx HTTP  (redirect to 443)         │
        │  :443   Nginx HTTPS ◄── public traffic        │
        │  :3000  Node.js API     ┐                     │
        │  :8000  FastAPI         │ internal only       │
        │  :5432  PostgreSQL      │ (firewall blocks    │
        │  :6379  Redis           ┘  from internet)     │
        └───────────────────────────────────────────────┘

Request to 13.235.10.20:443 → OS hands packet to Nginx
Nginx proxies to 127.0.0.1:3000 → Node.js
```

### IPv4 vs IPv6

```
IPv4:  192.168.1.10                       32 bits  → ~4.3 billion addresses
       └─┬─┘└┬┘└┬┘└┬┘   4 numbers, each 0–255

IPv6:  2406:da1a:0abc:1200:0000:0000:0000:0001     128 bits → 3.4 × 10³⁸ addresses
       short form: 2406:da1a:abc:1200::1           (:: = consecutive zeros)
```

### Public vs Private IP + NAT

```
Private IP ranges (not reachable from the internet, reusable everywhere):
   10.0.0.0      – 10.255.255.255     (10.0.0.0/8)       ← AWS VPCs usually use this
   172.16.0.0    – 172.31.255.255     (172.16.0.0/12)    ← Docker default bridge 172.17.x.x
   192.168.0.0   – 192.168.255.255    (192.168.0.0/16)   ← home Wi-Fi
Special:
   127.0.0.1  = localhost (this machine itself)
   0.0.0.0    = "all interfaces" when a server binds/listens

NAT (Network Address Translation) — many private devices share one public IP:

 Phone   192.168.1.5:51000 ─┐                       ┌──────────────────────┐
 Laptop  192.168.1.6:52000 ─┼──► Router (NAT) ────► │ Internet sees only   │
 TV      192.168.1.7:53000 ─┘   public 49.36.x.x    │ 49.36.x.x:40001/2/3  │
                                keeps a table:      └──────────────────────┘
                                40001 ↔ 192.168.1.5:51000
                                40002 ↔ 192.168.1.6:52000
```

> 💡 That's why your laptop is `192.168.x.x` at home but Google sees a different IP. Also why a server can't directly "call" your phone — NAT blocks unsolicited incoming connections → we need **push notifications / WebSockets** (client opens the connection first).

### CIDR — writing IP ranges (used in AWS VPC, security groups)

```
10.0.0.0/16   → first 16 bits fixed → 65,536 IPs  (10.0.0.0 – 10.0.255.255)   ← whole VPC
10.0.1.0/24   → first 24 bits fixed → 256 IPs     (10.0.1.0 – 10.0.1.255)     ← one subnet
13.235.10.20/32 → exactly 1 IP                                                 ← "only my office IP"
0.0.0.0/0     → the entire internet

Formula: number of IPs = 2^(32 − prefix)
```

### Port ranges

```
┌──────────────────┬──────────────┬────────────────────────────────────────┐
│ Range            │ Name         │ Examples                               │
├──────────────────┼──────────────┼────────────────────────────────────────┤
│ 0 – 1023         │ Well-known   │ 22 SSH, 53 DNS, 80 HTTP, 443 HTTPS,    │
│                  │ (need root)  │ 25 SMTP                                │
│ 1024 – 49151     │ Registered   │ 3000 Node, 3306 MySQL, 5432 Postgres,  │
│                  │              │ 6379 Redis, 27017 MongoDB, 8000 FastAPI│
│                  │              │ 9092 Kafka, 5672 RabbitMQ              │
│ 49152 – 65535    │ Ephemeral    │ Random port YOUR side uses for an      │
│                  │ (temporary)  │ outgoing connection                    │
└──────────────────┴──────────────┴────────────────────────────────────────┘
```

### A connection = 4 values (the "4-tuple")

```
(Source IP, Source Port, Destination IP, Destination Port)
(49.36.1.1, 52144,       13.235.10.20,   443)   ← user A
(49.36.1.1, 52145,       13.235.10.20,   443)   ← user A, second tab
(103.2.2.2, 61000,       13.235.10.20,   443)   ← user B

Same server port 443 handles thousands of connections, because each 4-tuple is unique.
```

## 🟢 कैसे काम करता है? (Hindi)
1. पैकेट पर लिखा होता है: किस IP पर जाना है और किस Port पर।
2. Router IP देखकर पैकेट सही मशीन तक पहुँचाता है।
3. मशीन का OS Port देखकर पैकेट सही प्रोग्राम को देता है (443 → Nginx, 5432 → Postgres)।
4. घर में सारे डिवाइस का private IP होता है; Router (NAT) सबको एक public IP के पीछे छिपा देता है।
5. एक कनेक्शन की पहचान 4 चीज़ों से होती है: Source IP, Source Port, Destination IP, Destination Port।

---

## 🟡 Real World Example

**Zomato's backend on AWS**
- Only the **load balancer** has public IPs and listens on 443.
- App servers live in **private subnets** (`10.0.x.x`) — no public IP at all, so hackers can't reach them directly.
- Databases (RDS PostgreSQL on 5432) allow connections **only from the app servers' security group**, not from the internet.
- Outbound calls from private servers (to payment gateways, SMS providers) go through a **NAT Gateway** that has a fixed public IP — that fixed IP is what Razorpay/banks whitelist.

**Exposed databases — real breaches**
- Thousands of MongoDB (27017) and Elasticsearch (9200) servers have been found open to `0.0.0.0/0` with no password, and their data was stolen or held for ransom. The cause: a port exposed to the internet when it should have been private.

## 🟡 Real Example Hindi में
Zomato में सिर्फ़ Load Balancer का IP पब्लिक है; App सर्वर और Database प्राइवेट नेटवर्क (10.x.x.x) में छिपे हैं, जहाँ इंटरनेट से कोई सीधे नहीं पहुँच सकता।
हज़ारों कंपनियों का MongoDB डेटा इसलिए चोरी हुआ क्योंकि पोर्ट 27017 पूरे इंटरनेट के लिए खुला था और पासवर्ड नहीं था।

---

## 🟠 My Stack Example

### Bind addresses — the #1 Docker bug
```js
// Node.js / Express
app.listen(3000, '127.0.0.1');   // ❌ inside Docker: unreachable from outside the container
app.listen(3000, '0.0.0.0');     // ✅ listen on all interfaces inside the container
```
```bash
# FastAPI
uvicorn main:app --host 0.0.0.0 --port 8000      # ✅ in Docker
```

### Docker port mapping
```yaml
services:
  nginx:
    image: nginx
    ports:
      - "80:80"        # host:container — PUBLIC
      - "443:443"
  api:
    build: ./api
    expose:
      - "3000"         # only visible to other containers, NOT the host/internet ✅
  db:
    image: postgres:16
    ports:
      - "127.0.0.1:5432:5432"   # ✅ only from the server itself (for your SSH tunnel)
      # - "5432:5432"           # ❌ opens Postgres to the world (Docker bypasses ufw!)
```

> ⚠️ Docker writes its own iptables rules, so `ports: "5432:5432"` can be reachable from the internet **even if `ufw` blocks 5432**. Bind to `127.0.0.1` or don't publish the port at all.

### Nginx: public 443 → private app port
```nginx
server {
  listen 443 ssl;
  server_name api.myapp.com;

  location / {
    proxy_pass http://api:3000;              # Docker service name + internal port
    proxy_set_header X-Real-IP $remote_addr; # pass the real client IP to Node
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  }
}
```
```js
// Express behind Nginx: trust proxy so req.ip is the USER's IP, not Nginx's 172.x IP.
// Needed for rate limiting by IP and audit logs.
app.set('trust proxy', 1);
```

### AWS Security Group (firewall by port + CIDR)
```
Load Balancer SG:  inbound 443 from 0.0.0.0/0
App Server SG:     inbound 3000 from LoadBalancer-SG only
RDS SG:            inbound 5432 from AppServer-SG only
SSH:               inbound 22 from 203.0.113.7/32 (your office IP) — or use SSM, no SSH at all
```

### Useful commands
```bash
lsof -i :3000                 # which process is using port 3000? ("EADDRINUSE" error)
kill -9 <PID>
ss -tulpn                     # linux: all listening ports
curl ifconfig.me              # your public IP
ipconfig getifaddr en0        # mac: your private IP
nc -zv db.internal 5432       # can I reach this port? (connectivity test)
```

### React Native dev tip
On an Android emulator, `localhost` means the **emulator itself**, not your laptop.
```js
const API = Platform.OS === 'android'
  ? 'http://10.0.2.2:3000'        // Android emulator → your laptop
  : 'http://localhost:3000';      // iOS simulator shares the laptop's network
// Real phone on same Wi-Fi → use laptop's private IP, e.g. http://192.168.1.6:3000
```

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between an IP address and a port?**
A1: An IP identifies a machine (network interface) on the network; a port identifies a specific process/service on that machine. The OS uses the destination port to deliver incoming packets to the right application. A connection is uniquely identified by the 4-tuple: source IP, source port, destination IP, destination port.

**Q2: Public vs private IP — and what is NAT?**
A2: Public IPs are globally unique and routable on the internet. Private IPs (10.x, 172.16–31.x, 192.168.x) are only valid inside a local network and can be reused by everyone. NAT lets many private devices share one public IP by rewriting addresses/ports and keeping a translation table. It saves IPv4 addresses and adds a layer of protection, since outsiders can't start connections to private devices.

**Q3: How many concurrent connections can a server handle on port 443 if there are only 65,535 ports?**
A3: The 65,535 limit applies to ports on one IP, but a connection is identified by the 4-tuple. All clients connect to the same server port 443, and each has a different source IP/port, so a server can hold millions of connections. The real limits are memory, file descriptors (`ulimit -n`) and CPU. The port limit matters on the **client** side, e.g. one Nginx making many outbound connections to one upstream, which can cause ephemeral port exhaustion. The fix is keep-alive connection reuse.

**Q4: Why should your database not have a public IP? How do you design network access for a typical web app?**
A4: To reduce the attack surface: if the DB port isn't reachable from the internet, it can't be brute-forced or exploited directly. The design: public subnet holds only the load balancer (443), private subnets hold app servers and databases, security groups allow traffic only from the layer in front (LB → App → DB), and outbound traffic goes through a NAT gateway. Admin access goes through a bastion host / VPN / AWS SSM.

**Q5: What is the difference between IPv4 and IPv6, and why hasn't IPv6 fully replaced IPv4?**
A5: IPv4 is 32-bit (~4.3B addresses); IPv6 is 128-bit (practically unlimited), removes the need for NAT, and has simpler headers. Adoption is slow because NAT extended IPv4's life, and old devices, ISPs and software need upgrades. Most systems run **dual stack** (both). Indian mobile networks like Jio are heavily IPv6, so your APIs should support AAAA records.

---

## 🔷 Trade-offs
✅ Advantages:
- Ports let one machine run many services → cheap, efficient servers.
- Private IPs + NAT save IPv4 space and hide internal machines.
- CIDR + security groups give fine-grained, simple firewall rules.

❌ Disadvantages:
- NAT breaks direct device-to-device connections (P2P, video calls need STUN/TURN; servers can't push without an open connection).
- IPv4 exhaustion → public IPs cost money (AWS charges for each public IPv4).
- Misconfigured ports (Docker publishing, 0.0.0.0/0 rules) are a common cause of data breaches.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| IP Address | Unique address of a device on a network | डिवाइस का नेटवर्क पता |
| Port | Number identifying a service on a device | प्रोग्राम का दरवाज़ा नंबर |
| Public IP | Reachable from the internet | इंटरनेट पर दिखने वाला पता |
| Private IP | Only inside local network | सिर्फ़ अंदरूनी नेटवर्क का पता |
| NAT | Many private IPs share one public IP | कई डिवाइस का एक सार्वजनिक पता |
| CIDR | Notation for IP ranges (10.0.0.0/16) | IP रेंज लिखने का तरीका |
| Localhost (127.0.0.1) | The machine itself | खुद की मशीन |
| Ephemeral Port | Temporary client-side port | अस्थायी पोर्ट |
| Security Group | AWS firewall by port + source | AWS का फ़ायरवॉल |

---

## ⚡ 3-Line Summary
**English:**
1. IP = which machine, Port = which program; a connection = (src IP, src port, dst IP, dst port).
2. Private IPs + NAT let many devices share a public IP; IPv6 solves the shortage permanently.
3. In production, expose only 443 on the load balancer; keep app and DB ports private.

**Hindi:**
1. IP = कौन सी मशीन, Port = कौन सा प्रोग्राम।
2. Private IP + NAT से कई डिवाइस एक public IP शेयर करते हैं; IPv6 में पते कभी ख़त्म नहीं होंगे।
3. Production में सिर्फ़ 443 पब्लिक रखो, DB और App पोर्ट प्राइवेट।

---

## ➡️ Next Topic Suggestion
**04. TCP vs UDP** — You now know how to reach a program (IP:Port). Next: the two ways to send data to it — reliable TCP (HTTP, DB connections) vs fast UDP (video calls, DNS, gaming) — and why HTTP/3 moved to UDP.
