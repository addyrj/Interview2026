# 50. useLayoutEffect vs useEffect
# हिंदी में: useLayoutEffect बनाम useEffect — Paint से पहले या बाद में चलने वाला Effect

---

## 🔵 Simple Definition (English)
Both hooks run side effects after React updates the DOM. **`useEffect`** runs **after the browser has painted** the screen (asynchronous, does not block painting). **`useLayoutEffect`** runs **after the DOM is updated but before the browser paints** (synchronous, blocks painting), so you can measure or change the layout without the user seeing a flicker.

## 🔵 सरल परिभाषा (Hindi)
दोनों hooks React के DOM update करने के बाद side effects चलाते हैं। **`useEffect`** **browser के screen paint करने के बाद** चलता है (asynchronous, paint को नहीं रोकता)। **`useLayoutEffect`** **DOM update के बाद पर paint से पहले** चलता है (synchronous, paint को रोकता है), इसलिए आप बिना flicker दिखाए layout को measure या बदल सकते हैं।

---

## 🔴 Problem it Solves

Sometimes you need to read the layout (size or position of an element) and then update the UI based on it: a tooltip positioned next to a button, a textarea that grows with its content, restoring a scroll position. If you do this in `useEffect`, the browser paints the first version (tooltip at the wrong spot), then the effect runs, state changes, and a second paint shows the correct version. The user sees a **flicker**. `useLayoutEffect` runs before the first paint, so only the correct frame is ever shown.

```jsx
// PROBLEM with useEffect: visible jump
function Tooltip({ targetRef, children }) {
  const [top, setTop] = useState(0);
  useEffect(() => {
    const rect = targetRef.current.getBoundingClientRect();
    setTop(rect.bottom + 8);              // runs AFTER paint → tooltip first appears at top=0, then jumps
  }, []);
  return <div style={{ position: 'fixed', top }}>{children}</div>;
}

// SOLUTION: useLayoutEffect → position is fixed BEFORE the user sees anything
//   useLayoutEffect(() => { ... setTop(...) }, []);
```

## 🔴 यह क्यों बना? (Hindi)
कभी-कभी आपको layout पढ़ना होता है (किसी element की size या position) और फिर उसी के आधार पर UI बदलना होता है: बटन के पास tooltip की position, content के साथ बढ़ता textarea, scroll position restore करना। अगर आप यह `useEffect` में करें, तो browser पहला version paint कर देता है (tooltip गलत जगह), फिर effect चलता है, state बदलती है, और दूसरा paint सही version दिखाता है। User को **flicker** दिखता है। `useLayoutEffect` पहले paint से पहले चलता है, इसलिए सिर्फ सही frame दिखता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → State/props change → React RENDERS your component (calls the function, no DOM yet)
Step 2 → React COMMITS: updates the real DOM (nodes exist, layout can be measured)
Step 3 → useLayoutEffect cleanups + effects run SYNCHRONOUSLY here
         (if you call setState inside, React re-renders immediately, still before paint)
Step 4 → Browser PAINTS the screen (user sees pixels)
Step 5 → useEffect cleanups + effects run (usually right after paint; async)
         (note: after a click or other discrete event, React may flush useEffect early,
          but it is still not guaranteed to be before paint)

TIMELINE
  render ─▶ commit DOM ─▶ useLayoutEffect ─▶ PAINT ─▶ useEffect
                          (blocks paint)     👁       (non-blocking)

DEFAULT: use useEffect. Switch to useLayoutEffect only if you SEE a flicker or need to measure the DOM before paint.
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → State/props बदलते हैं → React आपका component RENDER करता है (function चलता है, DOM अभी नहीं)
Step 2 → React COMMIT करता है: असली DOM update होता है (nodes मौजूद हैं, layout measure हो सकता है)
Step 3 → useLayoutEffect की cleanups और effects यहीं SYNCHRONOUSLY चलते हैं
         (अंदर setState करें तो React तुरंत re-render करता है, फिर भी paint से पहले)
Step 4 → Browser स्क्रीन PAINT करता है (user को pixels दिखते हैं)
Step 5 → useEffect की cleanups और effects चलते हैं (आम तौर पर paint के ठीक बाद; async)
         (नोट: click जैसे discrete event के बाद React useEffect को जल्दी flush कर सकता है,
          पर paint से पहले होने की गारंटी फिर भी नहीं)

TIMELINE
  render ─▶ commit DOM ─▶ useLayoutEffect ─▶ PAINT ─▶ useEffect
                          (paint रोकता है)     👁       (नहीं रोकता)

