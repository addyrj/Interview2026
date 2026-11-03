# 13. Functional vs Class Components
# हिंदी में: Functional बनाम Class Components — Component लिखने के दो तरीके

---

## 🔵 Simple Definition (English)
A **functional component** is a plain JavaScript function that takes props and returns JSX, and uses Hooks for state and side effects. A **class component** is an ES6 class that extends `React.Component`, keeps state in `this.state` and uses lifecycle methods like `componentDidMount`. Both produce the same UI.

## 🔵 सरल परिभाषा (Hindi)
**Functional component** एक साधारण JavaScript function है जो props लेता है और JSX return करता है, और state व side effects के लिए Hooks इस्तेमाल करता है। **Class component** एक ES6 class है जो `React.Component` को extend करती है, state `this.state` में रखती है और `componentDidMount` जैसे lifecycle methods इस्तेमाल करती है। दोनों एक जैसा UI बनाते हैं।

---

## 🔴 Problem it Solves

Before React 16.8 (2019), only class components could hold state or run code on mount and unmount. That forced developers to write classes even for small stateful widgets. Classes brought problems: the `this` keyword, binding event handlers in the constructor, related logic split across `componentDidMount`, `componentDidUpdate` and `componentWillUnmount`, and hard reuse of stateful logic (needing HOCs and render props). Hooks gave functions the same powers, so functional components can do everything classes did, with less code.

```jsx
// PROBLEM (class): logic for one feature is split across 3 methods, and `this` must be bound
class Timer extends React.Component {
  componentDidMount()   { this.id = setInterval(this.tick, 1000); }  // start
  componentDidUpdate()  { /* sometimes must restart the timer here */ }
  componentWillUnmount(){ clearInterval(this.id); }                  // stop
}

// SOLUTION (function + hook): start and stop live together in one effect
function TimerFixed() {
  useEffect(() => {
    const id = setInterval(tick, 1000);   // start
    return () => clearInterval(id);       // stop (cleanup right beside start)
  }, []);
}
```

## 🔴 यह क्यों बना? (Hindi)
React 16.8 (2019) से पहले सिर्फ class components में state रखी जा सकती थी या mount/unmount पर code चलाया जा सकता था। इसलिए छोटे stateful widgets के लिए भी class लिखनी पड़ती थी। Classes की दिक्कतें थीं: `this` keyword, constructor में event handlers को bind करना, एक ही काम का logic `componentDidMount`, `componentDidUpdate` और `componentWillUnmount` में बँट जाना, और stateful logic को दोबारा इस्तेमाल करना मुश्किल (HOC और render props चाहिए थे)। Hooks ने functions को वही ताकत दी, इसलिए functional components वह सब कर सकते हैं जो classes करती थीं, कम code में।

---

## 🟢 How it Works — Step by Step

```
FUNCTIONAL                                   CLASS
Step 1 → React calls the function            Step 1 → React creates an instance: new Counter(props)
Step 2 → Hooks read state for this render    Step 2 → constructor sets this.state
Step 3 → Function returns JSX                Step 3 → render() returns JSX
Step 4 → React commits to DOM                Step 4 → React commits to DOM
Step 5 → useEffect runs after paint          Step 5 → componentDidMount runs
Step 6 → State change: function runs AGAIN   Step 6 → setState: render() runs again,
         with new values (new closure)                same instance, reads this.state
Step 7 → Effect cleanup, then new effect     Step 7 → componentDidUpdate / componentWillUnmount

KEY DIFFERENCE: a function re-runs from the top each render and captures that render's values.
A class keeps one instance, and render() reads the *latest* this.props / this.state.
```

## 🟢 कैसे काम करता है? (Hindi)

```
FUNCTIONAL                                   CLASS
Step 1 → React function को call करता है      Step 1 → React instance बनाता है: new Counter(props)
Step 2 → Hooks इस render की state पढ़ते हैं    Step 2 → constructor में this.state set होती है
Step 3 → Function JSX return करता है          Step 3 → render() JSX return करता है
Step 4 → React DOM में commit करता है         Step 4 → React DOM में commit करता है
Step 5 → paint के बाद useEffect चलता है       Step 5 → componentDidMount चलता है
Step 6 → State बदली: function फिर से चलता है,  Step 6 → setState: उसी instance का render() फिर चलता है,
         नई values (नया closure) के साथ                this.state पढ़ता है
Step 7 → पहले cleanup, फिर नया effect          Step 7 → componentDidUpdate / componentWillUnmount

मुख्य फर्क: function हर render पर ऊपर से दोबारा चलता है और उसी render की values पकड़ता है।
Class में एक ही instance रहता है, और render() हमेशा *नई* this.props / this.state पढ़ता है।
```

