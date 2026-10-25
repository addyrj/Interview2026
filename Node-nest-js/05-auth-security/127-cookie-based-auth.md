# 127. Cookie Based Auth
# हिंदी में: Cookie Based Authentication — Transport Mechanism और Security

---

## 🔵 Simple Definition (English)
**Cookie-based auth** refers to using an HTTP cookie as the TRANSPORT mechanism for carrying authentication proof (a session ID or even a JWT) between client and server automatically on every request, without requiring the frontend to manually attach an `Authorization` header. Its defining characteristic is the BROWSER automatically sends cookies matching the domain/path — a double-edged convenience that also introduces CSRF risk requiring specific mitigations.

## 🔵 सरल परिभाषा (Hindi)
**Cookie-based auth** का मतलब है authentication proof (एक session ID या even एक JWT) को client और server के बीच automatically carry करने के लिए HTTP cookie को TRANSPORT mechanism के रूप में use करना, हर request पर, frontend को manually `Authorization` header attach करने की ज़रूरत के बिना। इसकी defining characteristic है कि BROWSER automatically domain/path से match होने वाली cookies भेजता है — एक double-edged convenience जो CSRF risk भी introduce करती है, specific mitigations की ज़रूरत होती है।

---

## 🔴 Problem it Solves
Manually attaching an `Authorization: Bearer <token>` header requires frontend JavaScript to store the token somewhere (localStorage/memory) and explicitly add it to every request — extra code, and if using localStorage, XSS exposure. Cookie-based auth leverages the browser's NATIVE cookie mechanism: once set, the browser automatically includes the cookie on every matching request (no JS involvement needed at all), works seamlessly with traditional page navigation/form submissions (no JS required at all for basic flows), and with `HttpOnly` set, the cookie is completely invisible to JavaScript — immune to token theft via XSS (though this trade introduces CSRF risk, requiring its own specific defenses).

## 🔴 यह क्यों बना? (Hindi)
Manually `Authorization: Bearer <token>` header attach करना frontend JavaScript को token कहीं store करने की ज़रूरत देता है (localStorage/memory) और हर request में explicitly add करना — extra code, और localStorage use करने पर, XSS exposure। Cookie-based auth browser के NATIVE cookie mechanism को leverage करता है: एक बार set होने पर, browser automatically हर matching request में cookie include करता है (JS involvement की ज़रूरत नहीं), traditional page navigation/form submissions के साथ seamlessly काम करता है (basic flows के लिए JS की ज़रूरत नहीं), और `HttpOnly` set होने पर, cookie JavaScript से पूरी तरह invisible है — XSS से token theft के against immune (हालांकि ये trade CSRF risk introduce करता है, जिसकी अपनी specific defenses चाहिए)।

---

## 🟢 How it Works — Step by Step

Step 1 → Server authenticates the user and sends `Set-Cookie: auth_token=<value>; HttpOnly; Secure; SameSite=Strict; Path=/` in the response.
Step 2 → The browser stores this cookie, scoped to the domain and path specified.
Step 3 → For EVERY subsequent request to a matching domain/path, the browser AUTOMATICALLY attaches `Cookie: auth_token=<value>` — no JavaScript code needed to do this.
Step 4 → Server-side middleware (`cookie-parser` or framework equivalent) reads `req.cookies.auth_token`, verifies it (session lookup, or JWT verify if the cookie holds a JWT), and populates `req.user`.
Step 5 → Because the browser auto-attaches cookies to ANY request to the matching domain (including ones triggered by a malicious third-party site, e.g., an auto-submitting form), CSRF protection (`SameSite` attribute, CSRF tokens) is essential — this is the core trade-off versus header-based auth, where the attacker's site has no way to read/attach your token.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Server user को authenticate करता है और response में `Set-Cookie: auth_token=<value>; HttpOnly; Secure; SameSite=Strict; Path=/` भेजता है।
Step 2 → Browser इस cookie को store करता है, specified domain और path तक scoped।
Step 3 → Matching domain/path की हर बाद की request के लिए, browser AUTOMATICALLY `Cookie: auth_token=<value>` attach करता है — इसके लिए कोई JavaScript code की ज़रूरत नहीं।
Step 4 → Server-side middleware (`cookie-parser` या framework equivalent) `req.cookies.auth_token` पढ़ता है, verify करता है (session lookup, या cookie में JWT होने पर JWT verify), और `req.user` populate करता है।
Step 5 → चूंकि browser matching domain की ANY request में cookies auto-attach करता है (malicious third-party site से trigger हुई requests भी, जैसे auto-submitting form), CSRF protection (`SameSite` attribute, CSRF tokens) ज़रूरी है — ये header-based auth के against core trade-off है, जहाँ attacker की site के पास आपका token read/attach करने का कोई तरीका नहीं है।

