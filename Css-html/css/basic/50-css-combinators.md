# 50. CSS Combinators (descendant, child, sibling)
# हिंदी में: CSS Combinators — Elements के आपसी रिश्ते से Target करना

---

## 🔵 Simple Definition (English)
A **combinator** joins two selectors and describes the **relationship** between elements in the DOM tree. There are four: **descendant** (space), **child** (`>`), **adjacent sibling** (`+`) and **general sibling** (`~`).

## 🔵 सरल परिभाषा (Hindi)
**Combinator** दो selectors को जोड़ता है और बताता है कि DOM tree में elements का **आपस में रिश्ता** क्या है। चार हैं: **descendant** (space), **child** (`>`), **adjacent sibling** (`+`) और **general sibling** (`~`)।

---

## 🔴 Problem it Solves
```
WITHOUT COMBINATORS you add a class to everything:
  <nav>
    <a class="nav-link">Home</a>
    <a class="nav-link">Cart</a>
  </nav>
  .nav-link { ... }            <- must remember to add class on each <a>

WITH COMBINATORS the structure itself is the selector:
  nav a { ... }                <- every <a> inside nav
  ul > li { ... }              <- only direct children
  h2 + p { ... }               <- first paragraph right after a heading
  input:checked ~ label { }    <- all later labels (checkbox hack)

Result: less HTML noise, styles follow structure.
```

## 🔴 यह क्यों बना? (Hindi)
```
Combinators के बिना हर element पर class लगानी पड़ती है।
Combinators से HTML की structure ही selector बन जाती है:
  nav a      -> nav के अंदर के सारे links
  ul > li    -> सिर्फ सीधे बच्चे
  h2 + p     -> heading के ठीक बाद वाला paragraph
  h2 ~ p     -> heading के बाद वाले सारे paragraphs (same parent)

फायदा: HTML साफ रहता है, और scoped styling (सिर्फ किसी section के अंदर) आसान होती है।
```

---

## 🟢 How it Works — Step by Step

```
FAMILY TREE ANALOGY:
  <div class="parent">
    <p>child 1</p>          <- child of .parent
    <p>child 2</p>          <- sibling of child 1
    <section>
      <p>grandchild</p>     <- descendant of .parent (NOT a direct child)
    </section>
  </div>

COMBINATORS:
  A B    DESCENDANT       any B anywhere inside A (child, grandchild, ...)
  A > B  CHILD            B that is a DIRECT child of A only
  A + B  ADJACENT SIBLING B immediately AFTER A, same parent (next one only)
  A ~ B  GENERAL SIBLING  every B AFTER A, same parent (not necessarily next)

  .parent p      -> child 1, child 2, grandchild   (all 3)
  .parent > p    -> child 1, child 2               (not grandchild)
  p + p          -> child 2 (p directly after a p)
  p ~ section    -> the section (it comes after a p)

IMPORTANT:
  - Sibling combinators only look FORWARD (next elements). CSS cannot select a
    previous sibling with + or ~ (use :has(), supported in modern browsers: Chrome 105+, Safari 15.4+, Firefox 121+).
  - Specificity of combinators = 0; only the selectors around them count.
  - Long descendant chains (a b c d e) make CSS fragile and slow to override.
```

## 🟢 कैसे काम करता है? (Hindi)
```
परिवार से समझो:
  A B    (space) -> A के अंदर कहीं भी B (बेटा, पोता, सब)
  A > B           -> सिर्फ A का सीधा बच्चा B
  A + B           -> A के ठीक बाद वाला पहला sibling B
  A ~ B           -> A के बाद वाले सारे siblings B (same parent)

ध्यान रखो:
  - Sibling combinators सिर्फ आगे देखते हैं, पीछे वाला sibling select नहीं कर सकते
    (पीछे/parent के लिए :has() है — modern browsers में चलता है)।
  - Combinator की अपनी specificity 0 होती है।
  - बहुत लंबी chain (a b c d) मत लिखो, override करना मुश्किल हो जाता है।
```

---

## 🟡 Real World Example
**Zomato restaurant menu:** a menu list `<ul class="menu">` has dish rows. `.menu > li` styles only top-level categories, while nested sub-lists (add-ons) stay unstyled. `h3 + p` makes the first description line right under each dish name grey and small. In a review list, `.review ~ .review` adds a top border to every review except the first, giving clean dividers without extra classes.

