# 90. CSS Attribute Selectors
# हिंदी में: CSS Attribute Selectors — Attribute से Element चुनना

---

## 🔵 Simple Definition (English)
Attribute selectors select elements based on **their HTML attributes or attribute values**, not just tag, class or id. Examples: `[disabled]`, `[type="email"]`, `[href^="https"]`, `[src$=".png"]`, `[class*="btn"]`.

## 🔵 सरल परिभाषा (Hindi)
Attribute selectors elements को उनके **HTML attributes या attribute की value** के आधार पर चुनते हैं — सिर्फ tag, class या id के आधार पर नहीं। जैसे `[disabled]`, `[type="email"]`, `[href^="https"]`, `[src$=".png"]`।

---

## 🔴 Problem it Solves
```
WITHOUT ATTRIBUTE SELECTORS:
  /* Want to style all email inputs, all PDF links, all external links */
  <input type="email" class="email-input">       /* extra class needed */
  <a href="report.pdf" class="pdf-link">         /* extra class on every link */
  <a href="https://x.com" class="external">      /* easy to forget one */
  /* CMS / Markdown content: you cannot add classes to auto-generated HTML */

WITH ATTRIBUTE SELECTORS:
  input[type="email"]  { ... }
  a[href$=".pdf"]      { ... }
  a[href^="https"]     { ... }
  /* No extra classes. Works even on content you do not control (Markdown, CMS, 3rd party widgets). */
```

## 🔴 यह क्यों बना? (Hindi)
हर element पर अलग class लगाना थकाने वाला है, और CMS / Markdown से आए HTML में तो class लगा भी नहीं सकते। Attribute selectors से हम सीधे `type`, `href`, `src`, `data-*` जैसे attributes पर style लगा देते हैं — कोई extra class नहीं।

---

## 🟢 How it Works — Step by Step

```
THE 7 FORMS:
──────────────────────────────────────────────────────────
  [attr]            has the attribute (any value)
  [attr="v"]        value is EXACTLY v
  [attr~="v"]       space-separated word list CONTAINS word v     (like class)
  [attr|="v"]       value is v OR starts with "v-"   (lang="en", lang="en-US")
  [attr^="v"]       value STARTS with v
  [attr$="v"]       value ENDS with v
  [attr*="v"]       value CONTAINS v anywhere

CASE FLAGS (inside the bracket, at end):
  [type="EMAIL" i]  i = case-INSENSITIVE match
  [data-x="a" s]    s = case-SENSITIVE (force)

EXAMPLES:
  a[target]                  → links that have target (any value)
  a[target="_blank"]         → only new-tab links
  a[href^="https://"]        → starts with https://
  a[href^="mailto:"]         → email links
  a[href$=".pdf"]            → ends with .pdf
  img[alt=""]                → decorative images (empty alt)
  [class*="col-"]            → any class containing "col-"
  [data-state="open"]        → custom data attribute state
  p[lang|="en"]              → en, en-US, en-GB

SPECIFICITY:
  An attribute selector counts like a CLASS = (0,1,0).
  a[href]           → (0,1,1)
  input[type="x"]   → (0,1,1)
  [data-x]          → (0,1,0)
  Example: input[type] is (0,1,1) and .field is (0,1,0) → input[type] wins
  because of the extra element part. [data-x] vs .btn → tie, source order decides.

QUOTES:
  [type=email] works if value is a valid identifier.
  Use quotes when value has spaces, dots, slashes or starts with a digit:
  [href$=".pdf"]   [data-id="12"]   ← quotes REQUIRED here.

SUPPORT: All forms work in every modern browser (CSS2/CSS3 selectors). The i flag: Chrome 49+, Firefox 47+, Safari 9+.
```

## 🟢 कैसे काम करता है? (Hindi)
1. `[attr]` — attribute मौजूद हो (value कुछ भी)।
2. `[attr="v"]` — value बिल्कुल `v` हो।
3. `[attr^="v"]` — value `v` से **शुरू** हो; `$=` — `v` पर **खत्म** हो; `*=` — `v` कहीं भी **शामिल** हो।
4. `[attr~="v"]` — space से अलग शब्दों में `v` मौजूद हो; `[attr|="v"]` — `v` या `v-...` हो (language codes के लिए)।
5. `i` flag लगाओ तो capital/small का फ़र्क नहीं पड़ता: `[type="EMAIL" i]`।
6. Specificity एक **class** के बराबर है (0,1,0)।
7. Value में dot, slash या space हो तो quotes ज़रूरी हैं।