---

## 🟡 Real World Example
**Myntra web checkout flow:** Myntra's web app (not mobile) uses cookie-based auth for the logged-in session during checkout — when you add items to cart and proceed to payment, the browser automatically sends your session cookie with every API call (`/cart/add`, `/checkout/confirm`) without the frontend JS needing to manage token storage manually. To prevent CSRF (where a malicious site could trick your browser into submitting an unwanted "place order" request using your valid cookie), Myntra sets `SameSite=Strict` (or `Lax`) on the auth cookie AND additionally validates a CSRF token embedded in the actual checkout form for state-changing actions like placing an order — defense in depth beyond `SameSite` alone.

## 🟡 Real Example Hindi mein
**Myntra web checkout flow:** Myntra का web app (mobile नहीं) checkout के दौरान logged-in session के लिए cookie-based auth use करता है — जब आप cart में items add करके payment तक जाते हो, browser automatically आपकी session cookie हर API call के साथ भेजता है (`/cart/add`, `/checkout/confirm`) बिना frontend JS को token storage manually manage करने की ज़रूरत के। CSRF रोकने के लिए (जहाँ कोई malicious site आपके browser को आपकी valid cookie use करके unwanted "place order" request submit करने के लिए trick कर सकती है), Myntra auth cookie पर `SameSite=Strict` (या `Lax`) set करता है AND additionally state-changing actions जैसे order place करने के लिए actual checkout form में embedded CSRF token भी validate करता है — `SameSite` के अलावा defense in depth।

---

## 💻 Code Example — Basic

```javascript
// cookie-auth-basic.js
const express = require('express');
const cookieParser = require('cookie-parser'); // npm install cookie-parser
const jwt = require('jsonwebtoken'); // npm install jsonwebtoken

const app = express();
app.use(express.json());
app.use(cookieParser());

const SECRET = 'cookie-auth-secret';

// ─── LOGIN: issue a JWT stored in an HttpOnly cookie (not response body) ──────
app.post('/login', (req, res) => {
  const { username, password } = req.body;
  if (username === 'rohit' && password === 'pass123') { // mock check
    const token = jwt.sign({ userId: 'u1', role: 'customer' }, SECRET, { expiresIn: '1h' });

    res.cookie('auth_token', token, {
      httpOnly: true, // invisible to JavaScript — protects against XSS token theft
      secure: false, // set true in production (HTTPS required)
      sameSite: 'strict', // CSRF protection — cookie not sent on cross-site requests
      maxAge: 60 * 60 * 1000, // 1 hour
    });

    return res.json({ message: 'Logged in' }); // no token in the response body at all!
  }
  res.status(401).json({ error: 'Invalid credentials' });
});

// ─── MIDDLEWARE: reads the cookie automatically on every request ─────────────
function authenticate(req, res, next) {
  const token = req.cookies.auth_token; // browser sent this automatically
  if (!token) return res.status(401).json({ error: 'Not authenticated' });

  try {
    req.user = jwt.verify(token, SECRET);
    next();
  } catch (err) {
    res.status(401).json({ error: 'Invalid or expired session' });
  }
}

app.get('/profile', authenticate, (req, res) => res.json({ user: req.user }));

app.post('/logout', (req, res) => {
  res.clearCookie('auth_token'); // tells browser to remove the cookie
  res.json({ message: 'Logged out' });
});

app.listen(3000, () => console.log('Cookie-based auth server running on port 3000'));
```

## 💻 Code Example — Advanced

