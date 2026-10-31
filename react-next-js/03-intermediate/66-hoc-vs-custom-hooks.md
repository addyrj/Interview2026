# 66. HOC vs Custom Hooks
# हिंदी में: HOC बनाम Custom Hooks — Logic Share करने के दो तरीके

---

## 🔵 Simple Definition (English)
Both **HOCs** and **custom hooks** share reusable logic between components. An **HOC** wraps a whole component and passes data down as props. A **custom hook** is a function whose name starts with `use`, that is called **inside** a component and returns values directly. In modern React, custom hooks are the preferred way to share stateful logic.

## 🔵 सरल परिभाषा (Hindi)
**HOC** और **custom hooks** दोनों components के बीच reusable logic share करते हैं। **HOC** पूरे component को wrap करता है और data को props के रूप में नीचे भेजता है। **Custom hook** एक function है जिसका नाम `use` से शुरू होता है, जो किसी component के **अंदर** call होता है और values सीधे लौटाता है। आज के React में stateful logic share करने का पसंदीदा तरीका custom hooks हैं।

---

## 🔴 Problem it Solves

Both patterns solve the same question: how do we reuse "the same behavior" (window size, auth state, logging) in many components? Before hooks, the only tools were HOCs and render props, and both add wrapper layers, nested JSX, and prop name conflicts. Custom hooks solve this by letting a function call other hooks and return plain values, without creating a new component layer in the tree.

```jsx
// PROBLEM with HOC: wrapping adds a layer and a prop named "width" can collide
const WithWidth = withWindowWidth(Header);   // new component layer
<WithWidth title="Home" />                    // Header receives width from the HOC

// SOLUTION with a hook: call it inside the component, no extra layer
function Header({ title }) {
  const width = useWindowWidth();            // returns the value directly
  return <h1>{title} ({width}px)</h1>;
}
```

## 🔴 यह क्यों बना? (Hindi)
दोनों patterns एक ही सवाल हल करते हैं: "एक ही behavior" (window size, auth state, logging) कई components में कैसे दोबारा इस्तेमाल करें। Hooks से पहले सिर्फ HOC और render props थे, और दोनों में wrapper layers, nested JSX और prop name टकराव होते थे। Custom hooks एक function को दूसरे hooks call करने और सीधी values लौटाने देते हैं, बिना tree में नई layer बनाए।

---

## 🟢 How it Works — Step by Step

```
HOC way:
Step 1 → withWidth(Header) returns a new component
Step 2 → The new component computes width and passes it as a prop
Step 3 → Header receives width as a prop (name chosen by the HOC author)
Step 4 → The tree gets one extra wrapper component

Custom hook way:
Step 1 → useWidth() is a function that uses useState and useEffect
Step 2 → Header calls useWidth() inside its own body
Step 3 → The return value is a plain variable in Header's scope
Step 4 → No extra component layer; each call has its own state
```

## 🟢 कैसे काम करता है? (Hindi)
```
HOC तरीका:
Step 1 → withWidth(Header) एक नया component लौटाता है
Step 2 → नया component width निकालकर उसे prop के रूप में भेजता है
Step 3 → Header को width prop मिलता है (नाम HOC लिखने वाले ने चुना)
Step 4 → Tree में एक extra wrapper component जुड़ता है

Custom hook तरीका:
Step 1 → useWidth() एक function है जो useState और useEffect इस्तेमाल करता है
Step 2 → Header अपने body के अंदर useWidth() call करता है
Step 3 → Return value Header के scope में एक सामान्य variable है
Step 4 → कोई extra component layer नहीं; हर call का अपना state होता है
```

---

## 🟡 Real World Example
**Zomato responsive restaurant grid:** The app needs to know if the screen is "mobile" or "desktop" in the restaurant list, the filter bar and the banner. With a hook (`useIsMobile()`), each component calls it directly and gets a boolean. With an HOC (`withIsMobile`), each component is wrapped and gets a prop, which adds three wrapper layers to the tree and a prop name that can clash with a restaurant field called `isMobile`.

