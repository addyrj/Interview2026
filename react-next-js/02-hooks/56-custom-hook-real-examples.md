# 56. Custom Hook — Real Examples
# हिंदी में: Custom Hook — असली Projects के उदाहरण

---

## 🔵 Simple Definition (English)
A custom hook is a function whose name starts with `use` and that calls other hooks inside it. It packages reusable stateful logic (debounce, localStorage, online status, fetch) so many components can share it without copying code. Each component that calls it gets its own separate state.

## 🔵 सरल परिभाषा (Hindi)
Custom hook एक function है जिसका नाम `use` से शुरू होता है और जो अंदर दूसरे hooks बुलाता है। यह दोबारा इस्तेमाल होने वाला stateful logic (debounce, localStorage, online status, fetch) पैक करता है ताकि कई components बिना code copy किए उसे इस्तेमाल करें। हर component को अपनी अलग state मिलती है।

---

## 🔴 Problem it Solves

Without custom hooks, the same `useState + useEffect` block gets copy-pasted into every component: search boxes each write their own debounce timer, forms each read localStorage, pages each add `online/offline` listeners. Bugs get fixed in one place and stay in the others. Patterns like HOCs and render props can share logic but add wrapper nesting. Custom hooks share logic with plain function calls.

```jsx
// PROBLEM: the same debounce code copied in SearchBar, AddressForm, FilterPanel ...
const [debounced, setDebounced] = useState(value);
useEffect(() => { const t = setTimeout(() => setDebounced(value), 400); return () => clearTimeout(t); }, [value]);

// SOLUTION: write once, call everywhere
const debounced = useDebounce(value, 400);
```

## 🔴 यह क्यों बना? (Hindi)
Custom hooks के बिना वही `useState + useEffect` block हर component में copy-paste होता है: हर search box अपना debounce timer लिखता है, हर form localStorage पढ़ता है, हर page `online/offline` listeners लगाता है। Bug एक जगह ठीक होता है और बाकी जगह रह जाता है। HOC और render props logic share करते हैं पर wrapper nesting बढ़ाते हैं। Custom hooks सिर्फ function call से logic share करते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Find logic repeated across components (state + effect + handlers)
Step 2 → Move it to a function named useSomething (the "use" prefix is required for lint rules)
Step 3 → Take inputs as arguments (value, key, url) and return what the UI needs
Step 4 → Inside, call normal hooks (useState, useEffect, useRef, useCallback)
Step 5 → Each call of the custom hook creates NEW independent state for that component
Step 6 → Clean up in effects (timers, listeners, aborted requests)

KEY: custom hooks share LOGIC, not STATE. For shared state use context or a store.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → वह logic ढूँढो जो कई components में दोहराया जा रहा है (state + effect + handlers)
Step 2 → उसे useSomething नाम के function में डालो ("use" prefix lint rules के लिए ज़रूरी है)
Step 3 → Inputs arguments से लो (value, key, url) और UI को जो चाहिए वह return करो
Step 4 → अंदर normal hooks बुलाओ (useState, useEffect, useRef, useCallback)
Step 5 → Custom hook की हर call उस component के लिए NEW independent state बनाती है
Step 6 → Effects में cleanup करो (timers, listeners, aborted requests)

KEY: custom hooks LOGIC share करते हैं, STATE नहीं। State share करने के लिए context या store इस्तेमाल करो।
```

---

## 🟡 Real World Example
**Flipkart search box:** The user types "iphone". Calling the API on every keystroke wastes requests, so the page uses `useDebounce(query, 400)` and fetches only after the user pauses. The same hook is reused for the pincode field and the filter price input. The cart page uses `useLocalStorage('recent-searches')`, and the app banner uses `useOnlineStatus()` to show "You are offline".

## 🟡 Real Example Hindi mein
**Flipkart search box:** User "iphone" टाइप करता है। हर keystroke पर API call करना बेकार है, इसलिए page `useDebounce(query, 400)` इस्तेमाल करता है और user के रुकने के बाद ही fetch करता है। यही hook pincode field और filter price input में भी reuse होता है। Cart page `useLocalStorage('recent-searches')` और app banner `useOnlineStatus()` से "You are offline" दिखाता है।

---

## 💻 Code Example — Basic

```jsx
// Basic: useToggle and useDebounce, two tiny custom hooks
import { useState, useEffect, useCallback } from 'react';   // built-in hooks used inside
import { createRoot } from 'react-dom/client';              // React 18/19 root API

