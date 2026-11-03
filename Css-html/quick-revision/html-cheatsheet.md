# HTML Cheatsheet (Topics 1-45)
Quick revision: gist + key snippet + हिंदी hint. Full notes: `../html/basic`, `../html/intermediate`, `../html/advanced`.

---

## A. BASIC (1-20)

### 1. What is HTML / how browser renders
HTML = markup (structure), not a programming language. Pipeline: HTML -> DOM, CSS -> CSSOM -> render tree -> layout -> paint -> composite.
```
HTML -> DOM ┐
CSS  -> CSSOM ┴-> Render Tree -> Layout -> Paint -> Composite
```
हिंदी: HTML = ढाँचा; browser DOM + CSSOM मिलाकर screen बनाता है।

### 2. Document structure
DOCTYPE -> `<html lang>` -> `<head>` (metadata) -> `<body>` (visible). No DOCTYPE = quirks mode; no viewport = broken mobile.
```html
<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Page</title></head>
<body>...</body>
</html>
```
हिंदी: head = छुपा metadata, body = दिखने वाला content।

### 3. Semantic HTML
Tags describe meaning: `header nav main section article aside footer`. Free landmarks, SEO, cleaner code. One `<main>` per page.
```html
<header><nav>...</nav></header>
<main><article><h1>Title</h1></article><aside>...</aside></main>
<footer>...</footer>
```
हिंदी: Semantic tag = अर्थ बताता है, सिर्फ look नहीं।

### 4. Non-semantic (div, span)
`div` (block) and `span` (inline) have no meaning; use only when nothing semantic fits. Never make buttons/links from div.
```html
<div class="card"><span class="badge">New</span></div>
```
हिंदी: div/span आखिरी option हैं, पहले semantic tag।

### 5. Semantic vs non-semantic
Semantic gives meaning to screen readers/search engines plus free behaviour (keyboard, forms, links). Fix wrong tags, do not pile on ARIA.
| Div soup | Semantic |
|---|---|
| `<div onclick>` | `<button>` |
| `<div class="nav">` | `<nav>` |

हिंदी: सही tag = accessibility + SEO मुफ़्त।

### 6. Headings h1-h6
One `h1`, then `h2` sections, `h3` sub-sections, no skipped levels. Choose level by structure, size by CSS.
```html
<h1>Site</h1><h2>Section</h2><h3>Sub</h3>
```
हिंदी: Heading = page की रूपरेखा; style के लिए नहीं।

### 7. Paragraphs, links, images
`<p>` text, `<a href>` links (`rel="noopener"` with `_blank`), `<img>` with meaningful `alt` + `width`/`height`. Whitespace collapses; use CSS not `<br>`.
```html
<a href="/docs" target="_blank" rel="noopener">Docs</a>
<img src="a.jpg" alt="Team photo" width="600" height="400" loading="lazy">
```
हिंदी: alt और width/height हमेशा दो।

### 8. Lists ul / ol / dl
`ul` unordered, `ol` ordered, `dl` term-description. Only `li` directly inside `ul/ol`. Menus are lists too.
```html
<nav><ul><li><a href="/">Home</a></li></ul></nav>
<dl><dt>HTML</dt><dd>Markup</dd></dl>
```
हिंदी: Menu भी असल में list है।

### 9. Tables
For real row/column data: `table > thead/tbody/tfoot > tr > th/td`, plus `caption`, `scope`, `colspan/rowspan`. Never for layout; wide tables get `overflow-x: auto` wrapper.
```html
<table><caption>Sales</caption>
<thead><tr><th scope="col">Month</th><th scope="col">Rs</th></tr></thead>
<tbody><tr><td>Jan</td><td>10</td></tr></tbody></table>
```
हिंदी: Table सिर्फ data के लिए, layout के लिए नहीं।

### 10. Forms
`<form>` collects named controls; each needs `<label for>` + `name`. Button default `type="submit"`.
```html
<form action="/login" method="post">
  <label for="email">Email</label>
  <input id="email" name="email" type="email" required>
  <button>Login</button>
</form>
```
हिंदी: name = server को जाने वाली key; label = id से जुड़ा।

### 11. Form attributes
`action` = where, `method` = GET (URL, read-only) / POST (body, changes data), `enctype` = body format (files need multipart). No passwords in GET.
| enctype | Use |
|---|---|
| `application/x-www-form-urlencoded` | default |
| `multipart/form-data` | file upload |

हिंदी: GET = URL में data, POST = body में।

