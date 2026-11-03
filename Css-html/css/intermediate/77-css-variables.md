# 77. CSS Variables (Custom Properties)
# हिंदी में: CSS Variables — एक बार लिखो, हर जगह use करो

---

## 🔵 Simple Definition (English)
CSS Variables (Custom Properties) let you store a value like a colour or spacing under a name that starts with `--`, for example `--brand: #ff5a5f;`. You read it anywhere with `var(--brand)`. Unlike Sass variables, they live in the browser, follow the cascade, and can be changed at runtime with JavaScript or media queries.

## 🔵 सरल परिभाषा (Hindi)
CSS Variables (Custom Properties) में आप किसी value (जैसे colour या spacing) को `--` से शुरू होने वाले नाम से store करते हो, जैसे `--brand: #ff5a5f;`। फिर कहीं भी `var(--brand)` से पढ़ लेते हो। Sass variables से अलग, ये browser में live रहते हैं, cascade follow करते हैं, और JavaScript या media query से runtime पर बदले जा सकते हैं।

---

## 🔴 Problem it Solves
```
BEFORE CSS VARIABLES:
  - Brand colour #ff5a5f repeated in 80 places across the stylesheet
  - Rebrand = find-and-replace, easy to miss one
  - Dark mode = duplicate the whole stylesheet
  - Sass variables compile to fixed values: JS cannot change them
  - Theme switching needed a new CSS file or inline style hacks

AFTER CSS VARIABLES:
  :root { --brand: #ff5a5f; }
  .btn  { background: var(--brand); }
  /* Change ONE line (or one class on <html>) and the whole site updates */
```

## 🔴 यह क्यों बना? (Hindi)
```
पहले:
  - एक ही colour 80 जगह copy-paste होता था
  - Rebrand करना = find-replace, कोई एक जगह छूट जाती थी
  - Dark mode = पूरी stylesheet दोबारा लिखना
  - Sass variables compile होकर fixed हो जाते हैं, JS से नहीं बदलते

अब:
  :root { --brand: #ff5a5f; }
  एक जगह बदलो, पूरी site बदल जाती है। Theme switching आसान।
```

---

## 🟢 How it Works — Step by Step

```
1. DECLARE: name must start with two dashes. Case-sensitive.
     :root { --space: 16px; --brand: #ff5a5f; }

2. USE: var(--name, fallback)
     padding: var(--space);
     color: var(--text, #222);      /* fallback used if --text is not defined */

3. SCOPE + INHERITANCE:
     Variables inherit like `color` or `font-family`.
     :root  = global (same as html, but with higher specificity than `html`)
     .card  = only .card and its children see the override

     :root { --brand: red; }
     .promo { --brand: gold; }      /* everything inside .promo uses gold */

4. RUNTIME CHANGE (this is the superpower):
     document.documentElement.style.setProperty('--brand', 'blue');
     Browser recalculates styles, everything using var(--brand) repaints.

5. THEMING:
     [data-theme="dark"] { --bg: #111; --text: #eee; }
     Toggle the attribute, every component re-themes. No JS per component.

6. GOTCHAS:
     - Variables hold TOKENS, not full declarations: --pad: 10px 20px is OK.
     - Invalid at computed time = property becomes `unset` (not ignored silently like bad CSS)
     - Cannot be used in media query conditions: @media (min-width: var(--bp)) does NOT work
     - Browser support: all modern browsers, Chrome 49+, Safari 9.1+. IE11 does not support.
     - @property (Houdini) lets you register typed variables so they can be animated.
       Support: Chrome 85+, Safari 16.4+, Firefox 128+.
```

## 🟢 कैसे काम करता है? (Hindi)

```
1. DECLARE: नाम `--` से शुरू होना चाहिए, case-sensitive है।
     :root { --space: 16px; --brand: #ff5a5f; }

2. USE: var(--name, fallback)
     color: var(--text, #222);   /* --text न मिले तो #222 */

3. SCOPE + INHERITANCE: variables parent से child को inherit होते हैं।
     :root में लिखो = पूरी page के लिए global।
     .promo में override करो = सिर्फ .promo और उसके children पर असर।

4. RUNTIME: JS से बदल सकते हो
     document.documentElement.style.setProperty('--brand', 'blue');
     सब कुछ जो var(--brand) use करता है, तुरंत update हो जाता है।

5. THEMING: [data-theme="dark"] में variables override करो, attribute toggle करो,
   पूरा UI बदल जाता है।

6. ध्यान दो: media query की condition में var() काम नहीं करता।
   Invalid value हो तो property `unset` हो जाती है।
```

---

## 🟡 Real World Example
**Zomato / Swiggy style theming:** Swiggy shows an orange brand across buttons, links, and offer badges. Behind the scenes a single variable like `--brand-primary` drives all of them. During festive campaigns (Diwali, IPL) the marketing team can swap a handful of variables (`--brand-primary`, `--hero-bg`) and the entire app re-skins without touching component CSS. The dark mode toggle on Instagram web works the same way: the `<html>` class changes, and `--bg`, `--text`, `--border` get new values.

