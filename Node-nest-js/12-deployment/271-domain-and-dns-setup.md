# 271. Domain + DNS Setup
# हिंदी में: Domain + DNS Setup

---

## 🔵 Simple Definition (English)
**DNS (Domain Name System)** translates human-readable domain names (`api.zomato.com`) into IP addresses that computers use to connect (`52.21.34.12`). Setting up a domain means buying it from a registrar and creating **DNS records** that point it to your Node.js server/load balancer.

## 🔵 सरल परिभाषा (Hindi)
**DNS** human-readable domain names (`api.zomato.com`) को IP addresses में translate करता है जो computers connect करने के लिए use करते हैं (`52.21.34.12`)। Domain setup का मतलब है registrar से domain खरीदना और **DNS records** बनाना जो उसे आपके Node.js server/load balancer पर point करें।

---

## 🔴 Problem it Solves
Users can't remember/type raw IP addresses (`13.234.56.78`), and IPs change when you migrate servers or scale infrastructure. DNS provides a stable, memorable name that can be repointed to new IPs without users noticing. It also enables routing a single domain to multiple services via subdomains (`api.`, `admin.`, `cdn.`) and supports email delivery (MX records), ownership verification (TXT records), and load distribution.

## 🔴 यह क्यों बना? (Hindi)
Users raw IP addresses (`13.234.56.78`) याद नहीं रख सकते/type नहीं कर सकते, और server migrate/scale करने पर IPs बदलते रहते हैं। DNS एक stable, memorable नाम देता है जो users को पता चले बिना नए IPs पर repoint हो सकता है। ये एक domain को subdomains (`api.`, `admin.`, `cdn.`) के through multiple services में route करने देता है, और email delivery (MX records), ownership verification (TXT records) भी support करता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Buy a domain from a registrar (GoDaddy, Namecheap, AWS Route 53, Google Domains) — this registers you as the owner in a global registry.
Step 2 → Point the domain's **nameservers** to your DNS provider (could be the registrar itself, or Cloudflare, or AWS Route 53 for more control).
Step 3 → Create an **A record**: maps `yourdomain.com` → your server's public IPv4 address (e.g. EC2 Elastic IP).
Step 4 → Create a **CNAME record** for subdomains: `www.yourdomain.com` → `yourdomain.com`, or `api.yourdomain.com` → a load balancer's DNS name (ALB hostnames, not static IPs).
Step 5 → Propagation: DNS changes take anywhere from minutes to 48 hours to spread globally (cached by ISPs/resolvers based on **TTL** — time to live).
Step 6 → Verify with `dig yourdomain.com` or `nslookup yourdomain.com`, then proceed to SSL setup (Let's Encrypt needs DNS pointed correctly first).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Registrar (GoDaddy, Namecheap, Route 53) से domain खरीदो — ये आपको global registry में owner के रूप में register करता है।
Step 2 → Domain के **nameservers** को अपने DNS provider पर point करो (registrar खुद, या Cloudflare, या Route 53)।
Step 3 → **A record** बनाओ: `yourdomain.com` → server का public IPv4 address।
Step 4 → Subdomains के लिए **CNAME record**: `www.yourdomain.com` → `yourdomain.com`, या `api.yourdomain.com` → load balancer का DNS name।
Step 5 → Propagation: DNS changes global रूप से फैलने में मिनटों से 48 घंटे लग सकते हैं (**TTL** के आधार पर cache होता है)।
Step 6 → `dig yourdomain.com` से verify करो, फिर SSL setup पर जाओ।

---

## 🟡 Real World Example
**Swiggy** uses `www.swiggy.com` for the main app, `partner.swiggy.com` for restaurant partners, and `api.swiggy.com` for mobile app backend calls — all managed through Route 53 DNS. `api.swiggy.com` is a CNAME pointing to an AWS Application Load Balancer's DNS name (not a static IP, since ALB IPs can change) which routes to ECS-hosted Node.js services. When Swiggy migrates infrastructure or scales to a new region, they update the ALB behind the CNAME — users never notice any URL change.

## 🟡 Real Example Hindi mein
**Swiggy** main app के लिए `www.swiggy.com`, restaurant partners के लिए `partner.swiggy.com`, और mobile backend के लिए `api.swiggy.com` use करता है — सब Route 53 DNS से managed। `api.swiggy.com` एक CNAME है जो AWS ALB के DNS name पर point करता है (static IP नहीं, क्योंकि ALB IPs बदल सकते हैं)। Infrastructure migrate या scale करने पर, Swiggy CNAME के पीछे ALB update करता है — users को URL change का पता भी नहीं चलता।

---

## 💻 Code Example — Basic

```javascript
// dns-lookup-basic.js
// Node's built-in dns module can resolve domains programmatically
// Run with: node dns-lookup-basic.js

const dns = require('dns');

// resolve4: get IPv4 addresses for a domain (follows A records)
dns.resolve4('google.com', (err, addresses) => {
  if (err) {
    console.error('DNS lookup failed:', err.message);
    return;
  }
  console.log('A records (IPv4) for google.com:', addresses);
});

// resolveCname: check if a domain is a CNAME alias for another
dns.resolveCname('www.github.com', (err, aliases) => {
  if (err) {
    console.log('No CNAME found (might be a direct A record):', err.code);
    return;
  }
  console.log('CNAME target:', aliases);
});

// lookup: uses the OS resolver (respects /etc/hosts, local cache) — most common
dns.lookup('nodejs.org', (err, address, family) => {
  if (err) throw err;
  console.log(`nodejs.org resolves to ${address} (IPv${family})`);
});
```

## 💻 Code Example — Advanced

```javascript
// dns-advanced.js
// Production pattern: health-check DNS resolution before deploy,
// and verify SSL-readiness (domain must resolve before Certbot can issue a cert)

const dns = require('dns').promises; // Promise-based API

async function verifyDnsSetup(domain, expectedIp) {
  const results = { domain, checks: [] };

  try {
    // 1. Check A record resolves to the expected server IP
    const addresses = await dns.resolve4(domain);
    const matches = addresses.includes(expectedIp);
    results.checks.push({
      name: 'A record matches expected IP',
      passed: matches,
      found: addresses,
      expected: expectedIp,
    });
  } catch (err) {
    results.checks.push({ name: 'A record lookup', passed: false, error: err.code });
  }

  try {
    // 2. Check www subdomain is set up (common oversight)
    const wwwAddresses = await dns.resolve4(`www.${domain}`);
    results.checks.push({ name: 'www subdomain resolves', passed: true, found: wwwAddresses });
  } catch (err) {
    results.checks.push({ name: 'www subdomain resolves', passed: false, error: err.code });
  }

  try {
    // 3. Check TXT records (useful for domain-ownership verification, e.g. for SSL/DNS-01)
    const txtRecords = await dns.resolveTxt(domain);
    results.checks.push({ name: 'TXT records present', passed: true, found: txtRecords.flat() });
  } catch (err) {
    results.checks.push({ name: 'TXT records present', passed: false, error: err.code });
  }

  return results;
}

(async () => {
  const report = await verifyDnsSetup('yourdomain.com', '13.234.56.78');
  console.log(JSON.stringify(report, null, 2));

  const allPassed = report.checks.every((c) => c.passed);
  if (!allPassed) {
    console.warn('⚠️  DNS not fully propagated yet — wait and retry before running Certbot');
  } else {
    console.log('✅ DNS ready — safe to proceed with SSL cert issuance');
  }
})();
```

---

## 🟠 Express.js Integration

```javascript
// Express apps rarely do DNS work directly — DNS routes traffic TO your app
// before any Express code runs. But apps DO need to handle multiple domains
// (multi-tenant) and validate the Host header matches what's expected.

const express = require('express');
const app = express();

// Allowed hosts — protects against Host header injection attacks
const ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com', 'api.yourdomain.com'];

app.use((req, res, next) => {
  const host = req.headers.host?.split(':')[0]; // strip port if present
  if (!ALLOWED_HOSTS.includes(host)) {
    // Reject requests with a spoofed/unexpected Host header
    return res.status(421).json({ error: 'Misdirected Request' });
  }
  next();
});

// Subdomain-based routing (common for api./admin. subdomains pointing to same app)
app.use((req, res, next) => {
  const subdomain = req.headers.host.split('.')[0];
  req.isApiRequest = subdomain === 'api';
  next();
});

app.get('/', (req, res) => {
  res.json({
    message: req.isApiRequest ? 'API root' : 'Website root',
    host: req.headers.host,
  });
});

app.listen(3000, () => console.log('Listening — DNS routes traffic here via A/CNAME records'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Pointing a CNAME to a static IP target or an A record pointing to a dynamic hostname (mixing types)
✅ Correct: Use A records for static IPs, CNAME records for hostnames that may change (load balancers, CDNs) — and never set both an A and CNAME for the same subdomain (DNS spec forbids it at the root).

```javascript
// Wrong (conceptually): CNAME at the zone apex (yourdomain.com itself)
//   yourdomain.com  CNAME  some-load-balancer.aws.com   ← INVALID, DNS spec disallows
//   (apex/root domain must be an A/ALIAS record, not CNAME)

// Right: use an ALIAS record (Route53-specific) or A record at the apex
//   yourdomain.com      A      13.234.56.78
//   www.yourdomain.com  CNAME  yourdomain.com
```

❌ Mistake 2: Setting SSL/Certbot before DNS has propagated
✅ Correct: Verify DNS resolves correctly (`dig +short yourdomain.com`) BEFORE running Certbot — Let's Encrypt's HTTP-01 challenge fails if DNS doesn't point to your server yet.

```javascript
// Wrong order: run certbot immediately after changing DNS
// → fails with "DNS problem: NXDOMAIN looking up A for yourdomain.com"

// Right order:
// 1. Update DNS A record
// 2. Wait for propagation, verify: dig +short yourdomain.com
// 3. Once it returns the correct IP, THEN run certbot
```

---

## 🧠 Tricky Interview Question

```javascript
// What's the catch with this code if run right after changing DNS records?
const dns = require('dns');
dns.lookup('yourdomain.com', (err, address) => {
  console.log(address); // might print the OLD IP even hours after the DNS change!
});
```
Answer: `dns.lookup` uses the OS-level resolver, which respects caching at multiple layers — your OS's DNS cache, your router, your ISP's resolver, and the TTL set on the DNS record itself. If the old record had `TTL=86400` (24 hours), resolvers that already cached it won't re-query until that TTL expires, even though the authoritative DNS server now has the new value. This is why `dig +trace yourdomain.com` or `dig @8.8.8.8 yourdomain.com` (querying a specific resolver directly, bypassing local cache) is used to check the ACTUAL current state, and why lowering TTL BEFORE a planned migration (to e.g. 60 seconds) minimizes propagation delay.

---

## ⚫ Interview Questions + Answers

Q1: What's the difference between an A record and a CNAME record?
A1: An **A record** maps a domain directly to an IPv4 address (`yourdomain.com → 13.234.56.78`). A **CNAME record** maps a domain to ANOTHER domain name, not an IP (`www.yourdomain.com → yourdomain.com`, or `api.yourdomain.com → my-alb-123.us-east-1.elb.amazonaws.com`). CNAMEs are preferred when the target's IP can change (load balancers, CDNs) since you only need to update one place. CNAMEs cannot be used at the zone apex (bare domain) per DNS spec — use an A record or provider-specific ALIAS record there instead.

Q2: What is TTL in DNS and why does it matter for deployments?
A2: TTL (Time To Live) tells resolvers how long (in seconds) to cache a DNS record before re-querying. High TTL (e.g. 86400s/24h) reduces DNS query load but means changes propagate slowly. Low TTL (e.g. 60s) propagates changes fast but increases query volume/cost. Before planned infrastructure migrations (new server IP, switching load balancers), lower the TTL days in advance so the eventual cutover propagates quickly.

Q3: How does Let's Encrypt's HTTP-01 challenge depend on DNS being correctly configured?
A3: HTTP-01 challenge requires Let's Encrypt's servers to reach `http://yourdomain.com/.well-known/acme-challenge/<token>` — this only works if the domain's A/CNAME record already points to the server running Certbot. If DNS isn't propagated yet, the challenge request either times out or hits the wrong server, and certificate issuance fails with a DNS/connection error.

Q4: What are MX and TXT records used for?
A4: **MX (Mail Exchange)** records specify which mail servers handle email for the domain (e.g. pointing to Google Workspace or SendGrid's servers) — critical for `support@yourdomain.com` to work. **TXT** records hold arbitrary text, commonly used for: domain ownership verification (Google Search Console, SSL DNS-01 challenges), SPF records (anti-spam, specifying which servers can send email as your domain), and DKIM/DMARC email authentication.

Q5: How would you set up a multi-region Node.js deployment using DNS?
A5: Use DNS-based load balancing/failover: Route 53 (or Cloudflare) supports **latency-based routing** (directs users to the nearest region) or **health-check-based failover** (if the primary region's health check fails, DNS automatically starts resolving to the secondary region's IP/ALB). Each region runs its own Node.js app behind its own load balancer; the Node app code itself needs no awareness of this — it's purely a DNS/infra-layer concern, though apps should expose a reliable `/health` endpoint that the DNS provider's health checker polls.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Launching any public-facing production application
- Needing branded, memorable URLs instead of raw IPs
- Routing traffic to multiple services via subdomains, or across regions

❌ Avoid when:
- Internal-only services with no external access requirement — a private DNS zone or `/etc/hosts` entry may suffice, no need for public registration
- Rapid local prototyping — `localhost` or `ngrok` tunnels are faster for demos than configuring real DNS

---

## 📊 Visual Diagram
```
USER TYPES: www.yourdomain.com
        │
        ▼
┌───────────────────┐
│ Browser's local    │  (checks OS cache first)
│ DNS cache          │
└─────────┬──────────┘
          │ cache miss
          ▼
┌───────────────────┐
│ ISP's DNS resolver  │  (checks its own cache, respects TTL)
└─────────┬──────────┘
          │ cache miss
          ▼
┌───────────────────┐        ┌─────────────────────┐
│ Your DNS provider's │──────► │ Zone records:         │
│ nameservers         │        │ A:     13.234.56.78   │
│ (Route53/Cloudflare)│        │ CNAME: www → apex      │
└─────────┬──────────┘        └─────────────────────┘
          │ returns IP
          ▼
┌───────────────────┐
│ Your server          │  Node.js app running here,
│ 13.234.56.78          │  behind Nginx (SSL) on port 443
└───────────────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| A Record | Maps domain → IPv4 address | Domain को IPv4 address से map करता है |
| CNAME | Maps domain → another domain name | Domain को किसी और domain name से map करता है |
| TTL | Cache duration for a DNS record | DNS record की cache duration |
| Nameserver | Server holding a domain's DNS zone records | Domain के DNS zone records रखने वाला server |
| Propagation | Time for DNS change to spread globally | DNS change global रूप से फैलने में लगने वाला समय |
| Registrar | Company where you buy/register a domain | Domain खरीदने/register करने वाली company |

---

## ⚡ 3-Line Summary
English: 1. DNS maps human domain names to server IPs via A records (direct IP) and CNAME records (alias to another hostname). 2. Changes take time to propagate based on TTL — verify with `dig` before dependent steps like SSL issuance. 3. CNAMEs are preferred for load-balancer/CDN targets since the underlying IP can change without updating your DNS config.
Hindi: 1. DNS domain names को server IPs से map करता है — A record (direct IP), CNAME (किसी और hostname का alias)। 2. Changes propagate होने में TTL के आधार पर समय लगता है — SSL issuance से पहले `dig` से verify करो। 3. Load-balancer/CDN के लिए CNAME बेहतर है क्योंकि underlying IP बिना DNS बदले change हो सकता है।

---

## ➡️ Next Topic
**272. Node.js Production Checklist** — deploy से पहले security, performance, monitoring की पूरी checklist।
