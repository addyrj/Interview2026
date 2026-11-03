# 65. CSS Position (static, relative, absolute, fixed, sticky)
# हिंदी में: CSS Position — Element को ठीक जगह पर रखना

---

## 🔵 Simple Definition (English)
`position` decides how an element is placed on the page. **static** is the normal flow (default). **relative** shifts it from its normal spot. **absolute** removes it from the flow and places it against the nearest positioned ancestor. **fixed** pins it to the viewport. **sticky** acts normal until you scroll, then sticks.

## 🔵 सरल परिभाषा (Hindi)
`position` तय करती है कि element page पर कहाँ बैठेगा। **static** normal flow है (default)। **relative** element को उसकी असली जगह से खिसकाता है। **absolute** element को flow से निकालकर सबसे नज़दीकी positioned parent के हिसाब से रखता है। **fixed** उसे screen (viewport) पर चिपका देता है। **sticky** scroll होने तक normal रहता है, फिर चिपक जाता है।

---

## 🔴 Problem it Solves
```
BEFORE position:
  - Product card pe "20% OFF" badge corner me kaise lagaye?
  - Navbar scroll karne pe upar kaise rahe?
  - Dropdown button ke neeche kaise khule bina baki layout todhe?
  - Chat widget screen ke bottom-right me hamesha kaise dikhe?

Normal flow sirf upar se neeche, left se right chalta hai.
Overlap, pin aur exact placement ke liye position chahiye.
```

## 🔴 यह क्यों बना? (Hindi)
Normal flow में elements एक के बाद एक आते हैं। लेकिन असली websites में badge, dropdown, tooltip, sticky header, chat button जैसी चीज़ें दूसरे elements के ऊपर या किसी fixed जगह पर चाहिए। `position` के बिना यह सब सिर्फ margin hacks से होता जो टूट जाते।

---

## 🟢 How it Works — Step by Step

```
THE 5 VALUES:
┌──────────┬────────────────────────┬───────────────────┬──────────────────┐
│ Value    │ In normal flow?        │ top/left/right/   │ Reference point  │
│          │ (takes space?)         │ bottom work?      │                  │
├──────────┼────────────────────────┼───────────────────┼──────────────────┤
│ static   │ Yes                    │ NO (ignored)      │ -                │
│ relative │ Yes (original space    │ Yes               │ its OWN original │
│          │ stays reserved)        │                   │ position         │
│ absolute │ NO (removed from flow) │ Yes               │ nearest ancestor │
│          │                        │                   │ with position    │
│          │                        │                   │ != static        │
│ fixed    │ NO                     │ Yes               │ viewport         │
│ sticky   │ Yes (until stuck)      │ Yes (threshold)   │ nearest scroll   │
│          │                        │                   │ container        │
└──────────┴────────────────────────┴───────────────────┴──────────────────┘

GOLDEN PATTERN (badge on card):
  .card  { position: relative; }          <- makes parent the reference
  .badge { position: absolute; top: 8px; right: 8px; }

  If NO ancestor is positioned, absolute uses the initial containing block
  (roughly the page/viewport) -> badge flies to the page corner. Common bug!

STICKY RULES:
  - Needs a threshold: top: 0 (or bottom/left/right).
  - Sticks only inside its PARENT's box; when parent scrolls away, it goes too.
  - Does NOT work if any ancestor has overflow: hidden/auto/scroll
    (that ancestor becomes the scroll container).

ABSOLUTE CENTERING:
  .center { position: absolute; top: 50%; left: 50%; transform: translate(-50%,-50%); }
  or: inset: 0; margin: auto; (with width/height set)

Shorthand: inset: 0  ==  top:0; right:0; bottom:0; left:0;

Positioned elements (anything but static) can use z-index (next topic).
```

## 🟢 कैसे काम करता है? (Hindi)
1. **static**: default। `top/left` काम नहीं करते।
2. **relative**: element अपनी जगह पर रहता है (वहाँ की जगह reserved रहती है) और `top/left` से अपनी ही जगह से खिसकता है। इसका सबसे बड़ा काम: बच्चों के लिए reference बनना।
3. **absolute**: element flow से बाहर, जगह नहीं लेता। यह सबसे नज़दीकी ऐसे parent को ढूँढता है जिसका position `static` नहीं है, और उसी के हिसाब से `top/right/bottom/left` लेता है। ऐसा parent न मिले तो पूरे page के हिसाब से।
4. **fixed**: viewport से चिपका, scroll पर भी वहीं रहता है (chat button, top bar)।
5. **sticky**: पहले normal, scroll करके threshold (जैसे `top: 0`) पर पहुँचे तो चिपक जाता है, पर सिर्फ अपने parent के अंदर।
6. Sticky काम न करे तो देखो: threshold दिया है? किसी parent पर `overflow: hidden` तो नहीं?

