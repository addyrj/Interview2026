# 89. CSS Pseudo-class :not()
# हिंदी में: CSS :not() — "इसे छोड़कर बाकी सब" वाला Selector

---

## 🔵 Simple Definition (English)
`:not(selector)` is a **negation pseudo-class**. It selects every element that does **not** match the selector inside the brackets. Example: `li:not(.active)` = all `li` that do not have the class `active`. Modern browsers accept a **list** inside: `:not(.a, .b)`.

## 🔵 सरल परिभाषा (Hindi)
`:not(selector)` एक **negation pseudo-class** है। ये उन सभी elements को select करता है जो bracket के अंदर वाले selector से **match नहीं करते**। जैसे `li:not(.active)` = वो सारे `li` जिन पर `active` class नहीं है। Modern browsers में अंदर **list** भी चलती है: `:not(.a, .b)`।

---

## 🔴 Problem it Solves
```
WITHOUT :not():
  .menu a        { border-bottom: 1px solid #ddd; }   /* style for ALL links */
  .menu a:last-child { border-bottom: none; }          /* then UNDO it for last one */
  /* Two rules, "set then reset" pattern. More CSS, more override fights. */

  .card          { margin-right: 16px; }
  .card:last-child { margin-right: 0; }                /* reset again */

WITH :not():
  .menu a:not(:last-child) { border-bottom: 1px solid #ddd; }
  .card:not(:last-child)   { margin-right: 16px; }
  /* One rule. Style only the elements that need it. Nothing to undo. */
```

## 🔴 यह क्यों बना? (Hindi)
पहले हम पहले सब elements पर style लगाते थे और फिर कुछ पर **reset** करते थे (`last-child { margin: 0 }`)। इससे CSS लंबा होता था और override की problem आती थी। `:not()` से हम सीधे बोलते हैं — "इन elements पर style लगाओ, उन पर नहीं।" एक rule, कोई reset नहीं।

---

## 🟢 How it Works — Step by Step

```
STEP 1: Browser takes the selector BEFORE :not()      →  li
STEP 2: For every matching element, it tests the argument inside :not()   →  .active
STEP 3: If the argument DOES match   → element is skipped
        If the argument does NOT match → element gets the styles

SYNTAX FORMS:
  p:not(.intro)                 /* p without class intro */
  input:not([type="checkbox"])  /* all inputs except checkboxes */
  li:not(:first-child)          /* every li except the first */
  a:not(.btn, .nav-link)        /* list form: NOT .btn AND NOT .nav-link */
  :not(p)                       /* every element that is not a paragraph */

SPECIFICITY (very common interview point):
  :not() itself adds ZERO specificity.
  Its ARGUMENT counts instead.

  a:not(.btn)        → (0,1,1)   = 1 class + 1 element
  a:not(#main)       → (1,0,1)   = 1 id + 1 element
  a:not(.a, #b)      → (1,0,1)   = takes the MOST specific item in the list

CHAINING (older style, works everywhere):
  li:not(.a):not(.b)             /* not .a AND not .b */
  /* Modern equivalent: li:not(.a, .b) */

BROWSER SUPPORT:
  Simple :not(.class) .............. all browsers, always
  Selector list :not(.a, .b) ....... Chrome 88+, Firefox 84+, Safari 9+ (Selectors Level 4)
  Complex :not(.a .b) .............. same era, supported in all modern browsers
```

## 🟢 कैसे काम करता है? (Hindi)
1. Browser पहले `:not()` से पहले वाला selector देखता है (जैसे `li`)।
2. हर matched element पर `:not()` के अंदर की condition check करता है।
3. अगर अंदर वाली condition **match हो गई** → element skip। **match नहीं हुई** → style लग जाती है।
4. **Specificity:** `:not()` खुद zero गिना जाता है, लेकिन उसके **अंदर वाला selector** गिना जाता है। `a:not(#main)` की specificity में id भी जुड़ती है।
5. List form `:not(.a, .b)` का मतलब है — `.a` भी नहीं और `.b` भी नहीं। पुराने browsers के लिए chain करो: `:not(.a):not(.b)`।

