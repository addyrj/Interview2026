# 02. DNS — Domain Name System
# हिंदी में: DNS — इंटरनेट की फ़ोनबुक, जो नाम (swiggy.com) को नंबर (IP Address) में बदलती है

---

## 🔵 Simple Definition (English)
DNS converts a human-friendly **domain name** (`swiggy.com`) into a machine address — an **IP address** (`13.235.10.20`).
It is a huge, distributed, cached "phonebook" of the internet.

## 🔵 सरल परिभाषा (Hindi)
DNS डोमेन नाम (जैसे swiggy.com) को IP Address (जैसे 13.235.10.20) में बदलता है।
जैसे फ़ोन में नाम सेव होता है और कॉल नंबर पर जाती है — वैसे ही DNS नाम से नंबर ढूँढता है।

---

## 🔴 Problem it Solves
- Computers only understand IP addresses. Humans can't remember `142.250.183.14` for Google.
- IPs **change** (new server, new region, failover). If users bookmarked IPs, every change would break them.
- In the early internet, one file (`HOSTS.TXT`) kept all names, downloaded manually by everyone. With millions of domains that became impossible.

DNS solves this by being:
1. **Human-friendly** — names instead of numbers.
2. **Distributed** — no single server holds everything; responsibility is split by hierarchy (`.` → `.com` → `swiggy.com`).
3. **Cached** — answers are remembered at many levels for a TTL, so lookups are fast.
4. **Flexible** — you can change the IP behind a name without users noticing.

## 🔴 यह क्यों बना? (Hindi)
कंप्यूटर सिर्फ़ IP समझता है, पर इंसान को नंबर याद नहीं रहते। साथ ही सर्वर का IP बदलता रहता है।
पहले एक ही फ़ाइल में सारे नाम थे — करोड़ों डोमेन के लिए यह नहीं चल सकता था। DNS ने इसे बाँटकर (hierarchy) और कैश करके तेज़ और बड़ा बनाया।

---

## 🟢 How it Works — Step by Step

### The hierarchy

```
                       . (Root)          ← 13 root server "names", 1000s of machines (anycast)
            ┌──────────┼──────────┐
          .com        .in        .org     ← TLD servers (Top-Level Domain)
           │           │
      swiggy.com    gov.in               ← Authoritative name servers (e.g. AWS Route 53)
           │
   www / api / cdn                        ← Records inside the zone
```

### Full lookup (cache miss)

```
 Browser            OS / Resolver         Root        .com TLD      Route 53 (Authoritative
 (cache?)           (ISP or 8.8.8.8)      Server      Server        for swiggy.com)
    │                    │                  │            │                 │
    │ 1. api.swiggy.com? │                  │            │                 │
    │───────────────────►│ 2. Who has .com? │            │                 │
    │                    │─────────────────►│            │                 │
    │                    │◄── "ask .com TLD"│            │                 │
    │                    │ 3. Who has swiggy.com?        │                 │
    │                    │──────────────────────────────►│                 │
    │                    │◄── "ask ns-1.awsdns.com" ─────│                 │
    │                    │ 4. IP of api.swiggy.com?                        │
    │                    │────────────────────────────────────────────────►│
    │                    │◄────────── "13.235.10.20, TTL 60s" ─────────────│
    │◄── 13.235.10.20 ───│  (resolver caches it for 60s)                   │
    │                    │                                                 │
 5. Browser connects to 13.235.10.20:443
```

```
Step 1 → Browser cache → OS cache (/etc/hosts too) → if found, done (0 ms)
Step 2 → Ask the Recursive Resolver (your ISP's, or 8.8.8.8 / 1.1.1.1)
Step 3 → Resolver asks Root → "go to .com TLD"
Step 4 → Resolver asks .com TLD → "go to swiggy's authoritative server"
Step 5 → Resolver asks Authoritative server → gets the IP + TTL
Step 6 → Resolver caches for TTL and returns the IP to you
```

## 🟢 कैसे काम करता है? (Hindi)
1. पहले ब्राउज़र और OS का कैश देखा जाता है — मिल गया तो तुरंत जवाब।
2. नहीं मिला तो Resolver (Jio का या 8.8.8.8) से पूछा जाता है।
3. Resolver → Root से पूछता है "`.com` किसके पास है?" → फिर `.com` TLD से "swiggy.com किसके पास है?"
4. आख़िर में Authoritative सर्वर (जैसे Route 53) असली IP बताता है।
5. Resolver इस जवाब को TTL तक याद (cache) रखता है ताकि अगली बार तेज़ हो।

> 💡 **Recursive resolver** does all the running around for you. **Authoritative server** is the final source of truth for a domain (the one you configure in Route 53 / Cloudflare / GoDaddy).

### Common DNS record types (must know)