---

## 🟡 Real World Example
**Zomato "Add to cart" counter:** Older Zomato-style code (2017) had a `CartButton` class with `this.state = { qty: 0 }`, two handlers bound in the constructor, and a `componentDidMount` that loaded the saved quantity. The same widget today is a 12-line function with `useState` and `useEffect`. Many large companies still run both styles side by side: old screens remain classes, and new screens are functions. Error boundaries are the one thing that still needs a class.

## 🟡 Real Example Hindi mein
**Zomato "Add to cart" counter:** 2017 के Zomato जैसे पुराने code में `CartButton` class थी जिसमें `this.state = { qty: 0 }`, constructor में bind किए दो handlers, और saved quantity load करने वाला `componentDidMount` था। वही widget आज `useState` और `useEffect` वाला 12 line का function है। कई बड़ी कंपनियों में आज भी दोनों style साथ चलते हैं: पुरानी screens classes हैं, नई screens functions। Error boundary अकेली चीज़ है जिसके लिए अब भी class चाहिए।

---

## 💻 Code Example — Basic

```jsx
// The SAME counter written twice: class first, function second
import { Component, useState } from 'react';       // Component for class, useState for function

// ---------- Class version ----------
class CounterClass extends Component {              // must extend Component
  constructor(props) {                              // runs once when the instance is created
    super(props);                                   // required before using `this`
    this.state = { count: 0 };                      // state is ONE object
    this.increment = this.increment.bind(this);     // bind, or `this` is undefined in the handler
  }

  increment() {                                     // event handler method
    this.setState((prev) => ({ count: prev.count + 1 })); // setState MERGES into state
  }

  render() {                                        // the only required method
    return (
      <button onClick={this.increment}>             {/* handler passed without calling it */}
        Class count: {this.state.count}             {/* read state through this.state */}
      </button>
    );
  }
}

// ---------- Function version ----------
function CounterFunction() {                        // just a function, no this, no bind
  const [count, setCount] = useState(0);            // state is ONE value (create more with more useState)
  return (
    <button onClick={() => setCount((c) => c + 1)}> {/* updater form, safe for batching */}
      Function count: {count}                       {/* read state as a normal variable */}
    </button>
  );
}

export default function App() {                     // show both side by side
  return (
    <>
      <CounterClass />                              {/* works exactly like the function version */}
      <CounterFunction />
    </>
  );
}
```

## 💻 Code Example — Advanced

```jsx
// Real world: a live order-status widget with fetch, polling and cleanup, written both ways
import { Component, useState, useEffect } from 'react';

// ---------- Class version: logic split across lifecycle methods ----------
class OrderStatusClass extends Component {
  state = { status: 'loading', error: null };          // class field syntax (no constructor needed)
  timer = null;                                        // instance variable for the interval id

  fetchStatus = async () => {                          // arrow property: `this` is auto-bound
    try {
      const res = await fetch(`/api/orders/${this.props.orderId}`); // read latest prop through this.props
      if (!res.ok) throw new Error('HTTP ' + res.status);           // fetch ignores HTTP errors
      const data = await res.json();                   // parse JSON
      this.setState({ status: data.status, error: null }); // merge into state
    } catch (e) {
      this.setState({ error: e.message });             // show an error
    }
  };

  componentDidMount() {                                // mount: first fetch + start polling
    this.fetchStatus();
    this.timer = setInterval(this.fetchStatus, 10000); // poll every 10 seconds
  }

  componentDidUpdate(prevProps) {                      // props changed? refetch manually
    if (prevProps.orderId !== this.props.orderId) this.fetchStatus();
  }

  componentWillUnmount() {                             // cleanup lives in a DIFFERENT method
    clearInterval(this.timer);
  }

  render() {
    const { status, error } = this.state;              // destructure state
    if (error) return <p role="alert">Error: {error}</p>;
    return <p>Order {this.props.orderId}: {status}</p>;
  }
}

// ---------- Function version: the same logic in ONE effect ----------
function OrderStatus({ orderId }) {
  const [status, setStatus] = useState('loading');     // separate state values
  const [error, setError] = useState(null);

  useEffect(() => {                                    // re-runs automatically when orderId changes
    let cancelled = false;                             // ignore results after unmount / id change

    async function fetchStatus() {
      try {
        const res = await fetch(`/api/orders/${orderId}`);
        if (!res.ok) throw new Error('HTTP ' + res.status);
        const data = await res.json();
        if (!cancelled) { setStatus(data.status); setError(null); } // guard against stale updates
      } catch (e) {
        if (!cancelled) setError(e.message);
      }
    }

    fetchStatus();                                     // first fetch
    const timer = setInterval(fetchStatus, 10000);     // polling
    return () => {                                     // cleanup beside the setup
      cancelled = true;
      clearInterval(timer);
    };
  }, [orderId]);                                       // dependency replaces componentDidUpdate

  if (error) return <p role="alert">Error: {error}</p>;
  return <p>Order {orderId}: {status}</p>;
}

export { OrderStatusClass, OrderStatus };
```

