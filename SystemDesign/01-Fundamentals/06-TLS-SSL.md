# 06. TLS/SSL — How Encryption Works
# हिंदी में: TLS — क्लाइंट और सर्वर के बीच एक गुप्त चाबी तय करके पूरी बातचीत को ताले में बंद करने का तरीका

---

## 🔵 Simple Definition (English)
**TLS** (Transport Layer Security) is the protocol that encrypts data between client and server. **SSL** is its old, insecure predecessor; people still say "SSL certificate", but today it's always TLS (1.2 or 1.3).
TLS uses a **certificate** to prove the server's identity, and a **handshake** to agree on a secret key that encrypts the rest of the conversation.

## 🔵 सरल परिभाषा (Hindi)
TLS क्लाइंट और सर्वर के बीच डेटा को एन्क्रिप्ट करता है। SSL इसका पुराना (अब असुरक्षित) रूप है।
सर्वर certificate से अपनी पहचान साबित करता है, फिर दोनों मिलकर एक गुप्त चाबी बनाते हैं जिससे पूरा डेटा लॉक होता है।

---

## 🔴 Problem it Solves
Two strangers (your phone and `paytm.com`) must talk secretly over a public network, but:
1. They have **never met** — how do they agree on a secret key without an eavesdropper learning it?
2. How does your phone know it's the **real paytm.com** and not a hacker on the Wi-Fi pretending to be it?
3. How do you detect if someone **modified** data in transit?

TLS solves:
- (1) with **asymmetric cryptography / key exchange** (Diffie-Hellman),
- (2) with **certificates** signed by trusted **Certificate Authorities (CAs)**,
- (3) with **authenticated encryption** (AES-GCM / ChaCha20-Poly1305), which includes a tamper check.

## 🔴 यह क्यों बना? (Hindi)
आपका फ़ोन और Paytm का सर्वर पहले कभी नहीं मिले — खुले इंटरनेट पर गुप्त चाबी कैसे तय करें, ताकि बीच वाला न जान सके?
और कैसे पता चले कि सामने असली Paytm है, कोई नकली नहीं? TLS ये दोनों समस्याएँ हल करता है — key exchange से चाबी, और certificate से पहचान।

---

## 🟢 How it Works — Step by Step

### Two kinds of encryption

```
SYMMETRIC (same key to lock & unlock)           ASYMMETRIC (key pair)
  key K: "hello" → AES(K) → "x8#k" → AES(K)        Public key  → anyone can lock (encrypt)/verify
  ✅ Very fast (bulk data)                          Private key → only owner can unlock/sign
  ❌ How do both sides get K safely?               ✅ Solves key sharing & identity
                                                    ❌ ~1000x slower

TLS = use ASYMMETRIC once (handshake) to agree on a key
      → then SYMMETRIC (AES) for all the actual data.
```

### Certificate chain of trust

```
┌────────────────────────────┐
│ Root CA (e.g. ISRG Root X1)│  ← pre-installed in your OS / browser / phone (trust store)
└────────────┬───────────────┘
             │ signs
┌────────────▼───────────────┐
│ Intermediate CA (Let's     │
│ Encrypt R11)               │
└────────────┬───────────────┘
             │ signs
┌────────────▼───────────────┐
│ Leaf cert: api.myapp.com   │  ← your server sends this (+ intermediate) = "fullchain.pem"
│ contains: domain, public   │
│ key, expiry, signature     │
└────────────────────────────┘

Client checks: ✓ signature chain leads to a trusted root
               ✓ domain matches (api.myapp.com)
               ✓ not expired / not revoked
```

### TLS 1.3 handshake (1 round trip)

