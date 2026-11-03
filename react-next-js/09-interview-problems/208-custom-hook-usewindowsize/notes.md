# 208. Build Custom Hook — useWindowSize
# हिंदी में: Custom Hook बनाओ — useWindowSize

Code: [useWindowSize.js](./useWindowSize.js) (complete working implementation, SSR safe, throttled)

---

## 🔵 Simple Definition (English)
**useWindowSize** is a custom hook that returns the current browser window `width` and `height` and updates them when the window is resized. It adds the resize listener on mount and removes it on unmount.

## 🔵 सरल परिभाषा (Hindi)
**useWindowSize** एक custom hook है जो browser window की मौजूदा `width` और `height` लौटाता है और window resize होने पर उन्हें update करता है। यह mount पर resize listener जोड़ता है और unmount पर हटा देता है।

---

## 🔴 Problem it Solves

Components often need to know the screen size in JavaScript: show a bottom sheet on mobile, a sidebar on desktop, a different number of columns. CSS media queries cover styling, but not logic. Without a hook, every component copies the same `addEventListener('resize')` code and often forgets the cleanup, which causes memory leaks. Also, reading `window` during render crashes on the server (Next.js) because `window` does not exist there.

## 🔴 यह क्यों बना? (Hindi)
Components को अक्सर JavaScript में screen size जानना पड़ता है: mobile पर bottom sheet, desktop पर sidebar, अलग columns की संख्या। CSS media queries styling संभालती हैं, logic नहीं। Hook के बिना हर component वही `addEventListener('resize')` code कॉपी करता है और cleanup भूल जाता है, जिससे memory leak होता है। साथ ही, render के दौरान `window` पढ़ने पर server (Next.js) पर crash होता है क्योंकि वहाँ `window` नहीं होता।

---

## 🟢 How it Works — Step by Step

```
Step 1 → useState starts with { width: undefined, height: undefined }
         (same on server and on the first client render, so hydration matches)
Step 2 → useEffect runs only in the browser, after the first paint
Step 3 → Inside the effect, read window.innerWidth / innerHeight and set state
Step 4 → Add a 'resize' listener; it schedules ONE update per throttle window
Step 5 → Cleanup function removes the listener and clears any pending timer
Step 6 → Component re-renders with the new size; callers read { width, height }
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → useState { width: undefined, height: undefined } से शुरू होता है
         (server और पहले client render में एक जैसा, इसलिए hydration match होता है)
Step 2 → useEffect सिर्फ browser में, पहले paint के बाद चलता है
Step 3 → Effect के अंदर window.innerWidth / innerHeight पढ़कर state set करो
Step 4 → 'resize' listener जोड़ो; वह हर throttle window में सिर्फ एक update schedule करता है
Step 5 → Cleanup function listener हटाता है और pending timer clear करता है
Step 6 → Component नई size के साथ re-render होता है; caller { width, height } पढ़ता है
```

---

## 🟡 Real World Example
**Flipkart / Amazon product grid:** On a phone the grid shows 2 columns and a filter button that opens a drawer. On a laptop it shows 4 columns and a permanent filter sidebar. The component uses `useWindowSize` to decide which layout (and which JavaScript, such as the drawer) to render. Resizing a desktop browser window changes the layout live.

## 🟡 Real Example Hindi mein
**Flipkart / Amazon product grid:** फ़ोन पर grid में 2 columns और एक filter button होता है जो drawer खोलता है। Laptop पर 4 columns और स्थायी filter sidebar। Component `useWindowSize` से तय करता है कि कौन सा layout (और कौन सा JavaScript, जैसे drawer) render करना है। Desktop browser window का size बदलने पर layout तुरंत बदल जाता है।

---

## 💻 Code Example — Basic

```jsx
// Basic version: no throttle, no SSR care, easiest to understand
import { useState, useEffect } from 'react';             // hooks
import { createRoot } from 'react-dom/client';            // root API

function useWindowSizeBasic() {
  const [size, setSize] = useState({ width: 0, height: 0 }); // 0 until measured

  useEffect(() => {
    const onResize = () =>
      setSize({ width: window.innerWidth, height: window.innerHeight }); // read current size
    onResize();                                           // set the initial size
    window.addEventListener('resize', onResize);          // listen for changes
    return () => window.removeEventListener('resize', onResize); // cleanup on unmount
  }, []);                                                 // [] = subscribe once

  return size;                                            // { width, height }
}

function App() {
  const { width, height } = useWindowSizeBasic();         // use the hook
  return <p>{width} x {height}</p>;                       // shows live size
}

createRoot(document.getElementById('root')).render(<App />);
```

