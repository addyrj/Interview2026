# 54. CSS Cascade + Inheritance
# हिंदी में: CSS Cascade + Inheritance — Rules टकराएँ तो कौन जीतता है, और Parent से क्या मिलता है

---

## 🔵 Simple Definition (English)
The **cascade** is the algorithm that picks ONE winning value when several CSS rules target the same property of the same element. **Inheritance** is when an element that has no value for a property gets it from its parent (e.g. `color`, `font-family`), instead of using the default.

## 🔵 सरल परिभाषा (Hindi)
**Cascade** वो algorithm है जो तय करता है कि जब एक ही element की एक ही property पर कई rules लगें तो कौन सा जीतेगा। **Inheritance** का मतलब: अगर element की उस property पर कोई value नहीं है तो वो parent से मिल जाती है (जैसे `color`, `font-family`)।

---

## 🔴 Problem it Solves
```
PROBLEM 1 - conflicts:
  p { color: red; }              (your stylesheet)
  p { color: blue; }             (another rule)
  .note { color: green; }        (class)
  Browser default: p { margin: 1em }
  -> Which colour does <p class="note"> get? Need ONE predictable answer.

PROBLEM 2 - repetition:
  Without inheritance you would write font-family on every <p>, <li>, <span>, <a>...
  With inheritance: body { font-family: Inter; color: #222; }  -> whole page.
```

## 🔴 यह क्यों बना? (Hindi)
```
समस्या 1 - टकराव: एक ही element पर कई rules अलग-अलग color बोलें तो browser को
ONE predictable जवाब चाहिए। Cascade यही तय करता है।

समस्या 2 - दोहराव: inheritance न होती तो हर <p>, <li>, <span>, <a> पर font-family
अलग से लिखनी पड़ती। अब body पर एक बार लिखो, पूरा page follow करता है।
```

---

## 🟢 How it Works — Step by Step

```
CASCADE DECISION ORDER (highest priority first):
  1. ORIGIN & IMPORTANCE
       !important author  >  !important user  >  !important user-agent(browser)
       >  normal author  >  normal user  >  normal browser default
       (transitions & animations sit in between, simplified)
  2. CASCADE LAYERS (@layer)    -> later layer wins (normal); reversed for !important
       (@layer: Chrome 99+, Safari 15.4+, Firefox 97+)
  3. SPECIFICITY                -> inline > #id > .class/:pseudo/[attr] > element
  4. SOURCE ORDER               -> the LAST rule written wins when all else ties

  Memory trick:  Importance -> Layer -> Specificity -> Order

EXAMPLE
  <p class="note" id="n1">Hi</p>
  p        { color: red; }      /* specificity 0,0,1 */
  .note    { color: green; }    /* 0,1,0  */
  #n1      { color: blue; }     /* 1,0,0  -> WINS */
  p        { color: black; }    /* same as first, later in file, still loses to #n1 */

INHERITANCE
  Inherited by default (text-related):
     color, font-*, line-height, letter-spacing, text-align, text-transform,
     visibility, cursor, list-style, direction, quotes
  NOT inherited by default (box-related):
     margin, padding, border, background, width, height, display, position,
     overflow, opacity, z-index, flex/grid props

  CONTROL KEYWORDS (work on any property):
     inherit  -> force take parent's value
     initial  -> reset to the spec's default value (not the browser's!)
     unset    -> inherit if property is inheritable, else initial
     revert   -> roll back to browser default stylesheet
     revert-layer -> roll back to the previous cascade layer

  Value flow:  specified -> computed -> used
     body { font-size: 16px } ; p { font-size: 1.25em }
     computed p font-size = 20px and it is the computed (20px) value children inherit,
     not the "1.25em" text.

  Typical trick:  a { color: inherit; }  (links take surrounding text colour)
                  button, input { font: inherit; } (form controls do NOT inherit font by default!)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Cascade का क्रम (ऊपर वाला ज़्यादा ताकतवर):
  1. Origin + !important   (author !important सबसे ऊपर)
  2. @layer                (बाद वाली layer जीतती है)
  3. Specificity           (inline > id > class > element)
  4. Source order          (सब बराबर हो तो फाइल में आखिर में लिखा हुआ जीतता है)

याद रखने की ट्रिक: Importance -> Layer -> Specificity -> Order

Inheritance:
  Inherit होती हैं (text वाली): color, font-family, font-size, line-height, text-align, visibility
  Inherit नहीं होतीं (box वाली): margin, padding, border, background, width, height, display

Keywords:
  inherit -> parent जैसा ले लो
  initial -> spec का default
  unset   -> inheritable है तो inherit, वरना initial
  revert  -> browser वाले default पर वापस

Note: <button> और <input> font inherit नहीं करते, इसलिए font: inherit लिखना पड़ता है।
```