---

## 🟠 Real App Integration

In the Next.js App Router, components are **Server Components by default**, and Server Components must be functions (they can be `async`). Class components cannot be Server Components and need `'use client'`. Hooks and classes both work only in Client Components. An Error Boundary class is the standard reason to still write a class, though the `react-error-boundary` package wraps it for you.

```jsx
// app/components/ErrorBoundary.jsx — still a class, because no Hook can catch render errors
'use client';                                          // required: classes need the client

import { Component } from 'react';

export default class ErrorBoundary extends Component {
  state = { hasError: false };                         // track whether a child crashed

  static getDerivedStateFromError() {                  // called when a child throws while rendering
    return { hasError: true };                         // switch to fallback UI
  }

  componentDidCatch(error, info) {                     // log to your monitoring tool
    console.error('Caught:', error, info.componentStack);
  }

  render() {
    if (this.state.hasError) return this.props.fallback; // show the fallback prop
    return this.props.children;                        // otherwise render normally
  }
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Forgetting to bind `this` (or calling the handler) in a class
✅ **Correct:** Use an arrow-function class property, or bind in the constructor

```jsx
// Wrong: `this` is undefined when React calls the handler
class A extends React.Component {
  state = { n: 0 };
  inc() { this.setState({ n: this.state.n + 1 }); }          // ❌ normal method, loses `this`
  render() { return <button onClick={this.inc}>+</button>; } // TypeError on click
}

// Right: arrow property keeps `this`
class B extends React.Component {
  state = { n: 0 };
  inc = () => this.setState((p) => ({ n: p.n + 1 }));        // ✅ bound automatically
  render() { return <button onClick={this.inc}>+</button>; }
}
```

❌ **Mistake 2:** Treating `setState` like Hooks (class `setState` merges, `useState` replaces)
✅ **Correct:** With `useState` on an object, spread the old values yourself

```jsx
// Wrong: user.name is lost, because the setter REPLACES the object
const [user, setUser] = useState({ name: 'Asha', city: 'Pune' });
setUser({ city: 'Delhi' });                                  // ❌ state is now { city: 'Delhi' }

// Right: copy the rest of the object
setUser((prev) => ({ ...prev, city: 'Delhi' }));             // ✅ name stays
```

❌ **Mistake 3:** Mutating `this.state` directly
✅ **Correct:** Always call `setState`

```jsx
// Wrong: no re-render happens
this.state.count = 5;                                        // ❌

// Right
this.setState({ count: 5 });                                 // ✅ schedules a re-render
```

---

## 🧠 Tricky Interview Question

```jsx
import { Component, useState } from 'react';

// Class version
class ClassAlert extends Component {
  render() {
    const show = () => setTimeout(() => alert('Class: ' + this.props.user), 3000);
    return <button onClick={show}>Class alert</button>;
  }
}

// Function version
function FunctionAlert({ user }) {
  const show = () => setTimeout(() => alert('Function: ' + user), 3000);
  return <button onClick={show}>Function alert</button>;
}

