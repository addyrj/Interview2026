# 40. useRef — Complete Guide
# हिंदी में: useRef — DOM Access और Persistent Values

---

## 🔵 Simple Definition (English)
`useRef` returns a **mutable ref object** with a `.current` property. Two main uses: (1) **Access DOM elements directly** (focus, measure, animate). (2) **Store a value that persists across renders without triggering re-render** — unlike state, changing `.current` does NOT cause a re-render.

## 🔵 सरल परिभाषा (Hindi)
`useRef` एक **mutable ref object** return करता है जिसमें `.current` property होती है। दो main uses: (1) **DOM elements directly access करना** (focus, measure, animate). (2) **एक value store करना जो renders में persist करे बिना re-render trigger किए** — state के उलट, `.current` बदलने से re-render नहीं होता।

---

## 🔴 Problem it Solves
```jsx
// Problem 1: Can't access DOM elements in React declaratively
// e.g., focus an input, measure element width, scroll to position

// Problem 2: Need to store value across renders WITHOUT re-rendering
// e.g., previous value, timer ID, whether component is mounted
// useState would cause infinite re-render loop for these!
```

## 🔴 यह क्यों बना? (Hindi)
```jsx
// Problem 1: React declaratively काम करता है लेकिन कभी-कभी
// direct DOM access चाहिए — focus, scroll, measure

// Problem 2: कभी-कभी value render में persist चाहिए
// बिना re-render trigger किए — timer ID, previous value, etc.
// useState इन cases में infinite loop बनाता!
```

---

## 🟢 How it Works — Step by Step

```
TWO USES OF useRef:

USE 1 — DOM Reference:
Step 1 → const inputRef = useRef(null)
Step 2 → <input ref={inputRef} />   ← React attaches DOM node to inputRef.current
Step 3 → inputRef.current.focus()  ← direct DOM access!
Step 4 → React sets inputRef.current = null on unmount

USE 2 — Persistent Value (no re-render):
Step 1 → const timerRef = useRef(null)
Step 2 → timerRef.current = setInterval(...)  ← store value
Step 3 → clearInterval(timerRef.current)      ← read value
Step 4 → Changing .current NEVER triggers re-render

KEY DIFFERENCE from useState:
  state change → re-render → UI updates ✓
  ref change   → NO re-render → .current updated silently
```

## 🟢 कैसे काम करता है? (Hindi)
```
USE 1 — DOM Reference:
Step 1 → const inputRef = useRef(null)
Step 2 → <input ref={inputRef} />  ← React DOM node inputRef.current में रखता है
Step 3 → inputRef.current.focus() ← direct DOM access!

USE 2 — Persistent Value:
Step 1 → const countRef = useRef(0)
Step 2 → countRef.current++        ← value change
Step 3 → Re-render नहीं होता!      ← state से फर्क

KEY DIFFERENCE:
  state बदला → re-render → UI update
  ref बदला   → NO re-render → .current silently update
```

---

## 🟡 Real World Example
**Zomato Search Bar:** When the page loads, the search input auto-focuses. You press ESC, it blurs. You click the search icon, it focuses again. All these use `useRef` to get the actual input DOM element and call `.focus()` / `.blur()` directly — you can't do this with state alone.

## 🟡 Real Example Hindi mein
**Zomato Search Bar:** Page load पर search input auto-focus। ESC press पर blur। Search icon click पर focus। यह सब `useRef` से input DOM element मिलाकर `.focus()` / `.blur()` directly call होता है — state से यह possible नहीं।

---

## 💻 Code Example — Basic

