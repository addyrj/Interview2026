# 12. Forward Proxy
# हिंदी में: Forward Proxy — क्लाइंट की तरफ़ से इंटरनेट पर request भेजने वाला बिचौलिया सर्वर

---

## 🔵 Simple Definition (English)
A **forward proxy** sits **in front of clients**. Clients send their outgoing requests to the proxy, and the proxy forwards them to the internet on their behalf. The destination server sees the **proxy's IP**, not the client's.
Examples: corporate/school proxies, VPNs, Squid, outbound (egress) proxies and NAT gateways used by servers.

## 🔵 सरल परिभाषा (Hindi)
Forward proxy क्लाइंट्स के आगे खड़ा रहता है — क्लाइंट की request पहले proxy पर जाती है, फिर proxy उसे इंटरनेट पर भेजता है।
बाहर का सर्वर proxy का IP देखता है, असली क्लाइंट का नहीं।

---

## 🔴 Problem it Solves
Organizations need to **control and observe outgoing traffic**:
- **Security / policy:** block malware sites, social media at work, data leaks.
- **Privacy / anonymity:** hide the user's real IP (VPN, Tor).
- **Access:** reach geo-restricted content, or reach internal resources from outside (VPN).
- **Caching:** an office of 500 people downloading the same Windows update → download once, serve locally.
- **Fixed IP for whitelisting (very common in backend!):** banks and payment gateways only accept calls from **known IPs**. Your auto-scaling servers have random IPs → route outbound calls through a proxy / NAT gateway with **one static IP**.
- **Auditing:** log every external call for compliance.

## 🔴 यह क्यों बना? (Hindi)
कंपनियों को बाहर जाने वाले ट्रैफ़िक पर नियंत्रण चाहिए — ख़तरनाक साइट रोकना, लॉग रखना, cache करना।
Backend में भी ज़रूरी: बैंक/पेमेंट गेटवे सिर्फ़ तय IP से आई request मानते हैं, जबकि हमारे सर्वरों के IP बदलते रहते हैं — इसलिए सब बाहर की कॉल एक fixed IP वाले proxy/NAT से भेजते हैं।

---

## 🟢 How it Works — Step by Step

```
 ┌──────────┐
 │ Laptop A │──┐
 └──────────┘  │     ┌──────────────────┐       ┌──────────────┐
 ┌──────────┐  ├────►│  Forward Proxy   │──────►│  Internet    │──► youtube.com
 │ Laptop B │──┤     │ - allow/deny list│       └──────────────┘    sees proxy IP
 └──────────┘  │     │ - cache          │                           (203.0.113.5)
 ┌──────────┐  │     │ - log            │
 │ Laptop C │──┘     │ - auth (user/pw) │
 └──────────┘        └──────────────────┘

Step 1 → Client is configured to use proxy (browser setting, PAC file, HTTPS_PROXY env var)
Step 2 → Client sends request to proxy: "GET http://example.com/" or "CONNECT example.com:443"
Step 3 → Proxy checks policy (blocked? authenticated?) and cache
Step 4 → Proxy opens its own connection to the destination
Step 5 → Response flows back through proxy to client (cached if allowed)
```

### HTTPS through a forward proxy — the CONNECT tunnel

```
Client ── "CONNECT api.razorpay.com:443" ──► Proxy
Proxy  ── opens TCP to razorpay:443 ──► "200 Connection Established"
Client ════ TLS handshake + encrypted data THROUGH the tunnel ════► Razorpay
Proxy sees only: destination host + bytes count. NOT the content.

(Unless TLS inspection: proxy has its own CA installed on client machines,
 decrypts & re-encrypts → "legal man-in-the-middle" in corporates.)
```

### Types

```
┌─────────────────────┬─────────────────────────────────────────────────────┐
│ Type                │ Use                                                 │
├─────────────────────┼─────────────────────────────────────────────────────┤
│ Corporate proxy     │ Filter, log, cache employee browsing (Zscaler,Squid)│
│ VPN                 │ Encrypted tunnel; all traffic exits from VPN server │
│ Anonymous / Tor     │ Hide identity (onion routing through 3 relays)      │
│ Egress proxy / NAT  │ Servers' outbound calls exit via fixed IP           │
│ Gateway             │ (AWS NAT Gateway, Squid in VPC)                     │
│ Transparent proxy   │ Intercepts without client config (ISP, school Wi-Fi)│
│ Residential proxies │ Scraping using real home IPs (often abused)         │
└─────────────────────┴─────────────────────────────────────────────────────┘
```

