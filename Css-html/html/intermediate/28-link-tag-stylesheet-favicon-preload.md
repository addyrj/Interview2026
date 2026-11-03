# 28. Link Tag (stylesheet, favicon, preload)
# हिंदी में: Link Tag — बाहरी Resources को Page से जोड़ना

---

## 🔵 Simple Definition (English)
`<link>` is a void element placed in `<head>` that connects the current document to an **external resource**. The `rel` attribute says the relationship: `stylesheet` (CSS), `icon` (favicon), `preload` / `preconnect` / `prefetch` (performance hints), `canonical` (SEO), `manifest` (PWA).

## 🔵 सरल परिभाषा (Hindi)
`<link>` एक void element है जो `<head>` में रखा जाता है और current document को **किसी बाहरी resource** से जोड़ता है। `rel` attribute बताता है कि रिश्ता क्या है: `stylesheet` (CSS), `icon` (favicon), `preload` / `preconnect` / `prefetch` (performance hints), `canonical` (SEO), `manifest` (PWA)।

---

## 🔴 Problem it Solves
```
BEFORE:
  - All CSS written inside <style> on every page = duplicated, never cached.
  - Browser discovers fonts/hero image LATE (only after CSS is parsed) -> slow first paint.
  - Browser tab shows a blank default icon; search engines see duplicate URLs.

WITH <link>:
  - One style.css cached once, shared across every page.
  - rel="preload" tells the browser "fetch this important file NOW".
  - rel="icon" gives your brand icon in tab/bookmarks.
  - rel="canonical" tells Google which URL is the real one.
```

## 🔴 यह क्यों बना? (Hindi)
```
पहले:
  - हर page पर <style> में पूरा CSS = duplicate, cache नहीं होता।
  - Fonts/hero image देर से मिलते थे (CSS parse होने के बाद) -> first paint slow।
  - Tab में default खाली icon; search engine को duplicate URLs दिखते।

<link> के साथ:
  - एक style.css, एक बार cache, सब pages में shared।
  - rel="preload" से browser को कहना "ये ज़रूरी file अभी लाओ"।
  - rel="icon" से tab/bookmark में brand icon।
  - rel="canonical" से Google को असली URL बताना।
```

---

## 🟢 How it Works — Step by Step

```
1. Parser meets <link rel="stylesheet" href="style.css"> in <head>.
2. Browser starts download. Stylesheets are RENDER-BLOCKING: no paint until CSS is ready
   (otherwise the user would see an unstyled flash, FOUC).
3. It does NOT block HTML parsing itself (but blocks later scripts that may read styles).
4. CSSOM is built, then combined with the DOM into the render tree.

COMMON rel VALUES:
  stylesheet   <link rel="stylesheet" href="app.css">
  icon         <link rel="icon" href="/favicon.ico" sizes="32x32">
               <link rel="icon" href="/icon.svg" type="image/svg+xml">
               <link rel="apple-touch-icon" href="/apple-icon.png">
  preload      <link rel="preload" href="/font.woff2" as="font" type="font/woff2" crossorigin>
               HIGH priority, current page, MUST declare as="..."
  preconnect   <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
               open DNS+TCP+TLS early to another origin
  dns-prefetch cheaper cousin: only DNS lookup
  prefetch     LOW priority, for the NEXT page the user will probably visit
  modulepreload preload an ES module
  canonical    <link rel="canonical" href="https://site.com/page">
  manifest     <link rel="manifest" href="/manifest.webmanifest">
  alternate    <link rel="alternate" hreflang="hi" href="/hi/">

MEDIA TRICK (non-blocking CSS): 
  <link rel="stylesheet" href="print.css" media="print">
  -> browser still downloads it, but at low priority and it does not block rendering
     for screen. 
  Also media="(min-width: 900px)" for conditional CSS.

OTHER ATTRIBUTES:
  crossorigin (required for fonts, even same-origin), integrity (SRI hash),
  fetchpriority="high|low", disabled, title (alternate stylesheets)
```

## 🟢 कैसे काम करता है? (Hindi)

