# 110. Cookie Parser
# हिंदी में: Cookie Parser — Request से Cookies पढ़ना

---

## 🔵 Simple Definition (English)
**cookie-parser** is Express middleware that parses the `Cookie` header from incoming requests and populates `req.cookies` (and `req.signedCookies` for signed cookies) as a JavaScript object, so route handlers can easily read cookie values without manually parsing the raw header string.

## 🔵 सरल परिभाषा (Hindi)
**cookie-parser** एक Express middleware है जो incoming requests के `Cookie` header को parse करता है और `req.cookies` (और signed cookies के लिए `req.signedCookies`) को एक JavaScript object की तरह populate करता है, ताकि route handlers raw header string को manually parse किए बिना cookie values आसानी से पढ़ सकें।

---

## 🔴 Problem it Solves
The raw `Cookie` HTTP header is a single string like `session_id=abc123; theme=dark; lang=en` — parsing this manually (splitting by `;`, then `=`, trimming whitespace, URL-decoding values) in every route is repetitive and error-prone. Also, without signature verification, a client could tamper with a cookie value (e.g., change `isAdmin=false` to `isAdmin=true` if such a cookie existed) and the server would have no way to detect it. cookie-parser solves both: automatic parsing into a clean object, and optional HMAC signing/verification to detect tampering.

## 🔴 यह क्यों बना? (Hindi)
Raw `Cookie` HTTP header एक single string होता है जैसे `session_id=abc123; theme=dark; lang=en` — इसे manually parse करना (`;` से split, फिर `=`, whitespace trim, values URL-decode) हर route में repetitive और error-prone है। साथ ही, signature verification के बिना, client cookie value के साथ tamper कर सकता है (जैसे `isAdmin=false` को `isAdmin=true` में बदलना अगर ऐसी cookie होती) और server को पता नहीं चलेगा। cookie-parser दोनों solve करता है: automatic parsing एक clean object में, और optional HMAC signing/verification tampering detect करने के लिए।

---

## 🟢 How it Works — Step by Step

Step 1 → Client sends request with `Cookie: session_id=abc123; theme=dark` header (browser automatically attaches cookies set earlier via `Set-Cookie`).
Step 2 → `cookieParser(secret)` middleware reads `req.headers.cookie`.
Step 3 → It splits the string into key-value pairs and URL-decodes each value, populating `req.cookies = { session_id: 'abc123', theme: 'dark' }`.
Step 4 → If a `secret` is provided and a cookie was signed (via `res.cookie(name, value, { signed: true })`), cookie-parser verifies the HMAC signature; valid signed cookies go into `req.signedCookies`, tampered ones are set to `false`.
Step 5 → Route handlers read `req.cookies.session_id` directly — no manual string parsing needed.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Client request में `Cookie: session_id=abc123; theme=dark` header भेजता है (browser पहले `Set-Cookie` से set की cookies automatically attach करता है)।
Step 2 → `cookieParser(secret)` middleware `req.headers.cookie` पढ़ता है।
Step 3 → ये string को key-value pairs में split करता है और हर value URL-decode करता है, `req.cookies = { session_id: 'abc123', theme: 'dark' }` populate करता है।
Step 4 → अगर `secret` दिया गया है और कोई cookie signed है (`res.cookie(name, value, { signed: true })` से), cookie-parser HMAC signature verify करता है; valid signed cookies `req.signedCookies` में जाती हैं, tampered वाली `false` हो जाती हैं।
Step 5 → Route handlers directly `req.cookies.session_id` पढ़ते हैं — manual string parsing की ज़रूरत नहीं।

---

## 🟡 Real World Example
**Amazon.in "Recently Viewed" feature:** When browsing products without logging in, Amazon sets a cookie `recently_viewed=B08L5V,B09K3L,B07X9M` (comma-separated product IDs). Every page load, `cookie-parser` reads this cookie from the request so the server can render the "Recently Viewed" carousel. For the `cart_session` cookie (tracking an anonymous cart), Amazon signs it with a secret — if a user tried to tamper with the cookie value in browser dev tools to inject a different cart ID, the signature verification would fail and `req.signedCookies.cart_session` would be `false`, triggering the server to create a fresh session instead of trusting the tampered value.

