# 58. Component Lifecycle (Class)
# हिंदी में: Class Component Lifecycle — Component बनने, बदलने और हटने का सफ़र

---

## 🔵 Simple Definition (English)
A **class component lifecycle** is the set of special methods React calls at fixed moments of a component's life: when it is **created and shown (mount)**, when it **re-renders (update)**, and when it is **removed (unmount)**. You hook your side effects (timers, API calls, subscriptions) into these methods.

## 🔵 सरल परिभाषा (Hindi)
Class component का lifecycle उन special methods का set है जिन्हें React component की life के तय समय पर call करता है: जब वह **बनता और दिखता है (mount)**, जब वह **दोबारा render होता है (update)**, और जब वह **हटाया जाता है (unmount)**। Timers, API calls और subscriptions इन्हीं methods में लगाए जाते हैं।

---

## 🔴 Problem it Solves

Components often need to do things **outside** rendering: start a timer, fetch data from a server, subscribe to a WebSocket, or update the DOM directly. These are called **side effects**. `render()` must stay pure (same input, same JSX, no side effects), so React needs well-defined moments where side effects are allowed. Without lifecycle methods, you would have no reliable place to start a timer or to clean it up, and leaked timers would keep running after the user left the page.

```jsx
// PROBLEM: where do we start and stop the timer?
function OrderTimer({ orderId }) {
  // Calling setInterval here runs on EVERY render → many timers stack up!
  setInterval(() => console.log('tick'), 1000); // ❌ leaks, never cleared
  return <p>Order {orderId}</p>;
}
```

## 🔴 यह क्यों बना? (Hindi)
Component अक्सर render के **बाहर** के काम करता है: timer शुरू करना, server से data लाना, WebSocket subscribe करना। इन्हें side effects कहते हैं। `render()` pure रहना चाहिए, इसलिए React को तय जगहें चाहिए जहाँ side effects चल सकें। Lifecycle methods के बिना timer कब शुरू और कब बंद करें, यह तय करना मुश्किल था, और leaked timers user के page छोड़ने के बाद भी चलते रहते थे।

---

## 🟢 How it Works — Step by Step

```
Step 1 → constructor(props)      → state set up, runs ONCE when instance is created
Step 2 → render()                → returns JSX. Must be PURE (no setState here!)
Step 3 → DOM is updated          → React commits the JSX to the real DOM
Step 4 → componentDidMount()     → runs ONCE after first commit: start timers, fetch data
Step 5 → (props/state change)    → render() again, then componentDidUpdate(prevProps, prevState)
Step 6 → componentWillUnmount()  → runs ONCE before removal: clear timers, unsubscribe
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → constructor(props)      → state तैयार, सिर्फ एक बार (instance बनते समय)
Step 2 → render()                → JSX लौटाता है। PURE होना चाहिए (यहाँ setState नहीं!)
Step 3 → DOM update होता है      → React JSX को असली DOM में commit करता है
Step 4 → componentDidMount()     → पहली commit के बाद एक बार: timer चालू, data fetch
Step 5 → (props/state बदलें)    → फिर से render(), फिर componentDidUpdate(prevProps, prevState)
Step 6 → componentWillUnmount()  → हटने से पहले एक बार: timer बंद, unsubscribe
```

---

## 🟡 Real World Example
**Swiggy order tracking:** When the "Track Order" screen opens, `componentDidMount` starts a 5-second poll to the order API. When the user switches to another order, `componentDidUpdate` sees the new `orderId` prop and restarts polling for that order. When the user leaves the screen, `componentWillUnmount` clears the interval. Without the cleanup step, every visit would leave one more poller running in the background.

## 🟡 Real Example Hindi mein
**Swiggy order tracking:** जब "Track Order" screen खुलती है, `componentDidMount` हर 5 सेकंड में order API को poll करना शुरू करता है। User दूसरे order पर जाए तो `componentDidUpdate` नया `orderId` prop देखकर उसी order के लिए polling दोबारा शुरू करता है। Screen छोड़ते ही `componentWillUnmount` interval बंद करता है। Cleanup न हो तो हर visit पर एक और poller background में चलता रहता।

---

## 💻 Code Example — Basic