```
1. Parser को <head> में <link rel="stylesheet"> मिलता है।
2. Download शुरू। Stylesheet RENDER-BLOCKING होती है: CSS आने तक paint नहीं होता
   (वरना बिना style का flash दिखता, FOUC)।
3. HTML parsing नहीं रुकती, पर बाद के scripts रुक सकते हैं।
4. CSSOM बनता है, DOM के साथ मिलकर render tree बनता है।

ज़रूरी rel values:
  stylesheet  = CSS file          icon = favicon
  preload     = इसी page के लिए ज़रूरी file अभी लाओ (as="..." देना ज़रूरी)
  preconnect  = दूसरे server से connection पहले ही खोल दो
  prefetch    = अगले page के लिए, low priority में पहले से लाओ
  canonical   = SEO का असली URL
  manifest    = PWA की file

Trick: media="print" वाली CSS screen rendering को block नहीं करती।
Fonts के लिए preload में crossorigin ज़रूर लगाएँ, वरना font दो बार download होगा।
```

---

## 🟡 Real World Example
**Zomato / Swiggy / Amazon** page source: a `<link rel="stylesheet">` for the main CSS, `<link rel="preconnect" href="https://fonts.gstatic.com">` for Google Fonts, `<link rel="preload" as="image" href="hero.webp">` so the hero banner (the Largest Contentful Paint element) starts downloading immediately, `<link rel="icon">` for the tab icon, `<link rel="canonical">` to avoid duplicate-URL SEO issues (`?utm_source=...`), and `<link rel="manifest">` for "Add to Home Screen" on Swiggy's PWA.

## 🟡 Real Example Hindi mein
**Zomato / Swiggy / Amazon** के page source में: main CSS के लिए `<link rel="stylesheet">`, Google Fonts के लिए `<link rel="preconnect">`, hero banner (जो Largest Contentful Paint element है) तुरंत लाने के लिए `<link rel="preload" as="image">`, tab icon के लिए `rel="icon"`, duplicate-URL SEO issue (`?utm_source=...`) से बचने के लिए `rel="canonical"`, और "Add to Home Screen" के लिए `rel="manifest"` मिलेगा।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Link Tag Demo</title>

  <!-- 1. Open connection to font servers early (crossorigin needed for font files) -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>

  <!-- 2. Google Font stylesheet. display=swap shows fallback text while font loads -->
  <link rel="stylesheet"
        href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap">

  <!-- 3. Our main CSS (render-blocking: intentional, prevents unstyled flash) -->
  <link rel="stylesheet" href="style.css">

  <!-- 4. Print CSS: downloaded at low priority, applies only when printing -->
  <link rel="stylesheet" href="print.css" media="print">

  <!-- 5. Favicons: modern SVG, ICO fallback, iOS home-screen icon -->
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'><text y='14' font-size='14'>🚀</text></svg>">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">

  <!-- 6. Preload hero image (LCP) so it starts before the parser reaches <img> -->
  <link rel="preload" as="image" href="https://picsum.photos/id/1015/1200/500" fetchpriority="high">

  <!-- 7. SEO: preferred URL -->
  <link rel="canonical" href="https://example.com/link-demo">

  <!-- 8. Hint: next page likely needed (low priority) -->
  <link rel="prefetch" href="/checkout.html">
</head>
<body>
  <header class="hero">
    <h1>Fast pages start in &lt;head&gt;</h1>
    <p>Open DevTools &gt; Network to see priorities.</p>
  </header>
  <img class="banner" src="https://picsum.photos/id/1015/1200/500" alt="Mountain river landscape" width="1200" height="500">
</body>
</html>
```

```css
/* style.css */
*, *::before, *::after { box-sizing: border-box; }

