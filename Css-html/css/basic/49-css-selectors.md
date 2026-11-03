# 49. CSS Selectors (element, class, id, universal)
# हिंदी में: CSS Selectors — Browser को बताओ कौन सा element style करना है

---

## 🔵 Simple Definition (English)
A **selector** is the part of a CSS rule that picks which HTML elements get the styles. The four basic ones are: **element** (`p`), **class** (`.card`), **id** (`#header`) and **universal** (`*`). Everything else in CSS builds on these.

## 🔵 सरल परिभाषा (Hindi)
**Selector** CSS rule का वो हिस्सा है जो तय करता है कि कौन से HTML elements पर style लगेगी। चार basic selectors हैं: **element** (`p`), **class** (`.card`), **id** (`#header`) और **universal** (`*`)। बाकी सब CSS इन्हीं पर बनी है।

---

## 🔴 Problem it Solves
```
BEFORE SELECTORS (inline styles):
  <p style="color:red">One</p>
  <p style="color:red">Two</p>
  <p style="color:red">Three</p>   <- 100 paragraphs = 100 copies of the same style

WITH SELECTORS:
  p { color: red; }                <- one rule styles every <p>
  .error { color: red; }           <- or only elements marked with class="error"

Need: target ONE element, a GROUP of elements, or ALL elements -> selectors give that control.
```

## 🔴 यह क्यों बना? (Hindi)
```
Selectors से पहले हर tag में अलग से style लिखनी पड़ती थी (inline)।
100 paragraphs = 100 बार same code। Change करना हो तो 100 जगह बदलो।

Selectors से:
  p { color: red; }        <- सारे <p> एक बार में
  .error { color: red; }   <- सिर्फ class="error" वाले
  #logo { ... }            <- सिर्फ एक unique element
  * { ... }                <- हर element

यानी: एक element, कुछ elements, या सब elements — पूरा control।
```

---

## 🟢 How it Works — Step by Step

```
SELECTOR TYPES:
──────────────────────────────────────────────────────────
  p            ELEMENT (type) selector   -> every <p>
  .card        CLASS selector            -> every element with class="card"
  #navbar      ID selector               -> the ONE element with id="navbar"
  *            UNIVERSAL selector        -> every element
  h1, h2, h3   SELECTOR LIST (comma)     -> any of them
  p.intro      COMPOUND (no space)       -> <p> that ALSO has class intro
  .a.b         TWO CLASSES               -> element with both classes

HOW THE BROWSER MATCHES (right-to-left in practice):
  1. Browser parses HTML into DOM tree
  2. For every element, it asks: "does this element match this selector?"
  3. If yes, the declarations in { } are applied (then cascade/specificity decide conflicts)

SPECIFICITY (strength) ORDER — details in topic 53:
  universal (*) = 0  <  element = 1  <  class = 10  <  id = 100  <  inline style = 1000

RULES:
  - class: reusable, many elements, one element can have many classes
  - id: must be unique in a page, avoid for styling (too strong, not reusable)
  - class names are case-sensitive in standards mode, no spaces inside a name
```

## 🟢 कैसे काम करता है? (Hindi)
```
1. Browser HTML पढ़कर DOM tree बनाता है।
2. हर element के लिए check करता है: "क्या ये selector match करता है?"
3. Match हुआ तो { } के अंदर की properties लग जाती हैं।
4. अगर दो rules टकराएँ तो specificity + cascade (topic 53, 54) तय करते हैं।

याद रखो:
  p        -> tag का नाम (element selector)
  .card    -> dot = class
  #navbar  -> hash = id (page में unique)
  *        -> star = सब कुछ
  p.intro  -> बीच में space नहीं = "<p> जिस पर class intro भी है"
  p .intro -> space है = "p के अंदर कोई .intro" (ये combinator है, topic 50)
```

---

