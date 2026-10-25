# 247. Docker Multi-Stage Build
# हिंदी में: Docker Multi-Stage Build

---

## 🔵 Simple Definition (English)
A multi-stage Docker build uses multiple `FROM` statements in one Dockerfile to separate the "build" environment (compiling TypeScript, installing dev dependencies, running build tools) from the final "runtime" image — only the compiled output and production dependencies are copied into the final, much smaller image.

## 🔵 सरल परिभाषा (Hindi)
Multi-stage Docker build एक Dockerfile में कई `FROM` statements use करता है "build" environment (TypeScript compile करना, dev dependencies install करना, build tools चलाना) को final "runtime" image से अलग करने के लिए — सिर्फ compiled output और production dependencies को final, बहुत smaller image में copy किया जाता है।

---

## 🔴 Problem it Solves
A naive Dockerfile that builds a TypeScript/compiled app in a single stage ends up with a FINAL image that includes build tools, dev dependencies (TypeScript compiler, test frameworks, linters), and source files that are no longer needed at runtime — bloating the image size (slower to pull/deploy) and increasing the attack surface (more installed tools = more potential vulnerabilities). Multi-stage builds solve this by using a throwaway "builder" stage for compilation, then copying ONLY the final artifacts into a clean, minimal runtime image, discarding everything else.

## 🔴 यह क्यों बना? (Hindi)
एक naive Dockerfile जो TypeScript/compiled app को single stage में build करता है, उसकी FINAL image में build tools, dev dependencies (TypeScript compiler, test frameworks, linters), और source files शामिल होते हैं जो runtime पर अब जरूरी नहीं — image size bloat होता है (pull/deploy slower) और attack surface बढ़ता है (ज्यादा installed tools = ज्यादा potential vulnerabilities)। Multi-stage builds compilation के लिए एक throwaway "builder" stage use करके, फिर सिर्फ final artifacts को एक clean, minimal runtime image में copy करके, बाकी सब discard करके यह solve करते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → Define a first stage (e.g., named `builder`) using a full Node.js image, installing ALL dependencies (including dev dependencies) needed for building.
Step 2 → Run build commands in this stage: `npm run build` (e.g., TypeScript compilation), producing compiled output (e.g., a `dist/` folder).
Step 3 → Define a second, final stage using a minimal base image (e.g., `node:20-alpine`).
Step 4 → Use `COPY --from=builder` to copy ONLY the needed artifacts (compiled `dist/` folder, `package.json`) from the builder stage into the final stage — none of the build tools or dev dependencies come along.
Step 5 → Install ONLY production dependencies in the final stage (`npm ci --production`).
Step 6 → The final image contains just what's needed to RUN the app — much smaller and more secure than if everything from the build process were included.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → एक पहला stage define करो (जैसे `builder` नाम से) एक full Node.js image use करते हुए, building के लिए जरूरी ALL dependencies (dev dependencies भी) install करते हुए।
Step 2 → इस stage में build commands run करो: `npm run build` (जैसे TypeScript compilation), compiled output produce करते हुए (जैसे एक `dist/` folder)।
Step 3 → एक दूसरा, final stage define करो एक minimal base image use करते हुए (जैसे `node:20-alpine`)।
Step 4 → `COPY --from=builder` use करो builder stage से सिर्फ जरूरी artifacts (compiled `dist/` folder, `package.json`) को final stage में copy करने के लिए — कोई build tools या dev dependencies साथ नहीं आते।
Step 5 → Final stage में सिर्फ production dependencies install करो (`npm ci --production`)।
Step 6 → Final image में सिर्फ वो होता है जो app RUN करने के लिए जरूरी है — बहुत छोटी और ज्यादा secure, अगर build process की हर चीज़ शामिल होती उससे।

---

## 🟡 Real World Example
**Razorpay's TypeScript-based payment service:** Their service is written in TypeScript and needs compiling before it can run. With a naive single-stage Dockerfile, the final production image would be ~1.2GB, including the TypeScript compiler, `ts-node`, test runners, and raw `.ts` source files. Using a multi-stage build, the builder stage compiles everything, but the final image only contains the compiled `.js` files and production `node_modules` — shrinking the image to ~150MB, which pulls and deploys dramatically faster across hundreds of Kubernetes pods during a deployment, and reduces the attack surface since compilers/dev tools aren't present in the production container at all.

## 🟡 Real Example Hindi mein
**Razorpay की TypeScript-based payment service:** उनकी service TypeScript में लिखी है और चलने से पहले compile होनी चाहिए। एक naive single-stage Dockerfile के साथ, final production image ~1.2GB की होगी, जिसमें TypeScript compiler, `ts-node`, test runners, और raw `.ts` source files शामिल होंगे। Multi-stage build use करके, builder stage सब कुछ compile करता है, लेकिन final image में सिर्फ compiled `.js` files और production `node_modules` होते हैं — image को ~150MB तक shrink करता है, जो hundreds of Kubernetes pods पर deployment के दौरान dramatically faster pull और deploy होती है, और attack surface कम करता है क्योंकि compilers/dev tools production container में बिल्कुल present नहीं होते।

