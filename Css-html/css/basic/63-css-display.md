# 63. CSS Display (block, inline, inline-block, none)
# हिंदी में: CSS Display — Element कैसे बैठेगा और कितनी जगह लेगा

---

## 🔵 Simple Definition (English)
The `display` property decides how an element takes part in the layout. **block** starts on a new line and fills the full width. **inline** flows inside text and ignores width/height. **inline-block** flows like text but accepts width/height. **none** removes the element from the layout completely.

## 🔵 सरल परिभाषा (Hindi)
`display` property तय करती है कि element layout में कैसे बैठेगा। **block** नई line से शुरू होता है और पूरी width लेता है। **inline** text की तरह बहता है और width/height नहीं मानता। **inline-block** text की तरह बहता है पर width/height मानता है। **none** element को layout से पूरी तरह हटा देता है।

---

## 🔴 Problem it Solves
```
BEFORE UNDERSTANDING display:
  <a> link ko button banana hai: a { width: 120px; height: 40px; }
  -> Kuch nahi hota! <a> inline hai, width/height ignore hoti hai.

  <span> pe margin-top lagaya -> vertical margin kaam nahi karta.

  Nav items ko ek line me rakhne ke liye log <table> ya float use karte the.

WITH display:
  a { display: inline-block; width: 120px; height: 40px; }  -> ab button jaisa
  li { display: inline-block; }                             -> horizontal menu
  .modal { display: none; }                                 -> hide / show toggle
```

## 🔴 यह क्यों बना? (Hindi)
हर HTML tag का एक default display होता है (div = block, span = inline)। अगर आप यह नहीं जानते तो `<a>` या `<span>` पर width/height/margin-top काम नहीं करेंगे और layout "टूटा हुआ" लगेगा। `display` से हम कोई भी element का behaviour बदल सकते हैं, बिना HTML tag बदले।

---

## 🟢 How it Works — Step by Step

```
DEFAULT DISPLAY VALUES:
  block        : div, p, h1-h6, ul, li (li = list-item), section, header, form
  inline       : span, a, strong, em, img (img is "inline replaced"), label
  inline-block : button, input, select (behave like inline-block)

COMPARISON:
┌───────────────┬───────────┬──────────────┬─────────────────┬──────────────┐
│ Feature       │ block     │ inline       │ inline-block    │ none         │
├───────────────┼───────────┼──────────────┼─────────────────┼──────────────┤
│ New line?     │ Yes       │ No           │ No              │ -            │
│ Width default │ 100%      │ content only │ content only    │ -            │
│ width/height  │ Works     │ IGNORED      │ Works           │ -            │
│ margin top/bot│ Works     │ IGNORED      │ Works           │ -            │
│ margin l/r    │ Works     │ Works        │ Works           │ -            │
│ padding       │ Works     │ Visual only* │ Works           │ -            │
│ Takes space?  │ Yes       │ Yes          │ Yes             │ NO           │
└───────────────┴───────────┴──────────────┴─────────────────┴──────────────┘
* inline vertical padding paints but does not push other lines away.

STEPS:
1. Browser gives every tag a default display from its UA stylesheet.
2. Your CSS display overrides it.
3. Browser builds boxes: block boxes stack vertically, inline boxes sit
   inside "line boxes" side by side and wrap like words.
4. display:none -> element is NOT in the render tree at all
   (no box, no space, not read by screen readers, not focusable).

THE WHITESPACE GAP (inline-block gotcha):
  <li>A</li>
  <li>B</li>     <- newline between tags = a space character (~4px gap)
  Fix: use flex + gap instead of inline-block for rows.

Modern values: display: flex | grid | inline-flex | inline-grid | contents | flow-root
  display: contents -> element's own box disappears, children stay (good for wrappers).
```

## 🟢 कैसे काम करता है? (Hindi)
1. हर tag का default display browser के stylesheet से आता है।
2. आपकी CSS का `display` उसे override कर देता है।
3. **block** boxes ऊपर से नीचे stack होते हैं और पूरी width लेते हैं। **inline** boxes शब्दों की तरह एक line में चलते हैं और जगह कम पड़े तो अगली line में wrap होते हैं।
4. **inline-block** = बाहर से inline (साथ-साथ बैठता है), अंदर से block (width/height/margin सब मानता है)।
5. `display: none` में element render tree में ही नहीं होता: जगह नहीं लेता, screen reader नहीं पढ़ता, Tab से focus नहीं होता।
6. Gotcha: inline-block elements के बीच HTML की newline एक space बन जाती है, इसलिए छोटा gap दिखता है। Row के लिए `flex` + `gap` बेहतर है।

