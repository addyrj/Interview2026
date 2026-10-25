# 113. Serving Static Files
# हिंदी में: Static Files Serve करना

---

## 🔵 Simple Definition (English)
`express.static()` is built-in Express middleware that serves static assets (HTML, CSS, JS, images, fonts) directly from a specified directory on disk, matching request URLs to file paths automatically — no custom route needed per file.

## 🔵 सरल परिभाषा (Hindi)
`express.static()` एक built-in Express middleware है जो static assets (HTML, CSS, JS, images, fonts) को disk पर दी गई directory से directly serve करता है, request URLs को automatically file paths से match करता है — हर file के लिए custom route की ज़रूरत नहीं।

---

## 🔴 Problem it Solves
Without `express.static()`, you'd need to write a separate route handler for every single static file (`app.get('/style.css', (req, res) => res.sendFile(...))`) — completely impractical for a site with hundreds of images, JS bundles, and CSS files. `express.static()` maps an entire directory tree to a URL prefix in one line, automatically handling content-type detection, caching headers, range requests (for video seeking), and directory traversal security.

## 🔴 यह क्यों बना? (Hindi)
`express.static()` के बिना, हर single static file के लिए अलग route handler लिखना पड़ता (`app.get('/style.css', ...)`) — सैकड़ों images, JS bundles, CSS files वाली site के लिए completely impractical। `express.static()` पूरी directory tree को एक URL prefix से map करता है एक line में, automatically content-type detection, caching headers, range requests (video seeking के लिए), और directory traversal security handle करता है।

---

## 🟢 How it Works — Step by Step

