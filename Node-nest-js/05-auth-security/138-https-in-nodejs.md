# 138. HTTPS in Node.js
# हिंदी में: Node.js में HTTPS

---

## 🔵 Simple Definition (English)
**HTTPS** is HTTP over **TLS/SSL** — it encrypts data in transit between client and server, verifies server identity via certificates, and ensures data integrity. In Node.js, the built-in `https` module creates a server that wraps regular HTTP handling with TLS encryption, requiring a certificate and private key.

## 🔵 सरल परिभाषा (Hindi)
**HTTPS** HTTP over **TLS/SSL** है — client और server के बीच data को encrypt करता है, certificates से server identity verify करता है, और data integrity ensure करता है। Node.js में built-in `https` module एक server बनाता है जो regular HTTP handling को TLS encryption से wrap करता है, certificate और private key की ज़रूरत होती है।

---

## 🔴 Problem it Solves
Plain HTTP sends data as plaintext over the network — anyone on the same network (public WiFi, ISP, a man-in-the-middle attacker) can read passwords, session cookies, and personal data in transit, or even MODIFY the data (injecting malicious scripts into an HTTP response). HTTPS encrypts the entire communication channel using TLS, so even if intercepted, the data is unreadable without the decryption key — and certificates prove you're actually talking to the real server, not an impersonator.

