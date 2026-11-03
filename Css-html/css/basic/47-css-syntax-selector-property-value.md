# 47. CSS Syntax (selector, property, value)
# हिंदी में: CSS Syntax — Selector, Property और Value

---

## 🔵 Simple Definition (English)
A CSS **rule** has a **selector** (which elements) and a **declaration block** `{ }` holding one or more **declarations**, each a `property: value;` pair. Example: `h1 { color: red; }`. Besides rules, CSS has **at-rules** (`@media`, `@font-face`), **comments** (`/* */`) and **functions** (`rgb()`, `calc()`, `var()`).

## 🔵 सरल परिभाषा (Hindi)
CSS **rule** में एक **selector** (किन elements पर) और एक **declaration block** `{ }` होता है, जिसमें एक या ज़्यादा **declarations** (`property: value;` जोड़ी) होती हैं। उदाहरण: `h1 { color: red; }`। Rules के अलावा CSS में **at-rules** (`@media`, `@font-face`), **comments** (`/* */`) और **functions** (`rgb()`, `calc()`, `var()`) भी हैं।

---

## 🔴 Problem it Solves
```
PROBLEM:
  Browser needs a precise, predictable grammar to know
  WHAT to style, WHICH property to change and to WHAT value.

  A single typo silently breaks styling:
     p { colour: red }       /* unknown property: ignored */
     p { color: red          /* missing semicolon/brace: next rule breaks */
     p { width: 10 px; }     /* space inside value: invalid, ignored */

  CSS does NOT throw errors. Invalid declarations are skipped quietly,
  so bugs are hard to spot unless you know the syntax well.
```

## 🔴 यह क्यों बना? (Hindi)
```
समस्या:
  Browser को सटीक grammar चाहिए ताकि पता चले
  क्या style करना है, कौन सी property बदलनी है और किस value पर।

  एक छोटी typo चुपचाप styling तोड़ देती है:
     p { colour: red }       /* अनजान property: ignore */
     p { color: red          /* semicolon/brace छूटा: अगला rule टूटेगा */
     p { width: 10 px; }     /* value में space: invalid, ignore */

  CSS error नहीं देती। गलत declaration चुपचाप छोड़ दी जाती है,
  इसलिए syntax अच्छे से पता होना चाहिए।
```

---

## 🟢 How it Works — Step by Step

```
ANATOMY OF A RULE (rule set):

   h1, h2.title   {   color   :   red   ;   font-size : 2rem ;  }
   └────┬──────┘     └──┬──┘     └─┬─┘                        
     selector list   property    value
                     └──────┬───────┘
                       declaration  (ends with ;)
   └─────────── declaration block { } ──────────────┘

PARTS:
  Selector list   : comma-separated selectors, rule applies to any of them
  Declaration     : property : value ;
  Semicolon       : separates declarations (last one optional but recommended)
  Property        : kebab-case name (background-color, NOT backgroundColor)
  Value           : keyword (red, auto), number+unit (16px), function (rgb(0 0 0)),
                    string ("x"), url(), or a space/comma separated list
  !important      : `color: red !important;` raises priority (use sparingly)

VALUE TYPES:
  keyword      display: flex          global: inherit | initial | unset | revert
  length       margin: 10px 2rem 5%   (0 needs no unit)
  color        #ff0000  rgb(255 0 0)  hsl(0 100% 50%)  red  rgb(255 0 0 / 50%)
  number       opacity: 0.5  line-height: 1.5
  function     calc(100% - 20px)  var(--x)  min() max() clamp()  url(img.png)
  shorthand    margin: 10px 20px;  (top/bottom right/left)
               border: 1px solid #ccc;  (width style color)

AT-RULES (start with @):
  @media (min-width: 768px) { ... }    conditional rules
  @font-face { ... }                   custom fonts
  @keyframes name { ... }              animations
  @import url("x.css");                import another stylesheet (avoid; slow)
  @supports (display: grid) { ... }    feature check
  @layer base, components;             cascade layers

COMMENTS:
  /* only this style: CSS has NO // single-line comments */

CASE & WHITESPACE:
  Property names and keywords: case-insensitive (write lowercase)
  Class/id selectors and custom property names: CASE-SENSITIVE
  Whitespace and newlines are free-form (minifiers remove them)

ERROR HANDLING:
  Invalid declaration -> only that declaration is dropped
  Unknown selector in a list -> whole rule dropped (use :is() to be forgiving)
  Later valid declaration of the same property overrides earlier ones:
      width: 50vw;
      width: 50dvw;     /* browsers without dvw ignore it, keep 50vw */
```

## 🟢 कैसे काम करता है? (Hindi)

