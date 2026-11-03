# 51. Pseudo-classes (:hover, :focus, :nth-child, :first-child)
# हिंदी में: Pseudo-classes — Element की State या Position के आधार पर Style

---

## 🔵 Simple Definition (English)
A **pseudo-class** (single colon `:`) selects an element when it is in a certain **state** (`:hover`, `:focus`, `:checked`) or at a certain **position** (`:first-child`, `:nth-child(2n)`), without adding any class in HTML.

## 🔵 सरल परिभाषा (Hindi)
**Pseudo-class** (एक colon `:`) किसी element को तब select करता है जब वो किसी **state** में हो (`:hover`, `:focus`, `:checked`) या किसी **position** पर हो (`:first-child`, `:nth-child(2n)`) — HTML में class जोड़े बिना।

---

## 🔴 Problem it Solves
```
BEFORE: to highlight a hovered row, or zebra-stripe a table, you needed JavaScript:
  row.addEventListener('mouseover', () => row.classList.add('hover'));
  rows.forEach((r, i) => { if (i % 2) r.classList.add('odd'); });

NOW (pure CSS):
  tr:hover { background: #eee; }
  tr:nth-child(odd) { background: #f9f9f9; }
  input:focus { outline: 2px solid blue; }

No JS, faster, works even before JS loads, and accessible (keyboard :focus-visible).
```

## 🔴 यह क्यों बना? (Hindi)
```
पहले hover, focus, या हर दूसरी row को रंग देने के लिए JavaScript लिखनी पड़ती थी।
अब सीधे CSS:
  tr:hover { ... }          <- mouse ऊपर आने पर
  tr:nth-child(odd) { ... } <- 1, 3, 5... वाली rows
  input:focus { ... }       <- user ने input चुना

JS नहीं चाहिए, page तेज़ रहता है, और keyboard users के लिए भी काम करता है।
```

---

## 🟢 How it Works — Step by Step

```
SYNTAX:   selector:pseudo-class { ... }       e.g.  a:hover { color: red; }

USER-ACTION STATES
  :hover          mouse is over element
  :focus          element has keyboard/click focus (inputs, links, buttons)
  :focus-visible  focus shown only when keyboard-like (best for outlines)
  :active         while being pressed
  :disabled / :checked / :required / :invalid   form states

LINK STATES — order matters: LVHA
  a:link  a:visited  a:hover  a:active     (Love-Hate: LoVe HAte)
  (:hover must come AFTER :link/:visited, :active AFTER :hover, else overridden)

STRUCTURAL (position among siblings)
  :first-child      first child of its parent
  :last-child       last child
  :nth-child(n)     formula based
      :nth-child(3)       -> 3rd child
      :nth-child(odd)     -> 1,3,5...       (even -> 2,4,6...)
      :nth-child(3n)      -> 3,6,9...
      :nth-child(3n+1)    -> 1,4,7...
      :nth-child(-n+3)    -> first 3 only
  :nth-of-type(n)   counts only same TAG siblings
  :only-child, :empty, :not(...)

SPECIFICITY: a pseudo-class counts like a class (0,1,0).
  a:hover = 0,1,1

HOVER ON TOUCH: phones have no true hover. Wrap with
  @media (hover: hover) { .btn:hover { ... } }
```

## 🟢 कैसे काम करता है? (Hindi)
```
Syntax: selector:pseudo-class { ... }

State वाले:
  :hover   -> mouse ऊपर है
  :focus   -> element select/focus हुआ (Tab दबाने पर भी)
  :active  -> दबाते समय
  :checked -> checkbox/radio ticked
  :disabled, :invalid, :required -> form states

Position वाले:
  :first-child / :last-child -> पहला / आखिरी बच्चा
  :nth-child(odd) -> 1, 3, 5...
  :nth-child(3n) -> हर तीसरा
  :nth-child(-n+3) -> सिर्फ पहले 3

Link order याद रखो LVHA: link, visited, hover, active — इसी क्रम में लिखो।
Specificity: pseudo-class = class जितनी (10)।
Mobile पर hover नहीं होता, इसलिए @media (hover: hover) में hover styles रखो।
```

---

## 🟡 Real World Example
**Instagram / Gmail:** in Gmail the inbox row highlights on `:hover` and shows the delete/archive icons; the compose box gets a blue outline on `:focus-within`. In Swiggy's restaurant list the third card of every row might get different spacing using `:nth-child(3n)`. Every table in a dashboard uses `tr:nth-child(even)` for zebra rows and `td:first-child` for a sticky label column. All without a single line of JS.