```jsx
// Class component lifecycle basics: constructor, render, mount, update, unmount
import React from 'react';                       // needed for React.Component (class base)
import { createRoot } from 'react-dom/client';   // React 18/19 way to render into the DOM

class OrderTimer extends React.Component {       // class component: extends React.Component
  constructor(props) {                           // runs FIRST, once, when instance is created
    super(props);                                // must call super(props) before using "this"
    this.state = { seconds: 0 };                 // the ONLY place we assign this.state directly
    console.log('1. constructor');               // logs when the instance is created
  }

  componentDidMount() {                          // runs ONCE, after the first render is in the DOM
    console.log('3. componentDidMount');         // safe place for timers, fetch, subscriptions
    this.timerId = setInterval(() => {           // start a repeating timer (every 1000 ms)
      this.setState(prev => ({ seconds: prev.seconds + 1 })); // functional update: uses latest state
    }, 1000);                                    // interval length in milliseconds
  }

  componentDidUpdate(prevProps) {                // runs after EVERY update, but NOT the first render
    if (prevProps.orderId !== this.props.orderId) { // compare old prop with new prop
      console.log('4. componentDidUpdate: new order', this.props.orderId); // react to the change
      this.setState({ seconds: 0 });             // reset the timer for the new order
    }
  }

  componentWillUnmount() {                       // runs ONCE, just before the component is removed
    clearInterval(this.timerId);                 // MUST clean up, otherwise the timer leaks forever
    console.log('5. componentWillUnmount');      // confirms cleanup happened
  }

  render() {                                     // must be PURE: no setState, no side effects
    console.log('2. render');                    // runs before componentDidMount, and on each tick
    return <p>Order {this.props.orderId}: {this.state.seconds}s</p>; // what the user sees
  }
}

const root = createRoot(document.getElementById('root')); // find <div id="root"> in the page
root.render(<OrderTimer orderId="ZOM-101" />);             // mount the component
setTimeout(() => root.unmount(), 1500);                    // after 1.5 s, unmount it (runs cleanup)
// Expected log: 1 → 2 → 3 → 2 (after 1 tick) → 5
```

## 💻 Code Example — Advanced

```jsx
// Production-style: error boundary, getDerivedStateFromProps, getSnapshotBeforeUpdate, PureComponent
import React from 'react';                       // React.Component, createRef, PureComponent
import { createRoot } from 'react-dom/client';   // React 18/19 root API

// ── 1. ERROR BOUNDARY (class-only feature — no hook equivalent yet) ──
class ErrorBoundary extends React.Component {
  state = { hasError: false };                   // class field: same as setting state in constructor

  static getDerivedStateFromError(error) {       // called during render when a child throws
    return { hasError: true };                   // return partial state → fallback UI is shown
  }

  componentDidCatch(error, info) {               // called after commit: side effects are allowed here
    // info.componentStack shows which component tree failed (good for logs)
    console.error('Logged to monitoring:', error.message); // send to Sentry-like service in real apps
  }

  render() {
    if (this.state.hasError) {                   // error happened in a child
      return <p>Something went wrong. Please retry.</p>; // fallback UI instead of white screen
    }
    return this.props.children;                  // normal path: render whatever was wrapped
  }
}

// ── 2. getDerivedStateFromProps: copy a prop into state BEFORE render ──
class Thermometer extends React.Component {
  state = { unit: 'C', lastSource: null };       // lastSource remembers the previous prop value

  static getDerivedStateFromProps(props, state) {// static: has NO access to "this"
    if (props.source !== state.lastSource) {     // only react when parent passed a NEW source
      return {                                   // return the state fields to update
        lastSource: props.source,
        unit: props.source === 'us' ? 'F' : 'C', // derive unit from the source
      };
    }
    return null;                                 // null = "no state change needed"
  }

  render() {
    return <p>Unit: {this.state.unit}</p>;      // uses the derived state
  }
}

// ── 3. getSnapshotBeforeUpdate: read DOM BEFORE it changes, use it AFTER ──
class ChatBox extends React.Component {
  listRef = React.createRef();                   // ref points to the real <ul> DOM node

  getSnapshotBeforeUpdate(prevProps) {           // runs right before DOM changes are applied
    if (this.props.messages.length > prevProps.messages.length) { // a new message arrived
      const el = this.listRef.current;           // real DOM node
      return el.scrollHeight - el.scrollTop;     // remember distance from the bottom
    }
    return null;                                 // no snapshot needed
  }

  componentDidUpdate(prevProps, prevState, snapshot) { // runs after DOM changed
    if (snapshot !== null) {                     // we captured a snapshot earlier
      const el = this.listRef.current;           // same DOM node, now with new messages
      el.scrollTop = el.scrollHeight - snapshot; // restore the same reading position
    }
  }

  render() {
    return (
      <ul ref={this.listRef}>                    {/* attach the ref to the real DOM node */}
        {this.props.messages.map((m, i) => <li key={i}>{m}</li>)}
      </ul>
    );
  }
}

// ── 4. PureComponent: shouldComponentUpdate with a shallow props check ──
class Price extends React.PureComponent {        // re-renders only if amount changed (shallow)
  render() {
    console.log('Price render', this.props.amount); // logs only when a real change happens
    return <b>₹{this.props.amount}</b>;          // rupee amount shown to user
  }
}

// ── Demo: all four pieces on the page ──
function Bomb() {
  throw new Error('payment service down');       // simulates a crash inside a child
}

const root = createRoot(document.getElementById('root'));
root.render(
  <>
    <Thermometer source="us" />                  {/* shows "Unit: F" */}
    <ErrorBoundary>                              {/* catches Bomb's crash */}
      <Bomb />
    </ErrorBoundary>
    <Price amount={99} />                        {/* logs "Price render 99" (React may retry the root once after the caught error, so it can print twice) */}
  </>
);
```

