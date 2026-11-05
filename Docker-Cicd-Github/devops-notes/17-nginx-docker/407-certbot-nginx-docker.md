# 407. Certbot + Nginx + Docker
# हिंदी में: Certbot + Nginx + Docker (पूरा HTTPS setup)

---

## 🔵 Simple Definition (English)
This topic combines the three pieces into one working recipe: **Nginx** (web server), **Certbot** (certificate client) and **Docker Compose** (glue). The key trick is a two-phase bootstrap: start Nginx on port 80 only, get the first certificate, then enable HTTPS and automatic renewal.

## 🔵 सरल परिभाषा (Hindi)
यह topic तीनों हिस्सों को एक चलने वाली recipe में जोड़ता है: **Nginx** (web server), **Certbot** (certificate client) और **Docker Compose** (जोड़ने वाला)। मुख्य तरकीब two-phase bootstrap है: पहले सिर्फ port 80 पर Nginx चलाओ, पहला certificate लो, फिर HTTPS और auto-renewal चालू करो।

---

## 🔴 Problem it Solves
- Chicken-and-egg: Nginx with `listen 443 ssl` refuses to start without cert files, but Certbot needs a running web server on port 80 to get them.
- People work around it with manual `docker run` commands that nobody can reproduce.
- Renewal is forgotten, or renews but never reloads Nginx.

## 🔴 यह क्यों बना? (Hindi)
- Chicken-and-egg: `listen 443 ssl` वाला Nginx cert files के बिना start नहीं होता, पर Certbot को cert लेने के लिए port 80 पर चलता web server चाहिए।
- लोग manual `docker run` commands से काम चलाते हैं जिन्हें कोई दोहरा नहीं पाता।
- Renewal भूल जाते हैं, या renew होता है पर Nginx reload नहीं होता।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Point DNS A record of the domain to the VPS; open ports 80/443
Step 2 → Phase 1: start nginx with HTTP-only config (acme.conf)
Step 3 → Run certbot once (staging first, then real) to fetch the cert
Step 4 → Phase 2: swap in the HTTPS config (site.conf), reload nginx
Step 5 → Start the renewal loop container (certbot renew every 12h)
Step 6 → A deploy hook / cron reloads nginx after renewal
Step 7 → Verify: curl -I https://domain, openssl s_client expiry date
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Domain का DNS A record VPS पर point करो; ports 80/443 खोलो
Step 2 → Phase 1: nginx को सिर्फ HTTP config (acme.conf) के साथ start करो
Step 3 → certbot एक बार चलाओ (पहले staging, फिर real) और cert लो
Step 4 → Phase 2: HTTPS config (site.conf) लगाओ, nginx reload करो
Step 5 → Renewal loop container चालू करो (हर 12 घंटे certbot renew)
Step 6 → Renewal के बाद deploy hook / cron nginx reload करता है
Step 7 → जाँच: curl -I https://domain, openssl s_client से expiry date
```

---

## 🟡 Real World Example
A student startup moves a Node.js MVP from `http://203.0.113.10:3000` (the VPS IP) to `https://mvp.example.com`. They run `./init-letsencrypt.sh` once on the VPS, it creates the cert and switches Nginx to HTTPS. Three months later nobody has touched anything and the site still has a valid certificate.

## 🟡 Real Example Hindi mein
एक student startup अपना Node.js MVP `http://203.0.113.10:3000` (VPS IP) से `https://mvp.example.com` पर ले जाती है। वे VPS पर एक बार `./init-letsencrypt.sh` चलाते हैं, वह cert बनाकर Nginx को HTTPS पर switch करता है। तीन महीने बाद किसी ने कुछ नहीं छुआ और site का certificate अब भी valid है।

---

## 💻 Code / Config Example — Basic