## 🟡 Real Example Hindi mein
**Instagram / Gmail:** Gmail में inbox की row पर mouse लाने पर (`:hover`) highlight होती है और delete/archive icons दिखते हैं; compose box पर click करने पर (`:focus-within`) नीला outline आता है। Swiggy की list में हर तीसरे card का margin अलग रखने के लिए `:nth-child(3n)` use होता है। Dashboard tables में `tr:nth-child(even)` से zebra rows बनती हैं। ये सब बिना JS के।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Pseudo-classes Demo</title>
  <style>
    * { box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; padding: 20px; background: #f3f4f6; }
    h2 { margin: 24px 0 8px; font-size: 16px; }

    /* ── 1. :hover, :active on button ── */
    .btn {
      background: #2563eb; color: #fff; border: 0;
      padding: 10px 18px; border-radius: 6px; cursor: pointer;
      transition: background .2s;           /* smooth colour change */
    }
    .btn:hover { background: #1d4ed8; }      /* mouse over */
    .btn:active { transform: scale(.97); }   /* while pressed */
    .btn:focus-visible { outline: 3px solid #f59e0b; outline-offset: 2px; } /* keyboard users */

    /* ── 2. :focus on input, :focus-within on wrapper ── */
    .field { display: inline-block; padding: 6px; border: 2px solid #d1d5db; border-radius: 6px; background: #fff; }
    .field input { border: 0; outline: none; font-size: 15px; }
    .field:focus-within { border-color: #2563eb; }   /* wrapper reacts when input inside is focused */

    /* ── 3. :checked on checkbox ── */
    input[type="checkbox"]:checked + label { text-decoration: line-through; color: #9ca3af; }

    /* ── 4. Structural: zebra rows + first/last ── */
    table { border-collapse: collapse; background: #fff; width: 100%; max-width: 420px; }
    td, th { padding: 8px 12px; text-align: left; }
    tbody tr:nth-child(even) { background: #f9fafb; }      /* every even row */
    tbody tr:hover { background: #dbeafe; }                /* hover highlight */
    td:first-child { font-weight: bold; }                  /* first cell of each row */
    tbody tr:last-child td { border-bottom: 2px solid #111; } /* last row line */

    /* ── 5. nth-child formulas on a grid of boxes ── */
    .boxes { display: flex; gap: 6px; flex-wrap: wrap; max-width: 420px; }
    .boxes span { width: 40px; height: 40px; background: #cbd5e1; display: grid; place-items: center; }
    .boxes span:nth-child(3n) { background: #fca5a5; }        /* 3, 6, 9, 12 */
    .boxes span:nth-child(-n+2) { background: #86efac; }      /* first two */
    .boxes span:first-child { border-radius: 50%; }           /* first one round */

    /* ── 6. :not() and :disabled ── */
    .list li:not(:last-child) { border-bottom: 1px solid #e5e7eb; }
    button:disabled { opacity: .5; cursor: not-allowed; }

    /* ── 7. Hover only on devices that really hover ── */
    @media (hover: hover) { .card-hover:hover { box-shadow: 0 6px 16px rgba(0,0,0,.15); } }
    .card-hover { background: #fff; padding: 12px; border-radius: 8px; max-width: 200px; }
  </style>
</head>
<body>
  <h2>1. Button states (try Tab key too)</h2>
  <button class="btn">Order Now</button>
  <button class="btn" disabled>Disabled</button>

  <h2>2. Input focus</h2>
  <div class="field"><input type="text" placeholder="Search..."></div>

  <h2>3. Checked</h2>
  <input type="checkbox" id="t1"><label for="t1">Buy milk</label>

  <h2>4. Table</h2>
  <table>
    <thead><tr><th>Name</th><th>Qty</th></tr></thead>
    <tbody>
      <tr><td>Apple</td><td>3</td></tr>
      <tr><td>Banana</td><td>12</td></tr>
      <tr><td>Mango</td><td>6</td></tr>
      <tr><td>Grapes</td><td>1</td></tr>
    </tbody>
  </table>

  <h2>5. nth-child</h2>
  <div class="boxes">
    <span>1</span><span>2</span><span>3</span><span>4</span><span>5</span><span>6</span><span>7</span><span>8</span><span>9</span>
  </div>

  <h2>6. :not(:last-child)</h2>
  <ul class="list"><li>One</li><li>Two</li><li>Three</li></ul>

  <h2>7. Hover-only-on-hover devices</h2>
  <div class="card-hover">Hover me</div>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. Pseudo-classes work normally in CSS / CSS Modules
// Button.module.css:  .btn:hover { background: #1d4ed8; }

// 2. Tailwind: state variants prefix the utility
<button className="bg-blue-600 hover:bg-blue-700 focus-visible:ring-2 active:scale-95 disabled:opacity-50">
  Order Now
</button>

// 3. Structural variants in Tailwind
<ul>
  <li className="first:pt-0 last:pb-0 odd:bg-gray-50 even:bg-white">Row</li>
</ul>

// 4. group-hover: parent hover affects child (like .card:hover .icon)
<div className="group">
  <span className="opacity-0 group-hover:opacity-100">Delete</span>
</div>

// 5. React has NO :hover prop on inline styles.
//    style={{ ':hover': {...} }} does NOT work.
//    Use CSS classes, CSS Modules, Tailwind, or styled-components (&:hover).
// styled-components / emotion:
//   const Btn = styled.button`  &:hover { background: red; }  `;

// 6. JS state (useState) is for logic; use :hover/:focus when it is purely visual.
```

---

## ⚫ Interview Questions + Answers

**Q1: Difference between pseudo-class and pseudo-element?**
A1: A pseudo-class (`:hover`, one colon) selects an existing element in a state or position. A pseudo-element (`::before`, two colons) styles a part of an element or creates a virtual one. See topic 52.

**Q2: Difference between `:focus`, `:focus-visible` and `:focus-within`?**
A2: `:focus` matches whenever the element is focused (including mouse click). `:focus-visible` matches only when the browser decides focus indicator should show (usually keyboard), so mouse clicks on buttons don't show an ugly ring. `:focus-within` matches a parent when any descendant has focus (good for search bars/forms).

**Q3: What does `:nth-child(2n+1)` mean? Difference from `:nth-of-type`?**
A3: `2n+1` goes n=0,1,2... giving 1,3,5: the odd children. `:nth-child` counts all siblings regardless of tag, and the element must also match the selector. `:nth-of-type` counts only siblings with the same tag. In `<h2><p><p>`, `p:nth-child(2)` matches the first p (it is 2nd child), `p:nth-of-type(2)` matches the second p.

**Q4: Why does `a:hover` sometimes not work? (LVHA)**
A4: Because of ordering/specificity. If `a:hover` is written before `a:visited`, the visited rule (same specificity) comes later and wins. Write in order: `:link`, `:visited`, `:hover`, `:active`.

**Q5: How do you handle hover on touch devices?**
A5: Touch screens have no real hover; the style may "stick" after a tap. Wrap hover styles in `@media (hover: hover) and (pointer: fine) { ... }` and never hide essential info behind hover only. Use `:focus-visible` / `:active` for feedback.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Removing the focus outline
```css
/* WRONG: keyboard users can't see where they are */
button:focus { outline: none; }

/* CORRECT: replace it with a visible style */
button:focus-visible { outline: 3px solid #f59e0b; outline-offset: 2px; }
```

❌ **Mistake 2:** Wrong link state order
```css
/* WRONG: hover never shows for visited links */
a:hover { color: red; }
a:visited { color: purple; }

/* CORRECT: LVHA */
a:link { color: blue; }
a:visited { color: purple; }
a:hover { color: red; }
a:active { color: orange; }
```

❌ **Mistake 3:** Using `:nth-child` expecting same-tag counting
```css
/* WRONG: heading counts as child 1, so this skips */
p:nth-child(1) { color: red; }    /* nothing if first child is h2 */

/* CORRECT */
p:first-of-type { color: red; }
```

❌ **Mistake 4:** Putting inline `:hover` in React style prop
```jsx
/* WRONG */ <div style={{ ":hover": { color: "red" } }} />
/* CORRECT */ <div className="hover:text-red-500" />
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Pseudo-class | `:state` selector | State/position वाला selector |
| :hover | Mouse over | Mouse ऊपर |
| :focus / :focus-visible | Element focused | Focus हुआ element |
| :focus-within | Parent of focused element | अंदर focus होने पर parent |
| :nth-child(an+b) | Formula position | Formula से position |
| :first-child / :last-child | First / last sibling | पहला / आखिरी बच्चा |
| :not() | Exclude matches | Exclude करना |
| LVHA | Link, Visited, Hover, Active order | Link states का क्रम |

---

## ⚡ 3-Line Summary
**English:**
1. Pseudo-classes (`:hover`, `:focus`, `:checked`, `:nth-child`) style elements by state or position, no JS needed.
2. Keep link order LVHA, use `:focus-visible` for accessible outlines, and guard hover with `@media (hover: hover)`.
3. In React use CSS/Tailwind variants (`hover:`, `focus:`, `first:`), not inline style.

**Hindi:**
1. Pseudo-classes state या position के हिसाब से style देते हैं, JS की ज़रूरत नहीं।
2. Link order LVHA रखो, outline के लिए `:focus-visible` और hover के लिए `@media (hover: hover)` use करो।
3. React में inline style नहीं, CSS/Tailwind variants (`hover:`, `focus:`) use करो।

---

## ➡️ Next Topic
**52. Pseudo-elements** — `::before`, `::after`, `::placeholder` — element के हिस्सों को style करना या extra content बनाना।
