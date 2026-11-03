# 64. CSS Visibility vs Display None
# हिंदी में: Visibility बनाम Display None — Element छुपाने के तरीके

---

## 🔵 Simple Definition (English)
`display: none` removes the element from the page completely (no space is kept). `visibility: hidden` only makes it invisible but its empty space stays. `opacity: 0` also keeps the space and it stays clickable. All three hide an element visually but behave very differently for layout, clicks and accessibility.

## 🔵 सरल परिभाषा (Hindi)
`display: none` element को page से पूरी तरह हटा देता है (जगह भी नहीं बचती)। `visibility: hidden` सिर्फ दिखना बंद करता है, खाली जगह बनी रहती है। `opacity: 0` में भी जगह रहती है और element click भी हो सकता है। तीनों element को छुपाते हैं पर layout, click और accessibility में अलग व्यवहार करते हैं।

---

## 🔴 Problem it Solves
```
PROBLEM: "Mujhe element chhupana hai" -- but which way?

  Case 1: Dropdown menu closed hai. Page ka layout uske liye jagah na rakhe.
          -> display: none

  Case 2: Form ke error text ko hide karna hai, par form ki height
          jump nahi honi chahiye jab error aaye.
          -> visibility: hidden  (space reserved)

  Case 3: Fade-in / fade-out animation chahiye.
          -> opacity (+ visibility) because display:none cannot animate smoothly.

Wrong choice = layout jump, invisible-but-clickable buttons, ya screen reader
ko galat content.
```

## 🔴 यह क्यों बना? (Hindi)
सिर्फ "छुपाना" काफ़ी नहीं है। कभी जगह बचानी होती है (layout jump न हो), कभी जगह हटानी होती है, कभी animation चाहिए। अगर गलत तरीका चुना तो error message आते ही form नीचे कूदता है, या अदृश्य button पर click हो जाता है। इसलिए CSS ने अलग-अलग तरीके दिए हैं।

---

## 🟢 How it Works — Step by Step

```
COMPARISON TABLE:
┌─────────────────────┬──────────────┬───────────────────┬──────────────────┐
│                     │ display:none │ visibility:hidden │ opacity: 0       │
├─────────────────────┼──────────────┼───────────────────┼──────────────────┤
│ Visible?            │ No           │ No                │ No               │
│ Takes space?        │ NO           │ YES               │ YES              │
│ Clickable/hover?    │ No           │ No                │ YES (!)          │
│ Keyboard focusable? │ No           │ No                │ YES (!)          │
│ Screen reader reads │ No           │ No                │ YES (still read) │
│ Animatable?         │ No (classic) │ Yes (discrete,    │ YES, smoothly    │
│                     │              │ flips at an end)  │                  │
│ Triggers reflow?    │ YES (heavy)  │ Repaint only      │ Composite only   │
│ Children can show?  │ No           │ YES: child with   │ No (inherits     │
│                     │              │ visibility:visible│ whole subtree)   │
└─────────────────────┴──────────────┴───────────────────┴──────────────────┘

STEPS inside the browser:
1. display:none  -> element not in render tree. Layout recalculated (reflow).
2. visibility:hidden -> box exists in layout, but paint step skips it.
3. opacity:0 -> box exists and is painted at 0 alpha. Events still hit it.

FADE-OUT PATTERN (best of both):
  .tooltip { opacity: 0; visibility: hidden; transition: opacity .2s, visibility .2s; }
  .tooltip.show { opacity: 1; visibility: visible; }
  -> fades smoothly AND is not clickable/focusable while hidden.

Other related ways:
  hidden attribute (HTML)  -> UA CSS gives display:none
  position:absolute; left:-9999px / sr-only -> hidden visually, still read by screen readers
  aria-hidden="true"       -> still visible, but hidden from screen readers
```

## 🟢 कैसे काम करता है? (Hindi)
1. `display: none`: element render tree से बाहर। Layout दोबारा calculate होता है (reflow, भारी)।
2. `visibility: hidden`: box layout में रहता है, बस paint नहीं होता। जगह खाली दिखती है।
3. `opacity: 0`: box पूरी तरह मौजूद है और 0 transparency से paint होता है। Click और focus अब भी काम करते हैं।
4. Fade animation के लिए `opacity` + `visibility` साथ में लगाओ: opacity smooth fade देती है और visibility hidden होने पर click/focus रोकती है।
5. Screen reader के लिए: `display:none` और `visibility:hidden` दोनों से content नहीं पढ़ा जाता, पर `opacity:0` वाला पढ़ा जाता है।
6. Child trick: parent `visibility: hidden` हो तो भी child `visibility: visible` लिखकर दिख सकता है। `display: none` में ऐसा नहीं होता।

