# 52. useTransition Hook
# हिंदी में: useTransition Hook — भारी Updates को Low Priority बनाना

---

## 🔵 Simple Definition (English)
**`useTransition`** lets you mark a state update as a non-urgent "transition". React keeps the UI responsive for urgent work (typing, clicking) and renders the transition in the background. It returns `[isPending, startTransition]`.

## 🔵 सरल परिभाषा (Hindi)
**`useTransition`** से आप किसी state update को non-urgent "transition" mark कर सकते हैं। React urgent काम (typing, click) को तुरंत करता है और transition को background में render करता है। यह `[isPending, startTransition]` return करता है।

---

## 🔴 Problem it Solves

Some state updates trigger expensive renders (filtering 10,000 products, switching to a heavy tab). In React 17 and earlier, every update had the same priority, so a heavy render **blocked** the main thread: the input froze, clicks felt late, and users thought the app hung. Developers added debouncing or manual `setTimeout` tricks, which delay the work but still block the thread when it finally runs.

```jsx
// PROBLEM: typing updates the input AND a heavy list in the same urgent render
function Search() {
  const [q, setQ] = useState('');
  return (
    <>
      <input value={q} onChange={(e) => setQ(e.target.value)} />  {/* feels laggy */}
      <HeavyList query={q} />                                      {/* 200ms render each key */}
    </>
  );
}
// SOLUTION: urgent = input text, non-urgent = the list → startTransition(() => setListQuery(...))
```

## 🔴 यह क्यों बना? (Hindi)
कुछ state updates बहुत भारी renders trigger करते हैं (10,000 products filter करना, भारी tab खोलना)। React 17 तक हर update की priority एक जैसी थी, इसलिए भारी render main thread को **block** कर देता था: input अटक जाता, click देर से होता और user को लगता कि app hang हो गया। Debounce या `setTimeout` से काम सिर्फ देर से होता था, जब चलता तब भी thread block होता था। `useTransition` से urgent और non-urgent updates अलग हो जाते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → const [isPending, startTransition] = useTransition()
Step 2 → On an event, do the urgent update normally: setInput(value)
Step 3 → Wrap the heavy update: startTransition(() => setQuery(value))
Step 4 → React renders the urgent update first (UI stays responsive)
Step 5 → React renders the transition in the background; it can be interrupted and restarted
         if a newer urgent update arrives
Step 6 → isPending is true while the transition is rendering → show a subtle loading hint
Step 7 → When done, React commits the new UI; old UI stayed visible meanwhile (no blank flash)

KEY: transitions do not make the work faster, they make the app stay responsive while it works.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → const [isPending, startTransition] = useTransition()
Step 2 → Event पर urgent update सामान्य तरह करो: setInput(value)
Step 3 → भारी update को wrap करो: startTransition(() => setQuery(value))
Step 4 → React पहले urgent update render करता है (UI responsive रहता है)
Step 5 → React transition को background में render करता है; नया urgent update आए तो
         वह रुक सकता है और दोबारा शुरू हो सकता है
Step 6 → Transition render होने तक isPending true रहता है → हल्का loading hint दिखाओ
Step 7 → पूरा होने पर React नया UI commit करता है; तब तक पुराना UI दिखता रहता है (blank flash नहीं)

KEY: transition काम को तेज़ नहीं करता, काम होते समय app को responsive रखता है।
```

---

## 🟡 Real World Example
**Flipkart category tabs:** A user taps "Mobiles", "Laptops", "Fashion" tabs. Each tab renders hundreds of product cards. Without a transition, tapping a tab freezes the highlighted tab until the whole grid renders. With `useTransition`, the tab highlight changes instantly, the old grid stays visible with a faded look (`isPending`), and the new grid replaces it when ready.

## 🟡 Real Example Hindi mein
**Flipkart category tabs:** User "Mobiles", "Laptops", "Fashion" tabs पर tap करता है। हर tab में सैकड़ों product cards render होते हैं। Transition के बिना tab tap करने पर पूरा grid render होने तक highlighted tab अटका रहता है। `useTransition` से tab highlight तुरंत बदलता है, पुराना grid हल्का (faded, `isPending`) दिखता रहता है और नया grid तैयार होते ही बदल जाता है।

---

## 💻 Code Example — Basic

```jsx
// Basic useTransition: heavy tab switch stays responsive
import { useState, useTransition } from 'react';         // hooks (React 18+)
import { createRoot } from 'react-dom/client';           // root API