```bash
#!/usr/bin/env bash
# init-letsencrypt.sh -- one-time bootstrap (run on the VPS in the project folder)
set -euo pipefail                                     # fail fast on any error

DOMAIN="${DOMAIN:-app.example.com}"                   # domain (override via env)
EMAIL="${EMAIL:-you@example.com}"                     # expiry notices go here
STAGING="${STAGING:-1}"                               # 1 = test CA, 0 = real CA

mkdir -p nginx/conf.d                                 # config directory

# Phase 1: HTTP-only config so nginx can start without certificates
cat > nginx/conf.d/default.conf <<EOF
server {
    listen 80;
    server_name ${DOMAIN};
    location /.well-known/acme-challenge/ { root /var/www/certbot; }
    location / { return 200 'bootstrap ok'; add_header Content-Type text/plain; }
}
EOF

docker compose up -d nginx                            # start only nginx

ARGS=""                                               # extra flags for certbot
[ "$STAGING" = "1" ] && ARGS="--staging"              # use staging when requested

docker compose run --rm --entrypoint certbot certbot \
  certonly --webroot -w /var/www/certbot \
  -d "$DOMAIN" --email "$EMAIL" --agree-tos --no-eff-email $ARGS
# --entrypoint certbot : override the renew-loop entrypoint for this one-off run
# certonly --webroot   : obtain the cert only; nginx config stays ours

echo "Cert obtained. Now copy nginx/site.conf.example to nginx/conf.d/default.conf and run:"
echo "  docker compose exec nginx nginx -t && docker compose exec nginx nginx -s reload"
```

## 💻 Code / Config Example — Advanced

```yaml
# docker-compose.yml -- full stack: nginx + certbot + Node.js API + FastAPI
services:
  nginx:
    image: nginx:1.27-alpine                          # example pinned tag
    restart: unless-stopped                           # survive reboots
    ports: ["80:80", "443:443"]                       # public ports
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d:ro           # site configs
      - certbot-etc:/etc/letsencrypt:ro               # certs, read-only
      - certbot-www:/var/www/certbot:ro               # ACME challenge files
    networks: [edge, backend]                         # reach the backends
    depends_on: [api, ml]
  certbot:
    image: certbot/certbot:latest                     # pin in production
    restart: unless-stopped
    volumes:
      - certbot-etc:/etc/letsencrypt                  # writes certs
      - certbot-www:/var/www/certbot                  # writes challenge tokens
      - /var/run/docker.sock:/var/run/docker.sock     # ONLY if you use a deploy hook; see Security
    entrypoint: >
      /bin/sh -c 'trap exit TERM; while :; do
      certbot renew --webroot -w /var/www/certbot --quiet;
      sleep 12h & wait $${!}; done'
    networks: [edge]
  api:
    build: ./api                                      # Node.js :3000
    restart: unless-stopped
    networks: [backend]
  ml:
    build: ./fastapi                                  # FastAPI :8000
    restart: unless-stopped
    networks: [backend]
networks:
  edge: {}
  backend: {}
volumes:
  certbot-etc: {}
  certbot-www: {}
```

```nginx
# nginx/conf.d/default.conf  (Phase 2: final HTTPS config)
server {
    listen 80;                                                  # HTTP
    server_name app.example.com;
    location /.well-known/acme-challenge/ { root /var/www/certbot; }   # keep ACME open
    location / { return 301 https://$host$request_uri; }        # redirect rest
}
server {
    listen 443 ssl;                                             # HTTPS
    http2 on;                                                   # nginx >= 1.25.1
    server_name app.example.com;
    ssl_certificate     /etc/letsencrypt/live/app.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/app.example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    add_header Strict-Transport-Security "max-age=31536000" always;
    location /api/ { proxy_pass http://api:3000; proxy_set_header Host $host;
                     proxy_set_header X-Forwarded-Proto https;
                     proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; }
    location /ml/  { proxy_pass http://ml:8000/; proxy_set_header Host $host;
                     proxy_set_header X-Forwarded-Proto https; }
    location /     { root /usr/share/nginx/html; try_files $uri /index.html; }
}
```

```bash
# /etc/cron.d/nginx-reload -- reload nginx weekly so renewed certs load
# (simple alternative to a docker.sock deploy hook; reload is cheap and graceful)
0 4 * * 1 root cd /opt/app && docker compose exec -T nginx nginx -s reload
```

Verification done: YAML parsed; `bash -n` on scripts. NOT run against Let's Encrypt (needs a real public domain). The bind-mount of `docker.sock` into certbot is shown for hooks but is risky; the cron reload above avoids it, so prefer cron and delete that volume line.

---

## 🟠 My Stack Integration
- Replace `app.example.com` with your Hostinger-pointed domain; the React build in `./web/dist` can be mounted at `/usr/share/nginx/html`.
- GitHub Actions deploy job: SSH into VPS, `git pull`, `docker compose up -d --build`, then `docker compose exec -T nginx nginx -t && ... nginx -s reload` (see 411).
- On first deploy run `./init-letsencrypt.sh` manually (or from a one-off workflow_dispatch job).

