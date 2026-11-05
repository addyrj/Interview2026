# 406. Let's Encrypt in Docker
# हिंदी में: Docker में Let's Encrypt

---

## 🔵 Simple Definition (English)
**Let's Encrypt** is a free, automated Certificate Authority. In Docker you run its client (usually **Certbot**) as a container that proves you control a domain (the ACME challenge), receives a certificate, stores it in a shared volume, and renews it every ~60 days. Nginx then reads that volume.

## 🔵 सरल परिभाषा (Hindi)
**Let's Encrypt** एक free, automated Certificate Authority है। Docker में इसका client (आम तौर पर **Certbot**) container की तरह चलता है, domain पर आपका कंट्रोल साबित करता है (ACME challenge), certificate लेता है, shared volume में रखता है और हर ~60 दिन में renew करता है। Nginx उसी volume से पढ़ता है।

---

## 🔴 Problem it Solves
- Paid certificates cost money and need manual purchase, CSR, upload and renewal.
- Manual renewals get forgotten, then the site shows "certificate expired" at 2 AM.
- Self-signed certs are rejected by browsers and API clients.

## 🔴 यह क्यों बना? (Hindi)
- Paid certificates में पैसा लगता है और खरीदना, CSR, upload, renewal सब manual।
- Manual renewal भूल जाते हैं और रात 2 बजे "certificate expired" दिखता है।
- Self-signed certs को browsers और API clients reject करते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → DNS: app.example.com A record -> your VPS public IP
Step 2 → Nginx serves /.well-known/acme-challenge/ from a shared
         "webroot" volume on port 80
Step 3 → certbot certonly --webroot asks Let's Encrypt for a cert
Step 4 → LE gives a random token; certbot writes it in the webroot
Step 5 → LE fetches http://app.example.com/.well-known/acme-challenge/<token>
         from the internet; match -> domain validated
Step 6 → Cert + key saved in /etc/letsencrypt (a named volume)
Step 7 → Nginx mounts the same volume, listens on 443 with the cert
Step 8 → certbot renew runs twice daily; renews if < 30 days left,
         then nginx -s reload picks the new cert
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → DNS: app.example.com का A record -> VPS का public IP
Step 2 → Nginx port 80 पर shared "webroot" volume से
         /.well-known/acme-challenge/ serve करता है
Step 3 → certbot certonly --webroot Let's Encrypt से cert माँगता है
Step 4 → LE एक random token देता है; certbot उसे webroot में लिखता है
Step 5 → LE internet से http://app.example.com/.well-known/acme-challenge/<token>
         खोलता है; match हुआ -> domain validated
Step 6 → Cert + key /etc/letsencrypt (named volume) में save होते हैं
Step 7 → Nginx वही volume mount करके 443 पर cert के साथ listen करता है
Step 8 → certbot renew दिन में दो बार चलता है; 30 दिन से कम बचें तो renew,
         फिर nginx -s reload नया cert उठाता है
```

---

## 🟡 Real World Example
A freelancer hosts five client sites on one Hostinger VPS. Before Let's Encrypt, each paid certificate expired on a different date. Now one Certbot container requests certs for all five domains and a renew loop keeps them valid. The monthly "cert renewal" calendar reminder is deleted.

## 🟡 Real Example Hindi mein
एक freelancer एक Hostinger VPS पर पाँच client sites होस्ट करता है। Let's Encrypt से पहले हर paid certificate अलग तारीख पर expire होता था। अब एक Certbot container पाँचों domains के certs माँगता है और renew loop उन्हें valid रखता है। महीने वाला "cert renewal" calendar reminder हट गया।

---

## 💻 Code / Config Example — Basic

```bash
# Step A: always test against the STAGING CA first (no rate-limit pain)
docker run --rm \
  -v certbot-etc:/etc/letsencrypt \
  -v certbot-www:/var/www/certbot \
  certbot/certbot certonly \
  --webroot -w /var/www/certbot \
  -d app.example.com \
  --email you@example.com --agree-tos --no-eff-email \
  --staging
