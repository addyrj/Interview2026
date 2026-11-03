# 105. CSS Nesting (new feature)
# हिंदी में: CSS Nesting — Selector के अंदर Selector लिखना (बिना Sass)

---

## 🔵 Simple Definition (English)
**CSS Nesting** lets you write a rule inside another rule, so child selectors, pseudo-classes and media queries stay grouped with their parent. It works natively in the browser with no Sass/Less compile step. The `&` symbol refers to the parent selector.

## 🔵 सरल परिभाषा (Hindi)
**CSS Nesting** से आप एक rule के अंदर दूसरा rule लिख सकते हैं, इसलिए child selectors, pseudo-classes और media queries अपने parent के साथ ही रहते हैं। यह browser में सीधे चलता है, Sass/Less compile की ज़रूरत नहीं। `&` चिह्न parent selector को दर्शाता है।

---

## 🔴 Problem it Solves
```
BEFORE (plain CSS):
  .card { ... }
  .card .title { ... }
  .card .title:hover { ... }
  .card:hover { ... }
  @media (min-width: 700px) { .card { ... } }
  -> Selector "card" repeated everywhere, rules scattered in the file.
  -> People installed Sass only to nest.

AFTER (native nesting):
  .card {
    ...
    .title { ... &:hover { ... } }
    &:hover { ... }
    @media (min-width: 700px) { ... }
  }
  -> Everything about .card is in ONE block. No build step.
```

## 🔴 यह क्यों बना? (Hindi)
```
पहले (plain CSS):
  .card { ... }
  .card .title { ... }
  .card .title:hover { ... }
  .card:hover { ... }
  @media (min-width: 700px) { .card { ... } }
  -> "card" selector बार-बार लिखना पड़ता था, rules पूरी file में बिखरे रहते थे।
  -> लोग सिर्फ nesting के लिए Sass install करते थे।

अब (native nesting):
  .card {
    ...
    .title { ... &:hover { ... } }
    &:hover { ... }
    @media (min-width: 700px) { ... }
  }
  -> .card की सारी चीज़ें एक ही block में। Build step नहीं।
```

---

## 🟢 How it Works — Step by Step

```
1. Write a normal rule:               .card { padding: 1rem; }
2. Put a child rule INSIDE it:        .card { .title { font-weight: 700; } }
   Browser reads it as:               .card .title { ... }   (descendant)

3. Use & when you need to attach to the parent itself:
       &:hover        -> .card:hover
       &.active       -> .card.active          (same element, extra class)
       .dark &        -> .dark .card           (parent in a different context)
       & + &          -> .card + .card
       & > p          -> .card > p

4. Nest at-rules directly:
       .card { @media (min-width: 700px) { padding: 2rem; } }
       .card { @container (min-width: 400px) { ... } }
       .card { @supports (display: grid) { ... } }

5. Nested rule specificity: behaves like :is() of the parent selector list.
       .a, #b { .c { } }  ->  :is(.a, #b) .c   (takes the HIGHEST specificity of the list, #b)

SUPPORT AND HISTORY:
  - Original spec (2023): nested selector had to START with a symbol (& . # : [ > + ~).
    So `.card { p { } }` (bare element) was NOT allowed at first.
  - Updated "relaxed nesting": Chrome 120+, Safari 17.2+ (relaxed), Firefox 117+
    now allow `p { }` directly. For old browsers, write `& p { }` — safest.
  - Mixing declarations AFTER nested rules: declarations after a nested rule are
    treated properly in newer browsers (Chrome 130+, Safari 18.2+), older ones
    behaved differently. Rule of thumb: put declarations FIRST, nested rules after.
  - Sass-style suffix `&-title` (to make .card-title) is NOT supported in CSS.
```

## 🟢 कैसे काम करता है? (Hindi)