## 🟡 Real Example Hindi mein
**Zomato / Swiggy style theming:** Swiggy में buttons, links और offer badges सब orange दिखते हैं। पीछे एक ही variable `--brand-primary` होता है। Diwali या IPL campaign में बस दो-तीन variables बदलने से पूरा app re-skin हो जाता है, component CSS को छूना नहीं पड़ता। Instagram web का dark mode भी ऐसे ही चलता है: `<html>` पर class बदलती है और `--bg`, `--text`, `--border` की values बदल जाती हैं।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CSS Variables Demo</title>
  <style>
    /* 1. GLOBAL TOKENS: declared on :root so every element can read them */
    :root {
      --brand: #ff5a5f;          /* brand colour */
      --bg: #ffffff;             /* page background */
      --text: #222222;           /* main text colour */
      --card-bg: #f7f7f7;        /* card background */
      --space: 16px;             /* base spacing unit */
      --radius: 12px;            /* shared corner radius */
    }

    /* 2. DARK THEME: only override the tokens, no component CSS changes */
    [data-theme="dark"] {
      --bg: #121212;
      --text: #f1f1f1;
      --card-bg: #1e1e1e;
    }

    *, *::before, *::after { box-sizing: border-box; }

    /* 3. USE the tokens via var() */
    body {
      margin: 0;
      padding: calc(var(--space) * 2);          /* variables work inside calc() */
      font-family: system-ui, sans-serif;
      background: var(--bg);
      color: var(--text);
      transition: background 0.3s, color 0.3s;  /* smooth theme switch */
    }

    .card {
      background: var(--card-bg);
      padding: var(--space);
      border-radius: var(--radius);
      max-width: 340px;
      margin-bottom: var(--space);
    }

    .btn {
      background: var(--btn-bg, var(--brand));  /* fallback chain: local override, else brand */
      color: #fff;
      border: 0;
      padding: calc(var(--space) / 2) var(--space);
      border-radius: var(--radius);
      cursor: pointer;
      font-size: 1rem;
    }

    /* 4. LOCAL SCOPE: override the variable only inside .promo */
    .promo {
      --btn-bg: #f5a623;          /* gold buttons only in this section */
      border: 2px dashed var(--brand);
    }

    /* 5. RESPONSIVE: change the token in a media query, all spacing adapts */
    @media (min-width: 768px) {
      :root { --space: 24px; }
    }
  </style>
</head>
<body>
  <h1>CSS Variables</h1>

  <div class="card">
    <h3>Normal card</h3>
    <p>Button uses --brand.</p>
    <button class="btn">Order Now</button>
  </div>

  <div class="card promo">
    <h3>Promo card</h3>
    <p>--btn-bg overridden locally to gold.</p>
    <button class="btn">Claim Offer</button>
  </div>

  <!-- 6. Toggle theme by flipping one attribute -->
  <button class="btn" id="toggle">Toggle Dark Mode</button>

  <script>
    // Flip data-theme on <html>: all variables swap instantly
    const root = document.documentElement;
    document.getElementById('toggle').addEventListener('click', () => {
      const next = root.dataset.theme === 'dark' ? 'light' : 'dark';
      root.dataset.theme = next;
    });

    // Change a single variable at runtime from JS
    root.style.setProperty('--radius', '16px');
  </script>
</body>
</html>
```

```css
/* Bonus: @property registers a typed variable so it can be animated.
   Support: Chrome 85+, Safari 16.4+, Firefox 128+. Check before relying on it. */
@property --angle {
  syntax: '<angle>';
  inherits: false;
  initial-value: 0deg;
}
.spinner-ring {
  background: conic-gradient(from var(--angle), #ff5a5f, #fff);
  animation: spin 2s linear infinite;
}
@keyframes spin { to { --angle: 360deg; } }
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. Global tokens in globals.css (Next.js app/globals.css)
/*
:root { --brand: #ff5a5f; --bg: #fff; }
.dark { --bg: #121212; }
*/

// 2. Dynamic value from props: pass it as a CSS variable via style
//    (the CSS file stays static, only the variable changes)
function ProgressBar({ percent, color }) {
  return (
    <div
      className="bar"
      // TypeScript needs a cast for custom properties: as React.CSSProperties
      style={{ '--percent': `${percent}%`, '--bar-color': color }}
    />
  );
}
/* .bar { width: var(--percent); background: var(--bar-color); } */

// 3. Theme toggle with next-themes (adds class="dark" on <html>)
import { useTheme } from 'next-themes';
function ThemeButton() {
  const { theme, setTheme } = useTheme();
  return <button onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}>Toggle</button>;
}

