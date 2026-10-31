# 67. React Portals
# हिंदी में: React Portals — DOM में Parent के बाहर Render करना

---

## 🔵 Simple Definition (English)
A **portal** lets a component render its children into a **different DOM node** (often `document.body`) while still belonging to its original place in the **React tree**. It is created with `createPortal(children, domNode)` from `react-dom`. The DOM position changes, but props, state, context and event bubbling still follow the React tree.

## 🔵 सरल परिभाषा (Hindi)
**Portal** एक component को उसके children को किसी **अलग DOM node** (अक्सर `document.body`) में render करने देता है, फिर भी वह **React tree** में अपनी असली जगह पर रहता है। यह `react-dom` से `createPortal(children, domNode)` से बनता है। DOM की जगह बदलती है, पर props, state, context और event bubbling React tree के हिसाब से चलते हैं।

---

## 🔴 Problem it Solves

A modal, tooltip or toast often sits deep inside a component tree, inside a container with `overflow: hidden`, a `position: relative`, or a `z-index` stacking context. If the modal renders in place, it can be clipped, pushed out of position or covered by other elements. Before portals, developers used imperative DOM code to move elements, which broke React's control of the tree. Portals solve this by rendering into another DOM node while keeping React's behavior.

```jsx
// PROBLEM: the modal is inside a container with overflow: hidden → it gets clipped
<div style={{ overflow: 'hidden', position: 'relative' }}>
  <Modal />            {/* clipped: cannot escape the parent box */}
</div>

// SOLUTION: render the modal's DOM into document.body, but keep it in the React tree
<div style={{ overflow: 'hidden' }}>
  {createPortal(<Modal />, document.body)}  {/* appears on top, outside the box */}
</div>
```

## 🔴 यह क्यों बना? (Hindi)
Modal, tooltip या toast अक्सर tree में गहराई पर होते हैं, किसी ऐसे container के अंदर जिसमें `overflow: hidden`, `position: relative` या `z-index` stacking context हो। Modal वहीं render हो तो कट सकता है, गलत जगह जा सकता है या दूसरे elements के नीचे छिप सकता है। Portals से पहले developers imperative DOM code से elements को हिलाते थे, जिससे React का control टूटता था। Portal दूसरे DOM node में render करता है और React का व्यवहार बनाए रखता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Component returns createPortal(children, targetDomNode)
Step 2 → React renders "children" into targetDomNode (for example document.body)
Step 3 → The DOM location changes, but the React tree position stays the same
Step 4 → Props, state and context come from the React parent, as usual
Step 5 → Events bubble through the REACT tree: a click in the portal reaches React parents
Step 6 → When the component unmounts, React removes the portal children from the target node

KEY: moves the DOM, not the React tree. Events and context follow React.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Component लौटाता है createPortal(children, targetDomNode)
Step 2 → React "children" को targetDomNode (जैसे document.body) में render करता है
Step 3 → DOM की जगह बदलती है, पर React tree में जगह वही रहती है
Step 4 → Props, state और context React parent से आते हैं, हमेशा की तरह
Step 5 → Events REACT tree में bubble होते हैं: portal के अंदर का click React parents तक पहुँचता है
Step 6 → Component unmount हो तो React target node से portal children हटा देता है

KEY: DOM को हिलाता है, React tree को नहीं। Events और context React के हिसाब से चलते हैं।
```

---

## 🟡 Real World Example
**Swiggy cart confirmation modal:** The "Clear cart?" modal is triggered from the checkout page, which sits inside a scrollable container with fixed heights. If the modal rendered in place, it would be cut off at the bottom of the screen on mobile. A portal renders the modal into `document.body`, so it covers the full screen with a dark overlay. Its "Yes" button still calls the checkout's `clearCart` function, because the event and the props follow the React tree.

## 🟡 Real Example Hindi mein
**Swiggy cart confirmation modal:** "Cart खाली करें?" modal checkout page से खुलता है, जो एक scrollable container के अंदर है जिसकी height तय है। Modal वहीं render होता तो mobile पर screen के नीचे से कट जाता। Portal modal को `document.body` में render करता है, जिससे वह पूरी screen पर dark overlay के साथ दिखता है। उसका "Yes" बटन अब भी checkout का `clearCart` function call करता है, क्योंकि props और events React tree के हिसाब से चलते हैं।

---

## 💻 Code Example — Basic

```jsx
// Basic portal: a modal is rendered into document.body, but still belongs to the App component
import { useState } from 'react';                // state to open and close the modal
import { createPortal } from 'react-dom';        // portal function from react-dom
import { createRoot } from 'react-dom/client';   // React 18/19 root API

