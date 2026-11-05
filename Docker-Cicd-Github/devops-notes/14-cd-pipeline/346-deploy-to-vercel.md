# 346. Deploy to Vercel
# हिंदी में: Vercel पर Deploy करना

---

## 🔵 Simple Definition (English)
Vercel is a hosting platform for frontends (React, Next.js) that builds your project and serves it from a global CDN. You can use its built-in Git integration (zero config) or deploy from GitHub Actions with the **Vercel CLI** (`vercel pull`, `vercel build`, `vercel deploy --prebuilt`) for full control.

## 🔵 सरल परिभाषा (Hindi)
Vercel frontends (React, Next.js) के लिए hosting platform है जो आपका project build करके global CDN से serve करता है। आप उसका built-in Git integration (बिना config) या GitHub Actions से **Vercel CLI** (`vercel pull`, `vercel build`, `vercel deploy --prebuilt`) इस्तेमाल कर सकते हैं ताकि पूरा control रहे।

---

## 🔴 Problem it Solves
Hosting a frontend yourself needs servers, Nginx, SSL, CDN and cache invalidation. Preview environments for each PR are hard to build by hand. Vercel gives HTTPS, edge CDN, instant rollbacks and a unique preview URL per pull request.

## 🔴 यह क्यों बना? (Hindi)
Frontend खुद host करने के लिए server, Nginx, SSL, CDN और cache invalidation चाहिए। हर PR का preview environment हाथ से बनाना कठिन है। Vercel HTTPS, edge CDN, instant rollback और हर pull request के लिए अलग preview URL देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create Vercel project; note VERCEL_ORG_ID and VERCEL_PROJECT_ID
Step 2 → Create an access token (Account Settings > Tokens)
Step 3 → Add the three values as GitHub secrets
Step 4 → PR: vercel pull (preview) → vercel build → vercel deploy --prebuilt
Step 5 → main: same with --prod flag
Step 6 → CLI prints deployment URL → comment on the PR / smoke test
Step 7 → Rollback = promote a previous deployment from dashboard/CLI
```

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Vercel project बनाओ; `VERCEL_ORG_ID` और `VERCEL_PROJECT_ID` नोट करो।
Step 2 → Access token बनाओ (Account Settings > Tokens)।
Step 3 → तीनों मान GitHub secrets में रखो।
Step 4 → PR पर: `vercel pull` (preview) → `vercel build` → `vercel deploy --prebuilt`।
Step 5 → main पर वही, `--prod` flag के साथ।
Step 6 → CLI deployment URL देता है → PR में comment / smoke test।
Step 7 → Rollback = dashboard/CLI से पिछला deployment promote करना।

---

## 🟡 Real World Example
A marketing site and dashboard (React/Next.js) for a startup. Each PR gets `https://myapp-git-feature-x.vercel.app` so designers can review before merge. Merge to `main` ships to production in about a minute, served from edge locations including Mumbai, with automatic HTTPS and rollback to the previous deployment in seconds.

## 🟡 Real Example Hindi mein
एक startup की marketing site और dashboard (React/Next.js)। हर PR को `https://myapp-git-feature-x.vercel.app` जैसा URL मिलता है ताकि designers merge से पहले review कर सकें। `main` पर merge होने के लगभग एक मिनट में production live हो जाता है, Mumbai सहित edge locations से serve होता है, HTTPS अपने आप और rollback कुछ सेकंड में।

---

## 💻 Code / Config Example — Basic

```yaml
# .github/workflows/vercel-basic.yml (simplest: CLI deploy on main)
name: vercel-basic                     # workflow name
on:
  push:
    branches: [main]                   # production deploy on main
jobs:
  deploy:
    runs-on: ubuntu-latest             # runner
    steps:
      - uses: actions/checkout@v4      # get code
      - uses: actions/setup-node@v4    # install Node
        with:
          node-version: 20
      - name: Deploy to Vercel         # npx downloads the CLI on demand
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}          # auth token
          VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}        # team/account id
          VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}  # project id
        run: npx vercel deploy --prod --yes --token "$VERCEL_TOKEN"   # remote build + deploy
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/vercel-advanced.yml (prebuilt, preview on PR, prod on main)
name: vercel-advanced
on:
  push:
    branches: [main]                   # production
  pull_request:                        # preview
permissions:
  contents: read
  pull-requests: write                 # allow commenting the preview URL
env:
  VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
  VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}
concurrency:
  group: vercel-${{ github.ref }}      # one deploy per ref
  cancel-in-progress: true
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci                    # install dependencies
      - run: npm test --if-present     # run tests when defined
      - run: npm i -g vercel@latest    # example: pin a version in production
      - name: Pull settings
        run: vercel pull --yes --environment=${{ github.ref == 'refs/heads/main' && 'production' || 'preview' }} --token=${{ secrets.VERCEL_TOKEN }}
      - name: Build
        run: vercel build ${{ github.ref == 'refs/heads/main' && '--prod' || '' }} --token=${{ secrets.VERCEL_TOKEN }}
      - name: Deploy prebuilt output
        id: deploy
        run: |
          URL=$(vercel deploy --prebuilt ${{ github.ref == 'refs/heads/main' && '--prod' || '' }} --token=${{ secrets.VERCEL_TOKEN }})  # stdout is the URL
          echo "url=$URL" >> "$GITHUB_OUTPUT"                  # expose to next step
      - name: Comment preview URL on PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: 'Preview: ${{ steps.deploy.outputs.url }}'
            })
```