## 🔴 यह क्यों बना? (Hindi)
Plain HTTP data को network पर plaintext भेजता है — कोई भी same network पर (public WiFi, ISP, man-in-the-middle attacker) passwords, session cookies, personal data पढ़ सकता है, या data modify भी कर सकता है। HTTPS पूरे communication channel को TLS से encrypt करता है, intercept होने पर भी data unreadable रहता है — और certificates prove करते हैं कि आप असली server से बात कर रहे हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → Obtain a TLS certificate + private key (from a CA like Let's Encrypt, or self-signed for dev)
Step 2 → Node's `https` module creates a server passing `{ key, cert }` options (read from files)
Step 3 → Client initiates **TLS handshake**: client sends supported TLS versions/ciphers, server responds with its certificate
Step 4 → Client verifies certificate (signed by a trusted CA, not expired, matches domain) — browsers do this automatically
Step 5 → Client and server perform key exchange (e.g., Diffie-Hellman) to agree on a shared symmetric session key WITHOUT ever sending the key itself over the wire
Step 6 → All subsequent data is encrypted using the fast symmetric session key (asymmetric crypto is only used for the initial handshake — too slow for bulk data)
Step 7 → In production, TLS termination often happens at a load balancer/reverse proxy (Nginx, AWS ALB) rather than directly in the Node process — Node then only handles plain HTTP behind that proxy

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → TLS certificate + private key प्राप्त करो
Step 2 → Node का `https` module `{ key, cert }` options से server बनाता है
Step 3 → Client TLS handshake शुरू करता है
Step 4 → Client certificate verify करता है
Step 5 → Client-server shared symmetric session key पर agree करते हैं
Step 6 → आगे का data symmetric key से encrypted होता है
Step 7 → Production में TLS termination अक्सर load balancer/proxy पर होता है

---

## 🟡 Real World Example
**Paytm's payment gateway:** All payment-related traffic MUST use HTTPS — card numbers, OTPs, UPI PINs are sent over an encrypted TLS channel. In production, Paytm's infrastructure typically terminates TLS at a load balancer/CDN edge (AWS ALB, Cloudflare) which handles certificate management and decryption, then forwards plain HTTP internally to Node.js app servers within their private, trusted network — this offloads the CPU-intensive TLS handshake work from the Node process and simplifies certificate rotation across many servers.

## 🟡 Real Example Hindi mein
**Paytm का payment gateway:** सभी payment traffic HTTPS use करता है — card numbers, OTPs encrypted TLS channel से भेजे जाते हैं। Production में TLS termination अक्सर load balancer/CDN edge पर होता है, फिर internal network में plain HTTP forward होता है Node.js app servers को।

---

## 💻 Code Example — Basic

```javascript
// https-basic.js — self-signed cert for local dev/testing
// Generate a self-signed cert first:
//   openssl req -nodes -new -x509 -keyout key.pem -out cert.pem -days 365
// Run with: node https-basic.js, visit https://localhost:3443 (browser will warn — self-signed)

const https = require('https');
const fs = require('fs');

// ─── 1. LOAD CERTIFICATE AND PRIVATE KEY FROM DISK ───────────────────────────
const options = {
  key: fs.readFileSync('key.pem'),    // private key — NEVER commit this to git
  cert: fs.readFileSync('cert.pem'),  // public certificate
};

// ─── 2. CREATE HTTPS SERVER ────────────────────────────────────────────────────
const server = https.createServer(options, (req, res) => {
  res.writeHead(200, { 'Content-Type': 'text/plain' });
  res.end('Hello over HTTPS! Connection is encrypted.\n');
});

server.listen(3443, () => {
  console.log('HTTPS server running on https://localhost:3443');
});

// NOTE: self-signed certs trigger browser warnings ("not trusted") because
// they aren't signed by a recognized Certificate Authority — fine for local
// dev, never acceptable for production (use Let's Encrypt or a paid CA there).
```

## 💻 Code Example — Advanced

```javascript
// https-advanced.js — production-style config with HTTP→HTTPS redirect + security options

const https = require('https');
const http = require('http');
const fs = require('fs');
const express = require('express');

const app = express();

app.get('/', (req, res) => {
  res.send('Secure endpoint over HTTPS');
});

// ─── 1. TLS OPTIONS WITH HARDENED SETTINGS ───────────────────────────────────
const httpsOptions = {
  key: fs.readFileSync(process.env.TLS_KEY_PATH),
  cert: fs.readFileSync(process.env.TLS_CERT_PATH),
  // Optional: certificate chain (intermediate CA certs) for full trust chain
  ca: fs.existsSync(process.env.TLS_CA_PATH || '') ? fs.readFileSync(process.env.TLS_CA_PATH) : undefined,

  // Restrict to modern, secure TLS versions only (avoid known-vulnerable TLS 1.0/1.1)
  minVersion: 'TLSv1.2',

  // Prefer strong cipher suites (forward secrecy, AEAD ciphers)
  ciphers: [
    'ECDHE-ECDSA-AES128-GCM-SHA256',
    'ECDHE-RSA-AES128-GCM-SHA256',
    'ECDHE-ECDSA-AES256-GCM-SHA384',
  ].join(':'),
  honorCipherOrder: true,
};

// ─── 2. START HTTPS SERVER ──────────────────────────────────────────────────────
https.createServer(httpsOptions, app).listen(443, () => {
  console.log('HTTPS server running on port 443');
});

// ─── 3. REDIRECT ALL PLAIN HTTP TRAFFIC TO HTTPS ──────────────────────────────
// Separate lightweight server on port 80, ONLY redirects — never serves real content
http
  .createServer((req, res) => {
    const host = req.headers.host?.split(':')[0];  // strip any port from Host header
    res.writeHead(301, { Location: `https://${host}${req.url}` });
    res.end();
  })
  .listen(80, () => {
    console.log('HTTP redirect server running on port 80');
  });

module.exports = { httpsOptions };
```

---

## 🟠 Express.js Integration

```javascript
// server.js — Express behind a reverse proxy (common production pattern)
const express = require('express');
const app = express();

// In production, TLS is often terminated at Nginx/AWS ALB/Cloudflare, and Node
// only sees plain HTTP from the proxy. Node must be told to trust the proxy's
// forwarded headers to correctly detect "is this request actually secure?"
app.set('trust proxy', 1);   // trust first proxy hop (e.g., ALB) for X-Forwarded-* headers