## 🟡 Real Example Hindi mein
**Zomato responsive restaurant grid:** Restaurant list, filter bar और banner को पता होना चाहिए कि screen "mobile" है या "desktop"। Hook (`useIsMobile()`) से हर component सीधा call करता है और boolean पाता है। HOC (`withIsMobile`) से हर component wrap होता है और prop पाता है, जो tree में तीन wrapper layers जोड़ता है, और `isMobile` नाम का prop restaurant के किसी field से टकरा सकता है।

---

## 💻 Code Example — Basic

```jsx
// The same behavior (window width) written as a custom hook — the modern way
import { useState, useEffect } from 'react';     // hooks used inside the custom hook
import { createRoot } from 'react-dom/client';   // React 18/19 root API

// Custom hook: its name starts with "use", so React knows its rules apply
function useWindowWidth() {
  const [width, setWidth] = useState(window.innerWidth); // initial value: current width

  useEffect(() => {                              // subscribe to resize events after mount
    function handleResize() {                    // runs on every window resize
      setWidth(window.innerWidth);               // update the stored width
    }
    window.addEventListener('resize', handleResize); // start listening
    return () => window.removeEventListener('resize', handleResize); // cleanup: stop listening
  }, []);                                        // subscribe once for the component's life

  return width;                                  // return the plain number to the caller
}

// Any component can call the hook directly: no wrapper, no extra props
function Header({ title }) {
  const width = useWindowWidth();                // get the current width
  const label = width < 768 ? 'mobile' : 'desktop'; // decide the layout
  return <h1>{title} — {label} layout ({width}px)</h1>; // show the result
}

createRoot(document.getElementById('root')).render(<Header title="Home" />);
```

## 💻 Code Example — Advanced

```jsx
// Hook vs HOC for the same feature, plus a HOC built ON TOP of the hook (best of both)
import { useState, useEffect, forwardRef } from 'react'; // hooks + forwardRef
import { createRoot } from 'react-dom/client';           // React 18/19 root API

// 1. Core logic lives in ONE custom hook: easy to test, no UI, no wrapper
function useMediaQuery(query) {
  const [matches, setMatches] = useState(false); // false until the browser answers
  useEffect(() => {                              // runs after mount (not during SSR)
    const mql = window.matchMedia(query);        // browser media query object
    setMatches(mql.matches);                     // read the current result
    function onChange(event) {                   // called when the screen crosses the breakpoint
      setMatches(event.matches);                 // store the new result
    }
    mql.addEventListener('change', onChange);    // subscribe to changes
    return () => mql.removeEventListener('change', onChange); // cleanup
  }, [query]);                                   // resubscribe if the query text changes
  return matches;                                // boolean for the component
}

// 2. Same logic as an HOC, implemented USING the hook (the hook does the work)
function withMobileOnly(Component) {
  // forwardRef keeps refs working; the HOC only chooses what to render
  return forwardRef(function WithMobileOnly(props, ref) {
    const isMobile = useMediaQuery('(max-width: 767px)'); // reuse the hook inside the HOC
    if (!isMobile) return null;                  // hide the component on desktop
    return <Component {...props} ref={ref} />;   // show it on mobile
  });
}

// 3. Components that use the hook directly (no wrapper layers)
function FilterBar() {
  const isMobile = useMediaQuery('(max-width: 767px)'); // hook call
  return <nav>{isMobile ? 'Filter (sheet)' : 'Filter (sidebar)'}</nav>; // layout by device
}

// 4. A component that is wrapped by an HOC for "mobile only" content
const MobileBanner = withMobileOnly(function MobileBanner({ text }) {
  return <p>{text}</p>;                          // rendered only on mobile
});

function App() {
  return (
    <div>
      <FilterBar />                              {/* hook version */}
      <MobileBanner text="Get the app for ₹0 delivery" /> {/* HOC version */}
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);
// In jsdom, window.matchMedia is not implemented; in a browser this runs normally.
```