function Modal({ onClose, children }) {          // modal UI: takes content and a close handler
  return createPortal(                           // render the result into a different DOM node
    <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)' }}> {/* full-screen overlay */}
      <div style={{ background: 'white', margin: '20vh auto', padding: 24, width: 300 }}> {/* dialog box */}
        {children}                               {/* content passed by the caller */}
        <button onClick={onClose}>Close</button> {/* calls the parent's close handler */}
      </div>
    </div>,
    document.body                                // the target DOM node (outside the #root div)
  );
}

function App() {
  const [open, setOpen] = useState(false);       // is the modal visible?
  return (
    <div>
      <h1>Checkout</h1>                          {/* normal page content */}
      <button onClick={() => setOpen(true)}>Clear cart</button> {/* opens the modal */}
      {open && (                                 // only render the portal when open
        <Modal onClose={() => setOpen(false)}>   {/* pass a close function down */}
          <p>Clear all items from your cart?</p> {/* modal content */}
        </Modal>
      )}
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />); // the modal lives in document.body
```

## 💻 Code Example — Advanced

```jsx
// Production portal: toast container created once, Escape key, accessibility, safe on the server
import { useState, useEffect, useRef } from 'react';    // hooks for state, effects and refs
import { createPortal } from 'react-dom';                // portal function
import { createRoot } from 'react-dom/client';          // React 18/19 root API

// Toast container: a separate DOM node, created only in the browser (guards against SSR)
function getToastRoot() {
  if (typeof document === 'undefined') return null;     // on the server there is no document
  let node = document.getElementById('toast-root');     // try to find an existing container
  if (!node) {                                          // not found → create it once
    node = document.createElement('div');               // new <div>
    node.id = 'toast-root';                             // give it a stable id
    document.body.appendChild(node);                    // attach it to the page
  }
  return node;                                          // the portal target
}

// Modal with Escape to close, focus management and a labelled dialog for screen readers
function Dialog({ title, onClose, children }) {
  const closeRef = useRef(null);                        // ref to the close button (for focus)

  useEffect(() => {                                     // runs after mount, only in the browser
    function handleKey(event) {                         // called for every key press
      if (event.key === 'Escape') onClose();            // Escape closes the dialog
    }
    document.addEventListener('keydown', handleKey);    // listen on the whole document
    closeRef.current?.focus();                          // move focus into the dialog
    return () => document.removeEventListener('keydown', handleKey); // cleanup on close
  }, [onClose]);                                        // re-subscribe if onClose changes

  const target = getToastRoot();                        // find or create the portal target
  if (!target) return null;                             // server: render nothing (no portal)

  return createPortal(
    <div role="dialog" aria-modal="true" aria-label={title} // accessibility attributes
      style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.4)' }}>
      <div style={{ background: 'white', padding: 20, margin: '15vh auto', width: 320 }}>
        <h2>{title}</h2>                                    {/* dialog heading */}
        {children}                                          {/* caller content */}
        <button ref={closeRef} onClick={onClose}>Close</button> {/* focused on open */}
      </div>
    </div>,
    target                                                  // render into the toast container
  );
}