---

## 🟡 Real World Example
**Gmail / Notion / Medium:** Article ke andar jo external links hote hain (`a[href^="http"]`), unke aage chhota arrow icon aata hai, internal links ke aage nahi.
**Amazon:** Disabled "Add to cart" button grey dikhta hai: `button[disabled] { opacity: .5; cursor: not-allowed; }`.
**Instagram web / Radix UI / shadcn:** Components `data-state="open"` ya `aria-expanded="true"` jaise attributes lagate hain, aur CSS `[data-state="open"]` se dropdown/accordion style karta hai — JavaScript se class toggle karne ki zarurat nahi.
**Swiggy checkout:** `input[type="tel"]` ko phone number keyboard style, `input[aria-invalid="true"]` ko red border.

## 🟡 Real Example Hindi mein
**Medium / Gmail articles:** External links (`a[href^="http"]`) के आगे छोटा arrow icon आता है, internal links के आगे नहीं।
**Amazon:** Disabled button grey दिखता है: `button[disabled] { opacity: .5 }`।
**shadcn/Radix UI:** Components `data-state="open"` लगाते हैं और CSS `[data-state="open"]` से dropdown style होता है — JS से class toggle करने की ज़रूरत नहीं।
**Swiggy checkout:** `input[aria-invalid="true"]` पर red border लगती है।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CSS Attribute Selectors Demo</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; padding: 20px; background: #f5f5f5; color: #222; line-height: 1.6; }
    h2 { margin: 26px 0 8px; font-size: 16px; border-bottom: 2px solid #333; padding-bottom: 4px; }
    .box { background: #fff; padding: 14px; border-radius: 8px; max-width: 480px; }

    /* ─── 1. PRESENCE: [attr] ────────────────────────────────────── */
    button { padding: 8px 14px; border: 0; border-radius: 6px; background: #2e7d32; color: #fff; cursor: pointer; }
    /* any button that HAS the disabled attribute */
    button[disabled] { opacity: .45; cursor: not-allowed; }

    /* ─── 2. EXACT VALUE: [attr="v"] ─────────────────────────────── */
    input { display: block; width: 100%; margin: 6px 0; padding: 8px; border: 1px solid #bbb; border-radius: 6px; }
    input[type="email"] { border-left: 4px solid #1976d2; }   /* email gets blue accent */
    input[type="password"] { border-left: 4px solid #d32f2f; }
    /* ARIA state: red border when invalid */
    input[aria-invalid="true"] { border-color: #d32f2f; background: #fff5f5; }

    /* ─── 3. STARTS WITH: [attr^="v"] ────────────────────────────── */
    /* external links get an arrow (anything starting with https://) */
    a[href^="https://"]::after { content: " ↗"; font-size: 12px; }
    /* mailto links get an envelope */
    a[href^="mailto:"]::before { content: "✉ "; }

    /* ─── 4. ENDS WITH: [attr$="v"] ──────────────────────────────── */
    a[href$=".pdf"]::after { content: " (PDF)"; color: #d32f2f; font-size: 12px; }
    /* external AND not pdf: combine with :not() from topic 89 */
    a[href^="https://"]:not([href$=".pdf"])::after { content: " ↗"; }

    /* ─── 5. CONTAINS: [attr*="v"] ───────────────────────────────── */
    /* any element whose class list string contains "btn-" */
    [class*="btn-"] { display: inline-block; padding: 6px 12px; border-radius: 6px; margin: 2px; color: #fff; }
    .btn-blue { background: #1976d2; }
    .btn-red  { background: #d32f2f; }

    /* ─── 6. WORD MATCH: [attr~="v"] ─────────────────────────────── */
    /* data-tags="new sale hot" → matches the WORD sale, not "salesman" */
    [data-tags~="sale"] { outline: 2px dashed #ff9800; padding: 6px; margin: 4px 0; }

    /* ─── 7. LANGUAGE: [attr|="v"] ───────────────────────────────── */
    p[lang|="hi"] { color: #c2185b; }   /* hi, hi-IN */

    /* ─── 8. CASE INSENSITIVE: i flag ────────────────────────────── */
    a[href$=".JPG" i] { font-style: italic; }   /* .jpg .JPG .Jpg all match */

    /* ─── 9. DATA ATTRIBUTE STATE (like Radix/shadcn) ────────────── */
    .panel { max-height: 0; overflow: hidden; background: #e3f2fd; transition: max-height .3s; padding: 0 12px; }
    .acc[data-state="open"] + .panel { max-height: 80px; padding: 12px; }
    .acc[data-state="open"] { background: #0d47a1; }
    .acc { background: #1976d2; width: 100%; text-align: left; }
  </style>
</head>
<body>
  <h1>Attribute Selectors</h1>

  <h2>1 &amp; 2. Presence and exact value</h2>
  <div class="box">
    <button>Add to cart</button>
    <button disabled>Out of stock</button>
    <input type="email" placeholder="Email">
    <input type="password" placeholder="Password">
    <input type="text" placeholder="Invalid field" aria-invalid="true">
  </div>

  <h2>3 &amp; 4. ^= and $= on links</h2>
  <div class="box">
    <p><a href="https://github.com">External link</a></p>
    <p><a href="mailto:hello@example.com">Mail us</a></p>
    <p><a href="/docs/guide.pdf">Local PDF</a></p>
    <p><a href="/about">Internal link (no icon)</a></p>
    <p><a href="/photos/pic.JPG">Photo (italic via i flag)</a></p>
  </div>

  <h2>5, 6 &amp; 7. *=  ~=  |=</h2>
  <div class="box">
    <span class="btn-blue">btn-blue</span>
    <span class="btn-red">btn-red</span>
    <div data-tags="new sale hot">Has the word "sale"</div>
    <div data-tags="salesman">Does not match ~="sale"</div>
    <p lang="hi-IN">यह हिंदी paragraph है (lang|="hi")</p>
    <p lang="en">English paragraph</p>
  </div>

  <h2>9. data-state accordion (no JS class toggle)</h2>
  <div class="box">
    <button class="acc" data-state="closed" onclick="
      /* flip the attribute; CSS does the rest */
      this.dataset.state = this.dataset.state === 'open' ? 'closed' : 'open';
    ">Click to toggle</button>
    <div class="panel">Hidden content revealed by [data-state="open"].</div>
  </div>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. Radix UI / shadcn/ui / Headless UI expose state as DATA ATTRIBUTES.
//    Style them with attribute selectors in CSS Modules or Tailwind:

/* Accordion.module.css */
.trigger[data-state="open"] > .chevron { transform: rotate(180deg); }
.content[data-state="closed"] { display: none; }

// 2. Tailwind: data-* and aria-* variants compile to attribute selectors
//    data-[state=open]:bg-blue-600   →  [data-state="open"] { ... }
//    aria-expanded:rotate-180        →  [aria-expanded="true"] { ... }
//    disabled:opacity-50             →  :disabled { ... }
<button
  data-state={open ? 'open' : 'closed'}
  className="bg-gray-200 data-[state=open]:bg-blue-600 data-[state=open]:text-white"
>
  Toggle
</button>

// 3. Prefer accessible attributes (aria-*) as the styling hook:
<input aria-invalid={!!error} className="border aria-[invalid=true]:border-red-500" />

// 4. Style rich text rendered from Markdown/CMS (you cannot add classes):
/* globals.css */
.prose a[href^="http"]:not([href*="mysite.com"])::after { content: " ↗"; }

// 5. Next.js note: React passes data-* props straight through to the DOM,
//    camelCase is NOT used: data-testid, not dataTestId.
```

---

## ⚫ Interview Questions + Answers

**Q1: What are attribute selectors and why use them?**
A1: They match elements by attribute presence or value: `[disabled]`, `[type="email"]`. Useful when you cannot or do not want to add classes: CMS content, third party widgets, form types, and state attributes like `aria-expanded` or `data-state`. They keep the HTML semantic and drive styling from real state.

**Q2: Explain `^=`, `$=`, `*=`, `~=`, `|=`.**
A2: `^=` value starts with; `$=` value ends with; `*=` value contains substring anywhere; `~=` space-separated list contains the exact word (works like class matching); `|=` value equals the string or starts with it followed by a hyphen (`en`, `en-US`). Example: `a[href$=".pdf"]` PDF links, `[class*="col-"]` any class containing col-.

**Q3: What is the specificity of an attribute selector?**
A3: Same as a class and pseudo-class: (0,1,0). So `input[type="text"]` is (0,1,1). It is NOT as strong as an id. This means `a[href]` can override `a`, and `.btn` (0,1,0) ties with `[data-x]` (0,1,0) so source order decides.

**Q4: Difference between `[class="btn"]` and `.btn`?**
A4: `[class="btn"]` needs the whole class attribute to be exactly `btn` — it fails for `class="btn primary"`. `.btn` matches any element whose class list contains `btn`. To match one word inside the attribute string use `[class~="btn"]` (same as `.btn`) or `[class*="btn"]` (substring: also matches `big-btn-x`).

**Q5: How do you match attribute values case-insensitively?**
A5: Add the `i` flag before the closing bracket: `a[href$=".jpg" i]` matches `.JPG`, `.Jpg`. By default, attribute NAME matching follows the HTML rules, and values are case-sensitive except for some HTML attributes like `type` (case-insensitive in HTML documents). The `s` flag forces case-sensitive.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Using `[class="btn"]` when multiple classes exist
```css
/* WRONG: fails for <button class="btn primary"> */
[class="btn"] { padding: 8px; }

/* CORRECT */
.btn { padding: 8px; }
/* or */
[class~="btn"] { padding: 8px; }
```

❌ **Mistake 2:** Using `*=` too loosely
```css
/* WRONG: matches "sub-nav-label", "banner", "nav" ... too many surprises */
[class*="nav"] { display: flex; }

/* CORRECT: exact class or word match */
.nav, [class~="nav"] { display: flex; }
```

❌ **Mistake 3:** Forgetting quotes for values with special characters
```css
/* WRONG: invalid, the dot breaks the identifier */
a[href$=.pdf] { color: red; }

/* CORRECT */
a[href$=".pdf"] { color: red; }
```

❌ **Mistake 4:** Expecting `input[value="x"]` to follow what the user types
```css
/* WRONG: the value ATTRIBUTE is the initial HTML value; typing changes the property, not the attribute */
input[value="hello"] { border-color: green; }

/* CORRECT: use :placeholder-shown, :valid, :invalid, or set the attribute from JS/React state */
input:invalid { border-color: red; }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Attribute | Extra info on an HTML tag (href, type) | Tag की extra जानकारी |
| [attr] | Has the attribute | Attribute मौजूद हो |
| [attr="v"] | Exact value match | बिल्कुल वही value |
| ^= | Starts with | से शुरू |
| $= | Ends with | पर खत्म |
| *= | Contains | कहीं भी शामिल |
| ~= | Contains word in space-list | शब्द मौजूद |
| i flag | Case-insensitive | Capital/small बराबर |
| data-* | Custom attributes for state | अपने बनाए attributes |

---

## ⚡ 3-Line Summary
**English:**
1. Attribute selectors match by attribute presence or value: `[x]`, `[x="v"]`, `^=`, `$=`, `*=`, `~=`, `|=`.
2. They count as a class for specificity (0,1,0) and are perfect for CMS content, form types, ARIA and `data-state` styling.
3. Use quotes for special characters and the `i` flag for case-insensitive matching.

**Hindi:**
1. Attribute selectors attribute के होने या उसकी value से element चुनते हैं।
2. Specificity एक class जितनी (0,1,0); CMS content, forms, ARIA और `data-state` के लिए बढ़िया।
3. Special characters के लिए quotes लगाओ और case ignore करने के लिए `i` flag।

---

## ➡️ Next Topic
**91. CSS Architecture (BEM, OOCSS, SMACSS)** — जब project बड़ा हो जाए तो CSS को organize कैसे करें, class naming कैसे हो ताकि team में कोई conflict न हो।
