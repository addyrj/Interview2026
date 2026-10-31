# 82. Debounce in React
# हिंदी में: React में Debounce — बार-बार चलने वाले function को रुककर एक बार चलाना

---

## 🔵 Simple Definition (English)
Debounce ek technique hai jisme function ko tab tak call nahi kiya jaata jab tak user kuch der ke liye ruk na jaaye. Har nayi call pichli pending call ka timer reset kar deti hai, aur aakhri call ke baad ek fixed delay (jaise 300 ms) par function chalta hai. React mein yeh search box aur resize jaise events ke liye use hota hai.

## 🔵 सरल परिभाषा (Hindi)
Debounce एक technique है जिसमें function तब तक call नहीं होता जब तक user कुछ देर के लिए रुक न जाए। हर नई call पिछली pending call का timer reset कर देती है, और आखिरी call के बाद एक तय delay (जैसे 300 ms) पर function चलता है। React में यह search box और resize जैसे events के लिए use होता है।

---

## 🔴 Problem it Solves
User search box mein "biryani" type karta hai, to har keystroke par API call jaayegi: "b", "bi", "bir"... yaani 7 requests. Server par load badhta hai, responses alag-alag order mein aate hain (race condition), aur UI flicker karta hai. Debounce 7 keystrokes ko ek request mein badal deta hai, jo user ke ruk jaane ke baad jaati hai.

## 🔴 यह क्यों बना? (Hindi)
User search box में "biryani" type करता है, तो हर keystroke पर API call जाएगी: "b", "bi", "bir"... यानी 7 requests। Server पर load बढ़ता है, responses अलग-अलग order में आते हैं (race condition), और UI flicker करता है। Debounce 7 keystrokes को एक request में बदल देता है, जो user के रुक जाने के बाद जाती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Input change hone par debounced function call karo
Step 2 → Pichla timer (if any) clearTimeout se hatao
Step 3 → Naya setTimeout(fn, 300) set karo
Step 4 → Agar 300 ms mein nayi call nahi aayi → timer chal jaata hai → fn(value) run
Step 5 → Component unmount par pending timer clear karo (cleanup)
Step 6 → Stale responses ko AbortController se cancel karo
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Input बदलने पर debounced function call करो
Step 2 → पिछला timer (अगर है) clearTimeout से हटाओ
Step 3 → नया setTimeout(fn, 300) सेट करो
Step 4 → 300 ms में नई call न आए → timer चलता है → fn(value) run
Step 5 → Unmount पर pending timer clear करो (cleanup)
Step 6 → पुराने responses को AbortController से cancel करो
```

---

## 🟡 Real World Example
**Swiggy restaurant search:** User "chicken" type karta hai. Debounce ki wajah se "c", "ch", "chi" par koi request nahi jaati. Jab user 300 ms ruk jaata hai, tab sirf "chicken" ke liye ek request jaati hai. Server ka load kam rehta hai, aur results mein purane keywords ka jhatka nahi aata. Flipkart ka search suggestion bhi isi tarah kaam karta hai.

## 🟡 Real Example Hindi mein
**Swiggy restaurant search:** User "chicken" type करता है। Debounce की वजह से "c", "ch", "chi" पर कोई request नहीं जाती। जब user 300 ms रुक जाता है, तब सिर्फ "chicken" के लिए एक request जाती है। Server का load कम रहता है, और results में पुराने keywords का झटका नहीं आता। Flipkart का search suggestion भी इसी तरह काम करता है।

---

## 💻 Code Example — Basic

```jsx
import { useEffect, useState } from 'react';              // hooks

// ── BASIC DEBOUNCE: a hook that delays a VALUE ────────
function useDebouncedValue(value, delay = 300) {          // generic hook, reusable
  const [debounced, setDebounced] = useState(value);      // the delayed copy of the value
  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay); // wait, then copy the value
    return () => clearTimeout(timer);                     // new value comes → cancel old timer
  }, [value, delay]);                                     // runs whenever value or delay changes
  return debounced;                                       // components use the delayed value
}