## 🟡 Real Example Hindi mein
**Amazon.in "Recently Viewed" feature:** बिना login किए browsing करते समय, Amazon एक cookie set करता है `recently_viewed=B08L5V,B09K3L,B07X9M` (comma-separated product IDs)। हर page load पर, `cookie-parser` request से ये cookie पढ़ता है ताकि server "Recently Viewed" carousel render कर सके। `cart_session` cookie (anonymous cart track करने वाली) के लिए, Amazon इसे secret से sign करता है — अगर user browser dev tools में cookie value tamper करके कोई दूसरा cart ID inject करने की कोशिश करे, signature verification fail हो जाएगी और `req.signedCookies.cart_session` `false` होगा, जिससे server tampered value trust करने के बदले नया session बना देगा।

---

## 💻 Code Example — Basic

```javascript
// cookie-parser-basic.js
const express = require('express');
const cookieParser = require('cookie-parser'); // npm install cookie-parser

const app = express();
app.use(cookieParser()); // parses req.headers.cookie into req.cookies

// Set a cookie when visiting the home page
app.get('/', (req, res) => {
  res.cookie('theme', 'dark', {
    maxAge: 24 * 60 * 60 * 1000, // cookie expires in 24 hours (ms)
    httpOnly: false, // accessible by client-side JS for this example
  });
  res.send('Theme cookie set to dark');
});

// Read the cookie on a subsequent request
app.get('/preferences', (req, res) => {
  const theme = req.cookies.theme; // reads parsed cookie value
  res.json({ currentTheme: theme || 'light' }); // default if no cookie sent yet
});

app.listen(3000, () => console.log('Server on port 3000 — visit / then /preferences'));
```

## 💻 Code Example — Advanced

```javascript
// cookie-parser-advanced.js — Signed cookies + tamper detection
const express = require('express');
const cookieParser = require('cookie-parser');

const app = express();

const COOKIE_SECRET = process.env.COOKIE_SECRET || 'super-secret-signing-key';
app.use(cookieParser(COOKIE_SECRET)); // secret enables signed cookie support

// ─── 1. SET A SIGNED COOKIE ────────────────────────────────────────────────────
app.post('/cart/create', (req, res) => {
  const cartId = `cart_${Date.now()}`; // generate a unique anonymous cart id

  res.cookie('cart_id', cartId, {
    signed: true, // cookie-parser will append an HMAC signature
    httpOnly: true, // not accessible via client-side JS (XSS protection)
    secure: process.env.NODE_ENV === 'production', // HTTPS only in prod
    sameSite: 'lax', // CSRF protection baseline
    maxAge: 7 * 24 * 60 * 60 * 1000, // 7 days
  });

  res.json({ message: 'Cart created', cartId });
});

// ─── 2. READ + VERIFY THE SIGNED COOKIE ────────────────────────────────────────
app.get('/cart', (req, res) => {
  const cartId = req.signedCookies.cart_id; // undefined if missing, false if tampered

  if (cartId === false) {
    // Signature verification failed — someone tampered with the cookie!
    return res.status(400).json({ error: 'Invalid cart cookie detected' });
  }

  if (!cartId) {
    return res.status(404).json({ error: 'No cart found, please create one' });
  }

  res.json({ cartId, items: [] }); // normally fetched from DB using cartId
});

// ─── 3. CLEAR COOKIE ON CHECKOUT COMPLETE ──────────────────────────────────────
app.post('/cart/checkout', (req, res) => {
  res.clearCookie('cart_id'); // must match path/domain options used when setting
  res.json({ message: 'Checkout complete, cart cleared' });
});

app.listen(3000, () => console.log('Signed-cookie server running on port 3000'));
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const cookieParser = require('cookie-parser');
const app = express();

app.use(cookieParser(process.env.COOKIE_SECRET));
app.use(express.json());

// Auth middleware reading a signed session cookie (common refresh-token pattern)
function requireAuth(req, res, next) {
  const sessionToken = req.signedCookies.session_token;
  if (!sessionToken) {
    return res.status(401).json({ error: 'Not authenticated' });
  }
  req.sessionToken = sessionToken; // attach for downstream handlers
  next();
}

app.get('/api/profile', requireAuth, (req, res) => {
  res.json({ message: 'Protected profile data', session: req.sessionToken });
});

app.listen(4000, () => console.log('Auth-protected API running on port 4000'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting to provide a secret when using signed cookies
✅ Correct: `cookieParser()` without a secret cannot verify signed cookies — `req.signedCookies` will always be empty; you must pass the same secret used to sign them.

```javascript
// Wrong — no secret, signed cookies can't be verified
app.use(cookieParser());
res.cookie('token', 'abc', { signed: true }); // signed, but can never be read back correctly