```
Rule की बनावट:
   selector { property: value; property: value; }

हिस्से:
  Selector       : किन elements पर लगे (कई हों तो comma से)
  Declaration    : property: value;
  Semicolon      : declarations को अलग करता है
  Property       : kebab-case (background-color, backgroundColor नहीं)
  Value          : keyword (auto), संख्या+unit (16px), function (rgb()), string, url()
  !important     : priority बढ़ाता है (कम use करो)

Value के प्रकार: keyword, length, color, number, function, shorthand
(margin: 10px 20px; border: 1px solid #ccc;)

At-rules (@ से शुरू): @media, @font-face, @keyframes, @supports, @layer

Comments: सिर्फ /* ... */ ; CSS में // काम नहीं करता।

Error handling: गलत declaration अकेली छोड़ी जाती है, बाकी चलती रहती हैं।
Selector list में एक selector गलत हो तो पूरा rule छूट जाता है।
Class/id नाम case-sensitive हैं, property और keywords नहीं।
```

---

## 🟡 Real World Example
**Amazon's "Add to Cart" button** is one rule: selector `.add-to-cart`, declarations `background: #ffd814; border-radius: 20px; padding: 8px 16px;`. Change the selector to `.add-to-cart:hover` and a darker `background` gives the hover state. **Instagram's** heart "like" uses `@keyframes` (an at-rule) to scale it up and down. **Zomato** loads its custom font with `@font-face` and uses `@media (max-width: 600px)` to change layout on phones.

