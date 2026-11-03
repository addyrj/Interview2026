# 133. Concurrent Mode
# हिंदी में: Concurrent Mode — rendering को रोक और बदल सकने वाला React

---

## 🔵 Simple Definition (English)
**Concurrent rendering** (the modern name for "Concurrent Mode") lets React start rendering an update, pause it, and switch to something more urgent (like typing), then resume or discard the old work. The old experimental "Concurrent Mode" flag was replaced in React 18 by concurrent features you opt into (`useTransition`, `useDeferredValue`, Suspense) simply by using `createRoot`.

## 🔵 सरल परिभाषा (Hindi)
**Concurrent rendering** (जिसे पहले "Concurrent Mode" कहते थे) React को update का render शुरू करने, उसे रोकने, किसी ज़्यादा ज़रूरी काम (जैसे typing) पर जाने, और फिर पुराना काम resume या discard करने देता है। पुराने experimental "Concurrent Mode" flag की जगह React 18 में concurrent features आए जिन्हें आप `createRoot` इस्तेमाल करके और `useTransition`, `useDeferredValue`, Suspense से अपनाते हैं।

---

## 🔴 Problem it Solves

Before React 18, once React started rendering, it could not stop until it finished (synchronous rendering). If a render took 300 ms (filtering 10,000 products), the browser could not process keystrokes, so the input froze and typing felt laggy.

```jsx
// PROBLEM (legacy sync rendering): one expensive render blocks everything
function Search() {
  const [q, setQ] = useState('');
  const results = slowFilter(allProducts, q);           // 300 ms of work on every keystroke
  return <input value={q} onChange={e => setQ(e.target.value)} />; // input feels frozen
}

// SOLUTION (concurrent): mark the slow update as non-urgent; React keeps the input responsive
const [isPending, startTransition] = useTransition();
startTransition(() => setFilter(q));                    // interruptible
```

## 🔴 यह क्यों बना? (Hindi)
React 18 से पहले, एक बार render शुरू होने पर React उसे पूरा होने तक रोक नहीं सकता था (synchronous rendering)। अगर एक render 300 ms ले (10,000 products filter करना), तो browser keystrokes process नहीं कर पाता था, इसलिए input अटक जाता था और typing laggy लगती थी।

---

## 🟢 How it Works — Step by Step

```
Step 1 → An update arrives (a keystroke, a click, a data load) and gets a priority (lane)
Step 2 → Urgent updates (typing, clicking) are rendered right away
Step 3 → Non-urgent updates (transitions, deferred values) render in small time slices
Step 4 → Between slices React yields to the browser so it can paint and handle input
Step 5 → If a more urgent update arrives, React pauses/abandons the low-priority render and starts the urgent one
Step 6 → Only a finished, consistent tree is committed to the DOM (no half-updated UI is ever shown)

KEY: rendering becomes interruptible; committing to the DOM is still one atomic step
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → कोई update आता है (keystroke, click, data load) और उसे priority (lane) मिलती है
Step 2 → Urgent updates (typing, clicking) तुरंत render होती हैं
Step 3 → Non-urgent updates (transitions, deferred values) छोटे time slices में render होती हैं
Step 4 → Slices के बीच React browser को मौका देता है ताकि वह paint कर सके और input संभाल सके
Step 5 → अगर ज़्यादा urgent update आए, तो React कम priority वाला render रोक/छोड़कर urgent वाला शुरू करता है
Step 6 → DOM में सिर्फ़ पूरा, consistent tree commit होता है (आधा-बदला UI कभी नहीं दिखता)

KEY: rendering interruptible हो जाती है; DOM में commit अब भी एक atomic step है
```

---

## 🟡 Real World Example
**Flipkart search with live filters:** A shopper types "shoes" and the page filters 8,000 products. Without concurrent rendering, every character triggers a heavy re-render of the grid, so the text box lags. With concurrent rendering, the text box updates instantly (urgent), the grid update is a transition (non-urgent). If the shopper types another letter before the grid finishes, React drops the stale grid render and starts again with the new text, so the app always feels responsive.