```javascript
// cookie-auth-advanced.js — CSRF protection with double-submit cookie pattern
const express = require('express');
const cookieParser = require('cookie-parser');
const jwt = require('jsonwebtoken');
const crypto = require('crypto');

const app = express();
app.use(express.json());
app.use(cookieParser());

const JWT_SECRET = process.env.JWT_SECRET || 'secret';

// ─── 1. LOGIN sets BOTH the HttpOnly auth cookie AND a readable CSRF cookie ───
app.post('/login', (req, res) => {
  const userId = 'u1'; // mock successful auth
  const authToken = jwt.sign({ userId }, JWT_SECRET, { expiresIn: '1h' });
  const csrfToken = crypto.randomBytes(32).toString('hex'); // random, unguessable

  res.cookie('auth_token', authToken, {
    httpOnly: true, // JS can't read this — protects the actual credential
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict',
    maxAge: 60 * 60 * 1000,
  });

  // CSRF token cookie is NOT HttpOnly — frontend JS NEEDS to read it to echo it back
  res.cookie('csrf_token', csrfToken, {
    httpOnly: false, // intentionally readable by JS
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict',
    maxAge: 60 * 60 * 1000,
  });

  res.json({ message: 'Logged in' });
});

// ─── 2. CSRF VALIDATION MIDDLEWARE (double-submit cookie pattern) ─────────────
function validateCsrf(req, res, next) {
  const cookieToken = req.cookies.csrf_token;
  const headerToken = req.headers['x-csrf-token']; // frontend JS reads cookie, sends as header

  if (!cookieToken || !headerToken || cookieToken !== headerToken) {
    // A cross-site attacker can trigger the cookie to be SENT automatically,
    // but CANNOT read the cookie value (different origin) to set the matching header
    return res.status(403).json({ error: 'CSRF validation failed' });
  }
  next();
}

function authenticate(req, res, next) {
  try {
    req.user = jwt.verify(req.cookies.auth_token, JWT_SECRET);
    next();
  } catch (err) {
    res.status(401).json({ error: 'Not authenticated' });
  }
}

// ─── 3. STATE-CHANGING ROUTES require BOTH auth AND CSRF validation ──────────
app.post('/api/transfer-money', authenticate, validateCsrf, (req, res) => {
  res.json({ message: 'Transfer processed', amount: req.body.amount });
});

// Read-only routes only need authentication, not CSRF protection
// (CSRF is a concern for state-CHANGING requests; GET requests shouldn't mutate state)
app.get('/api/balance', authenticate, (req, res) => res.json({ balance: 5000 }));

app.listen(3000, () => console.log('CSRF-hardened cookie auth server running on port 3000'));
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const cookieParser = require('cookie-parser');
const jwt = require('jsonwebtoken');
const helmet = require('helmet'); // npm install helmet
const app = express();

app.use(helmet()); // security headers
app.use(cookieParser());
app.use(express.json());

const router = express.Router();

router.post('/login', async (req, res) => {
  const user = await User.findOne({ email: req.body.email }); // mock
  const token = jwt.sign({ userId: user._id }, process.env.JWT_SECRET, { expiresIn: '1h' });

  res.cookie('session', token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax', // 'lax' allows top-level navigation (clicking a link from email) to still send cookie
    maxAge: 3600000,
  });
  res.json({ message: 'Logged in' });
});

const authenticate = (req, res, next) => {
  try {
    req.user = jwt.verify(req.cookies.session, process.env.JWT_SECRET);
    next();
  } catch {
    res.status(401).json({ error: 'Login required' });
  }
};

router.get('/dashboard', authenticate, (req, res) => res.json({ user: req.user }));

app.use('/auth', router);
app.listen(4000, () => console.log('App running on port 4000'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Omitting `SameSite` on auth cookies, leaving the app CSRF-vulnerable by default
✅ Correct: Always explicitly set `SameSite: 'strict'` or `'lax'` — without it, browsers may default to `Lax` (modern Chrome) but older browsers/configurations could default to no restriction at all, leaving state-changing endpoints vulnerable to CSRF.

```javascript
// Risky — relies on browser default, inconsistent across browser versions
res.cookie('auth_token', token, { httpOnly: true });

// Right — explicit SameSite policy
res.cookie('auth_token', token, { httpOnly: true, sameSite: 'strict', secure: true });
```

❌ Mistake 2: Using cookie-based auth for a mobile app or third-party API consumer where cookies don't fit naturally
✅ Correct: Mobile apps (especially native, not WebView) don't have an automatic cookie jar tied to a browser session in the same way — for those clients, header-based token auth (`Authorization: Bearer`) is more natural and avoids cookie-jar/domain complications.

```javascript
// Wrong — forcing cookie-based auth onto a native mobile client that doesn't manage cookies naturally
res.cookie('auth_token', token, { httpOnly: true }); // awkward for non-browser clients