body {
  margin: 0;
  /* Poppins comes from the Google link; fallback to system fonts if it fails */
  font-family: "Poppins", system-ui, sans-serif;
  color: #222;
}
.hero { padding: 32px 20px; background: #fff3e0; }
.hero h1 { margin: 0 0 8px; }
.banner { display: block; width: 100%; height: auto; }   /* width+height attrs avoid layout shift */
```

```css
/* print.css: only applied when printing */
body { font-family: serif; color: #000; }
.banner { display: none; }   /* save ink */
```

---

## 🟠 React/Next.js Connection

```jsx
// Next.js App Router: app/layout.jsx
// You rarely write <link> by hand; Next generates them.

import { Poppins } from "next/font/google";          // self-hosts font + preloads it automatically
const poppins = Poppins({ subsets: ["latin"], weight: ["400", "600"], display: "swap" });

export const metadata = {
  icons: { icon: "/icon.svg", apple: "/apple-touch-icon.png" },   // -> <link rel="icon">
  alternates: { canonical: "https://example.com/" },              // -> <link rel="canonical">
  manifest: "/manifest.webmanifest",                              // -> <link rel="manifest">
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={poppins.className}>
      <body>{children}</body>
    </html>
  );
}
```
- `next/image` with the `priority` prop adds a preload for the LCP image.
- `next/link` auto-**prefetches** routes in the viewport (the idea behind `rel="prefetch"`).
- React 19 can render `<link rel="stylesheet" precedence="default">` inside components and hoists it to head; `ReactDOM.preload()` / `preconnect()` APIs exist too. Check your React version before relying on these.
- Tailwind: one compiled CSS file, linked automatically.

---

## ⚫ Interview Questions + Answers

Q1: Is `<link rel="stylesheet">` render-blocking? Does it block HTML parsing?
A1: It blocks rendering (browser will not paint until CSSOM is ready) but not HTML parsing. It can however block later synchronous scripts, since scripts may query styles.

Q2: preload vs prefetch vs preconnect?
A2: `preload` = high-priority fetch of a resource needed on THIS page soon (needs `as`). `prefetch` = low-priority fetch for a FUTURE navigation. `preconnect` = only open the connection (DNS/TCP/TLS) to an origin, no download.

Q3: Why must font preload have `crossorigin`?
A3: Fonts are fetched in CORS mode. Without `crossorigin` the preloaded request has a different mode and the browser will not reuse it, so the font downloads twice.

Q4: How do you load non-critical CSS without blocking render?
A4: Use `media` queries (`media="print"` or conditional), split CSS per route, inline the critical CSS, and load the rest with the `media="print" onload="this.media='all'"` pattern (or framework tooling).

Q5: What is `rel="canonical"` for?
A5: It tells search engines which URL is the master copy when the same content is reachable via several URLs (query params, http/https, trailing slashes), consolidating SEO ranking.

---

## 🔷 Common Mistakes to Avoid
❌ Mistake 1: `<link rel="preload">` without `as`.
✅ Correct way: Always add `as="font|image|style|script"` (and `type`) so the browser sets priority and it matches the real request.

❌ Mistake 2: Preloading everything.
✅ Correct way: Preload only the 1-3 resources critical to first render (LCP image, main font); too many hints compete for bandwidth.

❌ Mistake 3: `@import` inside CSS to load other CSS.
✅ Correct way: Use parallel `<link>` tags (or bundle); `@import` creates a serial waterfall.

❌ Mistake 4: Self-closing `<link ... />` confusion or placing `<link rel=stylesheet>` at the end of body.
✅ Correct way: `<link>` is void (no closing tag), put stylesheets in `<head>` to avoid flash of unstyled content.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| rel | Relationship type of the link | Link का रिश्ता/प्रकार |
| render-blocking | Delays first paint | First paint रोकने वाला |
| preload | Fetch critical resource now | ज़रूरी file अभी लाओ |
| prefetch | Fetch for future page | अगले page के लिए पहले से लाओ |
| preconnect | Open connection early | Connection पहले खोलना |
| favicon | Tab/bookmark icon | Tab का छोटा icon |
| canonical | Preferred URL for SEO | SEO का असली URL |
| FOUC | Flash of unstyled content | बिना style का flash |

---

## ⚡ 3-Line Summary
English: `<link>` in `<head>` connects external resources: CSS, icons, manifest, canonical URL.
`preload`, `preconnect` and `prefetch` are performance hints with different priorities.
CSS is render-blocking, so keep it lean; preload only what is critical.

Hindi: `<head>` की `<link>` बाहरी resources जोड़ती है: CSS, icons, manifest, canonical URL।
`preload`, `preconnect` और `prefetch` अलग-अलग priority वाले performance hints हैं।
CSS render-blocking होती है, इसलिए छोटी रखें; सिर्फ ज़रूरी चीज़ें preload करें।

---

## ➡️ Next Topic
**29. Script Tag (defer vs async)** — CSS के बाद JavaScript load करना: कौन सा तरीका page को block करता है और कौन सा नहीं।

---
