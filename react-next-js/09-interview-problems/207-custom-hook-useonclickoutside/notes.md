# 207. Build Custom Hook — useOnClickOutside
# हिंदी में: Custom Hook — useOnClickOutside बनाना

> Code: [useOnClickOutside.js](./useOnClickOutside.js) (complete, tested with jsdom: inside click ignored, outside click calls handler)

---

## 🔵 Simple Definition (English)
**useOnClickOutside** is a custom hook that runs a function when the user clicks or touches anywhere outside a given element. It is used to close dropdowns, menus, popovers and modals.

## 🔵 सरल परिभाषा (Hindi)
**useOnClickOutside** एक custom hook है जो user के किसी element के बाहर click या touch करने पर एक function चलाता है। इसका इस्तेमाल dropdown, menu, popover और modal बंद करने के लिए होता है।

---

## 🔴 Problem it Solves
React gives you events for clicks **on** an element, but not for clicks **outside** it. Without a hook, each component adds `document.addEventListener`, forgets to remove it (memory leak), or uses a stale callback. The hook centralises the listener, cleanup and ref check.

## 🔴 यह क्यों बना? (Hindi)
React किसी element **पर** click के events देता है, पर उसके **बाहर** click का event नहीं। Hook के बिना हर component `document.addEventListener` लगाता है, उसे हटाना भूल जाता है (memory leak), या पुराना callback इस्तेमाल करता है। Hook listener, cleanup और ref जाँच एक जगह रखता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → The component attaches a ref to the element to protect (ref.current = DOM node)
Step 2 → The hook adds ONE mousedown (and touchstart) listener on document
Step 3 → On each event: if ref.current contains event.target → click was inside → ignore
Step 4 → Otherwise call the latest handler (the user closes the menu)
Step 5 → The handler is stored in a ref, so changing the callback never re-subscribes
Step 6 → Cleanup removes both listeners on unmount

Re-render: the hook itself causes none. The handler usually calls setOpen(false), which
re-renders the component once. Listener is attached once (deps [ref]) and not on every render.
Performance: one document listener per hook instance; negligible. Many open menus at once?
Share a single listener at the app level.
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Component उस element पर ref लगाता है जिसे बचाना है (ref.current = DOM node)
Step 2 → Hook document पर एक mousedown (और touchstart) listener जोड़ता है
Step 3 → हर event पर: अगर ref.current में event.target शामिल है → click अंदर था → अनदेखा करो
Step 4 → वरना सबसे नया handler बुलाओ (user menu बंद करता है)
Step 5 → Handler ref में रखा जाता है, इसलिए callback बदलने पर listener दोबारा नहीं लगता
Step 6 → Unmount पर cleanup दोनों listeners हटाता है

Re-render: Hook खुद कोई re-render नहीं करता। Handler आमतौर पर setOpen(false) बुलाता है, जिससे
component एक बार re-render होता है। Listener एक बार लगता है (deps [ref]), हर render पर नहीं।
Performance: हर hook पर एक document listener; नगण्य। बहुत सारे menus एक साथ खुले हों तो
app स्तर पर एक ही listener share करो।
```

---

## 🟡 Real World Example
**Flipkart / Amazon account dropdown:** hover or tap "Account" and a menu opens. Click anywhere else on the page and it closes. Click a link inside the menu and it should not close before navigating. The same behaviour is needed for city selectors, filters and notification panels.

## 🟡 Real Example Hindi mein
**Flipkart / Amazon account dropdown:** "Account" पर hover या tap करो तो menu खुलता है। Page पर कहीं और click करो तो बंद हो जाता है। Menu के अंदर link पर click करो तो navigate होने से पहले बंद नहीं होना चाहिए। यही व्यवहार city selector, filters और notification panels में चाहिए।

---

## 💻 Code Example — Basic

```jsx
// Basic: close a dropdown when clicking outside (logic inline, no hook yet)
import { useState, useEffect, useRef } from 'react';        // hooks
import { createRoot } from 'react-dom/client';              // root API

