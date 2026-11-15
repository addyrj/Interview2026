# 410. Nginx + React in Docker
# हिंदी में: Docker में Nginx + React

---

## 🔵 Simple Definition (English)
A React app is compiled into static files (HTML, JS, CSS). The standard Docker pattern is a **multi-stage build**: Node builds the files, then a tiny **Nginx** image serves them. The final image contains no Node, no source and no `node_modules`, only the build output and an Nginx config with SPA fallback.

## 🔵 सरल परिभाषा (Hindi)
React app compile होकर static files (HTML, JS, CSS) बन जाता है। Standard Docker pattern **multi-stage build** है: Node files बनाता है, फिर छोटी **Nginx** image उन्हें serve करती है। Final image में Node, source और `node_modules` नहीं होते, सिर्फ build output और SPA fallback वाली Nginx config।

---

## 🔴 Problem it Solves
- Running `npm start` (dev server) in production is slow, insecure and huge.
- Shipping Node + node_modules to serve static files makes 1 GB images with a big attack surface.
- React Router paths like `/orders/42` give 404 on refresh unless the server returns `index.html`.
- Poor caching causes users to see old JS after a deploy, or never cache at all.

## 🔴 यह क्यों बना? (Hindi)
- Production में `npm start` (dev server) धीमा, असुरक्षित और भारी है।
- Static files के लिए Node + node_modules भेजना 1 GB images और बड़ा attack surface बनाता है।
- React Router के paths (`/orders/42`) refresh पर 404 देते हैं जब तक server `index.html` न लौटाए।
- खराब caching से deploy के बाद users को पुराना JS दिखता है, या कुछ cache ही नहीं होता।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Stage "build": node image, npm ci, npm run build -> /app/dist (or /build)
Step 2 → Stage "serve": nginx:alpine, copy only the build output
Step 3 → nginx config: try_files $uri /index.html (SPA fallback)
Step 4 → Hashed files (assets/app.3f9a1.js) -> cache 1 year, immutable
Step 5 → index.html -> no-cache so new deploys are picked up
Step 6 → API calls go to /api/ (same origin) -> proxied to Node (no CORS)
Step 7 → Runtime config: env vars injected at container start, not build
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Stage "build": node image, npm ci, npm run build -> /app/dist (या /build)
Step 2 → Stage "serve": nginx:alpine, सिर्फ build output copy करो
Step 3 → nginx config: try_files $uri /index.html (SPA fallback)
Step 4 → Hashed files (assets/app.3f9a1.js) -> 1 साल cache, immutable
Step 5 → index.html -> no-cache ताकि नया deploy तुरंत दिखे
Step 6 → API calls /api/ (same origin) -> Node को proxy (CORS नहीं)
Step 7 → Runtime config: env vars container start पर inject, build पर नहीं
```

---

## 🟡 Real World Example
A SaaS dashboard (Vite + React) used to run `npm run dev` on the VPS and crashed under 50 users. After the multi-stage Nginx build the image dropped from 1.2 GB to about 45 MB, pages load from gzip-compressed cached assets, and a release is just a new image tag. Refreshing `/billing/invoices` works because of `try_files`.

## 🟡 Real Example Hindi mein
एक SaaS dashboard (Vite + React) VPS पर `npm run dev` चलाता था और 50 users में crash होता था। Multi-stage Nginx build के बाद image 1.2 GB से लगभग 45 MB हो गई, pages gzip और cached assets से तेज़ खुलते हैं, और release सिर्फ नया image tag है। `/billing/invoices` पर refresh `try_files` की वजह से चलता है।

---

## 💻 Code / Config Example — Basic

```dockerfile
# web/Dockerfile -- basic multi-stage for a Vite React app (output dir: dist)
FROM node:20-alpine AS build
# stage 1: build tools
WORKDIR /app
# work folder
COPY package*.json ./
# manifests first for caching
RUN npm ci
# install all deps (dev deps needed to build)
COPY . .
# copy source
RUN npm run build
# creates /app/dist (CRA outputs /app/build instead; adjust the COPY below)
FROM nginx:1.27-alpine
# stage 2: tiny web server
COPY --from=build /app/dist /usr/share/nginx/html
# copy only static output
COPY nginx.conf /etc/nginx/conf.d/default.conf
# replace default site config
EXPOSE 80
# documented port
```

```nginx
# web/nginx.conf -- basic SPA config
server {
    listen 80;                                  # HTTP inside container
    root /usr/share/nginx/html;                 # static files
    index index.html;                           # entry file
    location / {
        try_files $uri $uri/ /index.html;       # SPA fallback for client-side routes
    }
}
```

## 💻 Code / Config Example — Advanced

```nginx
# web/nginx.conf -- production SPA + API proxy + caching + headers
server {
    listen 8080;                                          # >1024 so a non-root nginx can bind
    server_name _;
    server_tokens off;                                    # hide version
    root /usr/share/nginx/html;
    index index.html;

    gzip on;                                              # compress text assets
    gzip_vary on;                                         # correct caching with compression
    gzip_types text/css application/javascript application/json image/svg+xml;

    add_header X-Content-Type-Options nosniff always;     # no MIME sniffing
    add_header X-Frame-Options DENY always;               # no framing
    add_header Referrer-Policy strict-origin-when-cross-origin always;
    # CSP must be tuned per app; this is a strict starting point (example):
    add_header Content-Security-Policy "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; connect-src 'self'" always;

    location /assets/ {                                   # Vite hashed files
        expires 1y;                                       # browser cache one year
        add_header Cache-Control "public, immutable" always;  # never revalidate
        try_files $uri =404;                              # missing asset = real 404, not index.html
    }

    location = /index.html {
        add_header Cache-Control "no-cache" always;       # always revalidate the entry file
    }

    location /api/ {
        proxy_pass http://api:3000;                       # Node.js container, same origin
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        try_files $uri /index.html;                       # SPA routing
        add_header Cache-Control "no-cache" always;
    }
}
```

```dockerfile
# web/Dockerfile -- production: pinned, non-root, build args for public config
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci --no-audit --no-fund
# faster, quiet install
COPY . .
ARG VITE_API_URL=/api
# PUBLIC build-time value only (anything VITE_* is visible to every user)
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build
# outputs dist/

