# 404. Nginx SSL in Docker
# हिंदी में: Docker में Nginx पर SSL/HTTPS

---

## 🔵 Simple Definition (English)
**Nginx SSL in Docker** means terminating HTTPS in the Nginx container: you mount a certificate and private key into it, listen on port 443 with `ssl`, and forward plain HTTP to backend containers over the private network. This is called **TLS termination**.

## 🔵 सरल परिभाषा (Hindi)
**Docker में Nginx SSL** मतलब HTTPS Nginx container में ही खत्म (terminate) करना: certificate और private key mount करो, port 443 पर `ssl` के साथ listen करो, और private network पर plain HTTP से backend containers को forward करो। इसे **TLS termination** कहते हैं।

---

## 🔴 Problem it Solves
- Plain HTTP exposes passwords, tokens and cookies to anyone on the network path.
- Browsers mark HTTP sites "Not secure"; many APIs, PWAs, service workers and secure cookies require HTTPS.
- Implementing TLS in every Node.js/FastAPI app duplicates work and certificate handling.

## 🔴 यह क्यों बना? (Hindi)
- Plain HTTP में passwords, tokens, cookies network पर किसी को भी दिख सकते हैं।
- Browsers HTTP sites को "Not secure" दिखाते हैं; कई APIs, PWAs, secure cookies को HTTPS चाहिए।
- हर Node.js/FastAPI app में TLS लगाना काम दोहराना है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Obtain cert + key (Let's Encrypt in 406/407, or purchased/self-signed)
Step 2 → Mount them read-only: ./certs -> /etc/nginx/certs
Step 3 → server { listen 443 ssl; ssl_certificate ...; ssl_certificate_key ...; }
Step 4 → Client and Nginx do TLS handshake (TLS 1.2/1.3), cipher chosen
Step 5 → Nginx decrypts and proxy_pass http://api:3000 (plain, internal)
Step 6 → Port 80 server redirects everything to https:// (301)
Step 7 → Add HSTS header so browsers stick to HTTPS
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Cert + key लो (406/407 में Let's Encrypt, या purchased/self-signed)
Step 2 → Read-only mount करो: ./certs -> /etc/nginx/certs
Step 3 → server { listen 443 ssl; ssl_certificate ...; ssl_certificate_key ...; }
Step 4 → Client और Nginx TLS handshake करते हैं (TLS 1.2/1.3)
Step 5 → Nginx decrypt करके proxy_pass http://api:3000 (plain, internal) करता है
Step 6 → Port 80 वाला server सब कुछ https:// पर redirect (301) करता है
Step 7 → HSTS header जोड़ो ताकि browsers हमेशा HTTPS ही इस्तेमाल करें
```

---

## 🟡 Real World Example
A fintech dashboard on a VPS gets a security audit finding: "login over HTTP". The team mounts a certificate into the Nginx container, adds a 301 redirect from port 80 and HSTS, and sets cookies with `Secure; HttpOnly`. Node.js still talks plain HTTP on the internal network, so no application code is changed apart from `trust proxy`.

## 🟡 Real Example Hindi mein
VPS पर एक fintech dashboard को security audit में finding मिलती है: "login HTTP पर है"। Team Nginx container में certificate mount करती है, port 80 से 301 redirect और HSTS जोड़ती है, और cookies `Secure; HttpOnly` रखती है। Node.js internal network पर plain HTTP ही बोलता है, इसलिए app code में सिर्फ `trust proxy` बदलना पड़ता है।

---

## 💻 Code / Config Example — Basic

```bash
# Create a SELF-SIGNED certificate for local testing only (browsers will warn)
mkdir -p certs                                          # folder to hold cert files
openssl req -x509 -nodes -newkey rsa:2048 -days 30 \
  -keyout certs/privkey.pem -out certs/fullchain.pem \
  -subj "/CN=localhost"
# -x509            : produce a certificate, not a request
# -nodes           : do not encrypt the key (nginx must start unattended)
# -newkey rsa:2048 : generate a new 2048-bit RSA key
# -days 30         : valid for 30 days (test cert)
# -subj /CN=...    : common name = host you will browse
chmod 600 certs/privkey.pem                             # key readable by owner only
```

```nginx
# nginx/conf.d/ssl.conf -- minimal HTTPS server
server {
    listen 443 ssl;                                     # HTTPS port with TLS
    server_name localhost;                              # replace with your domain
    ssl_certificate     /etc/nginx/certs/fullchain.pem; # public cert (+ chain)
    ssl_certificate_key /etc/nginx/certs/privkey.pem;   # private key
    location / {
        proxy_pass http://api:3000;                     # plain HTTP to backend
        proxy_set_header X-Forwarded-Proto https;       # tell app original scheme
        proxy_set_header Host $host;                    # keep host
    }
}
```

```yaml
# docker-compose.yml -- mount certs read-only and publish 443
services:
  nginx:
    image: nginx:1.27-alpine
    ports: ["80:80", "443:443"]                          # both ports
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d:ro              # config
      - ./certs:/etc/nginx/certs:ro                      # cert + key, read-only
    depends_on: [api]
  api:
    build: ./api                                         # Node.js on 3000
```

## 💻 Code / Config Example — Advanced

```nginx
# nginx/conf.d/ssl.conf -- production-grade TLS
server {
    listen 80;                                           # plain HTTP only for redirect (and ACME in 406)
    server_name app.example.com;                         # example domain
    location / { return 301 https://$host$request_uri; } # force HTTPS
}

server {
    listen 443 ssl;                                      # TLS listener
    http2 on;                                            # HTTP/2 (nginx >= 1.25.1 syntax)
    server_name app.example.com;
    server_tokens off;                                   # hide version

    ssl_certificate     /etc/nginx/certs/fullchain.pem;  # cert + intermediates
    ssl_certificate_key /etc/nginx/certs/privkey.pem;    # private key
    ssl_protocols TLSv1.2 TLSv1.3;                       # disable SSLv3/TLS1.0/1.1
    ssl_prefer_server_ciphers off;                       # let modern clients choose
    ssl_session_cache shared:SSL:10m;                    # resume sessions (~40k)
    ssl_session_timeout 1d;                              # session lifetime
    ssl_session_tickets off;                             # better forward secrecy
    ssl_stapling on;                                     # OCSP stapling (needs resolver + chain cert)
    ssl_stapling_verify on;
    resolver 1.1.1.1 8.8.8.8 valid=300s;                 # resolver for OCSP lookups

    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;  # HSTS
    add_header X-Content-Type-Options nosniff always;    # no MIME sniffing
    add_header X-Frame-Options DENY always;              # clickjacking protection

    location /api/ {
        proxy_pass http://api:3000;                      # internal plain HTTP
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;        # app knows request was secure
    }
}
```

```yaml
# docker-compose.yml -- secrets via Docker secrets instead of a bind-mounted key
services:
  nginx:
    image: nginx:1.27-alpine
    restart: unless-stopped
    ports: ["80:80", "443:443"]
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./certs/fullchain.pem:/etc/nginx/certs/fullchain.pem:ro   # public part
    secrets:
      - source: tls_key                                  # private key as a secret
        target: /etc/nginx/certs/privkey.pem             # appears here inside container
secrets:
  tls_key:
    file: ./certs/privkey.pem                            # host file, chmod 600, not in Git
```

Note: `http2 on;` needs Nginx 1.25.1+ (older versions use `listen 443 ssl http2;`). Compose file-based secrets mount as root-readable files; check the nginx master (root) can read it. Not run locally; verify with `nginx -t` inside the image and test with `curl -vk` / SSL Labs.

---

## 🟠 My Stack Integration
- Express: `app.set('trust proxy', 1)` so `req.secure` and secure cookies work behind Nginx.
- FastAPI: start uvicorn with `--proxy-headers` so redirects use `https`.
- React: serve the build from Nginx on 443; set API base URL to a relative `/api` to avoid mixed-content errors.
- AWS: if you later use ALB + ACM, TLS terminates at ALB and Nginx can keep port 80 internally.

```yaml
# CI check: fail the pipeline if cert config is invalid (GitHub Actions step)
      - name: Test nginx config   # runs the exact image in CI
        run: |
          docker run --rm \
            -v "$PWD/nginx/conf.d:/etc/nginx/conf.d:ro" \
            -v "$PWD/certs-ci:/etc/nginx/certs:ro" \
            nginx:1.27-alpine nginx -t
```

Security: never commit `privkey.pem`; add `certs/` to `.gitignore`; permissions 600; disable TLS < 1.2; enable HSTS only after you are sure HTTPS works for all subdomains; rotate and monitor expiry.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using only `cert.pem` (leaf) without intermediates, so some clients show chain errors.
✅ Correct: Use `fullchain.pem`.

❌ Mistake 2: Committing the private key to Git or baking it into the image.
✅ Correct: Mount at runtime / use secrets and keep it out of the repo.

❌ Mistake 3: Redirect loop because the app also redirects to HTTPS while seeing HTTP from Nginx.
✅ Correct: Send `X-Forwarded-Proto` and let the app trust it; redirect only in Nginx.

❌ Mistake 4: Forgetting to publish `443:443` (only `80:80`).
✅ Correct: Publish both and open 443 in the VPS firewall/security group.

---

## 🧠 Tricky Interview Question
Certificates were renewed on the host but users still get the old expired certificate. Nginx container is running fine. Why?

Answer: Nginx loads certificates into memory at start/reload. The new file on disk is not used until `nginx -s reload`. Also if the cert was mounted as a single-file bind mount and replaced by a tool that swaps inodes, the container may still see the old file; mounting the parent directory avoids this. Fix: mount the directory and reload Nginx after every renewal (deploy hook).

---

## ⚫ Interview Questions + Answers

Q1: What is TLS termination?
A1: The proxy decrypts HTTPS and forwards plain HTTP to backends, centralising certificates and offloading crypto from apps.

Q2: Should internal traffic also be encrypted?
A2: On a single private Docker network plain HTTP is usually accepted; for compliance or multi-host networks use mTLS or re-encryption (`proxy_pass https://...`).

Q3: What is HSTS and its risk?
A3: A header telling browsers to use only HTTPS for a period. If you later break HTTPS, browsers will refuse HTTP fallback until it expires, so roll out with a small max-age first.

Q4: Difference between `fullchain.pem` and `privkey.pem`?
A4: fullchain = your cert plus issuer chain (public). privkey = the secret key that proves you own it; never share.

Q5: Why disable `ssl_session_tickets`?
A5: Tickets are encrypted with a long-lived server key; if leaked, past sessions can be decrypted, hurting forward secrecy.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Anything user-facing or carrying credentials (always, in practice).
- You need HTTP/2, secure cookies, service workers.

❌ Avoid when:
- A cloud LB/CDN (ALB, Cloudflare) already terminates TLS and you only need internal HTTP; do not double-terminate without reason.

---

## 📊 Visual Diagram
```
 Browser ==== TLS 1.3 (encrypted) ====> nginx :443
                                          |  certs mounted :ro
                                          |  (fullchain.pem, privkey.pem)
   http://...:80 --301--> https://        |
                                          v  plain HTTP, private network
                                       api:3000 / ml:8000
   Headers added: Strict-Transport-Security, X-Forwarded-Proto: https
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| TLS | Encryption protocol behind HTTPS | HTTPS की encryption |
| TLS termination | Decrypt at the proxy | proxy पर decrypt |
| Certificate | Public identity proof signed by a CA | प्रमाणपत्र |
| Private key | Secret half of the key pair | निजी कुंजी |
| HSTS | Force HTTPS in browser | HTTPS अनिवार्य |
| OCSP stapling | Server attaches revocation status | revocation स्थिति |
| Self-signed | Cert signed by yourself | खुद-हस्ताक्षरित |

---

## ⚡ 3-Line Summary
English: Mount cert and key into Nginx, listen on 443 ssl, redirect 80 to 443.
Backends stay plain HTTP on a private network and trust `X-Forwarded-Proto`.
Reload after cert changes; never commit the key.
Hindi: Cert और key Nginx में mount करो, 443 ssl पर listen करो, 80 को 443 पर redirect करो।
Backends private network पर plain HTTP रखते हैं और `X-Forwarded-Proto` पर भरोसा करते हैं।
Cert बदलने पर reload करो; key कभी commit मत करो।

---

## ➡️ Next Topic
405. Nginx Config Management in CI/CD - certificates are in place; next we keep all Nginx config versioned, tested and deployed through pipelines.