// Right — pass the secret consistently
app.use(cookieParser('my-secret-key'));
res.cookie('token', 'abc', { signed: true }); // now req.signedCookies.token works
```

❌ Mistake 2: Storing sensitive data in a regular (unsigned, non-HttpOnly) cookie
✅ Correct: Sensitive identifiers (session IDs, tokens) must be `httpOnly` (prevents JS/XSS access) and ideally `signed` (prevents tampering) — never store them as plain readable/writable cookies.

```javascript
// Wrong — plain cookie, readable and editable via document.cookie in browser console
res.cookie('isAdmin', 'false'); // user can literally edit this in dev tools!

// Right — never trust client-controlled flags; derive role server-side from verified session/JWT
// (role should come from DB lookup or signed JWT payload, never a plain cookie)
```

---

## 🧠 Tricky Interview Question

```javascript
const express = require('express');
const cookieParser = require('cookie-parser');
const app = express();

app.use(cookieParser('secret1'));

app.get('/set', (req, res) => {
  res.cookie('role', 'admin', { signed: true });
  res.send('set');
});

app.listen(3000);
// Later, server restarts with a DIFFERENT secret:
// app.use(cookieParser('secret2'));
```
If a client has the `role` cookie from before the restart, what does `req.signedCookies.role` return after the server restarts with `'secret2'`?

Answer: `false`. The cookie's HMAC signature was computed using `'secret1'`. After restart, `cookieParser('secret2')` tries to verify the signature using a different secret — the recomputed signature won't match the one stored in the cookie, so cookie-parser treats it as tampered and sets `req.signedCookies.role = false` (not `undefined` — `false` specifically signals "a signed cookie was present but failed verification," distinct from `undefined` meaning "no such cookie exists at all"). This highlights why rotating the cookie secret invalidates all previously issued signed cookies — a real operational consideration when changing secrets in production.

---

## ⚫ Interview Questions + Answers

Q1: What's the difference between `req.cookies` and `req.signedCookies`?
A1: `req.cookies` contains all cookies parsed from the `Cookie` header, including signed ones (but with their signature suffix still attached as a raw string if not using the secret). `req.signedCookies` contains ONLY cookies that were set with `{ signed: true }` and successfully verified against the provided secret — unsigned cookies never appear here. A signed cookie that fails verification shows up as `false` in `req.signedCookies`, and its raw original value does NOT appear in `req.cookies` either (cookie-parser strips it out when a secret is configured).

Q2: Why use signed cookies instead of just HttpOnly cookies?
A2: `httpOnly` only prevents client-side JavaScript from reading/writing the cookie (XSS protection) — but a user could still manually edit cookies via browser dev tools or a proxy tool (Postman, Burp Suite) since the cookie value is still plain text sent by the browser. Signing adds an HMAC signature so the SERVER can detect if the value was tampered with between being set and being sent back, even if the attacker can see/edit the raw cookie text.

Q3: Why shouldn't you rely on cookie-parser's "signed" cookies as a substitute for JWT-based auth?
A3: Signed cookies only guarantee the cookie VALUE wasn't tampered with — they don't carry expiry/claims verification logic like JWT's `exp`, `iat`, `role` claims with structured verification (`jwt.verify`). For complex auth (access/refresh tokens, claims-based authorization), JWT or session-based auth with DB-backed sessions is more appropriate. Signed cookies are great for simple anti-tampering use cases like cart IDs or simple preference flags.

Q4: How does `res.clearCookie()` actually "delete" a cookie, given HTTP is stateless?
A4: There's no real "delete" operation in HTTP — `res.clearCookie(name)` works by sending a `Set-Cookie` header with the same name but an expiry date in the past (and empty value). The browser, upon receiving this, removes the cookie from its store since it's already expired. Critically, the `path`, `domain`, and other options passed to `clearCookie` must match those used when the cookie was originally SET, or the browser treats it as a different cookie and won't clear the intended one.

Q5: What security attributes should production cookies always set?
A5: `httpOnly: true` (blocks JS access, mitigates XSS token theft), `secure: true` (only sent over HTTPS), `sameSite: 'strict'` or `'lax'` (mitigates CSRF by restricting cross-site cookie sending), and a reasonable `maxAge`/`expires` (limits exposure window if stolen). For session/auth cookies specifically, all four should typically be set together in production.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Reading cookies in Express routes (session IDs, preferences, anonymous cart/visitor tracking)
- Needing tamper-evidence on cookie values without full JWT complexity (signed cookies)
- Building traditional server-rendered apps or hybrid apps using cookie-based sessions

❌ Avoid when:
- Building a pure stateless API consumed by mobile apps/SPAs where JWT in `Authorization` header is more appropriate (cookies have CSRF considerations, mobile apps don't manage cookies as naturally)
- You need encrypted (not just signed) cookie content — signed cookies prevent tampering but the payload is still readable (Base64); use proper encryption or keep sensitive data server-side with just an opaque session ID in the cookie

---

## 📊 Visual Diagram
```
WITHOUT cookie-parser:
  req.headers.cookie = "session_id=abc123; theme=dark"
  → developer must manually split/parse this string in every route ❌

