# 126. React Profiler Tool
# हिंदी में: React Profiler — Performance Measure करने का Tool

---

## 🔵 Simple Definition (English)
The **React Profiler** records how long components take to render and **why** they rendered. It exists as the **Profiler tab in React DevTools** (browser extension) and as a **`<Profiler>` component** you can put in code to collect timing data programmatically.

## 🔵 सरल परिभाषा (Hindi)
**React Profiler** record करता है कि components को render होने में कितना समय लगा और वे **क्यों** render हुए। यह **React DevTools (browser extension) का Profiler tab** है और code में लगाया जा सकने वाला **`<Profiler>` component** भी है जो timing data programmatically इकट्ठा करता है।

---

## 🔴 Problem it Solves

"The app feels slow" is not actionable. Without measurement, developers guess and add `memo` in the wrong places. You need to know **which** component renders, **how often**, **how long**, and **what triggered it** (props, state, hooks, parent).

```jsx
// PROBLEM: guessing
// "Maybe ProductCard is slow?" → wrap in memo → nothing improves, the real cause was elsewhere

// SOLUTION: record an interaction in the Profiler and read the flamegraph:
//   - which components rendered during the click?
//   - which one took the most time?
//   - "Why did this render?" → "Props changed: onAdd"
```

## 🔴 यह क्यों बना? (Hindi)
"App धीमा लग रहा है" एक काम करने लायक जानकारी नहीं है। Measure के बिना developers अंदाज़ा लगाते हैं और गलत जगह `memo` डाल देते हैं। आपको जानना होता है कि **कौन सा** component render हुआ, **कितनी बार**, **कितनी देर** और **किस वजह से** (props, state, hooks, parent)। Profiler यही बताता है।

---

## 🟢 How it Works — Step by Step

```
Using DevTools Profiler:
Step 1 → Install React Developer Tools (Chrome/Firefox/Edge). Open DevTools → "Profiler" tab
Step 2 → Use a PRODUCTION-like build when possible (dev builds are slower; a production profiling
         build is needed for accurate numbers in some setups)
Step 3 → Click the record button (blue circle). In Settings (gear) tick "Record why each component rendered"
Step 4 → Perform the slow interaction (type in search, open a modal)
Step 5 → Click stop. Read results:
           Flamegraph: bar width/colour = render time (grey = did not render in this commit)
           Ranked: components sorted by time spent
           Commit selector (top bar): each bar is one commit (one React update); tall = slow
Step 6 → Click a component → right panel says "Why did this render?" (props, state, hooks, parent)
Step 7 → Fix the biggest item; record again and compare

Using <Profiler> in code:
  <Profiler id="ProductList" onRender={callback}>…</Profiler>
  callback(id, phase, actualDuration, baseDuration, startTime, commitTime)
  phase = "mount" | "update" | "nested-update"
  actualDuration = time spent rendering this update; baseDuration = estimate of a full re-render
  without memoization. (<Profiler> does nothing useful in standard production builds unless you use a profiling build.)
```

## 🟢 कैसे काम करता है? (Hindi)
```
DevTools Profiler के साथ:
Step 1 → React Developer Tools install करो (Chrome/Firefox/Edge)। DevTools → "Profiler" tab खोलो
Step 2 → हो सके तो PRODUCTION जैसा build इस्तेमाल करो (dev build धीमा होता है; कुछ setups में
         सही numbers के लिए production profiling build चाहिए)
Step 3 → Record button (नीला गोला) दबाओ। Settings (gear) में "Record why each component rendered" tick करो
Step 4 → धीमा interaction करो (search में typing, modal खोलना)
Step 5 → Stop दबाओ। Results पढ़ो:
           Flamegraph: bar की चौड़ाई/रंग = render time (grey = इस commit में render नहीं हुआ)
           Ranked: components समय के अनुसार क्रमबद्ध
           Commit selector (ऊपर): हर bar एक commit (एक React update); ऊँचा = धीमा
Step 6 → किसी component पर click करो → दाईं तरफ "Why did this render?" (props, state, hooks, parent)
Step 7 → सबसे बड़ी चीज़ ठीक करो; फिर record करके तुलना करो

Code में <Profiler>:
  <Profiler id="ProductList" onRender={callback}>…</Profiler>
  callback(id, phase, actualDuration, baseDuration, startTime, commitTime)
  phase = "mount" | "update" | "nested-update"
  actualDuration = इस update में लगा समय; baseDuration = memoization के बिना पूरे re-render का अनुमान
  (<Profiler> सामान्य production builds में तब तक कुछ काम का नहीं जब तक profiling build न हो।)
```

