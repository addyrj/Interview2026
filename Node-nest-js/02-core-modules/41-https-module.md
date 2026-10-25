# 41. https Module
# हिंदी में: https Module — Secure Server और Requests

---

## 🔵 Simple Definition (English)
The **`https`** module is Node's built-in API for creating **encrypted** HTTP servers (using TLS/SSL certificates) and making secure outbound requests. It has nearly identical API shape to `http`, but wraps the connection in encryption, requiring a certificate and private key to run a server.

## 🔵 सरल परिभाषा (Hindi)
**`https`** module Node का built-in API है **encrypted** HTTP servers बनाने के लिए (TLS/SSL certificates use करके) और secure outbound requests भेजने के लिए। इसका API shape `http` जैसा ही है, पर connection को encryption में wrap करता है, server चलाने के लिए certificate और private key चाहिए।

---

## 🔴 Problem it Solves
Plain `http` traffic travels in CLEAR TEXT over the network — anyone intercepting it (on public WiFi, a compromised router, a man-in-the-middle attacker) can read passwords, tokens, payment details, and session cookies directly. `https` solves this by encrypting the entire connection using TLS (Transport Layer Security), ensuring data is unreadable to anyone except the intended client and server, and also providing certificate-based identity verification (so clients can trust they're really talking to the server they intended, not an impersonator).

## 🔴 यह क्यों बना? (Hindi)
Plain `http` traffic network पर CLEAR TEXT में travel करता है — इसे intercept करने वाला कोई भी (public WiFi पर, compromised router, man-in-the-middle attacker) passwords, tokens, payment details, और session cookies directly पढ़ सकता है। `https` इसे solve करता है पूरे connection को TLS (Transport Layer Security) से encrypt करके, ensure करता है कि data intended client और server के अलावा किसी को readable न हो, और certificate-based identity verification भी देता है (ताकि clients trust कर सकें कि वे really उस server से बात कर रहे हैं जिसका इरादा था, किसी impersonator से नहीं)।

---

## 🟢 How it Works — Step by Step

Step 1 → `const https = require('https')` or `require('node:https')`.
Step 2 → To CREATE an HTTPS server, you need a TLS certificate and private key: `https.createServer({ key: fs.readFileSync('key.pem'), cert: fs.readFileSync('cert.pem') }, handler)` — the `key`/`cert` pair is issued by a Certificate Authority (CA) like Let's Encrypt in production, or self-signed for local development/testing.
Step 3 → The rest of the server API is IDENTICAL to `http` — same `req`/`res` objects, same `listen()` call, same request-handling logic. The ONLY difference is the encrypted transport layer underneath.
Step 4 → To make OUTBOUND HTTPS requests (as a client calling another server), use `https.get(url, callback)` or `https.request(options, callback)` — same pattern as `http.get`/`http.request`, but automatically uses TLS.
Step 5 → In REAL production deployments, TLS termination often happens at a LOAD BALANCER or REVERSE PROXY (Nginx, AWS ALB, Cloudflare) in front of the Node app — the Node app itself runs plain `http` internally, while the proxy handles HTTPS with the public internet and forwards decrypted traffic internally. This means many Node apps never directly use `https.createServer()` in production, even though all public traffic to them IS encrypted.
Step 6 → Self-signed certificates (common for local dev) cause browsers/`curl` to show warnings/errors by default since they're not from a trusted CA — `rejectUnauthorized: false` can bypass this for outbound requests during local testing, but should NEVER be used in production (defeats the entire purpose of certificate verification).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `const https = require('https')` या `require('node:https')`।
Step 2 → HTTPS server बनाने के लिए, TLS certificate और private key चाहिए: `https.createServer({ key: fs.readFileSync('key.pem'), cert: fs.readFileSync('cert.pem') }, handler)` — `key`/`cert` pair production में किसी Certificate Authority (CA) जैसे Let's Encrypt से issued होता है, या local development/testing के लिए self-signed।
Step 3 → बाकी server API `http` जैसा IDENTICAL है — same `req`/`res` objects, same `listen()` call, same request-handling logic। सिर्फ FARAK underlying encrypted transport layer का है।
Step 4 → OUTBOUND HTTPS requests भेजने के लिए (दूसरे server को call करते समय client की तरह), `https.get(url, callback)` या `https.request(options, callback)` use करो — same pattern `http.get`/`http.request` जैसा, पर automatically TLS use करता है।
Step 5 → REAL production deployments में, TLS termination अक्सर एक LOAD BALANCER या REVERSE PROXY (Nginx, AWS ALB, Cloudflare) पर Node app के सामने होता है — Node app खुद internally plain `http` चलाता है, proxy public internet के साथ HTTPS handle करता है और decrypted traffic internally forward करता है। इसका मतलब है बहुत सारे Node apps production में कभी directly `https.createServer()` use नहीं करते, पर उन्हें जाने वाला सारा public traffic ENCRYPTED होता है।
Step 6 → Self-signed certificates (local dev के लिए common) browsers/`curl` में default रूप से warnings/errors दिखाते हैं क्योंकि trusted CA से नहीं आए — `rejectUnauthorized: false` local testing में outbound requests के लिए यह bypass कर सकता है, पर production में कभी use मत करो (certificate verification का पूरा purpose defeat करता है)।

---

## 🟡 Real World Example
**Paytm's merchant payment-gateway API:** Public-facing endpoints are terminated at AWS Application Load Balancer, which handles the actual TLS/HTTPS encryption using certificates from AWS Certificate Manager (auto-renewed, trusted by all browsers) — the Node.js service behind it only runs plain `http` internally, since traffic between the load balancer and the app runs within a private VPC network, not exposed to the public internet. For OUTBOUND calls (e.g., calling a bank's settlement API), the service uses `https.request()` (or more commonly, `axios`/`fetch` which use `https` internally) with strict certificate validation enabled, since bank APIs require verified TLS trust for financial compliance.