### Forward vs Reverse (remember)

```
             Forward Proxy                 Reverse Proxy
Sits near    Clients                       Servers
Hides        Client identity               Server identity
Controlled by Client's org                 Server's org
Example      VPN, corporate proxy, NAT GW  Nginx, Cloudflare, ALB
```

## 🟢 कैसे काम करता है? (Hindi)
1. क्लाइंट में proxy सेट होता है (ब्राउज़र setting या `HTTPS_PROXY` env)।
2. क्लाइंट request proxy को भेजता है; proxy नियम जाँचता है (blocked है? login है?)।
3. Proxy ख़ुद बाहर के सर्वर से कनेक्शन बनाता है — सर्वर को proxy का IP दिखता है।
4. HTTPS में proxy सिर्फ़ "CONNECT" से सुरंग (tunnel) बनाता है; अंदर का डेटा एन्क्रिप्टेड रहता है।
5. जवाब proxy से होकर क्लाइंट तक आता है, और ज़रूरत हो तो cache भी होता है।

---

## 🟡 Real World Example

**Payment gateway IP whitelisting (very common in Indian fintech)**
- Banks/NPCI partners and some payment APIs require: "Send requests only from these 2 IPs". A company running 40 auto-scaling ECS tasks routes all outbound traffic from private subnets through an **AWS NAT Gateway with an Elastic IP**, and gives that one IP to the bank.

**Zscaler at large companies (TCS, Infosys, banks)**
- Every employee laptop routes traffic through Zscaler's cloud forward proxy, which blocks malicious sites, prevents data upload to personal drives, and inspects TLS.

**Netflix and VPNs**
- Users use VPNs (forward proxies) to appear in another country. Netflix detects known VPN/datacenter IP ranges and blocks them. That's a cat-and-mouse game over forward-proxy IPs.

**Web scraping**
- Price comparison sites route scrapers through rotating proxy pools so the target site doesn't block a single IP.

## 🟡 Real Example Hindi में
भारत की fintech कंपनियाँ बैंक API को सिर्फ़ एक fixed IP से कॉल करती हैं — सारे सर्वर AWS NAT Gateway (Elastic IP) से बाहर जाते हैं, और बैंक वही एक IP whitelist करता है।
बड़ी IT कंपनियों में Zscaler जैसा proxy हर कर्मचारी के ट्रैफ़िक को जाँचता है और ख़तरनाक साइट ब्लॉक करता है।

---

## 🟠 My Stack Example

### AWS: private servers → NAT Gateway (static IP) → payment API
```
VPC 10.0.0.0/16
 ├─ Public subnet:  ALB, NAT Gateway (Elastic IP 3.110.x.x)  ← give THIS IP to bank
 └─ Private subnet: ECS/EC2 Node.js tasks (no public IP)
        │ route table: 0.0.0.0/0 → NAT Gateway
        └──► api.bank.com sees 3.110.x.x
```

### On a VPS: Squid as an egress proxy (allow-list only needed domains)
```conf
# /etc/squid/squid.conf
acl allowed_sites dstdomain .razorpay.com .twilio.com .amazonaws.com
http_access allow allowed_sites
http_access deny all
http_port 3128
```
This also limits damage if your server is hacked — malware can't call random domains (data exfiltration protection).

### Node.js — send outbound calls via proxy
```js
import { ProxyAgent, setGlobalDispatcher } from 'undici';
if (process.env.HTTPS_PROXY) setGlobalDispatcher(new ProxyAgent(process.env.HTTPS_PROXY));
await fetch('https://api.razorpay.com/v1/payments');   // goes through proxy

// axios
import { HttpsProxyAgent } from 'https-proxy-agent';
axios.create({ httpsAgent: new HttpsProxyAgent(process.env.HTTPS_PROXY), proxy: false });
```

### Python / FastAPI — httpx and requests respect env vars
```python
# HTTPS_PROXY=http://squid.internal:3128  NO_PROXY=localhost,10.0.0.0/8,db,redis
async with httpx.AsyncClient(proxy=os.environ.get("HTTPS_PROXY"), timeout=10) as client:
    r = await client.post("https://api.bank.com/v1/transfer", json=payload)
```

### Docker — build behind a corporate proxy
```dockerfile
ARG HTTPS_PROXY
ENV HTTPS_PROXY=${HTTPS_PROXY} NO_PROXY=localhost,127.0.0.1
RUN npm ci
```

