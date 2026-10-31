# 83. Throttle in React
# हिंदी में: React में Throttle — तेज़ events पर fixed interval में function चलाना

---

## 🔵 Simple Definition (English)
Throttle ek technique hai jisme function ko ek fixed time-interval mein sirf ek baar run kiya jaata hai, chahe event kitni bhi baar fire ho. Scroll, resize, mousemove jaise events par yeh UI ko smooth rakhta hai. React mein throttle ko timestamp ya `requestAnimationFrame` ke saath likhte hain, aur function reference ko stable rakhte hain.

## 🔵 सरल परिभाषा (Hindi)
Throttle एक technique है जिसमें function को एक तय time-interval में सिर्फ एक बार चलाया जाता है, चाहे event कितनी भी बार fire हो। Scroll, resize, mousemove जैसे events पर यह UI को smooth रखता है। React में throttle को timestamp या `requestAnimationFrame` के साथ लिखते हैं, और function reference को stable रखते हैं।

---

## 🔴 Problem it Solves
Scroll karte waqt browser ek second mein 60 se zyada `scroll` events fire karta hai. Har event par agar hum heavy calculation (sticky header, progress bar, analytics) karein, to main thread busy ho jaata hai aur scroll jhatke marta hai. Debounce yahan kaam nahi aata, kyunki woh scroll ruk-ruk ke chalne par hi call karega, aur progress bar ko scroll ke dauran update chahiye. Throttle har interval mein ek update deta hai, jisse UI bhi chalta hai aur kaam bhi kam hota hai.

## 🔴 यह क्यों बना? (Hindi)
Scroll करते समय browser एक second में 60 से ज़्यादा `scroll` events fire करता है। हर event पर heavy calculation (sticky header, progress bar, analytics) करें, तो main thread busy हो जाता है और scroll झटके मारता है। Debounce यहाँ काम नहीं करता, क्योंकि वह scroll रुकने पर ही call करेगा, जबकि progress bar को scroll के दौरान update चाहिए। Throttle हर interval में एक update देता है, जिससे UI भी चलता है और काम भी कम होता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Event aaya → now = Date.now() lo
Step 2 → now - lastRun >= interval? → haan: lastRun = now, fn() chalao
Step 3 → Nahi: call drop karo (ya trailing timer lagao, taaki aakhri value na chhoote)
Step 4 → Trailing timer: interval khatam hone par latest args se ek aur call
Step 5 → Unmount par pending trailing timer clear karo
Step 6 → Scroll/resize ke liye rAF use kar sakte ho: frame mein ek hi update
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Event आया → now = Date.now() लो
Step 2 → now - lastRun >= interval? → हाँ: lastRun = now, fn() चलाओ
Step 3 → नहीं: call drop करो (या trailing timer लगाओ, ताकि आखिरी value न छूटे)
Step 4 → Trailing timer: interval खत्म होने पर latest args से एक और call
Step 5 → Unmount पर pending trailing timer clear करो
Step 6 → Scroll/resize के लिए rAF इस्तेमाल कर सकते हो: एक frame में एक ही update
```

---

## 🟡 Real World Example
**Zerodha / Groww live price ticker:** Market data hazaron baar prices bhejta hai, lekin user ki screen ko ek second mein ek hi update kaafi hai. Throttle se UI har 1000 ms mein refresh hoti hai, aur browser freeze nahi hota. Google Maps mein map drag karte waqt bhi position updates throttle hote hain.

## 🟡 Real Example Hindi mein
**Zerodha / Groww live price ticker:** Market data हज़ारों बार prices भेजता है, लेकिन user की screen को एक second में एक update काफ़ी है। Throttle से UI हर 1000 ms में refresh होता है, और browser freeze नहीं होता। Google Maps में map drag करते समय भी position updates throttle होते हैं।

---

## 💻 Code Example — Basic

```jsx
import { useEffect, useState } from 'react';              // hooks