---

## 🟠 Real App Integration

In Next.js, a custom hook that touches `window` must run only in a Client Component, and its initial state must match the server output to avoid hydration mismatches. Start with a safe default (`false`) and read the browser value in an effect.

```jsx
// lib/use-is-mobile.js
'use client';                                            // hooks that use window run in the browser
import { useEffect, useState } from 'react';

export function useIsMobile() {
  const [isMobile, setIsMobile] = useState(false);       // same value on server and first client render
  useEffect(() => {                                      // runs only in the browser, after hydration
    const mql = window.matchMedia('(max-width: 767px)'); // browser media query
    setIsMobile(mql.matches);                            // real value after mount
    const onChange = (e) => setIsMobile(e.matches);      // update on resize across the breakpoint
    mql.addEventListener('change', onChange);
    return () => mql.removeEventListener('change', onChange); // cleanup
  }, []);
  return isMobile;                                       // boolean for the component
}
```

```jsx
// app/components/FilterBar.jsx
'use client';                                            // uses a hook from the client module
import { useIsMobile } from '@/lib/use-is-mobile';

export default function FilterBar() {
  const isMobile = useIsMobile();                        // no wrapper, no extra props
  return <nav>{isMobile ? 'Filter (sheet)' : 'Filter (sidebar)'}</nav>;
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Calling a hook conditionally, inside `if` or a loop
✅ **Correct:** Call hooks at the top level of the component or hook, every time in the same order

```jsx
// Wrong: the hook is called only sometimes → React cannot match state between renders
function Header({ isLoggedIn }) {
  if (isLoggedIn) {
    const user = useUser();                     // ❌ conditional hook call
  }
  return <h1>Header</h1>;
}

// Right: call the hook first, then decide what to do with the result
function Header({ isLoggedIn }) {
  const user = useUser();                       // ✅ always called, same order
  return <h1>{isLoggedIn ? user.name : 'Guest'}</h1>;
}
```

❌ **Mistake 2:** Naming a custom hook without the `use` prefix (React and linters cannot check the rules)
✅ **Correct:** Name every hook with `use` so the lint rules apply

```jsx
// Wrong: no "use" prefix, so the rules of hooks lint check is not applied
function windowWidth() {                        // ❌ looks like a normal function
  const [w, setW] = useState(window.innerWidth); // hook inside a non-hook name
  return w;
}

// Right: the "use" prefix tells React and ESLint this is a hook
function useWindowWidth() {                     // ✅ rules of hooks apply
  const [w, setW] = useState(window.innerWidth);
  return w;
}
```

---

## 🧠 Tricky Interview Question

```jsx
import { useState, useEffect } from 'react';
import { createRoot } from 'react-dom/client';

function useCounter() {                          // custom hook with its own state
  const [n, setN] = useState(0);                 // each call creates a SEPARATE state slot
  return [n, () => setN(x => x + 1)];            // return value and an increment function
}

function App() {
  const [a, incA] = useCounter();                // first call: state A
  const [b, incB] = useCounter();                // second call: state B (independent)

  useEffect(() => {
    incA();                                      // increase A twice
    incA();
  }, []);                                        // runs once after mount

  console.log(a, b);                             // prints the values on each render
  return <p>{a} and {b}</p>;
}

