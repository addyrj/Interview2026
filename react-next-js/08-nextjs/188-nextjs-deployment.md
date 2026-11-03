# 188. Next.js Deployment (Vercel/AWS)
# हिंदी में: Next.js Deployment — Vercel और AWS पर app को live करना

---

## 🔵 Simple Definition (English)
**Deployment** means building your Next.js app (`next build`) and running it on a server or platform so real users can open it. You can use a managed platform like **Vercel**, a container or Node server (for example on **AWS**), or a static export on a CDN.

## 🔵 सरल परिभाषा (Hindi)
**Deployment** का मतलब है अपने Next.js app को build करना (`next build`) और किसी server या platform पर चलाना ताकि असली users उसे खोल सकें। आप **Vercel** जैसा managed platform, **AWS** पर Node server या container, या CDN पर static export इस्तेमाल कर सकते हैं।

---

## 🔴 Problem it Solves

A Next.js app is not just HTML files. It has Server Components, API route handlers, middleware, image optimization and caching. If you copy the `app/` folder to a plain web server, none of that works. You also need HTTPS, a CDN, environment variables, rollbacks and scaling when traffic spikes (for example during a Flipkart Big Billion Days sale). Deployment platforms and a correct build setup solve these problems.

```
Dev machine (next dev)          Production (next build + next start)
- hot reload, slow, no cache    - optimized bundles, caching, minified
- only you use it               - thousands of users, needs HTTPS and scale
```

## 🔴 यह क्यों बना? (Hindi)
Next.js app सिर्फ HTML files नहीं है। इसमें Server Components, API route handlers, middleware, image optimization और caching होती है। अगर आप `app/` folder को किसी साधारण web server पर कॉपी कर दें तो यह सब काम नहीं करेगा। आपको HTTPS, CDN, environment variables, rollback और traffic बढ़ने पर scaling भी चाहिए (जैसे Flipkart की Big Billion Days sale में)। सही build setup और deployment platforms इन्हीं समस्याओं को हल करते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Push code to Git (GitHub)
Step 2 → Platform runs: npm install, then next build
Step 3 → next build creates the .next folder (server code, static files, route manifests)
Step 4 → Static pages and assets go to a CDN; dynamic routes run as serverless functions or on a Node server
Step 5 → Environment variables are set in the platform dashboard
Step 6 → The platform gives a URL; every Pull Request gets its own preview URL
Step 7 → Merge to main → new production deployment; the old one stays for instant rollback
```

Three common hosting options:

| Option | How | Good for |
|--------|-----|----------|
| Vercel | Connect Git repo, auto build and deploy | Fastest setup, all features work |
| Node server / Docker | `next build` then `next start` (use `output: 'standalone'`) | AWS ECS/EC2, any VM or container platform |
| Static export | `output: 'export'` gives plain HTML/JS/CSS | S3 + CloudFront; no server features |

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Code को Git (GitHub) पर push करो
Step 2 → Platform चलाता है: npm install, फिर next build
Step 3 → next build से .next folder बनता है (server code, static files, route manifests)
Step 4 → Static pages और assets CDN पर जाते हैं; dynamic routes serverless functions या Node server पर चलते हैं
Step 5 → Environment variables platform के dashboard में set होते हैं
Step 6 → Platform एक URL देता है; हर Pull Request को अपना preview URL मिलता है
Step 7 → main में merge → नया production deployment; पुराना rollback के लिए तैयार रहता है
```

तीन आम hosting options: **Vercel** (सबसे आसान, सारे features चलते हैं), **Node server / Docker** (`next build` + `next start`, AWS ECS/EC2 पर) और **Static export** (`output: 'export'`, S3 + CloudFront, लेकिन server features नहीं मिलते)।

---

## 🟡 Real World Example
**Swiggy-style food app:** The team keeps the code on GitHub. Each Pull Request gets a Vercel preview URL, so QA can test the new "Offers" page before release. Merging to `main` deploys to production. During a dinner rush the platform scales the serverless functions automatically. If a bug appears, one click rolls back to the previous deployment. A larger company with its own cloud might instead build a Docker image and run it on AWS ECS behind a load balancer and CloudFront.

## 🟡 Real Example Hindi mein
**Swiggy जैसा food app:** Team अपना code GitHub पर रखती है। हर Pull Request को Vercel का preview URL मिलता है, इसलिए QA release से पहले नया "Offers" page test कर लेती है। `main` में merge होते ही production deploy हो जाता है। रात के dinner rush में platform serverless functions अपने आप scale करता है। कोई bug आए तो एक click में पुराने deployment पर rollback हो जाता है। अपनी cloud वाली बड़ी कंपनी Docker image बनाकर उसे AWS ECS पर load balancer और CloudFront के पीछे चला सकती है।

---

## 💻 Code Example — Basic