## 🟡 Real Example Hindi mein
**Flipkart live filters वाला search:** Shopper "shoes" लिखता है और page 8,000 products filter करता है। Concurrent rendering के बिना हर अक्षर पर grid का भारी re-render होता है, इसलिए text box लैग करता है। Concurrent rendering में text box तुरंत update होता है (urgent) और grid update एक transition है (non-urgent)। अगर grid पूरा होने से पहले shopper एक और अक्षर लिखे, तो React पुराना grid render छोड़कर नए text से फिर शुरू करता है, इसलिए app हमेशा responsive लगता है।

---

## 💻 Code Example — Basic

```jsx
// Basic: concurrency is ON when you use createRoot (React 18+). Legacy ReactDOM.render is NOT concurrent.
import { createRoot } from 'react-dom/client';          // React 18/19 root API (concurrent)
import { useState, useDeferredValue } from 'react';     // useDeferredValue = a concurrent feature

const products = Array.from({ length: 5000 }, (_, i) => `Product ${i}`); // fake catalogue

function List({ query }) {
  // slow component: renders 5,000 rows matching the query
  const rows = products.filter(p => p.includes(query)).slice(0, 2000);   // heavy list
  return <ul>{rows.map(p => <li key={p}>{p}</li>)}</ul>;
}

function App() {
  const [query, setQuery] = useState('');               // urgent state: what the user typed
  const deferredQuery = useDeferredValue(query);        // lagging copy used for the slow part

  return (
    <div>
      <input
        value={query}                                   // input uses the URGENT value
        onChange={e => setQuery(e.target.value)}        // updates immediately on each keystroke
      />
      <List query={deferredQuery} />                    {/* list uses the DEFERRED value (interruptible) */}
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />); // createRoot enables concurrent features
```

## 💻 Code Example — Advanced

```jsx
// Advanced: tabs where the slow tab renders as a transition, so the UI never freezes
import { useState, useTransition, memo } from 'react';  // concurrent hooks
import { createRoot } from 'react-dom/client';          // root API

// Deliberately slow component: blocks the thread ~1 ms per item (500 items ≈ 500 ms)
const SlowItem = ({ text }) => {
  const start = performance.now();                      // measure start
  while (performance.now() - start < 1) { /* busy wait to simulate cost */ }
  return <li>{text}</li>;                               // trivial output
};

// memo: avoid re-rendering the slow list when unrelated state changes
const PostsTab = memo(function PostsTab() {
  const items = Array.from({ length: 500 }, (_, i) => <SlowItem key={i} text={`Post ${i}`} />);
  return <ul>{items}</ul>;                              // 500 slow rows
});

function Tabs() {
  const [tab, setTab] = useState('home');               // the tab that is actually shown
  const [isPending, startTransition] = useTransition(); // pending flag + transition starter

  function select(next) {
    startTransition(() => {                             // mark this update as NON-urgent
      setTab(next);                                     // React renders it in the background
    });
  }

  return (
    <div>
      <button onClick={() => select('home')}>Home</button>   {/* fast tab */}
      <button onClick={() => select('posts')}>Posts (slow)</button>
      <button onClick={() => select('about')}>About</button>

      {isPending && <span> Loading...</span>}           {/* tiny inline feedback, old UI stays visible */}

      <div style={{ opacity: isPending ? 0.6 : 1 }}>    {/* dim old content while the new one renders */}
        {tab === 'home' && <p>Welcome home</p>}
        {tab === 'posts' && <PostsTab />}
        {tab === 'about' && <p>About us</p>}
      </div>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<Tabs />);
// Click "Posts", then immediately click "About": React abandons the slow render and shows About right away.
```

---

## 🟠 Real App Integration

Next.js App Router uses React 18/19 concurrent features by default: streaming SSR with Suspense, selective hydration (interactive parts hydrate first, based on what the user clicks), and client navigation wrapped in transitions, so the old page stays visible while the next route loads.