```
   Client                                               Server
     │                                                    │
     │── ClientHello ────────────────────────────────────►│
     │   - supported ciphers (AES-GCM, ChaCha20)          │
     │   - client's key share (ECDHE public value)        │
     │   - SNI: "api.myapp.com"                           │
     │                                                    │
     │◄───────────────────────────────────── ServerHello ─│
     │   - chosen cipher                                  │
     │   - server's key share (ECDHE public value)        │
     │   - Certificate  (api.myapp.com)                   │
     │   - CertificateVerify (signed with private key)    │
     │   - Finished                                       │
     │                                                    │
     │  Both sides now compute the SAME session key       │
     │  from the two key shares (Diffie-Hellman magic).   │
     │  The key itself was NEVER sent over the network.   │
     │                                                    │
     │── Finished + first encrypted HTTP request ────────►│
     │◄════════════ encrypted data (AES-GCM) ═════════════│

TLS 1.2 needed 2 round trips. TLS 1.3 needs 1. Resumed sessions: 0-RTT.
```

> 💡 **Diffie-Hellman analogy (paint mixing):** Both start with a public color (yellow). You add secret red, I add secret blue. We exchange our mixes publicly. You add your red to my mix; I add my blue to yours → we both get the SAME final brown. An eavesdropper saw only yellow, orange and green and can't "un-mix" them to get brown.

### Forward secrecy
TLS 1.3 uses **ephemeral** keys (new for every session). Even if the server's private key leaks next year, old recorded traffic **can't** be decrypted.

### Where TLS gets terminated (architecture choice)

```
Option A: Terminate at Load Balancer / CDN  (most common)
  Client ══TLS══► ALB / CloudFront / Nginx ──HTTP (private VPC)──► Node.js
  ✅ certs in one place, app servers simpler, LB can inspect L7 (routing by path)
  ❌ traffic inside VPC unencrypted (OK for most; not for strict compliance)

Option B: Re-encrypt (TLS bridging)
  Client ══TLS══► ALB ══TLS══► Node.js
  ✅ encrypted end to end inside the network (PCI-DSS, banking)
  ❌ more CPU, more certs to manage

Option C: TLS passthrough (L4 LB)
  Client ══════TLS (LB doesn't decrypt)═════► App server
  ✅ LB never sees data    ❌ no path-based routing, no WAF

mTLS (mutual TLS): BOTH sides present certificates → service-to-service auth in
microservices / service mesh (Istio) — Topic 94.
```

## 🟢 कैसे काम करता है? (Hindi)
1. क्लाइंट "Hello" भेजता है — कौन-कौन से एन्क्रिप्शन आते हैं, और अपनी key share।
2. सर्वर अपना certificate भेजता है; क्लाइंट जाँचता है कि यह किसी भरोसेमंद CA ने साइन किया है और डोमेन सही है।
3. दोनों अपनी key share मिलाकर एक ही गुप्त चाबी (session key) बना लेते हैं — चाबी नेटवर्क पर कभी जाती ही नहीं।
4. इसके बाद सारा डेटा तेज़ symmetric encryption (AES) से लॉक होकर जाता है।
5. TLS 1.3 में यह सब सिर्फ़ 1 round trip में हो जाता है।

---

## 🟡 Real World Example

**Let's Encrypt**
- Before 2015, certificates cost money and had a manual process, so many small sites stayed on HTTP. Let's Encrypt made free, automated 90-day certificates. Today it issues certificates for 300+ million websites, a big reason the web is ~95% HTTPS.

**Expired certificate outages**
- Microsoft Teams (2020), Spotify, LinkedIn and the Pokémon GO servers all had outages because someone forgot to renew a certificate. Lesson: **automate renewal + monitor expiry**.

**Banking apps & SSL pinning**
- Apps like PhonePe and banking apps "pin" their server's certificate/public key inside the app. Even if a user installs a malicious root CA (or a corporate proxy intercepts traffic), the app refuses to connect. (Mobile topic M15.)

**Corporate proxies (TLS inspection)**
- Companies install their own root CA on employees' laptops so the firewall can decrypt and inspect HTTPS. That's a "legal man-in-the-middle", and it's exactly what pinning blocks.