```jsx
import { useState, useRef, useEffect } from 'react';

// ── USE 1: DOM ACCESS ─────────────────────
function SearchPage() {
  const inputRef = useRef(null); // initially null — DOM not mounted yet

  // Auto-focus on mount
  useEffect(() => {
    inputRef.current?.focus(); // .current is the <input> DOM node
  }, []);

  const handleClear = () => {
    inputRef.current.value = ''; // direct DOM manipulation
    inputRef.current.focus();    // re-focus after clear
  };

  return (
    <div>
      <input
        ref={inputRef}            // React attaches DOM node here
        type="text"
        placeholder="Search restaurants..."
      />
      <button onClick={handleClear}>Clear</button>
    </div>
  );
}

// ── USE 2: STORE VALUE WITHOUT RE-RENDER ──
function StopWatch() {
  const [time, setTime] = useState(0);       // triggers re-render (for display)
  const intervalRef = useRef(null);           // stores timer ID (no re-render needed)

  const start = () => {
    if (intervalRef.current) return;          // already running
    intervalRef.current = setInterval(() => {
      setTime(t => t + 1);
    }, 1000);
    // If we used useState for intervalRef:
    // setIntervalId(id) → re-render → setInterval called again → infinite loop!
  };

  const stop = () => {
    clearInterval(intervalRef.current);
    intervalRef.current = null;               // reset ref
  };

  const reset = () => {
    stop();
    setTime(0);
  };

  return (
    <div>
      <p>Time: {time}s</p>
      <button onClick={start}>Start</button>
      <button onClick={stop}>Stop</button>
      <button onClick={reset}>Reset</button>
    </div>
  );
}
```

## 💻 Code Example — Advanced

```jsx
import { useState, useRef, useEffect, useCallback } from 'react';

// ── TRACK PREVIOUS VALUE ─────────────────
// Classic useRef pattern — previous render's value
function usePrevious(value) {
  const prevRef = useRef(undefined);

  useEffect(() => {
    prevRef.current = value; // runs AFTER render — captures previous
  });

  return prevRef.current; // value from PREVIOUS render
}

function PriceDisplay({ price }) {
  const prevPrice = usePrevious(price);
  const direction = price > prevPrice ? '↑' : price < prevPrice ? '↓' : '→';

  return (
    <div>
      ₹{price} <span>{direction}</span>
      {prevPrice !== undefined && <small> (was ₹{prevPrice})</small>}
    </div>
  );
}

// ── IS MOUNTED CHECK ─────────────────────
// Prevent setState on unmounted component
function useIsMounted() {
  const isMounted = useRef(false);

  useEffect(() => {
    isMounted.current = true;
    return () => { isMounted.current = false; }; // cleanup on unmount
  }, []);

  return isMounted;
}

function AsyncComponent({ id }) {
  const [data, setData] = useState(null);
  const isMounted = useIsMounted();

  useEffect(() => {
    fetch(`/api/data/${id}`)
      .then(r => r.json())
      .then(result => {
        if (isMounted.current) { // only update if still mounted!
          setData(result);
        }
        // Without this check: setData on unmounted component → memory leak warning
      });
  }, [id]);

  return <div>{data?.name}</div>;
}

// ── SCROLL TO BOTTOM ─────────────────────
// Chat app — scroll to latest message
function ChatWindow({ messages }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    // Scroll to bottom when messages change
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="chat-window">
      {messages.map(msg => (
        <div key={msg.id} className="message">{msg.text}</div>
      ))}
      <div ref={bottomRef} /> {/* invisible element at bottom */}
    </div>
  );
}

// ── VIDEO PLAYER CONTROL ──────────────────
function VideoPlayer({ src }) {
  const videoRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);

  const toggle = useCallback(() => {
    if (!videoRef.current) return;

    if (isPlaying) {
      videoRef.current.pause(); // direct DOM API
    } else {
      videoRef.current.play().catch(console.error);
    }
    setIsPlaying(p => !p);
  }, [isPlaying]);

  return (
    <div>
      <video ref={videoRef} src={src} />
      <button onClick={toggle}>
        {isPlaying ? '⏸ Pause' : '▶ Play'}
      </button>
    </div>
  );
}
```

---