The `vercel pull/build/deploy --prebuilt` flow is the documented pattern for CI; flags and defaults can change between CLI versions, so pin a version and check `vercel --help`. Not run against a real Vercel account here.

---

## 🟠 My Stack Integration
Vercel is best for the React/Next.js frontend; your Node.js/FastAPI backends stay on the VPS or AWS. Point the frontend to the API with an environment variable and handle CORS on the backend.

```bash
# set the API URL for each Vercel environment (CLI prompts for the value)
vercel env add VITE_API_URL production      # e.g. https://api.example.com
vercel env add VITE_API_URL preview         # e.g. https://staging-api.example.com
```

```nginx
# Backend Nginx on the VPS: allow only your Vercel domain (CORS)
location /api/ {
    proxy_pass http://127.0.0.1:3000;                      # Node.js upstream
    add_header Access-Control-Allow-Origin "https://myapp.vercel.app" always;  # exact origin, no *
    add_header Access-Control-Allow-Credentials "true" always;                 # cookies allowed
}
```

(Nginx snippet not tested with `nginx -t` here; handle the OPTIONS preflight in your app or add a block for it.)

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Committing `.vercel/` or tokens to git.
✅ Correct: Gitignore `.vercel`, keep the token in secrets only.

❌ Mistake 2: Server secrets exposed via `NEXT_PUBLIC_` / `VITE_` variables.
✅ Correct: Only non-secret values are public; keep secrets on the backend.

❌ Mistake 3: Using both Vercel Git integration and the Actions workflow, causing double deploys.
✅ Correct: Disable one (turn off Git auto-deploy or skip the workflow).

❌ Mistake 4: Wrong `ORG_ID`/`PROJECT_ID`, giving "project not found".
✅ Correct: Copy from `.vercel/project.json` after `vercel link`.

---

## 🧠 Tricky Interview Question
The preview works but production shows an old API URL. Why?

Answer: Environment variables are scoped per environment (Development/Preview/Production) and are baked into the frontend at **build time**. Changing a variable does not affect existing deployments; you must redeploy. Also confirm `vercel pull --environment=production` was used in CI.

---

## ⚫ Interview Questions + Answers

Q1: Why `--prebuilt`?
A1: Build runs in your CI (cached, with your tests and secrets), and Vercel only uploads the output; deployments are reproducible and the build is auditable.

Q2: How does rollback work?
A2: Each deployment is immutable; promote an earlier one to production (`vercel rollback` / dashboard).

Q3: Serverless limits on Vercel?
A3: Function duration, size and region limits depend on plan; long jobs and WebSockets belong on your own backend.

Q4: Git integration vs Actions?
A4: Git integration is zero config; Actions gives gating (tests, approvals, scans) before deploy.

Q5: How is a custom domain set up?
A5: Add the domain in the project, then create DNS records (A / CNAME) as shown; Vercel issues the TLS certificate.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- React/Next.js frontends needing CDN, previews and instant rollbacks.
- Small teams who do not want to run Nginx for static hosting.

❌ Avoid when:
- Long-running backends, heavy WebSockets, or strict data residency.
- You need full infra control or very predictable flat cost at high traffic.

---

## 📊 Visual Diagram
```
 PR opened ─► Actions: pull(preview) → build → deploy --prebuilt
                                              │
                                              ▼
                            https://app-git-feature.vercel.app  (comment on PR)
 merge main ─► Actions: pull(prod) → build --prod → deploy --prebuilt --prod
                                              │
                                              ▼
              Vercel Edge CDN (global) ──► users ──► API on VPS / AWS (CORS)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Preview deployment | Per-PR temporary site | हर PR की अस्थायी site |
| Production deployment | Live site on main | live site |
| Edge CDN | Servers close to users | user के पास के servers |
| Prebuilt | Build locally/CI, upload output | पहले build, फिर upload |
| Environment variables | Per-environment config | environment अनुसार config |
| Rollback | Promote old deployment | पुराना deployment चालू करना |

---

## ⚡ 3-Line Summary
English: Vercel hosts frontends on a CDN with preview and production deploys. Use the CLI prebuilt flow in Actions for gated deploys. Env vars are build-time and never put secrets in public ones.
Hindi: Vercel frontends को CDN पर preview और production deploys के साथ host करता है। Gated deploys के लिए Actions में CLI prebuilt flow लो। Env vars build-time होते हैं और public ones में secrets न डालो।

---

## ➡️ Next Topic
**347. Deploy to Netlify** - another static/JAMstack host with a similar flow and its own features.
