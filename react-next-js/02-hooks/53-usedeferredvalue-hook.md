# 53. useDeferredValue Hook
# हिंदी में: useDeferredValue Hook — Value का Lagging Copy बनाना

---

## 🔵 Simple Definition (English)
**`useDeferredValue(value)`** returns a copy of a value that "lags behind" during urgent updates. React first renders with the old deferred value (fast), then re-renders in the background with the new one. It keeps typing and clicking responsive.

## 🔵 सरल परिभाषा (Hindi)
**`useDeferredValue(value)`** किसी value की ऐसी copy देता है जो urgent updates के दौरान "पीछे" रहती है। React पहले पुरानी deferred value से जल्दी render करता है, फिर background में नई value से दोबारा render करता है। इससे typing और click responsive रहते हैं।

---

## 🔴 Problem it Solves

A search box feeds a heavy results list. Each keystroke re-renders the list synchronously, so typing lags. You cannot always use `useTransition`, because the state setter may be in a parent or a library, and you only receive the **value** as a prop. Debouncing adds a fixed delay and still blocks when it fires.

```jsx
// PROBLEM: results re-render on every keystroke, typing freezes
function Results({ query }) { /* 5000 rows filtered synchronously */ }

// SOLUTION: inside Results' parent, render with a deferred copy of the query
const deferredQuery = useDeferredValue(query);   // lags behind while typing
<Results query={deferredQuery} />                // heavy render uses the lagging value
```

## 🔴 यह क्यों बना? (Hindi)
Search box एक भारी results list को data देता है। हर keystroke पर list synchronously re-render होती है, इसलिए typing अटकती है। हर बार `useTransition` नहीं चल सकता, क्योंकि state setter parent या library में हो सकता है और आपको सिर्फ **value** prop में मिलती है। Debounce एक fixed delay जोड़ता है और चलने पर फिर भी block करता है। `useDeferredValue` value की lagging copy देकर यह समस्या सुलझाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → const deferred = useDeferredValue(value)
Step 2 → Value changes (user types "s" → "sa")
Step 3 → React renders FIRST with deferred = old value ("s"): fast, input shows "sa"
Step 4 → React then starts a background render with deferred = new value ("sa")
Step 5 → If value changes again mid-render, the background render is abandoned and restarted
Step 6 → When finished, React commits the heavy UI with the new deferred value
Step 7 → Compare value !== deferred to know the UI is "stale" and show a fade

KEY: on first mount, deferred equals value (no extra render); optional 2nd argument
     initialValue exists in React 19 (version-dependent)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → const deferred = useDeferredValue(value)
Step 2 → Value बदलती है (user "s" से "sa" type करता है)
Step 3 → React पहले deferred = पुरानी value ("s") से render करता है: तेज़, input में "sa" दिखता है
Step 4 → फिर background में deferred = नई value ("sa") से render शुरू करता है
Step 5 → बीच में value फिर बदली तो background render छोड़कर दोबारा शुरू होता है
Step 6 → पूरा होने पर React भारी UI को नई deferred value के साथ commit करता है
Step 7 → value !== deferred से पता चलता है कि UI "stale" है, तब fade दिखा सकते हो

KEY: पहली mount पर deferred और value बराबर होती हैं (extra render नहीं); दूसरा argument
     initialValue React 19 में है (version-dependent)
```

---

## 🟡 Real World Example
**Zomato search:** The search bar lives in the header component and passes `query` down to a restaurant list that filters thousands of entries. The list component can't change how `query` is set. Using `useDeferredValue(query)` in the list's parent keeps the input instant while the list updates a moment later, and the old results stay visible and slightly faded instead of flashing empty.

## 🟡 Real Example Hindi mein
**Zomato search:** Search bar header component में है और `query` को नीचे restaurant list को भेजता है, जो हज़ारों entries filter करती है। List यह नहीं बदल सकती कि `query` कैसे set होती है। List के parent में `useDeferredValue(query)` लगाने से input तुरंत चलता है, list थोड़ी देर बाद update होती है, और पुराने results खाली flash होने की जगह हल्के faded दिखते रहते हैं।

---

## 💻 Code Example — Basic

```jsx
// Basic useDeferredValue: input stays instant, list updates a bit later
import { useState, useDeferredValue } from 'react';       // hooks (React 18+)
import { createRoot } from 'react-dom/client';            // root API

function SlowList({ text }) {                              // artificially slow component
  const items = [];                                        // collect rows
  for (let i = 0; i < 1500; i++) {                         // many rows → slow render
    items.push(<li key={i}>{text} - item {i}</li>);        // each row uses the text
  }
  return <ul>{items}</ul>;                                 // render rows
}

