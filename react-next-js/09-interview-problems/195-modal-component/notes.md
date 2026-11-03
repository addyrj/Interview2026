# 195. Build Modal Component
# हिंदी में: Modal Component बनाना

Code: [`App.jsx`](./App.jsx) in this folder (Portal, Escape to close, overlay click, focus trap, body scroll lock, focus returns to the opener, ARIA attributes).

---

## 🔵 Simple Definition (English)
A modal is a dialog box that appears on top of the page and blocks interaction with everything behind it until it is closed. A good React modal renders through a **Portal**, closes with Escape or an overlay click, keeps keyboard focus inside, and is accessible to screen readers.

## 🔵 सरल परिभाषा (Hindi)
Modal एक dialog box है जो page के ऊपर आता है और बंद होने तक पीछे की हर चीज़ पर interaction रोक देता है। अच्छा React modal **Portal** से render होता है, Escape या overlay click से बंद होता है, keyboard focus को अंदर रखता है और screen readers के लिए accessible होता है।

---

## 🔴 Problem it Solves

If you render a modal inside a deeply nested component, parent styles break it: `overflow: hidden` clips it, `transform` changes `position: fixed` behaviour and `z-index` stacking contexts hide it. Beyond layout, a naive modal is inaccessible: Tab moves focus to elements behind it, Escape does nothing, the page scrolls behind, and screen readers do not know a dialog opened.

```jsx
// PROBLEM: modal inside a parent with overflow hidden / transform
<div style={{ overflow: 'hidden', transform: 'translateZ(0)' }}>
  <div style={{ position: 'fixed', inset: 0 }}>Modal</div>       {/* clipped / mispositioned ❌ */}
</div>
// Also: Tab escapes to the page behind, no Escape key, body still scrolls
```

## 🔴 यह क्यों बना? (Hindi)
अगर modal को गहरे nested component के अंदर render करें तो parent के styles उसे बिगाड़ते हैं: `overflow: hidden` उसे काट देता है, `transform` से `position: fixed` का व्यवहार बदल जाता है और `z-index` stacking context उसे छिपा देता है। Layout के अलावा, साधारण modal accessible भी नहीं होता: Tab से focus पीछे के elements पर चला जाता है, Escape काम नहीं करता, पीछे page scroll होता रहता है और screen reader को पता नहीं चलता कि dialog खुला है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Props: open, onClose, title, children
Step 2 → If !open return null (nothing in the DOM)
Step 3 → createPortal(modalJSX, document.body) renders outside the parent DOM tree
Step 4 → Overlay div covers the screen; onClick={onClose}. The dialog stops propagation
Step 5 → role="dialog", aria-modal="true", aria-labelledby={titleId}
Step 6 → On open (effect): save document.activeElement, lock body scroll, focus the dialog
Step 7 → Keydown listener: Escape closes; Tab/Shift+Tab cycle inside the dialog (focus trap)
Step 8 → Cleanup on close: remove listener, restore scroll, focus the original button

React events still bubble through the PORTAL to React parents (they follow the React tree,
not the DOM tree).
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Props: open, onClose, title, children
Step 2 → अगर !open तो null return करो (DOM में कुछ नहीं)
Step 3 → createPortal(modalJSX, document.body) parent DOM tree के बाहर render करता है
Step 4 → Overlay div पूरी screen ढकता है; onClick={onClose}। Dialog propagation रोकता है
Step 5 → role="dialog", aria-modal="true", aria-labelledby={titleId}
Step 6 → खुलने पर (effect): document.activeElement सेव करो, body scroll lock करो, dialog पर focus
Step 7 → Keydown listener: Escape बंद करता है; Tab/Shift+Tab dialog के अंदर घूमते हैं (focus trap)
Step 8 → बंद होने पर cleanup: listener हटाओ, scroll वापस, पुराने button पर focus लौटाओ

React events PORTAL से होकर भी React parents तक bubble होते हैं (वे React tree
का पालन करते हैं, DOM tree का नहीं)।
```

---

## 🟡 Real World Example
**Swiggy "Replace cart items?" confirmation, Amazon "Sign in" popup, Flipkart login modal, Zomato location picker:** the page dims, the dialog appears in the centre, you cannot click the page behind, Escape closes it, and after closing, focus returns to the button you used. Banks use the same pattern for "Confirm payment" dialogs.

## 🟡 Real Example Hindi mein
**Swiggy का "Cart items बदलें?" confirmation, Amazon का "Sign in" popup, Flipkart login modal, Zomato location picker:** page धुंधला हो जाता है, बीच में dialog आता है, पीछे का page click नहीं होता, Escape से बंद होता है और बंद होने पर focus उसी button पर लौट आता है जिससे खोला था। Banks "Payment confirm करें" dialogs में यही pattern इस्तेमाल करते हैं।

---

## 💻 Code Example — Basic

```jsx
// Smallest useful modal: portal + overlay click + Escape
import { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';                    // render outside the parent

function Modal({ open, onClose, children }) {
  useEffect(() => {
    if (!open) return;
    const onKey = (e) => e.key === 'Escape' && onClose();    // Escape closes
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey); // cleanup
  }, [open, onClose]);

  if (!open) return null;                                    // closed: render nothing
  return createPortal(
    <div onClick={onClose} style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,.5)' }}>
      <div onClick={(e) => e.stopPropagation()} style={{ background: '#fff', margin: '20vh auto', padding: 24, width: 300 }}>
        {children}
      </div>
    </div>,
    document.body                                            // mounted at body level
  );
}