## 🟡 Real World Example
**Amazon product listing:** every product tile has `class="product-card"`, the page logo has `id="nav-logo"`, and a global reset uses `*` to zero margins. The designer writes `.product-card { ... }` once and it styles thousands of tiles. A sale tile gets an extra class: `class="product-card deal"`, and `.product-card.deal` adds a red badge only to those. Nobody writes `#product-1`, `#product-2`... that would be unmaintainable.

## 🟡 Real Example Hindi mein
**Amazon product listing:** हर product tile पर `class="product-card"` होती है, logo पर `id="nav-logo"`, और reset के लिए `*` use होता है। Designer `.product-card { ... }` एक बार लिखता है और हज़ारों tiles style हो जाते हैं। Sale वाले tile पर extra class `deal` लगती है, और `.product-card.deal` सिर्फ उन्हीं पर red badge जोड़ता है। `#product-1`, `#product-2` लिखना maintain करना असंभव होगा, इसलिए styling में id कम use होती है।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CSS Selectors Demo</title>
  <style>
    /* UNIVERSAL: applies to every element (use sparingly, good for resets) */
    * {
      box-sizing: border-box;   /* include padding+border in width */
      margin: 0;                /* remove default browser margin */
    }

    /* ELEMENT selector: every <body> */
    body {
      font-family: system-ui, sans-serif;
      background: #f4f4f5;
      padding: 24px;
    }

    /* ELEMENT selector: every <h1> */
    h1 { color: #111827; margin-bottom: 16px; }

    /* ELEMENT selector: every <p> */
    p { margin-bottom: 8px; line-height: 1.5; }

    /* ID selector: ONE unique element only */
    #page-title {
      border-bottom: 3px solid #f59e0b;   /* amazon-like orange underline */
      padding-bottom: 6px;
    }

    /* CLASS selector: reusable on many elements */
    .card {
      background: #fff;
      border: 1px solid #e5e7eb;
      border-radius: 8px;
      padding: 16px;
      margin-bottom: 12px;
      max-width: 420px;
    }

    /* CLASS selector used as a modifier */
    .deal { border-color: #dc2626; }

    /* COMPOUND selector: element + class (no space between) */
    p.price { font-weight: bold; color: #047857; }

    /* TWO CLASSES on the same element: needs BOTH */
    .card.deal .badge-text { color: #dc2626; }

    /* SELECTOR LIST: same style for multiple selectors */
    h2, h3 { color: #374151; }

    /* Attribute-free "state" class toggled by JS or React */
    .hidden { display: none; }
  </style>
</head>
<body>
  <!-- id must be unique in the page -->
  <h1 id="page-title">Today's Products</h1>

  <!-- Normal card: only .card applies -->
  <div class="card">
    <h2>Wireless Mouse</h2>
    <p>Comfortable and silent.</p>
    <p class="price">Rs. 599</p>
  </div>

  <!-- Deal card: two classes, both rules apply -->
  <div class="card deal">
    <h2>Keyboard</h2>
    <p class="badge-text">Lightning Deal!</p>
    <p class="price">Rs. 999</p>
  </div>

  <!-- Hidden by class: not shown in the page -->
  <div class="card hidden">
    <h3>You cannot see me</h3>
  </div>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. In React the HTML attribute "class" is written as className
export default function ProductCard({ name, price, isDeal }) {
  // Build the class string conditionally: "card" or "card deal"
  const cls = isDeal ? "card deal" : "card";
  return (
    <div className={cls}>
      <h2>{name}</h2>
      <p className="price">Rs. {price}</p>
    </div>
  );
}

// 2. Global CSS (app/globals.css in Next.js) uses normal selectors:
/*
  *, *::before, *::after { box-sizing: border-box; }
  .card { border: 1px solid #e5e7eb; }
*/

// 3. CSS Modules: class selectors are auto-renamed (e.g. card_abc12) so they never clash
// Card.module.css  ->  .card { padding: 16px; }
import styles from "./Card.module.css";
<div className={styles.card} />;

// 4. Tailwind: each utility class is a tiny class selector
<div className="rounded-lg border p-4 bg-white" />;

// 5. Prefer classes over id in React: components render many times,
//    and duplicate ids break the "unique id" rule.
```

---

## ⚫ Interview Questions + Answers

**Q1: Difference between class and id selectors?**
A1: A **class** (`.card`) is reusable: many elements can share it and one element can have many classes. An **id** (`#header`) must be unique in the page and has much higher specificity (100 vs 10). Use classes for styling, ids for fragment links (`#section`), label `for`, and JS hooks.

**Q2: What does the universal selector `*` do and is it bad for performance?**
A2: It matches every element. It has specificity 0, so anything overrides it. Used for resets like `* { box-sizing: border-box }`. Modern browsers handle it fine; it's only a concern if combined with heavy descendant chains (`.a * * *`). It does not match pseudo-elements unless you write `*::before`.

**Q3: What is the difference between `p.intro` and `p .intro`?**
A3: `p.intro` (no space) = a `<p>` that itself has class intro. `p .intro` (space) = any element with class intro that is a descendant of a `<p>`. One space changes the meaning completely.

**Q4: What does `h1, h2, h3 { }` mean?**
A4: A comma creates a selector list: the same declarations apply to each selector separately. Note: in older browsers one invalid selector in the list invalidated the whole rule; `:is()` and `:where()` are forgiving.

**Q5: Can an element have multiple classes? How is it used?**
A5: Yes: `class="btn btn-primary large"`. The element matches `.btn`, `.btn-primary` and `.large`. You can also require several: `.btn.large` matches only elements having both. This is how component variants (Bootstrap, Tailwind, BEM modifiers) work.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Styling with ids
```css
/* WRONG: specificity 100, can't be reused, hard to override */
#submit-btn { background: blue; }

/* CORRECT: use a class */
.btn-submit { background: blue; }
```

❌ **Mistake 2:** Writing a space by accident
```css
/* WRONG: means "any .active inside a .tab" */
.tab .active { color: red; }

/* CORRECT when the SAME element has both classes */
.tab.active { color: red; }
```

❌ **Mistake 3:** Forgetting the dot or hash
```css
/* WRONG: this targets <card> tags, which don't exist */
card { padding: 10px; }

/* CORRECT */
.card { padding: 10px; }
```

❌ **Mistake 4:** Starting a class name with a digit or using spaces
```css
/* WRONG */
.2col { }          /* invalid: can't start with a digit */

/* CORRECT */
.col-2 { }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Selector | Pattern that picks elements | Elements चुनने का pattern |
| Element (type) selector | Matches by tag name (`p`) | Tag के नाम से |
| Class selector | `.name`, reusable | Reusable, dot से शुरू |
| ID selector | `#name`, unique | Unique, hash से शुरू |
| Universal selector | `*`, all elements | सारे elements |
| Selector list | Comma-separated selectors | Comma से कई selectors |
| Compound selector | Selectors joined without space | बिना space के जुड़े selectors |
| Declaration block | `{ property: value; }` | Style लिखने का block |

---

## ⚡ 3-Line Summary
**English:**
1. Selectors choose which elements a rule styles: element (`p`), class (`.x`), id (`#x`), universal (`*`).
2. Prefer classes for styling; ids are unique and strong, `*` is mostly for resets.
3. Spaces matter: `p.x` is one element, `p .x` is a descendant.

**Hindi:**
1. Selector तय करता है कि rule किन elements पर लगेगा: `p`, `.x`, `#x`, `*`।
2. Styling के लिए class use करो; id unique और बहुत strong होती है; `*` ज़्यादातर reset के लिए।
3. Space का मतलब बदल देता है: `p.x` एक element, `p .x` अंदर वाला element।

---

## ➡️ Next Topic
**50. CSS Combinators** — descendant, child (`>`), adjacent (`+`) और general sibling (`~`) selectors, ताकि elements को उनके relation से target कर सको।
