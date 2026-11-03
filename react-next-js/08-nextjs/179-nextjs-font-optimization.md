# 179. Next.js Font Optimization
# हिंदी में: Next.js Font Optimization — next/font से बिना layout shift के fonts

---

## 🔵 Simple Definition (English)
**`next/font`** downloads fonts at build time and serves them from your own domain, with automatic fallback-font size adjustment. This removes extra requests to Google and prevents the text from jumping when the font loads.

## 🔵 सरल परिभाषा (Hindi)
**`next/font`** fonts को build time पर download करके आपके अपने domain से serve करता है, और fallback font का size अपने आप adjust करता है। इससे Google को extra request नहीं जाती और font load होते समय text कूदता नहीं।

---

## 🔴 Problem it Solves

Loading Google Fonts with a `<link>` tag needs DNS lookup and a request to another domain, blocks rendering or causes a flash. While the font downloads, the browser shows a fallback font (FOUT) or invisible text (FOIT); when the real font arrives, the text changes size and the layout shifts (CLS). There are also privacy concerns from sending visitors' IPs to Google.

```jsx
// PROBLEM: external request, layout shift, privacy concern
// <link href="https://fonts.googleapis.com/css2?family=Inter" rel="stylesheet" />

// SOLUTION: self-hosted at build time with zero layout shift
import { Inter } from 'next/font/google';
const inter = Inter({ subsets: ['latin'] });
```

## 🔴 यह क्यों बना? (Hindi)
Google Fonts को `<link>` tag से load करने पर दूसरे domain पर DNS lookup और request लगती है, rendering रुकती है या flash होता है। Font download होने तक browser fallback font (FOUT) या खाली text (FOIT) दिखाता है; असली font आने पर text का size बदलता है और layout कूदता है (CLS)। साथ ही visitors का IP Google को जाने की privacy चिंता भी रहती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Import the font function: import { Inter } from 'next/font/google'
Step 2 → Call it at module level with options (subsets, weight, display, variable)
Step 3 → At build time Next.js downloads the font files and stores them with your assets
Step 4 → It generates CSS with @font-face plus a size-adjusted fallback font (no layout shift)
Step 5 → Use the returned object: font.className or font.variable on <html> or <body>
Step 6 → Fonts are served from your domain, preloaded, and cached forever

Local fonts: import localFont from 'next/font/local' and point to a file in your repo
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Font function import करो: import { Inter } from 'next/font/google'
Step 2 → उसे module level पर options (subsets, weight, display, variable) के साथ call करो
Step 3 → Build time पर Next.js font files download करके आपके assets के साथ रख देता है
Step 4 → यह @font-face CSS और size-adjusted fallback font बनाता है (layout shift नहीं)
Step 5 → मिले हुए object का font.className या font.variable <html> या <body> पर लगाओ
Step 6 → Fonts आपके domain से serve होते हैं, preload होते हैं, और हमेशा के लिए cache होते हैं

Local fonts: import localFont from 'next/font/local' करके repo की file का path दो
```

---

## 🟡 Real World Example
**Zomato web:** The brand uses a custom typeface and a Devanagari font for Hindi menus. With `next/font`, both are self-hosted, so the first paint of restaurant names already uses a fallback with the same metrics. When the real font arrives, the text does not move, and no request leaves for `fonts.googleapis.com`, which speeds up first load on slow mobile networks.

## 🟡 Real Example Hindi mein
**Zomato web:** Brand का अपना typeface है और Hindi menus के लिए Devanagari font भी। `next/font` से दोनों self-host होते हैं, इसलिए restaurant names का पहला paint उसी metrics वाले fallback से होता है। असली font आने पर text हिलता नहीं, और `fonts.googleapis.com` पर कोई request नहीं जाती, जिससे slow mobile network पर पहला load तेज़ होता है।

---

## 💻 Code Example — Basic

```jsx
// app/layout.jsx: one Google font for the whole app
import { Inter } from 'next/font/google';              // font function from Next.js