// Right — for mobile/API clients, return the token in the response body for Authorization header use
res.json({ accessToken: token }); // client stores and sends via Authorization header
```

---

## 🧠 Tricky Interview Question

```javascript
// evil-site.com hosts this hidden auto-submitting form:
// <form action="https://yourbank.com/api/transfer-money" method="POST">
//   <input type="hidden" name="amount" value="10000" />
// </form>
// <script>document.forms[0].submit()</script>

// Your bank's cookie: Set-Cookie: auth_token=xyz; SameSite=Strict
```
If a logged-in user (with a valid `auth_token` cookie from yourbank.com) visits evil-site.com, does the hidden form's POST request to yourbank.com include the `auth_token` cookie?

Answer: **No**, with `SameSite=Strict` set, the browser will NOT include the `auth_token` cookie on this cross-site request, because the request originates from a different site (`evil-site.com`) than the cookie's origin (`yourbank.com`) — `SameSite=Strict` blocks the cookie from being sent on ANY cross-site request, including this classic CSRF attack pattern (an auto-submitting form from an attacker-controlled page). Without `SameSite` (or with `SameSite=None`), the browser WOULD have included the cookie automatically since it matches the target domain, and `yourbank.com`'s server would have seen what looks like a legitimate, authenticated request — processing the malicious transfer. This demonstrates exactly why `SameSite=Strict`/`Lax` is such an important, almost "free" CSRF defense for cookie-based auth — though for maximum defense-in-depth, critical state-changing actions (like a money transfer) typically ALSO validate an explicit CSRF token even with `SameSite` set, since `SameSite=Lax` still permits SOME cross-site scenarios (top-level GET navigation) that `Strict` fully blocks but at some UX cost (e.g., breaking some legitimate cross-site link-click flows).

---

## ⚫ Interview Questions + Answers

Q1: Why is cookie-based auth inherently more vulnerable to CSRF than header-based (Authorization: Bearer) auth?
A1: Cookies are automatically attached by the BROWSER to any request matching the cookie's domain, REGARDLESS of which page/site initiated the request — an attacker's page can trigger a request to your API, and the browser will "helpfully" attach your valid auth cookie, making the forged request appear authenticated. Header-based auth requires the REQUESTING JAVASCRIPT to explicitly read a token (from memory/localStorage) and attach it as a header — an attacker's page, running in a different origin, has no way to read YOUR site's localStorage or in-memory JS variables (same-origin policy), so it CANNOT construct a request with your valid Authorization header. This structural difference is why CSRF is a cookie-specific concern, not really applicable to header-based token auth.

Q2: What's the difference between `SameSite=Strict` and `SameSite=Lax`?
A2: `Strict` never sends the cookie on ANY cross-site request, even top-level navigation (clicking a link from an external site to yours won't include the cookie on that first request) — most secure, but can break flows like "click a link in an email to go directly to a logged-in page" (user would appear logged out on that first navigation). `Lax` (the modern browser default) sends the cookie on top-level navigations (GET requests from clicking a link) but NOT on cross-site POST requests or requests from embedded resources (img/iframe) — a reasonable middle ground balancing security and usability for most apps.

Q3: What is the "double-submit cookie" CSRF protection pattern, and why does it work?
A3: The server issues a CSRF token as a cookie that's NOT HttpOnly (readable by JS) alongside the HttpOnly auth cookie. Legitimate frontend JavaScript (running on YOUR domain) reads this CSRF cookie value and sends it back as a custom header (e.g., `X-CSRF-Token`) on state-changing requests. The server validates that the header value matches the cookie value. This works because an attacker's cross-site page CANNOT read your domain's cookies (same-origin policy prevents JS on evil-site.com from reading cookies set for yourbank.com) — so even though the attacker's forged request would automatically carry the auth cookie, it CANNOT construct the matching CSRF header value, since it can't read the CSRF cookie to copy it.

Q4: Can you use cookie-based auth with a JWT instead of a traditional opaque session ID?
A4: Yes — the "cookie" part refers to the TRANSPORT mechanism (how the credential travels between client/server), while "session ID vs JWT" is about the CREDENTIAL's nature (opaque reference vs self-contained signed token). You can absolutely store a JWT inside an HttpOnly cookie instead of a traditional session ID — this combines JWT's stateless verification (no DB lookup needed) with cookie-based auth's automatic browser transport and XSS protection (via HttpOnly), though you still need SameSite/CSRF protections since the transport mechanism (cookie) is what matters for that specific risk, not what's inside it.

Q5: Why might you choose cookie-based auth for a web app but header-based (Bearer token) auth for the SAME backend's mobile app?
A5: Web browsers have a native, well-understood cookie jar with automatic domain/path scoping, HttpOnly XSS protection, and built-in CSRF mitigations (SameSite) — a natural fit for browser-based clients. Native mobile apps don't have an equivalent automatic "browser cookie jar" tied to web-style same-origin semantics; they typically manage their own secure storage (iOS Keychain, Android Keystore) and explicitly attach tokens as headers on each request. Using the SAME backend endpoints to serve both client types often means supporting both transport methods (checking `Authorization` header OR cookie) in the authentication middleware, picking whichever is present per-request.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Building browser-based web applications where native browser cookie handling (automatic attachment, HttpOnly XSS protection) is advantageous
- Server-rendered apps or hybrid apps with traditional form submissions/page navigation
- You can properly implement CSRF protections (SameSite + CSRF tokens for critical actions)

❌ Avoid when:
- Building native mobile apps or pure API-to-API integrations where header-based Bearer token auth is more natural and avoids cookie-domain complications entirely
- Cross-origin API consumption by many different third-party domains, where cookie-based auth's domain-scoping becomes an awkward constraint compared to a portable Bearer token

---

## 📊 Visual Diagram
```
COOKIE-BASED AUTH vs HEADER-BASED AUTH (CSRF exposure):

  COOKIE-BASED:
    Browser automatically attaches cookie to ANY request matching the domain
    (including ones triggered by a malicious cross-site page)
    │
    ──▶ Vulnerable to CSRF unless SameSite/CSRF-token mitigations applied

  HEADER-BASED (Authorization: Bearer):
    JavaScript must EXPLICITLY read the token and attach it as a header
    An attacker's cross-site page CANNOT read your domain's localStorage/memory
    │
    ──▶ Not vulnerable to CSRF by design (but vulnerable to XSS if stored in localStorage)