// useToggle: boolean state with stable helper functions
function useToggle(initial = false) {
  const [on, setOn] = useState(initial);                    // the boolean
  const toggle = useCallback(() => setOn(v => !v), []);     // stable function, flips the value
  return [on, toggle];                                      // same shape as useState for easy use
}

// useDebounce: returns value only after it stops changing for delay ms
function useDebounce(value, delay = 400) {
  const [debounced, setDebounced] = useState(value);        // latest settled value
  useEffect(() => {
    const id = setTimeout(() => setDebounced(value), delay); // start timer on every change
    return () => clearTimeout(id);                          // cleanup cancels the previous timer
  }, [value, delay]);                                       // restart when value or delay changes
  return debounced;                                         // consumers read the settled value
}

function SearchBar() {
  const [query, setQuery] = useState('');                   // updates on every keystroke
  const debounced = useDebounce(query, 400);                // updates 400ms after typing stops
  const [open, toggleOpen] = useToggle(false);              // filter panel open/closed
  return (
    <div>
      <input value={query} onChange={e => setQuery(e.target.value)} placeholder="Search" />
      <p>Searching for: {debounced}</p>                     {/* would trigger the API call */}
      <button onClick={toggleOpen}>{open ? 'Hide' : 'Show'} filters</button>
      {open && <p>Filters panel</p>}
    </div>
  );
}

createRoot(document.getElementById('root')).render(<SearchBar />);
```

## 💻 Code Example — Advanced

```jsx
// Advanced: useLocalStorage (SSR-safe, syncs across tabs) + useOnlineStatus (useSyncExternalStore)
import { useState, useEffect, useCallback, useSyncExternalStore } from 'react';
import { createRoot } from 'react-dom/client';

// useLocalStorage: like useState, but persisted in localStorage
function useLocalStorage(key, initialValue) {
  // Lazy initializer runs once. typeof window check keeps it safe on the server
  const [value, setValue] = useState(() => {
    if (typeof window === 'undefined') return initialValue;     // no localStorage on server
    try {
      const raw = window.localStorage.getItem(key);             // read saved string
      return raw !== null ? JSON.parse(raw) : initialValue;     // parse or fall back
    } catch {
      return initialValue;                                      // corrupted JSON or blocked storage
    }
  });

  // Save every change. try/catch handles quota-exceeded and private mode
  useEffect(() => {
    try { window.localStorage.setItem(key, JSON.stringify(value)); } catch { /* ignore */ }
  }, [key, value]);

  // Keep other browser tabs in sync: the 'storage' event fires in OTHER tabs only
  useEffect(() => {
    const onStorage = e => {
      if (e.key === key && e.newValue !== null) setValue(JSON.parse(e.newValue));
    };
    window.addEventListener('storage', onStorage);              // subscribe
    return () => window.removeEventListener('storage', onStorage); // unsubscribe on cleanup
  }, [key]);

  const remove = useCallback(() => {
    window.localStorage.removeItem(key);                        // delete from storage
    setValue(initialValue);                                     // reset state
  }, [key, initialValue]);

  return [value, setValue, remove];                             // useState-like API plus remove
}

// useOnlineStatus: subscribes to browser events with the official external-store hook
function subscribe(callback) {
  window.addEventListener('online', callback);                  // tell React when status changes
  window.addEventListener('offline', callback);
  return () => {                                                // unsubscribe function
    window.removeEventListener('online', callback);
    window.removeEventListener('offline', callback);
  };
}
function useOnlineStatus() {
  return useSyncExternalStore(
    subscribe,                                                  // how to listen
    () => navigator.onLine,                                     // client snapshot
    () => true                                                  // server snapshot (assume online)
  );
}

