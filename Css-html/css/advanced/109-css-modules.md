# 109. CSS Modules
# हिंदी में: CSS Modules — हर Component का अपना Scoped CSS

---

## 🔵 Simple Definition (English)
A **CSS Module** is a normal `.css` file (named `*.module.css`) whose class names are **locally scoped by default**. At build time each class like `.title` is renamed to a unique name such as `Card_title__x7Ab2`, and you import the mapping as a JS object: `styles.title`. So two components can both use `.title` without clashing.

## 🔵 सरल परिभाषा (Hindi)
**CSS Module** एक normal `.css` file (नाम `*.module.css`) है जिसकी class names **default रूप से local scope** में होती हैं। Build के समय हर class (जैसे `.title`) का नाम unique बन जाता है, जैसे `Card_title__x7Ab2`, और आप mapping को JS object की तरह import करते हो: `styles.title`। इसलिए दो components दोनों `.title` use कर सकते हैं, टकराव नहीं होता।

---

## 🔴 Problem it Solves
```
BEFORE (global CSS):
  header.css:  .title { font-size: 32px; }
  card.css:    .title { font-size: 16px; }
  -> Both are global. Whichever loads last wins. Cards suddenly look huge.
  -> Fix: long BEM names (.card__title--large) and strict team discipline.
  -> Deleting CSS is scary: "is .title used somewhere else?"

AFTER (CSS Modules):
  Card.module.css:   .title { ... }   ->   .Card_title__x7Ab2
  Header.module.css: .title { ... }   ->   .Header_title__k9Qp1
  -> Conflicts are impossible. Delete a component = delete its CSS safely.
  -> Still plain CSS: no new syntax to learn, zero runtime cost.
```

## 🔴 यह क्यों बना? (Hindi)
```
पहले (global CSS):
  header.css:  .title { font-size: 32px; }
  card.css:    .title { font-size: 16px; }
  -> दोनों global हैं। जो बाद में load होगी वो जीतेगी। Cards अचानक बड़े दिखते हैं।
  -> उपाय: लंबे BEM नाम (.card__title--large) और team का अनुशासन।
  -> CSS हटाना डरावना: "क्या .title कहीं और use हो रहा है?"

अब (CSS Modules):
  Card.module.css:   .title { ... }   ->   .Card_title__x7Ab2
  Header.module.css: .title { ... }   ->   .Header_title__k9Qp1
  -> टकराव असंभव। Component हटाओ = उसका CSS भी सुरक्षित हट जाता है।
  -> फिर भी plain CSS: नया syntax नहीं, runtime cost शून्य।
```

---

## 🟢 How it Works — Step by Step

```
1. Create a file named  Card.module.css  (the ".module.css" suffix matters):
       .card  { padding: 16px; }
       .title { font-weight: 700; }

2. Import it in the component:
       import styles from './Card.module.css';
   `styles` is an object:  { card: "Card_card__a1B2c", title: "Card_title__d3E4f" }

3. Use the generated names:
       <div className={styles.card}><h2 className={styles.title}>Hi</h2></div>

4. At build time (webpack css-loader / Vite / Next.js built in), every class
   and keyframe name in that file gets a unique hash. Result in the browser:
       <div class="Card_card__a1B2c">...

5. SPECIAL FEATURES:
   a) :global(.x)          -> opt out of scoping for one selector
       .wrapper :global(.react-select) { ... }
   b) composes:            -> reuse another class (like a mixin, no duplication)
       .primary { composes: button from './base.module.css'; color: white; }
   c) Multiple classes:    className={`${styles.btn} ${styles.primary}`}
                           or clsx(styles.btn, isActive && styles.active)
   d) CSS variables for dynamic values: style={{ '--color': props.color }}
      and in CSS:  color: var(--color);
   e) Class names with dashes:  .main-title  -> styles['main-title']
      (camelCase config exists: localsConvention: 'camelCase')
   f) Element selectors are NOT scoped:  h2 { }  is still global.
      Next.js requires CSS Module selectors to be "pure" (must contain at
      least one class or id) -> `h2 {}` alone throws an error.

6. Not scoped: @keyframes names ARE scoped; CSS variables on :root are global.
```

## 🟢 कैसे काम करता है? (Hindi)