---

## 🟡 Real World Example
**Flipkart cart page:** Changing the quantity of one item felt slow on a mid-range Android phone. A recording with 4x CPU throttling showed that one click produced a commit of 180 ms: every `CartItem`, the `Recommendations` carousel and the footer rendered. "Why did this render?" showed "Parent component rendered" for the carousel, and the quantity state was held in the page root. Moving the cart state into a `CartList` component and memoizing the carousel brought the commit down to 25 ms.

## 🟡 Real Example Hindi mein
**Flipkart cart page:** Mid-range Android phone पर एक item की quantity बदलना धीमा लगता था। 4x CPU throttling के साथ recording से दिखा कि एक click पर 180 ms का commit बना: हर `CartItem`, `Recommendations` carousel और footer render हुए। "Why did this render?" ने carousel के लिए "Parent component rendered" दिखाया, और quantity state page root में थी। Cart state को `CartList` component में ले जाने और carousel को memoize करने से commit 25 ms पर आ गया।

---

## 💻 Code Example — Basic

```jsx
// Basic <Profiler>: log render timing for one subtree
import { Profiler, useState } from 'react';                    // Profiler is a built-in component
import { createRoot } from 'react-dom/client';

function onRender(id, phase, actualDuration, baseDuration, startTime, commitTime) {
  console.log(`${id} [${phase}] actual=${actualDuration.toFixed(2)}ms base=${baseDuration.toFixed(2)}ms`);
}

function List({ n }) {
  const rows = [];
  for (let i = 0; i < n; i++) rows.push(<li key={i}>Row {i}</li>);   // work being measured
  return <ul>{rows}</ul>;
}

function App() {
  const [n, setN] = useState(1000);                                  // size of the list
  return (
    <div>
      <button onClick={() => setN(n + 500)}>Add 500 rows</button>    {/* triggers an update commit */}
      <Profiler id="List" onRender={onRender}>                       {/* measures this subtree only */}
        <List n={n} />
      </Profiler>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);
// Console: "List [mount] ..." first, then "List [update] ..." on each click
```

## 💻 Code Example — Advanced

```jsx
// Advanced: send slow-render metrics to analytics + combine with the browser Performance API
import { Profiler, useCallback, useState } from 'react';
import { createRoot } from 'react-dom/client';

const SLOW_MS = 16;                                                  // ~1 frame at 60fps

// Reusable wrapper: reports only slow renders (keeps data volume small)
function Measured({ id, children }) {
  const onRender = useCallback((profilerId, phase, actualDuration) => {
    if (actualDuration > SLOW_MS) {
      // Replace with your analytics call (Sentry, Datadog, GA4, custom endpoint)
      console.warn('[slow render]', { id: profilerId, phase, actualDuration: Math.round(actualDuration) });
    }
  }, []);
  return <Profiler id={id} onRender={onRender}>{children}</Profiler>;
}

// Manual timing for non-render work (event handler + commit) with performance.mark/measure
function timeInteraction(name, fn) {
  performance.mark(`${name}-start`);                                 // start marker
  fn();                                                              // do the work (e.g. setState)
  requestAnimationFrame(() => {                                      // after the browser paints
    performance.mark(`${name}-end`);
    performance.measure(name, `${name}-start`, `${name}-end`);       // visible in the Performance tab
  });
}

function HeavyGrid({ count }) {
  const cells = Array.from({ length: count }, (_, i) => <span key={i}>{i % 10}</span>);
  return <div>{cells}</div>;
}

function App() {
  const [count, setCount] = useState(2000);
  return (
    <>
      <button onClick={() => timeInteraction('grow-grid', () => setCount((c) => c + 3000))}>Grow</button>
      <Measured id="HeavyGrid">                                      {/* wrap the suspected hot spot */}
        <HeavyGrid count={count} />
      </Measured>
    </>
  );
}

createRoot(document.getElementById('root')).render(<App />);
```