export default function App() {
  const [open, setOpen] = useState(false);
  return (<><button onClick={() => setOpen(true)}>Open</button>
    <Modal open={open} onClose={() => setOpen(false)}>Hello</Modal></>);
}
```

## 💻 Code Example — Advanced

The accessible version is in [`App.jsx`](./App.jsx). Key techniques:

```jsx
// 1. Keep the latest onClose in a ref so the effect depends only on `open`
const onCloseRef = useRef(onClose);
onCloseRef.current = onClose;                                // updated each render

// 2. Focus management
lastFocused.current = document.activeElement;                // remember the opener
dialogRef.current?.focus();                                  // dialog has tabIndex={-1}
// cleanup → lastFocused.current?.focus?.()                  // give focus back

// 3. Scroll lock that restores the previous value
const prevOverflow = document.body.style.overflow;
document.body.style.overflow = 'hidden';
// cleanup → document.body.style.overflow = prevOverflow;

// 4. Focus trap: wrap Tab at the first/last focusable element
if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }

// 5. ARIA: role="dialog" aria-modal="true" aria-labelledby={useId()}
```

Verified with jsdom: clicking the opener shows the dialog and sets `overflow: hidden`; Escape closes it and clears the lock; an overlay click closes it too.

Alternative (modern): the native `<dialog>` element with `dialog.showModal()` provides the top layer, focus trap, Escape and `::backdrop` for free in current browsers.

---

## 🟠 Next.js Connection

Modals are Client Components (state, effects, `document`). Two points: a Portal needs `document`, so it must render only after mount in SSR, and Next.js has a special feature, **intercepting + parallel routes**, to show a route (like `/photo/123`) as a modal over the current page while keeping a shareable URL (topic 183).

```jsx
// app/components/Modal.jsx
'use client';
import { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';

export default function Modal({ open, onClose, children }) {
  const [mounted, setMounted] = useState(false);             // false on the server
  useEffect(() => setMounted(true), []);                     // true only in the browser
  if (!mounted || !open) return null;                        // avoids document access during SSR
  return createPortal(
    <div role="dialog" aria-modal="true" onClick={onClose} className="overlay">
      <div onClick={(e) => e.stopPropagation()} className="box">{children}</div>
    </div>,
    document.body
  );
}
```
In `App.jsx`, the Portal is created only when `open` is true, which cannot happen during the server render, so it is already SSR-safe; the `mounted` guard is for modals that can start open.

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Rendering the modal inline inside the parent
✅ **Correct:** Use `createPortal(..., document.body)` to escape `overflow`, `transform` and `z-index` problems.

```jsx
// Wrong
return open ? <div className="modal">...</div> : null;              // ❌ clipped by parents
// Right
return open ? createPortal(<div className="modal">...</div>, document.body) : null; // ✅
```

❌ **Mistake 2:** Overlay click closes the modal even when clicking inside the dialog
✅ **Correct:** Stop propagation on the dialog (or compare `e.target === e.currentTarget` on the overlay).

```jsx
// Wrong: every click inside bubbles to the overlay → closes
<div onClick={onClose}><div>content</div></div>                      // ❌
// Right
<div onClick={onClose}><div onClick={(e) => e.stopPropagation()}>content</div></div> // ✅
```

❌ **Mistake 3:** Forgetting cleanup (listeners, scroll lock, focus), or putting `onClose` in dependencies of an effect that also locks scroll
✅ **Correct:** Return a cleanup that undoes everything. Use a ref for the latest `onClose` so inline arrow functions do not re-run the lock logic every render.

```jsx
// Wrong: scroll stays locked after close; listener leaks
useEffect(() => { document.body.style.overflow = 'hidden'; }, [open]);   // ❌ no cleanup
// Right
useEffect(() => {
  if (!open) return;
  const prev = document.body.style.overflow;
  document.body.style.overflow = 'hidden';
  return () => { document.body.style.overflow = prev; };                // ✅ restores
}, [open]);
```

---

## 🧠 Tricky Interview Question

```jsx
function Parent() {
  return (
    <div onClick={() => console.log('parent clicked')}>
      <Modal open onClose={() => {}}>
        <button>Inside</button>
      </Modal>
    </div>
  );
}
// Modal uses createPortal(..., document.body). The user clicks "Inside".
// Is "parent clicked" logged? The parent div is not an ancestor in the DOM.
```
**Answer:** Yes, `parent clicked` is logged. React synthetic events bubble along the **React component tree**, not the DOM tree. The portal's content is still a child of `Modal`, which is a child of the `div` with the handler, so the click bubbles up to it even though the DOM nodes live under `document.body`. To prevent it, call `e.stopPropagation()` inside the modal (as `App.jsx` does on the dialog), or avoid attaching click handlers to ancestors of a portal. This also means context from parents is available inside the portal.

---

## ⚫ Interview Questions + Answers

Q1: Why use a Portal for a modal?
A1: A Portal renders children into a different DOM node (usually `document.body`) while keeping them in the same React tree. That avoids parent CSS issues (overflow clipping, stacking contexts, transforms), keeps z-index simple, and still preserves context and event bubbling.

Q2: What makes a modal accessible?
A2: `role="dialog"` (or `alertdialog`), `aria-modal="true"`, a label (`aria-labelledby`), moving focus into the dialog on open, trapping Tab inside, closing with Escape, returning focus to the trigger on close, and making the background inert (`inert` attribute or `aria-hidden`). Native `<dialog>` handles most of this.

Q3: How do you stop the page scrolling behind the modal?
A3: Set `document.body.style.overflow = 'hidden'` while open and restore the previous value on cleanup. For iOS and layout shift from the missing scrollbar you may also add padding or use `overscroll-behavior`. Library implementations handle many edge cases.

Q4: Why store `onClose` in a ref?
A4: Parents often pass an inline function, a new reference on each render. If the effect depended on it, the effect would clean up and re-run each time (unlocking scroll, restoring focus, re-adding listeners). The ref gives the effect the latest function without being a dependency. (React's `useEffectEvent` is the future replacement, version-dependent.)

Q5: Controlled vs uncontrolled modal API?
A5: Controlled: the parent owns `open` and passes `onClose` (as in this solution), easy to coordinate with other state. Uncontrolled/compound: `<Dialog><Dialog.Trigger/><Dialog.Content/></Dialog>` owns state internally (Radix, Headless UI). Many production apps use these libraries for the accessibility details.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- You need a decision or focused task that should block the page (confirm delete, login, payment)
- Content is short and the user must act before continuing

❌ **Avoid when:**
- Showing non-critical info (use a toast, inline message, popover)
- Long forms or multi-step flows on mobile (use a full page or bottom sheet)
- Stacking modals on modals (confusing and harder to make accessible)

---

## 📊 Visual Diagram

```
  React tree                           DOM tree
  ──────────                           ────────
  <App>                                <body>
    <Parent onClick>                     <div id="root">
      <Modal open>  ──createPortal──┐      <div> Parent ... </div>
                                    │    </div>
                                    └─▶  <div class="overlay">   (child of body)
                                           <div role="dialog" aria-modal>
                                             Title / content / [Close]

  Lifecycle on open:  save focus → lock scroll → focus dialog → listen keys
  Lifecycle on close: remove listener → unlock scroll → restore focus

  Tab order: [first] → ... → [last] ──wrap──▶ [first]   (focus trap)
  Re-render: only Modal and children when `open`/children change; parent unaffected.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Portal | Render children in another DOM node | Children को दूसरे DOM node में render करना |
| Overlay / backdrop | Dimmed layer behind the dialog | Dialog के पीछे की धुंधली परत |
| Focus trap | Keep Tab focus inside the dialog | Tab focus को dialog के अंदर रखना |
| aria-modal | Tells assistive tech content behind is inert | पीछे का content निष्क्रिय होने का संकेत |
| Scroll lock | Prevent page scrolling | Page का scroll रोकना |
| Event bubbling | Event moving up to ancestors | Event का ऊपर के parents तक जाना |
| stopPropagation | Stops the event from bubbling | Event को bubble होने से रोकना |
| inert | Attribute that disables a subtree | Subtree को निष्क्रिय करने वाला attribute |

---

## ⚡ 3-Line Summary
**English:**
1. Render the modal with `createPortal` into `document.body`, with an overlay that closes on click and a dialog that stops propagation.
2. Handle accessibility: ARIA roles, Escape, focus trap, scroll lock, and returning focus to the trigger.
3. Always clean up effects; in Next.js keep it a Client Component and use intercepting routes for URL-based modals.

**Hindi:**
1. Modal को `createPortal` से `document.body` में render करो, overlay click पर बंद हो और dialog propagation रोके।
2. Accessibility संभालो: ARIA roles, Escape, focus trap, scroll lock और trigger पर focus वापस।
3. Effects का cleanup हमेशा करो; Next.js में इसे Client Component रखो और URL वाले modals के लिए intercepting routes इस्तेमाल करो।

---

## ➡️ Next Topic
**196. Build Accordion Component** — FAQ जैसे sections जो खुलते-बंद होते हैं: single/multiple open mode, `aria-expanded` और Set से state।