### React Native / Mobile dev
- **Charles / Proxyman / mitmproxy** are forward proxies you run on your laptop to inspect your app's API calls (install their CA on the simulator). Great for debugging. It's also exactly how attackers inspect apps, which is why sensitive apps use **SSL pinning** (Topic M15).

---

## ⚫ Interview Questions + Answers

**Q1: What is a forward proxy and how is it different from a reverse proxy?**
A1: A forward proxy acts on behalf of clients: it sends their outbound requests and hides their IPs, and the client's organization controls it (VPN, corporate proxy, NAT gateway). A reverse proxy acts on behalf of servers: it receives inbound requests and hides backend servers, and the server's organization controls it (Nginx, Cloudflare). Same mechanics, opposite sides.

**Q2: How does a forward proxy handle HTTPS if traffic is encrypted?**
A2: The client sends `CONNECT host:443`. The proxy opens a TCP connection to that host and blindly relays bytes, and the TLS handshake happens end-to-end between client and server. The proxy only sees the hostname (from CONNECT/SNI) and traffic volume. To see content, the proxy must do TLS interception with its own CA installed on clients (common in enterprises).

**Q3: Your payment partner requires a fixed source IP but your app auto-scales. What do you do?**
A3: Put app instances in private subnets and route outbound traffic through a NAT gateway with an Elastic IP (or a dedicated egress proxy like Squid or Envoy), then share that static IP with the partner. For high availability, use one NAT gateway per AZ (each with its own EIP, so whitelist all of them). Also add timeouts, retries and monitoring on that path, because it's now a critical dependency.

**Q4: What are the security benefits of an egress proxy for backend servers?**
A4: It allow-lists the external domains services can call, which blocks data exfiltration and command-and-control callbacks if a server is compromised. It centralizes logging and auditing of outbound calls (for compliance), applies uniform TLS and timeout policies, and gives a single place to rotate IPs. SSRF damage is also limited, because requests to internal or metadata IPs can be blocked.

**Q5: What is a transparent proxy?**
A5: A proxy that intercepts traffic without the client being configured, usually by network routing (ISPs, school or hotel Wi-Fi captive portals). Clients don't know it's there. It can cache and filter HTTP, but can only see hostnames for HTTPS unless it does TLS interception, which causes certificate warnings unless the CA is trusted.

---

## 🔷 Trade-offs
✅ Advantages:
- Central control, filtering and logging of outbound traffic.
- Privacy/anonymity for clients; static egress IP for servers.
- Caching saves bandwidth for many clients.

❌ Disadvantages:
- Extra hop → latency; single point of failure if not HA.
- TLS inspection raises privacy concerns and breaks pinned apps.
- Configuration pain (`NO_PROXY` for internal hosts, Docker builds, CI).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Forward Proxy | Proxy on the client side | क्लाइंट की तरफ़ का बिचौलिया |
| Egress | Outgoing traffic | बाहर जाने वाला ट्रैफ़िक |
| NAT Gateway | AWS service giving private servers internet via static IP | प्राइवेट सर्वर का बाहर जाने का रास्ता |
| IP Whitelisting | Only allow known IPs | सिर्फ़ तय IP को अनुमति |
| CONNECT tunnel | Proxy relays encrypted HTTPS bytes | एन्क्रिप्टेड सुरंग |
| TLS Inspection | Proxy decrypts HTTPS using own CA | HTTPS को बीच में खोलना |
| VPN | Encrypted tunnel to another network | सुरक्षित सुरंग |
| SSRF | Tricking server into calling internal URLs | सर्वर से अंदरूनी URL कॉल करवाना |

---

## ⚡ 3-Line Summary
**English:**
1. Forward proxy = acts for clients on outgoing requests; destination sees the proxy's IP.
2. Used for filtering, privacy (VPN), caching, auditing, and giving servers a static egress IP.
3. In AWS, a NAT Gateway with Elastic IP is the standard way to get a whitelisted outbound IP.

**Hindi:**
1. Forward proxy = क्लाइंट की तरफ़ से बाहर request भेजता है; सर्वर को proxy का IP दिखता है।
2. Filtering, VPN, cache, logging और fixed outbound IP के लिए इस्तेमाल।
3. AWS में NAT Gateway + Elastic IP से bank whitelisting होती है।

---

## ➡️ Next Topic Suggestion
**13. Monolith Architecture** — Networking basics are done. Next: how to structure the application itself, starting with the monolith: what it is, why most successful products start with one, and when it starts to hurt.
