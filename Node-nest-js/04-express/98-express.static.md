# 98. express.static()
# हिंदी में: express.static()

---

## 🔵 Simple Definition (English)
`express.static(root)` is built-in middleware that serves static files (HTML, CSS, JS, images, fonts) directly from a directory on disk. It automatically handles `Content-Type` detection, caching headers (`ETag`, `Last-Modified`), range requests (for video/audio streaming), and directory index files.

## 🔵 सरल परिभाषा (Hindi)
`express.static(root)` built-in middleware है जो static files (HTML, CSS, JS, images, fonts) को directly disk के एक directory से serve करता है। यह automatically `Content-Type` detect करता है, caching headers (`ETag`, `Last-Modified`) handle करता है, range requests (video/audio streaming के लिए) और directory index files भी handle करता है।

---

## 🔴 Problem it Solves
```
WITHOUT express.static():
  app.get('/style.css', (req, res) => {
    const fs = require('fs');
    const css = fs.readFileSync('./public/style.css');  // manual file read
    res.set('Content-Type', 'text/css');                 // manual content-type
    res.send(css);
    // Still missing: caching headers, 304 Not Modified handling,
    // range requests for video, directory listing, 404 for missing files...
  });
  → You'd need a route for EVERY file, with manual MIME type mapping

WITH express.static():
  app.use(express.static('public'));
  → ANY file in 'public/' is automatically served at its relative path
  → public/style.css   → GET /style.css
  → public/images/a.jpg → GET /images/a.jpg
  → Full caching, MIME detection, range support — all handled
```

## 🔴 यह क्यों बना? (Hindi)
बिना `express.static()` के, हर static file के लिए अलग route manually बनाना पड़ता, MIME type manually set करना पड़ता, caching/range requests खुद implement करने पड़ते — बहुत बड़ा काम। Express ने यह सब एक middleware में automate कर दिया, जो directory के किसी भी file को उसके relative path पर serve कर देता है।

---

## 🟢 How it Works — Step by Step

Step 1 → `express.static(root)` creates middleware bound to a specific directory (`root`)
Step 2 → For each incoming GET/HEAD request, it maps the URL path onto a file path inside `root` (e.g., `/images/logo.png` → `root/images/logo.png`)
Step 3 → It checks if that file exists; if yes, it determines MIME type from the file extension, sets headers (`Content-Type`, `Content-Length`, `ETag`, `Last-Modified`, `Cache-Control`), and streams the file content as the response
Step 4 → If the client sends `If-None-Match`/`If-Modified-Since` headers matching the cached `ETag`/`Last-Modified`, it responds `304 Not Modified` with NO body (saves bandwidth)
Step 5 → If the file doesn't exist, it calls `next()` — the request continues down the middleware chain instead of immediately returning 404

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `express.static(root)` एक specific directory (`root`) से bound middleware बनाता है
Step 2 → हर GET/HEAD request के लिए URL path को `root` के अंदर file path में map करता है
Step 3 → File exist करे तो MIME type decide करता है, headers set करता है (`Content-Type`, `ETag`, `Last-Modified`, `Cache-Control`), और content stream करता है
Step 4 → Client अगर matching `If-None-Match`/`If-Modified-Since` भेजे, तो `304 Not Modified` बिना body भेजता है (bandwidth बचता है)
Step 5 → File नहीं मिली तो `next()` call करता है — request chain में आगे जाता है, immediately 404 नहीं होता

---

## 🟡 Real World Example
**Swiggy restaurant images & menu PDFs:** `app.use('/static', express.static('public'))` serves restaurant logos, food photos, and downloadable menu PDFs directly from disk with `Cache-Control: max-age=86400` (1 day) so repeat visitors don't re-download unchanged images. Browsers send conditional requests (`If-None-Match`) on revisits, and the server responds `304 Not Modified` instantly instead of resending the whole image — saving bandwidth at Swiggy's scale (millions of daily app opens).

## 🟡 Real Example Hindi mein
**Swiggy restaurant images & menu PDFs:** `app.use('/static', express.static('public'))` restaurant logos, food photos, menu PDFs को disk से directly serve करता है `Cache-Control: max-age=86400` के साथ। Browsers revisit पर `If-None-Match` भेजते हैं, और server `304 Not Modified` instantly respond करता है — bandwidth बचता है Swiggy के scale पर।

