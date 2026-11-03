# 193. Build Search with Debounce
# हिंदी में: Debounce के साथ Search बनाना

Code: [`App.jsx`](./App.jsx) in this folder (debounce hook, AbortController cancellation, loading / error / empty states, fake API so it runs anywhere).

---

## 🔵 Simple Definition (English)
Search with debounce waits until the user **stops typing** for a short time (for example 400 ms) before calling the API. Instead of one request per keystroke, you send one request for the final text.

## 🔵 सरल परिभाषा (Hindi)
Debounce वाला search तब तक इंतज़ार करता है जब तक user थोड़ी देर (जैसे 400 ms) **टाइप करना बंद** न कर दे, फिर API बुलाता है। हर keystroke पर एक request की जगह, अंतिम text के लिए सिर्फ एक request जाती है।

---

## 🔴 Problem it Solves

Typing "biryani" fires 7 requests: "b", "bi", "bir"... That wastes bandwidth and server money, can hit rate limits, and causes **race conditions**: a slow response for "bi" may arrive after the response for "biryani" and overwrite the correct results. Debounce reduces the number of calls; cancelling stale requests fixes the order problem.

```jsx
// PROBLEM: request on every keystroke, and old responses can overwrite new ones
<input onChange={async (e) => {
  const res = await fetch(`/api/search?q=${e.target.value}`);   // 7 calls for "biryani"
  setResults(await res.json());                                  // late response wins ❌
}} />
```

## 🔴 यह क्यों बना? (Hindi)
"biryani" टाइप करने पर 7 requests जाती हैं: "b", "bi", "bir"... इससे bandwidth और server का पैसा बर्बाद होता है, rate limit लग सकती है, और **race condition** होती है: "bi" का धीमा response "biryani" के response के बाद आकर सही results को बदल सकता है। Debounce calls घटाता है; पुरानी requests cancel करने से क्रम की समस्या ठीक होती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → query state updates on EVERY keystroke (input stays responsive)
Step 2 → useDebounce(query, 400) starts a timer each time query changes
Step 3 → A new keystroke clears the previous timer (cleanup of the effect)
Step 4 → If 400 ms pass with no typing, the timer fires → debounced value updates
Step 5 → An effect depending on [debounced] runs and calls the API
Step 6 → The effect creates an AbortController; its cleanup aborts the previous request
Step 7 → Show loading, error, empty states; render results

Typing b-i-r quickly: timers for "b", "bi" are cancelled → only "bir" reaches the API
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → query state हर keystroke पर बदलती है (input तेज़ रहता है)
Step 2 → useDebounce(query, 400) query बदलने पर हर बार timer शुरू करता है
Step 3 → नया keystroke पिछला timer clear कर देता है (effect का cleanup)
Step 4 → अगर 400 ms तक typing नहीं हुई, timer चलता है → debounced value बदलता है
Step 5 → [debounced] पर निर्भर effect चलकर API बुलाता है
Step 6 → Effect एक AbortController बनाता है; उसका cleanup पिछली request abort करता है
Step 7 → loading, error, empty states दिखाओ; results render करो

b-i-r जल्दी टाइप करने पर: "b", "bi" के timers रद्द → सिर्फ "bir" API तक पहुँचता है
```

---

## 🟡 Real World Example
**Zomato / Swiggy search bar and Amazon autosuggest:** as you type "pizz", the app waits a moment and then asks for suggestions. Google Maps and Flipkart do the same. Without debounce, their servers would receive millions of extra requests per minute.

## 🟡 Real Example Hindi mein
**Zomato / Swiggy की search bar और Amazon autosuggest:** जैसे ही आप "pizz" टाइप करते हैं, app थोड़ा रुककर suggestions माँगता है। Google Maps और Flipkart भी यही करते हैं। Debounce के बिना उनके servers पर हर मिनट लाखों अतिरिक्त requests आएँगी।

---

## 💻 Code Example — Basic

```jsx
// Reusable debounce hook: returns `value` after `delay` ms without changes
import { useState, useEffect } from 'react';

export function useDebounce(value, delay = 400) {
  const [debounced, setDebounced] = useState(value);         // delayed copy
  useEffect(() => {
    const id = setTimeout(() => setDebounced(value), delay); // schedule the update
    return () => clearTimeout(id);                           // cancel if value changes first
  }, [value, delay]);                                        // restart on change
  return debounced;
}