// Demo: a dialog that opens from a button, closes with Escape or the button
function Checkout() {
  const [open, setOpen] = useState(false);                  // dialog visibility
  const [message, setMessage] = useState('');               // last message from the dialog
  return (
    <div>
      <button onClick={() => setOpen(true)}>Apply coupon</button> {/* open the dialog */}
      <p>{message}</p>                                      {/* shows the result */}
      {open && (
        <Dialog title="Coupon" onClose={() => setOpen(false)}>
          <p>Enter your code: FIRST20</p>                   {/* dialog body */}
          <button onClick={() => { setMessage('FIRST20 applied'); setOpen(false); }}>
            Apply
          </button>
        </Dialog>
      )}
    </div>
  );
}

createRoot(document.getElementById('root')).render(<Checkout />);
```

---

## 🟠 Real App Integration

In Next.js App Router, a modal with a portal must be a **Client Component**. The server cannot reach `document`, so the portal target is checked after mount. This is the pattern for a Razorpay-style confirmation dialog inside a Server Component page.

```jsx
// app/components/Modal.jsx
'use client';                                            // portal needs the browser → client component
import { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';

export default function Modal({ open, onClose, children }) {
  const [mounted, setMounted] = useState(false);         // false on the server and first render
  useEffect(() => { setMounted(true); }, []);            // true only after hydration in the browser
  if (!open || !mounted) return null;                    // nothing to draw yet
  return createPortal(                                   // draw into document.body, outside the page
    <div className="overlay" onClick={onClose}>          {/* click the backdrop to close */}
      <div className="dialog" onClick={e => e.stopPropagation()}> {/* clicks inside do not close */}
        {children}                                       {/* caller content */}
      </div>
    </div>,
    document.body
  );
}
```

```jsx
// app/checkout/page.jsx (Server Component)
import PayNowDialog from './PayNowDialog';               // 'use client' wrapper that uses Modal
export default function Page() {
  return <PayNowDialog />;                               // server renders the page, dialog hydrates in browser
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Rendering a portal to `document.body` during server rendering (in SSR, `document` does not exist)
✅ **Correct:** Only create the portal in the browser (for example inside `useEffect`, or check `typeof document`)

```jsx
// Wrong: crashes on the server, because document is undefined during SSR
function Modal({ children }) {
  return createPortal(children, document.body);   // ❌ ReferenceError on the server
}

// Right: wait until the component is mounted in the browser
function Modal({ children }) {
  const [mounted, setMounted] = useState(false);  // false during server render
  useEffect(() => setMounted(true), []);          // true after mount, in the browser only
  return mounted ? createPortal(children, document.body) : null; // ✅ no document on server
}
```

❌ **Mistake 2:** Expecting a portal to behave like it is in its DOM location (events and CSS inheritance are different)
✅ **Correct:** Remember that React events bubble through the React tree, while CSS and DOM events follow the real DOM

```jsx
// Wrong assumption: the parent div does NOT see a click on the DOM node "by position"
<div onClick={() => console.log('parent')}>
  {createPortal(<button>Click</button>, document.body)}  {/* DOM parent is body */}
</div>
// Clicking the button DOES log 'parent' — React bubbles events through the React tree.
// But a native listener on the real parent (addEventListener on the div) would NOT fire.
```

---

## 🧠 Tricky Interview Question

```jsx
import { createPortal } from 'react-dom';
import { createRoot } from 'react-dom/client';

function App() {
  return (
    <div onClick={() => console.log('parent div clicked')}>      {/* React parent of the portal */}
      <p>Page content</p>
      {createPortal(
        <button onClick={() => console.log('button clicked')}>Open</button>, // inside the portal
        document.body                                                         // outside the div in the DOM
      )}
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);

// Simulate a user click on the portal button after the first render
setTimeout(() => document.querySelector('button').click(), 50);
```
**Answer:** The output is:
```
button clicked
parent div clicked
```
In the DOM the button lives in `document.body`, outside the `div`. React, however, attaches its event handling at the root and dispatches synthetic events through the **React tree**. The portal's React parent is the `div`, so the click bubbles to the `div`'s `onClick` even though the DOM node is not inside it. Native listeners such as `div.addEventListener('click', …)` would not see this click, because they follow the real DOM tree.

---

## ⚫ Interview Questions + Answers

Q1: What is a React portal?
A1: A way to render children into a different DOM node with `createPortal(children, domNode)`, while the component stays in its place in the React tree. Props, state, context and React events keep working as usual.

Q2: Why do modals and tooltips use portals?
A2: They need to escape parent containers that clip content (`overflow: hidden`), create stacking contexts (`z-index`), or change layout. Rendering them into `document.body` avoids those problems.

Q3: Does an event inside a portal bubble to the React parent?
A3: Yes. React events bubble through the React component tree, not the DOM tree. A click inside a portal calls the `onClick` of its React ancestors, even when the DOM node is elsewhere.

Q4: What happens to a portal during server-side rendering?
A4: The server has no `document` object, so `createPortal` with `document.body` cannot run there. Create the portal only in the browser, for example after mount in `useEffect`, or return `null` when `typeof document === 'undefined'`.

Q5: Are portals a good fit for Next.js App Router?
A5: Yes, in a Client Component (`'use client'`). The Server Component renders the page, and the portal runs in the browser after hydration. Keep the `document` access inside an effect or a client-only guard.

---

## 🔷 When to Use + When Not to Use
✅ **Use portals when:**
- A modal, dialog, toast or tooltip must appear above everything else
- A parent has `overflow: hidden` or a stacking context that would clip the child
- You need the UI in a separate DOM node while keeping React state and events

❌ **Avoid portals when:**
- The element is a normal part of the layout (a portal adds complexity without benefit)
- You render during server-side rendering without a browser guard
- You rely on native DOM event bubbling from the portal's visual parent (it will not reach there)

---

## 📊 Visual Diagram

```
  REACT TREE (where the code lives)           DOM TREE (where the nodes end up)

  <App>                                         <body>
   └── <div onClick=…>                            ├── <div id="root">
        ├── <p>Page content</p>                   │     └── <div onClick=…>
        └── Portal ──────────────────────┐        │          └── <p>Page content</p>
             └── <button onClick=…>      │        ├── <div id="toast-root">  ← portal target
                                         │        │     └── <button onClick=…>
                                         │        └── …
                                         └── events bubble up the REACT tree only

  Click on the button:
    1. button onClick          → runs
    2. (React) bubble to div   → div onClick runs  (React tree)
    3. (DOM) div listener      → does NOT run  (button is not inside the div in the DOM)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Portal | Render into another DOM node | दूसरे DOM node में render करना |
| createPortal | Function that creates a portal | Portal बनाने वाला function |
| Target node | DOM element where the portal renders | वह DOM element जहाँ portal render होता है |
| React tree | Component hierarchy in React | React के components का structure |
| Event bubbling | Event moves up to parent elements | Event का parent तक ऊपर जाना |
| Stacking context | CSS layer that controls z-order | CSS की वह layer जो z-order तय करती है |
| SSR | Server-side rendering | Server पर HTML बनाना |
| Overflow hidden | CSS that clips content outside a box | Box के बाहर का content काटने वाला CSS |

---

## ⚡ 3-Line Summary
**English:**
1. `createPortal(children, domNode)` renders children into another DOM node but keeps them in the React tree.
2. Props, state, context and React events follow the React tree, so a click bubbles to React parents.
3. Use portals for modals, tooltips and toasts, and create them only in the browser (never during server rendering).

**Hindi:**
1. `createPortal(children, domNode)` children को किसी दूसरे DOM node में render करता है, पर React tree में रखता है।
2. Props, state, context और React events React tree के हिसाब से चलते हैं, इसलिए click React parents तक bubble होता है।
3. Modals, tooltips और toasts के लिए portal इस्तेमाल करो, और उन्हें सिर्फ browser में बनाओ (server rendering में कभी नहीं)।

---

## ➡️ Next Topic
**68. Error Boundaries and Suspense (logical next concept)** — Render के दौरान होने वाली errors को पकड़ना और data loading के दौरान fallback UI दिखाना। Portals की तरह ये भी React tree के नियमों पर चलते हैं, और ये intermediate React के आगे के बड़े विषय हैं।
