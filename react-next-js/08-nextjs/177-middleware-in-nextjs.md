# 177. Middleware in Next.js
# हिंदी में: Next.js Middleware — Request पूरा होने से पहले बीच में चलने वाला code

---

## 🔵 Simple Definition (English)
**Middleware** is a function in a root `middleware.js` file that runs before a request reaches a page or API route. It can redirect, rewrite, set headers or cookies, or block the request, based on the incoming URL, headers and cookies.

## 🔵 सरल परिभाषा (Hindi)
**Middleware** root की `middleware.js` file में एक function है जो request के page या API route तक पहुँचने से पहले चलता है। यह URL, headers और cookies देखकर redirect, rewrite, headers/cookies set या request को block कर सकता है।

---

## 🔴 Problem it Solves

Without middleware, auth checks, locale redirects and A/B tests were repeated inside every page. The check ran only after the page started rendering, so a logged-out user could still trigger server work. Middleware centralizes this logic at the edge of your app, runs before rendering and before cache lookup, and keeps pages clean.

```jsx
// PROBLEM: the same check copied into every page
export default async function Page() {
  const token = (await cookies()).get('token');
  if (!token) redirect('/login');        // repeated in /orders, /profile, /wallet ...
}

// SOLUTION: one middleware.js guards all of them
```

## 🔴 यह क्यों बना? (Hindi)
Middleware से पहले auth checks, locale redirects और A/B tests हर page में दोहराने पड़ते थे। Check तब चलता था जब page render होना शुरू हो चुका होता, इसलिए logged-out user भी server का काम करवा सकता था। Middleware इस logic को एक जगह रखता है, rendering और cache lookup से पहले चलता है, और pages को साफ रखता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create middleware.js (or .ts) at the project root, next to app/ (or inside src/)
Step 2 → Export a function middleware(request) (Next.js 16 renames this file to proxy.js; version-dependent)
Step 3 → Inspect request.nextUrl, request.cookies, request.headers
Step 4 → Return NextResponse.next() to continue, redirect() to send elsewhere,
         rewrite() to show different content on the same URL, or a Response to stop
Step 5 → Export config.matcher to limit which paths run the middleware
Step 6 → Runs on every matched request BEFORE the route, in the Edge runtime by default

Limits: Edge runtime has no full Node.js APIs; keep the code small and fast
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Project root में (app/ के बगल में, या src/ के अंदर) middleware.js (या .ts) बनाओ
Step 2 → function middleware(request) export करो (Next.js 16 में file का नाम proxy.js हो गया; version-dependent)
Step 3 → request.nextUrl, request.cookies, request.headers देखो
Step 4 → आगे जाने के लिए NextResponse.next(), कहीं और भेजने के लिए redirect(),
         उसी URL पर अलग content दिखाने के लिए rewrite(), या रोकने के लिए Response return करो
Step 5 → config.matcher export करके तय करो कि middleware किन paths पर चले
Step 6 → हर matched request पर route से पहले चलता है, default में Edge runtime में

सीमा: Edge runtime में पूरे Node.js APIs नहीं मिलते; code छोटा और तेज़ रखो
```

---

## 🟡 Real World Example
**Amazon India vs US:** A visitor from India opens `amazon.com`. Middleware reads the `x-vercel-ip-country` header (provided by the hosting platform) and redirects to the India storefront. Logged-out users who open `/your-orders` are redirected to `/login?next=/your-orders` before any page code runs. A/B test buckets are assigned by setting a cookie once.

## 🟡 Real Example Hindi mein
**Amazon India vs US:** भारत से कोई `amazon.com` खोलता है। Middleware hosting platform द्वारा दिया गया `x-vercel-ip-country` header पढ़ता है और India storefront पर redirect कर देता है। Logged-out user जब `/your-orders` खोलता है तो page code चलने से पहले ही उसे `/login?next=/your-orders` पर भेज दिया जाता है। A/B test का bucket एक बार cookie set करके तय होता है।

---

## 💻 Code Example — Basic

```jsx
// middleware.js (project root, same level as app/)
import { NextResponse } from 'next/server';            // response helpers