```yaml
# GitHub Actions snippet: manual bootstrap workflow
on:
  workflow_dispatch:                                  # run by hand from the Actions tab
    inputs:
      staging: { description: "Use staging CA (1/0)", default: "1" }
jobs:
  bootstrap:
    runs-on: ubuntu-latest
    steps:
      - name: Run init script on VPS
        run: ssh deploy@${{ secrets.VPS_HOST }} "cd /opt/app && STAGING=${{ inputs.staging }} ./init-letsencrypt.sh"
```
(SSH key setup omitted here, see 405; example only.)

Security: `certbot-etc` contains private keys, mount `:ro` for Nginx; do not expose Docker socket unless essential; firewall allows only 22/80/443; keep an email for expiry alerts; never log the keys.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Putting the final HTTPS config in place before the cert exists, so Nginx crash-loops.
✅ Correct: Bootstrap with HTTP-only config first.

❌ Mistake 2: DNS not yet propagated, causing "Timeout during connect" / 404 on challenge.
✅ Correct: `dig +short app.example.com` must show the VPS IP before running certbot.

❌ Mistake 3: Using the real CA while debugging and hitting the rate limit (you are blocked for days).
✅ Correct: `STAGING=1` until success, then rerun with `STAGING=0 --force-renewal`.

❌ Mistake 4: Cloudflare proxy or a firewall blocks port 80.
✅ Correct: Allow 80 (or use DNS-01 challenge).

---

## 🧠 Tricky Interview Question
Why does `docker compose up` fail on a fresh server with "cannot load certificate /etc/letsencrypt/live/..."? How do you break the cycle without self-signed hacks?

Answer: Nginx validates all referenced certificate files at startup. On a fresh server they do not exist yet, so Nginx exits. Break the cycle in phases: start with an HTTP-only config that serves the ACME path, obtain the cert via webroot, then switch to the HTTPS config and reload. The alternative is creating a temporary self-signed cert at the expected path, starting Nginx, then replacing it (what many bootstrap scripts do).

---

## ⚫ Interview Questions + Answers

Q1: Why mount certs `:ro` in Nginx?
A1: Nginx only needs to read; if it is compromised it cannot alter keys or certificates.

Q2: Where does Certbot store the files?
A2: `/etc/letsencrypt/live/<domain>/` has symlinks to `archive/<domain>/` versions; also `renewal/` configs and account keys.

Q3: How do you check the expiry date?
A3: `echo | openssl s_client -connect app.example.com:443 -servername app.example.com 2>/dev/null | openssl x509 -noout -dates`.

Q4: What if the domain changes?
A4: Run certbot again with new `-d` or `--expand`, update `server_name` and cert paths, reload.

Q5: How do you monitor renewal failures?
A5: Certbot emails the registered address; also monitor expiry with Prometheus blackbox exporter or an uptime check.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Single VPS, public domain, Docker Compose.
- You want free renewing HTTPS with no cloud dependency.

❌ Avoid when:
- Many servers need the same cert (use DNS-01 centrally, cert-manager on Kubernetes or ACM).
- Behind a CDN that already handles TLS to the origin with its own certs.

---

## 📊 Visual Diagram
```
 PHASE 1                     PHASE 2                       RUNNING
 -------                     -------                       -------
 nginx (HTTP only)           nginx (80+443)                nginx :443
   |  /.well-known             ^   reads certs               ^ reload
   v                           |                              | (cron weekly)
 certbot --webroot ---> [certbot-etc volume] <--- certbot renew loop (12h)
   |                           |
   +--- Let's Encrypt validates over :80 ---+
 api:3000  ml:8000  (private "backend" network)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Bootstrap | First-time setup sequence | पहली बार का setup |
| Webroot plugin | Certbot writes tokens to a folder | folder वाला plugin |
| `--force-renewal` | Renew even if not due | ज़बरदस्ती renew |
| `live/` symlinks | Always point to latest cert | नवीनतम cert के links |
| Deploy hook | Command run after renewal | renewal के बाद का command |
| Propagation | DNS change spreading | DNS बदलाव फैलना |

---

## ⚡ 3-Line Summary
English: Bootstrap Nginx on HTTP, get the cert with Certbot, then switch to HTTPS.
A renewal loop plus a reload keeps certificates fresh.
Test on staging, protect the key volume, verify DNS first.
Hindi: पहले Nginx HTTP पर चलाओ, Certbot से cert लो, फिर HTTPS पर switch करो।
Renewal loop और reload certificates को ताज़ा रखते हैं।
Staging पर test करो, key volume सुरक्षित रखो, पहले DNS जाँचो।

---

## ➡️ Next Topic
408. Nginx + Node.js in Docker Compose - the full app stack around this HTTPS front door.