---

## 🟡 Real World Example
**Amazon / Flipkart product cards:** the "Deal" or "-20%" badge is `position: absolute` inside a `position: relative` card. **Instagram / Gmail:** the top bar stays while you scroll (`fixed` or `sticky`). **Zomato:** the "View cart" bar sits at the bottom of the screen with `position: fixed; bottom: 0`. **Swiggy** restaurant menu: the category list on the left uses `position: sticky; top: 80px`. **WhatsApp Web / Intercom:** the chat bubble is `fixed` at bottom-right.

## 🟡 Real Example Hindi mein
**Amazon / Flipkart** के product card पर "-20%" badge `absolute` होता है और card `relative`। **Instagram / Gmail** का top bar scroll पर भी ऊपर रहता है (`fixed` या `sticky`)। **Zomato** का "View cart" bar screen के नीचे `fixed; bottom: 0` होता है। **Swiggy** menu की category list `sticky` होती है। Chat bubble जैसे widgets `fixed` होते हैं bottom-right में।

---

## 💻 Live Code Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CSS Position Demo</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; }
    body { margin: 0; font-family: system-ui, sans-serif; background: #f5f5f5; }

    /* STICKY header: normal until scrolled, then pinned at top:0 */
    .site-header {
      position: sticky;      /* needs a threshold below */
      top: 0;                /* the threshold */
      z-index: 10;           /* stay above content */
      background: #232f3e;
      color: #fff;
      padding: 14px 20px;
    }

    .page { max-width: 760px; margin: 0 auto; padding: 20px; }
    h2 { font-size: 16px; margin: 28px 0 8px; }

    /* RELATIVE: shifted from its own normal position; space is kept */
    .rel-box {
      position: relative;
      top: 12px;
      left: 20px;
      background: #bbdefb;
      padding: 12px;
    }

    /* ABSOLUTE badge inside RELATIVE card (the golden pattern) */
    .product-card {
      position: relative;     /* reference point for the badge */
      width: 240px;
      background: #fff;
      border: 1px solid #ddd;
      border-radius: 8px;
      padding: 16px;
    }
    .badge {
      position: absolute;     /* out of flow */
      top: 8px;               /* from card's top edge */
      right: 8px;             /* from card's right edge */
      background: #e53935;
      color: #fff;
      font-size: 12px;
      padding: 3px 8px;
      border-radius: 4px;
    }

    /* ABSOLUTE centering */
    .hero {
      position: relative;
      height: 140px;
      background: #c8e6c9;
    }
    .hero .centered {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);   /* pull back by half its own size */
      background: #fff;
      padding: 8px 16px;
      border-radius: 6px;
    }

    /* FIXED: pinned to viewport (like a chat button) */
    .chat-btn {
      position: fixed;
      right: 20px;
      bottom: 20px;
      background: #25d366;
      color: #fff;
      border: 0;
      padding: 12px 18px;
      border-radius: 999px;
      cursor: pointer;
      box-shadow: 0 2px 8px rgba(0,0,0,.3);
    }

    /* Filler so the page can scroll */
    .filler { height: 600px; background: repeating-linear-gradient(#fff, #fff 40px, #eee 40px, #eee 80px); }
  </style>
</head>
<body>
  <header class="site-header">Sticky Header (scroll down)</header>

  <main class="page">
    <h2>relative (shifted 12px down, 20px right; original space kept)</h2>
    <div class="rel-box">I am relative</div>

    <h2>absolute badge inside relative card</h2>
    <div class="product-card">
      <span class="badge">-20%</span>
      <h3>Wireless Mouse</h3>
      <p>Rs. 799</p>
    </div>

    <h2>absolute centering</h2>
    <div class="hero"><div class="centered">Centered</div></div>

    <h2>fixed chat button is at bottom-right of the screen</h2>
    <div class="filler"></div>
  </main>

  <button class="chat-btn">Chat</button>
</body>
</html>
```

---

## 🟠 React/Next.js Connection

```jsx
// 1. Badge on a card with Tailwind (relative parent + absolute child)
export function ProductCard({ product }) {
  return (
    <div className="relative w-60 rounded-lg border p-4">
      <span className="absolute right-2 top-2 rounded bg-red-600 px-2 py-0.5 text-xs text-white">
        -20%
      </span>
      <h3>{product.name}</h3>
    </div>
  );
}

// 2. Sticky navbar in Next.js layout
export default function Layout({ children }) {
  return (
    <>
      <header className="sticky top-0 z-50 bg-white shadow">Navbar</header>
      <main>{children}</main>
    </>
  );
}

// 3. Fixed floating action button
<button className="fixed bottom-5 right-5 rounded-full bg-green-500 p-3">Chat</button>

// 4. Centering absolute child
<div className="absolute inset-0 grid place-items-center">Overlay</div>

// 5. Portals: modals/dropdowns/tooltips are usually rendered with
//    ReactDOM.createPortal into document.body so they escape ancestors with
//    overflow:hidden or transform that would clip an absolute/fixed child.
```

---

## ⚫ Interview Questions + Answers

**Q1: Explain all five position values.**
A1: `static` default, normal flow, offsets ignored. `relative` stays in flow, offsets from own spot, creates a reference for children. `absolute` out of flow, offsets from nearest non-static ancestor. `fixed` out of flow, offsets from viewport. `sticky` in flow until scroll reaches the threshold, then behaves fixed within its parent.

**Q2: Absolute is positioned relative to what?**
A2: The nearest ancestor whose `position` is not `static` (relative, absolute, fixed, sticky). If none, the initial containing block (about the viewport size at the top of the page). Also, an ancestor with `transform`, `filter` or `will-change: transform` becomes the containing block for absolute and fixed children.

**Q3: Why is my `position: sticky` not working?**
A3: Common causes: no `top/bottom/left/right` threshold; an ancestor has `overflow: hidden/auto/scroll` (it becomes the scroll container); the parent is too short, so there is no room to stick; or the element is inside a flex/grid container with `align-items: stretch` making its height equal to the parent (use `align-self: flex-start`).

**Q4: Difference between fixed and sticky?**
A4: `fixed` is always pinned to the viewport and removed from flow (leaves a gap, you must add padding). `sticky` keeps its flow space, stays inside its parent, and only pins after reaching the threshold.

**Q5: Does `position: relative` with `top: 10px` affect other elements?**
A5: No. The element moves visually but its original space stays reserved, so siblings do not shift. It is commonly used just to become a reference for absolute children.

---

## 🔷 Common Mistakes to Avoid

❌ **Mistake 1:** Forgetting `position: relative` on the parent
```css
/* WRONG: badge goes to the page corner */
.badge { position: absolute; top: 0; right: 0; }
```
✅ **Correct way:**
```css
.card  { position: relative; }
.badge { position: absolute; top: 0; right: 0; }
```

❌ **Mistake 2:** Using `fixed` header and content hides under it
```css
/* WRONG: header is out of flow, first section is covered */
header { position: fixed; top: 0; height: 64px; }
```
✅ **Correct way:** add `padding-top: 64px` to body/main, or use `position: sticky; top: 0`.

❌ **Mistake 3:** Using absolute for whole page layouts
✅ **Correct way:** use Flexbox/Grid for layout; keep absolute for overlays, badges and tooltips.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| static | Default flow position | Default, normal जगह |
| relative | Offset from own spot | अपनी जगह से खिसकना |
| absolute | Out of flow, parent-based | Flow से बाहर, parent के हिसाब से |
| fixed | Pinned to viewport | Screen पर चिपका |
| sticky | Normal then pinned on scroll | Scroll पर चिपकने वाला |
| Containing block | Box that offsets are measured from | Offset का reference box |
| inset | Shorthand for top/right/bottom/left | चारों offsets का shorthand |
| Out of flow | Takes no space in layout | Layout में जगह नहीं लेता |

---

## ⚡ 3-Line Summary
**English:**
1. static is default, relative shifts and becomes a reference, absolute uses the nearest positioned ancestor, fixed uses the viewport, sticky pins on scroll.
2. Badge pattern: parent `relative`, child `absolute` with top/right.
3. Sticky needs a threshold and fails under ancestors with overflow set.

**Hindi:**
1. static default है, relative खिसकाता है और reference बनता है, absolute नज़दीकी positioned parent लेता है, fixed viewport लेता है, sticky scroll पर चिपकता है।
2. Badge pattern: parent `relative`, child `absolute` + top/right।
3. Sticky को threshold चाहिए और parent पर overflow हो तो काम नहीं करता।

---

## ➡️ Next Topic
**66. Z-index + Stacking Context** — positioned elements overlap होते हैं तो कौन ऊपर दिखेगा, और z-index कभी-कभी क्यों काम नहीं करता।