export default function App() {
  const [user, setUser] = useState('Asha');
  return (
    <>
      <select value={user} onChange={(e) => setUser(e.target.value)}>
        <option>Asha</option><option>Ravi</option>
      </select>
      <ClassAlert user={user} />
      <FunctionAlert user={user} />
    </>
  );
}
```
Question: Click both buttons with "Asha" selected, then switch to "Ravi" within 3 seconds. What do the alerts say?

**Answer:** The function button shows **"Function: Asha"** and the class button shows **"Class: Ravi"**. A function component captures the props of the render in which the handler was created (closure), so it remembers the value at click time. A class reads `this.props` when the timeout fires, and `this` is mutable, so it sees the latest props. This is the famous "functional components capture the values" difference. If a function needs the latest value instead, store it in a `useRef`.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between functional and class components?
A1: A functional component is a function using Hooks (`useState`, `useEffect`) and has no `this`. A class component extends `React.Component`, uses `this.state`, `this.setState` and lifecycle methods. Functions are shorter, easier to test and compose, and are the modern standard. Classes still work and are not deprecated.

Q2: Can functional components have state and lifecycle behavior?
A2: Yes, since React 16.8. `useState` gives state, and `useEffect` covers mount, update and unmount (`componentDidMount`, `componentDidUpdate`, `componentWillUnmount`) depending on the dependency array and cleanup.

Q3: Which things still require a class component?
A3: Error boundaries (`getDerivedStateFromError` and `componentDidCatch`) have no Hook equivalent as of React 18/19. Everything else can be a function. Class components are also allowed only in Client Components in Next.js.

Q4: Are classes removed from React?
A4: No. React says it has no plans to remove classes, and old code keeps working. The documentation just recommends writing new components as functions.

Q5: Why do Hooks make logic reuse easier than classes?
A5: Custom Hooks extract stateful logic into plain functions (`useOnlineStatus`) that any component can call, without wrapper components. In classes you needed HOCs or render props, which add nesting ("wrapper hell") and make data flow harder to follow.

---

## 🔷 When to Use + When Not to Use
✅ **Use functional components when:**
- Writing any new component (this is the default today)
- You want custom Hooks, Server Components, and the latest React features
- You want shorter code with related logic kept together

❌ **Use a class component only when:**
- You need an error boundary (or use the `react-error-boundary` library)
- You maintain a legacy codebase and a rewrite is not worth the risk
- Avoid mixing styles in the same new feature without a reason

---

## 📊 Visual Diagram

```
 CLASS COMPONENT                          FUNCTIONAL COMPONENT
 ┌──────────────────────────┐             ┌──────────────────────────┐
 │ class Cart extends       │             │ function Cart(props) {   │
 │   Component {            │             │                          │
 │  constructor → this.state│             │  const [qty,setQty] =    │
 │  componentDidMount()     │             │         useState(0)      │
 │  componentDidUpdate()    │             │                          │
 │  componentWillUnmount()  │             │  useEffect(() => {       │
 │  render() → JSX          │             │     setup;               │
 │ }                        │             │     return cleanup;      │
 └──────────────────────────┘             │  }, [deps]);             │
   one instance lives on;                 │  return JSX;             │
   reads latest this.props                │ }                        │
                                          └──────────────────────────┘
                                            re-runs each render;
                                            captures that render's values

 Lifecycle mapping:
 componentDidMount        ≈ useEffect(fn, [])
 componentDidUpdate       ≈ useEffect(fn, [dep])
 componentWillUnmount     ≈ cleanup function returned from useEffect
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Functional component | Function returning JSX | JSX return करने वाला function |
| Class component | ES6 class extending `React.Component` | `React.Component` को extend करने वाली class |
| `this` | The class instance | Class का instance |
| `setState` | Class method that merges new state | नई state को merge करने वाला class method |
| Lifecycle method | Class method run at mount/update/unmount | Mount/update/unmount पर चलने वाला method |
| Hook | Function that adds React features to functions | Functions को React features देने वाला function |
| Error boundary | Component that catches child render errors | Child की render errors पकड़ने वाला component |
| Closure | Function remembering values from its creation | बनने के समय की values याद रखने वाला function |

---

## ⚡ 3-Line Summary
**English:**
1. Functional components are functions with Hooks; class components extend `React.Component` with `this` and lifecycle methods.
2. Both work, but functions are shorter, reuse logic through custom Hooks, and are the standard for new code.
3. Functions capture the render's values, classes read the latest `this.props`; only error boundaries still need a class.

**Hindi:**
1. Functional components Hooks वाले functions हैं; class components `this` और lifecycle methods के साथ `React.Component` को extend करते हैं।
2. दोनों चलते हैं, लेकिन functions छोटे हैं, custom Hooks से logic reuse होता है, और नए code के लिए यही standard है।
3. Functions उस render की values पकड़ते हैं, classes नई `this.props` पढ़ती हैं; सिर्फ error boundaries के लिए अब भी class चाहिए।

---

## ➡️ Next Topic
**14. Why Functional Components Won** — इस फर्क के बाद देखो कि React community ने classes को छोड़कर functions क्यों चुना: Hooks, bundle size, Compiler और Server Components की वजहें।