createRoot(document.getElementById('root')).render(<App />);
```
**Answer:** The output is:
```
0 0
2 0
```
Custom hooks share **logic**, not **state**. Each call to `useCounter()` creates its own `useState`, so `a` and `b` are independent. The effect increments `a` twice and never touches `b`, so the first render logs `0 0` and the re-render logs `2 0`. Two hooks calls in one component give two separate state slots, the same way two HOC-wrapped components would each have their own state.

---

## ⚫ Interview Questions + Answers

Q1: What is the main difference between an HOC and a custom hook?
A1: An HOC wraps a component and adds props or a layer to the tree. A custom hook is called inside a component and returns values, without adding a component layer.

Q2: Can custom hooks share state between components?
A2: No. Each call to a custom hook creates its own state. To share state, use Context or a store (topic 61), and the hook can read from that shared source.

Q3: What are the rules of hooks?
A3: Call hooks only at the top level of a function component or another custom hook (not inside loops, conditions or nested functions), and only from React function components or custom hooks. Naming with the `use` prefix lets the ESLint plugin check these rules.

Q4: When is an HOC still the better choice?
A4: When you must wrap a whole component (route guards, layout wrappers), when you cannot change the component's code, or when you need to change what is rendered rather than what data is available. Error boundaries must be classes and cannot be hooks.

Q5: How can a custom hook and an HOC work together?
A5: Put the logic in a hook (for example `useMediaQuery`) so it is testable, then create an HOC that calls the hook and decides what to render (for example hiding a component on desktop). This keeps the logic reusable and the wrapper small.

---

## 🔷 When to Use + When Not to Use
✅ **Use custom hooks when:**
- Several components need the same stateful logic (subscriptions, timers, form state, data fetching)
- You want to keep the component tree flat and readable
- You need to test logic without rendering the UI

❌ **Avoid custom hooks when:**
- The logic is only used in one component (keep it inside that component)
- You need to wrap an entire component to change rendering (an HOC or composition may fit better)
- The hook is so generic it returns many unrelated values (split it into smaller hooks)

---

## 📊 Visual Diagram

```
  HOC approach (wrapper layer added to the tree)

  <WithWidth>              ← HOC component (extra layer)
    └── <Header width=…/>  ← receives the prop
  Tree: 2 levels for one feature

  Hook approach (no extra layer)

  <Header>                 ← calls useWindowWidth() inside its body
    └── (its own JSX)      ← uses the returned number directly
  Tree: 1 level, state lives in Header

  Each call to useWindowWidth() has its own state:
    Header A  → useWindowWidth() → width slot #1
    Header B  → useWindowWidth() → width slot #2 (independent)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| HOC | Function that wraps a component | Component को wrap करने वाला function |
| Custom hook | Function starting with `use` that calls hooks | `use` से शुरू होने वाला, hooks call करने वाला function |
| Wrapper layer | Extra component in the tree | Tree में एक extra component |
| Prop collision | Two sources setting the same prop name | एक ही prop name पर दो स्रोत |
| Rules of hooks | Top-level, same-order hook calls | Hooks हमेशा top-level और एक ही क्रम में |
| Stateful logic | Logic that keeps its own state | अपना state रखने वाला logic |
| Media query | Browser check for screen size | Screen size की browser जाँच |
| Separate state | Each hook call has its own state | हर hook call का अलग state |

---

## ⚡ 3-Line Summary
**English:**
1. HOCs wrap components and add layers; custom hooks are called inside components and return values directly.
2. Prefer custom hooks for shared stateful logic, and use HOCs for route guards or wrapping whole components.
3. Each hook call gets its own state (logic is shared, state is not); never call hooks conditionally.

**Hindi:**
1. HOCs components को wrap करके layers जोड़ते हैं; custom hooks component के अंदर call होकर values सीधे लौटाते हैं।
2. Shared stateful logic के लिए custom hooks चुनो; route guards या पूरे component को wrap करने के लिए HOC।
3. हर hook call का अपना state होता है (logic share होती है, state नहीं); hooks कभी conditionally call मत करो।

---

## ➡️ Next Topic
**67. React Portals** — Component को DOM में उसके parent से बाहर (जैसे `document.body`) render करना, जैसे modals और toasts के लिए। Logic share करने के बाद UI को सही DOM जगह पर भेजना अगला कदम है।