DEFAULT: useEffect इस्तेमाल करो। सिर्फ तब useLayoutEffect लो जब flicker दिखे या paint से पहले DOM measure करना हो।
```

---

## 🟡 Real World Example
**Zomato dish tooltip and Swiggy chat:** On a Zomato menu, hovering the "i" icon shows an allergen tooltip. The tooltip must sit below the icon, but if there is no space it flips above. That decision needs the tooltip's measured height, so the component measures it in `useLayoutEffect` and positions it before the first paint. In the Swiggy support chat, the message list scrolls to the bottom when a new message arrives; doing it in `useLayoutEffect` avoids the visible jump from top to bottom. Logging analytics, fetching data and subscribing to events stay in `useEffect`.

## 🟡 Real Example Hindi mein
**Zomato dish tooltip और Swiggy chat:** Zomato menu में "i" icon पर hover करने से allergen tooltip दिखता है। Tooltip icon के नीचे होना चाहिए, पर जगह न हो तो ऊपर पलटना चाहिए। इस फ़ैसले के लिए tooltip की नापी हुई height चाहिए, इसलिए component उसे `useLayoutEffect` में measure करके पहले paint से पहले position देता है। Swiggy support chat में नया message आने पर list नीचे scroll होती है; यह `useLayoutEffect` में करने से ऊपर से नीचे कूदता दिखाई नहीं देता। Analytics log करना, data fetch करना और events subscribe करना `useEffect` में ही रहते हैं।

---

## 💻 Code Example — Basic

```jsx
// Compare the two hooks measuring the same box: look for the flicker with useEffect
import { useState, useEffect, useLayoutEffect, useRef } from 'react';
import { createRoot } from 'react-dom/client';

function WithUseEffect() {
  const ref = useRef(null);                       // points to the DOM box
  const [width, setWidth] = useState(0);          // measured width

  useEffect(() => {
    setWidth(ref.current.getBoundingClientRect().width);   // runs AFTER paint → 0 is painted first
  }, []);

  return <div ref={ref} style={{ width: 200 }}>useEffect measured: {width}px</div>;
}

function WithUseLayoutEffect() {
  const ref = useRef(null);
  const [width, setWidth] = useState(0);

  useLayoutEffect(() => {
    setWidth(ref.current.getBoundingClientRect().width);   // runs BEFORE paint → user never sees 0
  }, []);

  return <div ref={ref} style={{ width: 200 }}>useLayoutEffect measured: {width}px</div>;
}

// Order of logs on mount
function Order() {
  console.log('1. render');
  useEffect(() => console.log('3. useEffect (after paint)'), []);
  useLayoutEffect(() => console.log('2. useLayoutEffect (before paint)'), []);
  return null;
}

createRoot(document.getElementById('root')).render(
  <>
    <WithUseEffect />
    <WithUseLayoutEffect />
    <Order />
  </>
);
```

## 💻 Code Example — Advanced

```jsx
// Real world: a smart tooltip (measure + flip) and a chat list that keeps scroll position
import { useState, useRef, useLayoutEffect, useEffect } from 'react';
import { createPortal } from 'react-dom';

// ---------- Tooltip: measure the tooltip and decide above/below before paint ----------
export function Tooltip({ anchorRef, text, open }) {
  const tipRef = useRef(null);
  const [pos, setPos] = useState({ top: 0, left: 0 });   // starts off-screen-ish, corrected before paint

  useLayoutEffect(() => {
    if (!open) return;                                   // nothing to measure while closed
    const anchor = anchorRef.current.getBoundingClientRect();
    const tip = tipRef.current.getBoundingClientRect();  // reading layout forces a reflow (fine, once)
    const spaceBelow = window.innerHeight - anchor.bottom;
    const top = spaceBelow > tip.height + 8
      ? anchor.bottom + 8                                // fits below
      : anchor.top - tip.height - 8;                     // flip above
    setPos({ top, left: anchor.left });                  // sync re-render BEFORE the browser paints
  }, [open, text, anchorRef]);

  if (!open) return null;
  return createPortal(                                    // render outside parent overflow
    <div ref={tipRef} role="tooltip"
         style={{ position: 'fixed', top: pos.top, left: pos.left, background: '#222', color: '#fff', padding: 6 }}>
      {text}
    </div>,
    document.body
  );
}