```
1. Normal rule लिखो:                  .card { padding: 1rem; }
2. उसके अंदर child rule रखो:          .card { .title { font-weight: 700; } }
   Browser इसे ऐसे पढ़ता है:           .card .title { ... }   (descendant)

3. Parent के साथ जोड़ना हो तो & use करो:
       &:hover        -> .card:hover
       &.active       -> .card.active          (वही element, extra class)
       .dark &        -> .dark .card           (parent दूसरे context में)
       & + &          -> .card + .card
       & > p          -> .card > p

4. At-rules सीधे अंदर लिखो:
       .card { @media (min-width: 700px) { padding: 2rem; } }
       .card { @container (min-width: 400px) { ... } }

5. Nested rule की specificity parent selector पर :is() जैसी चलती है।

Support:
  - शुरू में nested selector किसी symbol (& . # : [ > + ~) से शुरू होना ज़रूरी था;
    `.card { p { } }` allowed नहीं था।
  - अब "relaxed nesting" है: Chrome 120+, Safari 17.2+, Firefox 117+ में सीधे `p { }` चलता है।
    पुराने browsers के लिए `& p { }` सबसे safe है।
  - Declarations पहले लिखो, nested rules बाद में।
  - Sass वाला `&-title` (→ .card-title) CSS में काम नहीं करता।
```

---

## 🟡 Real World Example
**Design system for Gmail-style buttons / Amazon cards:** A single `.btn` block contains its hover, focus-visible, disabled state, icon child and a responsive tweak. A new developer reads one block and sees every state of the button. Many teams removed Sass from simple projects after native nesting arrived.