# -v certbot-etc:...    : named volume to persist certs/keys/account
# -v certbot-www:...    : webroot where challenge files are written
# certonly --webroot    : only obtain cert, do not edit nginx config
# -w                    : webroot path inside the certbot container
# -d                    : domain to certify (must point to this server)
# --staging             : fake CA for testing; browsers will not trust it

# Step B: real certificate (remove --staging, add --force-renewal if replacing staging)
docker run --rm -v certbot-etc:/etc/letsencrypt -v certbot-www:/var/www/certbot \
  certbot/certbot certonly --webroot -w /var/www/certbot \
  -d app.example.com --email you@example.com --agree-tos --no-eff-email \
  --force-renewal
```

```nginx
# nginx/conf.d/acme.conf -- HTTP server that answers ACME challenges
server {
    listen 80;                                          # LE validates over port 80
    server_name app.example.com;                        # domain being certified
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;                          # shared with certbot volume
    }
    location / {
        return 301 https://$host$request_uri;           # everything else -> HTTPS
    }
}
```

## 💻 Code / Config Example — Advanced

```yaml
# docker-compose.yml -- nginx + certbot auto-renew loop
services:
  nginx:
    image: nginx:1.27-alpine
    restart: unless-stopped
    ports: ["80:80", "443:443"]
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d:ro             # configs
      - certbot-etc:/etc/letsencrypt:ro                 # certs (read-only for nginx)
      - certbot-www:/var/www/certbot:ro                 # challenge files
    # reload nginx every 6h so renewed certs are picked up
    command: >
      /bin/sh -c 'while :; do sleep 6h & wait $${!}; nginx -s reload; done &
      nginx -g "daemon off;"'
  certbot:
    image: certbot/certbot:latest                       # pin a version in real use
    restart: unless-stopped
    volumes:
      - certbot-etc:/etc/letsencrypt                    # read-write: stores certs
      - certbot-www:/var/www/certbot                    # writes challenge tokens
    # try renewal every 12h; certbot only renews when < 30 days remain
    entrypoint: >
      /bin/sh -c 'trap exit TERM; while :; do certbot renew --webroot -w /var/www/certbot --quiet;
      sleep 12h & wait $${!}; done'
volumes:
  certbot-etc: {}                                       # persistent cert storage
  certbot-www: {}                                       # persistent challenge dir
