# 122. CSS Tooltip
# हिंदी में: CSS Tooltip

Files: [index.html](index.html) · [style.css](style.css) (open index.html directly)

---

## 🔵 Simple Definition (English)
A tooltip is a small text bubble that appears when a user hovers or focuses an element. In pure CSS it is built with `position: absolute`, a pseudo-element (`::after`) that reads text from `attr(data-tip)`, and `opacity`/`visibility` toggled on `:hover` and `:focus-visible`.

## 🔵 सरल परिभाषा (Hindi)
Tooltip एक छोटा text bubble है जो user के hover या focus करने पर दिखता है। Pure CSS में यह `position: absolute`, `::after` pseudo-element (जो `attr(data-tip)` से text लेता है) और `:hover`/`:focus-visible` पर `opacity`/`visibility` बदलकर बनता है।

---

## 🔴 Problem it Solves
```
PROBLEM: icon-only buttons and short labels need explanation without cluttering the UI.
  - native title="" tooltip: slow to appear, not stylable, not on touch
  - JS tooltip libraries: extra JS for a simple hint

SOLUTION: a CSS tooltip: tiny, stylable, works on hover + keyboard focus.
```

## 🔴 यह क्यों बना? (Hindi)
```
समस्या: सिर्फ icon वाले buttons और छोटे labels को UI भरे बिना समझाना होता है।
  - native title="" tooltip: देर से दिखता है, style नहीं होता, touch पर नहीं चलता
  - JS tooltip libraries: एक छोटे hint के लिए extra JS

हल: CSS tooltip: छोटा, style हो सकने वाला, hover + keyboard focus दोनों पर चलता है।
```

---

## 🟢 How it Works — Step by Step
```
1. Trigger gets position: relative (anchor)
2. Put the message in an attribute:  <button data-tip="Top tooltip">
3. .tip::after { content: attr(data-tip); position:absolute; }
   -> bubble text is read from HTML, no extra element
4. Place it: bottom: calc(100% + 10px); left: 50%; translateX(-50%)
5. Arrow: ::before with a border triangle (topic 116)
6. Hidden: opacity:0; visibility:hidden; pointer-events:none
7. Shown: .tip:hover::after, .tip:focus-visible::after { opacity:1; visibility:visible }
8. Small translate animation for a nice slide-in
9. Accessible version: real <span role="tooltip" id> + aria-describedby on the trigger
```

## 🟢 कैसे काम करता है? (Hindi)
```
1. Trigger पर position: relative (anchor)
2. Message attribute में रखो: <button data-tip="Top tooltip">
3. .tip::after { content: attr(data-tip); position:absolute; } -> text HTML से आता है
4. जगह: bottom: calc(100% + 10px); left: 50%; translateX(-50%)
5. तीर: ::before में border triangle (topic 116)
6. छिपा: opacity:0; visibility:hidden; pointer-events:none
7. दिखाओ: :hover और :focus-visible पर opacity:1; visibility:visible
8. थोड़ा translate animation
9. Accessible तरीका: असली <span role="tooltip" id> + trigger पर aria-describedby
```

---

## 🟡 Real World Example
**Gmail** toolbar icons (Archive, Delete, Snooze) show a tooltip on hover. **Amazon** shows tooltips on delivery info icons. **Instagram web** shows labels over icons in the sidebar. **Swiggy / Zomato** show an "i" tooltip for delivery fee breakdown.

## 🟡 Real Example Hindi mein
**Gmail** की toolbar icons (Archive, Delete, Snooze) hover पर tooltip दिखाती हैं। **Amazon** में delivery info icons पर tooltip होता है। **Instagram web** के sidebar icons पर label दिखता है। **Swiggy / Zomato** में delivery fee breakdown के लिए "i" tooltip होता है।

---

## 💻 Live Code Example
Complete page: [index.html](index.html) + [style.css](style.css). Core:

```html
<button class="tip" data-tip="Add to cart" type="button">Add</button>
```

```css
.tip { position: relative; }
.tip::after {
  content: attr(data-tip);               /* text from the attribute */
  position: absolute;
  bottom: calc(100% + 10px);             /* above the trigger */
  left: 50%;
  transform: translateX(-50%);           /* centre horizontally */
  padding: 6px 10px; border-radius: 6px;
  background: #202124; color: #fff; white-space: nowrap;
  opacity: 0; visibility: hidden; pointer-events: none;   /* hidden */
  transition: opacity .2s;
}
.tip:hover::after, .tip:focus-visible::after { opacity: 1; visibility: visible; }
```