export default function Search() {
  const [query, setQuery] = useState('');                    // instant value for the input
  const debounced = useDebounce(query, 400);                 // delayed value for the API
  return (
    <>
      <input value={query} onChange={(e) => setQuery(e.target.value)} />
      <p>Will search for: {debounced}</p>                    {/* updates 400ms after typing stops */}
    </>
  );
}
```

## 💻 Code Example — Advanced

The complete component is in [`App.jsx`](./App.jsx). The core effect:

```jsx
useEffect(() => {
  const q = debounced.trim();                                // ignore spaces
  if (!q) { setResults([]); return; }                        // empty query → clear results
  const controller = new AbortController();                  // one controller per request
  setLoading(true);
  setError(null);
  fakeSearch(q, controller.signal)                           // real app: fetch(url, { signal })
    .then(setResults)
    .catch((err) => { if (err.name !== 'AbortError') setError('Search failed'); }) // cancel is not an error
    .finally(() => { if (!controller.signal.aborted) setLoading(false); });
  return () => controller.abort();                           // cleanup: cancel stale request
}, [debounced]);                                             // only when the debounced value changes
```

Verified with jsdom: typing "bi" shows nothing for the first 100 ms, then returns exactly "Biryani" after debounce + fake network delay.

A TanStack Query v5 version does the cancel/race handling for you:

```jsx
import { useQuery } from '@tanstack/react-query';             // v5
const { data, isFetching, error } = useQuery({
  queryKey: ['search', debounced],                           // key changes → new request, old one ignored
  queryFn: ({ signal }) =>                                   // signal is passed automatically
    fetch(`/api/search?q=${encodeURIComponent(debounced)}`, { signal }).then((r) => r.json()),
  enabled: debounced.trim().length > 0,                      // do not run for empty text
  placeholderData: (prev) => prev,                           // v5: keep old results while loading
});
```

---

## 🟠 Next.js Connection

In the App Router, debounce the input in a Client Component and store the query in the **URL** (`?q=`). The Server Component page reads `searchParams` and fetches on the server, so results are shareable and SEO-friendly.

```jsx
// app/search/SearchBox.jsx
'use client';
import { useRouter, useSearchParams } from 'next/navigation';
import { useState, useEffect } from 'react';
import { useDebounce } from '@/hooks/useDebounce';            // the hook above

export default function SearchBox() {
  const router = useRouter();
  const params = useSearchParams();
  const [q, setQ] = useState(params.get('q') ?? '');          // start from the URL
  const debounced = useDebounce(q, 400);
  useEffect(() => {
    router.replace(`/search?q=${encodeURIComponent(debounced)}`); // replace: no history spam
  }, [debounced, router]);
  return <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search..." />;
}
```

```jsx
// app/search/page.jsx (Server Component)
import SearchBox from './SearchBox';
import { searchFood } from '@/lib/search';                    // hypothetical server function

export default async function Page({ searchParams }) {
  const { q = '' } = await searchParams;                      // Next.js 15: Promise (14: plain object)
  const results = q ? await searchFood(q) : [];               // runs on the server per request
  return (<><SearchBox /><ul>{results.map((r) => <li key={r.id}>{r.name}</li>)}</ul></>);
}
```
Version-dependent: `useSearchParams` may need a `<Suspense>` boundary in production builds.

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Debouncing the input's own state, so the input feels laggy
✅ **Correct:** Keep the input value instant; debounce only the value used for the API call.

```jsx
// Wrong: the text appears 400ms after typing
const debouncedSet = debounce(setQuery, 400);
<input onChange={(e) => debouncedSet(e.target.value)} value={query} />  // ❌ controlled input freezes

// Right
<input value={query} onChange={(e) => setQuery(e.target.value)} />     // ✅ instant
const debounced = useDebounce(query, 400);                              // delayed copy
```

❌ **Mistake 2:** Creating a new debounced function on every render (`debounce(fn)` inside the component)
✅ **Correct:** The timer id is lost on each render, so nothing is debounced. Use the value-based hook, or `useMemo`/`useRef` to keep the function.

```jsx
// Wrong: a fresh debounce each render, each with its own timer
const search = debounce((q) => fetchResults(q), 400);                   // ❌ recreated every render

// Right: debounce the value, not the function
const debounced = useDebounce(query, 400);                              // ✅ one timer in the hook
```

❌ **Mistake 3:** Ignoring race conditions and unmount
✅ **Correct:** Abort the previous request in the cleanup (or use an `ignore` flag).

```jsx
// Wrong: late response for "bi" overwrites "biryani"
useEffect(() => { fetch(url).then(r => r.json()).then(setResults); }, [debounced]); // ❌

