# 91. CSS Architecture (BEM, OOCSS, SMACSS)
# हिंदी में: CSS Architecture — बड़े Project में CSS को Organize करना

---

## 🔵 Simple Definition (English)
CSS architecture is a set of **rules for naming, structuring and organizing CSS** so a big team can add features without breaking old styles. The three classic methodologies are **BEM** (naming), **OOCSS** (reusable objects), and **SMACSS** (categorizing rules).

## 🔵 सरल परिभाषा (Hindi)
CSS architecture **naming, structure और organization के नियम** हैं ताकि बड़ी team नए features जोड़ते समय पुराने styles न तोड़े। तीन classic तरीके हैं: **BEM** (naming), **OOCSS** (reusable objects), और **SMACSS** (rules की categories)।

---

## 🔴 Problem it Solves
```
WITHOUT ARCHITECTURE (typical 2-year-old project):
  .header .nav ul li a { color: red; }          /* tied to the HTML structure */
  .sidebar .nav ul li a { color: blue; }        /* another copy, different place */
  #main .content .title { font-size: 20px !important; }   /* specificity war */
  .title2 { ... }  .title-new { ... }  .title-final { ... }  /* nobody knows which is used */

  Problems:
  - Changing one rule breaks something far away (global scope)
  - Nobody dares to delete CSS ("maybe it is used somewhere")
  - Specificity keeps rising, then !important everywhere
  - New developer spends days understanding naming

WITH ARCHITECTURE (BEM example):
  .nav__link { color: red; }                    /* flat, one class = (0,1,0) */
  .nav__link--active { color: blue; }
  .card__title { font-size: 20px; }
  /* Name tells what it is, where it belongs. Safe to edit, safe to delete. */
```

## 🔴 यह क्यों बना? (Hindi)
CSS में सब कुछ **global** है। बड़े project में `.title` एक जगह बदलो तो दूसरी जगह टूट जाता है। Specificity बढ़ती जाती है और फिर हर जगह `!important`। Architecture से हर class का नाम बताता है कि वो क्या है और कहाँ की है — इसलिए CSS safe तरीके से बदला और delete किया जा सकता है।

---

## 🟢 How it Works — Step by Step

```
1) BEM — Block, Element, Modifier  (naming convention)
──────────────────────────────────────────────────────────
  .block              → standalone component          .card
  .block__element     → part of the block             .card__title
  .block--modifier    → variation / state             .card--featured
  .block__el--mod                                     .card__button--disabled

  HTML:
    <article class="card card--featured">
      <h3 class="card__title">Biryani</h3>
      <button class="card__button card__button--disabled">Order</button>
    </article>

  RULES:
  - Only CLASS selectors (no ids, no tag selectors for styling)
  - Never nest selectors: NOT .card .card__title (use .card__title)
  - NO "element of element": NOT .card__body__title  → use .card__title
  - Modifier is added ALONGSIDE the base class (card card--featured)

2) OOCSS — Object Oriented CSS  (Nicole Sullivan)
──────────────────────────────────────────────────────────
  Principle A: SEPARATE STRUCTURE from SKIN
     .media   { display: flex; gap: 12px; }          /* structure */
     .skin-dark { background: #111; color: #fff; }   /* looks */
  Principle B: SEPARATE CONTAINER from CONTENT
     Style should not depend on WHERE it sits (.sidebar .btn is bad).
  Result: small reusable "objects": .media, .btn, .card, .stack
          Combine: <div class="media skin-dark">
  (Tailwind utilities are the modern, extreme form of this idea.)

3) SMACSS — Scalable and Modular Architecture (Jonathan Snook)
──────────────────────────────────────────────────────────
  5 categories of rules:
  1. BASE     → defaults for elements: body, a, h1      (no classes)
  2. LAYOUT   → page-level structure, prefix l-/layout-  (.l-sidebar)
  3. MODULE   → reusable components                      (.card, .navbar)
  4. STATE    → on/off conditions, prefix is-/has-       (.is-open, .is-hidden)
  5. THEME    → colors / skins                           (.theme-dark)

COMPARISON:
  BEM    → HOW to NAME classes     (most popular; used with CSS, Sass, CSS Modules)
  OOCSS  → HOW to SHARE styles     (reuse, composition)
  SMACSS → HOW to ORGANIZE files   (folders and categories)
  They are NOT competitors: many teams mix BEM names + SMACSS folders + OOCSS reuse.

FILE STRUCTURE (SMACSS-style, ITCSS-like):
  styles/
    base/        reset.css  typography.css
    layout/      grid.css  header.css
    components/  card.css  button.css  navbar.css
    utilities/   helpers.css   (.u-hidden, .u-text-center)
    themes/      dark.css
```

