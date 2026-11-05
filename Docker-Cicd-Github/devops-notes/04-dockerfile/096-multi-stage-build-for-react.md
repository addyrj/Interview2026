# 96. Multi-Stage Build for React
# हिंदी में: React के लिए Multi-Stage Build

---

## 🔵 Simple Definition (English)
A React app compiles into static HTML, JS and CSS. A multi-stage build uses a Node stage to run `npm run build`, then copies only the build output (`dist/` for Vite, `build/` for CRA) into a tiny Nginx image that serves the files. Node is not needed at runtime.

## 🔵 सरल परिभाषा (Hindi)
React app compile होकर static HTML, JS और CSS बन जाता है। Multi-stage build में Node stage `npm run build` चलाता है, फिर सिर्फ build output (Vite में `dist/`, CRA में `build/`) एक छोटी Nginx image में copy होता है जो files serve करती है। Runtime पर Node की ज़रूरत नहीं होती।

---

## 🔴 Problem it Solves
Running `npm start` or `vite dev` in production ships a 1 GB image with a dev server that is slow, insecure and not meant for traffic. Even `serve` under Node wastes memory. Nginx serves static files with gzip, caching headers and SPA fallback using about 10 MB RAM.

## 🔴 यह क्यों बना? (Hindi)
Production में `npm start` या `vite dev` चलाने से 1 GB की image बनती है जिसमें dev server होता है जो slow, insecure और traffic के लिए नहीं बना है। `serve` को Node पर चलाना भी memory बर्बाद करता है। Nginx static files को gzip, caching headers और SPA fallback के साथ सिर्फ ~10 MB RAM में serve करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Stage "build": node:20-alpine, npm ci
Step 2 → Pass API URL at BUILD time (VITE_API_URL) - it is baked in JS
Step 3 → npm run build -> /app/dist
Step 4 → Stage "serve": nginx:alpine
Step 5 → COPY --from=build /app/dist /usr/share/nginx/html
Step 6 → nginx.conf: try_files for SPA routes, cache hashed assets
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Stage "build": node:20-alpine, npm ci
Step 2 → API URL BUILD time पर दो (VITE_API_URL) - यह JS में bake होता है
Step 3 → npm run build -> /app/dist
Step 4 → Stage "serve": nginx:alpine
Step 5 → COPY --from=build /app/dist /usr/share/nginx/html
Step 6 → nginx.conf: SPA routes के लिए try_files, hashed assets cache
```

---

## 🟡 Real World Example
A SaaS dashboard (React + Vite) is deployed on a VPS. The image is 45 MB. Pushing a fix to GitHub triggers Actions, which builds the image, pushes to GHCR, and the VPS pulls it. Users hitting `/orders/123` directly get `index.html` thanks to `try_files`, so React Router works on refresh instead of showing a 404.

## 🟡 Real Example Hindi mein
एक SaaS dashboard (React + Vite) VPS पर deploy है। Image 45 MB की है। GitHub पर fix push करने से Actions image build करता है, GHCR पर push करता है, और VPS उसे pull करता है। `/orders/123` सीधे खोलने पर `try_files` की वजह से `index.html` मिलता है, इसलिए refresh पर React Router काम करता है, 404 नहीं आता।

---

## 💻 Code / Config Example — Basic

```dockerfile
# Dockerfile - basic React (Vite) to Nginx
# Stage 1: build the static files
FROM node:20-alpine AS build
# Work dir
WORKDIR /app
# Manifests first (cache)
COPY package.json package-lock.json ./
# Install all deps (build needs devDependencies)
RUN npm ci
# Copy source
COPY . .
# Build output goes to /app/dist (CRA uses /app/build)
RUN npm run build

# Stage 2: serve with Nginx
FROM nginx:1.27-alpine
# Copy only the static output
COPY --from=build /app/dist /usr/share/nginx/html
# Nginx listens on 80
EXPOSE 80
# Official image already has the right CMD; shown for clarity
CMD ["nginx", "-g", "daemon off;"]
```

## 💻 Code / Config Example — Advanced

```dockerfile
# syntax=docker/dockerfile:1
# Advanced React image: build args, SPA config, non-root nginx
# ---- build ----
FROM node:20-alpine AS build
# Work dir
WORKDIR /app
# Public API URL is compiled into the bundle, pass at build time
ARG VITE_API_URL=https://api.example.com
# Vite reads variables prefixed with VITE_ from the environment
ENV VITE_API_URL=$VITE_API_URL
# Manifests
COPY package.json package-lock.json ./
# Cache mount keeps npm cache out of layers
RUN --mount=type=cache,target=/root/.npm npm ci
# Source
COPY . .
# Production build
RUN npm run build