Step 1 → `app.use(express.static('public'))` registers middleware that checks incoming request paths against files in the `public` directory.
Step 2 → For a request like `GET /logo.png`, Express looks for `public/logo.png` on disk.
Step 3 → If found, it streams the file content with appropriate `Content-Type` (based on file extension) and `Content-Length` headers, plus caching headers (`ETag`, `Last-Modified`, optionally `Cache-Control` via options).
Step 4 → If not found, `express.static()` calls `next()`, passing control to the next middleware/route (so it doesn't swallow requests meant for other handlers — e.g., API routes).
Step 5 → Built-in protection prevents directory traversal attacks (e.g., `GET /../../etc/passwd` is blocked/normalized, can't escape the configured root directory).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `app.use(express.static('public'))` एक middleware register करता है जो incoming request paths को `public` directory की files से check करता है।
Step 2 → `GET /logo.png` जैसी request के लिए, Express disk पर `public/logo.png` ढूंढता है।
Step 3 → अगर मिल जाए, ये file content को appropriate `Content-Type` (file extension के आधार पर) और `Content-Length` headers के साथ stream करता है, साथ caching headers (`ETag`, `Last-Modified`, optionally `Cache-Control`) भी।
Step 4 → अगर नहीं मिलती, `express.static()` `next()` call करता है, control आगे के middleware/route को pass करता है (ताकि दूसरे handlers के लिए meant requests को swallow न करे — जैसे API routes)।
Step 5 → Built-in protection directory traversal attacks रोकता है (जैसे `GET /../../etc/passwd` block/normalize हो जाता है, configured root directory से बाहर नहीं जा सकता)।

---

## 🟡 Real World Example
**Paytm merchant dashboard:** The static frontend (React build output — `index.html`, `main.[hash].js`, `main.[hash].css`) is served via `app.use(express.static(path.join(__dirname, 'build')))`. Paytm sets long `Cache-Control: max-age=31536000, immutable` on hashed JS/CSS bundles (filenames change on every deploy due to content hashing, so caching forever is safe), but short/no-cache on `index.html` (so users always get the latest app shell pointing to the newest bundle hashes). This static-serving setup, combined with a catch-all route serving `index.html` for client-side routing (SPA fallback), lets the Express backend serve both the API (`/api/*`) and the frontend app from a single server.

## 🟡 Real Example Hindi mein
**Paytm merchant dashboard:** Static frontend (React build output — `index.html`, `main.[hash].js`, `main.[hash].css`) `app.use(express.static(path.join(__dirname, 'build')))` से serve होता है। Paytm hashed JS/CSS bundles पर long `Cache-Control: max-age=31536000, immutable` set करता है (filenames हर deploy पर content hashing के कारण बदलते हैं, तो forever cache करना safe है), लेकिन `index.html` पर short/no-cache (ताकि users को हमेशा नया app shell मिले जो नए bundle hashes को point करता हो)। ये static-serving setup, catch-all route (जो SPA fallback के लिए `index.html` serve करता है) के साथ combine होकर, एक ही Express server से API (`/api/*`) और frontend app दोनों serve करने देता है।

---

## 💻 Code Example — Basic

```javascript
// static-basic.js
const express = require('express');
const path = require('path');

const app = express();

// Serve everything in the 'public' folder at the root URL path
// e.g., public/style.css becomes accessible at http://localhost:3000/style.css
app.use(express.static(path.join(__dirname, 'public')));

app.get('/api/status', (req, res) => {
  res.json({ status: 'ok' }); // API routes still work alongside static serving
});

app.listen(3000, () => {
  console.log('Server on port 3000 — place files in ./public to serve them');
});
```

## 💻 Code Example — Advanced

```javascript
// static-advanced.js — Multiple static dirs, caching, SPA fallback
const express = require('express');
const path = require('path');

const app = express();

// ─── 1. SERVE UPLOADED USER CONTENT with a URL prefix ─────────────────────────
// Files in ./uploads become accessible at /media/<filename>, not /uploads/<filename>
app.use(
  '/media',
  express.static(path.join(__dirname, 'uploads'), {
    maxAge: '1d', // Cache-Control: max-age=86400 for user-uploaded images
    etag: true, // enable ETag for conditional requests (304 Not Modified)
  })
)

// ─── 2. SERVE HASHED BUNDLE FILES with aggressive long-term caching ───────────
app.use(
  '/static',
  express.static(path.join(__dirname, 'build/static'), {
    maxAge: '1y', // 1 year — safe because filenames include content hash
    immutable: true, // tells browser the file will NEVER change at this URL
  })
)

// ─── 3. SERVE THE REST OF THE BUILD OUTPUT (index.html etc) without long cache
app.use(
  express.static(path.join(__dirname, 'build'), {
    index: false, // don't auto-serve index.html here; we handle it explicitly below
  })
)

// ─── 4. API ROUTES mounted before the SPA fallback ────────────────────────────
app.get('/api/products', (req, res) => {
  res.json({ products: [] });
});

// ─── 5. SPA FALLBACK — any non-API, non-static route serves index.html ───────
// React Router / client-side routing needs this so refreshing on /dashboard works
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'build', 'index.html'), {
    headers: { 'Cache-Control': 'no-cache' }, // always fetch latest app shell
  });
});

app.listen(3000, () => console.log('Production-style static server running on port 3000'));
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const path = require('path');
const app = express();

// Typical real-world structure: API first, then static fallback
app.use('/api', require('./routes/api')); // all API logic isolated under /api

app.use(express.static(path.join(__dirname, 'public'), {
  maxAge: '7d',
  setHeaders: (res, filePath) => {
    // Custom header logic per file type
    if (filePath.endsWith('.html')) {
      res.setHeader('Cache-Control', 'no-cache'); // HTML should always revalidate
    }
  },
}));

app.listen(5000, () => console.log('App with API + static assets running on port 5000'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Mounting `express.static()` AFTER routes that should take priority, causing unexpected fallthrough behavior, or BEFORE API routes causing static 404s to never reach API handlers in edge cases
✅ Correct: Order matters — generally put API routes first (or on a distinct prefix like `/api`) and static serving after, or use distinct URL prefixes to avoid ambiguity.

```javascript
// Risky — static mounted at root alongside API at root; a file named 'users' in public/
// could shadow an intended /users API route if not careful with prefixes
app.use(express.static('public'));
app.get('/users', apiHandler);

// Safer — distinct prefix removes ambiguity entirely
app.use('/static', express.static('public'));
app.get('/api/users', apiHandler);
```

❌ Mistake 2: Serving sensitive files accidentally by pointing `express.static()` at the wrong (too broad) directory
✅ Correct: Only point it at a dedicated public assets folder — never at the project root, which could expose `.env`, `node_modules`, or server source code.

```javascript
// Wrong — serves the ENTIRE project directory, including .env, package.json, source code!
app.use(express.static(__dirname));

// Right — only the intended public assets folder
app.use(express.static(path.join(__dirname, 'public')));
```

---

## 🧠 Tricky Interview Question

```javascript
const express = require('express');
const path = require('path');
const app = express();

app.use(express.static(path.join(__dirname, 'public')));
app.get('/about', (req, res) => res.send('About page from route handler'));

app.listen(3000);
// public/about.html exists on disk!
```
If a client requests `GET /about`, which response do they get — the static `about.html` file or the route handler's "About page from route handler" text?

Answer: It depends on exact matching — `express.static()` looks for a file matching the EXACT path `/about` (not `/about.html` unless `extensions` option is configured to try `.html`). By default, `express.static()` does NOT automatically append `.html` to bare paths (that requires setting `extensions: ['html']` in the static options). So `GET /about` with no extension would NOT match `public/about.html` by default — `express.static()` calls `next()` since no exact file `public/about` exists, and the request falls through to the route handler, returning "About page from route handler". If `extensions: ['html']` were configured, the static middleware (registered first) WOULD match and serve `about.html`, and the route handler would never run (middleware order — static is registered before the route).

---

## ⚫ Interview Questions + Answers

Q1: Does `express.static()` return a 404 directly if a file isn't found?
A1: No — if the requested file doesn't exist in the configured directory, `express.static()` simply calls `next()`, passing control to the next middleware or route handler in the chain. It only sends a response (the file) when a match IS found. This is important because it lets you stack static serving with API routes or a custom 404 handler further down the chain.

Q2: How do you set cache headers differently for different types of static files?
A2: Use the `setHeaders` option (a callback receiving `res` and `filePath`) to apply conditional logic, or mount multiple `express.static()` instances at different path prefixes each with their own `maxAge`/`immutable` options — e.g., long cache + immutable for hashed JS/CSS bundles, short/no-cache for `index.html` or frequently-changing assets.

Q3: What security risk does `express.static()` protect against by default, and how?
A3: Directory traversal attacks — a malicious request like `GET /../../../etc/passwd` attempting to escape the configured static root and read arbitrary server files. `express.static()` (via the underlying `send` library) normalizes and validates the resolved path, rejecting any request that would resolve outside the configured root directory, returning a 403/404 instead.

Q4: What's the difference between serving static files via Express vs. via a CDN/Nginx in production?
A4: Express serving static files consumes Node.js process resources (CPU, event loop) for every static request, competing with your actual application logic — fine for small apps/development, but inefficient at scale. In production, it's standard to offload static asset serving to a CDN (CloudFront, Cloudflare) or reverse proxy (Nginx) which is purpose-built for high-throughput static file serving, freeing the Node.js process to focus solely on dynamic API/business logic.

Q5: How would you implement a Single Page Application (SPA) fallback route alongside `express.static()`?
A5: Serve the build output directory with `express.static()` for actual file matches (JS, CSS, images), then add a catch-all route (`app.get('*', ...)` placed AFTER all API routes and static middleware) that always responds with `index.html`. This ensures client-side routes like `/dashboard` or `/profile/123` (which don't correspond to real files) still load the SPA shell, letting the frontend router (React Router, Vue Router) take over and render the correct view.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Serving a frontend build output, images, documents, or any fixed assets from your Express app
- Small-to-medium apps where a separate CDN/static hosting setup is overkill
- Need SPA fallback behavior combined with API routes in one server

❌ Avoid when:
- High-traffic production apps where offloading to a CDN/Nginx/S3+CloudFront would significantly reduce load on the Node.js process and improve latency (static assets served geographically closer to users)
- Serving large media files (videos) at scale — dedicated streaming/CDN infrastructure handles range requests and bandwidth far more efficiently

---

## 📊 Visual Diagram
```
STATIC FILE SERVING FLOW:

  GET /logo.png
       │
       ▼
  express.static('public')
       │
       ├── public/logo.png exists? ──Yes──▶ stream file + headers ──▶ 200 OK
       │
       └── Not found? ──▶ next() ──▶ falls through to next middleware/route
                                           │
                                           ▼
                                   (API route / 404 handler)

DIRECTORY STRUCTURE:
  project/
  ├── public/          ◀── express.static(path.join(__dirname, 'public'))
  │   ├── logo.png      → GET /logo.png
  │   ├── style.css      → GET /style.css
  │   └── index.html     → GET / (default index file)
  └── server.js
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| express.static | Built-in static file serving middleware | Static file serving middleware |
| Content-Type | Header indicating file's MIME type | File के MIME type वाला header |
| ETag | Caching validator for conditional requests | Caching validator header |
| Cache-Control | Header controlling browser caching behavior | Browser caching control header |
| Directory traversal | Attack to access files outside root | Root के बाहर files access करने का attack |
| SPA fallback | Serving index.html for all unmatched routes | Unmatched routes पर index.html serve करना |

---

## ⚡ 3-Line Summary
English:
1. `express.static()` serves an entire directory of assets from one URL prefix, auto-handling content-type, caching, and directory-traversal security.
2. It calls `next()` on a miss rather than 404ing directly, so it stacks cleanly with API routes and SPA fallback handlers.
3. In production at scale, prefer offloading static serving to a CDN/Nginx, keeping Node.js focused on dynamic logic.

Hindi:
1. `express.static()` एक पूरी directory को एक URL prefix से serve करता है, content-type, caching, और directory-traversal security automatically handle करता है।
2. File न मिलने पर ये directly 404 नहीं भेजता, `next()` call करता है, तो API routes और SPA fallback handlers के साथ cleanly stack होता है।
3. Production scale पर, static serving CDN/Nginx को offload करना बेहतर है, Node.js को dynamic logic पर focused रखो।

---

## ➡️ Next Topic
**114. Template Engines (EJS, Pug)** — Server-side HTML rendering with dynamic data in Express।