---

## 🟠 React/Next.js Connection
```jsx
// 1) Tailwind "group" tooltip: simple and accessible with a real element
export function Tooltip({ label, children }) {
  return (
    <span className="group relative inline-block">
      {children}
      <span role="tooltip"
        className="pointer-events-none absolute bottom-full left-1/2 mb-2 -translate-x-1/2 whitespace-nowrap rounded bg-gray-900 px-2 py-1 text-xs text-white
                   opacity-0 transition-opacity group-hover:opacity-100 group-focus-within:opacity-100">
        {label}
      </span>
    </span>
  );
}

// 2) Tailwind arbitrary pseudo-element using data attr:
// <button data-tip="Hi" className="relative after:absolute after:bottom-full after:content-[attr(data-tip)] ...">

// 3) For auto-flipping near viewport edges use Radix Tooltip, Floating UI, or shadcn/ui <Tooltip>.
```

---

## ⚫ Interview Questions + Answers

**Q1: How do you create a tooltip with only CSS?**
A1: Anchor with `position: relative`, add a pseudo-element `::after` with `content: attr(data-tip)` positioned absolutely, hide it with opacity/visibility, show it on `:hover`/`:focus-visible`.

**Q2: Why `pointer-events: none` on the hidden tooltip?**
A2: Otherwise an invisible bubble sits over other elements and blocks clicks or causes hover flicker.

**Q3: Why use opacity + visibility instead of display none?**
A3: `display` cannot transition. `opacity` fades, and `visibility` removes it from interaction/accessibility after the fade (visibility is discretely animatable).

**Q4: What are the accessibility requirements?**
A4: Show on keyboard focus too, use `role="tooltip"` and `aria-describedby`, keep it visible while the pointer is over it, and let users dismiss with Esc (WCAG 1.4.13: dismissible, hoverable, persistent). Pseudo-element content is not reliably announced, so use a real element for important info.

**Q5: What are the limits of CSS-only tooltips?**
A5: They can be clipped by parents with `overflow: hidden`, cannot flip near viewport edges, are not announced reliably, and have no touch behaviour. Use Floating UI, Radix, or the Popover API with anchor positioning (newer; check browser support).

---

## 🔷 Common Mistakes to Avoid
❌ **Mistake 1:** Parent without `position: relative`, so the tooltip lands in a random place.
✅ **Correct way:** Set `position: relative` on the trigger.

❌ **Mistake 2:** Tooltip clipped by `overflow: hidden` on an ancestor.
✅ **Correct way:** Move overflow, or render with a portal / Popover API.

❌ **Mistake 3:** Only `:hover`, so keyboard users cannot see it.
✅ **Correct way:** Add `:focus-visible` (or `:focus-within`).

❌ **Mistake 4:** Long text with `white-space: nowrap` running off-screen.
✅ **Correct way:** Use `max-width` + `white-space: normal` for long tips.

❌ **Mistake 5:** Putting critical info only in a tooltip (touch users never see it).
✅ **Correct way:** Tooltips for hints only.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Tooltip | Small hover/focus hint | छोटा hint bubble |
| `attr()` | Reads HTML attribute in CSS `content` | Attribute को CSS में पढ़ना |
| `::before/::after` | Generated pseudo-elements | CSS से बने नकली elements |
| `pointer-events` | Whether element takes mouse events | Mouse events लेना या नहीं |
| `role="tooltip"` | ARIA role for tooltips | Tooltip की पहचान |
| `aria-describedby` | Links trigger to its description | Trigger से description जोड़ना |
| `:focus-visible` | Keyboard focus only | सिर्फ keyboard focus |

---

## ⚡ 3-Line Summary
**English:**
1. CSS tooltip = relative trigger + absolute `::after` with `content: attr(data-tip)`, shown on `:hover` and `:focus-visible`.
2. Hide with opacity/visibility/`pointer-events: none`; add a border-triangle arrow.
3. For accessibility and edge-flipping use a real `role="tooltip"` element or Radix/Floating UI in React.

**Hindi:**
1. CSS tooltip = relative trigger + absolute `::after` जिसमें `content: attr(data-tip)`, `:hover` और `:focus-visible` पर दिखता है।
2. opacity/visibility/`pointer-events: none` से छिपाओ; border-triangle का तीर लगाओ।
3. Accessibility और edge-flipping के लिए असली `role="tooltip"` element या React में Radix/Floating UI use करो।

---

## ➡️ Next Topic
**123. Form Styling** — inputs, labels, focus और validation states को सुंदर और accessible बनाना।