## 🟢 कैसे काम करता है? (Hindi)
1. **BEM:** `block__element--modifier`। Block = पूरा component (`card`), Element = उसका हिस्सा (`card__title`), Modifier = variation (`card--featured`)। सिर्फ class selectors, nesting नहीं।
2. **OOCSS:** Structure (layout) और Skin (रंग) अलग रखो। Style इस पर निर्भर न हो कि element कहाँ रखा है। छोटे reusable "objects" बनाओ और combine करो।
3. **SMACSS:** Rules को 5 category में बाँटो — Base, Layout, Module, State, Theme। State classes `is-open` जैसी होती हैं।
4. **फ़र्क:** BEM = नाम कैसे रखें, OOCSS = reuse कैसे करें, SMACSS = files कैसे organize करें। तीनों साथ भी इस्तेमाल होते हैं।

---

## 🟡 Real World Example
**Swiggy / Zomato restaurant card:** Ek `restaurant-card` block hai. Uske parts `restaurant-card__image`, `restaurant-card__name`, `restaurant-card__rating`. Jab restaurant "promoted" hota hai tab `restaurant-card--promoted` modifier lagta hai. Team ke 20 developers alag-alag pages par kaam karte hain aur ek doosre ka CSS nahi todte.
**Real BEM users:** Yandex (BEM ka creator), Bootstrap 4 ka kuch hissa (`.card-body`, `.btn-primary` - BEM-jaisa), GOV.UK Design System, Mailchimp. **SMACSS-style state classes:** `.is-active`, `.is-open`, `.has-error` har jagah milte hain.
**OOCSS in real life:** Facebook ka "media object" (image left, text right) ek hi class se kai jagah use hota tha.