### 12. Input types
`text email password tel number date checkbox radio file range hidden`. Right type = free validation + mobile keyboard. Radios share one `name`; unchecked checkbox sends nothing. OTP/phone: text + `inputmode`, not number.
```html
<input type="radio" name="plan" value="pro"> <input type="file" accept="image/*">
```
हिंदी: सही type = सही keyboard और validation।

### 13. Form validation
HTML5 attrs: `required pattern min max minlength type`. Style with `:valid/:invalid/:user-invalid`; custom via Constraint Validation API. Client validation is UX only; validate on server.
```html
<input type="text" required minlength="3" pattern="[A-Za-z]+">
```
```js
input.setCustomValidity("Bad value"); form.checkValidity();
```
हिंदी: Client validation सिर्फ UX; असली check server पर।

### 14. Attributes
`name="value"` pairs. `id` unique, `class` reusable, `name` form key, `placeholder` hint only, `value` actual data. Boolean attrs true when present. JSX: `className`, `htmlFor`.
हिंदी: id एक बार, class बार-बार; placeholder label नहीं।

### 15. Meta tags
In `<head>`: `charset` first, `viewport`, `description`, `og:*`. Next.js: `metadata` / `generateMetadata`.
```html
<meta name="description" content="Short summary">
<meta name="viewport" content="width=device-width, initial-scale=1">
```
हिंदी: Meta = browser/SEO/social के लिए छुपी जानकारी।

### 16. Comments
`<!-- ... -->` ignored but public in View Source: no secrets. No nesting. CSS `/* */`, JS `//`, JSX `{/* */}`.
हिंदी: Comment में secret कभी नहीं।

### 17. Entities
`&lt; &gt; &amp; &nbsp; &copy;` show reserved characters. `&nbsp;` for keeping words together, not layout. Escaping user text prevents XSS.
```html
&lt;div&gt; &copy; 2026
```
हिंदी: Special char दिखाने के लिए entity।

### 18. Inline vs block
Block = new line, full width. Inline = flows in text, ignores width/height. `inline-block` = flows + sizable. No block inside `<p>` (React hydration errors).
| | Block | Inline |
|---|---|---|
| Example | div p h1 ul | span a strong img |
| width/height | yes | no |

हिंदी: Block नई line लेता है, inline text में बहता है।

### 19. HTML5 new elements
Semantic tags, `details/summary`, `dialog`, `progress/meter`, `time`, `mark`, native `audio/video/canvas/svg`, form helpers. Removed: `center`, `font`.
```html
<details><summary>FAQ</summary>Answer</details>
<dialog id="d">Hi</dialog>
```
हिंदी: Native element = बिना JS के behaviour।

### 20. Audio / video
Several `<source>` formats, `controls`, `poster`, `preload`, `<track>` subtitles. Autoplay only when muted.
```html
<video controls poster="p.jpg" autoplay muted loop playsinline>
  <source src="v.webm" type="video/webm"><source src="v.mp4" type="video/mp4">
  <track kind="subtitles" src="en.vtt" srclang="en">
</video>
```
हिंदी: Autoplay के लिए muted ज़रूरी।

---

## B. INTERMEDIATE (21-35)

### 21. DOM
Live node tree built from HTML; JS reads/changes it. Use `querySelector`, `textContent`, `classList`, `createElement`, event delegation; avoid `innerHTML` with user data. Server has no `document`.
```js
const el = document.querySelector(".btn");
el.classList.toggle("on"); el.textContent = "Hi";
```
हिंदी: DOM = HTML का live tree; JS से बदलता है।

### 22. HTML accessibility
Semantic first, real `<button>/<a>`, `alt`, `<label>`. ARIA only when native fails (changes announcement, not behaviour). Visible focus, 4.5:1 contrast.
```html
<button aria-label="Close" aria-expanded="false">X</button>
```
हिंदी: पहले native tag, ARIA बाद में।

### 23. SEO basics
Unique `<title>` + description, one `h1`, semantic tags, crawlable `<a href>`, image `alt`, canonical, `lang`; sitemap.xml, robots.txt; SSR/SSG in Next.js.
```html
<link rel="canonical" href="https://site.com/page">
```
हिंदी: Crawler को पूरा HTML दिखना चाहिए।

### 24. data-* attributes
Custom string metadata, read via `element.dataset` (kebab -> camelCase). Used for delegation, CSS state hooks, test ids. Visible to users: no secrets.
```html
<button data-user-id="42" data-state="open"></button>
```
```js
btn.dataset.userId; // "42"
```
हिंदी: data-* = custom string; secret नहीं रखना।