function Dropdown() {
  const [open, setOpen] = useState(false);                  // menu visibility
  const ref = useRef(null);                                 // will point to the wrapper div

  useEffect(() => {
    const onDown = (e) => {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false); // outside → close
    };
    document.addEventListener('mousedown', onDown);         // listen on the whole page
    return () => document.removeEventListener('mousedown', onDown); // cleanup
  }, []);

  return (
    <div ref={ref}>
      <button onClick={() => setOpen((o) => !o)}>Account</button>
      {open && <ul><li>Orders</li><li>Logout</li></ul>}
    </div>
  );
}

createRoot(document.getElementById('root')).render(<Dropdown />);
```

## 💻 Code Example — Advanced

```jsx
// Reusable hook (useOnClickOutside.js) + a modal that uses it with Escape key support
import { useEffect, useRef, useState } from 'react';

export function useOnClickOutside(ref, handler) {
  const handlerRef = useRef(handler);                       // latest handler without re-subscribing
  useEffect(() => { handlerRef.current = handler; });       // update after every render

  useEffect(() => {
    const listener = (event) => {
      const el = ref.current;
      if (!el || el.contains(event.target)) return;         // inside or unmounted: ignore
      handlerRef.current(event);                            // outside: notify
    };
    document.addEventListener('mousedown', listener);
    document.addEventListener('touchstart', listener);      // touch devices
    return () => {
      document.removeEventListener('mousedown', listener);
      document.removeEventListener('touchstart', listener);
    };
  }, [ref]);                                                // ref object never changes
}

