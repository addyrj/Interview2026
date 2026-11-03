# 135. Transitions (useTransition)
# हिंदी में: Transitions — urgent और non-urgent updates को अलग करना

---

## 🔵 Simple Definition (English)
**`useTransition`** lets you mark a state update as a non-urgent "transition". React keeps the current UI responsive and interactive while it renders the new UI in the background. It returns `[isPending, startTransition]`: `startTransition(fn)` marks the updates inside `fn` as low priority, and `isPending` is `true` while that work is in progress.

## 🔵 सरल परिभाषा (Hindi)
**`useTransition`** किसी state update को non-urgent "transition" चिह्नित करने देता है। React नया UI background में render करते समय मौजूदा UI को responsive और interactive रखता है। यह `[isPending, startTransition]` लौटाता है: `startTransition(fn)` के अंदर के updates कम priority के हो जाते हैं, और काम चलने तक `isPending` `true` रहता है।

---

## 🔴 Problem it Solves

Some updates are cheap and must feel instant (typing, toggling), others are heavy (re-rendering a big list, switching to a heavy tab). If both are treated as equally urgent, the heavy one blocks the light one and the UI freezes. Also, when navigating, you might not want to replace visible content with a spinner immediately.

```jsx
// PROBLEM: switching to a heavy tab blocks the whole UI for 400 ms
<button onClick={() => setTab('posts')}>Posts</button>  // click feels dead until the render finishes

// SOLUTION: the tab switch becomes interruptible; the old tab stays usable meanwhile
<button onClick={() => startTransition(() => setTab('posts'))}>Posts</button>
```

## 🔴 यह क्यों बना? (Hindi)
कुछ updates सस्ते होते हैं और तुरंत महसूस होने चाहिए (typing, toggle), कुछ भारी (बड़ी list का re-render, भारी tab पर जाना)। अगर दोनों को बराबर urgent माना जाए तो भारी वाला हल्के को रोक देता है और UI freeze हो जाता है। Navigation में भी आप नहीं चाहते कि दिख रहे content की जगह तुरंत spinner आ जाए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → User clicks; you call startTransition(() => setTab('posts'))
Step 2 → React tags that update as a transition (low priority) instead of urgent
Step 3 → isPending becomes true immediately (an urgent update), so you can show feedback
Step 4 → React renders the new tab in the background, in small slices, without blocking input
Step 5 → If the user clicks again or types, the in-progress transition is interrupted or replaced
Step 6 → When the render finishes, React commits it and isPending becomes false

KEY: with Suspense, a transition keeps the OLD UI on screen instead of showing a fallback
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → User click करता है; आप startTransition(() => setTab('posts')) call करते हैं
Step 2 → React उस update को urgent की जगह transition (कम priority) चिह्नित करता है
Step 3 → isPending तुरंत true हो जाता है (urgent update), ताकि आप feedback दिखा सकें
Step 4 → React नया tab background में, छोटे slices में render करता है, input को रोके बिना
Step 5 → अगर user फिर click या type करे, तो चल रहा transition interrupt या replace हो जाता है
Step 6 → Render पूरा होने पर React commit करता है और isPending false हो जाता है

KEY: Suspense के साथ transition पुराने UI को screen पर रखता है, fallback नहीं दिखाता
```

---

## 🟡 Real World Example
**Zomato "Search restaurants" with filters:** A user taps filters (Rating 4+, Pure Veg, Under 30 min). Each tap re-renders a list of 3,000 restaurant cards. The filter chip must highlight immediately (urgent), while the list can refresh a moment later (transition). The old list stays visible with slight dimming and a small "Updating..." text driven by `isPending`. If the user taps another filter quickly, React discards the half-done render and starts over.

## 🟡 Real Example Hindi mein
**Zomato "Search restaurants" और filters:** User filters टैप करता है (Rating 4+, Pure Veg, Under 30 min)। हर tap 3,000 restaurant cards की list re-render करता है। Filter chip तुरंत highlight होना चाहिए (urgent), जबकि list थोड़ी देर बाद refresh हो सकती है (transition)। पुरानी list हल्के dim होकर और `isPending` से चलने वाले छोटे "Updating..." text के साथ दिखती रहती है। अगर user जल्दी से दूसरा filter टैप करे, तो React आधा बना render छोड़कर फिर से शुरू करता है।

---

## 💻 Code Example — Basic

```jsx
// Basic: filter a big list; the input stays instant, the list updates as a transition
import { useState, useTransition } from 'react';       // hooks
import { createRoot } from 'react-dom/client';         // React 18/19 root API