## 🟡 Real Example Hindi mein
**Paytm का merchant payment-gateway API:** Public-facing endpoints AWS Application Load Balancer पर terminate होते हैं, जो actual TLS/HTTPS encryption handle करता है AWS Certificate Manager के certificates से (auto-renewed, सभी browsers द्वारा trusted) — उसके पीछे Node.js service internally सिर्फ plain `http` चलाती है, क्योंकि load balancer और app के बीच traffic एक private VPC network के अंदर रहता है, public internet पर exposed नहीं। OUTBOUND calls के लिए (जैसे किसी bank के settlement API को call करना), service `https.request()` (या ज़्यादा commonly, `axios`/`fetch` जो internally `https` use करते हैं) strict certificate validation enabled के साथ use करती है, क्योंकि bank APIs financial compliance के लिए verified TLS trust चाहते हैं।

---

## 💻 Code Example — Basic

```javascript
// httpsBasics.js — a simple HTTPS server with a self-signed certificate (local dev only)
// First generate a self-signed cert for testing:
//   openssl req -nodes -new -x509 -keyout key.pem -out cert.pem -days 365
const https = require('https');
const fs = require('fs');

const options = {
  key: fs.readFileSync('./key.pem'),   // private key
  cert: fs.readFileSync('./cert.pem'), // certificate
};

const server = https.createServer(options, (req, res) => {
  res.writeHead(200, { 'Content-Type': 'text/plain' });
  res.end('Hello over HTTPS!');
});

server.listen(443, () => {
  console.log('HTTPS server running on https://localhost:443');
});

// Test with: curl -k https://localhost:443
// (-k skips certificate validation since it's self-signed, NOT for production use)
```

## 💻 Code Example — Advanced

```javascript
// httpsAdvanced.js — making secure outbound requests, and handling TLS options
const https = require('https');

// ─── Making a GET request over HTTPS (client-side usage) ───────────────────
function fetchJSON(url) {
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      let data = '';
      res.on('data', (chunk) => { data += chunk; });
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch (err) {
          reject(new Error('Failed to parse response as JSON'));
        }
      });
    }).on('error', reject); // network-level errors (DNS failure, connection refused, etc.)
  });
}

// ─── Making a POST request with a request body ─────────────────────────────
function postJSON(hostname, path, body) {
  return new Promise((resolve, reject) => {
    const payload = JSON.stringify(body);

    const options = {
      hostname,
      path,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(payload),
      },
      // rejectUnauthorized: true is the DEFAULT and should NEVER be disabled in production —
      // it ensures the server's certificate is verified against trusted CAs
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => { data += chunk; });
      res.on('end', () => resolve({ status: res.statusCode, body: JSON.parse(data || '{}') }));
    });

    req.on('error', reject);
    req.write(payload); // send the request body
    req.end(); // finalize the request
  });
}

(async () => {
  const data = await fetchJSON('https://api.github.com/users/nodejs');
  console.log('Fetched:', data.login);

  // const result = await postJSON('api.example.com', '/payments', { amount: 500 });
  // console.log('Posted:', result);
})();
```

---

## 🟠 Express.js Integration