FROM nginxinc/nginx-unprivileged:1.27-alpine
# nginx that runs as non-root user (listens on 8080)
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s CMD wget -qO- http://127.0.0.1:8080/ >/dev/null || exit 1
# alpine has busybox wget
```

```yaml
# docker-compose.yml -- web + api
services:
  web:
    build: ./web                              # builds the Dockerfile above
    restart: unless-stopped
    ports: ["80:8080"]                        # host 80 -> container 8080 (unprivileged)
    depends_on: [api]
    read_only: true                           # immutable root FS
    tmpfs: ["/tmp", "/var/cache/nginx"]       # writable temp for nginx
    cap_drop: [ALL]
    security_opt: ["no-new-privileges:true"]
  api:
    build: ./api
    restart: unless-stopped
```

Verified: YAML parse, Dockerfile instruction/stage check. Not built or run. `read_only` with the unprivileged image also needs the pid file in a writable path (the image's default uses `/tmp/nginx.pid`); test with `docker compose up` before depending on it. CRA outputs `build/`, Vite `dist/` - adjust. An external TLS front (topic 407) can sit before this container, or merge web into the edge Nginx.

---

## 🟠 My Stack Integration
- Browser -> edge Nginx (TLS) -> `web` container for `/`, `api` for `/api`, `ml` for `/ml`.
- Or simpler: one Nginx image contains React files and also proxies `/api/` (the advanced config above).
- GitHub Actions: `npm ci`, `npm test`, `docker build`, push; or build static files in CI and `rsync` to the VPS.
- Environment-specific API URLs: use relative `/api` so the same image works in staging and prod.

```yaml
# Edge nginx forwarding "/" to the web container
    location / {
        proxy_pass http://web:8080;               # React container
        proxy_set_header Host $host;
    }