```
1. File बनाओ  Card.module.css  (".module.css" suffix ज़रूरी है):
       .card  { padding: 16px; }
       .title { font-weight: 700; }

2. Component में import करो:
       import styles from './Card.module.css';
   `styles` एक object है:  { card: "Card_card__a1B2c", title: "Card_title__d3E4f" }

3. Generated नाम use करो:
       <div className={styles.card}><h2 className={styles.title}>Hi</h2></div>

4. Build के समय (webpack css-loader / Vite / Next.js में built-in) हर class और
   keyframe name में unique hash जुड़ जाता है। Browser में:
       <div class="Card_card__a1B2c">...

5. खास features:
   a) :global(.x)    -> किसी selector को scope से बाहर रखना
   b) composes:      -> दूसरी class को reuse करना (mixin जैसा)
   c) कई classes:    className={`${styles.btn} ${styles.primary}`} या clsx(...)
   d) Dynamic values: style={{ '--color': props.color }} और CSS में var(--color)
   e) Dash वाले नाम: styles['main-title']
   f) Element selectors scoped नहीं होते: h2 { } global रहता है।
      Next.js में selector "pure" होना चाहिए (कम से कम एक class या id)।

6. @keyframes के नाम scoped होते हैं; :root के CSS variables global रहते हैं।
```

---

## 🟡 Real World Example
**Next.js apps like a Swiggy/Zomato-style dashboard:** Each component folder has `Navbar.jsx` + `Navbar.module.css`, `RestaurantCard.jsx` + `RestaurantCard.module.css`. Ten developers can each name their wrapper `.container` without coordination. Next.js supports CSS Modules out of the box, so many production App Router projects use them for component CSS and keep a small `globals.css` for resets and variables.

## 🟡 Real Example Hindi mein
**Next.js apps (Swiggy/Zomato जैसा dashboard):** हर component folder में `Navbar.jsx` + `Navbar.module.css`, `RestaurantCard.jsx` + `RestaurantCard.module.css` होती हैं। दस developers बिना बात किए अपने wrapper का नाम `.container` रख सकते हैं। Next.js में CSS Modules built-in हैं, इसलिए कई production App Router projects component CSS के लिए इन्हें और resets/variables के लिए छोटी `globals.css` use करते हैं।

---

## 💻 Live Code Example

CSS Modules need a **build tool** (Next.js, Vite, CRA, webpack) to rename classes, so they cannot run from a plain `.html` file. Below: the real project files first, then a plain HTML page that **simulates the output** so you can see the idea in the browser.

```css
/* ─── src/components/Card.module.css ─── */
/* Every class here is LOCAL to Card */
.card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 16px;
  max-width: 320px;
}

.title {
  margin: 0 0 8px;
  font-size: 1.1rem;
  color: var(--text, #111827);   /* global CSS variable from globals.css */
}

/* Reuse styles from another class in the SAME file */
.button { padding: 8px 16px; border: 0; border-radius: 8px; cursor: pointer; }
.primary { composes: button; background: #e23744; color: #fff; }
.ghost   { composes: button; background: transparent; color: #e23744; border: 1px solid #e23744; }

/* Style a child coming from a 3rd-party lib using :global */
.card :global(.badge) { background: gold; padding: 2px 6px; border-radius: 4px; }

/* @keyframes names are scoped too */
@keyframes pop { from { transform: scale(.9); opacity: 0; } to { transform: scale(1); opacity: 1; } }
.card { animation: pop .25s ease-out; }
```

```jsx
// ─── src/components/Card.jsx ───
import styles from './Card.module.css';   // styles = { card, title, button, primary, ghost }
import clsx from 'clsx';                  // optional helper for conditional classes

export default function Card({ title, active, onBuy }) {
  return (
    <div className={clsx(styles.card, active && styles.active)}>
      <h2 className={styles.title}>{title}</h2>
      <button className={styles.primary} onClick={onBuy}>Buy</button>
      <button className={styles.ghost}>Save</button>
    </div>
  );
}
// In the browser DOM: <div class="Card_card__a1B2c"> ... <h2 class="Card_title__d3E4f">
```

