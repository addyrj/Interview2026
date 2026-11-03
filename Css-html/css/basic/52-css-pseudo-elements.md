# 52. Pseudo-elements (::before, ::after, ::placeholder)
# हिंदी में: Pseudo-elements — Element के हिस्से या Virtual Elements Style करना

---

## 🔵 Simple Definition (English)
A **pseudo-element** (double colon `::`) styles a **part** of an element (`::first-line`, `::placeholder`, `::selection`) or creates a **virtual child** (`::before`, `::after`) that exists only in CSS, not in the HTML.

## 🔵 सरल परिभाषा (Hindi)
**Pseudo-element** (double colon `::`) element के किसी **हिस्से** को style करता है (`::first-line`, `::placeholder`, `::selection`) या एक **virtual child** बनाता है (`::before`, `::after`) जो सिर्फ CSS में होता है, HTML में नहीं।

---

## 🔴 Problem it Solves
```
BEFORE: decorative things needed extra HTML:
  <h2><span class="icon">*</span> Title</h2>
  <div class="clearfix-helper"></div>
  <span class="badge-dot"></span>

NOW: HTML stays clean (semantic), decoration lives in CSS:
  h2::before { content: "* "; }
  .clearfix::after { content: ""; display: block; clear: both; }
  .required::after { content: " *"; color: red; }

Also impossible without pseudo-elements: styling the first letter,
the placeholder text colour, or the text selection colour.
```

## 🔴 यह क्यों बना? (Hindi)
```
पहले decoration (icon, dot, line, badge) के लिए extra <span>/<div> लिखने पड़ते थे।
अब HTML साफ रहता है, सजावट CSS में:
  h2::before { content: "* "; }
  .required::after { content: " *"; color: red; }

साथ ही पहला अक्षर (::first-letter), placeholder का रंग (::placeholder),
और select किए text का रंग (::selection) सिर्फ pseudo-elements से बदल सकते हैं।
```

---

## 🟢 How it Works — Step by Step

```
SYNTAX:  selector::pseudo-element { ... }       (CSS3: double colon; single colon still works for old four)

COMMON PSEUDO-ELEMENTS
  ::before        virtual FIRST child of element
  ::after         virtual LAST child of element
  ::placeholder   hint text inside input/textarea
  ::first-line    first rendered line of a block
  ::first-letter  first letter (drop caps)
  ::selection     text highlighted by user
  ::marker        bullet/number of list item
  ::backdrop      behind <dialog>/fullscreen

::before / ::after RULES
  1. They need  content: "..."  (even empty "") or they are not rendered at all.
  2. They are inline by default; set display:block / inline-block to give size.
  3. They are INSIDE the element (child), so they do NOT work on replaced
     elements like <img>, <input>, <br>.
  4. Not in the DOM: JS can't select them, screen readers may read `content` text,
     so never put essential text there.
  5. position: absolute on ::after + position: relative on parent = badges, underlines, overlays.

  content values:  "text"  |  ""  |  attr(data-tip)  |  counter(x)  |  url(img.png)

  ┌ element ────────────────────────┐
  │ ::before  [real children]  ::after │
  └─────────────────────────────────┘

SPECIFICITY: a pseudo-element counts like an element (0,0,1).
```

## 🟢 कैसे काम करता है? (Hindi)
```
Syntax: selector::pseudo-element { ... }

::before  -> element के अंदर सबसे पहले एक virtual child
::after   -> element के अंदर सबसे आखिर में virtual child
::placeholder -> input के hint text की style
::selection   -> user ने जो text select किया उसका रंग

::before/::after के नियम:
  1. content: "..." ज़रूरी है (खाली "" भी चलेगा) वरना कुछ दिखेगा ही नहीं।
  2. ये default inline होते हैं; size देने के लिए display:block या inline-block करो।
  3. ये element के अंदर बनते हैं, इसलिए <img>, <input> पर काम नहीं करते।
  4. ये DOM में नहीं होते, इसलिए ज़रूरी text यहाँ मत रखो (SEO/accessibility)।
  5. parent पर position:relative + ::after पर position:absolute से badge/underline बनते हैं।
```

---

## 🟡 Real World Example
**Zomato / Swiggy forms:** the red `*` after "Phone number" is `label.required::after { content: " *"; }`, not typed into HTML. The grey hint "Search for restaurant" is `::placeholder`. Instagram's story ring is a gradient `::before` circle behind the avatar. Amazon's "Prime" tick, tooltip arrows, and the animated underline under nav links are all `::after`. Highlighting text in Gmail with a custom blue is `::selection`.