Re-render behavior: `onRender` runs after every commit that includes the profiled subtree, so keep it cheap and never call `setState` in it (that creates extra commits). Performance impact: Profiler adds small overhead, which is why it is disabled in normal production builds; use it in development or in a dedicated profiling build (version-dependent: in React 19 `<Profiler>` is stripped from production unless profiling builds are enabled).

---

## 🟠 Next.js Connection

The DevTools Profiler works with Next.js Client Components in the browser. Server Components do not run in the browser, so they do not appear in the commit timeline; measure them with server timing, logs and Next.js tooling. Complementary tools: **Lighthouse / Web Vitals** (`useReportWebVitals`), `@next/bundle-analyzer`, and the React Server Components section of React DevTools (version-dependent).

```jsx
// app/web-vitals.jsx
'use client';                                                    // hook runs in the browser
import { useReportWebVitals } from 'next/web-vitals';            // built-in Next.js helper

export function WebVitals() {
  useReportWebVitals((metric) => {
    // metric.name: 'LCP' | 'INP' | 'CLS' | 'FCP' | 'TTFB'; metric.value in ms (CLS unitless)
    console.log(metric.name, Math.round(metric.value));          // replace with analytics.send(metric)
  });
  return null;                                                   // renders nothing
}
```

```jsx
// app/layout.jsx (Server Component) → add <WebVitals /> once
import { WebVitals } from './web-vitals';
export default function RootLayout({ children }) {
  return (<html><body><WebVitals />{children}</body></html>);
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Profiling the development build and trusting absolute numbers
✅ **Correct:** Use relative comparisons in dev, and confirm in a production build with throttling

```jsx
// Wrong: "ListItem takes 12ms, React is slow!" (dev build, StrictMode double render, no throttling)
// Right: npm run build && npm start → record with 4x CPU throttling → compare before/after
```

❌ **Mistake 2:** Not enabling "Record why each component rendered"
✅ **Correct:** Turn it on in Profiler settings so you see the exact cause

```jsx
// Wrong: you see that Row rendered 200 times but not why → you guess memo
// Right: panel says "Props changed: onSelect" → fix the unstable function, not the component
```

❌ **Mistake 3:** Calling `setState` inside `onRender`
✅ **Correct:** Only collect data (push to an array/ref, send to analytics)

```jsx
// Wrong: causes another commit → another onRender → infinite loop
function onRender(id, phase, actual) { setLastTime(actual); }             // ❌

// Right
const timings = [];                                                        // ✅ module-level collector
function onRender2(id, phase, actual) { timings.push({ id, phase, actual }); }
```

---

## 🧠 Tricky Interview Question

```jsx
<Profiler id="A" onRender={onRender}>
  <Parent />