DOUBLE-SUBMIT COOKIE PATTERN:
  Set-Cookie: auth_token=xyz; HttpOnly        ◀── credential, JS can't read
  Set-Cookie: csrf_token=abc; (readable)      ◀── JS CAN read this one

  Legitimate request: JS reads csrf_token, sends as X-CSRF-Token header
       → header matches cookie → ✅ allowed

  Forged cross-site request: auth cookie auto-attached, but attacker
  CANNOT read csrf_token cookie (different origin) → header missing/wrong
       → ❌ rejected
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Cookie-based auth | Using cookies as the auth transport | Auth transport के लिए cookies use करना |
| CSRF | Cross-Site Request Forgery attack | Cross-site forged request attack |
| SameSite | Cookie attribute restricting cross-site sending | Cross-site sending restrict करने वाला attribute |
| Double-submit cookie | CSRF defense comparing cookie + header | Cookie + header compare करने वाला CSRF defense |
| HttpOnly | Blocks JS access, prevents XSS token theft | JS access block, XSS theft रोकना |
| Bearer token | Header-based token transport alternative | Header-based token transport |

---

## ⚡ 3-Line Summary
English:
1. Cookie-based auth uses the browser's automatic cookie transport to carry credentials on every request — convenient, but introduces CSRF risk since cookies attach regardless of request origin.
2. Mitigate CSRF with `SameSite=Strict/Lax` plus explicit CSRF tokens (double-submit pattern) for critical state-changing actions.
3. Prefer cookies for browser-based web apps; prefer header-based Bearer tokens for mobile apps and cross-origin API consumers.

Hindi:
1. Cookie-based auth browser के automatic cookie transport को use करता है credentials हर request में carry करने के लिए — convenient, पर CSRF risk introduce करता है क्योंकि cookies request origin के बावजूद attach होती हैं।
2. CSRF mitigate करो `SameSite=Strict/Lax` plus explicit CSRF tokens (double-submit pattern) से critical state-changing actions के लिए।
3. Browser-based web apps के लिए cookies prefer करो; mobile apps और cross-origin API consumers के लिए header-based Bearer tokens prefer करो।

---

## ➡️ Next Topic
**128. API Key Authentication** — Simple token-based auth for server-to-server and third-party API access।
