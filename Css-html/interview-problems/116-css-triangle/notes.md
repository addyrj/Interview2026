# 116. CSS Triangle using borders
# हिंदी में: Borders से CSS Triangle बनाना

Files: [index.html](index.html) · [style.css](style.css) (open index.html directly)

---

## 🔵 Simple Definition (English)
A CSS triangle is made from a zero-size box with thick borders. Borders meet at diagonal joints, so if you make only one border coloured and the neighbours `transparent`, you see a triangle.

## 🔵 सरल परिभाषा (Hindi)
CSS triangle एक zero-size box पर मोटे borders से बनता है। Borders diagonal पर मिलते हैं, इसलिए सिर्फ एक border रंगीन रखो और बगल वाले `transparent` कर दो, तो triangle दिखता है।

---

## 🔴 Problem it Solves
```
BEFORE: needed an image/PNG/SVG for every small arrow
        (tooltip arrows, dropdown carets, speech-bubble tails)
        -> extra HTTP request, hard to recolour, blurry on retina

NOW: pure CSS, one colour variable, scales and recolours instantly
```

## 🔴 यह क्यों बना? (Hindi)
```
पहले: हर छोटे arrow (tooltip arrow, dropdown caret, speech-bubble tail) के लिए
      image/PNG/SVG चाहिए थी -> extra request, रंग बदलना मुश्किल, retina पर blur

अब: pure CSS, एक colour variable, आसानी से resize और recolour
```

---

## 🟢 How it Works — Step by Step
```
1. width:0; height:0           -> no content area, only borders remain
2. border-style: solid         -> borders must exist
3. border-width: 40px          -> each border is a trapezoid cut at 45 degrees
                                  (top/right/bottom/left borders meet in an "X")
4. Make 3 borders transparent, 1 visible:
     UP    : border-bottom coloured, border-left/right transparent
     DOWN  : border-top coloured,    border-left/right transparent
     LEFT  : border-right coloured,  border-top/bottom transparent
     RIGHT : border-left coloured,   border-top/bottom transparent
5. Size: the visible border's width = height of the triangle,
         the two transparent borders = half of its base each
6. Use ::after to place arrows without extra HTML
```

## 🟢 कैसे काम करता है? (Hindi)
```
1. width:0; height:0 -> content नहीं, सिर्फ borders बचते हैं
2. border-style: solid -> border दिखने के लिए ज़रूरी
3. border-width: 40px -> हर border 45 degree पर कटा trapezoid, चारों "X" में मिलते हैं
4. तीन borders transparent, एक रंगीन:
     UP    : border-bottom रंगीन, left/right transparent
     DOWN  : border-top रंगीन,    left/right transparent
     LEFT  : border-right रंगीन,  top/bottom transparent
     RIGHT : border-left रंगीन,   top/bottom transparent
5. रंगीन border की width = triangle की height; दोनों transparent borders = base का आधा-आधा
6. Extra HTML के बिना arrow के लिए ::after use करो
```

---

## 🟡 Real World Example
**Zomato / Swiggy dropdown carets** (small down arrow near the location), **Instagram/WhatsApp-style chat bubbles** with a tail, **Gmail's tooltip** arrows, and **Amazon's** "Account and Lists" flyout pointer are all triangles like this (or SVG/clip-path equivalents).

## 🟡 Real Example Hindi mein
**Zomato / Swiggy की dropdown caret** (location के पास छोटा नीचे का तीर), **Instagram/WhatsApp chat bubble** की पूँछ, **Gmail tooltip** के arrows और **Amazon "Account and Lists"** flyout का pointer ऐसे ही triangles होते हैं (या SVG/clip-path वाले)।

---

## 💻 Live Code Example
Complete page: [index.html](index.html) + [style.css](style.css).

```html
<div class="tri tri-up"></div>
<div class="bubble">Your order is out for delivery!</div>
```

