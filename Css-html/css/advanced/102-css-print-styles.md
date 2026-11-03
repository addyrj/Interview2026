# 102. CSS Print Styles
# हिंदी में: CSS Print Styles — Page को Print के लिए अलग Style देना

---

## 🔵 Simple Definition (English)
Print styles are CSS rules inside `@media print { ... }` (or a `<link media="print">` file) that apply **only when the page is printed or saved as PDF**. You hide navigation and ads, switch to black-on-white, control page breaks, and set paper margins with `@page`.

## 🔵 सरल परिभाषा (Hindi)
Print styles वो CSS rules हैं जो `@media print { ... }` के अंदर लिखे जाते हैं और **सिर्फ तब लगते हैं जब page print हो या PDF में save हो**। इनसे navigation और ads छुपाते हैं, black-on-white colors लगाते हैं, page breaks control करते हैं और `@page` से paper margins सेट करते हैं।

---

## 🔴 Problem it Solves
```
BEFORE:
  - Printing a webpage wasted 10 sheets: sidebar, header, footer, ads, dark background.
  - Text was cut in the middle of a table row or image between pages.
  - Links showed only blue text; on paper you could not see the URL.
  - Developers built separate "printer-friendly version" pages.

AFTER:
  - One page, one @media print block: hide extras, fix colors, control breaks.
  - Show URLs after links with a:after { content: " (" attr(href) ")" }
```

## 🔴 यह क्यों बना? (Hindi)
```
पहले:
  - Webpage print करने पर 10 पन्ने बर्बाद होते थे: sidebar, header, footer, ads, dark background।
  - Table की row या image दो पन्नों में बीच से कट जाती थी।
  - Links सिर्फ नीले text में आते थे; कागज़ पर URL नहीं दिखता था।
  - Developers अलग "printer-friendly" page बनाते थे।

अब:
  - एक ही page, एक @media print block: फालतू चीज़ें छुपाओ, colors ठीक करो, breaks control करो।
  - Links के बाद URL दिखाओ: a:after { content: " (" attr(href) ")" }
```

---

## 🟢 How it Works — Step by Step

```
1. User presses Ctrl/Cmd + P (or JS calls window.print()).
2. Browser switches the media type from "screen" to "print".
3. Your @media print rules now apply (they override screen rules
   if specificity is same and they come later).
4. Typical tasks:
     a) Hide:      nav, aside, .ads, .no-print, buttons  -> display: none
     b) Reset:     background: #fff; color: #000;  (saves ink)
     c) Fonts:     use pt units (12pt) and serif for body, readable on paper
     d) Links:     show URL with attr(href)
     e) Breaks:    break-inside: avoid;  break-before: page;  break-after: avoid;
     f) Orphans/widows: orphans: 3; widows: 3;  (no 1-line leftovers)
     g) Paper:     @page { size: A4; margin: 15mm; }
5. Test: DevTools -> Rendering -> "Emulate CSS media type: print",
   or just open Print Preview.

NOTE: Browsers by default do NOT print background colors/images.
      `print-color-adjust: exact` (older: -webkit-print-color-adjust) forces them.

NOTE: Use  break-*  (modern) instead of  page-break-*  (legacy; still works as alias).
```

## 🟢 कैसे काम करता है? (Hindi)

```
1. User Ctrl/Cmd + P दबाता है (या JS में window.print())।
2. Browser media type को "screen" से "print" कर देता है।
3. अब आपके @media print rules लगते हैं (specificity बराबर हो तो बाद वाले जीतते हैं)।
4. आम काम:
     a) छुपाना:   nav, aside, .ads, .no-print, buttons -> display: none
     b) Reset:    background: #fff; color: #000;  (स्याही बचती है)
     c) Fonts:    pt units (12pt) और serif body, कागज़ पर पढ़ने लायक
     d) Links:    attr(href) से URL दिखाओ
     e) Breaks:   break-inside: avoid;  break-before: page;
     f) Orphans/widows: orphans: 3; widows: 3;  (एक अकेली line न बचे)
     g) Paper:    @page { size: A4; margin: 15mm; }
5. Test: DevTools -> Rendering -> "Emulate CSS media type: print" या Print Preview।

NOTE: Browser default में background colors/images print नहीं करता।
      `print-color-adjust: exact` से force कर सकते हैं।
```

---

## 🟡 Real World Example
**Amazon invoice / IRCTC e-ticket / Swiggy order receipt:** When you click "Print Invoice", the website header, search bar and recommendations vanish. Only the order table, GST details and a QR code remain on a clean white A4 page, with the table never splitting a row across pages. That is a print stylesheet at work.