// ── BASIC THROTTLE: a scroll progress bar ─────────────
function ScrollProgress() {
  const [percent, setPercent] = useState(0);              // how far the user scrolled (0 to 100)

  useEffect(() => {
    let lastRun = 0;                                      // when the handler last ran (ms)
    function handleScroll() {
      const now = Date.now();                             // current time in milliseconds
      if (now - lastRun < 100) return;                    // ran < 100 ms ago → skip this event
      lastRun = now;                                      // remember this run
      const max = document.documentElement.scrollHeight - window.innerHeight; // total scrollable height
      setPercent(max > 0 ? (window.scrollY / max) * 100 : 0); // percent, avoid divide by zero
    }
    window.addEventListener('scroll', handleScroll);      // listen to scroll
    return () => window.removeEventListener('scroll', handleScroll); // cleanup on unmount
  }, []);                                                 // one listener for the whole life of the component

  return (
    <div style={{ position: 'fixed', top: 0, left: 0, height: 4, width: `${percent}%`, background: 'tomato' }} />
  );                                                      // the thin bar at the top
}

export default ScrollProgress;                            // make it importable
```

## 💻 Code Example — Advanced

```jsx
import { useCallback, useEffect, useRef, useState } from 'react'; // hooks

// Generic throttle: leading + trailing call, stable identity via ref, cancel on unmount
function useThrottledCallback(fn, interval = 100) {
  const fnRef = useRef(fn);                               // always the newest fn
  const lastRunRef = useRef(0);                           // time of the last real call
  const timerRef = useRef(null);                          // pending trailing timer
  const lastArgsRef = useRef(null);                       // latest args for the trailing call

  useEffect(() => { fnRef.current = fn; }, [fn]);         // keep the ref fresh

  const throttled = useCallback((...args) => {            // identity never changes
    const now = Date.now();                               // current time
    const remaining = interval - (now - lastRunRef.current); // ms until we may run again
    lastArgsRef.current = args;                           // remember the latest arguments
    if (remaining <= 0) {                                 // enough time has passed
      clearTimeout(timerRef.current);                     // a trailing timer is not needed now
      timerRef.current = null;                            // mark as idle
      lastRunRef.current = now;                           // start a new window
      fnRef.current(...args);                             // LEADING call: run immediately
    } else if (timerRef.current === null) {               // no trailing call scheduled yet
      timerRef.current = setTimeout(() => {               // TRAILING call: keeps the last value
        lastRunRef.current = Date.now();                  // start a new window
        timerRef.current = null;                          // timer done
        fnRef.current(...lastArgsRef.current);           // run with the newest args
      }, remaining);                                      // wait for the rest of the window
    }
  }, [interval]);

  useEffect(() => () => clearTimeout(timerRef.current), []); // cancel pending trailing call on unmount

  return throttled;                                       // hand back the stable throttled function
}

// Example: track the mouse position for a live tooltip, but update React state at most every 50 ms
export function CursorTooltip() {
  const [pos, setPos] = useState({ x: 0, y: 0 });         // position shown in the tooltip
  const update = useThrottledCallback((e) => {            // the expensive state update
    setPos({ x: e.clientX, y: e.clientY });               // React re-renders at most 20 times a second
  }, 50);                                                 // 50 ms window

  useEffect(() => {
    window.addEventListener('mousemove', update);         // raw event fires 100+ times per second
    return () => window.removeEventListener('mousemove', update); // cleanup
  }, [update]);                                           // update is stable, so this runs once

  return <div style={{ position: 'fixed', left: pos.x + 12, top: pos.y + 12 }}>📍 {pos.x},{pos.y}</div>;
}