## 🟡 Real Example Hindi mein
**Zomato / Swiggy forms:** "Phone number" के आगे लाल `*` HTML में नहीं लिखा, वो `label.required::after { content: " *"; }` है। Search box का grey hint `::placeholder` है। Instagram की story का गोल gradient ring avatar के पीछे `::before` से बनता है। Nav links के नीचे animated underline और tooltip का तीर `::after` से बनते हैं।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Pseudo-elements Demo</title>
  <style>
    * { box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; padding: 24px; background: #f9fafb; max-width: 560px; }
    h2 { font-size: 15px; margin: 26px 0 8px; color: #374151; }

    /* 1. ::before icon + ::after required star */
    .title::before { content: "🍕 "; }                 /* decoration, not in HTML */
    label.required::after { content: " *"; color: #dc2626; }

    /* 2. ::placeholder */
    input.search {
      padding: 10px 12px; width: 100%; border: 1px solid #d1d5db; border-radius: 6px;
    }
    input.search::placeholder { color: #9ca3af; font-style: italic; }   /* style hint text */

    /* 3. Animated underline using ::after */
    .nav-link {
      position: relative;            /* anchor for absolute ::after */
      text-decoration: none; color: #111827; font-weight: 600; padding-bottom: 4px;
    }
    .nav-link::after {
      content: "";                   /* required, empty = pure shape */
      position: absolute; left: 0; bottom: 0;
      width: 100%; height: 2px; background: #f59e0b;
      transform: scaleX(0);          /* hidden */
      transform-origin: left;
      transition: transform .25s;
    }
    .nav-link:hover::after { transform: scaleX(1); }   /* grows on hover */

    /* 4. Tooltip with attr() */
    .tip { position: relative; cursor: help; border-bottom: 1px dotted #6b7280; }
    .tip::after {
      content: attr(data-tip);       /* takes text from HTML attribute */
      position: absolute; left: 50%; bottom: 130%; transform: translateX(-50%);
      background: #111827; color: #fff; padding: 4px 8px; border-radius: 4px;
      font-size: 12px; white-space: nowrap;
      opacity: 0; pointer-events: none; transition: opacity .2s;
    }
    .tip:hover::after { opacity: 1; }

    /* 5. Badge / notification dot */
    .bell { position: relative; display: inline-block; font-size: 24px; }
    .bell::after {
      content: "3"; position: absolute; top: -4px; right: -10px;
      background: #dc2626; color: #fff; font-size: 11px;
      min-width: 18px; height: 18px; border-radius: 9px;
      display: grid; place-items: center;
    }

    /* 6. Clearfix (legacy float fix) */
    .clearfix::after { content: ""; display: block; clear: both; }

    /* 7. ::first-letter, ::first-line, ::selection, ::marker */
    .article::first-letter { font-size: 2.6em; float: left; line-height: 1; padding-right: 6px; color: #b45309; }
    .article::first-line { font-weight: bold; }
    ::selection { background: #fde68a; color: #111; }
    li::marker { color: #2563eb; }
  </style>
</head>
<body>
  <h2>1. before / after</h2>
  <div class="title">Pizza Menu</div>
  <label class="required">Phone</label>

  <h2>2. placeholder</h2>
  <input class="search" type="text" placeholder="Search restaurants...">

  <h2>3. animated underline</h2>
  <a class="nav-link" href="#">Orders</a>

  <h2>4. tooltip</h2>
  <span class="tip" data-tip="Cash on delivery">COD</span>

  <h2>5. badge</h2>
  <span class="bell">🔔</span>

  <h2>6. clearfix</h2>
  <div class="clearfix" style="background:#e5e7eb">
    <div style="float:left;width:60px;height:40px;background:#93c5fd"></div>
  </div>

  <h2>7. first-letter / selection / marker</h2>
  <p class="article">Hunger is the best sauce. Select this text to see the custom highlight colour.</p>
  <ul><li>Blue bullet</li><li>Blue bullet</li></ul>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. Pseudo-elements live in CSS, not JSX: you cannot write ::before in a style prop.
//    Use CSS Modules / global CSS:
// Badge.module.css
/*
  .bell { position: relative; }
  .bell::after { content: attr(data-count); position: absolute; top: -4px; right: -8px; }
*/
import styles from "./Badge.module.css";
export const Bell = ({ count }) => (
  <span className={styles.bell} data-count={count}>🔔</span>   // data attr feeds attr()
);

// 2. Tailwind: before: and after: variants; content needs content-['...'] (v3) or auto in v4
<span className="relative after:absolute after:left-0 after:bottom-0 after:h-0.5 after:w-0 hover:after:w-full after:bg-amber-500 after:transition-all after:content-['']">
  Orders
</span>

// 3. Placeholder in Tailwind
<input className="placeholder:text-gray-400 placeholder:italic" placeholder="Search" />

// 4. styled-components / emotion
// const Link = styled.a`
//   &::after { content: ""; position: absolute; ... }
// `;

// 5. Pseudo-element text is not in the DOM: React Testing Library / Jest can't find it.
//    Put important text in real JSX.
```

---

## ⚫ Interview Questions + Answers

**Q1: Pseudo-class vs pseudo-element?**
A1: Pseudo-class (`:hover`) selects an existing element in a state. Pseudo-element (`::before`) selects/creates a part of an element. Pseudo-elements use `::` (CSS3), pseudo-classes use `:`. Pseudo-element specificity is element-level (0,0,1), pseudo-class is class-level (0,1,0).

**Q2: Why is my `::before` not showing?**
A2: Usually missing `content` property. Without `content` (even `""`), nothing is generated. Other causes: it's on an `<img>`/`<input>` (replaced elements don't have children), zero size because it's inline with empty content, or hidden by `z-index`/overflow.

**Q3: Can JS select ::before/::after? Are they accessible?**
A3: No, they are not in the DOM; `querySelector` can't find them. You can read computed style via `getComputedStyle(el, '::before').content`. Screen readers may or may not read generated content, so never place essential text in them.

**Q4: How do you style the placeholder?**
A4: `input::placeholder { color: #999; }`. Legacy prefixes (`::-webkit-input-placeholder`) are no longer needed in modern browsers. Don't use placeholder instead of a label: it disappears on typing and has low contrast.

**Q5: How do you build a tooltip with pure CSS?**
A5: Put text in `data-tip`, then `.tip { position: relative } .tip::after { content: attr(data-tip); position:absolute; opacity:0 } .tip:hover::after { opacity:1 }`. For keyboard access add `:focus-visible` too, and for complex content prefer a real element with `role="tooltip"`.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Forgetting `content`
```css
/* WRONG: nothing renders */
.dot::after { width: 8px; height: 8px; background: red; }

/* CORRECT */
.dot::after { content: ""; display: inline-block; width: 8px; height: 8px; background: red; }
```

❌ **Mistake 2:** Putting important text in `content`
```css
/* WRONG: not selectable, not translated, maybe not read by screen readers */
.price::after { content: "Rs. 499"; }

/* CORRECT: real HTML text; use pseudo only for decoration */
```

❌ **Mistake 3:** Using on `<img>` or `<input>`
```css
/* WRONG: no effect (replaced elements) */
img::before { content: "x"; }

/* CORRECT: wrap in a container and use container::before */
.avatar::before { content: ""; }
```

❌ **Mistake 4:** Absolute `::after` without positioned parent
```css
/* WRONG: sticks to the page/another ancestor */
.badge::after { position: absolute; top: 0; right: 0; }

/* CORRECT */
.badge { position: relative; }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Pseudo-element | `::part` of an element | Element का हिस्सा |
| ::before / ::after | Virtual first/last child | Virtual पहला/आखिरी child |
| content | Required property for generated content | Generated content की property |
| ::placeholder | Hint text of input | Input का hint text |
| ::selection | Highlighted text | Select किया text |
| ::first-letter / ::first-line | First letter / line | पहला अक्षर / पहली line |
| attr() | Reads HTML attribute into content | HTML attribute से text |
| Replaced element | img, input: content from outside | img, input जैसे elements |

---

## ⚡ 3-Line Summary
**English:**
1. Pseudo-elements (`::before`, `::after`, `::placeholder`, `::selection`) style parts of an element or generate virtual ones.
2. `::before/::after` need `content`, aren't in the DOM, and don't work on `<img>`/`<input>`.
3. Use them for decoration (icons, underlines, tooltips, badges), never for essential text.

**Hindi:**
1. Pseudo-elements element के हिस्से style करते हैं या virtual elements बनाते हैं।
2. `::before/::after` को `content` चाहिए, ये DOM में नहीं होते, और `<img>`/`<input>` पर नहीं चलते।
3. इन्हें सजावट (icon, underline, tooltip, badge) के लिए use करो, ज़रूरी text के लिए नहीं।

---

## ➡️ Next Topic
**53. CSS Specificity** पहले से notes में है; इसलिए आगे **54. CSS Cascade + Inheritance** — जब कई rules टकराएँ तो कौन जीतता है और कौन सी properties parent से inherit होती हैं।
