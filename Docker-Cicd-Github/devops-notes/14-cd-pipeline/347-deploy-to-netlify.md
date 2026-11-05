# 347. Deploy to Netlify
# हिंदी में: Netlify पर Deploy करना

---

## 🔵 Simple Definition (English)
Netlify hosts static sites and serverless functions on a CDN. You can connect the Git repo (auto build) or deploy from GitHub Actions using the **Netlify CLI** (`netlify deploy --dir=dist --prod`) with a personal access token and the site ID.

## 🔵 सरल परिभाषा (Hindi)
Netlify static sites और serverless functions को CDN पर host करता है। आप Git repo जोड़ सकते हैं (auto build) या GitHub Actions से **Netlify CLI** (`netlify deploy --dir=dist --prod`) चला सकते हैं, personal access token और site ID के साथ।

---

## 🔴 Problem it Solves
Static frontends need HTTPS, CDN, redirects for single-page apps, form handling and previews. Setting this up with Nginx and servers is work and ongoing maintenance. Netlify makes each deploy atomic (all files or none) and keeps every deploy for instant rollback.

## 🔴 यह क्यों बना? (Hindi)
Static frontends को HTTPS, CDN, SPA के लिए redirects, form handling और previews चाहिए। Nginx और servers से यह सब बनाना और संभालना मेहनत है। Netlify हर deploy को atomic रखता है (सारी files या कोई नहीं) और instant rollback के लिए हर deploy सहेजता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create a site (netlify sites:create) → get Site ID
Step 2 → Create personal access token → NETLIFY_AUTH_TOKEN secret
Step 3 → CI: npm ci → npm run build → output in dist/ (Vite) or build/
Step 4 → PR: netlify deploy --dir=dist (draft/preview URL)
Step 5 → main: netlify deploy --dir=dist --prod
Step 6 → netlify.toml supplies redirects, headers, functions dir
Step 7 → Rollback: publish an earlier deploy from the UI/CLI
```

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Site बनाओ (`netlify sites:create`) → Site ID मिलेगा।
Step 2 → Personal access token बनाओ → `NETLIFY_AUTH_TOKEN` secret।
Step 3 → CI: `npm ci` → `npm run build` → output `dist/` (Vite) या `build/`।
Step 4 → PR पर: `netlify deploy --dir=dist` (draft/preview URL)।
Step 5 → main पर: `netlify deploy --dir=dist --prod`।
Step 6 → `netlify.toml` redirects, headers और functions dir देता है।
Step 7 → Rollback: UI/CLI से पुराना deploy publish करो।

---

## 🟡 Real World Example
A coaching-institute website built in React (Vite). Every PR gets a draft URL for content review. The `netlify.toml` redirects all routes to `index.html` so client-side routing (`/courses/123`) does not 404 on refresh, and sets security headers. Production deploy happens on merge; if a bug slips through, the team republishes the previous deploy in a click.

## 🟡 Real Example Hindi mein
एक coaching-institute की website React (Vite) में बनी है। हर PR पर content review के लिए draft URL मिलता है। `netlify.toml` सभी routes को `index.html` पर redirect करता है ताकि client-side routing (`/courses/123`) refresh पर 404 न दे, और security headers भी सेट करता है। merge पर production deploy होता है; bug निकले तो पिछला deploy एक click में दोबारा publish।

---

## 💻 Code / Config Example — Basic

```yaml
# .github/workflows/netlify-basic.yml
name: netlify-basic                    # workflow name
on:
  push:
    branches: [main]                   # production deploy on main
jobs:
  deploy:
    runs-on: ubuntu-latest             # runner
    steps:
      - uses: actions/checkout@v4      # get code
      - uses: actions/setup-node@v4    # Node for the build
        with:
          node-version: 20
      - run: npm ci                    # install exactly from lockfile
      - run: npm run build             # produces dist/
      - name: Deploy to Netlify
        env:
          NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}   # personal access token
          NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}         # which site to update
        run: npx netlify-cli deploy --dir=dist --prod             # upload build output
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/netlify-advanced.yml (draft preview on PR, prod on main)
name: netlify-advanced
on:
  push:
    branches: [main]
  pull_request:
permissions:
  contents: read
  pull-requests: write                 # to comment preview URL
env:
  NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
  NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - run: npm test --if-present
      - run: npm run build
        env:
          VITE_API_URL: ${{ github.ref == 'refs/heads/main' && 'https://api.example.com' || 'https://staging-api.example.com' }}  # build-time API URL
      - name: Deploy (draft on PR, prod on main)
        id: deploy
        run: |
          if [ "${{ github.ref }}" = "refs/heads/main" ]; then
            npx netlify-cli deploy --dir=dist --prod --json > result.json        # production
          else
            npx netlify-cli deploy --dir=dist --alias "pr-${{ github.event.number }}" --json > result.json   # preview alias
          fi
          echo "url=$(jq -r '.deploy_url' result.json)" >> "$GITHUB_OUTPUT"      # deploy URL
      - name: Comment on PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: 'Netlify preview: ${{ steps.deploy.outputs.url }}'
            })