```css
/* Base: zero-size box */
.tri { width: 0; height: 0; border-style: solid; }

/* UP triangle: 80px wide base, 70px tall */
.tri-up {
  border-width: 0 40px 70px 40px;                 /* top right bottom left */
  border-color: transparent transparent #3f51b5 transparent;
}

/* Arrow on a bubble (DOWN) using ::after */
.bubble { position: relative; }
.bubble::after {
  content: ""; position: absolute; top: 100%; left: 24px;
  border-style: solid; border-width: 10px 10px 0 10px;
  border-color: #1a73e8 transparent transparent transparent;
}

/* Modern alternative */
.clip-tri { width: 80px; height: 70px; background: #00897b; clip-path: polygon(50% 0, 100% 100%, 0 100%); }
```

---

## 🟠 React/Next.js Connection
```jsx
// Tailwind: arbitrary pseudo-element arrow
<div className="relative rounded-lg bg-blue-600 px-4 py-3 text-white
  after:absolute after:left-6 after:top-full after:border-x-8 after:border-t-8
  after:border-x-transparent after:border-t-blue-600 after:content-['']">
  Out for delivery
</div>

// Tailwind has border-x-8 / border-t-8 / border-transparent utilities,
// and clip-path via arbitrary value: [clip-path:polygon(50%_0,100%_100%,0_100%)]

// Component with a CSS variable for colour
export function Arrow({ color = '#3f51b5' }) {
  return <span style={{ '--c': color }} className="arrow" />;
}
// .arrow { border: 8px solid transparent; border-top-color: var(--c); }
```

---

## ⚫ Interview Questions + Answers

**Q1: How do you make a triangle with CSS?**
A1: Zero width/height box with a solid border. Make three borders transparent and one coloured. E.g. up triangle: `border-width: 0 40px 70px; border-color: transparent transparent #000`.

**Q2: Why does this work?**
A2: Where two borders meet, the browser draws a 45-degree diagonal joint. With a 0x0 content box the four borders become four triangles; transparent ones vanish.

**Q3: How do you control height and width of the triangle?**
A3: The coloured border's thickness is the height; the two transparent side borders add up to the base width. Make the sides larger for a wider triangle.

**Q4: Other ways to draw a triangle?**
A4: `clip-path: polygon(50% 0, 100% 100%, 0 100%)`, inline SVG `<polygon>`, a rotated square with `transform: rotate(45deg)` (used for tooltips with a border), or a conic/linear gradient.

**Q5: Border triangle vs clip-path?**
A5: Border triangles work in every browser and are tiny but cannot have borders or shadows easily. `clip-path` is more flexible (any polygon, gradients) but clips box-shadow and borders too.

---

## 🔷 Common Mistakes to Avoid
❌ **Mistake 1:** Forgetting `border-style: solid`, so nothing shows.
✅ **Correct way:** Always set the style (`border-style: solid`).

❌ **Mistake 2:** Using `border: 40px solid #000` and wondering why it is a square.
✅ **Correct way:** Set one colour and make the rest `transparent`.

❌ **Mistake 3:** Wrong direction: border-bottom makes an UP triangle, not down.
✅ **Correct way:** The visible border is the side the triangle's base sits on.

❌ **Mistake 4:** Arrow `::after` without `content: ""` or `position`.
✅ **Correct way:** Always set `content: ""` and position it.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Border joint | Diagonal where 2 borders meet | दो borders का तिरछा मिलन |
| `transparent` | Invisible colour | पारदर्शी रंग |
| `::after` | Pseudo-element after content | Content के बाद का नकली element |
| `clip-path` | Cuts an element to a shape | Shape में काटना |
| Caret | Small dropdown arrow | छोटा तीर |

---

## ⚡ 3-Line Summary
**English:**
1. Zero-size box + thick border: borders meet diagonally and form triangles.
2. Keep one border coloured and the other three transparent; its thickness is the triangle height.
3. `clip-path: polygon()` or SVG is the modern alternative, and Tailwind has `border-*` utilities.

**Hindi:**
1. Zero-size box + मोटा border: borders तिरछे मिलते हैं और triangles बनते हैं।
2. एक border रंगीन, बाकी तीन transparent; उसकी मोटाई ही triangle की height है।
3. `clip-path: polygon()` या SVG आधुनिक विकल्प हैं, Tailwind में `border-*` utilities हैं।

---

## ➡️ Next Topic
**117. Sticky Header** — `position: sticky` से scroll करने पर header ऊपर चिपका रहना।