```

Security: never put secrets in `VITE_*`/`REACT_APP_*` variables (they are bundled into public JS); add CSP, `nosniff`, frame protections; run unprivileged; scan the image; keep source maps off or private in production.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: No `try_files ... /index.html`, so refreshing `/dashboard` gives 404.
✅ Correct: Add the SPA fallback.

❌ Mistake 2: Caching `index.html` for a year, so users never see new releases.
✅ Correct: `no-cache` for index, immutable only for hashed assets.

❌ Mistake 3: Putting API keys in env vars used by the React build.
✅ Correct: Keep secrets on the backend; the frontend only has public config.

❌ Mistake 4: SPA fallback also returning `index.html` for missing JS files, giving "Unexpected token <".
✅ Correct: `try_files $uri =404` under `/assets/`.

---

## 🧠 Tricky Interview Question
After deployment some users see a white screen with "Loading chunk 123 failed" while others are fine. Why?

Answer: Old tabs still run the old `index.html` which requests hashed chunks (`123.abc.js`) that no longer exist after the new deploy replaced the files, and the SPA fallback may return `index.html` instead, causing a parse error. Fixes: keep previous assets for some time (do not delete old files immediately), return real 404s for `/assets/`, never cache `index.html`, and make the app reload on chunk-load errors.

---

## ⚫ Interview Questions + Answers

Q1: Why multi-stage?
A1: The build stage needs Node and dev dependencies; the runtime needs only static files. Multi-stage drops hundreds of MB and reduces vulnerabilities.

Q2: How to inject runtime config?
A2: Build-time variables are baked in. For runtime use a small `config.js` generated at container start (envsubst in `/docker-entrypoint.d/`) and loaded by `index.html`, or use relative URLs.

Q3: Why `immutable` caching is safe?
A3: Filenames include a content hash, so a changed file gets a new name; the old URL never changes content.

Q4: CORS here?
A4: Same-origin `/api` proxy avoids CORS entirely; otherwise configure allowed origins on the API.

Q5: nginx or `serve`/node for static files?
A5: Nginx; faster, mature caching, compression, and smaller image.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Single-page apps built to static files (Vite, CRA).
- You want a small immutable frontend image.

❌ Avoid when:
- Using Next.js SSR (needs a Node runtime) - then Nginx proxies to the Next server instead.
- Static hosting on S3 + CloudFront is cheaper and sufficient.

---

## 📊 Visual Diagram
```
 Dockerfile
 +------------------+       +------------------------------+
 | Stage 1: build   |       | Stage 2: nginx (unprivileged)|
 | node:20-alpine   | COPY  | /usr/share/nginx/html        |
 | npm ci           |------>|  index.html (no-cache)       |
 | npm run build    | dist  |  assets/*.js (immutable 1y)  |
 +------------------+       | /api/ -> proxy api:3000      |
   (thrown away)            +------------------------------+
 Browser: /orders/42 -> try_files -> index.html -> React Router renders
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| SPA | Single-page application | single-page app |
| Multi-stage build | Build then copy results to small image | कई stage वाला build |
| `try_files` | Serve file or fallback | file या fallback |
| Content hash | Hash in file name for cache busting | file नाम में hash |
| Immutable | Never changes, never revalidate | कभी न बदलने वाला |
| CSP | Browser rule on allowed sources | allowed sources का नियम |

---

## ⚡ 3-Line Summary
English: Build React with Node in stage one, serve the static output with Nginx in stage two.
Use SPA fallback, long cache for hashed assets and no-cache for index.html.
Keep secrets out of the bundle.
Hindi: Stage एक में Node से React build करो, stage दो में Nginx से static output serve करो।
SPA fallback, hashed assets पर लंबा cache और index.html पर no-cache रखो।
Bundle में secrets मत रखो।

---

## ➡️ Next Topic
411. Deploy Nginx Config via CI/CD - ship these configs to the server automatically and safely.