```

```nginx
# nginx/conf.d/site.conf -- HTTPS server using the LE paths
server {
    listen 443 ssl;                                                     # TLS
    http2 on;                                                           # nginx >= 1.25.1
    server_name app.example.com;
    ssl_certificate     /etc/letsencrypt/live/app.example.com/fullchain.pem;  # cert+chain
    ssl_certificate_key /etc/letsencrypt/live/app.example.com/privkey.pem;    # key
    ssl_protocols TLSv1.2 TLSv1.3;                                      # modern TLS only
    add_header Strict-Transport-Security "max-age=31536000" always;     # HSTS
    location / { proxy_pass http://api:3000; proxy_set_header Host $host; }
}
```

Chicken-and-egg warning: Nginx will not start if the `ssl_certificate` file does not exist yet. First deploy only the port-80 `acme.conf` (without the 443 server), obtain the cert, then add `site.conf` and reload. Topic 407 gives a complete script for this. Compose `$${!}` escapes `$` for the shell. Not run locally (no daemon, no public domain).

---

## 🟠 My Stack Integration
Domain DNS (A record) -> Hostinger VPS IP; ports 80 and 443 open in the firewall (`ufw allow 80,443/tcp`). The `api` and `ml` services stay private. For wildcard certs (`*.example.com`) you need the DNS-01 challenge with a DNS plugin (for example Route 53 on AWS) instead of webroot.

```bash
# AWS Route 53 DNS-01 example (wildcard); needs the dns-route53 plugin image
docker run --rm -v certbot-etc:/etc/letsencrypt \
  -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY \
  certbot/dns-route53 certonly --dns-route53 \
  -d '*.example.com' -d example.com --agree-tos --email you@example.com
```

Security: the `certbot-etc` volume holds private keys; give nginx read-only access, back it up securely, never print it in CI logs. Use a least-privilege IAM user for Route 53 (only `ChangeResourceRecordSets` on that zone). Let's Encrypt rate limits (e.g. 5 duplicate certificates per week, 50 per registered domain per week; check current docs) make `--staging` essential.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Not persisting `/etc/letsencrypt`, so each container run loses certs and you hit rate limits.
✅ Correct: Use a named volume or bind mount.

❌ Mistake 2: Port 80 blocked or redirecting ACME path to HTTPS before the cert exists.
✅ Correct: Keep `/.well-known/acme-challenge/` served over plain HTTP.

❌ Mistake 3: Renewal works but Nginx still serves the old cert.
✅ Correct: Schedule `nginx -s reload` (or use `--deploy-hook`).

❌ Mistake 4: Testing on the production CA repeatedly.
✅ Correct: Use `--staging` / `--dry-run` until the flow works.

---

## 🧠 Tricky Interview Question
Certbot renewal succeeds in the logs, yet users see an expired certificate after 90 days. Name two likely reasons.

Answer: (1) Nginx was never reloaded, so it keeps the old certificate in memory. (2) Nginx and Certbot use different volumes (or Nginx mounts a single file that was replaced via symlink swap), so Nginx reads stale files. Note `/etc/letsencrypt/live/<domain>/` holds symlinks to `archive/`; mount the whole `/etc/letsencrypt` directory, not individual files.

---

## ⚫ Interview Questions + Answers

Q1: What is the ACME protocol?
A1: Automatic Certificate Management Environment: the standard by which a client proves domain control to a CA and receives certificates automatically.

Q2: HTTP-01 vs DNS-01?
A2: HTTP-01 serves a token over port 80 (simple, no wildcards). DNS-01 creates a TXT record (works behind firewalls and supports wildcards, but needs DNS API credentials).

Q3: How long do Let's Encrypt certs last?
A3: 90 days; renew at about 60 days. Short life limits damage from key compromise and forces automation.

Q4: What is `--dry-run`?
A4: Simulates renewal against the staging CA without saving real certs; used to test the pipeline.

Q5: Can the same cert cover multiple domains?
A5: Yes, with several `-d` flags (SAN certificate), up to 100 names per certificate.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You own a public domain pointing to your server.
- You want free, automated HTTPS.

❌ Avoid when:
- Server has no public inbound access and DNS-01 is not possible (use an internal CA).
- A cloud service already provides managed certs (ACM on ALB/CloudFront).

---

## 📊 Visual Diagram
```
  Let's Encrypt CA
     ^   |  1. order cert for app.example.com
     |   v  2. token challenge
  +---------------------- VPS ----------------------+
  | certbot --writes token--> [certbot-www volume]  |
  |                                  |  (shared)    |
  | nginx :80 /.well-known/... <-----+              |
  |      ^  3. LE fetches token over HTTP           |
  | certbot --saves cert--> [certbot-etc volume]    |
  | nginx :443 reads cert  <------ (ro mount)       |
  | every 12h: certbot renew -> nginx -s reload     |
  +-------------------------------------------------+
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| CA | Authority that signs certs | प्रमाणन संस्था |
| ACME | Protocol for automatic issuance | स्वचालित issuance protocol |
| Webroot | Folder served for challenge files | challenge files का folder |
| Staging | Test CA, untrusted certs | test CA |
| SAN | One cert, many domain names | एक cert, कई domains |
| Rate limit | Max requests per period | सीमा |

---

## ⚡ 3-Line Summary
English: Certbot in a container proves domain ownership via a shared webroot and stores certs in a volume.
Nginx reads that volume; a loop renews and reloads.
Use staging first and protect the key volume.
Hindi: Container में Certbot shared webroot से domain ownership साबित करके certs volume में रखता है।
Nginx उसी volume को पढ़ता है; एक loop renew और reload करता है।
पहले staging इस्तेमाल करो और key volume की सुरक्षा रखो।

---

## ➡️ Next Topic
407. Certbot + Nginx + Docker - a full, step-by-step bootstrap that solves the "no cert yet, nginx won't start" problem.