// Middleware: enforce HTTPS by checking X-Forwarded-Proto (set by the proxy)
function requireHttps(req, res, next) {
  if (req.secure || req.headers['x-forwarded-proto'] === 'https') {
    return next();
  }
  // Redirect any stray HTTP request to HTTPS
  res.redirect(301, `https://${req.headers.host}${req.url}`);
}

app.use(requireHttps);

app.get('/api/payment', (req, res) => {
  res.json({ message: 'Processed over HTTPS', secure: req.secure });
});

// For direct Node-terminated HTTPS (no proxy), use the https module directly:
// const https = require('https');
// const fs = require('fs');
// https.createServer({ key: fs.readFileSync('key.pem'), cert: fs.readFileSync('cert.pem') }, app)
//      .listen(443);

app.listen(3000, () => console.log('App server on port 3000 (behind reverse proxy)'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Committing private keys/certificates to version control
```javascript
// WRONG: key.pem and cert.pem committed to git — exposes the private key publicly
// git add key.pem cert.pem && git commit -m "add certs"

// CORRECT: load from environment-specific paths, add to .gitignore
// .gitignore: *.pem, *.key
const options = {
  key: fs.readFileSync(process.env.TLS_KEY_PATH),   // path from env, file never committed
  cert: fs.readFileSync(process.env.TLS_CERT_PATH),
};
```

❌ Mistake 2: Trusting `req.secure` without configuring `trust proxy` behind a load balancer
```javascript
// WRONG: app behind a load balancer that terminates TLS — req.secure is ALWAYS false
// because Node only ever sees plain HTTP from the proxy
if (req.secure) { /* never true, even for genuinely HTTPS requests from users */ }

// CORRECT: tell Express to trust the proxy, so it reads X-Forwarded-Proto correctly
app.set('trust proxy', 1);
if (req.secure) { /* now correctly reflects the original client's protocol */ }
```

---

## 🧠 Tricky Interview Question

```javascript
// Node app has NO explicit HTTPS setup — just app.listen(3000) with plain HTTP.
// It sits behind an Nginx reverse proxy that terminates TLS on port 443.
// A user visits https://example.com — is the connection to the Node process encrypted?
```
Answer: **The connection between the USER's browser and Nginx IS encrypted (HTTPS/TLS)** — Nginx terminates TLS there. However, **the connection between Nginx and the Node.js process is typically PLAIN HTTP** (unencrypted), usually over `localhost` or an internal private network. This is fine from a security standpoint AS LONG AS that internal network is genuinely trusted/isolated (e.g., same machine, or a private VPC with no untrusted access) — this is an extremely common and acceptable production pattern called "TLS termination at the edge." It becomes a problem only if that internal hop crosses an untrusted network, in which case internal TLS (or at least a VPN/service mesh with mTLS) would also be needed.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between TLS and SSL?
A1: SSL (Secure Sockets Layer) is the OLDER protocol (SSL 2.0, 3.0) now considered insecure and deprecated. TLS (Transport Layer Security) is its modern successor (TLS 1.0 through 1.3) — people often still say "SSL certificate" colloquially, but the actual protocol in use today is TLS. TLS 1.2 and 1.3 are the only versions considered secure for production use; TLS 1.0/1.1 and all SSL versions should be disabled.

Q2: Why is a hybrid of asymmetric and symmetric encryption used in TLS, instead of just one?
A2: Asymmetric encryption (public/private key pairs) is secure for exchanging a secret without ever transmitting it directly, but it's computationally SLOW for large amounts of data. Symmetric encryption (same key both sides) is very fast but requires both parties to already share a secret key. TLS uses asymmetric crypto ONLY during the handshake to securely establish a shared symmetric session key, then switches to fast symmetric encryption (AES-GCM etc.) for all the actual bulk data transfer — getting both security and performance.

Q3: What does "TLS termination at a load balancer/proxy" mean, and why is it common in production?
A3: It means the load balancer/reverse proxy (Nginx, AWS ALB, Cloudflare) handles the TLS handshake and decryption, then forwards the DECRYPTED plain HTTP request to the backend app servers (Node.js) over an internal trusted network. Benefits: (1) centralizes certificate management/renewal in one place instead of every app server, (2) offloads CPU-intensive TLS handshake work from app servers, (3) simplifies horizontal scaling (new app instances don't need their own certs).

Q4: How do you make an Express app correctly detect HTTPS when it's behind a reverse proxy?
A4: Set `app.set('trust proxy', 1)` (or a specific number of hops / IP ranges for more granular trust) — this tells Express to trust and read the `X-Forwarded-Proto` and `X-Forwarded-For` headers set by the proxy, making `req.secure` and `req.protocol` accurately reflect the ORIGINAL client connection's protocol, not the internal (likely plain HTTP) connection between the proxy and Node.

Q5: What's an HSTS header and how does it relate to HTTPS enforcement?
A5: `Strict-Transport-Security` (HSTS) is a response header telling the browser "always use HTTPS for this domain for the next N seconds, never attempt plain HTTP." It protects against SSL-stripping man-in-the-middle attacks on the user's FIRST request (before any redirect could happen) by making the browser itself refuse to even try HTTP after the first HSTS-enabled visit. Combined with a 301 redirect from HTTP→HTTPS at the server/proxy level, this ensures HTTPS is consistently enforced across all subsequent visits.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- ANY production web app or API handling user data, authentication, or payments — HTTPS should be mandatory, no exceptions.
- Internal microservice communication crossing untrusted network boundaries — use mTLS/internal certs too.

❌ Avoid when:
- Direct Node.js TLS termination at scale is rarely preferred over proxy-based termination (Nginx/ALB) for operational simplicity — "avoid" here means avoid manual cert management per-instance, not avoid HTTPS itself.

---

## 📊 Visual Diagram

```
TLS HANDSHAKE (simplified):
──────────────────────────────────────────────────────────

  Client                                   Server
    │── ClientHello (supported ciphers) ──────►│
    │◄───── ServerHello + Certificate ─────────│
    │   (client verifies cert against trusted CAs)
    │── Key exchange (establishes shared ─────►│
    │   symmetric session key securely)        │
    │◄─────── Handshake complete ──────────────│
    │                                           │
    │══ Encrypted data (AES, using session key) ══│
    │ (fast symmetric encryption for all actual data)

PRODUCTION ARCHITECTURE:
  User (HTTPS) ──► Nginx/ALB (TLS termination) ──► Node.js (plain HTTP, internal network)
                         │
                   manages certs, handles handshake
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| TLS | Protocol encrypting data in transit | Data को transit में encrypt करने वाला protocol |
| Certificate | Signed proof of server identity | Server identity का signed proof |
| TLS handshake | Negotiation establishing encrypted session | Encrypted session establish करने वाली negotiation |
| TLS termination | Decrypting TLS at proxy/load balancer | Proxy पर TLS decrypt करना |
| Symmetric encryption | Same key for encrypt/decrypt (fast) | Encrypt/decrypt के लिए same key |
| HSTS | Header forcing HTTPS-only future requests | HTTPS-only force करने वाला header |

---

## ⚡ 3-Line Summary
English:
1. HTTPS encrypts client-server communication using TLS, verifying server identity via certificates and protecting data integrity/confidentiality.
2. Node's `https` module needs a key+cert pair; production commonly terminates TLS at a reverse proxy/load balancer instead of directly in Node.
3. Always redirect HTTP to HTTPS, use `trust proxy` correctly behind proxies, and never commit private keys to version control.

Hindi:
1. HTTPS TLS से client-server communication encrypt करता है, certificates से server identity verify करता है।
2. Node के `https` module को key+cert चाहिए; production में अक्सर proxy पर TLS terminate होता है।
3. हमेशा HTTP को HTTPS पर redirect करो, proxy के पीछे `trust proxy` सही use करो, private keys कभी commit मत करो।

---

## ➡️ Next Topic
**139. SSL Certificates in Node** — Certificate types, CA, Let's Encrypt, certificate chains।