---

## 💻 Code Example — Basic

```javascript
// static-basic.js
const express = require('express');
const app = express();

// Serve everything in 'public/' directly at the root URL
// Folder structure: public/index.html, public/style.css, public/images/logo.png
app.use(express.static('public'));

// GET /                 → serves public/index.html (default index file)
// GET /style.css        → serves public/style.css
// GET /images/logo.png  → serves public/images/logo.png

app.listen(3000, () => console.log('Server on 3000 — visit http://localhost:3000'));
```

## 💻 Code Example — Advanced

```javascript
// static-advanced.js — mount path, options, multiple directories

const express = require('express');
const path = require('path');
const app = express();

// Mount static files under a URL PREFIX (not at root)
// public/logo.png becomes accessible at /assets/logo.png (not /logo.png)
app.use('/assets', express.static(path.join(__dirname, 'public'), {
  maxAge: '7d',             // Cache-Control: max-age=604800 (7 days)
  etag: true,                // send ETag for conditional caching (default: true)
  lastModified: true,        // send Last-Modified header (default: true)
  index: false,              // disable serving index.html for directory requests
  dotfiles: 'ignore',        // 'allow' | 'deny' | 'ignore' — how to treat files starting with '.'
  setHeaders: (res, filePath) => {
    // custom header logic per file
    if (filePath.endsWith('.pdf')) {
      res.set('Content-Disposition', 'inline');  // open PDF in browser, not download
    }
  },
}));

// Serve user-uploaded files from a SEPARATE directory with different caching rules
app.use('/uploads', express.static(path.join(__dirname, 'uploads'), {
  maxAge: '1h',   // uploaded content changes more often — shorter cache
}));

// Fallback: anything not matched by static or routes gets a proper 404 JSON response
app.use((req, res) => {
  res.status(404).json({ error: `File not found: ${req.path}` });
});

app.listen(3000, () => console.log('Server on 3000'));
```

---

## 🟠 Express.js Integration

```javascript
// Real-world: serving a React SPA build alongside an API
const express = require('express');
const path = require('path');
const app = express();

// Serve API routes FIRST
app.use('/api/orders', require('./routes/orders'));

// Serve the built React app's static assets (JS/CSS bundles)
app.use(express.static(path.join(__dirname, 'client/build')));

// For any non-API route, serve index.html (client-side routing support — SPA fallback)
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'client/build', 'index.html'));
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Serving sensitive files accidentally because the static root is too broad
```javascript
// WRONG: serving the ENTIRE project root exposes .env, node_modules, server code!
app.use(express.static('.'));   // ❌ anyone can GET /.env or /server.js

// CORRECT: scope the static root to a dedicated public-only folder
app.use(express.static('public'));  // only files intentionally placed in public/
```

❌ **Mistake 2:** Expecting `express.static()` to return a 404 immediately when a file is missing
```javascript
// WRONG assumption: thinking static middleware ends the chain on a miss
app.use(express.static('public'));
// (no fallback 404 handler) → unmatched requests may hang if no later route/middleware handles them

// CORRECT: always add a final catch-all handler after static + routes
app.use(express.static('public'));
app.use('/api', apiRouter);
app.use((req, res) => res.status(404).json({ error: 'Not found' }));  // explicit fallback
```

---

## 🧠 Tricky Interview Question

```javascript
const express = require('express');
const app = express();

app.use(express.static('public'));   // public/report.pdf exists

app.get('/report.pdf', (req, res) => {
  res.json({ message: 'This is the API route, not the file!' });
});