---

## 🟠 Real App Integration

Class lifecycle is still used for **error boundaries** in Next.js. The App Router's `error.jsx` covers route-level errors, but a custom boundary around a widget needs a class. Pair it with a Server Component page that passes the id down.

```jsx
// app/components/ErrorBoundary.jsx
'use client';                                        // lifecycle methods run only in the browser
import { Component } from 'react';                   // base class for class components

export default class ErrorBoundary extends Component {
  state = { hasError: false };                       // flag that switches to fallback UI
  static getDerivedStateFromError() {                // called when a child throws during render
    return { hasError: true };                       // show the fallback on the next render
  }
  componentDidCatch(error, info) {                   // after commit: safe place for logging
    fetch('/api/log', {                              // send the error to your logging endpoint
      method: 'POST',                                // POST the details
      body: JSON.stringify({ message: error.message, stack: info.componentStack }),
    });
  }
  render() {
    if (this.state.hasError) {                       // fallback UI
      return <p>Something went wrong. <button onClick={() => this.setState({ hasError: false })}>Retry</button></p>;
    }
    return this.props.children;                      // normal UI
  }
}

```

```jsx
// app/orders/[id]/page.jsx  (Server Component: no 'use client')
import ErrorBoundary from '@/app/components/ErrorBoundary'; // client boundary imported into a server page
import OrderTimer from './OrderTimer';                    // a Client Component (class with componentDidMount)

export default async function Page({ params }) {
  const { id } = await params;                       // Next.js 15+: params is a Promise
  return (
    <ErrorBoundary>                                    {/* catches crashes inside OrderTimer */}
      <OrderTimer orderId={id} />                      {/* id comes from the server-side route */}
    </ErrorBoundary>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Starting a timer in `componentDidMount` but never clearing it
✅ **Correct:** Store the id and clear it in `componentWillUnmount`

```jsx
// Wrong: timer keeps running after the component is gone
class Clock extends React.Component {
  componentDidMount() {
    setInterval(() => this.setState({ t: Date.now() }), 1000); // ❌ no id saved, no cleanup
  }
  render() { return <p>{this.state?.t}</p>; }
}

// Right: save the id and clear it on unmount
class Clock extends React.Component {
  componentDidMount() {
    this.id = setInterval(() => this.setState({ t: Date.now() }), 1000); // ✅ keep the id
  }
  componentWillUnmount() {
    clearInterval(this.id);                      // ✅ stop the timer when removed
  }
  render() { return <p>{this.state?.t}</p>; }
}
```

❌ **Mistake 2:** Calling `setState` inside `render()` (causes an infinite loop)
✅ **Correct:** Move the state change to `componentDidMount`, an event handler, or `componentDidUpdate` with a condition

```jsx
// Wrong: render → setState → render → setState ... forever
class Badge extends React.Component {
  render() {
    this.setState({ count: 1 });                 // ❌ triggers another render, endlessly
    return <span>{this.state.count}</span>;
  }
}

// Right: side effects belong in lifecycle methods, not in render
class Badge extends React.Component {
  state = { count: 0 };
  componentDidMount() {
    this.setState({ count: 1 });                 // ✅ runs once, after the first commit
  }
  render() { return <span>{this.state.count}</span>; }
}
```

---

## 🧠 Tricky Interview Question

```jsx
import React from 'react';
import { createRoot } from 'react-dom/client';

class Counter extends React.Component {
  state = { count: 0 };                          // starts at 0

  componentDidMount() {
    console.log('mount, count =', this.state.count);     // reads 0
    this.setState({ count: this.state.count + 1 });      // reads 0 → will set 1
    this.setState({ count: this.state.count + 1 });      // ALSO reads 0 → will set 1 (not 2!)
  }

  componentDidUpdate() {
    console.log('update, count =', this.state.count);    // runs after the batched re-render
  }

  render() {
    console.log('render, count =', this.state.count);
    return <p>{this.state.count}</p>;
  }
}