```jsx
// next.config.js: settings that decide HOW the app is deployed
/** @type {import('next').NextConfig} */
const nextConfig = {
  // Pick ONE output mode (comment/uncomment as needed):
  // output: 'export',      // static HTML only: no server code, no ISR, no middleware, no default image optimizer
  output: 'standalone',      // small self-contained server folder, ideal for Docker/AWS
  images: {
    remotePatterns: [        // allow images only from trusted hosts
      { protocol: 'https', hostname: 'images.example-cdn.com' },
    ],
  },
};

module.exports = nextConfig; // Next.js reads this file at build time
```

```bash
# Local production check before deploying (always do this)
npm run build   # creates .next, shows which routes are static/dynamic
npm run start   # starts the production server on port 3000
# Vercel CLI (optional): npm i -g vercel, then run: vercel --prod
```

## 💻 Code Example — Advanced

```jsx
// Dockerfile for AWS (ECS/Fargate/EC2). Needs output: 'standalone' in next.config.js
// ---- stage 1: install and build ----
// FROM node:20-alpine AS builder          // small Node image
// WORKDIR /app
// COPY package*.json ./
// RUN npm ci                              // exact dependency versions
// COPY . .
// RUN npm run build                       // creates .next/standalone
//
// ---- stage 2: tiny runtime image ----
// FROM node:20-alpine AS runner
// WORKDIR /app
// ENV NODE_ENV=production
// COPY --from=builder /app/.next/standalone ./       // server + minimal node_modules
// COPY --from=builder /app/.next/static ./.next/static // static assets
// COPY --from=builder /app/public ./public
// EXPOSE 3000
// CMD ["node", "server.js"]               // standalone output creates server.js
```

```jsx
// app/api/health/route.js: health check used by the load balancer (AWS ALB target group)
export const dynamic = 'force-dynamic';        // never cache the health response

export async function GET() {
  return Response.json({ status: 'ok', time: Date.now() }); // 200 means the container is healthy
}
```

```jsx
// .github/workflows/ci.yml equivalent steps, written as a JS object for clarity
// A CI pipeline before deploy: install, lint, test, build, then deploy.
const pipeline = [
  'npm ci',            // install exact dependencies
  'npm run lint',      // catch code problems
  'npm test',          // run tests
  'npm run build',     // a failing build must stop the release
  // then: deploy to Vercel (vercel --prod) or push image to ECR and update the ECS service
];
console.log(pipeline.join(' -> '));
```

---

## 🟠 Next.js Connection
This whole topic is Next.js specific, but a few rules are worth remembering. Which features work depends on where you deploy:

```jsx
// app/dashboard/page.jsx
export const runtime = 'nodejs';     // full Node APIs (default). 'edge' = lighter, runs close to users, fewer APIs
export const revalidate = 60;        // ISR: needs a server or Vercel; NOT available with output: 'export'

export default async function Page() {
  const res = await fetch('https://api.example.com/stats'); // runs on the server at request/revalidate time
  const stats = await res.json();                           // parse JSON
  return <h1>Orders today: {stats.orders}</h1>;             // HTML sent to the browser
}
```

- Vercel: all features (ISR, middleware, Image Optimization, Server Actions) work with zero setup.
- Self-hosting (AWS): you manage the cache. With several containers, the default in-memory/file cache is not shared; use a custom cache handler (`cacheHandler` in `next.config.js`) or a shared store. Details are version-dependent, check the docs for your Next.js version.
- Static export: good for docs and landing pages, but no Server Actions, no cookies/headers, no ISR.

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using `output: 'export'` and then adding API routes, middleware or ISR
✅ **Correct:** Use static export only for fully static sites; otherwise deploy to Vercel or a Node server

```jsx
// Wrong: export mode cannot run server code
// next.config.js  -> output: 'export'
// app/api/orders/route.js exists  -> build error or feature missing

// Right: remove output: 'export' (or use 'standalone') when you need server features
module.exports = { output: 'standalone' };
```

❌ **Mistake 2:** Not testing the production build locally and finding errors only after deploy
✅ **Correct:** Run `npm run build && npm run start` and fix type, lint and prerender errors first

```jsx
// Wrong: deploy straight from `next dev`, which hides prerender and bundle problems
// Right: CI runs build; the release is blocked if the build fails
// package.json scripts: { "build": "next build", "start": "next start" }
```

❌ **Mistake 3:** Putting secrets in `NEXT_PUBLIC_` variables or committing `.env` files
✅ **Correct:** Set secrets in the platform dashboard, and expose only public values with `NEXT_PUBLIC_`

```jsx
// Wrong: this key is bundled into the browser JavaScript and visible to everyone
// NEXT_PUBLIC_STRIPE_SECRET=sk_live_...

// Right: server-only variable, read only in Server Components / route handlers
const secret = process.env.STRIPE_SECRET;   // never sent to the browser
```

---

## 🧠 Tricky Interview Question