const allItems = Array.from({ length: 20000 }, (_, i) => `Restaurant ${i}`); // big data set

function Search() {
  const [text, setText] = useState('');                // what the user typed (urgent)
  const [filter, setFilter] = useState('');            // what the list actually uses (non-urgent)
  const [isPending, startTransition] = useTransition(); // transition controls

  function onChange(e) {
    const value = e.target.value;                      // read the new text
    setText(value);                                    // URGENT: input shows the letter right away
    startTransition(() => {                            // everything inside is low priority
      setFilter(value);                                // NON-URGENT: heavy list refresh
    });
  }

  const shown = allItems.filter(r => r.includes(filter)).slice(0, 3000); // heavy derived list

  return (
    <div>
      <input value={text} onChange={onChange} placeholder="Search" /> {/* never lags */}
      {isPending && <p>Updating...</p>}                {/* feedback while background work runs */}
      <ul style={{ opacity: isPending ? 0.5 : 1 }}>    {/* dim the old list while pending */}
        {shown.map(r => <li key={r}>{r}</li>)}
      </ul>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<Search />);
```

## 💻 Code Example — Advanced

```jsx
// Advanced: Suspense + transition: switching tabs keeps the old tab visible instead of flashing a spinner
import { useState, useTransition, Suspense, use } from 'react'; // React 19 `use` (version-dependent)
import { createRoot } from 'react-dom/client';                   // root API

// Simple promise cache so the same tab does not refetch on each render
const cache = new Map();                                          // key → promise
function loadTab(name) {
  if (!cache.has(name)) {                                         // create the promise once per tab
    cache.set(name, new Promise(r => setTimeout(() => r(`${name} content`), 800)));
  }
  return cache.get(name);                                         // same promise every render
}

function TabContent({ name }) {
  const text = use(loadTab(name));                                // suspends until the promise resolves
  return <p>{text}</p>;                                           // real content
}

function Tabs() {
  const [tab, setTab] = useState('home');                         // active tab
  const [isPending, startTransition] = useTransition();           // transition state

  function go(next) {
    startTransition(() => setTab(next));                          // do NOT show the Suspense fallback; keep old UI
  }

  return (
    <div>
      {['home', 'orders', 'offers'].map(t => (
        <button
          key={t}
          onClick={() => go(t)}                                   // transition-based navigation
          style={{ fontWeight: tab === t ? 'bold' : 'normal' }}   // active style
        >
          {t}
        </button>
      ))}
      {isPending && <span> loading...</span>}                     {/* small inline indicator */}

      <Suspense fallback={<p>Loading first tab...</p>}>           {/* fallback appears only on the very first load */}
        <div style={{ opacity: isPending ? 0.6 : 1 }}>            {/* old content dims, stays visible */}
          <TabContent name={tab} />
        </div>
      </Suspense>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<Tabs />);
```

---

## 🟠 Real App Integration

In Next.js App Router, `router.push()` already runs inside a transition, and `<Link>` navigation does too. Use `useTransition` yourself for `router.replace` on search params, and with Server Actions to track the pending state. The old page stays visible while the next route's Server Components stream in.

```jsx
// app/products/Filters.jsx
'use client';                                            // uses hooks → Client Component
import { useTransition } from 'react';                   // transition hook
import { useRouter, useSearchParams, usePathname } from 'next/navigation'; // App Router hooks

export default function Filters() {
  const router = useRouter();                            // programmatic navigation
  const pathname = usePathname();                        // current path
  const params = useSearchParams();                      // read-only current query string
  const [isPending, startTransition] = useTransition(); // track the server round trip

  function setSort(value) {
    const next = new URLSearchParams(params.toString()); // copy current params
    next.set('sort', value);                             // change one param
    startTransition(() => {                              // keep the old list visible meanwhile
      router.replace(`${pathname}?${next.toString()}`);  // server re-renders the page with the new sort
    });
  }

  return (
    <div aria-busy={isPending}>                          {/* accessibility: busy during transition */}
      <button onClick={() => setSort('price')}>Price</button>
      <button onClick={() => setSort('rating')}>Rating</button>
      {isPending && <span>Updating...</span>}
    </div>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Wrapping a controlled input's state setter in `startTransition`
✅ **Correct:** Update the input state urgently; transition only the heavy derived state

```jsx
// Wrong: the input lags because its update is low priority
startTransition(() => setText(e.target.value));         // ❌

// Right
setText(e.target.value);                                // ✅ urgent
startTransition(() => setFilter(e.target.value));       // ✅ heavy part
```

❌ **Mistake 2:** Putting async work (awaiting a fetch) inside `startTransition` in React 18
✅ **Correct:** In React 18 the callback must be synchronous; React 19 supports async actions in transitions

```jsx
// React 18 wrong: updates after await are NOT part of the transition
startTransition(async () => {                           // ❌ React 18: async callback not tracked
  const data = await fetchData();
  setData(data);                                        // this update runs as a normal urgent update
});

// React 19 right (version-dependent): async functions are supported in startTransition ("Actions")
startTransition(async () => {
  const data = await fetchData();
  startTransition(() => setData(data));                 // ✅ wrap updates after await in a new transition
});
```

❌ **Mistake 3:** Using transitions to control text input or when the work is not rendering
✅ **Correct:** Use debounce for network calls; transitions only help with rendering cost

```jsx
// Wrong: expecting transition to delay or cancel a network request
startTransition(() => { fetch(`/api?q=${q}`); });       // ❌ fetch is not React rendering work

// Right: debounce the request, and transition the render of results
const results = useDeferredValue(data);                 // ✅ or debounce the fetch call itself
```

---

## 🧠 Tricky Interview Question

```jsx
function App() {
  const [count, setCount] = useState(0);
  const [isPending, startTransition] = useTransition();

  function onClick() {
    startTransition(() => {
      setCount(c => c + 1);
    });
    setCount(c => c + 10);
  }

  console.log('render', count, isPending);
  return <button onClick={onClick}>go</button>;
}
// Question: from count = 0, click once. What is logged?
```
**Answer:** React processes the urgent update first. Updates are applied in priority order, so the urgent `+10` renders first and shows `render 10 true` (the `isPending` flag is set in the same urgent batch). When React then renders the transition lane, it re-applies the queued updates in order: the transition's `+1` is applied on top of the already urgent state, so the final committed value is `11`, logged as `render 11 false`. Transitions never lose updates: they are only deferred in priority. This is also why `isPending` is `true` in the first log. (Exact intermediate logs are version-dependent; the final state `11` is the reliable part.)

---

## ⚫ Interview Questions + Answers

Q1: What does `useTransition` do?
A1: It marks state updates as non-urgent so React can interrupt their rendering to handle urgent updates (typing, clicks). It gives `isPending` to show feedback and `startTransition` to wrap the updates.

Q2: `useTransition` vs `useDeferredValue`?
A2: `useTransition` wraps the code that sets state, so you need control over the setter and get `isPending`. `useDeferredValue` takes a value (for example from props) and returns a lagging copy. Use `useDeferredValue` when you cannot wrap the update, such as a value from a parent or a library.

Q3: How do transitions work with Suspense?
A3: If an update inside a transition makes a component suspend, React keeps showing the already visible UI instead of replacing it with the Suspense fallback. The new UI appears when ready. Without a transition, the boundary would show its fallback immediately.

Q4: Can you use `startTransition` without the hook?
A4: Yes. `import { startTransition } from 'react'` works anywhere (outside components, in libraries), but it does not give you `isPending`. The hook is for when you need the pending flag.

Q5: Which updates cannot be transitions?
A5: Updates to controlled text inputs (they must be synchronous), and anything that must be immediate. Also, transitions do not make slow code faster; they only make it interruptible. Heavy computation that is not React rendering still blocks the thread.

---

## 🔷 When to Use + When Not to Use
✅ **Use `useTransition` when:**
- A state change triggers heavy re-rendering (lists, charts, tab content)
- You navigate between screens that suspend and want the old UI to stay
- You want `isPending` for subtle loading feedback

❌ **Avoid when:**
- The update is cheap (no visible lag)
- It is a controlled input or must apply instantly
- The slowness is in a network call or a long synchronous calculation (use debounce, workers or memoization)

---

## 📊 Visual Diagram

```
  click ──▶ startTransition(() => setTab('posts'))
              │
              ├─ urgent lane:  isPending = true  ─▶ paint (button feedback, dim old UI)
              │
              └─ transition lane: render <Posts/> in time slices
                      │        ▲
                      │        └── user clicks again → drop this render, start a new one
                      ▼
                 render finished ─▶ commit new UI ─▶ isPending = false

  With Suspense:
  without transition → [old UI] ─▶ [fallback spinner] ─▶ [new UI]
  with transition    → [old UI, dimmed, isPending] ─────▶ [new UI]
```

Re-render behavior: the component re-renders once for `isPending: true` and again when the transition commits (`isPending: false`). Slow children inside the transition render in the background. Performance impact: no reduction of total work, but the UI stays responsive and avoids layout flashes from spinners.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Transition | Non-urgent update that can be interrupted | Non-urgent और interruptible update |
| startTransition | Marks updates inside as a transition | अंदर के updates को transition चिह्नित करता है |
| isPending | True while the transition renders | Transition render होने तक true |
| Urgent update | Instant interaction feedback | तुरंत मिलने वाला interaction feedback |
| useDeferredValue | Lagging copy of a value | किसी value की पीछे चलने वाली copy |
| Time slicing | Rendering in small chunks | छोटे हिस्सों में render करना |
| Action (React 19) | Async function used in a transition | Transition में इस्तेमाल होने वाला async function |
| Suspense fallback | UI shown while waiting | इंतज़ार के दौरान दिखने वाला UI |

---

## ⚡ 3-Line Summary
**English:**
1. `useTransition` marks heavy updates as non-urgent, so typing and clicks stay instant while the new UI renders in the background.
2. It returns `isPending` for feedback; with Suspense it keeps the old UI instead of showing a fallback.
3. Keep input state urgent; in Next.js, wrap `router.replace` in a transition (`router.push` and `<Link>` already use one).

**Hindi:**
1. `useTransition` भारी updates को non-urgent चिह्नित करता है, ताकि नया UI background में बनते समय typing और clicks तुरंत रहें।
2. यह feedback के लिए `isPending` देता है; Suspense के साथ यह fallback की जगह पुराना UI दिखाता रहता है।
3. Input की state को urgent रखो; Next.js में `router.replace` को transition में लपेटो (`router.push` और `<Link>` पहले से इस्तेमाल करते हैं)।

---

## ➡️ Next Topic
**136. React 18 — New Features** — `createRoot`, automatic batching, transitions, Suspense on the server, `useId`, `useSyncExternalStore` और बाकी सब React 18 की नई चीज़ें एक जगह।