## 🟡 Real Example Hindi mein
**Amazon invoice / IRCTC e-ticket / Swiggy order receipt:** "Print Invoice" दबाते ही website का header, search bar और recommendations गायब हो जाते हैं। सिर्फ order table, GST details और QR code साफ़ सफेद A4 page पर बचते हैं, और table की कोई row दो पन्नों में नहीं कटती। यह print stylesheet का काम है।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Print Styles Demo - Invoice</title>
  <style>
    /* ───────── SCREEN STYLES (normal browsing) ───────── */
    * { box-sizing: border-box; }
    body { margin: 0; font-family: system-ui, sans-serif; background: #eef1f5; color: #222; }
    .topbar { background: #232f3e; color: #fff; padding: 14px 24px; display: flex; gap: 20px; }
    .topbar a { color: #fff; text-decoration: none; }
    .layout { display: grid; grid-template-columns: 200px 1fr; gap: 20px; padding: 20px; max-width: 960px; margin: auto; }
    .sidebar { background: #fff; padding: 16px; border-radius: 8px; }
    .invoice { background: #fff; padding: 24px; border-radius: 8px; }
    table { width: 100%; border-collapse: collapse; margin: 16px 0; }
    th, td { border-bottom: 1px solid #ddd; padding: 8px; text-align: left; }
    thead th { background: #f0f2f5; }
    .total { font-weight: bold; font-size: 1.2rem; }
    .print-btn { background: #ffd814; border: 0; padding: 10px 18px; border-radius: 20px; cursor: pointer; }
    .tag { background: #1a73e8; color: #fff; padding: 2px 8px; border-radius: 4px; }

    /* ───────── PRINT STYLES ───────── */

    /* Paper size and margins (@page is only valid at top level) */
    @page {
      size: A4;
      margin: 15mm;
    }

    @media print {
      /* 1. Hide everything that is useless on paper */
      .topbar,
      .sidebar,
      .print-btn,
      .no-print {
        display: none !important;
      }

      /* 2. Remove screen layout: let content use the full page width */
      .layout {
        display: block;
        padding: 0;
        max-width: none;
      }

      /* 3. Clean colors: white paper, black text (saves ink) */
      body {
        background: #fff;
        color: #000;
        font: 12pt/1.4 Georgia, "Times New Roman", serif; /* pt = physical unit */
      }
      .invoice { padding: 0; box-shadow: none; border-radius: 0; }

      /* 4. Keep badge colors on paper (browser usually strips backgrounds) */
      .tag {
        background: #1a73e8;
        color: #fff;
        -webkit-print-color-adjust: exact; /* Safari / older Chrome */
        print-color-adjust: exact;         /* standard */
      }

      /* 5. Show the URL after external links */
      a[href^="http"]::after {
        content: " (" attr(href) ")";
        font-size: 10pt;
        color: #444;
      }

      /* 6. Page-break control */
      h2 { break-after: avoid; }              /* heading never alone at page bottom */
      tr, .card { break-inside: avoid; }      /* do not split a row across pages */
      .page-break { break-before: page; }     /* force a new page */
      p { orphans: 3; widows: 3; }            /* avoid 1-2 line leftovers */

      /* 7. Repeat table header on each printed page */
      thead { display: table-header-group; }
    }
  </style>
</head>
<body>
  <!-- Visible on screen only -->
  <div class="topbar"><strong>ShopEasy</strong><a href="#">Orders</a><a href="#">Help</a></div>

  <div class="layout">
    <aside class="sidebar">
      <p>Your account</p><p>Addresses</p><p>Payments</p>
    </aside>

    <main class="invoice">
      <h1>Invoice <span class="tag">PAID</span></h1>
      <p>Order #402-8812 &middot; Terms:
         <a href="https://example.com/terms">Read terms</a></p>

      <table>
        <thead><tr><th>Item</th><th>Qty</th><th>Price</th></tr></thead>
        <tbody>
          <tr><td>Wireless Mouse</td><td>1</td><td>&#8377;799</td></tr>
          <tr><td>USB-C Cable</td><td>2</td><td>&#8377;598</td></tr>
          <tr><td>Laptop Stand</td><td>1</td><td>&#8377;1,299</td></tr>
        </tbody>
      </table>
      <p class="total">Total: &#8377;2,696</p>

      <button class="print-btn" onclick="window.print()">Print invoice</button>
    </main>
  </div>
</body>
</html>
```

```html
<!-- Alternative: separate print file, loaded only when printing -->
<link rel="stylesheet" href="print.css" media="print">
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. Tailwind has a built-in print: variant
<nav className="print:hidden">Menu</nav>
<main className="bg-gray-100 print:bg-white print:text-black">...</main>
<tr className="break-inside-avoid">...</tr>      {/* Tailwind: break-inside-avoid */}
<section className="break-before-page">...</section>

// 2. Button that prints in React
function PrintButton() {
  return <button className="print:hidden" onClick={() => window.print()}>Print</button>;
}

// 3. react-to-print library: print only one component (like invoice)
import { useReactToPrint } from 'react-to-print';
import { useRef } from 'react';
function Invoice() {
  const ref = useRef(null);
  const print = useReactToPrint({ contentRef: ref });
  return (
    <>
      <button onClick={print}>Print</button>
      <div ref={ref}>... invoice markup ...</div>
    </>
  );
}

// 4. Next.js: global print rules go in globals.css or a CSS Module with @media print
//    (@page must be in global CSS; CSS Modules would still emit it, but keep it global for clarity)
```

---

## ⚫ Interview Questions + Answers

**Q1: How do you apply special styles when a page is printed?**
A1: Use `@media print { ... }` inside your stylesheet, or `<link rel="stylesheet" href="print.css" media="print">`. These rules apply only in print and PDF output.

**Q2: How do you stop a table row or card from splitting across two pages?**
A2: `break-inside: avoid;` (legacy: `page-break-inside: avoid`). To force a new page use `break-before: page` / `break-after: page`. Use `break-after: avoid` on headings so they are not stranded at the page bottom.

**Q3: What is `@page` and what can you set with it?**
A3: `@page` is an at-rule to configure the printed page box: `size` (A4, letter, landscape), `margin`, and pseudo-pages like `:first`. It cannot style content; only the page area. Support is good for size/margin in Chromium; some features (like margin boxes for page numbers) are limited in browsers.

**Q4: Why are background colors missing when I print?**
A4: Browsers skip backgrounds by default to save ink. Force them with `print-color-adjust: exact` (and `-webkit-print-color-adjust: exact`). Better: design so important info does not depend on background (use borders, text).

**Q5: Which units are best in print CSS and how do you test it?**
A5: Use physical units: `pt`, `mm`, `cm`, `in` (12pt body text, margins in mm) rather than `px`/`vw`, because paper has fixed size. Test with Print Preview or DevTools -> Rendering -> "Emulate CSS media type: print".

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Hiding with `visibility: hidden` and leaving empty gaps
```css
/* WRONG: space is still reserved, blank areas on paper */
@media print { .ads { visibility: hidden; } }
/* CORRECT */
@media print { .ads { display: none; } }
```

❌ **Mistake 2:** Using web units and dark backgrounds
```css
/* WRONG: burns ink, layout based on viewport */
body { background: #111; font-size: 2vw; }
/* CORRECT */
@media print { body { background: #fff; color: #000; font-size: 12pt; } }
```

❌ **Mistake 3:** Putting `@page` inside `@media print` rules and expecting nesting tricks
```css
/* SAFE: write @page at top level, and test in Print Preview */
@page { size: A4; margin: 15mm; }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| @media print | Rules only for printing | सिर्फ print के लिए rules |
| @page | Configures the paper page box | Page का size और margin |
| break-inside | Controls splitting inside an element | Element को बीच में कटने से रोकना |
| orphans / widows | Min lines left at bottom / top of a page | पन्ने के नीचे/ऊपर बची lines |
| print-color-adjust | Force backgrounds to print | Background print करवाना |
| pt / mm | Physical length units | Physical माप की units |
| attr(href) | Reads attribute value into content | Attribute की value text में |

---

## ⚡ 3-Line Summary
**English:**
1. `@media print` applies styles only when printing or saving to PDF; hide nav/ads, use white background and black text.
2. Control pagination with `break-inside`, `break-before`, `orphans`, `widows`, and set paper with `@page`.
3. Use `pt/mm` units, show link URLs with `attr(href)`, and test via Print Preview or DevTools emulation.

**Hindi:**
1. `@media print` सिर्फ print/PDF के समय लगता है; nav/ads छुपाओ, सफेद background और काला text रखो।
2. `break-inside`, `break-before`, `orphans`, `widows` से pagination control करो और `@page` से paper सेट करो।
3. `pt/mm` units use करो, `attr(href)` से link URL दिखाओ, और Print Preview या DevTools emulation से test करो।

---

## ➡️ Next Topic
**103. CSS Subgrid** — अब हम layout की तरफ लौटते हैं; nested grid को parent grid की tracks से align करना सीखेंगे, जैसे cards के अंदर title/price/button एक लाइन में।