## 🟠 Next.js Connection

```jsx
// useRef works in Next.js Client Components
// In Next.js Server Components: refs don't apply (no DOM on server)

'use client';
// app/components/InfiniteScroll.jsx
import { useRef, useEffect, useState } from 'react';

function InfiniteScrollList({ fetchMore }) {
  const [items, setItems] = useState([]);
  const [page, setPage] = useState(1);
  const loaderRef = useRef(null); // ref to "load more" trigger element

  useEffect(() => {
    // Intersection Observer — load more when bottom visible
    const observer = new IntersectionObserver(
      entries => {
        if (entries[0].isIntersecting) {
          setPage(p => p + 1);
        }
      },
      { threshold: 1.0 }
    );

    if (loaderRef.current) observer.observe(loaderRef.current);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    fetchMore(page).then(newItems => setItems(prev => [...prev, ...newItems]));
  }, [page]);

  return (
    <div>
      {items.map(item => <div key={item.id}>{item.name}</div>)}
      <div ref={loaderRef}>Loading more...</div>
    </div>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using ref for values that should trigger UI updates
```jsx
// WRONG: using ref where state is needed
function Counter() {
  const countRef = useRef(0);

  return (
    <div>
      <p>{countRef.current}</p>          {/* ❌ won't update in UI! */}
      <button onClick={() => countRef.current++}>Add</button>
      {/* clicking does change countRef.current but UI never updates! */}
    </div>
  );
}

// CORRECT: use state for UI values
function Counter() {
  const [count, setCount] = useState(0);
  return (
    <div>
      <p>{count}</p>
      <button onClick={() => setCount(c => c + 1)}>Add</button>
    </div>
  );
}
```

❌ **Mistake 2:** Reading ref.current during render
```jsx
// WRONG: ref.current may not be set during render
function Bad() {
  const divRef = useRef(null);
  const width = divRef.current?.offsetWidth; // ❌ null during first render!

  return <div ref={divRef}>Width: {width}</div>;
}