```jsx
// app/search/SearchBox.jsx: URL-driven search that stays responsive during navigation
'use client';                                            // uses hooks → Client Component
import { useState, useTransition } from 'react';         // concurrent hooks
import { useRouter } from 'next/navigation';             // App Router navigation

export default function SearchBox() {
  const router = useRouter();                            // navigation API
  const [q, setQ] = useState('');                        // input state, always instant
  const [isPending, startTransition] = useTransition();  // track the navigation

  function onChange(e) {
    const value = e.target.value;                        // new text
    setQ(value);                                         // urgent update: input stays responsive
    startTransition(() => {                              // non-urgent: server re-render + navigation
      router.replace(`/search?q=${encodeURIComponent(value)}`); // results page re-renders on the server
    });
  }

  return (
    <div>
      <input value={q} onChange={onChange} placeholder="Search" />
      {isPending && <p>Updating results...</p>}          {/* feedback while the server work is pending */}
    </div>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Still using the legacy `ReactDOM.render` (or thinking React 18 enables concurrency automatically)
✅ **Correct:** Use `createRoot`, then opt in using transitions/deferred values

```jsx
// Wrong: React 17-style root → legacy synchronous mode (and removed in React 19)
import ReactDOM from 'react-dom';
ReactDOM.render(<App />, document.getElementById('root'));      // ❌

// Right: concurrent root
import { createRoot } from 'react-dom/client';
createRoot(document.getElementById('root')).render(<App />);    // ✅
```

❌ **Mistake 2:** Putting controlled input state inside `startTransition`
✅ **Correct:** Keep the input state urgent; transition only the expensive derived update

```jsx
// Wrong: input updates become low priority → typing feels delayed
startTransition(() => setQuery(e.target.value));                // ❌

// Right
setQuery(e.target.value);                                       // ✅ urgent: input
startTransition(() => setFilter(e.target.value));               // ✅ non-urgent: heavy list
```

❌ **Mistake 3:** Doing side effects during render, assuming it runs only once
✅ **Correct:** Keep render pure; React may start, pause, discard and repeat a render

```jsx
// Wrong: a render can be called several times, or thrown away
function Item({ id }) {
  analytics.track('viewed', id);                                // ❌ duplicate/phantom events
  return <p>{id}</p>;
}