```
┌────────┬────────────────────────────────────┬────────────────────────────────────────┐
│ Type   │ Meaning                            │ Example                                │
├────────┼────────────────────────────────────┼────────────────────────────────────────┤
│ A      │ Name → IPv4                        │ api.myapp.com  → 13.235.10.20          │
│ AAAA   │ Name → IPv6                        │ api.myapp.com  → 2406:da1a::1          │
│ CNAME  │ Name → another name (alias)        │ www.myapp.com  → myapp.vercel.app      │
│ ALIAS/ │ Like CNAME but allowed at root     │ myapp.com      → my-alb.elb.aws.com    │
│ ANAME  │ (Route 53 "Alias" record)          │                                        │
│ MX     │ Mail server for the domain         │ myapp.com      → mail.google.com       │
│ TXT    │ Free text — verification, SPF/DKIM │ "google-site-verification=abc"         │
│ NS     │ Which servers are authoritative    │ myapp.com      → ns-1.awsdns-01.com    │
│ SOA    │ Zone admin info, serial number     │ (auto-created)                         │
│ CAA    │ Which CA can issue SSL certs       │ 0 issue "letsencrypt.org"              │
└────────┴────────────────────────────────────┴────────────────────────────────────────┘
```

### TTL — Time To Live

```
TTL = how long resolvers may cache the answer.

High TTL (86400s = 1 day)  → fast for users, fewer DNS queries, BUT IP change takes up to 1 day to reach everyone
Low  TTL (60s)             → changes spread fast (good for failover), BUT more DNS queries

Pro tip: Before a migration, lower TTL to 60s a day earlier → migrate → raise TTL again.
```

### DNS used for system design (not just name lookup)

```
1. DNS Load Balancing (Round Robin)
   api.myapp.com → [13.1.1.1, 13.1.1.2, 13.1.1.3]   (client picks one)

2. Geo / Latency-based routing (Route 53)
   User in India  → ap-south-1 (Mumbai) IP
   User in USA    → us-east-1 IP

3. Failover routing
   Health check on primary fails → DNS starts returning secondary region's IP

4. Weighted routing (canary release)
   90% → old version, 10% → new version
```

---

## 🟡 Real World Example

**Hotstar during an India–Pakistan match**
- Millions of users open the app at the same time. DNS for Hotstar's domains uses **latency-based / geo routing** to send users to the nearest CDN edge (Akamai/CloudFront) instead of a single origin.
- The CDN domains have low TTLs so traffic can be shifted between edges/providers within minutes if one gets overloaded.

**The Facebook outage (Oct 2021)**
- A bad config change withdrew the BGP routes to Facebook's **authoritative DNS servers**. No one in the world could resolve `facebook.com` → Facebook, Instagram, WhatsApp were down for ~6 hours, even though the servers themselves were running.
- Lesson: **DNS is a critical dependency / potential single point of failure.** Big companies use multiple DNS providers.

**Dyn DDoS attack (2016)**
- Attackers flooded Dyn (a DNS provider) → Twitter, GitHub, Netflix, Reddit unreachable for hours in parts of the US. Again: DNS = critical infrastructure.

## 🟡 Real Example Hindi में
Hotstar मैच के समय DNS से यूज़र को सबसे पास वाले CDN सर्वर पर भेजता है, ताकि करोड़ों लोग एक साथ देख सकें।
2021 में Facebook के DNS सर्वर इंटरनेट से कट गए — सर्वर चालू थे, फिर भी 6 घंटे तक कोई facebook.com नहीं खोल पाया। सीख: DNS भी एक "single point of failure" है।

---

## 🟠 My Stack Example

### Typical DNS setup for your full-stack app (Route 53 / Cloudflare)
```
myapp.com          ALIAS  →  Vercel / CloudFront     (Next.js web)
www.myapp.com      CNAME  →  myapp.com
api.myapp.com      A      →  13.235.10.20 (EC2 / VPS running Nginx → Node/FastAPI)
                    or ALIAS → my-alb-123.ap-south-1.elb.amazonaws.com (AWS ALB)
cdn.myapp.com      CNAME  →  d1234.cloudfront.net    (S3 images)
myapp.com          MX     →  Google Workspace mail
myapp.com          TXT    →  "v=spf1 include:_spf.google.com ~all"
```

> ⚠️ Never hardcode an AWS load balancer's IP — ALB IPs change. Always use ALIAS/CNAME to its DNS name.

### Debugging DNS
```bash
dig api.myapp.com              # full answer + TTL
dig +short api.myapp.com       # just the IP
dig api.myapp.com @8.8.8.8     # ask Google's resolver specifically
dig +trace api.myapp.com       # see Root → TLD → Authoritative chain
nslookup api.myapp.com         # simple alternative
```

### Docker Compose — DNS inside your containers
Docker has its own internal DNS. Service names become hostnames:
```yaml
services:
  api:
    build: .
    environment:
      DATABASE_URL: postgres://user:pass@db:5432/app   # "db" resolved by Docker DNS
      REDIS_URL: redis://redis:6379
  db:
    image: postgres:16
  redis:
    image: redis:7
```
Same idea in Kubernetes: `http://payment-service.default.svc.cluster.local` → this is **service discovery via DNS** (Topic 92).

