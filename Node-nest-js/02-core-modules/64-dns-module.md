# 64. dns Module
# हिंदी में: dns Module — Domain Name को IP में बदलना

---

## 🔵 Simple Definition (English)
The **`dns`** module lets Node.js resolve domain names (like `api.razorpay.com`) into IP addresses, and do the reverse too. It has two modes: `dns.lookup()` (uses OS resolver, like `ping` does) and `dns.resolve*()` functions (talk directly to DNS servers, bypassing OS cache — more control, more detail like TTL, MX records, etc).

## 🔵 सरल परिभाषा (Hindi)
**`dns`** module domain names (जैसे `api.razorpay.com`) को IP address में convert करता है, और reverse भी कर सकता है। दो modes हैं: `dns.lookup()` (OS resolver use करता है, जैसे `ping`) और `dns.resolve*()` functions (directly DNS servers से बात करते हैं — ज्यादा detail जैसे TTL, MX records मिलते हैं)।

---

## 🔴 Problem it Solves
```
BEFORE dns MODULE:
  Your app wants to call https://api.payment-gateway.com
  Browser/OS handles DNS automatically — but Node needs programmatic control:
  - Pre-resolve hostnames to warm up connections (reduce latency)
  - Debug "which IP is this hostname actually resolving to?"
  - Build custom load balancers / service discovery
  - Check MX records before sending email (verify domain can receive mail)
  - Detect DNS outages before making HTTP calls

WITH dns MODULE:
  dns.lookup('api.payment-gateway.com', (err, address) => {
    console.log(address); // '104.18.32.7'
  });
  → Full programmatic control over name resolution
```

## 🔴 यह क्यों बना? (Hindi)
```
Node apps को hostname → IP resolution पर control चाहिए था:
- Latency कम करने के लिए pre-resolve / connection warm-up
- Service discovery/load balancing के custom logic के लिए
- Email से पहले MX records verify करने के लिए
dns module ये सब programmatically possible बनाता है
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → require('dns') to get the module
Step 2 → Choose API: dns.lookup() (OS-level, uses /etc/hosts + OS cache)
          OR dns.resolve4()/resolve6()/resolveMx() etc (pure DNS query)
Step 3 → dns.lookup() calls getaddrinfo() in libuv's THREAD POOL (blocking call, offloaded)
Step 4 → dns.resolve*() sends UDP packets directly to DNS server (non-blocking, c-ares library)
Step 5 → Callback/Promise returns resolved IP address(es) or records
Step 6 → App uses the IP to make the actual TCP/HTTP connection
```

## 🟢 कैसे काम करता है? (Hindi)
```
1. require('dns') module import करो
2. dns.lookup() (OS resolver, thread pool में चलता है) या dns.resolve*() (direct DNS query, c-ares) चुनो
3. Callback/Promise में resolved IP मिलती है
4. उस IP से आगे HTTP/TCP connection बनता है
```

---

## 🟡 Real World Example
**Swiggy microservices:** Internal service `order-service` needs to call `payment-service.internal.swiggy.com`. Before making 10,000 HTTP calls/sec, Swiggy's infra pre-resolves and caches the IP using `dns.resolve4()` with a custom TTL-aware cache, avoiding a DNS lookup on every single request (which would add 5-50ms latency each time). They also use `dns.lookup()` with `{ all: true }` to get all IPs behind a load-balanced hostname for client-side load balancing.

## 🟡 Real Example Hindi mein
**Swiggy:** `order-service` को `payment-service.internal.swiggy.com` call करना है। हर request पर DNS lookup (5-50ms) से बचने के लिए `dns.resolve4()` से custom TTL-cache बनाया जाता है। `dns.lookup({ all: true })` से load-balanced hostname के सभी IPs मिलते हैं client-side load balancing के लिए।

---

## 💻 Code Example — Basic