const inter = Inter({
  subsets: ['latin'],                                  // only download the latin glyphs (smaller)
  display: 'swap',                                     // show fallback text immediately, swap later
});

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={inter.className}>       {/* apply the font to the whole page */}
      <body>{children}</body>                          {/* all text inherits the font */}
    </html>
  );
}
```

## 💻 Code Example — Advanced

```jsx
// app/layout.jsx: multiple fonts via CSS variables + a local font, with Tailwind-style usage
import { Inter, Noto_Sans_Devanagari } from 'next/font/google'; // two Google fonts
import localFont from 'next/font/local';                // font file stored in the repo

const inter = Inter({
  subsets: ['latin'],                                  // English text
  variable: '--font-inter',                            // expose as a CSS variable
  display: 'swap',                                     // avoid invisible text
});

const devanagari = Noto_Sans_Devanagari({
  subsets: ['devanagari', 'latin'],                    // Hindi glyphs plus latin
  weight: ['400', '700'],                              // non-variable fonts need weights listed
  variable: '--font-hindi',                            // second CSS variable
  display: 'swap',
});

const brand = localFont({
  src: [
    { path: '../public/fonts/Brand-Regular.woff2', weight: '400', style: 'normal' }, // regular file
    { path: '../public/fonts/Brand-Bold.woff2', weight: '700', style: 'normal' },    // bold file
  ],
  variable: '--font-brand',                            // third CSS variable
});

export default function RootLayout({ children }) {
  return (
    // Put all variables on <html> so any CSS can use them
    <html lang="hi" className={`${inter.variable} ${devanagari.variable} ${brand.variable}`}>
      <body style={{ fontFamily: 'var(--font-inter), var(--font-hindi), sans-serif' }}>
        <h1 style={{ fontFamily: 'var(--font-brand), sans-serif' }}>Order Now</h1> {/* brand heading */}
        {children}                                     {/* rest of the app */}
      </body>
    </html>
  );
}
```

---

## 🟠 Real App Integration

Define fonts once in a shared file and import them where needed, so each font is loaded only once. Using the same font function in several files creates several instances, so export one instance.

```jsx
// app/fonts.js: single source of truth for fonts
import { Poppins } from 'next/font/google';

export const poppins = Poppins({
  subsets: ['latin'],                                   // glyph subset
  weight: ['400', '600'],                               // weights used by the design
  display: 'swap',
  variable: '--font-poppins',                           // usable in CSS/Tailwind
});
```

```jsx
// app/(shop)/Price.jsx: use the exported font on one component only
import { poppins } from '../fonts';                     // reuse the same instance