// ---------- Chat: keep the view pinned to the bottom when messages are added ----------
export function ChatList({ messages }) {
  const listRef = useRef(null);

  useLayoutEffect(() => {
    const el = listRef.current;
    el.scrollTop = el.scrollHeight;                      // jump to bottom before paint → no visible scroll jump
  }, [messages.length]);

  // Non-visual work stays in useEffect: it must not block painting
  useEffect(() => {
    document.title = `(${messages.length}) Support chat`;  // title update is not a layout concern
  }, [messages.length]);

  return (
    <ul ref={listRef} style={{ height: 200, overflowY: 'auto' }}>
      {messages.map((m) => <li key={m.id}>{m.text}</li>)}
    </ul>
  );
}
```

---

## 🟠 Real App Integration

This is the topic where Next.js matters the most. Components also render on the **server**, where there is no DOM and no layout, and **`useLayoutEffect` does nothing on the server**. Older React versions (≤ 18) printed a warning: "useLayoutEffect does nothing on the server". React 19 removed that warning, but the logic is still the same: the layout effect runs only in the browser, after hydration, so the first server HTML cannot contain its result. Practical rules:

1. Use `useLayoutEffect` only in Client Components (`'use client'`).
2. Do not rely on it to change what the server HTML contains; it will flash the server version for a moment until the browser runs the effect (hydration happens first).
3. For a cross-environment hook, the common pattern is an isomorphic layout effect.

```jsx
// lib/useIsomorphicLayoutEffect.js — works in React 17/18/19 and in SSR
import { useEffect, useLayoutEffect } from 'react';

// On the server `window` is undefined → fall back to useEffect (which also does not run on the server,
// but avoids the old warning). In the browser use the real useLayoutEffect.
export const useIsomorphicLayoutEffect =
  typeof window !== 'undefined' ? useLayoutEffect : useEffect;
```

```jsx
// app/components/AutoGrowTextarea.jsx — Client Component
'use client';
import { useRef, useState } from 'react';
import { useIsomorphicLayoutEffect } from '@/lib/useIsomorphicLayoutEffect';