## 🟡 Real Example Hindi mein
**Amazon का "Add to Cart" button** एक rule है: selector `.add-to-cart`, declarations `background: #ffd814; border-radius: 20px; padding: 8px 16px;`। Selector `.add-to-cart:hover` करके गहरा `background` दो तो hover state बन जाती है। **Instagram का** "like" heart `@keyframes` (एक at-rule) से बड़ा-छोटा होता है। **Zomato** अपना custom font `@font-face` से लाता है और `@media (max-width: 600px)` से phone पर layout बदलता है।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CSS Syntax Demo</title>
  <style>
    /* ═══ 1. BASIC RULE: selector { property: value; } ═══ */
    body {
      font-family: system-ui, sans-serif;   /* value list: first available font wins */
      margin: 0;
      padding: 20px;
      background: #f5f5f5;                  /* color value (hex) */
    }

    /* ═══ 2. SELECTOR LIST: one rule, many selectors ═══ */
    h1, h2, h3 {
      color: #222;
      margin: 0 0 8px;                      /* shorthand: top right bottom left = 0 0 8px 0 */
    }

    /* ═══ 3. VALUE TYPES ═══ */
    .types {
      width: 80%;                           /* percentage */
      max-width: 600px;                     /* length (px) */
      padding: 1rem 1.5rem;                 /* length (rem), two-value shorthand: vertical horizontal */
      background-color: rgb(255 255 255);   /* function value */
      border: 2px solid hsl(210 80% 50%);   /* shorthand: width style color */
      border-radius: 8px;
      line-height: 1.6;                     /* unitless number */
      margin-bottom: 20px;
    }

    /* ═══ 4. CALC() and VAR() FUNCTIONS ═══ */
    :root { --gap: 12px; }                  /* custom property (case-sensitive) */
    .gap-demo {
      display: flex;
      gap: var(--gap);
      width: calc(100% - 40px);             /* spaces around - are REQUIRED in calc */
    }
    .gap-demo div { flex: 1; background: #bbdefb; padding: 10px; text-align: center; }

    /* ═══ 5. GLOBAL KEYWORDS ═══ */
    .inherit-demo { color: seagreen; }
    .inherit-demo span { color: inherit; border: 1px dashed; }   /* take parent's colour */

    /* ═══ 6. !important (avoid; shows how it beats normal rules) ═══ */
    .warn { color: gray; }
    .warn { color: crimson !important; }

    /* ═══ 7. AT-RULES ═══ */
    @media (max-width: 500px) {             /* conditional block */
      .gap-demo { flex-direction: column; }
    }
    @keyframes pulse { from { transform: scale(1); } to { transform: scale(1.15); } }
    .heart { display: inline-block; animation: pulse .6s ease-in-out infinite alternate; }

    /* ═══ 8. ERROR HANDLING DEMO ═══ */
    .oops {
      colour: red;                          /* unknown property -> ignored */
      font-size: 10 px;                     /* invalid value (space) -> ignored */
      background: #ffe0b2;                  /* valid -> still applied */
      padding: 8px;
    }

    /* ═══ 9. COMMENTS: only the /* */ form exists ═══ */
    /* // this is NOT a comment in CSS */
  </style>
</head>
<body>
  <h1>CSS Syntax</h1>

  <div class="types">
    <h2>Rule anatomy</h2>
    <p><code>selector { property: value; }</code> - this box uses shorthand, rem, rgb(), hsl() and unitless line-height.</p>
  </div>

  <div class="gap-demo">
    <div>calc()</div><div>var()</div><div>flex gap</div>
  </div>

  <p class="inherit-demo">Parent seagreen. <span>Child uses inherit.</span></p>
  <p class="warn">!important wins here, so crimson.</p>
  <p>Like it: <span class="heart">❤</span></p>
  <p class="oops">Invalid lines were skipped, the valid background applies.</p>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. Plain CSS in .css / .module.css files: identical syntax.
/* Card.module.css */
.card {
  padding: 1rem;
  border-radius: 8px;
}

// 2. Inline style in React uses a JS OBJECT, so:
//    - properties are camelCase  (backgroundColor, not background-color)
//    - values are strings (numbers become px for most properties)
//    - no selectors, no @media, no :hover
<div style={{ backgroundColor: '#fff', padding: 16, borderRadius: 8, lineHeight: 1.6 }} />

// 3. CSS custom properties from JS:
<div style={{ '--gap': '12px' }} className="row" />

// 4. Tailwind: each class = one declaration
//    p-4 -> padding: 1rem;  rounded-lg -> border-radius: .5rem;
//    Arbitrary value: w-[calc(100%-40px)] (underscore for spaces)
<div className="w-[calc(100%-40px)] bg-[#ffd814] hover:bg-yellow-400" />

// 5. styled-components writes real CSS syntax inside template literals:
import styled from 'styled-components';
const Button = styled.button`
  background: #ffd814;     /* regular CSS syntax */
  &:hover { background: #f7ca00; }
`;

// 6. Lint/format: Prettier + Stylelint catch syntax mistakes early.
```

---

## ⚫ Interview Questions + Answers

**Q1: Explain the syntax of a CSS rule.**
A1: A rule = selector + declaration block. The selector picks elements; inside `{ }` are declarations, each `property: value;`. Example: `.btn { color: white; padding: 8px 16px; }`. Several selectors can share a rule separated by commas.

**Q2: What is the difference between a property and a value? What are shorthand properties?**
A2: The property is what to change (`margin`), the value is what to set it to (`10px`). Shorthand sets several related longhand properties at once: `margin: 10px 20px` sets all four margins; `border: 1px solid red` sets width, style and color. Omitted shorthand values reset to initial.

**Q3: What are at-rules?**
A3: Instructions beginning with `@` that are not simple style rules: `@media` (conditions), `@font-face` (fonts), `@keyframes` (animation), `@supports` (feature queries), `@import`, `@layer`, `@container`, `@charset`.

**Q4: What happens if one declaration is invalid?**
A4: The browser drops only that declaration and continues with the rest. If the selector list contains an invalid selector, the whole rule is ignored (unless using `:is()`/`:where()` which are forgiving). CSS does not throw errors, so use DevTools (struck-through/warning icon) to find issues.

**Q5: Are CSS property names and values case-sensitive? How do you write comments?**
A5: Property names and keywords are case-insensitive (convention: lowercase). Class names, IDs and custom property names (`--Main`) are case-sensitive. Comments are `/* ... */` only; `//` is not valid and can break the following rule.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Missing semicolon
```css
/* WRONG: padding gets lost / merged */
.a { color: red
     padding: 8px; }
/* CORRECT */
.a { color: red; padding: 8px; }
```

❌ **Mistake 2:** Space between number and unit
```css
/* WRONG */ .a { width: 10 px; }
/* CORRECT */ .a { width: 10px; }
```

❌ **Mistake 3:** Using JS-style names or `//` comments
```css
/* WRONG */ .a { backgroundColor: red; } // comment
/* CORRECT */ .a { background-color: red; } /* comment */
```

❌ **Mistake 4:** No spaces in calc
```css
/* WRONG */ width: calc(100%-20px);
/* CORRECT */ width: calc(100% - 20px);
```

❌ **Mistake 5:** Quoting wrongly or forgetting units
```css
/* WRONG: margin: 10; (no unit) */
/* CORRECT: margin: 10px; (only 0 may be unitless; line-height/opacity/flex take numbers) */
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Rule set | Selector + declaration block | Selector और block का पूरा rule |
| Selector | Picks target elements | Target elements चुनता है |
| Declaration | property: value; pair | property: value; जोड़ी |
| Property | What aspect to style | कौन सा गुण बदलना है |
| Value | Setting for the property | उस गुण की value |
| Shorthand | One property sets many | एक property से कई सेट |
| At-rule | Rule starting with @ | @ से शुरू होने वाला rule |
| !important | Highest priority flag | सबसे ऊँची priority का flag |
| Function | Computed value like calc() | calc() जैसी गणना वाली value |

---

## ⚡ 3-Line Summary
**English:**
1. A rule is `selector { property: value; }`; selectors can be listed with commas and declarations end with semicolons.
2. Values can be keywords, lengths, colors, numbers or functions; at-rules (`@media`, `@keyframes`) add conditions and animations; comments are `/* */`.
3. Invalid declarations are silently skipped; in React inline styles use camelCase object syntax, while Tailwind maps classes to declarations.

**Hindi:**
1. Rule का रूप `selector { property: value; }`; selectors comma से और declarations semicolon से अलग होते हैं।
2. Value keyword, length, color, number या function हो सकती है; at-rules (`@media`, `@keyframes`) शर्तें और animations देते हैं; comments `/* */` हैं।
3. गलत declarations चुपचाप छूट जाती हैं; React inline style में camelCase object syntax, Tailwind classes को declarations से जोड़ता है।

---

## ➡️ Next Topic
**48. Ways to Add CSS (inline, internal, external)** — CSS को HTML से जोड़ने के तीन तरीके और कब कौन सा use करें।