```javascript
// dns-basic.js
// Run: node dns-basic.js

const dns = require('dns');  // import core dns module

// dns.lookup() — uses OS-level resolver (getaddrinfo), respects /etc/hosts
dns.lookup('google.com', (err, address, family) => {
  if (err) {
    console.error('Lookup failed:', err.message);  // handle DNS errors
    return;
  }
  console.log('Address:', address);   // e.g. '142.250.183.46'
  console.log('IP Family:', family);  // 4 (IPv4) or 6 (IPv6)
});

// dns.resolve4() — direct DNS query for A records (IPv4), bypasses OS cache
dns.resolve4('google.com', (err, addresses) => {
  if (err) {
    console.error('Resolve failed:', err.message);
    return;
  }
  console.log('All IPv4 addresses:', addresses);  // array, e.g. ['142.250.183.46', ...]
});

// dns.resolveMx() — get mail server records (useful before sending email)
dns.resolveMx('gmail.com', (err, mxRecords) => {
  if (err) return console.error(err.message);
  console.log('MX records:', mxRecords);
  // [{ exchange: 'gmail-smtp-in.l.google.com', priority: 5 }, ...]
});

// Reverse lookup — IP to hostname
dns.reverse('8.8.8.8', (err, hostnames) => {
  if (err) return console.error(err.message);
  console.log('Hostnames for 8.8.8.8:', hostnames);  // ['dns.google']
});
```

## 💻 Code Example — Advanced

```javascript
// dns-advanced.js — Production-style DNS cache with TTL + promises

const dns = require('dns').promises;  // Promise-based API (no callbacks)

class DnsCache {
  constructor(ttlMs = 60_000) {  // default: cache entries for 60 seconds
    this.cache = new Map();      // hostname -> { address, expiresAt }
    this.ttlMs = ttlMs;
  }

  async resolve(hostname) {
    const cached = this.cache.get(hostname);

    // Return cached value if still valid
    if (cached && cached.expiresAt > Date.now()) {
      return cached.address;
    }

    try {
      // resolve4 bypasses OS cache, talks directly to DNS server
      const addresses = await dns.resolve4(hostname);
      const address = addresses[0];  // pick first IP (could round-robin here)

      // Store in cache with expiry
      this.cache.set(hostname, {
        address,
        expiresAt: Date.now() + this.ttlMs,
      });

      return address;
    } catch (err) {
      // Fallback: if we have a stale cached value, use it rather than failing
      if (cached) {
        console.warn(`DNS resolve failed for ${hostname}, using stale cache`);
        return cached.address;
      }
      throw new Error(`DNS resolution failed for ${hostname}: ${err.message}`);
    }
  }

  // Periodically clear expired entries to avoid memory growth
  startCleanup(intervalMs = 300_000) {
    setInterval(() => {
      const now = Date.now();
      for (const [host, entry] of this.cache) {
        if (entry.expiresAt <= now) this.cache.delete(host);
      }
    }, intervalMs).unref();  // unref so this timer doesn't keep process alive
  }
}

// Usage: resolve internal microservice hostname before HTTP call
(async () => {
  const dnsCache = new DnsCache(30_000);
  dnsCache.startCleanup();

  try {
    const ip = await dnsCache.resolve('api.github.com');
    console.log('Resolved IP (cached after first call):', ip);

    // Second call within TTL — served from cache, no network round trip
    const ipAgain = await dnsCache.resolve('api.github.com');
    console.log('Second call (from cache):', ipAgain);
  } catch (err) {
    console.error('Production error:', err.message);
  }
})();
```

---

## 🟠 Express.js Integration

```javascript
// Using dns to pre-warm connections and health-check upstream services
const express = require('express');
const dns = require('dns').promises;
const app = express();

// Middleware: resolve and attach upstream payment gateway IP before forwarding
app.use('/pay', async (req, res, next) => {
  try {
    const [ip] = await dns.resolve4('payments.partner-bank.com');
    req.upstreamIp = ip;  // could be used for logging/monitoring
    next();
  } catch (err) {
    // DNS failure means the payment partner is likely unreachable
    res.status(503).json({ error: 'Payment gateway unreachable (DNS failure)' });
  }
});

app.post('/pay/charge', (req, res) => {
  console.log('Forwarding to upstream IP:', req.upstreamIp);
  res.json({ status: 'charged' });
});

// Health check endpoint that verifies DNS resolution of critical dependencies
app.get('/health/dns', async (req, res) => {
  const hosts = ['db.internal.company.com', 'cache.internal.company.com'];
  const results = {};

  for (const host of hosts) {
    try {
      await dns.resolve4(host);
      results[host] = 'ok';
    } catch {
      results[host] = 'FAILED';
    }
  }

  const healthy = Object.values(results).every(v => v === 'ok');
  res.status(healthy ? 200 : 503).json(results);
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using `dns.lookup()` for high-throughput internal calls without caching
```javascript
// WRONG: resolves DNS on every single request — adds latency, overloads DNS server
app.get('/data', async (req, res) => {
  const { address } = await require('dns').promises.lookup('internal-service.local');
  const data = await fetch(`http://${address}/data`);
  res.json(await data.json());
});

