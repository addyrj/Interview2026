# 2. HTML Document Structure (DOCTYPE, head, body)
# हिंदी में: HTML Document का Structure (DOCTYPE, head, body)

---

## 🔵 Simple Definition (English)
Every HTML page has the same skeleton: `<!DOCTYPE html>` (tells the browser the HTML version), `<html>` (root), `<head>` (invisible info: title, meta, CSS links) and `<body>` (everything the user sees).

## 🔵 सरल परिभाषा (Hindi)
हर HTML page का skeleton एक जैसा होता है: `<!DOCTYPE html>` (browser को HTML version बताता है), `<html>` (root), `<head>` (छुपी जानकारी: title, meta, CSS links) और `<body>` (जो user को दिखता है)।

---

## 🔴 Problem it Solves
```
WITHOUT a proper structure:
  - No DOCTYPE      -> browser enters QUIRKS MODE (old IE-style box model, odd layouts)
  - No charset      -> Hindi / emoji show as garbage: "à¤¨à¤®à¤¸à¥..."
  - No viewport     -> mobile shows a tiny zoomed-out desktop page
  - No <title>      -> tab says "index.html", bad for SEO and bookmarks
  - No lang         -> screen readers pronounce text in the wrong accent

WITH a proper structure:
  - Standards mode, correct text, mobile-friendly, accessible, SEO-ready
```

## 🔴 यह क्यों बना? (Hindi)
```
सही structure के बिना:
  - DOCTYPE नहीं     -> browser QUIRKS MODE में चला जाता है (पुराने browsers जैसा layout)
  - charset नहीं     -> हिंदी / emoji टूटे-फूटे अक्षर दिखते हैं
  - viewport नहीं    -> mobile पर छोटा desktop page दिखता है
  - <title> नहीं     -> tab में "index.html" दिखता है, SEO ख़राब
  - lang नहीं        -> screen reader गलत उच्चारण में पढ़ता है

सही structure के साथ:
  - Standards mode, सही text, mobile-friendly, accessible, SEO-ready
```

---

## 🟢 How it Works — Step by Step

```
THE SKELETON:
──────────────────────────────────────────────────────────
<!DOCTYPE html>                 <- 1. Not a tag; a "mode switch" instruction
<html lang="en">                <- 2. Root element; lang helps a11y + translation
  <head>                        <- 3. Metadata (NOT displayed on the page)
    <meta charset="UTF-8">      <-    encoding (must be within first 1024 bytes)
    <meta name="viewport" ...>  <-    mobile scaling
    <title>...</title>          <-    tab title + search result title
    <link rel="stylesheet" ...> <-    CSS
    <script defer ...></script> <-    JS
  </head>
  <body>                        <- 4. Visible content
    ...
  </body>
</html>

WHAT GOES IN <head> (never visible, except <title> in the tab):
  <title> <meta> <link> <style> <script> <base> <noscript>

WHAT GOES IN <body>:
  headings, paragraphs, images, forms, header/footer, scripts (optional at end)

STANDARDS vs QUIRKS MODE:
  <!DOCTYPE html>  -> standards mode (use always)
  missing/old      -> quirks mode (browser imitates 1990s bugs)

ONE rule: only ONE <html>, ONE <head>, ONE <body> per document.
The browser auto-creates missing <html>, <head>, <body> in the DOM,
but you should write them explicitly.
```

## 🟢 कैसे काम करता है? (Hindi)
```
STEP BY STEP:
  1. DOCTYPE     -> browser को बताता है "modern standards mode use करो"
  2. <html>      -> पूरे document का root; lang="hi" या "en" लगाओ
  3. <head>      -> metadata: charset, viewport, title, CSS, JS links (screen पर नहीं दिखता)
  4. <body>      -> जो कुछ user देखता है: text, images, buttons, forms

नियम:
  - एक document में एक ही <html>, <head>, <body>
  - charset सबसे ऊपर रखो
  - head के अंदर कभी <div> या <p> मत रखो (invalid)
```

---