function App() {
  const [text, setText] = useState('');                    // urgent state (input)
  const deferredText = useDeferredValue(text);             // lagging copy of the text

  return (
    <div>
      <input
        value={text}                                       // input uses the real value → instant
        onChange={(e) => setText(e.target.value)}          // update on each key
      />
      <SlowList text={deferredText} />                     {/* list uses the lagging value */}
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);
```

## 💻 Code Example — Advanced

```jsx
// Advanced: memoized results + stale indicator + Suspense-friendly structure
import { useState, useDeferredValue, memo, useMemo } from 'react'; // hooks
import { createRoot } from 'react-dom/client';

const RESTAURANTS = Array.from({ length: 8000 }, (_, i) => ({ // fake dataset
  id: i,
  name: `Restaurant ${i} ${i % 3 === 0 ? 'Biryani' : 'Dosa'}`,
}));

// memo is REQUIRED for the benefit: if props are equal, the heavy list skips the urgent render
const ResultList = memo(function ResultList({ query }) {
  const matches = useMemo(                                  // cache filter per query
    () => RESTAURANTS.filter((r) => r.name.toLowerCase().includes(query.toLowerCase())),
    [query]                                                 // recompute only when query changes
  );
  return (
    <ul>
      {matches.slice(0, 300).map((r) => <li key={r.id}>{r.name}</li>)} {/* cap rendered rows */}
    </ul>
  );
});

function SearchPage() {
  const [query, setQuery] = useState('');                   // real input value
  const deferredQuery = useDeferredValue(query);            // lagging value for the heavy part
  const isStale = query !== deferredQuery;                  // true while the background render runs

  return (
    <div>
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}          // urgent update
        placeholder="Search restaurants"
      />
      <div style={{ opacity: isStale ? 0.5 : 1, transition: 'opacity .2s' }}> {/* stale hint */}
        <ResultList query={deferredQuery} />                {/* memo compares deferredQuery only */}
      </div>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<SearchPage />);
```

Re-render behavior: each keystroke triggers two renders of `SearchPage`. In render 1 `deferredQuery` is old, so the memoized `ResultList` is skipped (cheap). In render 2 `deferredQuery` is new, so `ResultList` renders in the background and can be interrupted. Performance impact: the input stays smooth; the total CPU work is similar.

---

## 🟠 Next.js Connection

In a Next.js App Router page the `searchParams` come from the server, but the typed text is Client state. A common pattern: keep the input state on the client, defer it for client-side filtering, and sync the URL with a debounce or a transition. `useDeferredValue` works only in Client Components.

```jsx
// app/search/SearchClient.jsx
'use client';                                               // uses hooks
import { useState, useDeferredValue } from 'react';         // hooks
import ResultList from './ResultList';                      // memoized client list (as above)

export default function SearchClient({ initialItems }) {    // initialItems fetched in a Server Component
  const [q, setQ] = useState('');                           // real input
  const deferredQ = useDeferredValue(q);                    // lagging value
  return (
    <>
      <input value={q} onChange={(e) => setQ(e.target.value)} /> {/* instant typing */}
      <ResultList items={initialItems} query={deferredQ} /> {/* heavy filter uses deferred value */}
    </>
  );
}
```

```jsx
// app/search/page.jsx (Server Component)
import SearchClient from './SearchClient';                  // client island
import { getRestaurants } from '@/lib/restaurants';         // hypothetical data helper

export default async function Page() {
  const items = await getRestaurants();                     // server fetch, no client waterfall
  return <SearchClient initialItems={items} />;             // pass data as props
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Not memoizing the heavy child, so there is no benefit
✅ **Correct:** Wrap the heavy component in `memo` (or `useMemo` the heavy work)

```jsx
// Wrong: the list re-renders in the urgent render too, because it is not memoized
function Page() {
  const [q, setQ] = useState('');
  const dq = useDeferredValue(q);
  return <HeavyList query={dq} />;                          // ❌ HeavyList is a plain component
}

// Right
const HeavyList2 = memo(HeavyListImpl);                     // ✅ skip render when query is unchanged
```

❌ **Mistake 2:** Passing a new object/array each render to `useDeferredValue`
✅ **Correct:** Defer primitives or stable references

```jsx
// Wrong: {text} is a new object each render → deferred value always looks "changed"
const deferred = useDeferredValue({ text });                // ❌ new identity every render

// Right
const deferredText = useDeferredValue(text);                // ✅ primitive string compares by value
```

❌ **Mistake 3:** Using it to reduce network requests
✅ **Correct:** Use a debounce (or TanStack Query with the deferred value as the key, which deduplicates)

```jsx
// Wrong assumption: "deferred value means fewer API calls"
useEffect(() => { fetch(`/api?q=${deferred}`); }, [deferred]); // ❌ still fires for many intermediate values

// Right: debounce the value for network calls, use deferred only for render cost
const debounced = useDebounce(query, 300);                   // ✅ custom hook (topic 206)
```

---

## 🧠 Tricky Interview Question

```jsx
import { useState, useDeferredValue } from 'react';

function App() {
  const [text, setText] = useState('a');
  const deferred = useDeferredValue(text);
  console.log(text, deferred);                               // what is logged after typing "b" quickly?
  return <input value={text} onChange={(e) => setText(e.target.value)} />;
}
```
**Answer:** After the user types "b", the component renders twice. The first pass logs `ab a` (new `text`, old `deferred`), and the background pass logs `ab ab`. If the render is cheap, React finishes the second pass almost immediately, but the first pass always shows the lag. On the very first mount it logs `a a` (no extra render). `useDeferredValue` alone does not make a render faster; it only schedules the second render at lower priority.

---

## ⚫ Interview Questions + Answers

Q1: What does `useDeferredValue` do?
A1: It gives you a version of a value that updates later, at low priority. During urgent updates React keeps showing the old value to the heavy part of the UI, then re-renders it in the background with the new value.

Q2: `useDeferredValue` vs `useTransition`?
A2: `useTransition` wraps the state **setter** call, so you need access to the update code, and it provides `isPending`. `useDeferredValue` wraps a **value**, so it works with props or values you don't control. Use the one that matches where you have control.

Q3: Why do I still need `memo`?
A3: Without `memo`, the component re-renders in the urgent render too with the same cost. With `memo` the child sees equal props during the urgent render and skips; it renders only in the background pass.

Q4: Is it the same as debouncing?
A4: No. There is no fixed time delay. The deferred render starts right away and can be interrupted. On a fast device it may be immediate. Debouncing is better for limiting network calls.

Q5: How do I know the UI is stale?
A5: Compare `value !== deferredValue`. When they differ, the background render is still in progress, so you can fade the list or show a small indicator.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- A value (prop or state) drives an expensive render and typing must stay smooth
- You don't control the setter (value arrives from a parent or library)
- You want old results visible while new ones are computed

❌ **Avoid when:**
- The render is cheap (no need)
- You want fewer network requests (debounce instead)
- The child isn't memoized and the cost is in an unmemoized subtree

---

## 📊 Visual Diagram

```
 text:      "s"  ──────► "sa" ─────────────► "sam"
 deferred:  "s"  ───────"s"──► "sa" ───────► "sa" ──► "sam"
                    │      ▲        │
 render #1 (urgent): input updates, heavy list SKIPPED (memo, same deferred)
 render #2 (background): heavy list renders with the new deferred value
                         (abandoned if a newer value arrives)

 Input  : instant instant instant
 List   : ·····old·····[new]···old···[newer]
 stale? : value !== deferred → show fade
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| useDeferredValue | Hook returning a lagging copy of a value | Value की पीछे चलने वाली copy |
| Deferred value | Value updated at low priority | Low priority पर update होने वाली value |
| Stale UI | UI showing old data while new renders | पुराना data दिखाता UI |
| memo | Skips render when props are equal | Props बराबर हों तो render छोड़ना |
| Background render | Low-priority render pass | Low-priority render pass |
| initialValue | Optional first value (React 19) | शुरुआती value (React 19) |
| Debounce | Delay until activity stops | गतिविधि रुकने तक देरी |
| Concurrent rendering | Prioritised, interruptible rendering | Priority वाली, रुक सकने वाली rendering |

---

## ⚡ 3-Line Summary
**English:**
1. `useDeferredValue` gives a lagging copy of a value so heavy UI updates in the background.
2. Pair it with `memo` and compare `value !== deferred` for a stale indicator.
3. It is not debouncing and does not reduce network requests.

**Hindi:**
1. `useDeferredValue` value की पीछे चलने वाली copy देता है ताकि भारी UI background में update हो।
2. इसे `memo` के साथ इस्तेमाल करो और stale indicator के लिए `value !== deferred` जाँचो।
3. यह debounce नहीं है और network requests कम नहीं करता।

---

## ➡️ Next Topic
**111. useQuery Hook** — अब server data fetch करने के लिए TanStack Query v5 का मुख्य hook। Loading, error और caching सब एक जगह मिलता है।