// requestAnimationFrame variant: at most ONE update per screen frame (best for scroll/drag visuals)
export function useRafCallback(fn) {
  const fnRef = useRef(fn);                               // newest function
  const frameRef = useRef(null);                          // id of the scheduled frame
  const argsRef = useRef(null);                           // latest args

  useEffect(() => { fnRef.current = fn; }, [fn]);         // keep it fresh

  const schedule = useCallback((...args) => {             // call this from event handlers
    argsRef.current = args;                               // keep only the latest event
    if (frameRef.current !== null) return;                // a frame is already scheduled
    frameRef.current = requestAnimationFrame(() => {      // run before the next paint
      frameRef.current = null;                            // frame done
      fnRef.current(...argsRef.current);                  // one update per frame
    });
  }, []);

  useEffect(() => () => cancelAnimationFrame(frameRef.current), []); // cancel on unmount
  return schedule;                                        // stable function
}
```

---

## 🟠 Real app integration

Throttle on the client (UI updates) and rate limiting on the server (incoming traffic) solve different parts of one problem. The Express example below is the server half: it limits how fast one client may send events, such as analytics pings or price polls.

```javascript
const express = require('express');                       // web framework
const rateLimit = require('express-rate-limit');          // server-side throttle per client IP
const app = express();                                    // create the app
app.use(express.json({ limit: '10kb' }));                 // small bodies only (protects memory)

const eventLimiter = rateLimit({                          // throttle analytics events
  windowMs: 1000,                                         // 1 second window
  limit: 10,                                              // at most 10 events per second per IP
  standardHeaders: 'draft-7',                             // modern RateLimit headers
  legacyHeaders: false,                                   // no old X-RateLimit headers
  message: { error: 'Too many events, slow down' },       // JSON body for 429
});

app.post('/api/events', eventLimiter, (req, res) => {     // client sends a batch of UI events
  const events = Array.isArray(req.body.events) ? req.body.events.slice(0, 50) : []; // cap batch size
  // queue events for storage here (never trust client data blindly)
  res.status(202).json({ accepted: events.length });      // 202 Accepted: processed later
});
```

Next.js: the hook above works unchanged in a Client Component (put `'use client'` at the top). The API route stays a Route Handler with the same rate limiting idea.

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Throttle created inside render, so every render has a fresh timer
✅ **Correct:** Create it once (`useRef`/`useCallback`/`useMemo`).

```jsx
// Wrong: each render creates a new throttled function with lastRun = 0
function Panel() {
  const onScroll = throttle(handle, 100);              // ❌ new closure every render
  return <div onScroll={onScroll} />;                  // throttling is ineffective
}

// Right: one throttled function for the component's life
function Panel2() {
  const onScroll = useThrottledCallback(handle, 100);  // ✅ stable identity, shared state
  return <div onScroll={onScroll} />;
}
```

❌ **Mistake 2:** Dropping the last call, so the final position is never applied
✅ **Correct:** Use a trailing call (or `requestAnimationFrame`) so the latest value always arrives.

```javascript
// Wrong: the user stops at y = 900, but the last update was at y = 400
const throttled = throttle(y => setPos(y), 100);     // ❌ no trailing call

// Right: schedule one trailing call with the latest value
// (see useThrottledCallback above: lastArgsRef + setTimeout for the remaining window)
```

❌ **Mistake 3:** Using throttle where debounce is correct (search box) or the reverse (scroll indicator)
✅ **Correct:** Search = debounce (wait for the user to stop). Scroll/drag visuals = throttle (update while moving).

```jsx
// Wrong: throttling a search box sends a request every 300 ms while typing
const search = useThrottledCallback(fetchResults, 300); // ❌ intermediate queries still fire

// Right: debounce the search, throttle the visual update
const searchDebounced = useDebouncedCallback(fetchResults, 300); // ✅ one request at the end
```

---

## 🧠 Tricky Interview Question

```javascript
function throttle(fn, ms) {
  let last = 0;                                          // time of the last allowed call
  return (...args) => {
    const now = Date.now();                              // current time
    if (now - last >= ms) {                              // enough time has passed?
      last = now;                                        // start a new window
      fn(...args);                                       // run the function
    }
  };                                                     // NO trailing call
}

