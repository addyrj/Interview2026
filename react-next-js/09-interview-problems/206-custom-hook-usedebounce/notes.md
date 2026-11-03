# 206. Build Custom Hook — useDebounce
# हिंदी में: Custom Hook — useDebounce बनाना

> Code: [useDebounce.js](./useDebounce.js) (complete, tested with jsdom: value settles only after the delay)

---

## 🔵 Simple Definition (English)
**useDebounce** is a custom hook that returns a copy of a value which updates only after the original value has stopped changing for a set delay (for example 300 ms). It is used to avoid doing expensive work on every keystroke.

## 🔵 सरल परिभाषा (Hindi)
**useDebounce** एक custom hook है जो किसी value की ऐसी copy लौटाता है जो तभी बदलती है जब असली value तय delay (जैसे 300 ms) तक बदलना बंद कर दे। इसका इस्तेमाल हर keystroke पर भारी काम से बचने के लिए होता है।

---

## 🔴 Problem it Solves
A search box that calls an API on every keystroke sends 10 requests to find "biryani". That wastes bandwidth, overloads the server, and shows flickering results. Debouncing waits until the user pauses typing and then sends just one request.

## 🔴 यह क्यों बना? (Hindi)
जो search box हर keystroke पर API बुलाता है, वह "biryani" खोजने के लिए 7 requests भेजता है। इससे bandwidth बर्बाद होती है, server पर बोझ पड़ता है, और results झिलमिलाते हैं। Debounce तब तक रुकता है जब तक user typing रोक न दे, और फिर सिर्फ एक request भेजता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Input state updates instantly on every keystroke (the box stays responsive)
Step 2 → useDebounce(value, delay) keeps a second state: debounced
Step 3 → Each time value changes, the effect starts setTimeout(delay)
Step 4 → If value changes again before the timer fires, cleanup clears the old timer
Step 5 → When typing stops for delay ms, the timer fires and updates debounced
Step 6 → Your search effect depends on debounced, so it runs once

Re-render: typing "abc" quickly renders the component 3 times (input state), plus one more
render when debounced updates. The API effect runs once.
Performance: saves N-1 requests. The timer is cheap. Do not confuse with throttle (see Q&A).
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Input state हर keystroke पर तुरंत बदलती है (box responsive रहता है)
Step 2 → useDebounce(value, delay) दूसरी state रखता है: debounced
Step 3 → value बदलने पर effect setTimeout(delay) शुरू करता है
Step 4 → Timer चलने से पहले value फिर बदले तो cleanup पुराना timer साफ़ कर देता है
Step 5 → Typing delay ms तक रुके तो timer चलता है और debounced बदलती है
Step 6 → आपका search effect debounced पर depend करता है, इसलिए वह एक बार चलता है

Re-render: "abc" जल्दी टाइप करने पर component 3 बार render होता है (input state), और debounced
बदलने पर एक बार और। API वाला effect एक ही बार चलता है।
Performance: N-1 requests बचती हैं। Timer सस्ता है। Throttle से confuse मत करना (Q&A देखें)।
```

---

## 🟡 Real World Example
**Zomato search bar:** you type "pizza" fast. The text shows instantly, but the app waits 400 ms after the last letter before asking the server for suggestions. One request goes out, not five.

## 🟡 Real Example Hindi mein
**Zomato search bar:** आप "pizza" जल्दी टाइप करते हो। Text तुरंत दिखता है, पर app आखिरी अक्षर के 400 ms बाद ही server से suggestions माँगता है। पाँच नहीं, एक request जाती है।

---

## 💻 Code Example — Basic

```jsx
// Basic: the hook itself
import { useState, useEffect } from 'react';               // hooks

export function useDebounce(value, delay = 300) {
  const [debounced, setDebounced] = useState(value);       // slow copy of the value

  useEffect(() => {
    const id = setTimeout(() => setDebounced(value), delay); // update after the pause
    return () => clearTimeout(id);                         // value changed: cancel the old timer
  }, [value, delay]);                                      // restart on every change

  return debounced;                                        // consumers use this value
}
```

## 💻 Code Example — Advanced

```jsx
// Real search box: instant typing, debounced + cancellable requests
import { useState, useEffect } from 'react';
import { createRoot } from 'react-dom/client';
import { useDebounce } from './useDebounce';

function Search() {
  const [query, setQuery] = useState('');                  // instant input value
  const debounced = useDebounce(query.trim(), 400);        // settled value (trimmed)
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!debounced) { setResults([]); return undefined; }  // empty query: clear results
    const controller = new AbortController();              // cancel if the query changes again
    setLoading(true);
    fetch(`/api/search?q=${encodeURIComponent(debounced)}`, { signal: controller.signal })
      .then((r) => r.json())
      .then((data) => { setResults(data); setLoading(false); })
      .catch((e) => { if (e.name !== 'AbortError') setLoading(false); });
    return () => controller.abort();                       // cleanup
  }, [debounced]);                                         // runs only when the debounced value changes

  return (
    <div>
      <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search dishes" />
      {query !== debounced && <small>Typing...</small>}    {/* optional hint while waiting */}
      {loading ? <p>Loading...</p> : <ul>{results.map((r) => <li key={r.id}>{r.name}</li>)}</ul>}
    </div>
  );
}

createRoot(document.getElementById('root')).render(<Search />);
```

Callback version: if you need to debounce a **function** (not a value), keep it in a ref and
create the timer with `useRef` + `useMemo`, so the debounced function keeps the same identity.

---

## 🟠 Next.js Connection
In the App Router, a common pattern is to debounce the input and push the value into the **URL search params**, so the Server Component page re-renders with fresh data (shareable, bookmarkable URLs). The debounce keeps the router from navigating on every keystroke.

```jsx
// app/search/SearchBox.jsx
'use client';                                             // uses hooks and router
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';              // App Router navigation
import { useDebounce } from '@/hooks/useDebounce';