function RestaurantSearch() {
  const [query, setQuery] = useState('');                 // what the user types (updates every key)
  const debouncedQuery = useDebouncedValue(query, 300);   // updates 300 ms after typing stops
  const [results, setResults] = useState([]);             // search results

  useEffect(() => {
    if (debouncedQuery.trim() === '') {                   // empty search
      setResults([]);                                     // clear the list, no request
      return;                                             // stop here
    }
    fetch(`/api/restaurants?q=${encodeURIComponent(debouncedQuery)}`) // one request per pause
      .then(res => res.json())                            // parse JSON
      .then(setResults);                                  // store the results
  }, [debouncedQuery]);                                   // fires only when the delayed value changes

  return (
    <div>
      <input
        value={query}                                     // controlled: input shows the instant value
        onChange={e => setQuery(e.target.value)}          // update on every keystroke (cheap)
        placeholder="Search restaurants"                  // hint text
      />
      <ul>{results.map(r => <li key={r.id}>{r.name}</li>)}</ul> {/* show matches */}
    </div>
  );
}

export default RestaurantSearch;                          // make it importable
```

## 💻 Code Example — Advanced

```jsx
import { useCallback, useEffect, useRef, useState } from 'react'; // hooks

// Debounced CALLBACK hook: stable identity, always calls the LATEST fn, with cancel and flush
function useDebouncedCallback(fn, delay = 300) {
  const fnRef = useRef(fn);                               // always holds the newest fn
  const timerRef = useRef(null);                          // holds the pending timer id
  const argsRef = useRef(null);                           // last arguments, for flush()

  useEffect(() => { fnRef.current = fn; }, [fn]);         // refresh the ref after each render

  const debounced = useCallback((...args) => {            // same identity across renders
    argsRef.current = args;                               // remember the latest arguments
    clearTimeout(timerRef.current);                       // cancel the previous timer
    timerRef.current = setTimeout(() => {                 // schedule the call
      timerRef.current = null;                            // timer finished
      fnRef.current(...argsRef.current);                  // call the newest function
    }, delay);
  }, [delay]);                                            // only delay can change identity

  const cancel = useCallback(() => {                      // drop the pending call
    clearTimeout(timerRef.current);                       // stop the timer
    timerRef.current = null;                              // mark as idle
  }, []);

  const flush = useCallback(() => {                       // run the pending call NOW
    if (timerRef.current !== null) {                      // only if one is waiting
      cancel();                                           // stop the timer first
      fnRef.current(...argsRef.current);                  // then run immediately
    }
  }, [cancel]);

  useEffect(() => cancel, [cancel]);                      // cancel the timer on unmount

  return { debounced, cancel, flush };                    // expose the three controls
}

export function ProductSearch() {
  const [query, setQuery] = useState('');                 // input text
  const [items, setItems] = useState([]);                 // matching products
  const controllerRef = useRef(null);                     // AbortController for the last request

  const search = useCallback((text) => {                  // the expensive action
    controllerRef.current?.abort();                       // cancel the previous request
    if (text.trim().length < 2) {                         // too short to search
      setItems([]);                                       // clear results
      return;                                             // no request
    }
    const controller = new AbortController();             // new controller for this request
    controllerRef.current = controller;                   // store it
    fetch(`/api/products/search?q=${encodeURIComponent(text)}`, { signal: controller.signal }) // request
      .then(res => res.json())                            // parse
      .then(setItems)                                     // show results
      .catch(err => { if (err.name !== 'AbortError') console.error(err); }); // ignore cancels
  }, []);                                                 // no reactive values inside

  const { debounced, cancel } = useDebouncedCallback(search, 400); // debounced version of search

  useEffect(() => () => controllerRef.current?.abort(), []); // abort on unmount

  function handleChange(e) {
    setQuery(e.target.value);                             // input updates instantly
    debounced(e.target.value);                            // search runs after a pause
  }

  function handleClear() {
    setQuery('');                                         // reset the input
    cancel();                                             // drop any pending search
    setItems([]);                                         // clear the results
  }

  return (
    <div>
      <input value={query} onChange={handleChange} placeholder="Search products" /> {/* controlled input */}
      <button onClick={handleClear}>Clear</button>        {/* cancels pending work */}
      <ul>{items.map(p => <li key={p.id}>{p.name}</li>)}</ul> {/* results */}
    </div>
  );
}
```

---

## 🟠 Real app integration

Express search endpoint that is safe to receive debounced (and not-so-debounced) traffic:

```javascript
const express = require('express');                       // web framework
const rateLimit = require('express-rate-limit');          // per-IP rate limiting (server-side throttle)
const app = express();                                    // create the app
// db is a pg Pool created elsewhere