export default function AutoGrowTextarea() {
  const ref = useRef(null);
  const [value, setValue] = useState('');

  useIsomorphicLayoutEffect(() => {
    const el = ref.current;
    el.style.height = 'auto';                         // reset first, so it can shrink
    el.style.height = el.scrollHeight + 'px';         // grow to fit before paint → no flicker
  }, [value]);

  return <textarea ref={ref} value={value} onChange={(e) => setValue(e.target.value)} rows={1} />;
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using `useLayoutEffect` for everything (data fetching, logging, subscriptions)
✅ **Correct:** Default to `useEffect`; use the layout version only for DOM measurement and mutation that must happen before paint

```jsx
// Wrong: heavy sync work blocks the first paint → slower, janky page
useLayoutEffect(() => {
  fetch('/api/orders').then((r) => r.json()).then(setOrders);   // ❌ no need to block paint
  heavyAnalytics();                                              // ❌ blocks painting
}, []);

// Right
useEffect(() => {
  fetch('/api/orders').then((r) => r.json()).then(setOrders);   // ✅ after paint
}, []);
```

❌ **Mistake 2:** Using `useLayoutEffect` in a Server Component, or expecting it to affect server HTML
✅ **Correct:** Add `'use client'`, and design the server output to be acceptable on its own

```jsx
// Wrong: Server Components cannot use hooks at all
// app/page.jsx (no 'use client')
export default function Page() {
  useLayoutEffect(() => {});            // ❌ error: hooks are only available in Client Components
  return null;
}

// Right: move it into a Client Component file that starts with 'use client'
```

❌ **Mistake 3:** Forgetting that setState inside `useLayoutEffect` blocks paint, causing infinite loops
✅ **Correct:** Guard the update and use proper dependencies

```jsx
// Wrong: runs on every render and always sets a NEW object → endless synchronous loop
useLayoutEffect(() => {
  setSize({ w: ref.current.offsetWidth });       // ❌ new object every time, no deps
});

// Right
useLayoutEffect(() => {
  const w = ref.current.offsetWidth;
  setSize((prev) => (prev.w === w ? prev : { w }));   // ✅ same object when unchanged → bail out
}, []);
```

---

## 🧠 Tricky Interview Question

```jsx
function App() {
  const [n, setN] = useState(0);

  console.log('render', n);

  useEffect(() => {
    console.log('effect', n);
    return () => console.log('effect cleanup', n);
  }, [n]);

  useLayoutEffect(() => {
    console.log('layout effect', n);
    return () => console.log('layout cleanup', n);
  }, [n]);

  return <button onClick={() => setN(n + 1)}>{n}</button>;
}
```
Question: What is logged on mount, and then after one click?

**Answer:**
```
// Mount (StrictMode off):
render 0
layout effect 0
effect 0

// After one click:
render 1
layout cleanup 0
layout effect 1
effect cleanup 0
effect 1
```
Order: render, then layout effects (cleanup of the previous, then new), then — after paint — passive effects (cleanup of the previous, then new). In a real browser the screen paints between `layout effect` and `effect cleanup`. (With StrictMode in development, you would additionally see the extra render and the setup, cleanup, setup cycle.)

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `useEffect` and `useLayoutEffect`?
A1: Timing. `useLayoutEffect` runs synchronously after DOM mutations but before the browser paints, so it blocks painting. `useEffect` runs after paint, asynchronously. Both run after render and share the same API (effect, cleanup, dependencies).

Q2: When would you choose `useLayoutEffect`?
A2: When you must read layout (`getBoundingClientRect`, `scrollHeight`, `offsetWidth`) and synchronously update DOM or state before the user sees a frame: tooltips and popovers positioning, auto-resizing textareas, scroll restoration, animations that start from a measured size. Use it when you can actually see a flicker with `useEffect`.

Q3: Why can overusing `useLayoutEffect` hurt performance?
A3: It runs before paint, so slow code inside it delays the first visible frame, which hurts metrics like INP and perceived speed. `useEffect` lets the browser show the UI first.

Q4: What problem does `useLayoutEffect` cause with SSR/Next.js?
A4: It cannot run on the server, since there is no DOM. React ≤ 18 warned about it on the server. Use it only in Client Components, and use an isomorphic layout effect helper for shared code. The server HTML will not contain what the effect computes, so the first paint may show the unmeasured version.

Q5: Does `useEffect` always run after the browser paints?
A5: Usually, but not guaranteed. React may flush passive effects earlier (for example, before the next render, or synchronously after a discrete user event like a click). Do not depend on "after paint" for correctness; depend on it only as a performance hint.

---

## 🔷 When to Use + When Not to Use
✅ **Use `useLayoutEffect` when:**
- You measure DOM size/position and update UI before the user can see it
- You see a flicker or "jump" with `useEffect`
- You need to keep scroll position or focus stable across a DOM change

❌ **Avoid `useLayoutEffect` when:**
- You fetch data, subscribe to events, log analytics, or set timers (`useEffect` is right)
- The work is slow (it blocks the first frame)
- The code runs in a Server Component, or the result must appear in the server HTML

---

## 📊 Visual Diagram

```
  setState / props change
          │
          ▼
   ┌─────────────┐
   │   RENDER    │  your component function runs (pure, no DOM access)
   └──────┬──────┘
          ▼
   ┌─────────────┐
   │ COMMIT DOM  │  React updates real DOM nodes
   └──────┬──────┘
          ▼
   ┌─────────────────────┐
   │  useLayoutEffect    │  ◀── sync; can measure + setState; browser is WAITING
   └──────┬──────────────┘       (if setState here → re-render → layout effect again, still no paint)
          ▼
   ┌─────────────┐
   │   PAINT 👁   │  user sees pixels
   └──────┬──────┘
          ▼
   ┌─────────────────────┐
   │     useEffect       │  ◀── async; fetch, subscribe, log; does not block UI
   └─────────────────────┘

  useEffect + setState to fix layout  →  frame 1 (wrong) ➜ frame 2 (right)  = FLICKER
  useLayoutEffect + setState          →  only the right frame is painted
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `useEffect` | Effect that runs after paint | Paint के बाद चलने वाला effect |
| `useLayoutEffect` | Effect that runs before paint | Paint से पहले चलने वाला effect |
| Paint | Browser draws pixels on screen | Browser का स्क्रीन पर pixels बनाना |
| Commit | React applies changes to the DOM | React का DOM में बदलाव लगाना |
| Flicker | Brief wrong frame shown to user | User को दिखने वाला पल भर का गलत frame |
| Layout measurement | Reading size/position of elements | Elements की size/position पढ़ना |
| Passive effect | Another name for `useEffect` | `useEffect` का दूसरा नाम |
| Isomorphic | Works on both server and browser | Server और browser दोनों पर चलने वाला |

---

## ⚡ 3-Line Summary
**English:**
1. `useLayoutEffect` runs after the DOM update but before paint (blocking); `useEffect` runs after paint (non-blocking).
2. Default to `useEffect`; use `useLayoutEffect` only to measure/adjust layout and avoid flicker.
3. It does not run on the server, so use it in Client Components or via an isomorphic helper in Next.js.

**Hindi:**
1. `useLayoutEffect` DOM update के बाद पर paint से पहले चलता है (रोकता है); `useEffect` paint के बाद चलता है (नहीं रोकता)।
2. डिफ़ॉल्ट `useEffect` रखो; सिर्फ layout measure/adjust करके flicker रोकने के लिए `useLayoutEffect` लो।
3. यह server पर नहीं चलता, इसलिए Next.js में Client Components में या isomorphic helper से इस्तेमाल करो।

---

## ➡️ Next Topic
**51. useId Hook** — Effects का timing समझने के बाद `useId` सीखो, जो SSR और hydration में सुरक्षित unique IDs देता है, खासकर forms और accessibility के लिए.