</Profiler>
// Parent re-renders once. Child is wrapped in memo and its props did not change.
// What does actualDuration vs baseDuration show for that commit?
```
**Answer:** `actualDuration` is the time actually spent rendering the subtree in this commit; since the memoized `Child` was skipped, it only counts `Parent` (small). `baseDuration` is an estimate of how long the whole subtree would take to render **without** any memoization (the sum of the most recent render times of every component in the subtree), so it stays large. If `actualDuration` is much smaller than `baseDuration`, your memoization is working. If they are about equal, memoization is not skipping anything.

---

## ⚫ Interview Questions + Answers

Q1: What is the React Profiler?
A1: A tool (DevTools tab and `<Profiler>` component) that records render timing and the reasons components rendered. It is the standard way to find unnecessary or slow renders before optimizing.

Q2: How do you find why a component re-rendered?
A2: In DevTools Profiler settings enable "Record why each component rendered", record the interaction, select the component in the commit and read "Why did this render?" (props changed, state changed, hooks changed, parent rendered, context changed).

Q3: What is a commit and what do the flamegraph colours mean?
A3: A commit is one React update applied to the DOM. In the flamegraph, wider/hotter bars took more time; grey bars did not render in that commit. The ranked chart sorts components by render time.

Q4: What do `actualDuration` and `baseDuration` mean in `<Profiler onRender>`?
A4: `actualDuration` is the time spent rendering for this update (reflects memoization). `baseDuration` is the estimated worst case without memoization. Comparing them shows the benefit of `memo`.

Q5: What other tools do you use beside the React Profiler?
A5: Chrome Performance tab (long tasks, INP), Lighthouse, Web Vitals, `why-did-you-render` library, bundle analyzers for JS size, and network tab. React Profiler covers render work only, not network or layout cost.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- A specific interaction feels slow (typing, filtering, opening a menu)
- You need to prove an optimization worked (before/after commits)
- You want slow-render telemetry from real users (with a profiling build)

❌ **Avoid / be careful when:**
- You want to measure network speed or bundle size (use other tools)
- You trust dev-mode numbers as absolute values
- You leave `<Profiler>` wrappers everywhere in production code

---

## 📊 Visual Diagram

```
 DevTools → Profiler → ● Record → (interact) → ■ Stop

 Commits:   ▂ ▂ ▇ ▂ ▂ ▆ ▂      ← each bar = one update, tall = slow
                 ▲
                 selected commit 3 (140 ms)

 Flamegraph for commit 3:
 ┌───────────────────────── App 2ms ─────────────────────────────┐
 │ ┌────────── CartPage 8ms ──────────┐ ┌─ Footer (grey, skipped) ┐│
 │ │ ┌─ CartItem 30ms ─┐┌─ CartItem 30ms ─┐┌─ Carousel 70ms ─┐    ││
 └─┴──────────────────────────────────────────────────────────────┘
 Select Carousel → "Why did this render?" → "Parent component rendered"
                 → fix: move state down or memo(Carousel) with stable props
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Profiler | Tool that records render timing | Render timing record करने वाला tool |
| Commit | One React update applied to the DOM | DOM पर लागू एक React update |
| Flamegraph | Chart of components and render time | Components और render time का chart |
| Ranked chart | Components sorted by render time | Render time के क्रम में components |
| actualDuration | Time spent rendering this commit | इस commit में render का समय |
| baseDuration | Estimated render time without memo | memo के बिना अनुमानित render time |
| Why did this render? | DevTools explanation of render cause | Render के कारण की जानकारी |
| Web Vitals | Core user-experience metrics (LCP, INP, CLS) | User-experience के मुख्य metrics |

---

## ⚡ 3-Line Summary
**English:**
1. The Profiler records render times and causes, in DevTools or via the `<Profiler>` component.
2. Enable "Record why each component rendered", profile realistic builds, and read commits and flamegraphs.
3. Measure before and after every optimization, and never `setState` in `onRender`.

**Hindi:**
1. Profiler render times और कारण record करता है, DevTools में या `<Profiler>` component से।
2. "Record why each component rendered" चालू करो, असली जैसे builds profile करो, और commits व flamegraph पढ़ो।
3. हर optimization से पहले और बाद में measure करो, और `onRender` में कभी `setState` मत करो।

---

## ➡️ Next Topic
**127. Virtualization (react-window)** — Profiler से पता चले कि हज़ारों list items ही धीमेपन की वजह हैं, तो अगला कदम है सिर्फ दिखने वाले rows render करना।