// CORRECT: cache resolved IPs with a TTL (see DnsCache class above)
app.get('/data', async (req, res) => {
  const ip = await dnsCache.resolve('internal-service.local');
  const data = await fetch(`http://${ip}/data`);
  res.json(await data.json());
});
```

❌ **Mistake 2:** Confusing `dns.lookup()` with `dns.resolve()`
```javascript
// WRONG assumption: they behave identically
dns.lookup('example.com', cb);   // uses OS resolver (getaddrinfo) — runs in LIBUV THREAD POOL
dns.resolve4('example.com', cb); // pure DNS query via c-ares — does NOT use thread pool

// CORRECT understanding:
// dns.lookup() respects /etc/hosts, OS DNS cache, and NSS config — good for general use
// dns.resolve*() is faster for high-volume lookups and gives more record types (MX, TXT, NS)
// but skips /etc/hosts entirely — won't resolve "localhost" entries from hosts file reliably
```

---

## 🧠 Tricky Interview Question

```javascript
const dns = require('dns');

console.log('start');

dns.lookup('localhost', (err, address) => {
  console.log('lookup:', address);
});

dns.resolve4('localhost', (err, addresses) => {
  console.log('resolve4 err:', err ? err.code : null);
});

console.log('end');
```

**Answer:** Output is `start`, `end`, then `lookup: 127.0.0.1`, then `resolve4 err: ENOTFOUND`. Explanation: `dns.lookup('localhost')` checks the OS resolver which knows `localhost` maps to `127.0.0.1` via `/etc/hosts` or OS-level config — it succeeds. `dns.resolve4('localhost')` sends an actual DNS query over the network/c-ares, bypassing `/etc/hosts` — `localhost` isn't a real DNS record so it fails with `ENOTFOUND`. This is the classic trap: `resolve*()` functions don't consult the hosts file.

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between `dns.lookup()` and `dns.resolve()`?**
A1: `dns.lookup()` uses the OS's native resolver (`getaddrinfo` in C), which checks `/etc/hosts`, NSS config, and OS DNS cache — it runs inside libuv's **thread pool** because `getaddrinfo` is a blocking syscall. `dns.resolve()` (and `resolve4`/`resolve6`/`resolveMx` etc.) use the **c-ares** library to send DNS queries directly over the network, completely bypassing `/etc/hosts` and OS cache — these do NOT use the thread pool, they're event-loop driven I/O. Use `lookup()` for general hostname resolution; use `resolve*()` for detailed DNS records or when you need to avoid OS-level caching quirks.

**Q2: Why does `dns.lookup()` use the thread pool but `dns.resolve4()` doesn't?**
A2: `getaddrinfo()` (used by `lookup`) is a synchronous OS-level function with no async variant on most platforms, so Node must run it on a worker thread (from libuv's default 4-thread pool) to avoid blocking the event loop. `resolve4()` uses the c-ares library, which has native async socket-based DNS resolution — so it can use the normal event loop (poll phase) without needing a separate thread.

**Q3: How would you speed up DNS resolution for a service making thousands of outbound calls per second?**
A3: (1) Implement an in-memory TTL-based cache (like the `DnsCache` class) so repeated lookups to the same hostname don't hit the network every time. (2) Prefer `dns.resolve4()`/`resolve6()` over `dns.lookup()` for bulk/high-throughput cases since they avoid the thread pool bottleneck (only 4 threads by default). (3) Increase `UV_THREADPOOL_SIZE` if still using `lookup()` heavily. (4) Use connection pooling (keep-alive) so you're not re-resolving DNS on every request anyway.

**Q4: What does `dns.resolve4()` with `{ ttl: true }` option return?**
A4: It returns objects like `{ address: '1.2.3.4', ttl: 300 }` instead of plain IP strings — the `ttl` field tells you how many seconds the DNS record is valid for, per the DNS server's response. This is useful for building a cache that respects the actual DNS TTL rather than using an arbitrary fixed cache duration.

**Q5: Can DNS resolution failures crash a Node.js app?**
A5: Only if not handled. `dns.lookup()`/`resolve()` calls that fail pass an `Error` as the first callback argument (e.g., `ENOTFOUND`, `ETIMEOUT`) — if you don't check `err` or don't catch rejected promises, an unhandled promise rejection can crash the process (in newer Node versions, unhandled rejections terminate the process by default). Always wrap DNS calls in try/catch (with the promises API) or check the `err` parameter in callbacks, and have a fallback/retry strategy for transient DNS failures.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- Building custom load balancers or service discovery
- Pre-warming/caching DNS for high-throughput internal service calls
- Verifying domain health (MX records before sending email, A records before HTTP calls)
- Debugging "which IP does this hostname resolve to"

❌ **Avoid when:**
- Simple one-off HTTP requests — `http`/`fetch`/`axios` already do DNS resolution internally, no need to call `dns` module yourself
- You need `/etc/hosts` overrides respected — use `dns.lookup()`, not `resolve*()`

---

## 📊 Visual Diagram

```
DNS MODULE — TWO PATHS:
──────────────────────────────────────────────────────

  dns.lookup(hostname)
       │
       ▼
  getaddrinfo() [OS syscall, BLOCKING]
       │
       ▼
  Runs on LIBUV THREAD POOL (4 threads default)
       │
       ▼
  Checks: /etc/hosts → OS DNS cache → OS resolver
       │
       ▼
  Callback with resolved IP


  dns.resolve4(hostname)
       │
       ▼
  c-ares library — async socket-based DNS query
       │
       ▼
  Runs on EVENT LOOP (poll phase, no thread pool needed)
       │
       ▼
  Sends UDP packet directly to DNS server (bypasses /etc/hosts!)
       │
       ▼
  Callback with IP addresses / records
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `dns.lookup()` | OS-resolver based lookup (thread pool) | OS resolver based lookup |
| `dns.resolve4()` | Direct DNS query via c-ares | Direct DNS query |
| A Record | Hostname → IPv4 mapping | Hostname से IPv4 mapping |
| MX Record | Mail server records | Mail server का record |
| TTL | Time-to-live for cached DNS entry | DNS entry valid रहने का समय |
| c-ares | Async DNS resolver library used by Node | Node का async DNS library |
| ENOTFOUND | DNS resolution failure error code | DNS resolve ना होने का error |

---

## ⚡ 3-Line Summary
English:
1. `dns` module resolves hostnames to IPs — `dns.lookup()` uses the OS resolver (thread pool, respects `/etc/hosts`), `dns.resolve*()` queries DNS servers directly via c-ares (event-loop based, no `/etc/hosts`).
2. Use caching with TTL for high-throughput services to avoid repeated DNS lookups adding latency on every request.
3. `resolve4`/`resolve6`/`resolveMx`/`reverse` give fine-grained record access useful for health checks, service discovery, and email validation.

Hindi:
1. `dns` module hostname को IP में resolve करता है — `lookup()` OS resolver (thread pool) use करता है, `resolve*()` direct DNS query (c-ares) करता है।
2. High-throughput services के लिए TTL-based caching use करो ताकि हर request पर DNS lookup latency ना बढ़े।
3. `resolve4`/`resolveMx`/`reverse` जैसे functions से health checks, service discovery, email validation में detailed record मिलते हैं।

---

## ➡️ Next Topic
**65. net Module** — Low-level TCP socket programming in Node.js, building servers below the HTTP layer।