## 🟡 Real Example Hindi mein
**Zomato menu:** `<ul class="menu">` में dishes की list है। `.menu > li` सिर्फ top-level categories को style करता है, अंदर की add-ons वाली nested list पर असर नहीं पड़ता। `h3 + p` हर dish के नाम के ठीक नीचे वाली description को grey और छोटा बना देता है। Reviews में `.review ~ .review` पहले review को छोड़कर बाकी सब पर ऊपर border लगाता है — बिना extra class के divider।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CSS Combinators Demo</title>
  <style>
    * { box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; padding: 20px; background: #fafafa; }

    .box { background: #fff; border: 1px solid #ddd; padding: 12px; margin-bottom: 20px; max-width: 460px; }
    .label { font-size: 12px; color: #6b7280; margin-bottom: 4px; }

    /* 1. DESCENDANT (space): every <span> anywhere inside .demo-1 */
    .demo-1 span { background: #fde68a; padding: 2px 6px; }

    /* 2. CHILD (>): only <span> that are DIRECT children of .demo-2 */
    .demo-2 > span { background: #bbf7d0; padding: 2px 6px; }

    /* 3. ADJACENT SIBLING (+): the <p> immediately after an <h3> */
    .demo-3 h3 + p { color: #dc2626; font-weight: bold; }

    /* 4. GENERAL SIBLING (~): every <li> after the .active item */
    .demo-4 li.active ~ li { opacity: 0.4; }   /* items after the active one are dimmed */

    /* 5. Realistic: divider between items without extra class */
    .reviews .review ~ .review { border-top: 1px solid #e5e7eb; margin-top: 8px; padding-top: 8px; }

    /* 6. Realistic: owl selector - spacing between all siblings */
    .stack > * + * { margin-top: 10px; }       /* every child except the first */
  </style>
</head>
<body>
  <h1>Combinators</h1>

  <!-- 1. Descendant: both the direct span AND the nested span match -->
  <div class="box demo-1">
    <div class="label">1. descendant (space)</div>
    <span>direct</span>
    <div><span>nested deeper</span></div>
  </div>

  <!-- 2. Child: only the direct span matches, nested one does not -->
  <div class="box demo-2">
    <div class="label">2. child (&gt;)</div>
    <span>direct (matches)</span>
    <div><span>nested (no match)</span></div>
  </div>

  <!-- 3. Adjacent sibling: only first <p> after h3 is red -->
  <div class="box demo-3">
    <div class="label">3. adjacent sibling (+)</div>
    <h3>Paneer Tikka</h3>
    <p>I am right after h3 (red)</p>
    <p>I am second paragraph (normal)</p>
  </div>

  <!-- 4. General sibling: li after .active are dimmed -->
  <div class="box demo-4">
    <div class="label">4. general sibling (~)</div>
    <ul>
      <li>Before active (normal)</li>
      <li class="active">Active</li>
      <li>After 1 (dim)</li>
      <li>After 2 (dim)</li>
    </ul>
  </div>

  <!-- 5. Review dividers -->
  <div class="box reviews">
    <div class="label">5. dividers with ~</div>
    <div class="review">Great food!</div>
    <div class="review">Late delivery.</div>
    <div class="review">Loved the biryani.</div>
  </div>

  <!-- 6. Lobotomized owl: spacing -->
  <div class="box stack">
    <div class="label">6. .stack &gt; * + *</div>
    <p>One</p>
    <p>Two</p>
    <p>Three</p>
  </div>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. Combinators work the same in global CSS or CSS Modules
// Menu.module.css
/*
  .menu > li { padding: 8px 0; }          // direct items only
  .menu li + li { border-top: 1px solid #eee; }
*/
import styles from "./Menu.module.css";

export default function Menu({ items }) {
  return (
    <ul className={styles.menu}>
      {items.map((i) => <li key={i.id}>{i.name}</li>)}
    </ul>
  );
}

// 2. Tailwind equivalents
// space-y-4  => > :not([hidden]) ~ :not([hidden]) { margin-top: 1rem }  (sibling combinator under the hood)
// divide-y   => adds borders between children
<ul className="divide-y divide-gray-200 space-y-2">...</ul>

// 3. Tailwind arbitrary variants for child combinator
<div className="[&>p]:text-gray-600 [&_a]:underline">
  <p>direct paragraph</p>
  <a href="/x">descendant link</a>
</div>

// 4. Peer pattern (sibling combinator ~): style label when checkbox before it is checked
<input type="checkbox" className="peer sr-only" id="t" />
<label htmlFor="t" className="peer-checked:bg-green-500">Toggle</label>
```

---

## ⚫ Interview Questions + Answers

**Q1: Difference between `div p` and `div > p`?**
A1: `div p` matches every `<p>` at any depth inside a div. `div > p` matches only `<p>` that are direct children. A paragraph inside `div > section > p` matches the first but not the second.

**Q2: Difference between `+` and `~`?**
A2: `A + B` selects only the one `B` that comes immediately after `A`. `A ~ B` selects all `B` siblings that come after `A` (same parent), whether directly next or later. Both need a shared parent.

**Q3: Can CSS select a previous sibling or parent?**
A3: Not with combinators. Modern CSS has `:has()` (Chrome 105+, Safari 15.4+, Firefox 121+): `.card:has(img)` selects a parent that contains an image, `h2:has(+ p)` an h2 followed by a p. Always check support for older targets.

**Q4: Is descendant selector bad for performance?**
A4: Browsers match selectors right to left, so `.menu li` first finds all `li` then checks ancestors. It is fine in practice. The real cost is maintainability: deep chains like `.a .b .c .d span` have high specificity and are hard to override. Keep chains short (2-3 levels) or use BEM classes.

**Q5: What does `.stack > * + *` do?**
A5: Called the "lobotomized owl". It selects every direct child that has a previous sibling, so every child except the first. Used to add spacing between items without leaving extra margin at the top. Today you can also use `display:flex; gap` or Tailwind `space-y-*`.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Using descendant when you want direct child
```css
/* WRONG: also styles links in nested dropdown */
nav li a { color: white; }

/* CORRECT: only the top level links */
nav > ul > li > a { color: white; }
```

❌ **Mistake 2:** Expecting `+` to match all following siblings
```css
/* WRONG: only the first p after h2 */
h2 + p { color: red; }

/* CORRECT: all paragraphs after h2 */
h2 ~ p { color: red; }
```

❌ **Mistake 3:** Adding spaces around wrong place
```css
/* WRONG: space makes it "descendant" */
.card .active { }     /* .active INSIDE .card */

/* CORRECT if both classes are on the same element */
.card.active { }
```

❌ **Mistake 4:** Very long selector chains
```css
/* WRONG: fragile, specificity 0,4,1 */
.page .content .list .item a { }

/* CORRECT: one meaningful class */
.item-link { }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Combinator | Symbol that relates two selectors | दो selectors का रिश्ता |
| Descendant (space) | Any depth inside | अंदर कहीं भी |
| Child (`>`) | Direct child only | सीधा बच्चा |
| Adjacent sibling (`+`) | Immediately next sibling | ठीक अगला भाई |
| General sibling (`~`) | All following siblings | बाद के सारे भाई |
| Lobotomized owl | `* + *` spacing trick | पहले को छोड़कर बाकी सब |
| :has() | Relational pseudo-class (parent/previous) | Parent select करने वाला |
| DOM tree | Hierarchy of elements | Elements का tree |

---

## ⚡ 3-Line Summary
**English:**
1. Combinators relate selectors: space = descendant, `>` = direct child, `+` = next sibling, `~` = all later siblings.
2. They only look down and forward; use `:has()` for parent/previous-sibling needs.
3. Keep chains short to avoid high specificity and brittle CSS.

**Hindi:**
1. Combinators: space = कहीं भी अंदर, `>` = सीधा बच्चा, `+` = अगला sibling, `~` = बाद के सारे siblings।
2. ये सिर्फ नीचे और आगे देखते हैं; parent/पिछले के लिए `:has()` है।
3. Chain छोटी रखो, वरना specificity बढ़ती है और CSS नाज़ुक हो जाती है।

---

## ➡️ Next Topic
**51. Pseudo-classes** — `:hover`, `:focus`, `:nth-child`, `:first-child` — elements को उनकी state या position के आधार पर style करना।