---

## 💻 Code Example — Basic

```dockerfile
# Dockerfile — basic multi-stage build for a plain JavaScript Node.js app
# Even without TypeScript, multi-stage helps separate install-time vs run-time concerns

# ─── STAGE 1: builder — installs ALL dependencies (including dev) ───────────
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install                  # installs dev + production dependencies for building/testing
COPY . .
RUN npm run build                 # e.g., runs a bundler/linter/test step, produces /app/dist

# ─── STAGE 2: runtime — minimal final image ──────────────────────────────────
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --production           # ONLY production dependencies in the final image

# Copy ONLY the built output from the builder stage — not source files, not dev tools
COPY --from=builder /app/dist ./dist

CMD ["node", "dist/server.js"]
```

## 💻 Code Example — Advanced

```dockerfile
# Dockerfile — TypeScript app with multi-stage build, non-root user, and smaller final image
# Build:  docker build -t payment-service .
# Run:    docker run -p 3000:3000 payment-service

# ─── STAGE 1: dependencies — cached separately for faster rebuilds ──────────
FROM node:20-alpine AS dependencies
WORKDIR /app
COPY package*.json ./
RUN npm ci   # full install (including devDependencies) needed for the TypeScript build step

# ─── STAGE 2: build — compiles TypeScript using dependencies from stage 1 ────
FROM node:20-alpine AS build
WORKDIR /app
COPY --from=dependencies /app/node_modules ./node_modules
COPY . .
RUN npm run build          # tsc compiles src/*.ts → dist/*.js
RUN npm prune --production  # removes devDependencies from node_modules IN THIS STAGE

# ─── STAGE 3: runtime — final, minimal, secure image ─────────────────────────
FROM node:20-alpine AS runtime
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
WORKDIR /app

# Only copy the PRODUCTION node_modules (already pruned) and compiled dist/ folder
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/dist ./dist
COPY package*.json ./

USER appuser
EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s CMD node -e "require('http').get('http://localhost:3000/health', r => process.exit(r.statusCode===200?0:1))"

CMD ["node", "dist/server.js"]

# Result: final image has NO TypeScript compiler, NO dev dependencies, NO raw .ts source —
# just compiled JS and production node_modules, running as a non-root user.
```

---

## 🟠 Express.js Integration

```typescript
// src/server.ts — the TypeScript Express app that gets compiled by the "build" stage
import express from 'express';

const app = express();

app.get('/health', (req, res) => res.sendStatus(200));
app.get('/api/payments', (req, res) => res.json({ payments: [] }));

const PORT = process.env.PORT || 3000;
const server = app.listen(PORT, () => console.log(`Payment service running on port ${PORT}`));

process.on('SIGTERM', () => server.close(() => process.exit(0)));

// `npm run build` (tsc) compiles this into dist/server.js, which is what the
// final Docker stage actually runs — src/server.ts itself never ships to production.
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting to copy `package.json` into the final stage, breaking `node` module resolution or scripts
✅ Correct: Copy `package*.json` into the final stage even if you only need `node_modules` + `dist`

```dockerfile
# Wrong — final stage has no package.json, some tooling/metadata-dependent code may break
FROM node:20-alpine
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/dist ./dist
CMD ["node", "dist/server.js"]

# Right
FROM node:20-alpine
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/dist ./dist
COPY package*.json ./
CMD ["node", "dist/server.js"]
```

❌ Mistake 2: Running `npm install` (with dev dependencies) in the FINAL stage instead of pruning/installing production-only
✅ Correct: Either `npm ci --production` in the final stage, or `npm prune --production` after building in an earlier stage

```dockerfile
# Wrong — final image still has devDependencies (TypeScript, test frameworks, etc.)
FROM node:20-alpine
COPY package*.json ./
RUN npm install   # installs EVERYTHING, including dev deps, into the final image

# Right
FROM node:20-alpine
COPY package*.json ./
RUN npm ci --production   # production deps only
```

---

## 🧠 Tricky Interview Question

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY . .
RUN npm install && npm run build

FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app .
CMD ["node", "dist/server.js"]
# What's wrong with this multi-stage Dockerfile, even though it technically "works"?
```
Answer: The final `COPY --from=builder /app .` copies the ENTIRE builder stage's `/app` directory — including `node_modules` with devDependencies, raw TypeScript source files, test files, and any build tool caches — completely defeating the purpose of a multi-stage build. The final image ends up just as bloated as a single-stage build would be. The fix is to copy ONLY the specific artifacts needed (`COPY --from=builder /app/dist ./dist` and a separately, properly pruned/installed `node_modules`), not the entire builder directory wholesale.