---

## 🟡 Real World Example
**Zomato / Swiggy filter chips** ("Rating 4.0+", "Pure Veg", "Fast Delivery"): each chip is an `<a>` or `<button>` with `display: inline-block` (or a flex row) so it can have padding, height and rounded corners while sitting side by side. **Amazon's** "Add to cart" link is an `<a>` turned into a button with `display: inline-block`. **Gmail's** compose dialog is shown/hidden with `display: none` toggled by JavaScript.

## 🟡 Real Example Hindi mein
**Zomato / Swiggy** के filter chips ("Rating 4.0+", "Pure Veg") एक-दूसरे के बगल में बैठते हैं और उनमें padding, height और गोल corners होते हैं। यह `inline-block` (या flex row) से होता है। **Amazon** का "Add to cart" असल में `<a>` tag है जिसे `inline-block` बनाकर button जैसा दिखाया जाता है। **Gmail** का compose box `display: none` को toggle करके दिखाया/छुपाया जाता है।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CSS Display Demo</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; padding: 20px; background: #f5f5f5; }
    h2 { margin: 24px 0 8px; font-size: 16px; border-bottom: 2px solid #333; }

    /* 1. BLOCK: each div goes on its own line and fills the width */
    .block-demo div { background: #bbdefb; margin-bottom: 6px; padding: 8px; }

    /* 2. INLINE: width/height/margin-top are IGNORED */
    .inline-demo span {
      display: inline;          /* default for span, written for clarity */
      background: #ffcdd2;
      width: 200px;             /* ignored! */
      height: 80px;             /* ignored! */
      margin-top: 40px;         /* ignored! */
      margin-left: 10px;        /* horizontal margin works */
      padding: 4px 8px;
    }

    /* 3. INLINE-BLOCK: sits inline but honours width/height */
    .ib-demo a {
      display: inline-block;    /* key line */
      width: 110px;
      height: 40px;
      line-height: 40px;        /* centre text vertically */
      text-align: center;
      background: #2e7d32;
      color: #fff;
      text-decoration: none;
      border-radius: 20px;
    }

    /* 4. DISPLAY NONE: toggle with a class (like Gmail compose) */
    .panel {
      background: #fff3e0;
      border: 1px solid #fb8c00;
      padding: 12px;
      margin-top: 8px;
    }
    .panel.hidden { display: none; }  /* removed from layout */

    /* 5. MODERN ROW: flex + gap instead of inline-block (no whitespace gap) */
    .chips { display: flex; gap: 8px; flex-wrap: wrap; }
    .chips span {
      padding: 6px 14px;
      border: 1px solid #bbb;
      border-radius: 999px;
      background: #fff;
    }
  </style>
</head>
<body>
  <h2>1. block</h2>
  <div class="block-demo">
    <div>Block 1 (full width)</div>
    <div>Block 2 (new line)</div>
  </div>

  <h2>2. inline (width/height ignored)</h2>
  <div class="inline-demo">
    Text before <span>inline span</span> text after.
  </div>

  <h2>3. inline-block (width/height work)</h2>
  <div class="ib-demo">
    <a href="#">Add to cart</a>
    <a href="#">Buy now</a>
  </div>

  <h2>4. display: none toggle</h2>
  <button id="toggle">Toggle panel</button>
  <div id="panel" class="panel">I disappear completely when hidden.</div>

  <h2>5. Modern chips row (flex + gap)</h2>
  <div class="chips">
    <span>Pure Veg</span><span>Rating 4.0+</span><span>Fast Delivery</span>
  </div>

  <script>
    // Toggle the .hidden class; CSS decides the display value
    document.getElementById('toggle').addEventListener('click', function () {
      document.getElementById('panel').classList.toggle('hidden');
    });
  </script>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. Conditional rendering vs display:none
function Modal({ open }) {
  // Option A: not in DOM at all (state is lost, cheaper DOM)
  // if (!open) return null;

  // Option B: stays in DOM, only hidden (state kept, e.g. video/form)
  return <div style={{ display: open ? 'block' : 'none' }}>Hello</div>;
}

// 2. Tailwind utility classes map 1:1 to display values
<div className="block">block</div>
<span className="inline">inline</span>
<a className="inline-block w-28 h-10 text-center">inline-block</a>
<div className="hidden md:block">hidden on mobile, shown from md (768px) up</div>
<div className="flex gap-2">flex row</div>

// 3. CSS Modules
/* Nav.module.css */
.link { display: inline-block; padding: 8px 16px; }

// 4. Next.js <Link> renders an <a>, so it is INLINE by default.
//    Add className="inline-block" or "block" if you need width/height/padding.
```

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between block, inline and inline-block?**
A1: **block** starts on a new line, takes full available width, accepts width/height/margin/padding. **inline** stays in the text flow, takes only content width, ignores width/height and vertical margins. **inline-block** stays in the flow like inline but accepts width, height and all margins/padding like block.

**Q2: Why does `width` not work on a `<span>` or `<a>`?**
A2: Because they are `display: inline` by default and inline elements ignore width and height. Change them to `inline-block` or `block` (or make the parent flex).

**Q3: What is the small gap between inline-block elements and how to remove it?**
A3: Whitespace/newline in the HTML between inline-block tags is rendered as a space character. Fix: use `display: flex` with `gap` (best), or set `font-size: 0` on the parent, or remove whitespace in HTML. Flex is the modern answer.

**Q4: What does `display: none` do to the layout and accessibility?**
A4: The element generates no box: no space, not painted, not focusable, and screen readers skip it. Descendants are also gone. Images may still be downloaded, but animations/transitions cannot run from `none` to a value (it is not animatable in the classic way; newer browsers support `transition-behavior: allow-discrete`).

**Q5: What is `display: contents`?**
A5: The element's own box is removed but its children are laid out as if they were children of the grandparent. Useful for wrapper elements inside grid/flex. Caveat: older browsers had accessibility bugs with it on buttons and semantic elements, so test with a screen reader.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Setting width/height on an inline element
```css
/* WRONG: <a> is inline, this does nothing */
a.btn { width: 120px; height: 40px; }
```
✅ **Correct way:**
```css
a.btn { display: inline-block; width: 120px; height: 40px; }
```

❌ **Mistake 2:** Using inline-block for whole page layouts and fighting the whitespace gap
```css
/* WRONG: 3 columns of width 33.33% wrap because of whitespace gaps */
.col { display: inline-block; width: 33.33%; }
```
✅ **Correct way:**
```css
.row { display: flex; gap: 16px; }
.col { flex: 1; }
```

❌ **Mistake 3:** Hiding important content with `display: none` and expecting it to be indexed or announced
✅ **Correct way:** Use `display: none` only when it should be hidden for everyone. For screen-reader-only text use a visually-hidden utility class (Tailwind: `sr-only`).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| block | New line, full width, sizeable | नई line, पूरी width |
| inline | Flows in text, no width/height | text की तरह बहता है |
| inline-block | Inline flow + block sizing | साथ बैठे पर size दे सके |
| display: none | Removes element from layout | element पूरी तरह गायब |
| display: contents | Box removed, children kept | खुद का box हटे, बच्चे रहें |
| Line box | Row that holds inline content | inline content की line |
| UA stylesheet | Browser's default CSS | Browser की default CSS |
| Replaced element | img, video: content from outside CSS | बाहर से content वाला element |

---

## ⚡ 3-Line Summary
**English:**
1. block = new line + full width; inline = flows in text, ignores width/height; inline-block = flows but sizeable.
2. `display: none` removes the element from layout and accessibility tree entirely.
3. For rows and columns use flex or grid instead of inline-block.

**Hindi:**
1. block = नई line + पूरी width; inline = text में बहता है, width/height नहीं मानता; inline-block = साथ बैठता है और size मानता है।
2. `display: none` element को layout और accessibility दोनों से हटा देता है।
3. Rows/columns के लिए inline-block की जगह flex या grid use करो।

---

## ➡️ Next Topic
**64. CSS Visibility vs Display None** — hide करने के तरीकों में फर्क (`visibility`, `display`, `opacity`) और कब कौन सा use करना है।