## 🟡 Real Example Hindi mein
**Gmail जैसे buttons / Amazon cards का design system:** एक `.btn` block में hover, focus-visible, disabled state, icon child और responsive बदलाव सब मिल जाते हैं। नया developer एक ही block पढ़कर button की सारी states समझ लेता है। Native nesting आने के बाद कई छोटे projects ने Sass हटा दिया।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CSS Nesting Demo</title>
  <style>
    * { box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; background: #f5f5f7; margin: 0; padding: 24px; }

    /* ─── CARD: everything about .card in ONE block ─── */
    .card {
      /* 1. Declarations FIRST (safe in all nesting-capable browsers) */
      background: #fff;
      border: 1px solid #ddd;
      border-radius: 12px;
      padding: 16px;
      max-width: 360px;
      margin: 0 auto 16px;

      /* 2. Descendant: becomes ".card .title" */
      & .title {
        margin: 0 0 8px;
        font-size: 1.2rem;

        /* 3. Nested again: ".card .title:hover" */
        &:hover { color: #d9480f; }
      }

      /* 4. Child combinator: ".card > p" */
      & > p { color: #555; line-height: 1.5; }

      /* 5. State on the card itself: ".card:hover" */
      &:hover { box-shadow: 0 6px 18px rgb(0 0 0 / .12); }

      /* 6. Extra class on the SAME element: ".card.featured" */
      &.featured { border-color: gold; background: #fffbe6; }

      /* 7. Parent in another context: ".dark .card" */
      .dark & { background: #1f2937; color: #f3f4f6; border-color: #374151; }

      /* 8. Media query nested inside the rule */
      @media (min-width: 700px) {
        padding: 28px;
        max-width: 480px;
      }
    }

    /* ─── BUTTON with states ─── */
    .btn {
      background: #1a73e8;
      color: #fff;
      border: 0;
      padding: 10px 18px;
      border-radius: 8px;
      cursor: pointer;

      &:hover { background: #1557b0; }
      &:focus-visible { outline: 3px solid #fbbc04; outline-offset: 2px; }
      &:disabled { opacity: .5; cursor: not-allowed; }

      /* icon inside button */
      & svg { width: 16px; height: 16px; margin-right: 6px; vertical-align: -2px; }
    }

    /* Dark wrapper to demonstrate ".dark &" */
    .dark { background: #111827; padding: 16px; border-radius: 12px; }
  </style>
</head>
<body>
  <!-- Normal card -->
  <article class="card">
    <h3 class="title">Normal card</h3>
    <p>Hover the title and the card to see nested rules at work.</p>
    <button class="btn">Buy now</button>
    <button class="btn" disabled>Sold out</button>
  </article>

  <!-- Featured card -->
  <article class="card featured">
    <h3 class="title">Featured card</h3>
    <p>Uses &amp;.featured nested rule.</p>
  </article>

  <!-- Inside .dark wrapper -->
  <div class="dark">
    <article class="card">
      <h3 class="title">Inside .dark</h3>
      <p>Uses the .dark &amp; nested rule.</p>
    </article>
  </div>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. CSS Modules + native nesting (Next.js uses its own CSS pipeline that
//    supports nesting through lightningcss / postcss-nesting depending on setup)
/* Card.module.css */
.card {
  padding: 1rem;
  & .title { font-weight: 700; }
  &:hover { box-shadow: 0 4px 12px rgb(0 0 0 / .15); }
}

import styles from './Card.module.css';
export default function Card() {
  return <article className={styles.card}><h3 className={styles.title}>Hi</h3></article>;
}
// Caution: in CSS Modules every class gets hashed; nesting `& .title` still works,
// and `styles.title` is the hashed class for it.

// 2. Tailwind v4 / v3: use the built-in nesting support
//    v3: add "tailwindcss/nesting" before tailwindcss in postcss.config.js
//    v4: nesting works out of the box (uses Lightning CSS)

// 3. If you need to support old browsers, keep Sass or postcss-nesting
//    in the build; it compiles nesting to flat CSS.
```

---

## ⚫ Interview Questions + Answers

**Q1: What is native CSS nesting and how is it different from Sass nesting?**
A1: Native nesting lets browsers parse rules inside rules, no compilation needed. Differences: you use `&` explicitly for same-element selectors (`&:hover`, `&.active`), `&-suffix` string concatenation does not exist, there are no variables/mixins/loops, and nested rules keep the specificity of `:is()` over the parent selector list.

**Q2: What does `&` mean in nested CSS?**
A2: It represents the parent selector. `&:hover` = parent on hover; `.dark &` = parent inside `.dark`; `& + &` = adjacent same elements. Without `&`, a nested selector is a descendant of the parent.

**Q3: Can you nest media queries?**
A3: Yes. `.card { @media (min-width: 700px) { padding: 2rem; } }` applies the declarations to `.card` in that condition. Same with `@container`, `@supports`, `@layer`.

**Q4: Are there any specificity gotchas?**
A4: Nested rules are treated as `:is()` of the parent. If the parent is a selector list like `.a, #b`, the nested rule uses the highest specificity in the list (that of `#b`) for all items. Also, deep nesting makes selectors long and heavy to override; keep it to 2-3 levels.

**Q5: What is the browser support, and how do you handle old browsers?**
A5: Supported in Chrome/Edge 112+, Safari 16.5+, Firefox 117+ (basic); "relaxed" nesting without leading symbol is Chrome 120+, Safari 17.2+. For older browsers, use PostCSS (`postcss-nesting`) or Lightning CSS to flatten it at build time.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Sass-style string concatenation
```css
/* WRONG: does NOT create .card__title */
.card { &__title { color: red; } }

/* CORRECT */
.card { & .card__title { color: red; } }
/* or write .card__title separately */
```

❌ **Mistake 2:** Nesting too deep
```css
/* WRONG: .page .main .list .item .link .icon -> hard to override */
/* CORRECT: 2-3 levels max, use classes (BEM) for deep parts */
```

❌ **Mistake 3:** Writing a bare element selector and expecting support everywhere
```css
/* RISKY in older browsers (before relaxed nesting) */
.card { p { margin: 0; } }

/* SAFE */
.card { & p { margin: 0; } }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Nesting | Rule inside a rule | Rule के अंदर rule |
| & | Nesting selector = parent | Parent selector का चिह्न |
| Relaxed nesting | Nested selector without leading symbol | बिना symbol के nested selector |
| :is() | Matches any in list; highest specificity | List में से कोई भी match |
| PostCSS | Tool to transform CSS in build | Build में CSS बदलने वाला tool |
| Descendant | Element inside another | अंदर का element |

---

## ⚡ 3-Line Summary
**English:**
1. Native CSS nesting lets you write child rules, states and media queries inside the parent rule.
2. Use `&` for same-element states (`&:hover`), parent context (`.dark &`) and combinators; no `&-suffix` concatenation.
3. Supported in modern browsers (2023+); put declarations first and keep nesting shallow.

**Hindi:**
1. Native CSS nesting से child rules, states और media queries parent rule के अंदर लिखे जाते हैं।
2. `&` से same-element states (`&:hover`), parent context (`.dark &`) और combinators लिखो; `&-suffix` नहीं चलता।
3. Modern browsers (2023+) में चलता है; declarations पहले लिखो और nesting कम गहरी रखो।

---

## ➡️ Next Topic
**106. CSS Layers (@layer)** — nesting से code साफ़ हुआ; अब specificity की लड़ाई को layers के ज़रिए पूरी तरह control करना सीखेंगे।