## 🟡 Real World Example
**Zomato restaurant page:** The `<head>` carries the title ("Burger King - Koramangala | Zomato"), a meta description used by Google as the snippet, Open Graph tags used when you share the link on WhatsApp, a favicon link and preloaded fonts. The `<body>` holds the header, menu, reviews and footer. Users never see the head, but search engines, social apps and screen readers rely on it.

## 🟡 Real Example Hindi mein
**Zomato restaurant page:** `<head>` में title ("Burger King - Koramangala | Zomato"), Google में दिखने वाला meta description, WhatsApp पर link share करने के लिए Open Graph tags, favicon और fonts preload होते हैं। `<body>` में header, menu, reviews और footer होता है। User head नहीं देखता, पर search engines, social apps और screen readers उसी पर निर्भर हैं।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<!-- 1. DOCTYPE: first line, forces standards mode -->
<html lang="en">
<!-- 2. root element; lang="hi" for Hindi pages -->
<head>
  <!-- 3a. Encoding: put first so every later byte is read correctly -->
  <meta charset="UTF-8">

  <!-- 3b. Mobile: width = device width, no initial zoom -->
  <meta name="viewport" content="width=device-width, initial-scale=1.0">

  <!-- 3c. Title: 50-60 characters is ideal for Google -->
  <title>Pizza Palace - Order Online | Fast Delivery</title>

  <!-- 3d. Description: shown under the title in search results (~150 chars) -->
  <meta name="description" content="Order fresh pizza online. 30-minute delivery.">

  <!-- 3e. Favicon: tiny icon in the browser tab -->
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg'><text y='14' font-size='14'>🍕</text></svg>">

  <!-- 3f. Internal CSS (small pages / critical CSS) -->
  <style>
    body { font-family: system-ui, sans-serif; margin: 0; }   /* reset margin */
    header, footer { background: #e23744; color: #fff; padding: 16px; } /* Zomato-like red */
    main { padding: 24px; max-width: 700px; margin: auto; }   /* centered content */
  </style>
</head>

<body>
  <!-- 4. Visible content -->
  <header>
    <h1>🍕 Pizza Palace</h1>
  </header>

  <main>
    <p>Welcome! Open DevTools and look at the Elements panel:
       the &lt;head&gt; is there, but nothing from it is drawn on the page.</p>
  </main>

  <footer>
    <small>&copy; 2025 Pizza Palace</small>
  </footer>

  <!-- 5. Inline script: runs after the HTML above is parsed -->
  <script>
    // document.title reads the <title> from <head>
    console.log("Title:", document.title);
    // document.doctype tells us standards mode is on
    console.log("DOCTYPE:", document.doctype.name);       // "html"
    // compatMode: "CSS1Compat" = standards, "BackCompat" = quirks
    console.log("Mode:", document.compatMode);
  </script>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// Next.js App Router: app/layout.js IS your <html>/<body> skeleton.
// You never write <head> by hand; use the Metadata API.
export const metadata = {
  title: "Pizza Palace - Order Online",          // becomes <title>
  description: "Order fresh pizza online.",       // becomes <meta name="description">
};

export const viewport = { width: "device-width", initialScale: 1 }; // <meta name="viewport">

export default function RootLayout({ children }) {
  return (
    <html lang="en">           {/* lang attribute set here */}
      <body>{children}</body>  {/* every page renders inside body */}
    </html>
  );
}

// Pages Router: use next/head
import Head from "next/head";
export default function Home() {
  return (
    <>
      <Head><title>Home</title></Head>
      <h1>Hello</h1>
    </>
  );
}

// Plain React (Vite): the skeleton lives in public/index.html or index.html;
// react-helmet / react-helmet-async can change <head> from components.
// charset + viewport are already there from the template.
// Tailwind: add the CSS via globals.css; the <link> is injected by the framework.
```

---

## ⚫ Interview Questions + Answers

**Q1: What is `<!DOCTYPE html>` and is it an HTML tag?**
A1: It is not a tag; it is a **declaration** (instruction) telling the browser to render in **standards mode** using the HTML5 spec. Without it, browsers fall back to **quirks mode** and emulate old, inconsistent behaviour (e.g., different box model in old IE). It must be the first line. It is case-insensitive.

**Q2: What is the difference between `<head>` and `<body>`?**
A2: `<head>` holds **metadata** about the document (title, charset, viewport, links to CSS/JS, SEO and social tags) and is not displayed. `<body>` holds the **visible content** and interactive elements. Only `<title>` is surfaced (in the tab/bookmark/search result).

**Q3: Why do we need `<meta charset="UTF-8">` and where should it go?**
A3: It tells the browser how to decode bytes into characters. UTF-8 supports all languages and emoji. Without it Hindi text may show as garbage. Place it as the **first element in `<head>`** (within the first 1024 bytes) so the browser knows the encoding before reading any text.

**Q4: What does `<meta name="viewport" content="width=device-width, initial-scale=1">` do?**
A4: On mobile, browsers by default pretend the screen is ~980px wide and zoom out. This tag sets the layout viewport width to the real device width, so **media queries and responsive design work**. Without it, your responsive CSS appears to do nothing on phones.

**Q5: Can you have multiple `<h1>`, `<body>` or `<head>` tags? What if you omit `<html>`, `<head>`, `<body>`?**
A5: Only one `<html>`, `<head>`, `<body>` is allowed. If you omit them, the HTML parser **auto-inserts** them in the DOM, so the page still works, but it is bad practice (attributes like `lang` are lost, validators fail, and tools behave inconsistently). Always write the full skeleton.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Missing DOCTYPE (quirks mode)
```html
<!-- WRONG: layout may break in subtle ways -->
<html><body>...</body></html>
<!-- ✅ Correct way -->
<!DOCTYPE html>
<html lang="en">...</html>
```

❌ **Mistake 2:** Forgetting the viewport meta tag
```html
<!-- WRONG: responsive CSS ignored on phones -->
<head><title>Shop</title></head>
<!-- ✅ Correct way -->
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Shop</title>
</head>
```

❌ **Mistake 3:** Putting visible elements inside `<head>` (invalid; browser moves them to body)
```html
<!-- WRONG -->
<head><title>Shop</title><div>Banner</div></head>
<!-- ✅ Correct way: only metadata in head -->
<head><title>Shop</title></head>
<body><div>Banner</div></body>
```

❌ **Mistake 4:** Missing `lang` attribute and blocking `user-scalable=no`
```html
<!-- ✅ Good: lang for screen readers; never disable zoom (accessibility) -->
<html lang="hi"> ... <meta name="viewport" content="width=device-width, initial-scale=1">
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| DOCTYPE | Declares HTML5 / standards mode | Browser को mode बताने वाली declaration |
| `<html>` | Root element | Document का root |
| `<head>` | Metadata container | छुपी जानकारी का हिस्सा |
| `<body>` | Visible content container | दिखने वाला हिस्सा |
| Quirks mode | Old browser emulation | पुराने browsers जैसा व्यवहार |
| charset | Character encoding (UTF-8) | अक्षरों को पढ़ने का encoding |
| viewport | Visible area for layout on mobile | Mobile screen का layout area |
| lang | Document language | Page की भाषा |
| Metadata | Data about the page | Page के बारे में जानकारी |

---

## ⚡ 3-Line Summary
**English:**
1. Every page follows DOCTYPE -> `<html lang>` -> `<head>` (metadata) -> `<body>` (visible content).
2. Always add `charset="UTF-8"`, the viewport meta and a unique `<title>`.
3. Missing DOCTYPE triggers quirks mode; missing viewport breaks mobile responsiveness.

**Hindi:**
1. हर page: DOCTYPE -> `<html lang>` -> `<head>` (metadata) -> `<body>` (दिखने वाला content)।
2. हमेशा `charset="UTF-8"`, viewport meta और unique `<title>` लगाओ।
3. DOCTYPE न हो तो quirks mode; viewport न हो तो mobile पर responsive design काम नहीं करता।

---

## ➡️ Next Topic
**3. Semantic HTML (header, footer, main, section, article, nav, aside)** — body ke andar content ko meaningful tags se kaise organise karte hain।