### 25. iframe
Embeds isolated page (YouTube, Maps, payments). Give `title`, `loading="lazy"`, `sandbox`. Cross-origin talk via `postMessage` (check origin); servers block with `X-Frame-Options`/CSP.
```html
<iframe src="https://..." title="Map" loading="lazy" sandbox="allow-scripts"></iframe>
```
हिंदी: iframe = page के अंदर अलग page; sandbox लगाओ।

### 26. Canvas
Pixel surface drawn with JS (games, charts). Attribute width/height = real resolution; CSS only scales (`devicePixelRatio`). Opaque to screen readers: add `aria-label`, fallback text.
```js
const ctx = canvas.getContext("2d"); ctx.fillRect(10, 10, 50, 50);
```
हिंदी: Canvas = pixels; accessible नहीं by default।

### 27. SVG
Vector shapes: crisp at any size, small file. Inline SVG is styleable by CSS/JS; use `viewBox` and `currentColor`. `<title>`/`aria-label` meaningful, `aria-hidden` decorative.
```html
<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><circle cx="12" cy="12" r="10"/></svg>
```
हिंदी: SVG = vector, हर size पर साफ।

### 28. link tag
`<link>` in head: stylesheet, icon, manifest, canonical. `preload` (critical now), `preconnect` (early connection), `prefetch` (next page). CSS is render-blocking.
```html
<link rel="stylesheet" href="app.css">
<link rel="preload" href="font.woff2" as="font" crossorigin>
<link rel="preconnect" href="https://cdn.example.com">
```
हिंदी: preload सिर्फ ज़रूरी चीज़ों का।

### 29. script defer vs async
Plain script blocks parsing. `defer` = after parsing, in order (app code). `async` = ASAP, any order (analytics). Modules deferred by default.
```html
<script src="app.js" defer></script>
<script src="ga.js" async></script>
```
हिंदी: defer = क्रम में, parsing के बाद; async = जब मिले तब।

### 30. template tag
Parsed but not rendered, inert until cloned.
```js
const node = tpl.content.cloneNode(true);
node.querySelector("h3").textContent = title; list.append(node);
```
हिंदी: template = native component का ढाँचा।

### 31. localStorage / sessionStorage
String key-value, sync, ~5 MB, per-origin. local persists; session dies with tab. Readable by any script: no secrets. JSON for objects, `useEffect` in Next.js.
```js
localStorage.setItem("t", JSON.stringify(obj)); JSON.parse(localStorage.getItem("t"));
```
हिंदी: local = स्थायी, session = tab तक।

### 32. Cookies vs storage
| | Cookie | localStorage | sessionStorage |
|---|---|---|---|
| Sent to server | auto | no | no |
| Size | ~4 KB | ~5 MB | ~5 MB |
| Lifetime | expiry | forever | tab |
| JS-hidden | HttpOnly yes | no | no |

Auth = HttpOnly cookie; prefs = localStorage; temp = sessionStorage.
हिंदी: Auth के लिए HttpOnly cookie।

### 33. Multipart file upload
Needs `method="post"`, `enctype="multipart/form-data"`, named `<input type="file">`. With fetch + `FormData` never set Content-Type manually. `accept` is UX only.
```html
<form method="post" enctype="multipart/form-data"><input type="file" name="avatar" accept="image/*"></form>
```
हिंदी: Content-Type हाथ से मत लगाओ।

### 34. picture / responsive images
`srcset` + `sizes` = browser picks width; `<picture>` = formats/art direction. Keep `<img alt width height>` fallback. Next.js: `next/image`.
```html
<picture><source srcset="a.avif" type="image/avif"><img src="a.jpg" alt="..." width="800" height="450"></picture>
<img srcset="s.jpg 480w, l.jpg 1200w" sizes="(min-width:768px) 50vw, 100vw" src="l.jpg" alt="">
```
हिंदी: srcset = सही size, picture = सही format।

### 35. Lazy loading
`loading="lazy"` defers off-screen images/iframes. Set width/height; never lazy-load hero/LCP image. `IntersectionObserver` for custom; `React.lazy` / `next/dynamic` for JS.
```html
<img src="x.jpg" alt="" width="400" height="300" loading="lazy">
```
हिंदी: Hero image कभी lazy नहीं।

---

## C. ADVANCED (36-45)

### 36. Critical rendering path
DOM + CSSOM -> render tree -> layout -> paint -> composite. CSS blocks rendering, scripts block parsing: `defer/async`, inline critical CSS, fewer bytes.
हिंदी: CSS rendering रोकती है, script parsing रोकता है।