## 🟡 Real Example Hindi में
Let's Encrypt ने 2015 से मुफ़्त certificate देना शुरू किया, इसलिए आज लगभग हर वेबसाइट HTTPS पर है।
Microsoft Teams और Spotify जैसी कंपनियाँ भी certificate expire होने से डाउन हुई हैं — इसलिए renewal हमेशा automatic रखो। बैंकिंग ऐप्स SSL pinning करती हैं ताकि नकली certificate से कोई बीच में न घुस सके।

---

## 🟠 My Stack Example

### VPS + Nginx + Let's Encrypt (your common setup)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d myapp.com -d api.myapp.com
sudo certbot renew --dry-run           # renewal runs automatically via systemd timer
```

```nginx
server {
  listen 443 ssl;
  http2 on;
  server_name api.myapp.com;

  ssl_certificate     /etc/letsencrypt/live/api.myapp.com/fullchain.pem;  # leaf + intermediate
  ssl_certificate_key /etc/letsencrypt/live/api.myapp.com/privkey.pem;    # NEVER commit this

  ssl_protocols TLSv1.2 TLSv1.3;         # disable SSLv3, TLS 1.0, 1.1
  ssl_prefer_server_ciphers off;         # let TLS 1.3 clients pick (Mozilla "intermediate")
  ssl_session_cache shared:SSL:10m;      # session resumption → faster repeat handshakes
  ssl_session_timeout 1d;
  ssl_stapling on;                       # OCSP stapling: server proves cert not revoked
  ssl_stapling_verify on;

  location / {
    proxy_pass http://api:3000;          # TLS terminated here; plain HTTP inside Docker network
    proxy_set_header X-Forwarded-Proto https;
  }
}
```

### Docker Compose with Caddy (auto-HTTPS alternative)
```yaml
services:
  caddy:
    image: caddy:2
    ports: ["80:80", "443:443", "443:443/udp"]   # 443/udp → HTTP/3
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
      - caddy_data:/data
# Caddyfile:
#   api.myapp.com {
#     reverse_proxy api:3000
#   }
# Caddy gets and renews Let's Encrypt certs automatically.
```

### AWS
```
Route 53 → CloudFront (ACM cert, us-east-1) → S3 / Next.js
Route 53 → ALB (ACM cert, ap-south-1) → EC2/ECS Node.js on HTTP 3000
ACM certs are free and auto-renew. Private keys never leave AWS.
```

### Node.js — behind a TLS-terminating proxy
```js
app.set('trust proxy', 1);
app.use((req, res, next) => {
  // req.secure is true when X-Forwarded-Proto is https
  if (!req.secure) return res.redirect(301, `https://${req.headers.host}${req.url}`);
  next();
});
```

### Connecting to managed Postgres (RDS) over TLS
```js
const pool = new pg.Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: { ca: fs.readFileSync('rds-global-bundle.pem').toString(), rejectUnauthorized: true },
});
// ❌ Never "rejectUnauthorized: false" in prod — that disables certificate checks (MITM possible).
```

### Debug / monitor certificates
```bash
openssl s_client -connect api.myapp.com:443 -servername api.myapp.com </dev/null \
  | openssl x509 -noout -subject -issuer -dates       # who issued, expiry date