```javascript
// server.js — Express app served over HTTPS directly (less common in production,
// where a reverse proxy usually handles TLS, but useful for internal services or local dev)
const express = require('express');
const https = require('https');
const fs = require('fs');

const app = express();

app.get('/', (req, res) => {
  res.send('Secure Express server');
});

const options = {
  key: fs.readFileSync('./key.pem'),
  cert: fs.readFileSync('./cert.pem'),
};

// Note: https.createServer(options, app) — Express app works as the request
// handler here exactly like it does with http.createServer(app)
https.createServer(options, app).listen(443, () => {
  console.log('Secure Express server running on https://localhost:443');
});

// In most real production setups, this would instead be:
//   app.listen(3000);  // plain http, internal only
// ... with Nginx/ALB/Cloudflare handling public HTTPS termination in front of it
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Disabling certificate validation (`rejectUnauthorized: false`) outside of local testing
```javascript
// Wrong — disables TLS certificate verification, opening the door to man-in-the-middle attacks
const options = {
  hostname: 'api.payment-provider.com',
  rejectUnauthorized: false, // DANGEROUS in production — accepts ANY certificate, even fake ones
};
https.request(options, callback);

// Right — keep default certificate validation enabled (rejectUnauthorized: true, the default)
const options = {
  hostname: 'api.payment-provider.com',
  // rejectUnauthorized defaults to true — leave it alone in production
};
https.request(options, callback);
```

❌ Mistake 2: Hardcoding certificate paths without handling missing files gracefully at startup
```javascript
// Wrong — crashes with an unhelpful stack trace if cert files are missing/misconfigured
const options = {
  key: fs.readFileSync('./key.pem'),   // throws ENOENT if file is missing, cryptic error
  cert: fs.readFileSync('./cert.pem'),
};