### 37. Reflow vs repaint
Reflow = recompute geometry (costly, implies repaint); repaint = redraw pixels. `transform`/`opacity` skip both. Batch DOM reads then writes; use `requestAnimationFrame`.
```js
const h = el.offsetHeight; el.style.height = h + 10 + "px"; // read, then write
```
हिंदी: पहले सब read, फिर सब write।

### 38. HTML performance
`defer` scripts, preload critical only, inline critical CSS, image width/height, WebP/AVIF + `srcset`, lazy below fold. Measure Core Web Vitals: LCP, INP, CLS (Lighthouse).
हिंदी: LCP, INP, CLS तीन metrics।

### 39. Progressive enhancement vs graceful degradation
PE: start with working HTML, add layers. GD: build full, add fallbacks. Use `@supports` and feature detection, not browser sniffing.
```css
@supports (display: grid) { .layout { display: grid; } }
```
हिंदी: PE नीचे से ऊपर, GD ऊपर से नीचे।

### 40. Cross-browser compatibility
Define targets, standard code, check MDN/caniuse, fallbacks + `@supports`, Autoprefixer, Babel, polyfills. Test real browsers (iOS Safari). No UA sniffing.
हिंदी: Feature detect करो, browser नहीं।

### 41. Web accessibility (WCAG)
POUR: Perceivable, Operable, Understandable, Robust; target level AA. Labels, alt, headings, landmarks, real buttons, visible focus, 4.5:1 contrast, keyboard. Test: keyboard, screen reader, axe/Lighthouse.
हिंदी: POUR = चार सिद्धांत।

### 42. Open Graph tags
Control share-card title/description/image. Absolute https image (1200x630), `property="og:*"`, `twitter:card`.
```html
<meta property="og:title" content="Title"><meta property="og:image" content="https://site.com/og.png">
<meta name="twitter:card" content="summary_large_image">
```
हिंदी: Link share का preview OG से तय।

### 43. Structured data (Schema.org)
JSON-LD describes content for rich results (stars, price, breadcrumbs). Must match visible content; validate with Rich Results Test.
```html
<script type="application/ld+json">{"@context":"https://schema.org","@type":"Product","name":"Shoe"}</script>
```
हिंदी: JSON-LD = search engine के लिए label।

### 44. HTML security (XSS, CSP)
XSS = attacker JS in your page. Prevent: escape, `textContent`, DOMPurify. CSP (nonce, no `unsafe-inline`) second layer; cookies `HttpOnly Secure SameSite`; `rel="noopener"`, SRI, iframe `sandbox`. React risk: `dangerouslySetInnerHTML`.
```
Content-Security-Policy: default-src 'self'; script-src 'nonce-abc123'
```
हिंदी: User input कभी innerHTML में नहीं।

### 45. Shadow DOM
Own encapsulated DOM + CSS via `attachShadow()`. Only inherited props, CSS variables, `::part()`, slots cross the boundary; events need `composed: true`.
```js
const root = host.attachShadow({ mode: "open" }); root.innerHTML = "<style>p{color:red}</style><p>Hi</p>";
```
हिंदी: Shadow DOM = style बाहर से अलग।

---

## Top 20 HTML interview questions (quick list)
1. Semantic vs non-semantic HTML; why it matters (SEO, a11y). -> #3-5
2. What happens when you type a URL / how does browser render HTML? -> #1, #36
3. `defer` vs `async` scripts. -> #29
4. `localStorage` vs `sessionStorage` vs cookies. -> #31-32
5. `<div>` vs `<span>`; block vs inline vs inline-block. -> #4, #18
6. Why one `h1` and no skipped heading levels? -> #6
7. GET vs POST; what is `enctype`? How to upload a file? -> #11, #33
8. Difference between `id`, `class`, `name`; `placeholder` vs `label`. -> #14
9. HTML5 new elements and APIs. -> #19-20, #26-27
10. `srcset`/`sizes` vs `<picture>`; how to serve responsive images? -> #34
11. Lazy loading: what, when not to use it (LCP). -> #35
12. Reflow vs repaint; how to avoid layout thrashing. -> #37
13. How do you make a page accessible (WCAG, ARIA rules)? -> #22, #41
14. What is DOCTYPE / quirks mode / viewport meta? -> #2, #15
15. Explain XSS and CSP; how does React protect you? -> #44
16. `<link rel="preload|preconnect|prefetch">` differences. -> #28
17. What is Shadow DOM / template / web components? -> #30, #45
18. Progressive enhancement vs graceful degradation. -> #39
19. SEO basics in HTML: title, meta, canonical, JSON-LD, Open Graph. -> #23, #42-43
20. Client-side vs server-side form validation; Constraint Validation API. -> #13