---

## 🟡 Real World Example
**Amazon / Gmail theming:** the site sets `body { font-family: "Amazon Ember", Arial; color: #0f1111; }` once; every paragraph, list and link inherits it. A product title overrides only `font-size`. A promotional banner inside has `.banner { color: white }`; all its children inherit white text automatically. When a developer adds `.btn { color: red }` after a library's `.btn { color: blue }` with equal specificity, the later one wins (source order), which is why CSS file order matters.

## 🟡 Real Example Hindi mein
**Amazon / Gmail:** `body { font-family: ...; color: ... }` एक बार लिखा और हर paragraph, list, link ने वही font ले लिया। Product title सिर्फ `font-size` override करता है। Banner पर `.banner { color: white }` लगाया तो उसके अंदर के सारे children का text अपने आप white। और अगर library की `.btn { color: blue }` के बाद आप `.btn { color: red }` लिखो (same specificity) तो बाद वाला जीतता है — इसीलिए CSS files का क्रम मायने रखता है।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Cascade + Inheritance Demo</title>
  <style>
    * { box-sizing: border-box; }

    /* INHERITANCE: set once on body, everything below follows */
    body {
      font-family: system-ui, sans-serif;
      color: #1f2937;            /* inherited by all text */
      line-height: 1.5;          /* inherited (unitless ratio) */
      padding: 20px;
      border: 4px solid #6366f1; /* NOT inherited: only body gets the border */
    }

    h2 { font-size: 15px; margin: 22px 0 6px; }
    .box { padding: 10px; margin-bottom: 8px; background: #eef2ff; border-radius: 6px; }

    /* CASCADE 1: same specificity -> last wins */
    .same { color: red; }
    .same { color: green; }          /* wins (later in file) */

    /* CASCADE 2: specificity beats order */
    #strong { color: blue; }         /* 1,0,0 */
    .weak.weak { color: orange; }    /* 0,2,0 - written later but loses to id */

    /* CASCADE 3: !important beats specificity (use rarely) */
    .force { color: purple !important; }
    #force-id.force { color: black; }   /* loses to !important */

    /* INHERITANCE: parent colour flows down */
    .banner { background: #111827; color: #fff; padding: 12px; border-radius: 6px; }
    .banner a { color: inherit; }       /* link takes banner's white instead of blue */

    /* NOT inherited: child doesn't get parent's border/background */
    .parent { border: 2px dashed #ef4444; padding: 10px; background: #fee2e2; }
    .child { padding: 6px; }            /* no border, background transparent */

    /* KEYWORDS */
    .reset-demo { color: crimson; }
    .reset-demo .inh   { color: inherit; }   /* crimson */
    .reset-demo .ini   { color: initial; }   /* black (spec default for color is CanvasText/black) */
    .reset-demo .uns   { color: unset; }     /* color inheritable -> crimson */

    /* Form controls don't inherit font by default; fix: */
    button, input { font: inherit; }

    /* @layer: later layer wins regardless of specificity (modern browsers) */
    @layer base, theme;
    @layer base  { #lay { color: red; } }    /* high specificity but lower layer */
    @layer theme { p.lay { color: teal; } }  /* low specificity but later layer -> WINS */
  </style>
</head>
<body>
  <h2>1. Same specificity: later wins (green)</h2>
  <div class="box same">I am green</div>

  <h2>2. id beats extra classes (blue)</h2>
  <div class="box weak weak" id="strong">I am blue</div>

  <h2>3. !important (purple)</h2>
  <div class="box force" id="force-id">I am purple</div>

  <h2>4. Inherit from parent</h2>
  <div class="banner">Free delivery today. <a href="#">Learn more</a></div>

  <h2>5. Border/background not inherited</h2>
  <div class="parent"><div class="child">Child has no border</div></div>

  <h2>6. Keywords</h2>
  <div class="box reset-demo">
    crimson parent
    <div class="inh">inherit (crimson)</div>
    <div class="ini">initial (black)</div>
    <div class="uns">unset (crimson)</div>
  </div>

  <h2>7. Layers: teal wins over id</h2>
  <p class="lay" id="lay">Teal because theme layer is later</p>

  <h2>8. Form controls</h2>
  <input value="inherits page font" />
  <button>Same font</button>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. Inheritance in React = normal CSS inheritance through the DOM.
//    Set typography once on <body> via layout:
// app/layout.tsx
import { Inter } from "next/font/google";
const inter = Inter({ subsets: ["latin"] });
export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>   {/* every child inherits Inter */}
    </html>
  );
}

// 2. Cascade order in Next.js: CSS import order decides "last wins".
//    Global CSS first, then component CSS Modules. Same specificity -> later import wins.
import "./globals.css";
import styles from "./Card.module.css";

// 3. Tailwind v3/v4 uses @layer (base, components, utilities) so utilities win over components:
/*
  @layer components { .btn { @apply px-4 py-2 bg-blue-600; } }
  <button className="btn bg-red-500"> -> bg-red-500 wins (utilities layer is later)
*/

// 4. Theme via inheritance: set CSS variables on a wrapper, all descendants read them
<div style={{ "--brand": "#e23744" }}>   {/* Zomato red */}
  <Button />   {/* uses background: var(--brand) */}
</div>

// 5. Debug: Chrome DevTools > Styles pane shows struck-through losers,
//    "Computed" tab > filter shows final value + which rule won.
```

---

## ⚫ Interview Questions + Answers

**Q1: What is the cascade? In what order are conflicts resolved?**
A1: The cascade picks the winning declaration by: (1) origin and `!important`, (2) cascade layers, (3) specificity, (4) source order (last wins). Only if all earlier steps tie does the next one decide.

**Q2: Which CSS properties are inherited by default? Name some that aren't.**
A2: Inherited: `color`, `font-family`, `font-size`, `font-weight`, `line-height`, `text-align`, `letter-spacing`, `visibility`, `cursor`, `list-style`. Not inherited: `margin`, `padding`, `border`, `background`, `width`, `height`, `display`, `position`, `overflow`, `opacity`. Rule of thumb: text properties inherit, box/layout properties don't.

**Q3: Difference between `inherit`, `initial`, `unset`, `revert`?**
A3: `inherit` takes the parent's computed value. `initial` uses the CSS spec default (e.g. `display: inline`). `unset` = `inherit` for inherited properties, else `initial`. `revert` rolls back to the browser's default stylesheet (e.g. `div` becomes `display: block`, not `inline`).

**Q4: Why is my style not applying even though the selector looks right?**
A4: Typical causes: a higher-specificity rule wins (check DevTools for struck-through lines), a later rule overrides, `!important` elsewhere, an `@layer` ordering issue, a typo/invalid value (dropped by browser), the stylesheet loads before another one, or the property isn't inherited and you set it on the parent.

**Q5: Why don't buttons and inputs use my body font?**
A5: The browser's default stylesheet sets `font` on form controls (`font: -webkit-small-control` etc.), which beats inheritance. Fix with `button, input, select, textarea { font: inherit; }`. It's included in Tailwind's Preflight and most resets.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Escalating with `!important`
```css
/* WRONG: starts a specificity war */
.title { color: red !important; }

/* CORRECT: understand why it loses, fix selector/order/layer */
.card .title { color: red; }
```

❌ **Mistake 2:** Expecting box properties to inherit
```css
/* WRONG: children will not get a border */
.parent { border: 1px solid red; }

/* CORRECT: if you really need it */
.parent * { border: inherit; }   /* or style the child directly */
```

❌ **Mistake 3:** Relying on source order across files unknowingly
```css
/* WRONG: in a.css .btn{color:red}, in b.css .btn{color:blue}; import order changes the result */

/* CORRECT: use unique classes (CSS Modules), or @layer to make order explicit */
@layer reset, base, components, utilities;
```

❌ **Mistake 4:** Forgetting form controls don't inherit font
```css
/* WRONG: input looks different from rest of page */
body { font-family: Inter; }

/* CORRECT */
button, input, select, textarea { font: inherit; }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Cascade | Algorithm to resolve conflicts | टकराव सुलझाने का algorithm |
| Inheritance | Child takes parent's value | Parent से value मिलना |
| Origin | Browser / user / author stylesheet | Style का स्रोत |
| Specificity | Selector weight | Selector का वज़न |
| Source order | Later rule wins on tie | बाद वाला जीतता है |
| !important | Overrides normal rules | सबसे ऊपर priority |
| @layer | Explicit cascade layers | Priority layers |
| Computed value | Resolved value children inherit | Final resolved value |

---

## ⚡ 3-Line Summary
**English:**
1. Cascade resolves conflicts: importance, then layer, then specificity, then source order (last wins).
2. Text properties (`color`, `font-*`, `line-height`) inherit; box properties (`margin`, `border`, `background`) do not.
3. Use `inherit / initial / unset / revert` to control it, and avoid `!important` wars.

**Hindi:**
1. Cascade का क्रम: importance, फिर layer, फिर specificity, फिर source order (आखिरी जीतता है)।
2. Text properties (`color`, `font-*`, `line-height`) inherit होती हैं; box properties (`margin`, `border`, `background`) नहीं।
3. `inherit / initial / unset / revert` से control करो और `!important` की लड़ाई से बचो।

---

## ➡️ Next Topic
**56. box-sizing (content-box vs border-box)** — 55 (Box Model) पहले से है, अब देखो कि width की गणना कैसे बदलती है और हर project में border-box reset क्यों ज़रूरी है।