## 💻 Code Example — Advanced

This is the file [useWindowSize.js](./useWindowSize.js): SSR safe, throttled, and fully cleaned up.

```jsx
// useWindowSize: current window width/height, SSR safe, listener cleaned up, optional throttle
import { useState, useEffect } from 'react';

export function useWindowSize(throttleMs = 100) {
  // undefined on the server AND on the first client render, so hydration matches
  const [size, setSize] = useState({ width: undefined, height: undefined });

  useEffect(() => {
    let timer = null;                                      // pending throttled update
    const update = () => {
      timer = null;                                        // allow the next schedule
      setSize({ width: window.innerWidth, height: window.innerHeight });
    };
    const onResize = () => {
      if (timer === null) timer = setTimeout(update, throttleMs); // at most one update per window
    };

    update();                                              // initial measurement after mount
    window.addEventListener('resize', onResize);
    return () => {
      window.removeEventListener('resize', onResize);      // remove listener
      if (timer !== null) clearTimeout(timer);             // remove pending timer
    };
  }, [throttleMs]);                                        // re-subscribe only if the delay changes

  return size;
}

// Usage in a component
function ProductGrid() {
  const { width } = useWindowSize(150);                    // throttled to ~6 updates/second
  const isMobile = width !== undefined && width < 768;     // guard the undefined first render
  return <div>{isMobile ? <MobileFilters /> : <Sidebar />}</div>;
}
function MobileFilters() { return <button>Filters</button>; }
function Sidebar() { return <aside>Filters</aside>; }
```

Verified by script in jsdom: the hook reports `window.innerWidth` after mount, and updates to 500 after setting the width and dispatching a `resize` event.

---

## 🟠 Next.js Connection

In Next.js the component is first rendered on the server where there is no `window`. That is why the hook starts with `undefined` and reads `window` only inside `useEffect` (effects never run on the server). The hook must live in a Client Component.

```jsx
// app/components/ResponsiveNav.jsx
'use client';                                              // uses hooks, so it is a Client Component
import { useWindowSize } from '@/hooks/useWindowSize';     // the hook above

export default function ResponsiveNav() {
  const { width } = useWindowSize();
  if (width === undefined) return <nav aria-busy="true" />; // server + first render: neutral markup
  return width < 768 ? <button>Menu</button> : <nav>Home | Orders | Offers</nav>;
}
```

If you read `window.innerWidth` directly in `useState(() => window.innerWidth)` Next.js throws "window is not defined" on the server, or you get a hydration mismatch. For layout that only changes styling, prefer CSS media queries: they cost no JavaScript and cause no layout flash.

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Forgetting to remove the listener
✅ **Correct:** Return a cleanup function from `useEffect`

```jsx
// Wrong: every mount adds one more listener that is never removed (leak)
useEffect(() => { window.addEventListener('resize', onResize); }, []);

// Right
useEffect(() => {
  window.addEventListener('resize', onResize);
  return () => window.removeEventListener('resize', onResize);
}, []);
```

❌ **Mistake 2:** Reading `window` during render (breaks SSR)
✅ **Correct:** Read it inside `useEffect`

```jsx
// Wrong: ReferenceError: window is not defined on the Next.js server
const [width] = useState(window.innerWidth);

// Right: undefined first, real value after mount
const [size, setSize] = useState({ width: undefined, height: undefined });
useEffect(() => setSize({ width: window.innerWidth, height: window.innerHeight }), []);
```

❌ **Mistake 3:** Updating state on every resize event with no throttle
✅ **Correct:** Throttle (or debounce) the update

```jsx
// Wrong: dragging the window fires dozens of events per second, each causing a re-render
window.addEventListener('resize', () => setSize(read()));

// Right: schedule one update per window, as in useWindowSize(throttleMs)
const onResize = () => { if (timer === null) timer = setTimeout(update, throttleMs); };
```

---

## 🧠 Tricky Interview Question

```jsx
function useWindowSize() {
  const [size, setSize] = useState({ width: window.innerWidth });
  useEffect(() => {
    const onResize = () => setSize({ width: window.innerWidth });
    window.addEventListener('resize', onResize);
  }, []);
  return size;
}
```
Name every problem, in a Next.js app and in React Strict Mode.

