# 328. CI Pipeline for React
# हिंदी में: React के लिए CI Pipeline

---

## 🔵 Simple Definition (English)
A **React CI pipeline** installs dependencies, lints, type-checks, runs component tests (Jest/Vitest + Testing Library), builds the production bundle, checks bundle size and optionally runs end-to-end tests (Playwright), on every push and pull request.

## 🔵 सरल परिभाषा (Hindi)
**React CI pipeline** dependencies install करती है, lint, type-check, component tests (Jest/Vitest + Testing Library) चलाती है, production bundle build करती है, bundle size जाँचती है और optionally end-to-end tests (Playwright) चलाती है, हर push और pull request पर।

---

## 🔴 Problem it Solves
Frontend bugs are visible to every user at once: a broken import fails only at `npm run build`, a missing environment variable renders a blank page, a new heavy library doubles the bundle and makes mobile users wait 8 seconds, and a refactor silently breaks the checkout button. CI catches build failures, regressions and size explosions before the static files reach Nginx or a CDN.

## 🔴 यह क्यों बना? (Hindi)
Frontend bugs हर user को एक साथ दिखते हैं: टूटा import सिर्फ `npm run build` पर fail होता है, गायब environment variable से blank page बनता है, नई भारी library bundle दोगुना करके mobile users को 8 सेकंड इंतज़ार कराती है, और refactor चुपचाप checkout button तोड़ देता है। CI static files के Nginx या CDN पर पहुँचने से पहले build failures, regressions और size विस्फोट पकड़ लेता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Trigger on PR and push to main (paths: web/**)
Step 2 → setup-node with cache: npm, then npm ci
Step 3 → ESLint + tsc --noEmit
Step 4 → Unit/component tests (Vitest or Jest) with coverage
Step 5 → npm run build with the same env vars shape as production (VITE_API_URL etc.)
Step 6 → Check bundle size budget; upload dist/ as an artifact
Step 7 → (optional) Playwright e2e against `vite preview`
Step 8 → Docker build (nginx serving dist/) to verify the production image
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → PR और main पर push पर trigger (paths: web/**)
Step 2 → cache: npm के साथ setup-node, फिर npm ci
Step 3 → ESLint + tsc --noEmit
Step 4 → Coverage के साथ unit/component tests (Vitest या Jest)
Step 5 → production जैसे env vars (VITE_API_URL आदि) के साथ npm run build
Step 6 → Bundle size budget जाँचो; dist/ को artifact के रूप में upload करो
Step 7 → (optional) `vite preview` पर Playwright e2e
Step 8 → Production image जाँचने के लिए Docker build (nginx, dist/ serve करता है)
```

---

## 🟡 Real World Example
A Myntra-style fashion storefront (React + Vite) ships daily. A PR imported all of `lodash` instead of `lodash/debounce`, which pushed the main bundle from 180 KB to 310 KB. The CI bundle-size check (a simple script comparing `dist/assets/*.js` size to a budget) failed the PR with a clear message, so the team fixed the import before it slowed every mobile page.

## 🟡 Real Example Hindi mein
Myntra-जैसा fashion storefront (React + Vite) रोज़ ship होता है। एक PR ने `lodash/debounce` की जगह पूरा `lodash` import कर दिया जिससे main bundle 180 KB से 310 KB हो गया। CI के bundle-size check (एक सरल script जो `dist/assets/*.js` का size budget से मिलाती है) ने साफ message के साथ PR fail कर दिया और टीम ने import ठीक किया, इससे पहले कि हर mobile page धीमा होता।

---

## 💻 Code / Config Example — Basic
```yaml
# .github/workflows/web-ci.yml  (minimal React CI)
name: Web CI                        # workflow name
on: [push, pull_request]            # run on push and PR
jobs:                               # jobs
  build:                            # job id
    runs-on: ubuntu-latest          # runner
    steps:                          # steps
      - uses: actions/checkout@v4   # get code (example version)
      - uses: actions/setup-node@v4 # install Node
        with:                       # inputs
          node-version: 20          # Node 20
          cache: npm                # cache npm
      - run: npm ci                 # reproducible install
      - run: npm run lint           # ESLint
      - run: npm test -- --run      # Vitest single run (Jest: npm test -- --ci)
      - run: npm run build          # production bundle must compile
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/web-ci.yml  (production React CI with e2e + budget)
name: Web CI                        # workflow name
on:                                 # triggers
  push:                             # push
    branches: [main]                # main
  pull_request:                     # PRs
    paths: ['web/**', '.github/workflows/web-ci.yml']  # run only for frontend changes
concurrency:                        # cancel stale
  group: web-ci-${{ github.ref }}   # per ref
  cancel-in-progress: true          # newer wins
permissions:                        # least privilege
  contents: read                    # read only
defaults:                           # defaults
  run:                              # run steps
    working-directory: web          # React app lives in web/
jobs:                               # jobs
  quality:                          # fast gate
    runs-on: ubuntu-latest          # runner
    timeout-minutes: 10             # cap
    steps:                          # steps
      - uses: actions/checkout@v4   # checkout
      - uses: actions/setup-node@v4 # node
        with:                       # inputs
          node-version: 20          # version
          cache: npm                # cache
          cache-dependency-path: web/package-lock.json  # lock file in subfolder
      - run: npm ci                 # install
      - run: npm run lint           # ESLint
      - run: npx tsc --noEmit       # types
      - run: npm test -- --run --coverage  # component tests with coverage (Vitest syntax)
  build:                            # production build + size budget
    needs: quality                  # after gate
    runs-on: ubuntu-latest          # runner
    timeout-minutes: 10             # cap
    env:                            # build-time env (public values only!)
      VITE_API_URL: https://api.example.com  # example API base URL baked into bundle
    steps:                          # steps
      - uses: actions/checkout@v4   # checkout
      - uses: actions/setup-node@v4 # node
        with:                       # inputs
          node-version: 20          # version
          cache: npm                # cache
          cache-dependency-path: web/package-lock.json  # lock
      - run: npm ci                 # install
      - run: npm run build          # creates dist/
      - name: Bundle size budget    # fail if the biggest JS file is over 250 KB
        run: |                      # shell
          max=256000                                           # budget in bytes
          size=$(find dist/assets -name '*.js' -printf '%s\n' | sort -n | tail -1)  # largest js file
          echo "largest bundle: $size bytes (budget $max)"      # log
          [ "$size" -le "$max" ]                                # non-zero exit if over budget
      - uses: actions/upload-artifact@v4  # keep build for deploy/inspection
        with:                       # inputs
          name: web-dist            # artifact name
          path: web/dist            # build output
          retention-days: 7         # cleanup
  e2e:                              # Playwright browser tests
    needs: build                    # after build
    runs-on: ubuntu-latest          # runner
    timeout-minutes: 20             # cap
    steps:                          # steps
      - uses: actions/checkout@v4   # checkout
      - uses: actions/setup-node@v4 # node
        with:                       # inputs
          node-version: 20          # version
          cache: npm                # cache
          cache-dependency-path: web/package-lock.json  # lock
      - run: npm ci                 # install
      - run: npx playwright install --with-deps chromium  # download browser + OS libs
      - run: npx playwright test    # run e2e (config starts vite preview via webServer)
      - uses: actions/upload-artifact@v4  # keep report on failure
        if: failure()               # only when e2e failed
        with:                       # inputs
          name: playwright-report   # name
          path: web/playwright-report  # HTML report
```

---

## 🟠 My Stack Integration
The React app is built to static files and served by Nginx on the VPS. A multi-stage Dockerfile mirrors that: Node builds, Nginx serves. API calls go to `/api` which Nginx proxies to the Node/FastAPI container, so no API URL or CORS needed in the browser.

```dockerfile
# web/Dockerfile (copy-paste ready)
# Stage 1: build the static bundle
FROM node:20-alpine AS build
# Working directory
WORKDIR /app
# Copy manifests first for caching
COPY package*.json ./
# Exact install
RUN npm ci
# Copy source
COPY . .
# Build; relative API path means Nginx proxies /api
ARG VITE_API_URL=/api
# Make ARG visible to the build tool
ENV VITE_API_URL=$VITE_API_URL
# Produce dist/
RUN npm run build

# Stage 2: serve with nginx
FROM nginx:1.27-alpine
# SPA routing config (try_files to index.html, proxy /api)
COPY nginx.conf /etc/nginx/conf.d/default.conf
# Copy only the compiled files
COPY --from=build /app/dist /usr/share/nginx/html
# HTTP port
EXPOSE 80
```

Security: everything with a `VITE_` prefix is public inside the bundle, so never put secrets in it; CI uses `contents: read` and no deploy credentials.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Putting API keys in `VITE_*`/`REACT_APP_*` variables.
✅ Correct: Only public config goes there; secrets stay on the backend.

❌ Mistake 2: Running Jest in watch mode in CI, so the job hangs forever.
✅ Correct: Use `--ci` (Jest) or `--run` (Vitest) and set `CI=true`.

❌ Mistake 3: Skipping `npm run build` because tests pass.
✅ Correct: Always build; many errors (bad imports, env typos) appear only there.

❌ Mistake 4: Not caching Playwright browsers and reinstalling every run.
✅ Correct: Cache `~/.cache/ms-playwright` or only run e2e on main/nightly.

---

## 🧠 Tricky Interview Question
**Q:** CI is green, the site deploys, but users see a blank page on refresh of `/orders/42` while `/` works. Why, and can CI catch it?

Answer: The static server does not fall back to `index.html` for client-side routes, so Nginx returns 404 (or blank). Fix with `try_files $uri /index.html;`. CI can catch it by building the Docker image, running it, and curling a deep route (or a Playwright test that opens `/orders/42` directly), which checks both the bundle and the server config together.

---

## ⚫ Interview Questions + Answers

Q1: Why does `npm run build` matter in CI?
A1: It runs the real bundler with tree-shaking and type/import resolution, finding errors tests never touch.

Q2: How do you stop environment-specific values from being hardcoded?
A2: Use build-time variables (`VITE_*`) set per environment in the workflow/Docker `ARG`, or runtime config via a `/config.json`; never commit `.env` with secrets.

Q3: Jest vs Vitest in CI?
A3: Both work. Vitest shares Vite config and is faster for Vite apps; Jest is the CRA-era default. In CI use non-watch flags in both.

Q4: How do you control bundle size?
A4: Code splitting (`React.lazy`), analyzer plugins, and a CI budget check that fails on regression.

Q5: Should e2e run on every PR?
A5: Run a small smoke e2e on PRs, the full suite on main or nightly, because browsers are slow and flaky if overused.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any React/Vite/Next static build with multiple contributors.
- You deploy static files to Nginx/S3/CDN.

❌ Avoid when:
- Prototype with no tests: still keep lint + build.
- Don't run full browser e2e on every tiny commit.

---

## 📊 Visual Diagram
```
PR (web/** changed)
   |
   v
[lint -> tsc -> vitest] --fail--> RED
   |
   v
[vite build -> size budget -> upload dist] --fail--> RED
   |
   v
[playwright e2e on built app] --fail--> RED (report artifact)
   |
   v
GREEN -> merge -> CD builds nginx image -> VPS serves dist/ + proxies /api
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Bundle | Compiled JS/CSS output | compile होकर बनी JS/CSS |
| Budget | Max allowed size | अधिकतम अनुमत size |
| e2e | Whole-app browser test | पूरे app का browser test |
| Tree-shaking | Removes unused code | बेकार code हटाना |
| SPA fallback | Serve index.html for routes | routes पर index.html देना |

---

## ⚡ 3-Line Summary
English: React CI = cached `npm ci`, lint, types, tests, production build, size budget, optional e2e.
English: Use non-watch test flags and keep secrets out of `VITE_*` variables.
English: Verify the Nginx image serves deep routes, not just the home page.

Hindi: React CI = cached `npm ci`, lint, types, tests, production build, size budget, optional e2e।
Hindi: Non-watch test flags इस्तेमाल करो और `VITE_*` variables में secrets मत रखो।
Hindi: जाँचो कि Nginx image deep routes भी serve करती है, सिर्फ home page नहीं।

---

## ➡️ Next Topic
**329. CI Pipeline for NestJS** — a structured TypeScript backend with e2e tests and its own build step.