// Right — validate certificate files exist with a clear error message before starting
function loadTLSOptions() {
  try {
    return {
      key: fs.readFileSync('./key.pem'),
      cert: fs.readFileSync('./cert.pem'),
    };
  } catch (err) {
    throw new Error(`Failed to load TLS certificates: ${err.message}. Check key.pem/cert.pem exist.`);
  }
}
https.createServer(loadTLSOptions(), handler).listen(443);
```

---

## 🧠 Tricky Interview Question

```javascript
// Scenario: A Node.js app behind an AWS Application Load Balancer (ALB).
// The ALB terminates HTTPS and forwards plain HTTP to the app on port 3000.
// The app itself uses: app.listen(3000); (plain http, not https)
// Is any part of this setup "insecure"?
```
Answer: It depends on the NETWORK BOUNDARY, not just the app's own code. If the connection between the ALB and the Node app travels over a PRIVATE network (e.g., inside an AWS VPC, not traversing the public internet), this setup is considered SECURE in practice — the public-facing, potentially-hostile network segment (client ↔ ALB) IS encrypted via HTTPS at the ALB, and the internal, trusted network segment (ALB ↔ app) doesn't strictly need its OWN encryption since it's not exposed to external attackers. This is called "TLS termination at the edge" and is an extremely common, architecturally sound production pattern — it does NOT mean the overall system is insecure, even though the Node app itself never directly handles TLS. (For stricter compliance requirements — e.g., PCI-DSS in some configurations — end-to-end encryption even on internal networks may still be mandated, requiring mTLS between the proxy and app.)

---

## ⚫ Interview Questions + Answers

Q1: What's the fundamental difference between `http` and `https` modules in terms of API usage?
A1: The request/response handling API (`req`, `res`, `writeHead`, `write`, `end`, routing logic) is essentially IDENTICAL between the two. The core difference is that `https.createServer()` requires a `key`/`cert` (TLS credentials) as its first argument, and the underlying transport is encrypted via TLS/SSL. For CLIENT requests, `https.get`/`https.request` work the same way as their `http` counterparts but connect over an encrypted channel and validate server certificates by default.

Q2: Why do many production Node.js apps never directly call `https.createServer()`, even though all their traffic is encrypted?
A2: Because TLS termination is commonly delegated to a reverse proxy or load balancer (Nginx, AWS ALB/ELB, Cloudflare) sitting in front of the Node application. The proxy handles the public-facing HTTPS connection (certificate management, renewal, encryption/decryption), then forwards plain `http` traffic to the Node app over a private, trusted internal network. This simplifies certificate management (one place to configure/renew certs instead of per-app) and often provides better performance for TLS handling at the infrastructure layer.

Q3: What does `rejectUnauthorized: false` do, and why is it dangerous in production?
A3: It disables TLS certificate verification for outbound HTTPS requests — the client will accept ANY certificate presented by the server, including self-signed, expired, or fraudulent ones, without validating them against trusted Certificate Authorities. This completely defeats the purpose of TLS's identity-verification guarantee, opening the connection to man-in-the-middle attacks where an attacker could intercept and impersonate the real server. It should ONLY ever be used for local development/testing against self-signed certs, never in production code calling real external services.

Q4: How would you generate a self-signed certificate for local HTTPS development?
A4: Using OpenSSL: `openssl req -nodes -new -x509 -keyout key.pem -out cert.pem -days 365` generates a private key (`key.pem`) and a self-signed certificate (`cert.pem`) valid for 365 days. These can be passed directly to `https.createServer({ key, cert }, handler)`. Browsers/curl will show a security warning (or require `-k`/`--insecure` flags) since the cert isn't signed by a trusted CA — this is expected and acceptable for LOCAL development only.

Q5: Does using `https` instead of `http` impact performance?
A5: Yes, slightly — TLS adds computational overhead for the initial handshake (negotiating encryption, exchanging/verifying certificates) and ongoing encryption/decryption of data. Modern hardware and optimized TLS implementations (session resumption, HTTP/2 multiplexing which requires TLS in practice) minimize this overhead significantly, making it negligible for the vast majority of applications relative to the massive security benefit. The performance cost is virtually always worth paying — plain `http` for public-facing production traffic is considered unacceptable practice today regardless of minor speed differences.

---

## 🔷 When to Use + When Not to Use
✅ Use `https.createServer()` directly when:
- Running a standalone service without a reverse proxy/load balancer in front (e.g., simple VPS deployments, certain internal tools).
- Building local development servers needing to test HTTPS-specific behavior (secure cookies, HSTS, etc.).

✅ Use `https.request`/`https.get` (or libraries built on them like `axios`) when:
- Making any outbound call to an external API over the public internet — always use HTTPS, never plain HTTP, for anything handling sensitive data.

❌ Avoid when:
- Manually managing TLS certificates in the app when a reverse proxy/load balancer could handle termination more simply and centrally.
- Disabling certificate validation (`rejectUnauthorized: false`) for anything beyond strictly local, throwaway testing.

---

## 📊 Visual Diagram
```
TLS TERMINATION PATTERNS:
──────────────────────────────────────────────────────────

  PATTERN A: App handles HTTPS directly
    Client ──HTTPS (encrypted)──► https.createServer() [Node app]

  PATTERN B: Proxy/load balancer terminates TLS (common in production)
    Client ──HTTPS (encrypted)──► [Nginx/ALB] ──HTTP (private network)──► http.createServer() [Node app]
                                    ↑ handles cert management, renewal

  OUTBOUND REQUEST VALIDATION:
    App ──https.request()──► External API
           │
           └── rejectUnauthorized: true (default) → verifies cert against trusted CAs
               rejectUnauthorized: false (DANGEROUS) → accepts ANY cert, no verification
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| https module | Encrypted HTTP server/client API | Encrypted HTTP server/client API |
| TLS/SSL | Transport-layer encryption protocol | Transport-layer encryption protocol |
| Certificate (cert.pem) | Public identity proof for a server | Server की public identity proof |
| Private key (key.pem) | Secret key paired with the certificate | Certificate के साथ जुड़ी secret key |
| TLS termination | Where encryption/decryption happens | जहाँ encryption/decryption होता है |
| rejectUnauthorized | Controls cert validation strictness | Cert validation strictness control |
| Self-signed certificate | Cert not issued by a trusted CA | Trusted CA से issue न हुआ cert |

---

## ⚡ 3-Line Summary
English: `https` mirrors `http`'s API but requires a TLS certificate/key pair and encrypts all traffic, protecting data from interception and verifying server identity. In production, TLS termination is often delegated to a reverse proxy/load balancer in front of the Node app, which then communicates internally over plain `http` on a trusted network. Never disable certificate validation (`rejectUnauthorized: false`) outside of local testing — it defeats TLS's entire security purpose.
Hindi: `https` `http` का API mirror करता है पर TLS certificate/key pair चाहिए और सारा traffic encrypt करता है, data को interception से बचाता है और server identity verify करता है। Production में, TLS termination अक्सर Node app के सामने एक reverse proxy/load balancer को delegate किया जाता है, जो फिर internally trusted network पर plain `http` से communicate करता है। Local testing के बाहर कभी certificate validation disable मत करो (`rejectUnauthorized: false`) — यह TLS का पूरा security purpose defeat करता है।

---

## ➡️ Next Topic
**42. url Module** — parsing and constructing URLs, query strings, and the modern WHATWG URL API in Node.
