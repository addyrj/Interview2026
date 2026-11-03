# 114. Build a Modal/Popup
# हिंदी में: Modal/Popup बनाना

Files: [index.html](index.html) · [style.css](style.css) (open index.html directly in browser)

---

## 🔵 Simple Definition (English)
A modal is a box that appears on top of the page and blocks interaction with the content behind it until the user closes it. It has a dark overlay (backdrop), a centred dialog, and a close action.

## 🔵 सरल परिभाषा (Hindi)
Modal एक box है जो page के ऊपर आता है और जब तक user उसे बंद न करे, पीछे के content से interaction रोक देता है। इसमें dark overlay (backdrop), बीच में dialog और close का तरीका होता है।

---

## 🔴 Problem it Solves
```
BEFORE:
  - window.alert / confirm: ugly, cannot be styled, blocks the thread
  - Hand-made modals: forgot focus trap, Esc key, scroll lock, z-index wars
  - Screen readers could not tell it was a dialog

NEEDED: a styled, accessible way to ask the user for a decision/info without leaving the page.
```

## 🔴 यह क्यों बना? (Hindi)
```
पहले:
  - alert / confirm: बदसूरत, style नहीं हो सकता, page रोक देता है
  - खुद का modal: focus trap, Esc key, scroll lock, z-index की दिक्कतें
  - screen reader को पता नहीं चलता कि यह dialog है

ज़रूरत: page छोड़े बिना user से decision/info लेने का styled और accessible तरीका।
```

---

## 🟢 How it Works — Step by Step
```
1. Markup: <dialog> element with heading, body, footer buttons
2. JS: dialog.showModal() opens it in the browser "top layer"
   (always above everything: no z-index fight)
3. ::backdrop pseudo-element = the dark overlay (style it with background)
4. Browser gives for free: focus trap, Esc closes, inert background
5. dialog.close() closes it; click-outside is detected by checking click
   coordinates against getBoundingClientRect()
6. CSS: width:min(92vw,420px) for responsive size, animation for fade/scale
7. Lock page scroll: body:has(dialog[open]) { overflow:hidden }
```

## 🟢 कैसे काम करता है? (Hindi)
```
1. Markup: <dialog> element में heading, body, footer buttons
2. JS: dialog.showModal() इसे browser की "top layer" में खोलता है
   (हमेशा सबसे ऊपर, z-index की ज़रूरत नहीं)
3. ::backdrop pseudo-element = dark overlay (background से style करो)
4. Browser खुद देता है: focus trap, Esc से close, पीछे का हिस्सा inert
5. dialog.close() बंद करता है; बाहर click पकड़ने के लिए click के coordinates को
   getBoundingClientRect() से compare करते हैं
6. CSS: width:min(92vw,420px) responsive size, fade/scale animation
7. Page scroll lock: body:has(dialog[open]) { overflow:hidden }
```

---

## 🟡 Real World Example
**Swiggy / Zomato:** "Cancel order?" confirmation, location picker and login popups. **Instagram:** the "Delete post?" dialog and the photo viewer overlay. **Gmail:** the "Discard draft?" confirmation. **Amazon:** the "Add to cart" side confirmation. All dim the page and focus attention on one task.

## 🟡 Real Example Hindi mein
**Swiggy / Zomato:** "Order cancel करें?" confirmation, location picker और login popup। **Instagram:** "Post delete करें?" dialog और photo viewer overlay। **Gmail:** "Draft discard करें?" confirmation। **Amazon:** "Add to cart" का confirmation। सब page को dim करके user का ध्यान एक काम पर लाते हैं।

---

## 💻 Live Code Example
Complete page: [index.html](index.html) + [style.css](style.css). Essentials:

```html
<!-- Native dialog: focus trap + Esc + backdrop for free -->
<dialog id="modal" aria-labelledby="modalTitle">
  <h2 id="modalTitle">Delete this order?</h2>
  <button id="closeBtn" type="button">Close</button>
</dialog>
<button id="openBtn" type="button">Open</button>

<script>
  const modal = document.getElementById('modal');
  // Open as modal (top layer + backdrop)
  document.getElementById('openBtn').addEventListener('click', () => modal.showModal());
  // Close
  document.getElementById('closeBtn').addEventListener('click', () => modal.close());
</script>
```