app.listen(3000);
// GET /report.pdf → file or JSON response?
```
Answer: The FILE (`public/report.pdf`) is served, NOT the JSON response. Because `express.static()` is registered BEFORE the `/report.pdf` route, and it finds a matching file on disk, it immediately serves that file and ends the response — it never calls `next()` in that case, so the later route handler never executes. To make the API route win instead, you'd need to register `app.get('/report.pdf', ...)` BEFORE `app.use(express.static('public'))`.

---

## ⚫ Interview Questions + Answers

Q1: What happens when `express.static()` can't find a matching file for the request path?
A1: It calls `next()`, passing control to the next middleware/route in the chain — it does NOT immediately send a 404. This design allows `express.static()` to safely coexist with API routes: if a URL doesn't correspond to a static file, the request simply continues down the chain to be handled by your actual routes (or eventually your fallback 404 handler).

Q2: How do `ETag` and `Last-Modified` headers enable efficient caching with `express.static()`?
A2: On first request, the server sends `ETag` (a hash/fingerprint of file content) and `Last-Modified` (file's modification timestamp) headers along with the file. On SUBSEQUENT requests, the browser sends `If-None-Match` (with the cached ETag) or `If-Modified-Since` headers. If the file hasn't changed, the server responds `304 Not Modified` with NO body — the browser uses its cached copy, saving bandwidth and server processing.

Q3: How do you mount static files under a URL prefix different from the actual folder name?
A3: Pass a path as the first argument to `app.use()`: `app.use('/assets', express.static('public'))`. Now files in the `public/` folder are accessible under `/assets/...` in the URL (e.g., `public/logo.png` → `GET /assets/logo.png`), decoupling the URL structure from your actual disk layout.

Q4: What's a security risk of calling `express.static()` with too broad a root directory, and how do you avoid it?
A4: If you point it at your project root (`.`) instead of a dedicated public folder, you risk exposing sensitive files like `.env` (secrets), `package.json`, server source code, or `node_modules` to anyone who guesses the URL. Always use a DEDICATED directory (e.g., `public/`) that contains ONLY files meant for public access, and never put secrets or source code inside it.

Q5: Can `express.static()` handle range requests, and why does that matter?
A5: Yes — it supports the `Range` HTTP header, which lets clients request PARTIAL content (e.g., bytes 1000-2000 of a video file). This is essential for video/audio streaming and allows browsers to seek within a media file without downloading the entire thing first, and supports resumable downloads if a connection drops midway.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Serving CSS/JS bundles, images, fonts, downloadable files for a small-to-medium app directly from your server
- Local development or simple deployments where a CDN isn't set up yet

❌ Avoid when:
- Serving large-scale media/assets in production — use a CDN (CloudFront, Cloudflare) or object storage (S3) instead; Express serving from local disk doesn't scale as well and ties bandwidth/CPU to your app servers
- Serving sensitive files — never point `express.static()` at a directory containing secrets or server code

---

## 📊 Visual Diagram
```
  express.static() REQUEST FLOW
  ────────────────────────────────────────────
  GET /images/pizza.jpg
       │
       ▼
  express.static('public')
       │
       ▼
  Check: does 'public/images/pizza.jpg' exist?
       │
    ┌──┴──┐
   YES    NO
    │       │
    ▼       ▼
  Set headers:        next() → continue to
  Content-Type,       next middleware/route
  ETag, Cache-Control
    │
    ▼
  Stream file as response
  (chain ends here)

  Repeat visit with If-None-Match header matching ETag:
    → respond 304 Not Modified (no body, fast)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Static file | File served as-is (no processing) | बिना processing serve होने वाली file |
| `ETag` | Content fingerprint for caching | Content का fingerprint caching के लिए |
| `304 Not Modified` | Response meaning "use your cache" | "अपना cache use करो" का response |
| Range request | Partial content request (streaming) | Partial content request (streaming) |
| Mount path | URL prefix for static files | Static files का URL prefix |

---

## ⚡ 3-Line Summary
English: 1. `express.static(root)` serves files from a directory automatically, handling MIME types, caching headers, and range requests. 2. If a file isn't found, it calls `next()` instead of 404ing — safe to combine with API routes. 3. Never point it at a directory containing secrets or source code; always use a dedicated public folder.
Hindi: 1. `express.static(root)` directory से files automatically serve करता है, MIME types, caching, range requests handle करता है। 2. File न मिले तो `next()` call करता है, 404 नहीं — API routes के साथ safely combine हो सकता है। 3. कभी secrets या source code वाली directory पर इसे point मत करो।

---

## ➡️ Next Topic
**99. Router — Express Router** — Modular, mountable route handlers using `express.Router()`.