// Right
useEffect(() => {
  const c = new AbortController();
  fetch(url, { signal: c.signal }).then(r => r.json()).then(setResults).catch(() => {});
  return () => c.abort();                                               // ✅
}, [debounced]);
```

---

## 🧠 Tricky Interview Question

```jsx
function App() {
  const [text, setText] = useState('');
  const debounced = useDebounce(text, 500);
  console.log('render', text, debounced);
  return <input value={text} onChange={(e) => setText(e.target.value)} />;
}
// The user types "ab" quickly (both keys within 500ms), then waits 1 second.
// What is logged (ignore the very first mount log)?
```
**Answer:** `render a ` → `render ab ` → (after ~500 ms) `render ab ab`. Each keystroke updates `text` and re-renders; `debounced` stays at its old value `''` because the timer for "a" was cleared by the effect cleanup when "ab" arrived. Only one timer finishes, 500 ms after the last key, calling `setDebounced('ab')`, which triggers one more render. So there are 3 renders after mount for 2 keystrokes, and only the last one has the new debounced value. Debounce does not reduce renders caused by typing; it reduces the work driven by the debounced value.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between debounce and throttle?
A1: Debounce waits until activity stops, then fires once (good for search input). Throttle fires at most once per interval during continuous activity (good for scroll or resize handlers). Debounce delays the first call; throttle usually allows the first immediately.

Q2: How does `useDebounce` work?
A2: It keeps a copy of the value in state. An effect sets a timer to update the copy after `delay`; the cleanup clears the timer when the value changes first. So the copy changes only after the value has been stable for `delay` ms.

Q3: What is a race condition in search and how do you fix it?
A3: Responses can return out of order, so an old response replaces newer results. Fix by cancelling the previous request with `AbortController`, by an `ignore` flag in the effect cleanup, or by using TanStack Query where the query key identifies the latest request.

Q4: Why is an `AbortError` ignored in the catch block?
A4: Aborting is intentional when the query changes or the component unmounts. Treating it as a failure would flash an error message and call state setters after unmount.

Q5: How do you choose the delay?
A5: Typically 250 to 500 ms: shorter feels responsive but sends more requests; longer feels slow. Combine with a minimum length (for example 2 characters) and caching of previous queries. Test with real users and network speed.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- An action triggers expensive work per keystroke (API search, autosuggest, validation calls)
- You auto-save a form while the user types

❌ **Avoid when:**
- The work is cheap and local (filtering 20 items in memory: just compute it)
- You need immediate feedback on every key (character counter, UI preview)
- The user must press a button anyway (explicit submit)

---

## 📊 Visual Diagram

```
 keystrokes:   b   i   r   .....(400ms pause).....   y
 query:        b → bi → bir ──────────────────────▶  biry
 timers:       T1  T2  T3 (T1,T2 cleared)  fires ✔   T4 ...
 debounced:    ''  ''  ''  ──────────────▶  "bir"
 API calls:                                 GET q=bir   (only one)
                                            previous call (if any) is ABORTED
 
 Components:  [input: instant]  →  [useDebounce]  →  [effect + AbortController]  →  [results]

 Re-render: every keystroke re-renders (state), one extra render when debounced updates,
 one for loading, one for results.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Debounce | Wait for a pause, then run once | रुकने के बाद एक बार चलाना |
| Throttle | Run at most once per interval | एक interval में अधिकतम एक बार |
| AbortController | Cancels fetch requests | Fetch request रद्द करने का tool |
| Race condition | Out-of-order async results | Async results का उल्टे क्रम में आना |
| Cleanup function | Returned from useEffect to undo work | useEffect का सफ़ाई वाला function |
| Autosuggest | Suggestions while typing | टाइप करते समय सुझाव |
| queryKey | TanStack Query cache identity | TanStack Query में cache की पहचान |
| Controlled input | Input value held in state | State में रखा input value |

---

## ⚡ 3-Line Summary
**English:**
1. Keep the typed text in state for instant UI, and a debounced copy (via a timer + cleanup) for the API call.
2. Abort stale requests with `AbortController` so old responses cannot overwrite new ones.
3. In Next.js store the query in the URL and let a Server Component fetch the results.

**Hindi:**
1. टाइप किया text तुरंत UI के लिए state में रखो, और API call के लिए debounced copy (timer + cleanup से) रखो।
2. `AbortController` से पुरानी requests रद्द करो ताकि पुराने responses नए को न बदलें।
3. Next.js में query को URL में रखो और results Server Component से fetch करवाओ।

---

## ➡️ Next Topic
**194. Build Infinite Scroll** — page के नीचे पहुँचने पर अपने-आप अगला data लोड करना, `IntersectionObserver` और pagination state के साथ।