const searchLimiter = rateLimit({                         // limit abusive or buggy clients
  windowMs: 60 * 1000,                                    // 1 minute window
  limit: 120,                                             // max 120 requests per IP per minute
  standardHeaders: 'draft-7',                             // send RateLimit headers
  legacyHeaders: false,                                   // skip old X-RateLimit headers
});

app.get('/api/restaurants', searchLimiter, async (req, res) => { // GET /api/restaurants?q=
  const q = typeof req.query.q === 'string' ? req.query.q.trim() : ''; // validate type
  if (q.length < 2 || q.length > 50) {                    // reject tiny or huge input
    return res.status(400).json({ error: 'Query must be 2 to 50 characters' }); // 400
  }
  const { rows } = await db.query(                        // parameterized query
    `SELECT id, name FROM restaurants WHERE name ILIKE $1 LIMIT 20`, // LIKE with wildcards
    [`%${q}%`]                                            // parameter, never string concatenation
  );
  res.json(rows);                                         // array of matches
});
```

Next.js: the same hook, used in a Client Component (`'use client'` at the top of the file) inside a Server-rendered page.

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Creating the debounced function inside the component body (new timer on every render)
✅ **Correct:** Keep one debounced function across renders with `useRef`, `useMemo`, or `useCallback`.

```jsx
// Wrong: every render makes a NEW debounced function with its own timer
function Search() {
  const [q, setQ] = useState('');
  const debounced = debounce(v => fetchResults(v), 300); // ❌ new function each render
  return <input onChange={e => debounced(e.target.value)} />; // no call is ever delayed together
}

// Right: the same debounced function survives renders
function Search2() {
  const [q, setQ] = useState('');
  const debounced = useMemo(() => debounce(v => fetchResults(v), 300), []); // ✅ created once
  return <input onChange={e => debounced(e.target.value)} />;
}
```

❌ **Mistake 2:** Debouncing the input value itself, so typing lags
✅ **Correct:** Keep the input value instant, and debounce only the side effect (the API call).

```jsx
// Wrong: the input value comes from the delayed value, so letters appear late
const debounced = useDebouncedValue(query, 300);
<input value={debounced} onChange={e => setQuery(e.target.value)} />; // ❌ typing feels broken

// Right: the input uses the instant value, the request uses the delayed one
<input value={query} onChange={e => setQuery(e.target.value)} />;     // ✅ instant
useEffect(() => { fetchResults(debouncedQuery) }, [debouncedQuery]);  // ✅ delayed side effect
```

❌ **Mistake 3:** No cleanup, so timers fire after unmount
✅ **Correct:** Clear the timer in the effect cleanup or in an unmount effect.

```jsx
// Wrong: the timer keeps running after the user left the page
useEffect(() => {
  setTimeout(() => setResults(data), 300);             // ❌ no cleanup, setState after unmount
}, [data]);