```html
<!-- SIMULATION: plain HTML showing what the build produces (open directly in browser) -->
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>CSS Modules Simulation</title>
  <style>
    /* Two components BOTH wrote ".title", the build renamed them: no clash */
    .Header_title__k9Qp1 { font-size: 28px; color: #e23744; margin: 0 0 12px; }
    .Card_card__a1B2c    { border: 1px solid #ddd; border-radius: 12px; padding: 16px; max-width: 320px; }
    .Card_title__d3E4f   { font-size: 16px; color: #111; margin: 0 0 8px; }   /* same source name .title */
  </style>
</head>
<body style="font-family: sans-serif; padding: 20px">
  <h1 class="Header_title__k9Qp1">Header .title (large, red)</h1>
  <div class="Card_card__a1B2c">
    <h2 class="Card_title__d3E4f">Card .title (small, dark)</h2>
    <p>Both were written as <code>.title</code> in different module files.</p>
  </div>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. Next.js (App Router or Pages): works with ZERO config for *.module.css
//    app/page.jsx
import styles from './page.module.css';
export default function Home() { return <main className={styles.main}>Hello</main>; }

// 2. Global CSS only in the root layout (or _app.js in Pages Router)
//    app/layout.jsx -> import './globals.css';

// 3. TypeScript: Next.js ships types for *.module.css. For Vite add
//    "types": ["vite/client"]. For stricter typing use typed-css-modules or typescript-plugin-css-modules.

// 4. Combining with Tailwind: possible. Use CSS Modules for complex one-off
//    animations/selectors, Tailwind for everyday spacing.

// 5. Vite config for dash -> camelCase names:
// export default { css: { modules: { localsConvention: 'camelCaseOnly' } } }

// 6. Dynamic values through CSS variables (no inline styles for everything)
<div className={styles.bar} style={{ '--progress': `${percent}%` }} />
/* .bar { width: var(--progress); } */
```

---

## ⚫ Interview Questions + Answers

**Q1: What are CSS Modules and what problem do they solve?**
A1: CSS files whose class names are locally scoped by default. The bundler rewrites class names to unique hashed names and exports a mapping object. This removes global name collisions and makes CSS safe to delete with its component, while staying plain CSS.

**Q2: How do CSS Modules differ from CSS-in-JS like styled-components?**
A2: CSS Modules are static CSS extracted at build time, so there is zero runtime cost, they work great with React Server Components, and you keep real `.css` files. CSS-in-JS generates styles at runtime from JS, makes dynamic props styling easy, but adds runtime overhead and needs extra setup with Server Components.

**Q3: How do you apply multiple classes or conditional classes?**
A3: Template string (`` `${styles.a} ${styles.b}` ``), array join, or `clsx(styles.a, cond && styles.b)`. `composes` in the CSS file can also combine classes at build time.

**Q4: How do you target a global class or a third-party class from a module?**
A4: Use `:global(.class-name)`; e.g. `.wrapper :global(.slick-slide) { ... }`. Or `:global { ... }` block. Without it, `.slick-slide` would be renamed and match nothing.

**Q5: What are common pitfalls?**
A5: Using `styles.main-title` (invalid JS; use `styles['main-title']`), using element-only selectors (global and not allowed as pure in Next.js), expecting CSS variables or `:root` to be scoped, forgetting the `.module.css` extension (then it's global CSS), and dynamic class lookup like `styles[`btn-${type}`]` which works only if the classes exist in the file (the bundler keeps them).

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Using a plain class string instead of the imported object
```jsx
/* WRONG: hashed name is not "title" */
<h2 className="title">Hi</h2>
/* CORRECT */
<h2 className={styles.title}>Hi</h2>
```

❌ **Mistake 2:** Importing the file but forgetting `.module` in its name
```jsx
import styles from './Card.css';        // WRONG: global CSS, styles is undefined/empty
import styles from './Card.module.css'; // CORRECT
```

❌ **Mistake 3:** Style an element only (not scoped, may break the Next.js build)
```css
/* WRONG */ h2 { color: red; }
/* CORRECT */ .card h2 { color: red; }   /* contains a local class */
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| CSS Module | CSS file with locally scoped classes | Local scope वाली CSS file |
| Scoping | Limiting names to one component | नाम को component तक सीमित करना |
| Hashed class | Unique generated class name | Build से बना unique नाम |
| :global() | Opt out of local scoping | Scoping से बाहर |
| composes | Reuse another class | दूसरी class दोबारा use करना |
| Bundler | Tool that builds assets | Build करने वाला tool |
| Pure selector | Selector containing a local class/id | Local class वाला selector |

---

## ⚡ 3-Line Summary
**English:**
1. CSS Modules (`*.module.css`) scope class names locally by hashing them at build time, preventing global clashes.
2. Import as `styles` and use `className={styles.name}`; use `:global()` for external classes and `composes` for reuse.
3. Zero runtime cost, built into Next.js/Vite; keep resets and variables in a global CSS file.

**Hindi:**
1. CSS Modules (`*.module.css`) build के समय class names को hash करके local scope देते हैं, इसलिए global टकराव नहीं होता।
2. `styles` import करके `className={styles.name}` use करो; बाहरी classes के लिए `:global()` और reuse के लिए `composes`।
3. Runtime cost शून्य, Next.js/Vite में built-in; resets और variables के लिए global CSS file रखो।

---

## ➡️ Next Topic
**110. Styled Components Basics** — CSS-in-JS: styles को JS में लिखना, props से dynamic styling और theme के साथ।