function Modal({ onClose, children }) {
  const ref = useRef(null);
  useOnClickOutside(ref, onClose);                          // click on backdrop closes
  useEffect(() => {
    const onKey = (e) => e.key === 'Escape' && onClose();   // keyboard users can close too
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, [onClose]);
  return (
    <div className="backdrop">
      <div ref={ref} role="dialog" aria-modal="true">{children}</div>
    </div>
  );
}
```

---

## 🟠 Next.js Connection
The hook uses `document` and refs, so any component using it must be a Client Component (`'use client'`). Keep the Server Component page static and import only the small interactive menu as a client island. The `document` access is inside `useEffect`, which never runs on the server, so there is no SSR crash.

```jsx
// app/components/AccountMenu.jsx
'use client';                                              // hooks + DOM listeners
import { useRef, useState } from 'react';
import { useOnClickOutside } from '@/hooks/useOnClickOutside';

export default function AccountMenu({ children }) {         // children can be Server Components
  const ref = useRef(null);
  const [open, setOpen] = useState(false);
  useOnClickOutside(ref, () => setOpen(false));
  return (
    <div ref={ref}>
      <button onClick={() => setOpen((o) => !o)}>Account</button>
      {open && <nav>{children}</nav>}                       {/* server-rendered links passed in */}
    </div>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Not removing the listener
✅ **Correct:** Return a cleanup function

```jsx
// Wrong: every mount adds another listener (leak, handlers on unmounted components)
useEffect(() => { document.addEventListener('mousedown', fn); }, []);
// Right
useEffect(() => { document.addEventListener('mousedown', fn); return () => document.removeEventListener('mousedown', fn); }, []);
```

❌ **Mistake 2:** Putting `handler` in the dependency array (re-subscribes every render with an inline arrow)
✅ **Correct:** Keep the latest handler in a ref

```jsx
// Wrong: [ref, handler] → remove/add listeners on every render
// Right: handlerRef.current = handler; deps [ref]
```

❌ **Mistake 3:** Using only `click` when the clicked element can disappear
✅ **Correct:** Use `mousedown` and `touchstart`

```jsx
// Wrong: a button inside the menu removes itself on click; by the time the document
// click listener runs, event.target is no longer inside ref → menu closes wrongly
// Right: mousedown fires before the click handler changes the DOM
```

---

## 🧠 Tricky Interview Question

```jsx
function Menu() {
  const ref = useRef(null);
  const [open, setOpen] = useState(false);
  useOnClickOutside(ref, () => setOpen(false));
  return (
    <div>
      <button onClick={() => setOpen(true)}>Open</button>   {/* outside the ref! */}
      {open && <ul ref={ref}><li>Item</li></ul>}
    </div>
  );
}
```
**Answer:** The menu does not stay open when you click "Open", or flickers. The "Open" button is **outside** the element with the ref, so pressing it is an "outside click". `mousedown` fires first and calls `setOpen(false)`, then `click` calls `setOpen(true)`. Because mousedown happens before click, the final state is usually open, but when the menu is already open, clicking the button closes it and immediately reopens it, so the toggle never works. Fix: put the ref on a wrapper that contains both the button and the menu.

---

## ⚫ Interview Questions + Answers

Q1: How does the hook decide the click was outside?
A1: `ref.current.contains(event.target)` is false. `contains` checks whether the target is the element or one of its descendants.

Q2: Why `mousedown` instead of `click`?
A2: It fires earlier, before other handlers change the DOM. With `click`, an element removed during the click can make `contains` return false, so inside clicks look like outside clicks. Also add `touchstart` for touch devices.

Q3: Why store the handler in a ref?
A3: Callers usually pass an inline arrow function that changes every render. Keeping the latest one in a ref lets the document listener stay attached once, and still call fresh code with current state.

Q4: Do portals (modals rendered with `createPortal`) break this hook?
A4: Yes. A portal's DOM is outside the ref's DOM subtree, so clicks in it look outside, even though React events bubble through the React tree. Include both refs, or check `event.target.closest('[data-portal]')`.

Q5: How do you also support the Escape key and focus trapping?
A5: Add a `keydown` listener for Escape, return focus to the trigger on close, and trap focus inside dialogs. Libraries like Radix UI or the native `<dialog>` element handle this for you.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- Closing dropdowns, popovers, tooltips, autocomplete lists
- Modal backdrops where clicking outside should dismiss

❌ **Avoid when:**
- The dialog must not be dismissed accidentally (payment confirmation)
- You can use the native `<dialog>` or a library that already handles it

---

## 📊 Visual Diagram

```
  document ── mousedown ──►  listener(event)
                                 │
          ref.current.contains(event.target)?
                  │ yes                     │ no
                  ▼                         ▼
              ignore (inside)       handlerRef.current(event) → setOpen(false)

  ┌── wrapper (ref) ───────┐
  │ [Account ▾]            │   click here  = inside
  │  ├ Orders              │
  │  └ Logout              │
  └────────────────────────┘   click anywhere else = outside → close
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ref | Holds a DOM node across renders | Renders के बीच DOM node पकड़ता है |
| contains() | DOM method: is node inside element | क्या node element के अंदर है |
| event.target | Element that was actually clicked | जिस element पर असल click हुआ |
| mousedown | Fires when the button is pressed | Button दबते ही fire होता है |
| Portal | Renders children outside the parent DOM | Children को parent DOM के बाहर render करना |
| Memory leak | Listeners never removed | Listeners का कभी न हटना |
| Client island | Small interactive Client Component | छोटा interactive Client Component |

---

## ⚡ 3-Line Summary
**English:**
1. Attach one `mousedown` and `touchstart` listener to `document` and call the handler when `ref.contains(target)` is false.
2. Keep the handler in a ref so the listener is added once, and always remove it in cleanup.
3. In Next.js it must live in a Client Component; keep surrounding content on the server.

**Hindi:**
1. `document` पर एक `mousedown` और `touchstart` listener लगाओ और `ref.contains(target)` false होने पर handler बुलाओ।
2. Handler को ref में रखो ताकि listener एक बार लगे, और cleanup में उसे हमेशा हटाओ।
3. Next.js में इसे Client Component में रखना होगा; आसपास का content server पर रखो।

---

## ➡️ Next Topic
**208. Build Custom Hook — useWindowSize** — अब resize events, SSR safety और hydration की practice: responsive logic के लिए window का size track करना।