function App() {
  const [recent, setRecent] = useLocalStorage('recent-searches', []);  // persisted list
  const online = useOnlineStatus();                                    // live connection status
  return (
    <div>
      {!online && <p style={{ background: 'orange' }}>You are offline</p>}
      <button onClick={() => setRecent(r => [...r, 'biryani'].slice(-5))}>Add search</button>
      <ul>{recent.map((s, i) => <li key={i}>{s}</li>)}</ul>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);
```

---

## 🟠 Next.js Connection

Custom hooks that use state, effects or browser APIs run only in **Client Components** (`'use client'`). The hook file itself needs no directive if only client files import it, but a file that calls it must be a client file. During SSR the component is rendered once on the server, so touching `window` or `localStorage` while rendering crashes. Read browser APIs inside effects, behind a `typeof window` check, or use `useSyncExternalStore` with a server snapshot. Reading `localStorage` in the `useState` initializer can cause a hydration mismatch (server renders the default, client the saved value), so for visible UI prefer reading it in an effect.

```jsx
// hooks/useDebounce.js (plain hook, usable from any client component)
import { useState, useEffect } from 'react';
export function useDebounce(value, delay = 400) {
  const [debounced, setDebounced] = useState(value);        // server and first client render match
  useEffect(() => {
    const id = setTimeout(() => setDebounced(value), delay); // effects never run on the server
    return () => clearTimeout(id);
  }, [value, delay]);
  return debounced;
}

// app/search/SearchBox.jsx
'use client';                                               // uses hooks → Client Component
import { useState } from 'react';
import { useDebounce } from '@/hooks/useDebounce';
export default function SearchBox() {
  const [q, setQ] = useState('');
  const debounced = useDebounce(q, 400);                    // fetch with this value, not q
  return <input value={q} onChange={e => setQ(e.target.value)} aria-label={`Search ${debounced}`} />;
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Expecting two components to share state because they use the same custom hook
✅ **Correct:** Each call has its own state. Use context, a store or React Query to share.

```jsx
// Wrong: expecting B to see A's change
function A() { const [on, toggle] = useToggle(); return <button onClick={toggle}>{String(on)}</button>; }
function B() { const [on] = useToggle(); return <p>{String(on)}</p>; }   // ❌ always its own false

// Right: lift state up or use context
function Parent() { const [on, toggle] = useToggle(); return <><A2 on={on} toggle={toggle} /><B2 on={on} /></>; }
```

❌ **Mistake 2:** Forgetting effect cleanup (timers and listeners pile up, memory leak, wrong results)
✅ **Correct:** Always return a cleanup function

```jsx
// Wrong: listener added on every run and never removed
useEffect(() => { window.addEventListener('resize', onResize); }, []);  // ❌ leaks

// Right
useEffect(() => {
  window.addEventListener('resize', onResize);
  return () => window.removeEventListener('resize', onResize);          // ✅
}, []);
```

❌ **Mistake 3:** Returning a new object or function on every render so consumers' effects re-run
✅ **Correct:** Stabilize with `useCallback` / `useMemo` when consumers put the result in dependency arrays

```jsx
// Wrong: `refresh` is a new function every render → consumer effect [refresh] loops
function useData() { const refresh = () => {/* ... */}; return { refresh }; }   // ❌

// Right
function useData2() { const refresh = useCallback(() => {/* ... */}, []); return { refresh }; } // ✅
```

---

## 🧠 Tricky Interview Question

```jsx
import { useState } from 'react';

function useCounter() {
  const [count, setCount] = useState(0);
  return { count, inc: () => setCount(count + 1) };
}

function App() {
  const a = useCounter();
  const b = useCounter();
  return (
    <>
      <button onClick={() => { a.inc(); a.inc(); }}>A</button>
      <p>{a.count} {b.count}</p>
    </>
  );
}
```
**Answer:** After one click on A the text shows `1 0`. First, `a` and `b` are independent, so `b.count` stays `0`. Second, `inc` uses `setCount(count + 1)` with the `count` from that render (`0`), so calling it twice queues `setCount(1)` twice, not `1` then `2`. Writing `setCount(c => c + 1)` would give `2 0`. Both updates are batched into one re-render.

---

## ⚫ Interview Questions + Answers

Q1: What is a custom hook and why must it start with `use`?
A1: It is a function that calls other hooks to reuse stateful logic. The `use` prefix lets React's ESLint rules check the Rules of Hooks inside it and tells readers it uses hooks.

Q2: Do custom hooks share state between components?
A2: No. Every call creates independent state. They share logic, not data. To share data use context, Redux/Zustand or a data cache like React Query.

Q3: Custom hook vs a normal utility function?
A3: A utility is a plain function without hooks. A custom hook uses hooks (`useState`, `useEffect`...), so it must follow the Rules of Hooks: only called at the top level of components or other hooks.

Q4: How do you make `useLocalStorage` safe for SSR?
A4: Check `typeof window` before touching storage, wrap reads in try/catch, and avoid reading storage during the first render if it changes visible markup (to prevent a hydration mismatch). Reading in an effect is the safest approach.

Q5: How do you test a custom hook?
A5: Use `renderHook` from React Testing Library, with `act` for updates, and fake timers for debounce. Or test it through a small component that uses it.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- The same state + effect pattern appears in 2 or more components
- You want to hide messy details (listeners, timers, storage) behind a clean API
- You want to test the logic separately from UI

❌ **Avoid when:**
- The logic has no hooks inside (use a plain function)
- You only use it once and it is short (extraction adds indirection)
- You need to share live state between components (use context or a store)

---

## 📊 Visual Diagram

```
  SearchBar              AddressForm            FilterPanel
     │                       │                      │
     │ useDebounce(q)        │ useDebounce(pin)     │ useDebounce(price)
     ▼                       ▼                      ▼
  ┌──────────────┐     ┌──────────────┐      ┌──────────────┐
  │ own state    │     │ own state    │      │ own state    │   ← separate copies
  │ own timer    │     │ own timer    │      │ own timer    │
  └──────┬───────┘     └──────┬───────┘      └──────┬───────┘
         └────────────────────┴─────────────────────┘
                              ▼
               ONE shared definition: useDebounce()   ← logic written once

  Re-render: state change inside the hook → only the component that called it re-renders
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Custom hook | Function starting with `use` that calls hooks | `use` से शुरू होने वाला function जो hooks बुलाता है |
| Debounce | Wait until input stops, then act | Input रुकने तक इंतज़ार, फिर काम |
| Persistence | Keeping data after reload | Reload के बाद भी data बचाना |
| useSyncExternalStore | Hook to read external data sources safely | बाहरी data source सुरक्षित पढ़ने वाला hook |
| Hydration mismatch | Server HTML differs from first client render | Server HTML और पहले client render में फर्क |
| Cleanup | Function returned from an effect | Effect से return होने वाला cleanup function |
| Stable reference | Same function/object across renders | Renders में वही function/object |
| renderHook | Testing helper for hooks | Hooks test करने का helper |

---

## ⚡ 3-Line Summary
**English:**
1. A custom hook is a `use...` function that packages reusable stateful logic with other hooks.
2. Every call gets its own state, so hooks share logic and not data.
3. Always clean up effects, guard browser APIs for SSR, and return stable references.

**Hindi:**
1. Custom hook एक `use...` function है जो दूसरे hooks से reusable stateful logic पैक करता है।
2. हर call की अपनी state होती है, इसलिए hooks logic share करते हैं, data नहीं।
3. Effects का cleanup करो, SSR के लिए browser APIs को guard करो, और stable references return करो।

---

## ➡️ Next Topic
**57. Rules of Hooks — Why These Rules** — Custom hooks लिखते समय सबसे ज़्यादा गलतियाँ rules तोड़ने से होती हैं। अगला topic बताता है कि hooks सिर्फ top level पर क्यों बुलाए जाते हैं और React अंदर से यह कैसे track करता है।