// CORRECT: read in useEffect (after DOM mounted)
function Good() {
  const divRef = useRef(null);
  const [width, setWidth] = useState(0);

  useEffect(() => {
    setWidth(divRef.current.offsetWidth); // ✅ DOM mounted now
  }, []);

  return <div ref={divRef}>Width: {width}px</div>;
}
```

---

## 🧠 Tricky Interview Question

```jsx
function Component() {
  const [count, setCount] = useState(0);
  const countRef = useRef(count);

  useEffect(() => {
    countRef.current = count;
  });

  const handleAlertClick = () => {
    setTimeout(() => {
      alert(`count state: ${count}, countRef: ${countRef.current}`);
    }, 3000);
  };

  return (
    <button onClick={handleAlertClick}>
      Count: {count} (click then increment fast)
    </button>
  );
}
```
**Answer:** If you click the button (starts 3s timer) and then increment count 5 times: `count state: 0` (stale closure captures 0), `countRef: 5` (ref always has latest). This is the ref pattern for "latest value in callbacks" — refs escape stale closure.

---

## ⚫ Interview Questions + Answers

**Q1: What is useRef and what are its two main uses?**
A1: `useRef(initialValue)` returns `{ current: initialValue }` — a mutable container that persists for the component's lifetime. Use 1: DOM reference — `<div ref={myRef} />` makes `myRef.current` point to the DOM node. Use 2: Persistent mutable value — store anything that needs to survive re-renders without causing re-renders (timer IDs, previous values, flags, third-party instances).

**Q2: What is the difference between useRef and useState?**
A2: Both persist across renders. Key differences: `useState` — changing value triggers re-render, value is immutable (must use setter), used for values that drive the UI. `useRef` — changing `.current` does NOT trigger re-render, directly mutable (`ref.current = x`), used for values the UI doesn't need to display (timer IDs, DOM refs, previous values, flags).

**Q3: When should you use useRef instead of a variable declared outside the component?**
A3: Variables outside a component are shared across ALL instances. `useRef` gives each component instance its own value. Example: a timer ID — if declared outside, two `<Timer />` components would share it, clearing each other's timers. With `useRef`, each Timer has its own isolated `intervalRef.current`.

**Q4: Can you explain the "previous value" pattern with useRef?**
A4: After render, `useEffect` (with no deps) updates `prevRef.current = currentValue`. When the component renders next time, `prevRef.current` still holds the value from the PREVIOUS render (because `useEffect` hasn't run yet). The function returns `prevRef.current` which is the previous render's value. This works because refs are set after render, so during render you see the previous render's ref value.

**Q5: How does forwardRef work with useRef?**
A5: By default, `ref` prop doesn't work on custom components — React doesn't know where to attach it. `React.forwardRef` lets a component receive a `ref` from its parent and forward it to a DOM element inside. `const Input = forwardRef((props, ref) => <input ref={ref} {...props} />)`. Parent: `<Input ref={inputRef} />` → `inputRef.current` is the `<input>` DOM node.

---

## 🔷 When to Use + When Not to Use
✅ **Use useRef when:**
- Need direct DOM access (focus, scroll, measure, canvas, video)
- Storing timer/interval IDs
- Storing previous render's values
- Storing third-party library instances (D3, Chart.js)
- Tracking mount status (avoid setState on unmounted)

❌ **Don't use useRef when:**
- Value change should update the UI → use `useState`
- Computing derived values → compute inline or `useMemo`
- Storing component-independent globals → module-level variable

---

## 📊 Visual Diagram

```
useRef vs useState:
───────────────────────────────────────────────────
                useState        useRef
                ───────         ──────
  Change causes  re-render       NO re-render
  Update method  setState()      ref.current = x
  Used for       UI display      DOM, timers, flags
  Persists?      Yes             Yes

DOM REF LIFECYCLE:
───────────────────────────────────────────────────
  Mount:    ref.current = null
               ↓
            <div ref={myRef} /> renders
               ↓
            ref.current = <div> DOM node ✅
               ↓
            useEffect runs → use ref.current here!

  Unmount:  ref.current = null (cleanup)

PERSISTENT VALUE (no re-render):
───────────────────────────────────────────────────
  Render 1  → intervalRef.current = null
  click     → intervalRef.current = setInterval(...)
  Render 2  → intervalRef.current still has timer ID ✅
  (no re-render triggered by the assignment!)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Ref object | `{ current: value }` container | `{ current: value }` container |
| DOM ref | Reference to actual DOM node | Actual DOM node का reference |
| Persistent value | Value surviving re-renders | Re-renders में survive करने वाली value |
| forwardRef | Pass ref through component | Component के through ref pass करना |
| Mutable | Can be changed directly | Directly बदला जा सकता है |
| Stale closure | Old captured variable value | पुरानी captured variable value |

---

## ⚡ 3-Line Summary
**English:**
1. `useRef` has two uses: DOM element reference (`<div ref={myRef}>`) and persistent mutable value (timer IDs, flags, previous values).
2. Unlike `useState`, changing `ref.current` does NOT trigger a re-render — it's invisible to React's render cycle.
3. Read `ref.current` in event handlers or `useEffect`, never during render (DOM not yet mounted on first render).

**Hindi:**
1. `useRef` के दो uses: DOM element reference (`<div ref={myRef}>`) और persistent mutable value (timer IDs, flags, previous values)।
2. `useState` के उलट, `ref.current` बदलने से re-render नहीं होता — React के render cycle को दिखता ही नहीं।
3. `ref.current` event handlers या `useEffect` में read करो, render के दौरान नहीं (first render पर DOM mounted नहीं होता)।

---

## ➡️ Next Topic
**41. useRef vs useState** — कब क्या use करना है — decision guide और common patterns।