const log = [];
const t = throttle(v => log.push(v), 100);               // allow at most one call per 100 ms
for (let i = 1; i <= 5; i++) t(i);                       // five calls in a tight loop
console.log(log);
```

**Answer:** `[ 1 ]`. `last` starts at `0`, so the first call passes (`now - 0` is far more than 100). The loop finishes in well under 100 ms, so calls 2 to 5 fail the check and are dropped. The value `5` is the most recent one, but it is never delivered, because this throttle has no trailing call. That is why real throttles keep the latest arguments and run them when the window ends.

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between throttle and debounce?**
A1: Throttle runs at most once per interval while events keep coming (scroll tracking). Debounce runs once after events stop for a set delay (search). Throttle gives regular updates during activity, debounce gives one final update.

**Q2: What is a leading versus a trailing throttle?**
A2: Leading runs the first call immediately. Trailing runs the last call when the window ends. A good throttle does both, so the first and last values are always applied.

**Q3: Why is `requestAnimationFrame` a good throttle for scroll?**
A3: The browser calls the frame callback once before each paint (about 60 times per second). Scheduling one update per frame matches the screen refresh exactly, so you never do more visual work than the screen can show.

**Q4: Why keep the throttled function stable in React?**
A4: If it is recreated on each render, its `lastRun` timestamp resets, and the throttle stops working. A ref or `useCallback` keeps one timestamp for the component's lifetime.

**Q5: Can throttle replace server-side rate limiting?**
A5: No. Throttling in React only limits what your UI does. Anyone can call your API directly, so the server needs its own limits (for example `express-rate-limit`).

---

## 🔷 When to Use + When Not to Use

✅ **Use when:**
- Events fire very often: `scroll`, `resize`, `mousemove`, `pointermove`, drag
- You update React state from those events and the UI must stay smooth
- You want regular feedback while the user is still moving

❌ **Avoid when:**
- You only need the final value (use debounce, for search and form validation)
- The event is rare (click, submit): throttling a button just delays the user's action
- The work is already cheap (updating one CSS variable with a ref does not need a state throttle)

---

## 📊 Visual Diagram

```
Events:   e1  e2  e3  e4  e5  e6  e7  e8  e9  e10 e11 e12   (every ~16 ms)
          │   │   │   │   │   │   │   │   │   │   │   │
Window:   |─────── 100 ms ───────|─────── 100 ms ───────|
Run fn:   ▲ e1 (leading)         ▲ e7                   ▲ e12 (trailing, if pending)
Dropped:      e2 e3 e4 e5 e6        e8 e9 e10 e11

Debounce (for comparison):
Events:   e1 e2 ... e12 ───── quiet 300 ms ─────► run once with e12
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Throttle | Fixed interval mein max ek call | Fixed interval में ज़्यादा से ज़्यादा एक call |
| Leading call | Window ki pehli call turant | Window की पहली call तुरंत |
| Trailing call | Window khatam hone par aakhri call | Window खत्म होने पर आखिरी call |
| requestAnimationFrame | Har screen frame se pehle callback | हर screen frame से पहले callback |
| Main thread | Jahan JavaScript aur layout chalta hai | जहाँ JavaScript और layout चलता है |
| Rate limit | Server par ek client ke requests ki limit | Server पर client की requests की limit |

---

## ⚡ 3-Line Summary
**English:**
1. Throttle ek fixed interval mein function ko ek baar chalata hai, scroll/mousemove jaise fast events ke liye.
2. Throttled function ko stable rakho, aur trailing call rakho taaki aakhri value na chhoote.
3. Search ke liye debounce, visual updates ke liye throttle/rAF, aur server par alag se rate limit lagao.

**Hindi:**
1. Throttle एक fixed interval में function को एक बार चलाता है, scroll/mousemove जैसे तेज़ events के लिए।
2. Throttled function को stable रखो, और trailing call रखो ताकि आखिरी value न छूटे।
3. Search के लिए debounce, visual updates के लिए throttle/rAF, और server पर अलग से rate limit लगाओ।

---

## ➡️ Next Topic
**84. React Router v6 — Complete Guide** — client-side routing की बुनियाद: BrowserRouter, Routes, और data router।