**Answer:** (1) `window.innerWidth` in `useState` runs during server rendering and throws. (2) Even if guarded with `typeof window`, the server renders one value and the client another, which causes a hydration mismatch. (3) No cleanup: in development Strict Mode mounts, unmounts and mounts again, so two listeners stay attached, and on real unmount the listener leaks and calls `setSize` on an unmounted component. (4) No throttle, so many re-renders while resizing. The fix is the `useWindowSize` implementation above.

---

## ⚫ Interview Questions + Answers

Q1: Why start with `undefined` instead of the real width?
A1: The server has no window, so it renders with no size. The first client render must produce the same HTML, otherwise React reports a hydration mismatch. The real size is set after mount in an effect. Callers must handle `undefined`.

Q2: Why return a cleanup from `useEffect`?
A2: The effect adds a global listener. Without removing it, each mount adds another one, memory leaks, and handlers keep calling `setState` for components that no longer exist. Cleanup also makes Strict Mode double-mount safe.

Q3: Throttle vs debounce for resize?
A3: Throttle runs at most once per interval, so the UI updates smoothly during the drag. Debounce waits until the user stops, so the UI updates only at the end. This hook uses throttle. Use debounce when only the final size matters.

Q4: What does `[throttleMs]` in the dependency array do?
A4: The effect uses `throttleMs`, so it is a dependency. If the caller changes the delay, the old listener is cleaned up and a new one is added with the new delay. With `[]` the hook would keep using the first delay (a stale closure).

Q5: When would you use CSS instead of this hook?
A5: When only styling changes with width. Media queries and container queries need no JavaScript, no re-renders and have no hydration issue. Use the hook when behaviour or the rendered tree must change (different components, different data).

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- JavaScript logic depends on the viewport (render different components, chart sizing)
- You need numeric width/height values in code
- You want one tested place for resize handling

❌ **Avoid when:**
- Only styles change (use CSS media or container queries)
- You need an element's size, not the window's (use `ResizeObserver`)
- You only need a boolean for one breakpoint (`window.matchMedia` with a `useMediaQuery` hook re-renders less)

---

## 📊 Visual Diagram

```
  SERVER render            CLIENT first render        AFTER MOUNT (effect)
  size = {undefined}  ==   size = {undefined}   ──►   update(): size = {1280, 720}
  (no window)              (hydration matches)         addEventListener('resize')

  resize, resize, resize, resize ...   (many events while dragging)
        │
        ▼ onResize: if (timer === null) timer = setTimeout(update, 100)
        └─► ONE setSize per 100 ms ──► ONE re-render of components using the hook

  unmount ──► removeEventListener + clearTimeout   (no leak)

  Re-renders: components using the hook re-render when width OR height changes.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Custom hook | Function starting with `use` that reuses stateful logic | `use` से शुरू होने वाला reusable logic function |
| Cleanup | Function returned from an effect to undo it | Effect को undo करने वाला function |
| Throttle | Run at most once per time window | समय window में अधिकतम एक बार चलाना |
| Debounce | Run after events stop for some time | Events रुकने के बाद चलाना |
| Hydration | React attaching to server HTML | Server HTML से React को जोड़ना |
| SSR | Rendering on the server | Server पर render करना |
| Memory leak | Unreleased listeners or objects | जो listeners/objects कभी मुक्त नहीं होते |
| Stale closure | Function using old values | पुरानी values इस्तेमाल करने वाला function |

---

## ⚡ 3-Line Summary
**English:**
1. `useWindowSize` stores `{ width, height }` in state, measures in `useEffect`, and listens to `resize`.
2. Start with `undefined` for SSR and hydration safety, throttle updates, and always clean up the listener and timer.
3. Use CSS for pure styling changes, and the hook when logic or the rendered tree depends on the size.

**Hindi:**
1. `useWindowSize` `{ width, height }` को state में रखता है, `useEffect` में नापता है, और `resize` सुनता है।
2. SSR और hydration की सुरक्षा के लिए `undefined` से शुरू करो, updates throttle करो, और listener व timer हमेशा cleanup करो।
3. सिर्फ styling बदलनी हो तो CSS, और जब logic या rendered tree size पर निर्भर हो तब hook इस्तेमाल करो।

---

## ➡️ Next Topic
**209. Implement Virtual List** — हज़ारों rows में से सिर्फ दिखने वाली rows render करके list को तेज़ कैसे रखें (windowing)।