export function middleware(request) {                  // runs before matched routes
  const token = request.cookies.get('token')?.value;   // read the auth cookie
  const { pathname } = request.nextUrl;                // current path, e.g. /orders

  if (!token) {                                        // user not logged in
    const loginUrl = new URL('/login', request.url);   // build absolute login URL
    loginUrl.searchParams.set('next', pathname);       // remember where they wanted to go
    return NextResponse.redirect(loginUrl);            // 307 redirect to /login
  }

  return NextResponse.next();                          // logged in: continue to the page
}

export const config = {
  matcher: ['/orders/:path*', '/profile/:path*'],      // only run on these paths
};
```

## 💻 Code Example — Advanced

```jsx
// middleware.js: auth + geo redirect + A/B cookie + security headers
import { NextResponse } from 'next/server';

const PUBLIC_PATHS = ['/login', '/signup', '/about'];  // pages anyone can open

export function middleware(request) {
  const { pathname } = request.nextUrl;                // path of this request
  const res = NextResponse.next();                     // start from "continue"

  // 1) Geo redirect (header is set by Vercel; other hosts differ)
  const country = request.headers.get('x-vercel-ip-country');
  if (pathname === '/' && country === 'IN') {          // Indian visitors on the home page
    return NextResponse.rewrite(new URL('/in', request.url)); // show /in content, URL stays /
  }

  // 2) Auth guard for private pages
  const isPublic = PUBLIC_PATHS.some(p => pathname.startsWith(p));
  const token = request.cookies.get('token')?.value;
  if (!isPublic && !token && pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  // 3) A/B test bucket: assign once, keep in a cookie
  if (!request.cookies.has('bucket')) {
    const bucket = Math.random() < 0.5 ? 'A' : 'B';    // 50/50 split
    res.cookies.set('bucket', bucket, { maxAge: 60 * 60 * 24 * 30 }); // 30 days
  }

  // 4) Security header for every response
  res.headers.set('X-Frame-Options', 'DENY');          // block clickjacking

  return res;                                          // continue with modified response
}

export const config = {
  // Skip static files, images and Next internals so middleware stays cheap
  matcher: ['/((?!_next/static|_next/image|favicon.ico|.*\\.(?:png|jpg|svg)$).*)'],
};
```

---

## 🟠 Real App Integration

Middleware should only do a cheap check (cookie exists, token shape). Do the real authorization (is this user allowed to see this order?) in the page, Route Handler or Server Action. In 2025, a Next.js middleware auth-bypass vulnerability (CVE-2025-29927) showed that middleware must not be the only line of defense.

```jsx
// app/dashboard/page.jsx (Server Component): second layer of defense
import { cookies } from 'next/headers';                 // server cookie access
import { redirect } from 'next/navigation';             // server redirect helper
import { verifySession } from '@/lib/session';          // your real verification (hypothetical)

export default async function Dashboard() {
  const token = (await cookies()).get('token')?.value;  // Next.js 15+: cookies() is async
  const user = token ? await verifySession(token) : null; // real check, not just "exists"
  if (!user) redirect('/login');                        // never trust middleware alone
  return <h1>Welcome {user.name}</h1>;                  // protected content
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** No `matcher`, so middleware runs on every image, script and font request
✅ **Correct:** Limit it with `config.matcher`

```jsx
// Wrong: runs for /_next/static/*, images, favicon (slow and wasteful)
export function middleware(request) { /* ... */ }      // ❌ no config

// Right: only run where needed
export const config = { matcher: ['/dashboard/:path*'] }; // ✅
```

❌ **Mistake 2:** Using Node-only libraries (fs, some JWT/DB drivers) inside middleware
✅ **Correct:** Use Edge-compatible code (for example `jose` for JWT) and keep DB calls out

```jsx
// Wrong: Prisma / fs in the Edge runtime fails or bloats the bundle
import fs from 'fs';                                    // ❌ not available on Edge
import { PrismaClient } from '@prisma/client';          // ❌ not for middleware (version-dependent)

// Right: verify a signed token with an Edge-safe library
import { jwtVerify } from 'jose';                       // ✅ works on Edge
const { payload } = await jwtVerify(token, new TextEncoder().encode(process.env.JWT_SECRET));
```

---

## 🧠 Tricky Interview Question

```jsx
// middleware.js
import { NextResponse } from 'next/server';
export function middleware(request) {
  if (request.nextUrl.pathname === '/login') {
    return NextResponse.redirect(new URL('/login', request.url));
  }
  return NextResponse.next();
}
// no config.matcher
```
**Answer:** This creates an infinite redirect loop. A request to `/login` is redirected to `/login`, which hits the middleware again, and so on; the browser stops with "too many redirects" (ERR_TOO_MANY_REDIRECTS). The fix is to redirect only when a condition is false (for example "no token") and to exclude the target path, either by checking `pathname` or with a `matcher`. Also, because there is no matcher, it would run on static assets too.

---

## ⚫ Interview Questions + Answers

Q1: What is Middleware in Next.js and when does it run?
A1: A function in `middleware.js` at the project root that runs on the server (Edge runtime by default) before a matched request is completed, before rendering and before the cache is checked.

Q2: What can middleware do?
A2: Redirect, rewrite, set or read cookies and headers, return a response directly (for example 401 JSON), and continue with `NextResponse.next()`.

Q3: What is the difference between redirect and rewrite?
A3: A redirect tells the browser to go to a new URL (the address bar changes). A rewrite serves content from a different path while the address bar keeps the original URL (used for A/B tests, locales, proxies).

Q4: How do you limit which routes use middleware?
A4: With `export const config = { matcher: [...] }`, which accepts path patterns and regex, or with manual `pathname` checks inside the function.

Q5: Is middleware enough to secure a page?
A5: No. Use it as a fast first filter. Always verify authorization again in the data layer, Route Handler or Server Action, because middleware can be bypassed through bugs or misconfiguration (see CVE-2025-29927).

---

## 🔷 When to Use + When Not to Use
✅ **Use middleware when:**
- Redirecting unauthenticated users early
- Locale or geo routing, A/B tests with cookies
- Adding headers (security, tracing) to many routes

❌ **Avoid middleware when:**
- You need heavy work (DB queries, large libraries); it hurts latency on every request
- You need fine-grained permission checks (do them in the data layer)
- A single page needs the check (put it in that page)

---

## 📊 Visual Diagram

```
  Browser request: GET /dashboard
        │
        ▼
  ┌────────────────────────┐
  │ middleware.js (Edge)   │  matcher says: runs for /dashboard
  │  no token?  ───────────┼──► redirect → /login
  │  has token? ───────────┤
  └───────────┬────────────┘
              ▼ NextResponse.next()
        Cache lookup → Page render (Server Component) → HTML

  Re-render behavior: middleware is NOT a React component, it never re-renders.
  It runs fresh on every matched request.
  Performance: it adds latency to every matched request, so keep it tiny and
  use matcher to skip static files.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Middleware | Code that runs before the route | Route से पहले चलने वाला code |
| matcher | Config listing paths for middleware | Middleware के paths की list |
| NextResponse.next() | Continue to the route | आगे route पर जाने दो |
| redirect | Send browser to a new URL | Browser को नए URL पर भेजना |
| rewrite | Show other content, same URL | उसी URL पर अलग content |
| Edge runtime | Lightweight JS runtime near users | Users के पास का हल्का runtime |
| Cookie | Small data stored in the browser | Browser में रखा छोटा data |
| Redirect loop | Redirects that never end | कभी खत्म न होने वाले redirects |

---

## ⚡ 3-Line Summary
**English:**
1. Middleware runs before a request reaches the route, and can redirect, rewrite, set headers or cookies.
2. Use `matcher` and keep it light, because it runs on the Edge for many requests.
3. It is a first filter only; verify real authorization in your data layer.

**Hindi:**
1. Middleware request के route तक पहुँचने से पहले चलता है, और redirect, rewrite, headers या cookies set कर सकता है।
2. `matcher` इस्तेमाल करो और इसे हल्का रखो, क्योंकि यह Edge पर कई requests पर चलता है।
3. यह सिर्फ पहला filter है; असली authorization अपनी data layer में verify करो।

---

## ➡️ Next Topic
**178. Next.js Image Optimization** — `next/image` कैसे images को resize, compress, lazy-load करती है, और layout shift (CLS) से कैसे बचाती है।