## 🟡 Real Example Hindi mein
**Swiggy/Zomato restaurant card:** एक `restaurant-card` block है। उसके parts: `restaurant-card__image`, `restaurant-card__name`, `restaurant-card__rating`। Promoted restaurant पर `restaurant-card--promoted` modifier लगता है। 20 developers अलग pages पर काम करते हैं और किसी का CSS किसी को नहीं तोड़ता।
**Real users:** Yandex (BEM के creator), GOV.UK Design System। **State classes:** `.is-active`, `.is-open`, `.has-error` लगभग हर बड़े project में दिखते हैं।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CSS Architecture: BEM + OOCSS + SMACSS</title>
  <style>
    /* ═══ SMACSS: 1. BASE (element defaults, no classes) ════════ */
    *, *::before, *::after { box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; background: #f5f5f5; color: #222; margin: 0; padding: 20px; }
    h1 { margin-top: 0; }

    /* ═══ SMACSS: 2. LAYOUT (prefix l-) ═════════════════════════ */
    .l-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
      gap: 16px;
    }

    /* ═══ OOCSS: reusable OBJECT (structure only, no colors) ════ */
    .media { display: flex; gap: 12px; align-items: center; }   /* image + text row */
    .media__img { width: 56px; height: 56px; border-radius: 8px; flex: none; }

    /* ═══ OOCSS: SKIN (look only, reusable on anything) ════════ */
    .skin-white { background: #fff; box-shadow: 0 1px 4px rgba(0,0,0,.15); border-radius: 12px; }

    /* ═══ BEM: BLOCK  (.restaurant-card) ════════════════════════ */
    .restaurant-card { padding: 14px; position: relative; }  /* flat selector: (0,1,0) */

    /* BEM ELEMENTS (parts of the block) */
    .restaurant-card__name   { margin: 0; font-size: 16px; }
    .restaurant-card__meta   { margin: 2px 0 0; font-size: 13px; color: #666; }
    .restaurant-card__rating {
      margin-left: auto;            /* push to the far right of the .media row */
      background: #2e7d32; color: #fff;
      padding: 2px 8px; border-radius: 6px; font-size: 13px;
    }
    .restaurant-card__button {
      margin-top: 12px; width: 100%;
      padding: 8px; border: 0; border-radius: 8px;
      background: #e23744; color: #fff; cursor: pointer;
    }

    /* BEM MODIFIERS (variations): added ALONGSIDE the base class */
    .restaurant-card--promoted { outline: 2px solid #ff9800; }
    .restaurant-card--promoted::before {
      content: "Promoted"; position: absolute; top: -10px; left: 12px;
      background: #ff9800; color: #fff; font-size: 11px; padding: 1px 8px; border-radius: 10px;
    }
    .restaurant-card__button--disabled { background: #bbb; cursor: not-allowed; }

    /* ═══ SMACSS: 4. STATE (prefix is-/has-) ════════════════════ */
    .is-hidden { display: none; }
    .is-selected { outline: 2px solid #1976d2; }

    /* ═══ SMACSS: 5. THEME ══════════════════════════════════════ */
    .theme-dark .skin-white { background: #222; color: #eee; }
    .theme-dark .restaurant-card__meta { color: #aaa; }

    /* ═══ UTILITY (single purpose helpers) ══════════════════════ */
    .u-mb-16 { margin-bottom: 16px; }
  </style>
</head>
<body>
  <h1>Restaurants near you</h1>

  <!-- Theme toggle shows how SMACSS theme + state classes work -->
  <button class="u-mb-16" onclick="document.body.classList.toggle('theme-dark')">Toggle theme</button>

  <section class="l-grid">

    <!-- Normal card: block + OOCSS skin -->
    <article class="restaurant-card skin-white">
      <div class="media">
        <img class="media__img" alt="" src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='56' height='56'%3E%3Crect width='56' height='56' fill='%23ffcc80'/%3E%3C/svg%3E">
        <div>
          <h2 class="restaurant-card__name">Biryani House</h2>
          <p class="restaurant-card__meta">Mughlai - 30 min</p>
        </div>
        <span class="restaurant-card__rating">4.3</span>
      </div>
      <button class="restaurant-card__button">Order now</button>
    </article>

    <!-- Modifier: promoted -->
    <article class="restaurant-card restaurant-card--promoted skin-white">
      <div class="media">
        <img class="media__img" alt="" src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='56' height='56'%3E%3Crect width='56' height='56' fill='%23ef9a9a'/%3E%3C/svg%3E">
        <div>
          <h2 class="restaurant-card__name">Pizza Corner</h2>
          <p class="restaurant-card__meta">Italian - 25 min</p>
        </div>
        <span class="restaurant-card__rating">4.6</span>
      </div>
      <button class="restaurant-card__button">Order now</button>
    </article>

    <!-- Element modifier: closed (disabled button) -->
    <article class="restaurant-card skin-white">
      <div class="media">
        <img class="media__img" alt="" src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='56' height='56'%3E%3Crect width='56' height='56' fill='%23a5d6a7'/%3E%3C/svg%3E">
        <div>
          <h2 class="restaurant-card__name">Dosa Plaza</h2>
          <p class="restaurant-card__meta">South Indian - Closed</p>
        </div>
        <span class="restaurant-card__rating">4.1</span>
      </div>
      <button class="restaurant-card__button restaurant-card__button--disabled" disabled>Closed</button>
    </article>

  </section>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. BEM works great with plain CSS in React:
export default function RestaurantCard({ r }) {
  // build class list: base + modifier
  const cls = ['restaurant-card', r.promoted && 'restaurant-card--promoted']
    .filter(Boolean).join(' ');
  return (
    <article className={cls}>
      <h2 className="restaurant-card__name">{r.name}</h2>
      <button className={`restaurant-card__button ${r.open ? '' : 'restaurant-card__button--disabled'}`}>
        Order
      </button>
    </article>
  );
}

// 2. Use the "clsx" library to combine modifiers cleanly:
import clsx from 'clsx';
<article className={clsx('card', { 'card--featured': featured, 'is-open': open })} />

// 3. CSS Modules REPLACE the need for BEM's long names (scope is automatic):
/* Card.module.css */
.card { }  .title { }  .featured { }
import s from './Card.module.css';
<article className={clsx(s.card, featured && s.featured)}>
  <h3 className={s.title}>...</h3>
</article>
// Class names become Card_title__x7Yz — no global collision.

// 4. Tailwind = OOCSS taken to the extreme (many tiny single-purpose objects):
<div className="flex items-center gap-3 rounded-xl bg-white p-4 shadow">...</div>
// Extract repeated patterns into a React COMPONENT (not a CSS class) — the component is the "block".

// 5. Component-based frameworks make "block" = component, "element" = its inner tags,
//    "modifier" = props (variant="featured").
```

---

## ⚫ Interview Questions + Answers

**Q1: What is BEM and what are its rules?**
A1: BEM = Block, Element, Modifier: `.block__element--modifier`. Block is a standalone component (`.card`), element is a part of it (`.card__title`), modifier is a variation or state (`.card--featured`). Rules: use only class selectors, keep specificity flat (0,1,0), no deep nesting, no element-of-element names (`.card__body__title` is wrong), and apply the modifier along with the base class. Benefit: no specificity wars, easy to find and delete code.

**Q2: What is OOCSS? What are its two principles?**
A2: Object Oriented CSS: build small reusable "objects". Principle 1: **separate structure from skin** (layout properties in one class, colors/borders in another). Principle 2: **separate container from content**: a component must look the same wherever it is placed, so avoid `.sidebar .button` overrides. Utility-first CSS like Tailwind follows the same idea.

**Q3: What are the five categories of SMACSS?**
A3: Base (element defaults), Layout (page structure, `l-` prefix), Module (reusable components), State (`is-active`, `has-error`), and Theme (visual skins). It helps organize files and decide where a new rule belongs.

**Q4: BEM vs CSS Modules vs Tailwind: how do you choose?**
A4: BEM is a naming **convention** (human discipline) for global CSS. CSS Modules give **automatic scoping** by hashing class names at build time, so no naming convention is needed. Tailwind uses **utility classes** and avoids writing custom CSS. In React/Next.js teams usually pick CSS Modules or Tailwind; BEM is still common in design systems, legacy code, and server-rendered sites. Choose by team size, tooling, and whether you need global CSS.

**Q5: What are the downsides of BEM?**
A5: Long verbose class names (`.search-form__submit-button--disabled`), HTML gets heavier, naming discipline needs to be enforced (linter like stylelint-selector-bem-pattern), and it does not solve global scope — two blocks with the same name still collide. It also does not tell you how to organize files, which is why people pair it with SMACSS or ITCSS.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Nesting BEM elements inside elements
```css
/* WRONG: element of an element, ties name to HTML depth */
.card__body__title { }

/* CORRECT: elements are always one level deep under the block */
.card__title { }
```

❌ **Mistake 2:** Writing modifier without the base class, or styling by nesting
```html
<!-- WRONG: modifier alone loses base styles -->
<div class="card--featured">
<!-- CORRECT -->
<div class="card card--featured">
```
```css
/* WRONG: descendant selectors raise specificity */
.card .card__title { }
/* CORRECT */
.card__title { }
```

❌ **Mistake 3:** Styling by tag or id inside components
```css
/* WRONG: global, hard to override */
#header ul li a { }
/* CORRECT */
.nav__link { }
```

❌ **Mistake 4:** Mixing layout concerns into the component (breaking OOCSS)
```css
/* WRONG: the card decides its own margin in the grid */
.card { margin: 0 24px 24px 0; }

/* CORRECT: the PARENT/layout controls spacing */
.l-grid { display: grid; gap: 24px; }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| BEM | Block__Element--Modifier naming | Naming का तरीका |
| Block | Independent component | पूरा component |
| Element | Part of a block | Block का हिस्सा |
| Modifier | Variation or state | Variation / रूप |
| OOCSS | Reusable CSS objects | Reusable objects |
| SMACSS | Categorize rules in 5 groups | 5 category में बाँटना |
| State class | is-open, has-error | अवस्था बताने वाली class |
| ITCSS | Inverted triangle layering of CSS | CSS की layers |
| Utility class | Single-purpose class | एक काम वाली class |

---

## ⚡ 3-Line Summary
**English:**
1. CSS is global, so big projects need rules: BEM names classes, OOCSS promotes reusable objects, SMACSS categorizes files and rules.
2. BEM (`block__element--modifier`) keeps selectors flat at (0,1,0), avoiding specificity wars.
3. In React/Next.js, CSS Modules and Tailwind often replace BEM, but the ideas (component as block, reuse, flat specificity) still apply.

**Hindi:**
1. CSS global होता है इसलिए नियम चाहिए: BEM naming, OOCSS reuse, SMACSS organization।
2. BEM (`block__element--modifier`) selectors flat रखता है — specificity की लड़ाई नहीं।
3. React/Next.js में CSS Modules और Tailwind BEM की जगह लेते हैं, पर सोच वही रहती है।

---

## ➡️ Next Topic
**92. CSS Specificity Wars + !important** — जब architecture नहीं होता तब specificity की लड़ाई कैसे होती है और उसे कैसे सुलझाएँ।
