# 48. Ways to Add CSS (inline, internal, external)
# हिंदी में: CSS जोड़ने के तरीके — Inline, Internal, External

---

## 🔵 Simple Definition (English)
There are three ways to add CSS to HTML: **Inline** (`style="..."` attribute on one element), **Internal** (a `<style>` block in the page), and **External** (a separate `.css` file linked with `<link rel="stylesheet">`). External CSS is the standard for real projects because it is reusable and cacheable.

## 🔵 सरल परिभाषा (Hindi)
HTML में CSS जोड़ने के तीन तरीके हैं: **Inline** (एक element पर `style="..."` attribute), **Internal** (page में `<style>` block), और **External** (अलग `.css` file जो `<link rel="stylesheet">` से जुड़ती है)। असली projects में External CSS standard है क्योंकि यह reuse और cache हो सकती है।

---

## 🔴 Problem it Solves
```
NEED: Different situations need different scopes of styling.

  Inline   -> style one single element (quick fix, email HTML, dynamic values)
  Internal -> style one single page (demo, landing page, critical CSS)
  External -> style the WHOLE site from one file

PROBLEMS WITH THE WRONG CHOICE:
  - Inline everywhere: cannot reuse, cannot use :hover/@media,
    hard to override, bloats HTML, blocks strict CSP
  - Internal in 50 pages: change a colour = edit 50 files, no caching
  - External only: one extra network request (render-blocking)
```

## 🔴 यह क्यों बना? (Hindi)
```
ज़रूरत: अलग स्थितियों में अलग scope की styling चाहिए।

  Inline   -> सिर्फ एक element (quick fix, email HTML, dynamic values)
  Internal -> सिर्फ एक page (demo, landing page, critical CSS)
  External -> पूरी site, एक file से

गलत चुनाव की समस्याएँ:
  - हर जगह inline: reuse नहीं, :hover/@media नहीं, override मुश्किल, HTML भारी
  - 50 pages में internal: रंग बदलना = 50 files बदलना, caching नहीं
  - सिर्फ external: एक अतिरिक्त network request (render-blocking)
```

---

## 🟢 How it Works — Step by Step

```
1. INLINE  - attribute on the element
   <p style="color: red; font-size: 18px;">Text</p>
   - Highest priority among normal rules (specificity 1,0,0,0)
   - Only declarations. No selectors, :hover, ::before, @media
   - Overridden only by !important in a stylesheet

2. INTERNAL - <style> in <head>
   <head><style> p { color: blue; } </style></head>
   - Applies to that page only
   - No extra request, so good for tiny pages and critical CSS

3. EXTERNAL - separate file
   <link rel="stylesheet" href="styles.css">
   - Cached across pages, one change updates all
   - Render-blocking: the browser waits for it before painting
   - @import inside CSS also works but loads sequentially (slower): avoid

CASCADE ORDER (same specificity -> LATER wins, by source order):
   <link href="a.css">
   <style>p{color:blue}</style>     <- later than link: wins over a.css
   <link href="b.css">              <- later still: wins over both
   style="color:red"                <- inline beats all (unless !important)

ALSO POSSIBLE:
   - JS:  el.style.color = 'red';  el.classList.add('active');
          el.style.setProperty('--x', '10px');
   - Constructable stylesheets (adoptedStyleSheets) for shadow DOM
   - <link> with media:  <link rel="stylesheet" href="print.css" media="print">
   - Preload: <link rel="preload" as="style" href="main.css">

BEST PRACTICE:
   - External for the site's styles
   - A small inline <style> for critical above-the-fold CSS (optional)
   - Inline style only for truly dynamic values (e.g. progress bar width)
   - Put <link> in <head> (so CSS loads before body paints)
   - Minify + compress (Brotli) + cache with a hashed filename
```

## 🟢 कैसे काम करता है? (Hindi)

```
1. Inline: element पर style attribute
   <p style="color: red;">Text</p>
   - सामान्य rules में सबसे ऊँची priority
   - सिर्फ declarations; :hover, ::before, @media नहीं चलते

2. Internal: <head> में <style>
   - सिर्फ उसी page पर लगता है
   - अतिरिक्त request नहीं; छोटे pages और critical CSS के लिए ठीक

3. External: अलग file
   <link rel="stylesheet" href="styles.css">
   - सब pages में cache होती है, एक बदलाव सब जगह
   - Render-blocking है
   - CSS के अंदर @import धीमा है, बचो

क्रम: समान specificity पर बाद वाला जीतता है (link -> style -> link)।
Inline सबसे ऊपर (जब तक stylesheet में !important न हो)।

सबसे अच्छा तरीका: Site के लिए external, छोटा critical CSS inline,
और inline style सिर्फ dynamic values (जैसे progress bar की width) के लिए।
<link> को <head> में रखो।
```