### Node.js — DNS lookups cost time
```js
// Node's http client calls dns.lookup() for every new connection.
// Reuse connections (keep-alive) so you don't pay DNS + TCP + TLS each time.
import { Agent, setGlobalDispatcher } from 'undici';
setGlobalDispatcher(new Agent({ keepAliveTimeout: 30_000, connections: 100 }));

// Now fetch() to external APIs (payment gateway, SMS) reuses sockets
await fetch('https://api.razorpay.com/v1/orders', { method: 'POST', /* ... */ });
```

### React Native / Next.js — warm up DNS early
```html
<!-- Next.js: in app/layout.tsx <head> — resolve DNS for other domains before needed -->
<link rel="dns-prefetch" href="https://cdn.myapp.com" />
<link rel="preconnect" href="https://api.myapp.com" crossorigin />
```

---

## ⚫ Interview Questions + Answers

**Q1: Explain how DNS resolution works.**
A1: Browser cache → OS cache → recursive resolver (ISP / 8.8.8.8). On a miss, the resolver asks a root server (which points to the TLD server), then the TLD server (which points to the domain's authoritative server), then the authoritative server, which returns the IP and a TTL. The resolver caches it for the TTL and returns it to the client.

**Q2: What's the difference between an A record and a CNAME?**
A2: An A record maps a name directly to an IPv4 address. A CNAME maps a name to another name (alias), which is then resolved further. CNAMEs can't be used at the zone apex (`myapp.com`) per the DNS standard, so providers offer ALIAS/ANAME records (Route 53 Alias) for that case.

**Q3: What is TTL, and how do you choose it?**
A3: TTL is how long a DNS answer can be cached. A high TTL reduces lookups and latency but slows down changes. A low TTL (30–60s) allows fast failover and migrations but increases DNS traffic. Use a low TTL for records you might fail over (API, LB) and a higher one for stable records (MX). Lower the TTL before planned migrations.

**Q4: How can DNS be used for load balancing and failover? What are its limits?**
A4: Return multiple IPs (round robin), return different IPs based on user location/latency (geo routing), or switch IPs when health checks fail (failover routing), all supported by Route 53. Limits: clients and resolvers cache answers, so traffic doesn't shift instantly; some ignore TTL; DNS doesn't know real-time server load. That's why DNS is used for coarse routing (region-level), and a real load balancer is used inside the region.

**Q5: Is DNS TCP or UDP? Why?**
A5: Mostly **UDP on port 53**, because queries are tiny and one round trip is enough, with no handshake overhead. It falls back to **TCP** when the response is too large (more than 512 bytes classic / EDNS limits, e.g. DNSSEC) and for zone transfers between DNS servers. Modern privacy options are DNS-over-HTTPS (DoH) and DNS-over-TLS (DoT).

---

## 🔷 Trade-offs
✅ Advantages:
- Human-friendly names; IPs can change behind the scenes.
- Highly scalable thanks to hierarchy + caching everywhere.
- Doubles as a global traffic manager (geo, weighted, failover routing).

❌ Disadvantages:
- Caching = changes are not instant (propagation delay).
- A DNS provider outage can take your whole product offline (single point of failure).
- Plain DNS is unencrypted → spoofing/cache poisoning risk (mitigated by DNSSEC, DoH).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Domain Name | Human-readable address (swiggy.com) | वेबसाइट का नाम |
| Recursive Resolver | Server that finds the answer for you | आपकी तरफ़ से जवाब ढूँढने वाला सर्वर |
| Authoritative Server | Final source of truth for a domain | डोमेन का असली रिकॉर्ड रखने वाला सर्वर |
| TLD | Top-level domain (.com, .in) | सबसे ऊपर का डोमेन हिस्सा |
| A Record | Name → IPv4 | नाम से IP का रिकॉर्ड |
| CNAME | Name → another name | उपनाम (alias) |
| TTL | Cache lifetime of a DNS answer | कैश में रखने का समय |
| Propagation | Time for DNS change to reach everyone | बदलाव फैलने में लगने वाला समय |

---

## ⚡ 3-Line Summary
**English:**
1. DNS converts domain names to IP addresses using a hierarchy: Root → TLD → Authoritative.
2. Answers are cached everywhere for a TTL — fast lookups, but changes take time to spread.
3. DNS is also a traffic tool (geo, weighted, failover routing) and a critical single point of failure.

**Hindi:**
1. DNS नाम को IP में बदलता है: Root → TLD → Authoritative सर्वर।
2. जवाब TTL तक कैश होता है — तेज़ है, पर बदलाव में समय लगता है।
3. DNS से ट्रैफ़िक रूटिंग भी होती है, और यह डाउन हुआ तो पूरी साइट डाउन।

---

## ➡️ Next Topic Suggestion
**03. IP Address + Ports** — DNS gives you an IP. Next: what an IP really is (public vs private, IPv4 vs IPv6, NAT) and how **ports** let one server run Nginx, Node, Postgres and Redis at the same time.