createRoot(document.getElementById('root')).render(<Counter />);
```
**Answer:** The output is, in order:
```
render, count = 0
mount, count = 0
render, count = 1
update, count = 1
```
Both `setState` calls are batched and both read `this.state.count` while it is still `0`, so the final value is `1`, not `2`. React does one re-render with the merged result. The fix is the functional form: `this.setState(prev => ({ count: prev.count + 1 }))`, which receives the latest state each time and gives `2`.

---

## ⚫ Interview Questions + Answers

Q1: What are the main lifecycle methods of a class component?
A1: Mounting: `constructor`, `static getDerivedStateFromProps`, `render`, `componentDidMount`. Updating: `static getDerivedStateFromProps`, `shouldComponentUpdate`, `render`, `getSnapshotBeforeUpdate`, `componentDidUpdate`. Unmounting: `componentWillUnmount`. Error handling: `static getDerivedStateFromError` and `componentDidCatch`.

Q2: Why must `render()` be pure?
A2: React may call `render()` several times (and in StrictMode it calls it twice in development) before it commits anything. If `render()` starts timers, makes network calls, or calls `setState`, those side effects can run more often than expected or cause infinite loops. Side effects belong in `componentDidMount` / `componentDidUpdate`.

Q3: What is the difference between `componentDidMount` and `componentDidUpdate`?
A3: `componentDidMount` runs once, after the first successful commit. `componentDidUpdate` runs after every re-render that is not the first one. To react only to a specific change, compare `prevProps` with `this.props` inside `componentDidUpdate`, otherwise you may create an update loop.

Q4: What does `getDerivedStateFromProps` do and why is it static?
A4: It returns a partial state object (or `null`) from props before every render, so state can be derived from props. It is static because React calls it without a component instance; it therefore cannot read `this`. Use it rarely, because most derived data is better computed during render.

Q5: Why is `getSnapshotBeforeUpdate` useful?
A5: It runs after render but before the DOM is changed, so it can read the current DOM (for example the scroll position). Its return value is passed to `componentDidUpdate` as the third argument, letting you restore the same scroll position after new content appears, as in a chat list.

---

## 🔷 When to Use + When Not to Use
✅ **Use class lifecycle when:**
- You maintain an older codebase that is already written with classes
- You need an **Error Boundary** (`getDerivedStateFromError` / `componentDidCatch`), which still requires a class
- You need `getSnapshotBeforeUpdate` for DOM measurements before an update

❌ **Avoid class lifecycle when:**
- You write new code: function components with hooks (`useEffect`) are the modern default
- Logic for one concern is split across three methods (mount, update, unmount) and is hard to follow
- You only need a simple value copied from props (compute it during render instead)

---

## 📊 Visual Diagram

```
                 MOUNTING                         UPDATING                       UNMOUNTING
  ┌────────────────────────────────┐   ┌──────────────────────────────┐   ┌──────────────────────┐
  │ constructor(props)             │   │ getDerivedStateFromProps     │   │                      │
  │ getDerivedStateFromProps       │   │ shouldComponentUpdate        │   │ componentWillUnmount │
  │ render()        ← pure JSX     │   │ render()                     │   │   (clear timers,     │
  │   ── DOM committed ──          │   │ getSnapshotBeforeUpdate      │   │    unsubscribe)      │
  │ componentDidMount()  ← effects │   │   ── DOM committed ──        │   │                      │
  └────────────────────────────────┘   │ componentDidUpdate(prev,…)   │   └──────────────────────┘
                                       └──────────────────────────────┘

  Error path:  child throws → getDerivedStateFromError (set fallback) → componentDidCatch (log)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Lifecycle | Ordered phases of a component's life | Component की life के चरण |
| Mount | First time the component is inserted in the DOM | पहली बार DOM में आना |
| Update | Re-render caused by new props or state | Props या state बदलने से दोबारा render |
| Unmount | Component removed from the DOM | DOM से हटाया जाना |
| Side effect | Work outside rendering (timer, fetch, subscription) | Render के बाहर का काम |
| Cleanup | Undoing side effects before removal | Hatane se pehle side effects बंद करना |
| Error boundary | Class that catches child render errors | Child की render error पकड़ने वाला class |
| Pure function | Same input gives same output, no side effects | एक ही input पर हमेशा एक ही output |

---

## ⚡ 3-Line Summary
**English:**
1. Class lifecycle methods run at fixed moments: mount, update and unmount.
2. Put timers, fetches and subscriptions in `componentDidMount`, and always clean them up in `componentWillUnmount`.
3. Keep `render()` pure, and use error boundaries (a class-only feature) to catch child crashes.

**Hindi:**
1. Class lifecycle methods तय समय पर चलते हैं: mount, update और unmount।
2. Timers, fetch और subscriptions `componentDidMount` में रखो, और `componentWillUnmount` में हमेशा बंद करो।
3. `render()` को pure रखो, और child crashes पकड़ने के लिए error boundary (सिर्फ class में) इस्तेमाल करो।

---

## ➡️ Next Topic
**59. Component Lifecycle (Functional)** — `useEffect`, cleanup और dependency array से वही lifecycle hooks में कैसे लिखा जाता है। Class lifecycle समझने के बाद यही सबसे ज़रूरी अगला कदम है।