---

## 🟡 Real World Example
**Amazon/Flipkart** serve one cached external stylesheet (hashed file name such as `main.3f2a1.css`) for the whole site, plus a tiny inline `<style>` with critical CSS so the header paints instantly. **Gmail** emails you receive use **inline styles** everywhere because email clients ignore external CSS. **Swiggy's** delivery progress bar sets `style="width: 65%"` inline because the value comes from live data.

## 🟡 Real Example Hindi mein
**Amazon/Flipkart** पूरी site के लिए एक cached external stylesheet (hash वाला नाम जैसे `main.3f2a1.css`) देते हैं, और header तुरंत दिखे इसलिए छोटा inline `<style>` critical CSS के साथ। **Gmail** में आने वाले emails में **inline styles** होते हैं क्योंकि email clients external CSS नहीं मानते। **Swiggy** का delivery progress bar `style="width: 65%"` inline रखता है क्योंकि value live data से आती है।

---

## 💻 Live Code Example

Save both files in the same folder (`index.html` and `styles.css`) and open `index.html`.

```html
<!-- index.html -->
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Three Ways to Add CSS</title>

  <!-- 3) EXTERNAL: linked file (best for real projects) -->
  <link rel="stylesheet" href="styles.css">

  <!-- 2) INTERNAL: page-level styles. Comes AFTER the link, so it wins ties. -->
  <style>
    .demo p { margin: 6px 0; }
    .internal { background: #bbdefb; padding: 8px; }

    /* Same specificity as the rule in styles.css (.box p) but LATER, so it wins */
    .tie { color: green; }
  </style>
</head>
<body>
  <h1>Ways to add CSS</h1>

  <div class="demo">
    <!-- Uses external CSS only -->
    <p class="external">External: styled by styles.css</p>

    <!-- Uses internal <style> -->
    <p class="internal">Internal: styled by the style block in the head</p>

    <!-- 1) INLINE: style attribute (beats both for this element) -->
    <p class="external" style="background: #ffe0b2; color: #b71c1c; padding: 8px;">
      Inline: style attribute wins over the class rules
    </p>

    <!-- Cascade tie: styles.css says .tie is blue, the later internal rule says green -->
    <p class="tie">Tie: external says blue, internal (later) says green</p>

    <!-- Legit use of inline: a dynamic value -->
    <div class="progress"><div class="bar" style="width: 65%"></div></div>

    <!-- Inline cannot do :hover or media queries: use a class instead -->
    <button class="btn">Hover me (class-based, hover works)</button>
    <button style="background:#999;color:#fff;border:0;padding:8px 14px">Inline (no hover possible)</button>
  </div>

  <script>
    // JS can add CSS too
    const p = document.querySelector('.external');
    p.style.fontWeight = 'bold';                    // inline via JS
    document.documentElement.style.setProperty('--brand', '#6a1b9a'); // change a CSS variable
  </script>
</body>
</html>
```

```css
/* styles.css  (external file) */
*, *::before, *::after { box-sizing: border-box; }

:root { --brand: #fc8019; }

body { font-family: system-ui, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
h1 { color: var(--brand); }

/* Applies to every .external paragraph */
.external { background: #c8e6c9; padding: 8px; }

/* Tie demo: same specificity as the later internal rule. Loses (earlier). */
.tie { color: blue; }

/* Progress bar: width is supplied dynamically via inline style */
.progress { background: #ddd; height: 14px; border-radius: 7px; overflow: hidden; margin: 12px 0; }
.bar { height: 100%; background: var(--brand); }

/* Pseudo-classes and states need real CSS, not inline */
.btn { background: var(--brand); color: #fff; border: 0; padding: 8px 14px; cursor: pointer; border-radius: 6px; }
.btn:hover { filter: brightness(0.9); }

/* Load-by-condition example (print) goes in <link media="print"> or here: */
@media print { .btn { display: none; } }
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. External CSS = global stylesheet import (Next.js app/layout.jsx)
import './globals.css';              // bundled, minified, split per route

// 2. Internal-style equivalent: CSS Modules / <style jsx> / CSS-in-JS
import styles from './Card.module.css';   // scoped class names
<div className={styles.card} />

// 3. Inline style = style prop (object, camelCase). Good for dynamic values:
function Progress({ percent }) {
  return (
    <div className="progress">
      <div className="bar" style={{ width: `${percent}%` }} />   {/* dynamic */}
    </div>
  );
}

// 4. Set CSS variables inline for theming:
<div style={{ '--brand': theme.color }} className="card" />

// 5. Tailwind = utility classes in an external generated stylesheet
<button className="bg-orange-500 hover:bg-orange-600 px-4 py-2 rounded">Buy</button>

// 6. Note: React inline styles cannot use :hover, @media or ::before.
//    Use className (Tailwind/CSS Modules) for those.
// 7. Next.js <link> in <head>? Not needed, import the CSS and Next injects it.
//    For a third-party stylesheet use: <link rel="stylesheet" href="..."> in layout.
```