---

## 🟡 Real World Example
**Amazon / Flipkart filter sidebar:** Har filter row ke neeche ek divider line hoti hai, lekin last row ke neeche nahi. Developer likhta hai `.filter-row:not(:last-child) { border-bottom: 1px solid #e7e7e7; }`.
**Zomato restaurant list:** Jab ek restaurant "Closed" hota hai, uska card grey dikhta hai: `.restaurant:not(.open) { opacity: .5; filter: grayscale(1); }`.
**Gmail inbox:** Unread mails bold dikhte hain, read mails normal — `.mail-row:not(.read) { font-weight: 700; }`।
**Forms:** `input:not([type="checkbox"]):not([type="radio"])` se sirf text-type inputs ko full-width style dete hain.

## 🟡 Real Example Hindi mein
**Amazon filter sidebar:** हर filter row के नीचे divider line होती है, लेकिन आखिरी row के नीचे नहीं। Developer लिखता है `.filter-row:not(:last-child) { border-bottom: ... }`।
**Zomato:** जो restaurant "Closed" है उसका card grey दिखता है: `.restaurant:not(.open) { opacity: .5 }`।
**Gmail:** Unread mails bold होते हैं — `.mail-row:not(.read) { font-weight: 700 }`।
**Forms:** `input:not([type="checkbox"])` से सिर्फ text-type inputs को full-width किया जाता है, checkbox को नहीं।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CSS :not() Demo</title>
  <style>
    /* Modern reset so widths are predictable */
    *, *::before, *::after { box-sizing: border-box; }

    body { font-family: system-ui, sans-serif; background: #f5f5f5; padding: 20px; color: #222; }
    h2 { margin: 28px 0 10px; font-size: 16px; border-bottom: 2px solid #333; padding-bottom: 4px; }

    /* ─── 1. DIVIDERS EXCEPT LAST (filter sidebar) ───────────────── */
    .filters { background: #fff; width: 260px; border: 1px solid #ddd; border-radius: 8px; }
    .filter-row { padding: 12px 16px; }
    /* Divider on every row EXCEPT the last: no reset rule needed */
    .filter-row:not(:last-child) { border-bottom: 1px solid #e7e7e7; }

    /* ─── 2. INBOX: UNREAD ROWS ARE BOLD (Gmail style) ───────────── */
    .inbox { background: #fff; width: 320px; border-radius: 8px; overflow: hidden; }
    .mail { padding: 10px 14px; border-bottom: 1px solid #eee; }
    /* Bold only if the row does NOT have .read */
    .mail:not(.read) { font-weight: 700; background: #f2f6fc; }
    .mail.read { color: #666; }

    /* ─── 3. FORM: STYLE ALL INPUTS EXCEPT CHECKBOX/RADIO ────────── */
    form { background: #fff; width: 320px; padding: 16px; border-radius: 8px; }
    /* Chained :not() works in every browser */
    input:not([type="checkbox"]):not([type="radio"]) {
      display: block;
      width: 100%;            /* checkbox must NOT become full width */
      padding: 8px 10px;
      margin-bottom: 10px;
      border: 1px solid #bbb;
      border-radius: 6px;
    }
    label.check { display: flex; gap: 8px; align-items: center; }

    /* ─── 4. LIST FORM :not(.a, .b) ──────────────────────────────── */
    /* Every button that is NOT primary and NOT danger gets a grey style */
    .actions button:not(.primary, .danger) {
      background: #e0e0e0; color: #222;
    }
    .actions button { padding: 8px 14px; border: 0; border-radius: 6px; cursor: pointer; }
    .actions .primary { background: #1976d2; color: #fff; }
    .actions .danger  { background: #d32f2f; color: #fff; }

    /* ─── 5. HOVER FOCUS EFFECT ON SIBLINGS (cards) ──────────────── */
    .cards { display: flex; gap: 12px; }
    .card { width: 90px; height: 70px; background: #ff9800; border-radius: 8px;
            display: grid; place-items: center; color: #fff; transition: opacity .2s; }
    /* When the container is hovered, fade every card that is NOT hovered */
    .cards:hover .card:not(:hover) { opacity: .4; }

    /* ─── 6. SAFE LINK STYLE: external links only ────────────────── */
    /* Add an arrow to links that start with http (external) but not our own domain */
    a[href^="http"]:not([href*="example.com"])::after { content: " ↗"; font-size: 12px; }
  </style>
</head>
<body>
  <h1>CSS :not()</h1>

  <h2>1. Divider on all rows except the last</h2>
  <div class="filters">
    <div class="filter-row">Brand</div>
    <div class="filter-row">Price</div>
    <div class="filter-row">Rating</div>
  </div>

  <h2>2. Unread (no .read) = bold</h2>
  <div class="inbox">
    <div class="mail">Swiggy: Your order is on the way</div>
    <div class="mail read">Amazon: Delivered yesterday</div>
    <div class="mail">Zomato: 50% off today</div>
    <div class="mail read">Gmail Team: Welcome</div>
  </div>

  <h2>3. Inputs except checkbox/radio</h2>
  <form>
    <input type="text" placeholder="Name">
    <input type="email" placeholder="Email">
    <label class="check"><input type="checkbox"> Remember me</label>
  </form>

  <h2>4. :not(.primary, .danger) list form</h2>
  <div class="actions">
    <button>Cancel</button>
    <button class="primary">Save</button>
    <button class="danger">Delete</button>
    <button>Reset</button>
  </div>

  <h2>5. Fade siblings on hover</h2>
  <div class="cards">
    <div class="card">A</div>
    <div class="card">B</div>
    <div class="card">C</div>
  </div>

  <h2>6. External link icon</h2>
  <p>
    <a href="https://example.com/about">Own site</a> |
    <a href="https://github.com">External</a>
  </p>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. In CSS Modules / globals.css, :not() works exactly like plain CSS:
/* Card.module.css */
.item:not(:last-child) { border-bottom: 1px solid var(--border); }
/* Note: with CSS Modules, class names inside :not() are also hashed — that is fine. */

// 2. Tailwind: use the "not-" variant (Tailwind v4) or arbitrary variants (v3)
// Tailwind v4:   not-last:border-b       → :not(:last-child) equivalent via not-last
// Tailwind v3:   [&:not(:last-child)]:border-b
<ul>
  {items.map((it) => (
    <li key={it.id} className="py-3 [&:not(:last-child)]:border-b border-gray-200">
      {it.name}
    </li>
  ))}
</ul>

// 3. Tailwind also has "first:" "last:" "odd:" — but :not() lets you invert.
//    Group-based dimming (hover a card, dim the others):
<div className="group flex gap-3">
  {cards.map((c) => (
    <div key={c.id}
      className="transition-opacity group-hover:[&:not(:hover)]:opacity-40">
      {c.title}
    </div>
  ))}
</div>

// 4. Prefer a CLASS from React state over :not() when logic is complex:
<Mail className={mail.read ? 'read' : ''} />   // .mail:not(.read) { font-weight: 700 }
```

---

## ⚫ Interview Questions + Answers

**Q1: What does `:not()` do?**
A1: It is the negation pseudo-class. It matches elements that do **not** match the selector passed inside. `p:not(.intro)` selects all paragraphs without the class `intro`. It removes the need for "style everything, then reset the exception" patterns.

**Q2: What is the specificity of `:not()`?**
A2: `:not()` itself adds nothing. The specificity equals the **most specific argument** inside. `a:not(.btn)` = (0,1,1). `a:not(#nav)` = (1,0,1). In `:not(.a, #b)` the whole thing counts as the id (1,0,0) even for elements that only fail `.a`. Interviewers like this because `:not(#x)` can accidentally make a rule very strong.

**Q3: Can you put multiple selectors inside `:not()`?**
A3: Yes in modern browsers (Selectors Level 4): `:not(.a, .b)` means "not `.a` and not `.b`". It is supported in all current browsers. For very old browsers, chain: `:not(.a):not(.b)`. Do not confuse with `:is(.a, .b)` which is the opposite (matches either). Note: `:not(.a, .b)` is **AND of negations**, not "not (a and b)".

**Q4: How would you remove the border from only the last item without a reset rule?**
A4: `.item:not(:last-child) { border-bottom: 1px solid #ddd; }`. Only items that are not last get the border, so there is nothing to override. Alternative today is `gap` in flex/grid for spacing, but for borders `:not(:last-child)` is the standard answer.

**Q5: Can `:not()` be nested or used with pseudo-elements?**
A5: Nesting `:not(:not(.a))` is allowed in modern browsers (double negation = `.a`). But you cannot put a **pseudo-element** inside `:not()` — `:not(::before)` is invalid. You can, however, put pseudo-classes inside (`:not(:hover)`, `:not(:disabled)`), and you can attach a pseudo-element after: `a:not(.btn)::after`.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Forgetting that `:not(#id)` raises specificity
```css
/* WRONG: this rule suddenly beats almost everything */
button:not(#special) { background: grey; }   /* specificity (1,0,1) */
.btn-primary { background: blue; }           /* (0,1,0) loses! */

/* CORRECT: use a class inside :not() */
button:not(.special) { background: grey; }   /* (0,1,1) */
```

❌ **Mistake 2:** Confusing `:not(.a, .b)` with "not both"
```css
/* WRONG assumption: "skips only elements that have BOTH .a and .b" */
li:not(.a, .b) { color: red; }

/* REALITY: skips elements that have .a OR .b (either one). */
/* To skip only those having both: */
li:not(.a.b) { color: red; }
```

❌ **Mistake 3:** Using `:not()` on huge sets with long selectors
```css
/* WRONG: broad, expensive, hard to read */
:not(div):not(span):not(p) { margin: 0; }

/* CORRECT: be specific about the parent/target */
.content > :not(h2, h3) { margin-block: .5rem; }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Negation | Matches things that do NOT match | "इसके अलावा" वाला match |
| :not(.x) | Select elements without class x | class x वाले को छोड़कर |
| Selector list | Comma separated selectors inside | कई selectors की list |
| Specificity | Weight of the selector | Selector का वज़न |
| :is() | Opposite idea: matches any in list | इनमें से कोई भी |
| :where() | Like :is() but zero specificity | :is() जैसा, specificity 0 |
| Chaining | :not(.a):not(.b) | एक के बाद एक :not |
| Selectors Level 4 | Spec that allows lists in :not() | नया selector standard |

---

## ⚡ 3-Line Summary
**English:**
1. `:not(x)` selects every element that does not match `x`, so you can style exceptions directly without reset rules.
2. `:not()` adds no specificity itself; its most specific argument is what counts (`:not(#id)` is strong).
3. Lists `:not(.a, .b)` work in modern browsers and mean "not a AND not b"; pseudo-elements are not allowed inside.

**Hindi:**
1. `:not(x)` उन सब elements को select करता है जो `x` नहीं हैं — reset rules की ज़रूरत नहीं।
2. `:not()` खुद specificity नहीं जोड़ता; अंदर का सबसे strong selector गिना जाता है।
3. `:not(.a, .b)` modern browsers में चलता है — मतलब "न a, न b"; अंदर pseudo-element नहीं चलता।

---

## ➡️ Next Topic
**90. CSS Attribute Selectors** — `[type="email"]`, `[href^="https"]`, `[class*="btn"]` — attributes के आधार पर elements select करना, जो `:not()` के साथ बहुत powerful combo बनता है।