export default function SearchBox({ initial = '' }) {
  const [q, setQ] = useState(initial);                    // instant value
  const debounced = useDebounce(q, 400);                  // settled value
  const router = useRouter();

  useEffect(() => {
    router.replace(`/search?q=${encodeURIComponent(debounced)}`); // server page re-renders with new q
  }, [debounced, router]);

  return <input value={q} onChange={(e) => setQ(e.target.value)} />;
}
// The page.jsx (Server Component) reads `await searchParams` and queries the database.
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Forgetting the cleanup (`clearTimeout`)
✅ **Correct:** Always clear the previous timer

```jsx
// Wrong: every keystroke leaves a timer running → many updates, wrong final value possible
useEffect(() => { setTimeout(() => setDebounced(value), delay); }, [value]);
// Right
useEffect(() => { const id = setTimeout(...); return () => clearTimeout(id); }, [value]);
```

❌ **Mistake 2:** Debouncing the input's own state (the box lags)
✅ **Correct:** Debounce only the value used for expensive work

```jsx
// Wrong: <input value={debounced} /> → text appears late and feels broken
// Right: <input value={query} />  and use `debounced` for the API call
```

❌ **Mistake 3:** Creating the debounced function inside render without `useMemo`/`useRef`
✅ **Correct:** Keep one timer across renders

```jsx
// Wrong: new debounce() every render → each has its own timer → nothing is debounced
const onChange = debounce(fn, 300);
// Right: const onChange = useMemo(() => debounce(fn, 300), []); (and clear on unmount)
```

---

## 🧠 Tricky Interview Question

```jsx
function App() {
  const [text, setText] = useState('');
  const debounced = useDebounce(text, 300);
  useEffect(() => { console.log('effect:', JSON.stringify(debounced)); }, [debounced]);
  // user types "a", "b", "c" within 100 ms total, then stops
  return <input onChange={(e) => setText(e.target.value)} />;
}
```
**Answer:** The console shows `effect: ""` once on mount (the initial value), then after 300 ms of silence `effect: "abc"` once. The intermediate values "a" and "ab" never reach `debounced`, because each new keystroke clears the previous timer. Note the initial run: the effect also fires on mount with the initial value, so guard it if you do not want a request for an empty query.

---

## ⚫ Interview Questions + Answers

Q1: What is debounce?
A1: A technique that delays running a function until a quiet period has passed since the last call. Only the last call in a burst runs.

Q2: Debounce vs throttle?
A2: Debounce runs once after the events stop (search box). Throttle runs at most once per interval while events continue (scroll, resize). Debounce waits; throttle samples.

Q3: Why does the hook return a value rather than a function?
A3: Value debouncing fits React's declarative model: effects depend on the settled value. A function debounce needs a stable timer across renders (ref/useMemo), which is easier to get wrong.

Q4: How do you handle slow responses arriving out of order?
A4: Debounce reduces the number of requests, but it does not remove races. Also cancel with `AbortController` in the effect cleanup (or use TanStack Query, which handles stale queries).

Q5: What delay should you choose?
A5: 250 to 500 ms for search typing feels responsive but saves requests. Shorter for autocomplete, longer for expensive operations. Always test with real users.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- Search-as-you-type, autocomplete
- Saving a draft after the user stops typing
- Validating a field with a server check

❌ **Avoid when:**
- You need regular updates during activity (use throttle: scroll, drag, resize)
- The action must run immediately (button clicks, submit)
- The work is cheap and instant (filtering 20 items locally)

---

## 📊 Visual Diagram

```
 keystrokes:  a    b   c                  (pause 400ms)
 time ──────► |----|---|--------------------|──────────►
 timers:      ⏱(x) ⏱(x) ⏱────────────────► fires → debounced = "abc"
              cancelled cancelled
 input state: "a" → "ab" → "abc"          (instant, every key)
 API calls:                                1 call with "abc"
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Debounce | Run after the activity stops | गतिविधि रुकने के बाद चलाना |
| Throttle | Run at most once per interval | हर अंतराल में अधिकतम एक बार |
| Delay | Quiet time to wait | इंतज़ार का समय |
| setTimeout | Schedules a function later | बाद में function चलाना |
| clearTimeout | Cancels a scheduled function | तय किया हुआ function रद्द करना |
| Cleanup | Effect's return function | Effect का लौटाया function |
| Search params | Query string in the URL | URL का query string |

---

## ⚡ 3-Line Summary
**English:**
1. `useDebounce` returns a value that updates only after the input has been quiet for `delay` ms.
2. It uses `setTimeout` in an effect and `clearTimeout` in cleanup, so only the last value wins.
3. In Next.js combine it with `router.replace` and search params so Server Components fetch once per pause.

**Hindi:**
1. `useDebounce` ऐसी value लौटाता है जो input के `delay` ms शांत रहने के बाद ही बदलती है।
2. यह effect में `setTimeout` और cleanup में `clearTimeout` इस्तेमाल करता है, इसलिए सिर्फ आखिरी value जीतती है।
3. Next.js में इसे `router.replace` और search params के साथ जोड़ो ताकि Server Components हर pause पर एक बार fetch करें।

---

## ➡️ Next Topic
**207. Build Custom Hook — useOnClickOutside** — अब DOM events और refs: dropdown या modal को बाहर click करने पर बंद करना।