---

## ⚫ Interview Questions + Answers

**Q1: What are the three ways to add CSS and which is best?**
A1: Inline (`style` attribute), Internal (`<style>` in the head) and External (`<link rel="stylesheet">`). External is best for most sites: reusable across pages, cached by the browser, easy to maintain and keeps HTML clean.

**Q2: Which has the highest priority: inline, internal or external?**
A2: Inline styles beat selector-based rules regardless of where those rules live (specificity). Internal vs external have no inherent priority; with equal specificity, whichever appears later in the document wins. `!important` in a stylesheet beats a normal inline style.

**Q3: What are the drawbacks of inline CSS?**
A3: No reuse, no pseudo-classes/pseudo-elements/media queries, hard to override (needs `!important`), larger HTML, harder maintenance, and blocked by a strict Content Security Policy unless allowed. Still fine for dynamic values and HTML emails.

**Q4: `<link>` vs `@import`?**
A4: `<link>` lets the browser fetch stylesheets in parallel. `@import` inside CSS is discovered only after the parent CSS is downloaded, causing sequential loading and a slower page. Prefer `<link>` or a bundler.

**Q5: Why is external CSS considered render-blocking and how do you reduce its impact?**
A5: The browser will not paint until it builds the CSSOM, so it waits for linked stylesheets. Reduce impact by minifying, compressing and caching, inlining critical CSS, splitting non-critical CSS (`media` attribute or preload swap), and removing unused rules.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Styling everything inline
```html
<!-- WRONG -->
<button style="background:blue;color:white;padding:8px">Buy</button>
<!-- CORRECT -->
<button class="btn">Buy</button>
```

❌ **Mistake 2:** Wrong path or missing `rel`
```html
<!-- WRONG -->
<link href="styles.css">
<!-- CORRECT -->
<link rel="stylesheet" href="styles.css">
```

❌ **Mistake 3:** Putting `<link>` at the end of `<body>`
✅ **Correct way:** Put in `<head>` so the page does not flash unstyled content.

❌ **Mistake 4:** Using `@import` chains
```css
/* WRONG: sequential downloads */
@import url("base.css");
/* CORRECT: <link> tags or bundle with a build tool */
```

❌ **Mistake 5:** `<style>` placed inside `<body>` scattered everywhere
✅ **Correct way:** Keep styles in head/external files; `<style>` in body is allowed but can cause repaint and is harder to maintain.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Inline CSS | style attribute on element | Element पर style attribute |
| Internal CSS | `<style>` block in the page | Page में style block |
| External CSS | Separate .css file | अलग CSS file |
| `<link>` | Tag to attach a stylesheet | Stylesheet जोड़ने वाला tag |
| @import | CSS rule to include a file | CSS में file जोड़ना (धीमा) |
| Critical CSS | Above-the-fold styles inlined | ऊपरी हिस्से की ज़रूरी CSS |
| Source order | Later rule wins on a tie | बाद वाला rule जीतता है |
| Render-blocking | Delays first paint | पहला paint रोकना |
| Minify | Remove whitespace/comments | अनावश्यक हिस्सा हटाना |

---

## ⚡ 3-Line Summary
**English:**
1. CSS can be added inline (`style` attribute), internal (`<style>`), or external (`<link rel="stylesheet">`); external is the standard.
2. Inline beats selector rules; internal and external tie on specificity, so source order decides; avoid `@import`.
3. In React/Next.js import global CSS or CSS Modules, use Tailwind classes, and use the `style` prop only for dynamic values.

**Hindi:**
1. CSS inline (`style`), internal (`<style>`) या external (`<link rel="stylesheet">`) जोड़ी जाती है; external standard है।
2. Inline selector rules को हराता है; internal और external में source order तय करता है; `@import` से बचो।
3. React/Next.js में global CSS या CSS Modules import करो, Tailwind classes लगाओ, और `style` prop सिर्फ dynamic values के लिए।

---

## ➡️ Next Topic
**49. CSS Selectors (element, class, id, universal)** — अब सीखें कि किस element पर style लगानी है यह कैसे चुनें।