export default function Price({ value }) {
  return <span className={poppins.className}>₹{value}</span>; // only this element uses Poppins
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Calling the font function inside a component (or in a loop)
✅ **Correct:** Call it at module scope, as the function must be evaluated at build time

```jsx
// Wrong: font loader called inside render
export default function Page() {
  const inter = Inter({ subsets: ['latin'] });          // ❌ build error: must be module scope
  return <p className={inter.className}>Hi</p>;
}

// Right
const inter = Inter({ subsets: ['latin'] });            // ✅ module scope
export default function Page() { return <p className={inter.className}>Hi</p>; }
```

❌ **Mistake 2:** Forgetting `subsets`, or listing too many weights
✅ **Correct:** Specify only the subsets and weights you really use

```jsx
// Wrong: downloads many files, warns about missing subsets
const f = Roboto({ weight: ['100','200','300','400','500','600','700','800','900'] }); // ❌ heavy

// Right
const f = Roboto({ subsets: ['latin'], weight: ['400', '700'] });                       // ✅ light
```

---

## 🧠 Tricky Interview Question

```jsx
// app/page.jsx
import { Inter } from 'next/font/google';
export default function Page() {
  return <p style={{ fontFamily: 'Inter' }}>Hello</p>;
}
```
**Answer:** The text will NOT use the downloaded Inter font (unless Inter is installed on the user's device). `next/font` generates a unique, hashed `font-family` name (like `__Inter_a1b2c3`) so names never clash. Writing `fontFamily: 'Inter'` refers to a global family that was never registered. You must use `inter.className`, `inter.style.fontFamily`, or the `variable` CSS custom property. Also, here the font function is imported but never called, which is why nothing is loaded at all.

---

## ⚫ Interview Questions + Answers

Q1: What problems does `next/font` solve?
A1: Extra network requests to font providers, flash of invisible/unstyled text, and layout shift. It self-hosts fonts at build time and adjusts the fallback font to match metrics (`size-adjust`).

Q2: What does the `display` option control?
A2: The `font-display` behavior. `swap` shows the fallback immediately and swaps when loaded; `block`, `fallback`, `optional` choose other trade-offs. Default is `swap`.

Q3: How do you use more than one font?
A3: Create each font with a `variable` name, put all variables on `<html>`, and use `var(--font-x)` in CSS or Tailwind config.

Q4: Are Google Fonts requested by the browser at runtime?
A4: No. They are downloaded at build time and served from your own domain, so the visitor's browser makes no request to Google.

Q5: Does it work with variable fonts?
A5: Yes. For variable fonts you do not need to list `weight`; Next.js recommends variable fonts for flexibility and smaller total size.

---

## 🔷 When to Use + When Not to Use
✅ **Use `next/font` when:**
- You use Google Fonts or local font files
- You care about CLS and first paint
- You want privacy-friendly self-hosting

❌ **Avoid when:**
- The font comes from a paid provider with its own required script (Adobe Fonts kit)
- You use system fonts only (`font-family: system-ui`), nothing to optimize
- You need to switch fonts dynamically at runtime per user (use CSS variables with several preloaded fonts instead)

---

## 📊 Visual Diagram

```
  BUILD TIME                               RUNTIME (browser)
  ┌──────────────────────────┐            ┌──────────────────────────┐
  │ Inter({subsets:[latin]}) │            │ HTML + <link preload>    │
  │  → download from Google  │            │ font file from YOUR host │
  │  → save in .next/static  │──deploy──► │ fallback (size-adjusted) │
  │  → generate @font-face   │            │   → swap to Inter        │
  └──────────────────────────┘            │ text does not move (CLS 0)│
                                          └──────────────────────────┘

  Re-render behavior: the font object is a constant created at module load;
  components using className do not re-render because of fonts.
  Performance: fewer connections, no render-blocking CSS from third party,
  better CLS and LCP.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| next/font | Built-in font optimization | Next.js का built-in font optimizer |
| subset | Part of font glyphs (latin) | Font के glyphs का हिस्सा |
| display: swap | Show fallback, then swap | पहले fallback, फिर असली font |
| FOUT | Flash of unstyled text | बिना style का text दिखना |
| FOIT | Flash of invisible text | Text का अदृश्य रहना |
| CSS variable | `--font-x` custom property | CSS custom property |
| Variable font | One file, many weights | एक file में कई weights |
| Fallback font | Temporary font before load | Load से पहले का अस्थायी font |

---

## ⚡ 3-Line Summary
**English:**
1. `next/font` self-hosts fonts at build time and avoids requests to Google at runtime.
2. It adjusts fallback fonts so text does not shift, and fonts are called at module scope.
3. Use `className` or a `variable`, limit subsets and weights, and share one instance across files.

**Hindi:**
1. `next/font` fonts को build time पर self-host करता है और runtime में Google को request नहीं जाती।
2. यह fallback fonts adjust करता है ताकि text न हिले, और font function module scope में call होता है।
3. `className` या `variable` इस्तेमाल करो, subsets और weights सीमित रखो, और एक instance कई files में share करो।

---

## ➡️ Next Topic
**180. Next.js Metadata + SEO** — `metadata` object, `generateMetadata`, Open Graph, sitemap और robots से search engines और social sharing के लिए pages को तैयार करना।