WITH cookie-parser:
  app.use(cookieParser('secret'))
         │
         ▼
  req.cookies = { session_id: 'abc123', theme: 'dark' }
  req.signedCookies = { cart_id: 'cart_999' }  (if signed + verified)

SIGNED COOKIE FLOW:
  res.cookie('cart_id', 'cart_999', { signed: true })
         │
         ▼
  Set-Cookie: cart_id=s%3Acart_999.HMAC_SIGNATURE
         │
         ▼ (client sends it back on next request)
  cookie-parser recomputes HMAC(cart_999, secret)
         │
    matches? ──Yes──▶ req.signedCookies.cart_id = 'cart_999'  ✅
         │
        No──▶ req.signedCookies.cart_id = false  ❌ (tampered!)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| cookie-parser | Middleware that parses Cookie header | Cookie header parse करने वाला middleware |
| req.cookies | Parsed unsigned cookies object | Parsed unsigned cookies object |
| req.signedCookies | Verified signed cookies object | Verified signed cookies object |
| Signed cookie | Cookie with HMAC signature for tamper detection | Tamper-detection वाली signed cookie |
| HttpOnly | Flag blocking JS access to cookie | JS access block करने वाला flag |
| SameSite | CSRF protection attribute | CSRF protection attribute |
| clearCookie | Expires a cookie via Set-Cookie in the past | Past date से cookie expire करना |

---

## ⚡ 3-Line Summary
English:
1. cookie-parser reads the raw `Cookie` header and exposes a clean `req.cookies` object, avoiding manual string parsing.
2. Pass a secret to enable signed cookies (`req.signedCookies`), which detect tampering via HMAC verification — `false` means tampered, `undefined` means absent.
3. Always set `httpOnly`, `secure`, and `sameSite` on sensitive cookies; signed cookies are not a substitute for full JWT/session security.

Hindi:
1. cookie-parser raw `Cookie` header पढ़कर एक clean `req.cookies` object बनाता है, manual string parsing से बचाता है।
2. Signed cookies enable करने के लिए secret pass करो (`req.signedCookies`), जो HMAC verification से tampering detect करते हैं — `false` मतलब tampered, `undefined` मतलब absent।
3. Sensitive cookies पर हमेशा `httpOnly`, `secure`, और `sameSite` set करो; signed cookies पूरी JWT/session security का substitute नहीं हैं।

---

## ➡️ Next Topic
**111. Session Management** — Server-side session storage, cookie-session linkage, and session stores।