// Right: cancel the timer when the value changes or the component unmounts
useEffect(() => {
  const t = setTimeout(() => setResults(data), 300);   // start the timer
  return () => clearTimeout(t);                        // ✅ cleanup
}, [data]);
```

---

## 🧠 Tricky Interview Question

```jsx
function Search() {
  const [query, setQuery] = useState('');              // input text
  const [log, setLog] = useState([]);                  // every call that actually ran

  // A plain debounce, created INSIDE the component (on every render)
  function debounce(fn, ms) {
    let timer;                                         // lives in this debounce's closure
    return (v) => {
      clearTimeout(timer);                             // clears ONLY this closure's timer
      timer = setTimeout(() => fn(v), ms);
    };
  }
  const debounced = debounce(v => setLog(prev => [...prev, v]), 300); // new fn per render

  return (
    <input
      value={query}
      onChange={e => {
        setQuery(e.target.value);
        debounced(e.target.value);                     // one call per keystroke
      }}
    />
  );
}
// The user types "a", then "b", then "c" within 100 ms. What is in `log` after 300 ms?
```

**Answer:** `log` is `['a', 'b', 'c']`. The debounce does **not** work here. Each keystroke runs a new render, and each render creates a new `debounce` closure with its own `timer` variable. The `onChange` handler from that render calls the `debounced` from that render, so the `clearTimeout` never touches the timers of the earlier renders. Each of the three timers runs and calls `setLog`. The fix is to create the debounced function once (`useMemo` or `useRef`), so all three calls share one `timer` variable and only `'c'` is logged.

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between debounce and throttle?**
A1: Debounce waits until the calls stop for a set time, then runs once (search box). Throttle runs at most once per interval while calls keep coming (scroll tracking). Debounce answers "what is the final value?", throttle answers "how often can I update?".

**Q2: Why do we store the timer in `useRef`?**
A2: A plain variable is recreated on every render, so the timer id is lost. A ref keeps the same object across renders, and `clearTimeout` can reach the pending timer.

**Q3: Why use a ref for the latest function in a debounced callback?**
A3: The timer fires later, with the function that existed when it was scheduled. Storing the function in a ref (updated each render) lets the timer call the newest `fn` without recreating the debounced function, which keeps its identity stable.

**Q4: Should you debounce a controlled input's value?**
A4: No. The controlled input must update on every keystroke or the typing lags. Keep the input state instant and debounce only the expensive work, like the API call.

**Q5: How do you avoid showing results for an old query?**
A5: Cancel the previous request with `AbortController` when a new search starts, and ignore responses whose query no longer matches the input. Debounce reduces the requests, but it does not fix out-of-order responses by itself.

---

## 🔷 When to Use + When Not to Use

✅ **Use when:**
- Input triggers an API call (search, autocomplete, validation against a server)
- Window or element resize triggers expensive layout work
- You want fewer requests and a calmer UI

❌ **Avoid when:**
- The action must happen on every event (drawing, live cursor position, slider drag with live preview)
- The delay makes the app feel broken (very short delays still feel instant; test the timing)
- The work is cheap and local (filtering 20 items in memory does not need debounce)

---

## 📊 Visual Diagram

```
User types:      b    i    r    i    y    a    n    i
                 │    │    │    │    │    │    │    │
Timer (300 ms):  ├─x──├─x──├─x──├─x──├─x──├─x──├─x──┤──300ms quiet──► fn("biryani")
                 each keystroke CLEARS the old timer and starts a new one

Without debounce:  8 requests  ───► /search?q=b, /search?q=bi, ... /search?q=biryani
With debounce:     1 request   ───► /search?q=biryani

Input value (instant):    b bi bir biri biryani  (state updates every key)
Debounced value (delayed):                        biryani (state updates after pause)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Debounce | Calls ke rukne ke baad hi ek baar run karna | Calls रुकने के बाद एक बार चलाना |
| Timer | `setTimeout` ka id, jisse cancel kar sakte hain | `setTimeout` का id |
| clearTimeout | Pending timer ko cancel karna | Pending timer cancel करना |
| Race condition | Responses ka galat order mein aana | Responses का गलत order में आना |
| Stale closure | Purana variable value hold karna | पुरानी value पकड़ कर रखना |
| Flush | Pending call ko turant run karna | Pending call को तुरंत चलाना |

---

## ⚡ 3-Line Summary
**English:**
1. Debounce har call par timer reset karta hai, aur user ruk jaane ke baad ek baar function chalata hai.
2. Debounced function ko stable rakho (`useRef`/`useMemo`/`useCallback`), warna har render par naya timer ban jaata hai.
3. Input value instant rakho, sirf API call ko debounce karo, aur cleanup/abort karna mat bhoolo.

**Hindi:**
1. Debounce हर call पर timer reset करता है, और user के रुकने के बाद एक बार function चलाता है।
2. Debounced function को stable रखो (`useRef`/`useMemo`/`useCallback`), वरना हर render पर नया timer बन जाता है।
3. Input value को instant रखो, सिर्फ API call को debounce करो, और cleanup/abort करना मत भूलो।

---

## ➡️ Next Topic
**83. Throttle in React** — scroll और mousemove जैसे events पर fixed interval में ज़्यादा से ज़्यादा एक call।