# ---- serve (nginx-unprivileged runs as uid 101, listens on 8080) ----
FROM nginxinc/nginx-unprivileged:1.27-alpine AS serve
# Custom server config for SPA routing and caching
COPY nginx.conf /etc/nginx/conf.d/default.conf
# Static files from the build stage
COPY --from=build /app/dist /usr/share/nginx/html
# Unprivileged image uses 8080 (non-root cannot bind port 80)
EXPOSE 8080
# Simple health probe
HEALTHCHECK --interval=30s --timeout=3s CMD wget -qO- http://127.0.0.1:8080/ || exit 1
```

```nginx
# nginx.conf (goes to /etc/nginx/conf.d/default.conf) - not tested with nginx -t here
server {
    listen 8080;                              # unprivileged port
    server_name _;                            # match any host
    root /usr/share/nginx/html;               # build output
    index index.html;                         # default file

    gzip on;                                  # compress text assets
    gzip_types text/css application/javascript application/json image/svg+xml;  # types

    # hashed asset files can be cached for a year
    location /assets/ {
        add_header Cache-Control "public, max-age=31536000, immutable";  # long cache
        try_files $uri =404;                  # real 404 for missing assets
    }

    # SPA fallback: unknown paths return index.html
    location / {
        add_header Cache-Control "no-cache";  # always revalidate index.html
        try_files $uri $uri/ /index.html;     # React Router support
    }

    # security headers (NOTE: nginx drops server-level add_header in a location that defines its own
    # add_header, so repeat these inside each location, or use an include file)
    add_header X-Content-Type-Options "nosniff" always;  # block MIME sniffing
    add_header X-Frame-Options "SAMEORIGIN" always;      # clickjacking protection
}
```

---

## 🟠 My Stack Integration
**React**: this image. **Node/FastAPI**: React calls `/api/...`; instead of hardcoding the API URL, proxy `/api/` to the backend in Nginx so the same image works in dev, staging and prod. **VPS**: host Nginx terminates TLS (Let's Encrypt) and proxies to the container on 8080. **AWS**: alternatively upload `dist/` to S3 + CloudFront; the Docker route suits VPS/ECS.

```yaml
# docker-compose.yml - web + api on one VPS
services:
  web:
    image: ghcr.io/myorg/web:1.2.0        # built by GitHub Actions (example name)
    restart: unless-stopped               # restart policy
    read_only: true                       # immutable root filesystem
    tmpfs:
      - /tmp                              # nginx temp files
    ports:
      - "127.0.0.1:8080:8080"             # host Nginx -> this container
  api:
    image: ghcr.io/myorg/api:1.2.0        # backend image
    restart: unless-stopped               # restart policy
    env_file: .env                        # secrets stay on the server
    expose:
      - "3000"                            # internal port only
```

Security: never put secrets in `VITE_*` variables; they are public inside the JS bundle. Add a Content-Security-Policy header for production.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Expecting runtime `-e API_URL=...` to change a Vite/CRA app.
✅ Correct: Variables are baked at build. Use `ARG` at build, or load `/config.js` generated at container start, or proxy `/api` in Nginx.

❌ Mistake 2: No `try_files ... /index.html` so refreshing `/dashboard` gives 404.
✅ Correct: Add the SPA fallback.

❌ Mistake 3: Copying `build/` when Vite outputs `dist/` (or the reverse).
✅ Correct: Check your tool's output folder.

---

## 🧠 Tricky Interview Question
Your React image is rebuilt and deployed but users still see the old UI. Server and image are correct. Why?

Answer: `index.html` was cached by the browser or CDN (for example with long `Cache-Control`). Hashed JS/CSS files can be cached forever, but `index.html` must be `no-cache` so it points to new hashed bundles. Set caching per location as above and invalidate the CDN.

---

## ⚫ Interview Questions + Answers

Q1: Why not run Node in production for React?
A1: The app is static; Nginx is faster, smaller and has fewer vulnerabilities.

Q2: How do you handle different API URLs per environment?
A2: Build-time args per environment, an Nginx `/api` proxy, or a runtime `config.js` injected by an entrypoint script (envsubst).

Q3: Why use nginx-unprivileged?
A3: It runs as non-root and listens on 8080, which fits read-only/hardened clusters.

Q4: What is the final image size?
A4: Around 25-50 MB depending on assets.

Q5: How to cache npm in CI?
A5: BuildKit cache mounts plus GitHub Actions cache (`type=gha`).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Single-page apps deployed on VPS, ECS or Kubernetes.
- You want identical images across environments.

❌ Avoid when:
- You need server-side rendering (Next.js): that needs a Node runtime stage instead.
- You already deploy to S3 + CloudFront; Docker adds nothing.

---

## 📊 Visual Diagram
```
 +---- build (node:20-alpine) ----+       +---- serve (nginx) ------------+
 | npm ci -> npm run build        |       | /usr/share/nginx/html         |
 | src/*.jsx  -->  dist/          | ----> |   index.html, assets/*.js     |
 +--------------------------------+ COPY  | try_files -> /index.html      |
   (~1 GB, thrown away)                   +-------------------------------+
                                                 |
          Browser -> host Nginx (TLS) -> :8080 --+ (~40 MB image)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| SPA | Single page app, one HTML shell | एक HTML वाला app |
| try_files | Nginx fallback rule | Nginx का fallback नियम |
| Build-time variable | Value baked while building | build के समय बैठा value |
| Hashed asset | File name with content hash | content hash वाली file |
| nginx-unprivileged | Non-root Nginx image | non-root Nginx image |

---

## ⚡ 3-Line Summary
English: Build React with Node, serve the static output with Nginx.
Env vars are baked at build time, and SPA needs try_files.
Cache hashed assets long, but never cache index.html.
Hindi: React को Node से build करो और static output Nginx से serve करो।
Env vars build के समय bake होते हैं, और SPA को try_files चाहिए।
Hashed assets को लंबा cache करो, पर index.html को कभी नहीं।

---

## ➡️ Next Topic
**97. Distroless Images**: even smaller and safer runtime images with no shell.