```

```toml
# netlify.toml - lives in repo root
[build]
  command = "npm run build"            # build command (used by Netlify's own builder)
  publish = "dist"                     # folder to publish

[[redirects]]
  from = "/api/*"                      # proxy API calls to your backend (no CORS needed)
  to = "https://api.example.com/:splat"
  status = 200                         # rewrite, not redirect

[[redirects]]
  from = "/*"                          # SPA fallback for client-side routing
  to = "/index.html"
  status = 200

[[headers]]
  for = "/*"                           # security headers on every response
  [headers.values]
    X-Frame-Options = "DENY"
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"
```

The `--alias` and `--json` flags exist in the Netlify CLI at the time of writing; verify with `netlify deploy --help` for your pinned version. Not run against a real Netlify account here.

---

## 🟠 My Stack Integration
React front end on Netlify, Node.js/FastAPI on VPS or AWS. The `/api/*` proxy rewrite above hides your backend origin and removes browser CORS issues. Your VPS Nginx should still restrict traffic (rate limits, TLS) because proxied traffic reaches it from Netlify's edge.

```bash
# local check before pushing: build and preview the production bundle
npm ci && npm run build               # same steps as CI
npx netlify-cli dev --dir=dist        # serve locally with netlify.toml rules applied
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Refreshing `/dashboard` returns 404.
✅ Correct: Add the `/* -> /index.html` 200 rewrite.

❌ Mistake 2: Publishing the wrong folder (`build` vs `dist`).
✅ Correct: Match `--dir`/`publish` to your tool's output (Vite: `dist`, CRA: `build`).

❌ Mistake 3: Secrets in `VITE_`/`REACT_APP_` variables, which end up in the public bundle.
✅ Correct: Keep secrets in the backend.

❌ Mistake 4: Both Netlify Git auto-build and Actions deploy enabled.
✅ Correct: Choose one pipeline.

---

## 🧠 Tricky Interview Question
Your `--prod` deploy succeeded but the site shows an old page. Why?

Answer: Common causes: browser/service-worker cache serving the old `index.html`; deploying to a different site ID; publishing the wrong directory (an old folder); or the "Production deploys" being locked/stopped auto-publishing in the Netlify UI (deploy exists but is not published). Check the deploy list for the published one and add `Cache-Control: no-cache` for `index.html`.

---

## ⚫ Interview Questions + Answers

Q1: Draft deploy vs production deploy?
A1: Draft gets a unique unlisted URL; `--prod` publishes to the main domain.

Q2: What are Netlify Functions?
A2: Serverless functions (AWS Lambda under the hood) in a configured directory, called at `/.netlify/functions/<name>`.

Q3: How do you roll back?
A3: Deploys are immutable; click "Publish deploy" on an older one.

Q4: Netlify vs Vercel?
A4: Very similar. Vercel is optimized for Next.js features; Netlify has forms, identity, and a broader static/JAMstack focus. Choose by features and pricing.

Q5: How to keep tokens safe?
A5: Store in GitHub secrets, use an environment with approvals for production, and rotate tokens.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Static React/Vue sites, docs, landing pages.
- You want previews per PR and simple rollback.

❌ Avoid when:
- You need a long-running API or database.
- Heavy SSR requirements better handled by your own infra.

---

## 📊 Visual Diagram
```
 PR ─► build (dist/) ─► netlify deploy --alias pr-12 ─► draft URL ─► comment
 main ─► build (dist/) ─► netlify deploy --prod ─► atomic publish
                                   │
                                   ▼
                  Netlify CDN: / → index.html, /* → SPA fallback
                  /api/* ──proxy──► your Node.js / FastAPI backend
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Site ID | Identifier of the site | site की पहचान |
| Draft deploy | Unlisted preview | अस्थायी preview |
| Atomic deploy | All-or-nothing publish | सब या कुछ नहीं |
| netlify.toml | Config file for the site | site की config file |
| Rewrite | Serve other content, same URL | URL वही, content दूसरा |
| Functions | Serverless endpoints | serverless endpoints |

---

## ⚡ 3-Line Summary
English: Build in CI and deploy `dist/` with the Netlify CLI. Use netlify.toml for SPA fallback, headers and API proxy. Previews on PRs, atomic prod deploys, instant rollback.
Hindi: CI में build करके Netlify CLI से `dist/` deploy करो। SPA fallback, headers और API proxy के लिए netlify.toml। PR पर preview, atomic prod deploy, instant rollback।

---

## ➡️ Next Topic
**348. Deploy to Railway** - a platform that runs full backends, databases and containers with minimal setup.