// 4. Tailwind: arbitrary values read variables directly
<div className="bg-[var(--brand)] p-[var(--space)]">Card</div>
// Tailwind v3 theme can map colours to variables:
// colors: { brand: 'var(--brand)' }  -> className="bg-brand"
// shadcn/ui uses exactly this pattern for light/dark themes.
```

---

## ⚫ Interview Questions + Answers

**Q1: What are CSS Custom Properties and how do you declare and use them?**
A1: They are author-defined properties whose names start with `--`. Declare with `--name: value;` (usually in `:root`) and read with `var(--name, fallback)`. They participate in the cascade and inherit, so child elements can read and override them.

**Q2: How are CSS variables different from Sass/Less variables?**
A2: Sass variables are compile-time: they are replaced by plain values before the browser sees the CSS, so they cannot change at runtime and have no knowledge of the DOM. CSS variables are runtime: they follow the cascade and inheritance, can be scoped to an element, changed by JS (`setProperty`), and changed inside media queries. Sass can still do things CSS cannot (loops, functions), so they are often used together.

**Q3: Why declare variables on `:root`? What is the scope of a custom property?**
A3: `:root` matches `<html>`, so every element inherits the variable (global scope). Scope is lexical in the DOM: a variable declared on `.card` is only visible to `.card` and its descendants. A closer declaration wins, so you can override a global token locally (like `.promo { --btn-bg: gold }`).

**Q4: How do you implement dark mode with CSS variables?**
A4: Define colour tokens in `:root` for light theme, override the same names inside `[data-theme="dark"]` (or `@media (prefers-color-scheme: dark)`), and write components using only `var(--bg)`, `var(--text)`. Toggle the attribute with JS and save the choice in localStorage. No component needs a dark-specific rule.

**Q5: Can you use `var()` in media queries? What happens with invalid values or missing variables?**
A5: No. `@media (min-width: var(--bp))` does not work because variables are resolved on elements, not in the at-rule condition. For a missing variable, the fallback is used if given (`var(--x, 10px)`). If there is no fallback, or the value is invalid for that property, the declaration becomes "invalid at computed-value time", and the property falls back to `inherit` or `initial` depending on whether it inherits naturally.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Expecting `var()` to work inside media query conditions
```css
/* WRONG: does nothing */
@media (min-width: var(--tablet)) { .box { display: grid; } }

/* CORRECT: write the real number; use variables inside the rules instead */
@media (min-width: 768px) { :root { --cols: 3; } }
```

❌ **Mistake 2:** No fallback, and a typo in the name
```css
/* WRONG: --brnad is a typo, background silently becomes transparent */
.btn { background: var(--brnad); }

/* CORRECT: add a fallback so mistakes are visible and safe */
.btn { background: var(--brand, #ff5a5f); }
```

❌ **Mistake 3:** Making every value a variable (over-tokenizing)
```css
/* WRONG: --margin-top-of-footer-link-in-sidebar */
/* CORRECT: only tokenize shared design decisions: colours, spacing scale, radius, font sizes */
```

❌ **Mistake 4:** Putting a unit-less number in a variable and forgetting the unit
```css
/* WRONG */
:root { --gap: 16; }  .box { padding: var(--gap); }   /* invalid, no unit */

/* CORRECT */
:root { --gap: 16px; }  /* or: padding: calc(var(--gap) * 1px) if you need a bare number */
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Custom Property | Variable name starting with `--` | अपना बनाया हुआ CSS variable |
| `var()` | Function that reads a custom property | Variable की value पढ़ने का function |
| Fallback | Second argument to `var()` used if missing | Variable न मिले तो backup value |
| `:root` | Matches `<html>`, global scope | पूरी page का global scope |
| Scope | Where a variable is visible (element + children) | Variable कहाँ तक दिखता है |
| Design token | Named value for colour/spacing/etc. | Design की named value |
| `setProperty` | JS method to change a variable at runtime | JS से variable बदलना |
| `@property` | Register typed, animatable variable | Typed variable register करना |

---

## ⚡ 3-Line Summary
**English:**
1. Custom properties are declared as `--name: value` and read with `var(--name, fallback)`; they inherit and can be scoped to any element.
2. Unlike Sass variables they are live in the browser, so JS, media queries, and theme classes can change them at runtime.
3. Best use: design tokens (colours, spacing, radius) and theming such as dark mode; they cannot be used inside media query conditions.

**Hindi:**
1. Custom properties `--name: value` से बनते हैं और `var(--name, fallback)` से पढ़े जाते हैं; ये inherit होते हैं और किसी भी element तक scope हो सकते हैं।
2. Sass variables से अलग ये browser में live रहते हैं, इसलिए JS, media query और theme class runtime पर बदल सकते हैं।
3. सबसे अच्छा use: design tokens (colour, spacing, radius) और dark mode; media query की condition में काम नहीं करते।

---

## ➡️ Next Topic
**78. CSS Transitions** — अब variables से values बदलना सीख लिया, अगला step है उन बदलावों को smooth बनाना (hover, theme switch) बिना JavaScript के।