```jsx
// next.config.js
module.exports = { output: 'export' };

// app/page.jsx
export default async function Page() {
  const data = await fetch('https://api.example.com/price', { cache: 'no-store' }).then(r => r.json());
  return <p>{data.price}</p>;
}
```
**Answer:** With `output: 'export'` the page is rendered once at build time into static HTML. The `fetch` runs during `next build`, not for each visitor, so the price is frozen at the moment of the build. `cache: 'no-store'` would normally make the page dynamic, but a dynamic page cannot be exported, so the build is expected to fail with an error (exact message is version-dependent). If you need fresh prices, either fetch on the client (for example with TanStack Query) or deploy with a server and use dynamic rendering or ISR.

---

## ⚫ Interview Questions + Answers

Q1: How do you deploy a Next.js app to Vercel?
A1: Push the code to GitHub, import the repo in Vercel, set environment variables and click deploy. Vercel detects Next.js, runs `next build`, puts static assets on its CDN and runs dynamic routes as serverless or edge functions. Every Pull Request gets a preview URL and every merge to the main branch gets a production deployment.

Q2: What is the difference between `next start`, `output: 'standalone'` and `output: 'export'`?
A2: `next start` runs the production server using the full `node_modules`. `standalone` copies only the files needed into `.next/standalone` with a small `server.js`, which makes Docker images small. `export` produces only static HTML/CSS/JS with no server, so server features (Server Actions, middleware, ISR, cookies) are unavailable.

Q3: What changes when self-hosting on AWS compared to Vercel?
A3: You own the infrastructure: build the Docker image, run it on ECS/EC2, put an Application Load Balancer and CloudFront in front, handle HTTPS, logs, autoscaling and a shared cache for ISR across instances. On Vercel these are handled for you.

Q4: What is a preview deployment and why is it useful?
A4: A unique deployment created for every branch or Pull Request. Developers, designers and QA can test changes on a real URL before merging, which catches bugs early and makes review easier.

Q5: How do you roll back a bad release?
A5: On Vercel, promote a previous deployment to production in one click, since old deployments are kept immutable. On AWS, redeploy the previous Docker image tag to the ECS service. This is why you should tag images with the Git commit hash and never rely on `latest`.

---

## 🔷 When to Use + When Not to Use
✅ **Use Vercel when:**
- You want the fastest setup and all Next.js features working out of the box
- You need preview deployments, instant rollback and automatic scaling

✅ **Use AWS / Docker when:**
- Company rules require your own cloud, VPC, or data residency
- You want fixed, predictable cost at very high traffic or need other AWS services nearby

❌ **Avoid static export when:**
- You need personalization, Server Actions, ISR, or authenticated pages
- Content changes often and a full rebuild for each change is too slow

---

## 📊 Visual Diagram

```
   Developer ──git push──► GitHub ──webhook──► Build (next build)
                                                   │
                           ┌───────────────────────┴───────────────────┐
                           ▼                                           ▼
                  Static assets, ISR pages                   Dynamic routes / Actions
                       (CDN edge)                       (serverless functions / Node server)
                           │                                           │
                           └──────────────► User's browser ◄───────────┘

   AWS self-host:  User ─► CloudFront ─► ALB ─► ECS tasks (Docker: node server.js)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Deployment | Making the built app available to users | App को users के लिए live करना |
| `next build` | Creates the optimized production build | Production build बनाने वाला command |
| CDN | Network of servers that serve files near the user | User के पास से files देने वाला server network |
| Serverless function | Code that runs on demand without managing servers | बिना server संभाले ज़रूरत पर चलने वाला code |
| Preview deployment | Temporary URL for each Pull Request | हर Pull Request का अस्थायी URL |
| standalone output | Minimal self-contained server build | छोटा self-contained server build |
| Static export | Plain HTML build without a server | बिना server का सादा HTML build |
| Rollback | Going back to a previous release | पुराने release पर वापस जाना |

---

## ⚡ 3-Line Summary
**English:**
1. Deploying Next.js means running `next build` and hosting the output on Vercel, a Node/Docker server (AWS), or as a static export.
2. Vercel supports every feature with zero setup; self-hosting gives control but you manage cache, scaling and HTTPS.
3. Always test the production build locally, keep secrets out of `NEXT_PUBLIC_`, and keep rollback ready.

**Hindi:**
1. Next.js deploy करने का मतलब `next build` चलाकर output को Vercel, Node/Docker server (AWS) या static export के रूप में host करना है।
2. Vercel पर सारे features बिना setup चलते हैं; self-hosting में control मिलता है लेकिन cache, scaling और HTTPS आपको संभालना पड़ता है।
3. Production build को हमेशा local में test करो, secrets को `NEXT_PUBLIC_` में मत रखो, और rollback तैयार रखो।

---

## ➡️ Next Topic
**189. Next.js Environment Variables** — deployment में सबसे ज़्यादा गलतियाँ env variables से होती हैं: कौन सा browser को जाता है, कौन सा सिर्फ server पर रहता है, और build time बनाम runtime का फर्क।