---

## 🟡 Real World Example
**Instagram** profile page: the "Following" button area keeps its space even when a label is hidden so the header does not jump (visibility). **Swiggy** cart drawer: when closed it is `display: none` (or `visibility: hidden` with a slide animation) so keyboard users cannot tab into invisible buttons. **Amazon's** mega-menu: appears with fade (opacity + visibility) when you hover "All". **Gmail** hides the left sidebar labels with `display: none` on small screens to free up space.

## 🟡 Real Example Hindi mein
**Instagram** में form के validation message की जगह पहले से reserve रहती है (`visibility: hidden`) ताकि error आने पर page नीचे न कूदे। **Swiggy** का cart drawer बंद होने पर `visibility: hidden` या `display: none` होता है ताकि keyboard user अदृश्य buttons पर Tab न करे। **Amazon** का mega-menu hover पर fade होकर आता है (opacity + visibility)। **Gmail** छोटी screen पर sidebar को `display: none` करके जगह बचाता है।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Visibility vs Display None</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; padding: 20px; background: #fafafa; }
    h2 { font-size: 16px; margin: 24px 0 8px; }

    /* Row where we can SEE the space each hiding method keeps */
    .row {
      display: flex;
      gap: 0;
      border: 2px dashed #90a4ae;   /* dashed border shows the container */
      background: #fff;
    }
    .row button, .row .box {
      padding: 14px 18px;
      border: 1px solid #1976d2;
      background: #e3f2fd;
      cursor: pointer;
    }

    /* The three hiding techniques, applied to the MIDDLE box */
    .hide-none .middle       { display: none; }        /* no space */
    .hide-visibility .middle { visibility: hidden; }   /* space kept, not clickable */
    .hide-opacity .middle    { opacity: 0; }           /* space kept, STILL clickable */

    /* Child can override visibility (not possible with display:none) */
    .parent-hidden { visibility: hidden; padding: 10px; background: #ffe0b2; }
    .parent-hidden .peek { visibility: visible; background: #c8e6c9; padding: 6px; }

    /* Smooth fade pattern: opacity + visibility together */
    .tooltip-wrap { position: relative; display: inline-block; margin-top: 10px; }
    .tooltip {
      position: absolute;
      top: 110%;
      left: 0;
      white-space: nowrap;
      background: #263238;
      color: #fff;
      padding: 6px 10px;
      border-radius: 4px;
      opacity: 0;                  /* invisible, can fade */
      visibility: hidden;          /* not clickable/focusable while hidden */
      transition: opacity 0.25s, visibility 0.25s;
    }
    .tooltip-wrap:hover .tooltip,
    .tooltip-wrap:focus-within .tooltip {
      opacity: 1;
      visibility: visible;
    }
  </style>
</head>
<body>
  <h1>Hide methods</h1>

  <h2>display: none (the middle box is gone, no gap)</h2>
  <div class="row hide-none">
    <div class="box">Left</div>
    <button class="middle" onclick="alert('clicked!')">Middle</button>
    <div class="box">Right</div>
  </div>

  <h2>visibility: hidden (gap stays, cannot click)</h2>
  <div class="row hide-visibility">
    <div class="box">Left</div>
    <button class="middle" onclick="alert('clicked!')">Middle</button>
    <div class="box">Right</div>
  </div>

  <h2>opacity: 0 (gap stays, click the gap: alert still fires!)</h2>
  <div class="row hide-opacity">
    <div class="box">Left</div>
    <button class="middle" onclick="alert('clicked!')">Middle</button>
    <div class="box">Right</div>
  </div>

  <h2>Child can re-show under visibility:hidden</h2>
  <div class="parent-hidden">
    Parent text is hidden
    <div class="peek">...but this child is visible</div>
  </div>

  <h2>Fade tooltip (opacity + visibility)</h2>
  <div class="tooltip-wrap">
    <button>Hover or focus me</button>
    <div class="tooltip">Fades in smoothly</div>
  </div>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. Unmount vs hide: React's two ways of "hiding"
function Panel({ open }) {
  // A) display:none equivalent: not rendered, state is lost
  // return open ? <Content /> : null;

  // B) keep mounted but hidden, state is preserved (form inputs, video)
  return (
    <div hidden={!open}>          {/* hidden attr = display:none via UA CSS */}
      <Content />
    </div>
  );
}

// 2. Tailwind utilities
<div className="hidden">display:none</div>
<div className="invisible">visibility:hidden</div>
<div className="opacity-0">opacity:0 (still clickable!)</div>
<div className="sr-only">visually hidden, screen readers still read it</div>

// 3. Smooth fade in Tailwind (opacity + visibility)
<div className={`transition-all duration-200 ${open ? 'opacity-100 visible' : 'opacity-0 invisible'}`}>
  Dropdown
</div>

// 4. Accessibility: libraries like Headless UI / Radix handle focus and aria
//    for you, but you must still pick the correct hide method for closed state.
```

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between `display: none` and `visibility: hidden`?**
A1: `display: none` removes the element from layout: no space is reserved and the page reflows. `visibility: hidden` hides it but keeps its box and space. Neither is clickable or read by screen readers.

**Q2: How is `opacity: 0` different from `visibility: hidden`?**
A2: With `opacity: 0` the element is fully there: it keeps its space, receives clicks, hover and keyboard focus, and screen readers still read it. With `visibility: hidden` it cannot be interacted with. `opacity` is smoothly animatable and GPU-composited.

**Q3: Which one is better for performance?**
A3: Toggling `display` triggers reflow plus repaint (expensive on big trees). `visibility` triggers repaint only. `opacity` often only needs compositing, the cheapest. For frequent show/hide animations prefer opacity (and transform) with visibility to block interaction.

**Q4: How do you animate a hide/show with CSS?**
A4: Transition `opacity` and `visibility` together: `transition: opacity .2s, visibility .2s`. `display` cannot be transitioned the classic way. Newer browsers support `transition-behavior: allow-discrete` and `@starting-style` to animate `display`, but check support before relying on it.

**Q5: Can a child be visible if its parent has `visibility: hidden`?**
A5: Yes. `visibility` is inherited but a child may set `visibility: visible` and it will show. With `display: none` on the parent, children can never show.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Using `opacity: 0` to "close" a dropdown
```css
/* WRONG: invisible links are still tabbable and clickable */
.menu { opacity: 0; }
```
✅ **Correct way:**
```css
.menu { opacity: 0; visibility: hidden; }
.menu.open { opacity: 1; visibility: visible; }
```

❌ **Mistake 2:** Expecting `transition` to fade `display: none`
```css
/* WRONG: element just snaps, no fade */
.box { display: none; transition: opacity .3s; }
```
✅ **Correct way:** animate `opacity` + `visibility`, or toggle `display` after `transitionend` in JS.

❌ **Mistake 3:** Using `display: none` for text meant only visually hidden (like an icon button's label)
✅ **Correct way:** use the `sr-only` pattern so screen readers still announce "Close".

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| display: none | No box, no space | जगह भी नहीं, box भी नहीं |
| visibility: hidden | Invisible, space kept | अदृश्य पर जगह बनी रहती है |
| opacity: 0 | Transparent but interactive | पारदर्शी पर click होता है |
| Reflow | Layout recalculation | Layout दोबारा बनना |
| Repaint | Re-drawing pixels | Pixels दोबारा रंगना |
| Composite | GPU layer blending | GPU से layers जोड़ना |
| sr-only | Hidden visually, read by readers | दिखे नहीं, screen reader पढ़े |
| hidden attribute | HTML way to display:none | HTML का छुपाने वाला attribute |

---

## ⚡ 3-Line Summary
**English:**
1. `display: none` = gone from layout; `visibility: hidden` = invisible but space stays; `opacity: 0` = transparent but still clickable.
2. For smooth fades use opacity plus visibility so hidden items cannot be clicked or focused.
3. Choose by need: space, interaction, animation, and accessibility.

**Hindi:**
1. `display: none` = layout से गायब; `visibility: hidden` = अदृश्य पर जगह बची; `opacity: 0` = पारदर्शी पर click होता है।
2. Smooth fade के लिए opacity + visibility साथ use करो ताकि hidden item click/focus न हो।
3. जरूरत देखकर चुनो: जगह, interaction, animation और accessibility।

---

## ➡️ Next Topic
**65. CSS Position (static, relative, absolute, fixed, sticky)** — elements को normal flow से निकालकर ठीक जगह पर रखना, dropdown, sticky header और badges की नींव।