// Right: side effects go in effects (they run only for committed renders)
function Item2({ id }) {
  useEffect(() => { analytics.track('viewed', id); }, [id]);    // ✅
  return <p>{id}</p>;
}
```

---

## 🧠 Tricky Interview Question

```jsx
function App() {
  const [text, setText] = useState('');
  const [isPending, startTransition] = useTransition();
  const [list, setList] = useState([]);

  function onChange(e) {
    setText(e.target.value);
    startTransition(() => {
      setList(makeSlowList(e.target.value));
    });
  }
  console.log('render', text, isPending);
  return <input value={text} onChange={onChange} />;
}
// Question: user types "a". What does the console show (ignoring StrictMode)?
```
**Answer:** The urgent update `setText('a')` and the transition's pending flag are batched in the first render, so you see `render a true` (urgent render with `isPending` true). Then React starts rendering the transition (`setList`) in the background, and when it finishes you get a second render `render a false` with the new `list`. If the user types another letter before the background render finishes, React abandons that stale transition render and starts a new one, so you may see extra `render ab true` lines but never a committed render for the abandoned work. The point: `text` shows up instantly while the expensive list update is interruptible.

---

## ⚫ Interview Questions + Answers

Q1: What is concurrent rendering in React?
A1: It is React's ability to prepare multiple versions of the UI, prioritize urgent updates, and interrupt or discard low-priority renders. It is enabled by `createRoot` in React 18 and is used through `useTransition`, `useDeferredValue` and Suspense. Rendering can be paused; the commit to the DOM is still synchronous and atomic.

Q2: What happened to "Concurrent Mode"?
A2: It was an all-or-nothing experimental mode in React 16/17 previews. React 18 replaced it with gradual adoption: concurrent behavior only applies to updates you mark as transitions or to features like Suspense, so existing code keeps working.

Q3: Is concurrent rendering multi-threading?
A3: No. JavaScript still runs on one thread. React splits rendering into small units of work and yields to the browser between them (time slicing), so urgent events can run in between.

Q4: How does concurrent rendering change how you write components?
A4: Components must be pure: render may run multiple times or be discarded. No mutation of external variables or side effects during render. StrictMode (double rendering in dev) helps to catch violations.

Q5: What is the difference between `useTransition` and `useDeferredValue`?
A5: `useTransition` wraps the state setter, so you control the update source and get `isPending`. `useDeferredValue` wraps a value you receive (for example a prop), so you control the consumer. Both mark work as low priority and interruptible.

---

## 🔷 When to Use + When Not to Use
✅ **Use concurrent features when:**
- An update is expensive (big lists, charts, filtering) and must not block typing or clicks
- You navigate between heavy screens and want the old screen to stay visible
- You want streaming SSR and selective hydration

❌ **Avoid when:**
- The update is already fast; transitions add little and complicate the code
- The work is not rendering (a slow network call): use async patterns, loading UI or debounce
- You need the update to apply instantly (controlled input, animation state)

---

## 📊 Visual Diagram

```
  Synchronous (legacy):
  keystroke ─▶ [=========== 300 ms render ===========] ─▶ paint      (input frozen)

  Concurrent (React 18):
  keystroke ─▶ [urgent: input render] ─▶ paint
                 ─▶ [slice][yield][slice][yield][slice] ─▶ commit ─▶ paint   (list update)
                       ▲
       new keystroke ──┘  interrupts: drop stale list work, render input first, restart list work

  Priority lanes:  urgent (click, typing)  >  transition (non-urgent)  >  idle/offscreen
```

Re-render behavior: a render can run more than once and may be abandoned, so components must be pure. Only the committed render runs effects. Performance impact: total CPU work can be the same or slightly higher, but perceived responsiveness improves a lot since urgent updates never wait for slow ones.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Concurrent rendering | Interruptible rendering with priorities | Priorities के साथ interruptible rendering |
| Time slicing | Splitting render work into small chunks | Render के काम को छोटे हिस्सों में बाँटना |
| Transition | Non-urgent update marked by startTransition | startTransition से चिह्नित non-urgent update |
| Urgent update | Update users expect instantly (typing, click) | जो update तुरंत चाहिए (typing, click) |
| createRoot | React 18+ root API enabling concurrency | Concurrency चालू करने वाला React 18+ root API |
| Selective hydration | Hydrate parts by priority and interaction | Priority और interaction के हिसाब से hydrate करना |
| Lane | Internal priority level for updates | Updates का internal priority level |
| Commit | Applying a finished render to the DOM | पूरे हुए render को DOM में लगाना |

---

## ⚡ 3-Line Summary
**English:**
1. Concurrent rendering lets React pause, resume or drop low-priority renders so urgent updates stay instant.
2. You get it by using `createRoot` and opting in with `useTransition`, `useDeferredValue` and Suspense.
3. Keep components pure; Next.js builds on it with streaming, selective hydration and transition-based navigation.

**Hindi:**
1. Concurrent rendering से React कम priority वाले renders को रोक, resume या छोड़ सकता है, ताकि urgent updates तुरंत रहें।
2. `createRoot` इस्तेमाल करने और `useTransition`, `useDeferredValue` व Suspense से opt-in करने पर यह मिलता है।
3. Components को pure रखो; Next.js इसी पर streaming, selective hydration और transition-based navigation बनाता है।

---

## ➡️ Next Topic
**134. Automatic Batching (React 18)** — एक से ज़्यादा state updates को React एक ही render में कैसे जोड़ता है, और React 18 में promises, timeouts व native events में भी batching कैसे आई।