---

## ⚫ Interview Questions + Answers

Q1: What is the main benefit of a multi-stage Docker build?
A1: It separates the build-time environment (which needs compilers, dev dependencies, build tools, source files) from the runtime environment (which only needs compiled output and production dependencies). This produces a much smaller, more secure final image — faster to pull/deploy, with a reduced attack surface since build tools and source code aren't present in what actually runs in production.

Q2: How does `COPY --from=<stage>` work, and why is it central to multi-stage builds?
A2: `COPY --from=<stage-name-or-index>` copies files from a PREVIOUS build stage (identified by name via `AS <name>` or by its 0-based index) into the current stage, rather than from the host machine's build context. This is what allows a later, minimal stage to selectively pull in just the compiled output or specific artifacts from an earlier, heavier "builder" stage — without inheriting everything else that stage installed or created.

Q3: Why would you separate a "dependencies" stage from a "build" stage, as in the advanced example?
A3: Separating them allows Docker's layer caching to work more granularly: if only source code changes (not `package.json`), the dependency-installation layer (often the slowest step) can be reused from cache across both the dependencies stage and anything that copies from it, while only the build/compile step needs to rerun. This further speeds up iterative development/CI builds beyond what a single combined stage would achieve.

Q4: What's the risk of copying the entire builder stage's working directory into the final stage (`COPY --from=builder /app .`)?
A4: It defeats the size/security benefits of multi-stage builds — you'd be copying devDependencies, build tool caches, raw source files, and test files into the production image, resulting in a final image nearly as bloated as a naive single-stage build. The correct practice is to copy ONLY the specific, minimal set of artifacts actually needed at runtime (e.g., `dist/`, a pruned `node_modules`, `package.json`).

Q5: How does multi-stage building improve security, beyond just reducing image size?
A5: A smaller final image with fewer installed packages/tools means a smaller attack surface — there's no TypeScript compiler, no test frameworks, no build-time CLI tools, and often no shell utilities beyond the bare minimum present in the running container that an attacker could exploit if they gained some level of access. It also reduces the risk of accidentally shipping sensitive build-time artifacts (like `.env` files used only for building, or cached credentials) into the production image, since the final stage only contains what's explicitly copied over.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- The app requires a build/compile step (TypeScript, bundlers, native module compilation)
- You want to minimize final image size and attack surface for production deployments
- You're optimizing CI/CD pipeline speed via better layer caching

❌ Avoid when:
- A trivial plain-JavaScript app with no build step and few dependencies — a single-stage Dockerfile may be simple enough and multi-stage adds unnecessary complexity (though it rarely hurts to use it preemptively)

---

## 📊 Visual Diagram
```
┌─────────────────────────┐        ┌─────────────────────────┐
│   STAGE 1: builder        │        │   STAGE 2: runtime         │
│  - full node image         │        │  - minimal alpine image    │
│  - ALL deps (incl. dev)    │        │  - ONLY prod deps          │
│  - compiles TS → dist/     │──COPY──▶  - ONLY dist/ + package.json│
│  - test tools, source .ts  │ artifacts │  - non-root user           │
│  (discarded after build)   │        │  (this is what actually ships)│
└─────────────────────────┘        └─────────────────────────┘
       ~1.2 GB                              ~150 MB
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Multi-stage build | Multiple FROM stages in one Dockerfile | एक Dockerfile में multiple FROM stages |
| Builder stage | Throwaway stage used for compiling | Compile करने के लिए throwaway stage |
| COPY --from | Copies artifacts from a previous stage | पिछले stage से artifacts copy करना |
| Image bloat | Unnecessarily large final image | Unnecessarily बड़ी final image |
| npm prune --production | Removes devDependencies from node_modules | node_modules से devDependencies हटाना |

---

## ⚡ 3-Line Summary
**English:**
1. Multi-stage builds separate the build environment from the runtime environment within one Dockerfile.
2. Only the compiled output and production dependencies are copied into the final, minimal image.
3. This dramatically shrinks image size and reduces security attack surface compared to single-stage builds.

**Hindi:**
1. Multi-stage builds build environment को runtime environment से एक ही Dockerfile के अंदर अलग करते हैं।
2. सिर्फ compiled output और production dependencies final, minimal image में copy होते हैं।
3. यह single-stage builds की तुलना में image size को dramatically shrink करता है और security attack surface कम करता है।

---

## ➡️ Next Topic
**248. Docker Compose + Node + DB** — Orchestrating a Node.js app alongside its database and other services for local development.