```css
/* Dark overlay */
dialog::backdrop { background: rgba(0,0,0,.55); }
/* Responsive centred box (dialog is centred by default) */
dialog { width: min(92vw, 420px); border: 0; border-radius: 14px; }
/* Animation on open */
dialog[open] { animation: pop .22s ease-out; }
@keyframes pop { from { opacity: 0; transform: scale(.92); } to { opacity: 1; transform: none; } }
```

---

## 🟠 React/Next.js Connection
```jsx
'use client';
import { useEffect, useRef } from 'react';

// Controlled modal wrapper using native <dialog>
export function Modal({ open, onClose, children }) {
  const ref = useRef(null);

  useEffect(() => {
    const d = ref.current;
    if (open && !d.open) d.showModal();   // open
    if (!open && d.open) d.close();       // close
  }, [open]);

  return (
    // onClose fires on Esc as well, keeping React state in sync
    <dialog ref={ref} onClose={onClose} className="w-[min(92vw,420px)] rounded-xl backdrop:bg-black/50">
      {children}
    </dialog>
  );
}
// Alternatives: createPortal(modalJSX, document.body), Radix Dialog, shadcn/ui Dialog.
// Tailwind: backdrop:bg-black/50, open:animate-... variants.
// Next.js: Parallel + Intercepting routes make URL-based modals (Instagram-style photo modal).
```

---

## ⚫ Interview Questions + Answers

**Q1: How do you build an accessible modal?**
A1: Use `<dialog>` + `showModal()`; or `role="dialog" aria-modal="true"` with `aria-labelledby`, trap focus inside, close on Esc, return focus to the opener, make the background `inert`.

**Q2: Why does `<dialog>.showModal()` not need z-index?**
A2: It is rendered in the browser's top layer, above all stacking contexts, so ancestor `z-index`/`overflow` cannot hide it.

**Q3: How do you stop the background page from scrolling?**
A3: `body { overflow: hidden }` while open (here via `body:has(dialog[open])`, or a JS class toggle). Also consider `overscroll-behavior: contain` on the modal.

**Q4: `show()` vs `showModal()`?**
A4: `show()` opens a non-modal dialog (no backdrop, background stays interactive). `showModal()` makes it modal: backdrop, inert background, Esc closes.

**Q5: How do you close when clicking outside?**
A5: With `<dialog>`, a backdrop click targets the dialog element itself; compare click coordinates with `getBoundingClientRect()`. With a div-based overlay, add an onClick on the overlay and `stopPropagation` on the content.

---

## 🔷 Common Mistakes to Avoid
❌ **Mistake 1:** Overlay and modal with random `z-index: 9999` values.
✅ **Correct way:** Use the top layer (`<dialog>` / Popover API) or a portal at the end of `<body>`.

❌ **Mistake 2:** No focus management; Tab moves to the page behind.
✅ **Correct way:** `showModal()` handles it; custom modals need a focus trap and focus restore.

❌ **Mistake 3:** Icon-only close button without a label.
✅ **Correct way:** `aria-label="Close dialog"`.

❌ **Mistake 4:** Fixed `width: 500px` that overflows on phones.
✅ **Correct way:** `width: min(92vw, 420px)`.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Modal | Blocks background until closed | पीछे का हिस्सा block करने वाला popup |
| `::backdrop` | Overlay behind a modal dialog | पीछे का dark पर्दा |
| Top layer | Browser layer above all z-index | सबसे ऊपर की layer |
| Focus trap | Tab stays inside the dialog | Focus dialog के अंदर रहना |
| `inert` | Makes element non-interactive | निष्क्रिय हिस्सा |
| Portal | Render outside parent DOM node | Parent के बाहर render |

---

## ⚡ 3-Line Summary
**English:**
1. Use native `<dialog>` + `showModal()` for backdrop, focus trap and Esc for free.
2. Style `::backdrop`, size with `min(92vw, 420px)`, lock body scroll while open.
3. In React use a ref, a portal or Radix/shadcn Dialog; always label it for accessibility.

**Hindi:**
1. Native `<dialog>` + `showModal()` से backdrop, focus trap और Esc मुफ़्त मिलते हैं।
2. `::backdrop` style करो, `min(92vw, 420px)` से size दो, खुले होने पर body scroll lock करो।
3. React में ref, portal या Radix/shadcn Dialog use करो; accessibility के लिए label ज़रूर दो।

---

## ➡️ Next Topic
**115. Build a Responsive Grid Layout** — cards की grid जो बिना media query के हर screen पर adjust हो।