curl -vI https://api.myapp.com 2>&1 | grep -E "SSL|TLS|expire"
# Online: ssllabs.com/ssltest → aim for grade A
```
Set an uptime monitor (UptimeRobot / Better Stack / CloudWatch) to alert 14 days before expiry.

---

## ⚫ Interview Questions + Answers

**Q1: Walk me through a TLS handshake.**
A1: (TLS 1.3) The client sends ClientHello with supported cipher suites, a key share (ephemeral ECDHE public value) and SNI (hostname). The server replies with ServerHello (chosen cipher, its key share), its certificate, a signature proving it owns the private key (CertificateVerify), and Finished. The client validates the certificate chain against its trust store, checks hostname and expiry, and both sides derive the same symmetric session key from the key shares. All further data is encrypted with AES-GCM or ChaCha20. One round trip, or 0-RTT on resumption.

**Q2: Why does TLS use both asymmetric and symmetric encryption?**
A2: Asymmetric crypto solves key agreement and identity between strangers, but it's slow. Symmetric crypto is very fast but needs a shared key. TLS uses asymmetric operations only during the handshake to authenticate and agree on a key, then symmetric encryption for the bulk data.

**Q3: How does the browser know a certificate is valid?**
A3: It builds a chain from the server's leaf certificate through intermediate CAs to a root CA that is pre-installed in the OS/browser trust store, and verifies each signature. It also checks that the hostname matches the certificate's SAN, that the certificate is within its validity dates, and its revocation status (OCSP/CRL, often via OCSP stapling). Public certificates must also appear in Certificate Transparency logs.

**Q4: Where should TLS be terminated in a microservices architecture?**
A4: Usually at the edge (CDN/load balancer/API gateway), which centralizes certificates, offloads CPU, and allows L7 routing and a WAF. Internal traffic stays inside a private VPC. For zero-trust or compliance (PCI, healthcare), re-encrypt to the backends, or use mTLS between services, often automated by a service mesh such as Istio or Linkerd.

**Q5: What is forward secrecy and why does it matter?**
A5: With forward secrecy, each session uses ephemeral Diffie-Hellman keys that are thrown away afterwards. If the server's long-term private key is stolen later, attackers still can't decrypt previously recorded sessions. TLS 1.3 makes it mandatory by removing RSA key exchange.

---

## 🔷 Trade-offs
✅ Advantages:
- Confidentiality + integrity + server authentication.
- TLS 1.3 is fast (1-RTT, 0-RTT) with tiny CPU overhead on modern hardware (AES-NI).
- Free and automated certificates (Let's Encrypt, ACM).

❌ Disadvantages:
- Certificate lifecycle management — expiry causes outages if not automated.
- Extra handshake latency on new connections (mitigated by resumption, keep-alive).
- Encrypted traffic is harder to debug/inspect (need logs at the termination point).
- 0-RTT data can be replayed — only use it for idempotent requests.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| TLS | Protocol that encrypts traffic | डेटा एन्क्रिप्ट करने का प्रोटोकॉल |
| Certificate | Signed proof of domain ownership + public key | सर्वर की पहचान का प्रमाणपत्र |
| CA | Trusted organization that signs certificates | प्रमाणपत्र जारी करने वाली भरोसेमंद संस्था |
| Public / Private key | Key pair: lock/verify vs unlock/sign | सार्वजनिक / निजी चाबी |
| Symmetric encryption | Same key both sides (AES) | एक ही चाबी से लॉक-अनलॉक |
| Handshake | Negotiation before encrypted data | एन्क्रिप्शन से पहले की बातचीत |
| Forward secrecy | Old sessions safe even if key leaks | पुराना डेटा हमेशा सुरक्षित |
| TLS termination | Point where traffic is decrypted | जहाँ डेटा डिक्रिप्ट होता है |
| mTLS | Both client & server show certificates | दोनों तरफ़ से पहचान |
| SSL pinning | App trusts only a specific cert/key | ऐप सिर्फ़ तय certificate माने |

---

## ⚡ 3-Line Summary
**English:**
1. TLS = certificate (identity) + key exchange (shared secret) + symmetric encryption (fast data).
2. TLS 1.3: 1-RTT handshake, forward secrecy by default; SSL and TLS 1.0/1.1 are dead.
3. Terminate TLS at the edge (Nginx/ALB/CDN), automate certs (Let's Encrypt/ACM), monitor expiry.

**Hindi:**
1. TLS = certificate से पहचान + key exchange से गुप्त चाबी + AES से तेज़ एन्क्रिप्शन।
2. TLS 1.3 सिर्फ़ 1 round trip लेता है; SSL अब पुराना और असुरक्षित है।
3. TLS को Nginx/ALB पर ख़त्म करो, certificate auto-renew रखो, expiry पर अलर्ट लगाओ।

---

## ➡️ Next Topic Suggestion
**07. REST API Design** — The secure pipe is ready. Next: how to design clean, scalable APIs on top of it — resources, URLs, methods, status codes, pagination, filtering, errors and versioning, which every backend interview checks.