function SlowList({ tab }) {                              // simulates an expensive render
  const items = [];                                       // build a big list
  for (let i = 0; i < 2000; i++) {                        // 2000 rows is heavy enough to feel
    items.push(<li key={i}>{tab} product #{i}</li>);      // each row depends on the tab
  }
  return <ul>{items}</ul>;                                // render the list
}

function App() {
  const [tab, setTab] = useState('Mobiles');              // the tab that is actually shown
  const [isPending, startTransition] = useTransition();   // transition controls

  function selectTab(next) {
    startTransition(() => {                               // mark this update as non-urgent
      setTab(next);                                       // heavy render happens in the background
    });
  }

  return (
    <div>
      {['Mobiles', 'Laptops', 'Fashion'].map((t) => (
        <button key={t} onClick={() => selectTab(t)}>{t}</button> // click handler starts a transition
      ))}
      <div style={{ opacity: isPending ? 0.5 : 1 }}>      {/* fade old content while pending */}
        <SlowList tab={tab} />                            {/* old list stays until new one is ready */}
      </div>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);
```

## 💻 Code Example — Advanced

```jsx
// Advanced: separate urgent input state from transition state + memoized heavy child
import { useState, useTransition, memo } from 'react';   // hooks and memo
import { createRoot } from 'react-dom/client';

const PRODUCTS = Array.from({ length: 5000 }, (_, i) => ({ id: i, name: `Product ${i}` })); // fake data

// memo: skip re-render when `query` did not change (the input typing should not re-render this)
const ProductGrid = memo(function ProductGrid({ query }) {
  const filtered = PRODUCTS.filter((p) =>                  // expensive-ish filter
    p.name.toLowerCase().includes(query.toLowerCase())
  );
  return (
    <ul>
      {filtered.slice(0, 500).map((p) => <li key={p.id}>{p.name}</li>)} {/* cap rows to keep DOM sane */}
    </ul>
  );
});

function Catalog() {
  const [text, setText] = useState('');                    // urgent: what the user typed
  const [query, setQuery] = useState('');                  // non-urgent: what the grid uses
  const [isPending, startTransition] = useTransition();    // transition state

  function onChange(e) {
    const value = e.target.value;                          // read before the callback (events pool safe)
    setText(value);                                        // URGENT: input updates immediately
    startTransition(() => {
      setQuery(value);                                     // NON-URGENT: grid may lag, can be interrupted
    });
  }

  return (
    <div>
      <input value={text} onChange={onChange} placeholder="Search products" /> {/* never lags */}
      {isPending && <span role="status"> Updating...</span>} {/* subtle pending hint */}
      <div style={{ opacity: isPending ? 0.6 : 1, transition: 'opacity .2s' }}>
        <ProductGrid query={query} />                      {/* renders with the deferred query */}
      </div>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<Catalog />);
```

Re-render behavior: on each keystroke React renders `Catalog` twice. Render 1 (urgent) has the new `text` and old `query`, with `isPending = true`. Render 2 (transition) has the new `query` and `isPending = false`. `memo` makes sure the grid skips render 1. If another key arrives before render 2 finishes, React abandons render 2 and starts again with the newest value. Performance impact: total work is similar, but input latency stays low.

---

## 🟠 Next.js Connection

In the App Router, navigation is already wrapped in a transition internally. `useTransition` is useful with `router.push` and Server Actions to get an `isPending` flag. In Next.js 15 / React 19, functions passed to `startTransition` can be async (Actions), which is version-dependent (React 19+).

```jsx
// app/components/FilterBar.jsx
'use client';                                              // hooks and router need a Client Component
import { useTransition } from 'react';                     // transition hook
import { useRouter, useSearchParams } from 'next/navigation'; // App Router navigation hooks

export default function FilterBar() {
  const router = useRouter();                              // programmatic navigation
  const params = useSearchParams();                        // current URL query params
  const [isPending, startTransition] = useTransition();    // pending flag for the navigation

  function setCategory(cat) {
    const next = new URLSearchParams(params.toString());   // copy current params
    next.set('category', cat);                             // change the category
    startTransition(() => {
      router.push(`/products?${next.toString()}`);         // server re-renders page; old UI stays visible
    });
  }

  return (
    <div style={{ opacity: isPending ? 0.6 : 1 }}>         {/* fade while the server page loads */}
      <button onClick={() => setCategory('mobiles')}>Mobiles</button>
      <button onClick={() => setCategory('laptops')}>Laptops</button>
    </div>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Putting the controlled input's own state inside `startTransition`
✅ **Correct:** Keep the input state urgent, and transition only the derived/heavy state

```jsx
// Wrong: the text box value update is delayed → typing feels broken, caret may jump
startTransition(() => setText(e.target.value));            // ❌ input must update immediately

// Right
setText(e.target.value);                                   // ✅ urgent for the input
startTransition(() => setQuery(e.target.value));           // ✅ transition for the heavy part
```

❌ **Mistake 2:** Expecting `startTransition` to wait for `await`ed code (React 18)
✅ **Correct:** In React 18, only state updates called synchronously inside the callback are transitions. In React 19, async actions are supported, but state updates after an `await` still need another `startTransition`

```jsx
// Wrong in React 18: update after await is NOT part of the transition
startTransition(async () => {                              // ❌ async callback (React 18 ignores the awaited part)
  const data = await fetch('/api/x').then((r) => r.json());
  setData(data);                                           // runs as a normal urgent update
});

// Right: fetch first, then transition the state update
const data = await fetch('/api/x').then((r) => r.json());  // ✅ do async work outside
startTransition(() => setData(data));                      // ✅ mark only the render as a transition
```

❌ **Mistake 3:** Using transitions for controlled text input values or for fast updates
✅ **Correct:** Use them only for slow renders; if the render is already fast, transitions add complexity for nothing

```jsx
// Wrong: wrapping a trivial counter update
startTransition(() => setCount((c) => c + 1));             // ❌ no benefit, adds a second render

// Right
setCount((c) => c + 1);                                    // ✅ plain update when render is cheap
```

---

## 🧠 Tricky Interview Question

```jsx
import { useState, useTransition } from 'react';

function App() {
  const [count, setCount] = useState(0);
  const [isPending, startTransition] = useTransition();

  function handleClick() {
    startTransition(() => {
      setCount(count + 1);                                 // transition update
    });
    console.log(isPending);                                // what is logged on the first click?
  }
  return <button onClick={handleClick}>{count}</button>;
}
```
**Answer:** It logs `false`. `isPending` is a value from the current render (a snapshot), like any state. It does not change inside the event handler that started the transition. React re-renders with `isPending = true` right after the handler, then with `false` once the transition commits. Also, `setCount(count + 1)` uses the `count` captured in that render, so use the updater form `setCount(c => c + 1)` if multiple updates may be batched.

---

## ⚫ Interview Questions + Answers

Q1: What does `useTransition` do?
A1: It marks state updates as non-urgent. React renders urgent updates first and renders the transition in the background, interruptibly. It returns `isPending` and `startTransition`.

Q2: How is it different from debouncing?
A2: Debouncing delays the update by a fixed time and then still blocks the thread when it renders. A transition starts immediately but can be interrupted by urgent work, and there is no fixed delay. They can also be combined for network requests.

Q3: How is `useTransition` different from `useDeferredValue`?
A3: `useTransition` wraps the code that **sets** state (you control the update). `useDeferredValue` wraps a **value** you receive (for example a prop from a parent you cannot change). Both give lower-priority rendering.

Q4: Can I use a transition to control input values?
A4: No. The controlled input must update synchronously, otherwise typing breaks. Use two states: one urgent for the input, one transitioned for the heavy view.

Q5: Is there a standalone `startTransition`?
A5: Yes. `import { startTransition } from 'react'` works anywhere (outside components too), but it does not give you `isPending`. Use the hook when you need a loading indicator.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- A state update causes a slow render (big lists, charts, heavy tabs)
- You want to keep the old UI visible with a pending hint instead of a blank spinner
- Navigating with `router.push` and you need an `isPending` flag

❌ **Avoid when:**
- The render is already fast (no visible lag)
- It is a controlled input value or a text field
- The slowness is from the network, not from rendering (use loading states or Suspense)

---

## 📊 Visual Diagram

```
 User types "s"
      │
      ├── URGENT lane      : setText("s")     → input shows "s" immediately
      │
      └── TRANSITION lane  : setQuery("s")    → heavy grid render (interruptible)
                                   │
        user types "sa" before it finishes
                                   │
                                   ▼
                       abandon render, restart with "sa"
                                   │
                                   ▼
                  commit once → grid updated, isPending = false

 Timeline:
 input   : ──s──sa──sam────────────────  (always instant)
 grid    : ········[render...]x [render...]x [render.....]✔
 pending : ──true────────────────────false
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Transition | Non-urgent state update | Non-urgent state update |
| startTransition | Function that marks updates as transitions | Updates को transition mark करने वाला function |
| isPending | True while the transition is rendering | Transition चल रहा हो तो true |
| Urgent update | Update needing instant feedback (typing) | तुरंत चाहिए वाला update |
| Interruptible rendering | Render can pause or restart | Render रुक या दोबारा शुरू हो सकता है |
| Concurrent rendering | React can work on several priorities | कई priorities पर काम कर सकना |
| Main thread blocking | Long JS task freezing the UI | लंबा JS task जो UI को अटका दे |
| Debounce | Delaying a call until activity stops | गतिविधि रुकने तक call रोकना |

---

## ⚡ 3-Line Summary
**English:**
1. `useTransition` marks a heavy state update as low priority so urgent work like typing stays instant.
2. It returns `isPending` for a loading hint, and React can interrupt and restart the transition.
3. Do not wrap input values or cheap updates, and do not expect it to fix slow network calls.

**Hindi:**
1. `useTransition` भारी state update को low priority बनाता है ताकि typing जैसा urgent काम तुरंत रहे।
2. `isPending` से loading hint मिलता है, और React transition को रोककर दोबारा शुरू कर सकता है।
3. Input values या सस्ते updates को wrap मत करो, और slow network calls ठीक होने की उम्मीद मत रखो।

---

## ➡️ Next Topic
**53. useDeferredValue Hook** — वही goal, लेकिन तब जब state का setter आपके control में नहीं होता (जैसे parent से आया prop)। `useTransition` के बाद इसे तुरंत समझो।
