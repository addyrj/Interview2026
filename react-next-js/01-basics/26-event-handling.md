# 26. Event Handling in React
# हिंदी में: React में Event Handling — User Actions को Handle करना

---

## 🔵 Simple Definition (English)
React handles events using **camelCase event props** (`onClick`, `onChange`, `onSubmit`) that accept **function references**. React uses **Synthetic Events** — wrapper objects around native browser events that provide a consistent API across all browsers.

## 🔵 सरल परिभाषा (Hindi)
React events को **camelCase event props** (`onClick`, `onChange`, `onSubmit`) से handle करता है जो **function references** accept करते हैं। React **Synthetic Events** use करता है — native browser events के wrapper objects जो सभी browsers में consistent API provide करते हैं।

---

## 🔴 Problem it Solves
```jsx
// Vanilla JS: manually add/remove event listeners, inconsistent cross-browser
document.getElementById('btn').addEventListener('click', handler);
// Must remember to removeEventListener on cleanup!

// React: declarative event handling — no manual DOM, auto cleanup
<button onClick={handler}>Click Me</button>
// React attaches/detaches automatically, consistent across browsers
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → Add event prop to JSX element:
         <button onClick={handleClick}>Click</button>
         Note: onClick, not onclick (camelCase!)

Step 2 → React attaches a single listener at the root (event delegation)
         (NOT on each element — one listener for all!)

Step 3 → User clicks → native event bubbles to root
         React creates SyntheticEvent wrapping native event

Step 4 → React finds which component's handler matches
         Calls handleClick(syntheticEvent)

Step 5 → SyntheticEvent has: .target, .currentTarget,
         .preventDefault(), .stopPropagation(), .nativeEvent
```

---

## 🟡 Real World Example
**Zomato Add to Cart:** Clicking "Add" button, pressing Enter on quantity input, changing filter dropdown — all use React event handlers. The synthetic event system ensures the same `onClick`, `onChange`, `onKeyDown` work identically on Chrome, Firefox, Safari.

---

## 💻 Code Example — Basic

```jsx
import { useState } from 'react';

function EventExamples() {
  const [count, setCount] = useState(0);
  const [text, setText] = useState('');
  const [position, setPosition] = useState({ x: 0, y: 0 });

  // 1. CLICK EVENT
  const handleClick = (event) => {
    console.log('Button clicked!');
    console.log('event.type:', event.type);           // 'click'
    console.log('event.target:', event.target);       // the button DOM node
    console.log('event.currentTarget:', event.currentTarget); // same as target here
    setCount(c => c + 1);
  };

  // 2. CHANGE EVENT (input)
  const handleChange = (event) => {
    setText(event.target.value); // read value from event.target
  };

  // 3. FORM SUBMIT
  const handleSubmit = (event) => {
    event.preventDefault(); // MUST do this! Prevents page reload
    console.log('Submitted:', text);
  };

  // 4. MOUSE EVENTS
  const handleMouseMove = (event) => {
    setPosition({ x: event.clientX, y: event.clientY });
  };

  // 5. KEYBOARD EVENTS
  const handleKeyDown = (event) => {
    if (event.key === 'Enter') console.log('Enter pressed!');
    if (event.key === 'Escape') console.log('Escape pressed!');
    if (event.ctrlKey && event.key === 's') {
      event.preventDefault(); // prevent browser save
      console.log('Ctrl+S!');
    }
  };

  return (
    <div onMouseMove={handleMouseMove}>
      {/* onClick: pass function REFERENCE, not call! */}
      <button onClick={handleClick}>         {/* ✅ reference */}
        Clicked: {count}
      </button>

      {/* WRONG: onClick={handleClick()} would call it during render! */}

      {/* Pass data via arrow function */}
      <button onClick={() => handleClick()}>  {/* also ✅ */}
        Also click
      </button>

      <form onSubmit={handleSubmit}>
        <input
          value={text}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          placeholder="Type something..."
        />
        <button type="submit">Submit</button>
      </form>

      <p>Mouse: {position.x}, {position.y}</p>
    </div>
  );
}
```

## 💻 Code Example — Advanced

```jsx
import { useState, useCallback } from 'react';

// ── PASSING ARGUMENTS TO EVENT HANDLERS ──
function ProductList({ products }) {
  const [cart, setCart] = useState([]);

  // Pattern 1: Arrow function wrapper (simple, but new fn each render)
  return products.map(product => (
    <button
      key={product.id}
      onClick={() => setCart(prev => [...prev, product])}  // passes product
    >
      Add {product.name}
    </button>
  ));
}

// Pattern 2: useCallback (memo-friendly)
function ProductListOptimized({ products }) {
  const [cart, setCart] = useState([]);

  const handleAddToCart = useCallback((product) => {
    setCart(prev => [...prev, product]);
  }, []); // stable reference

  return products.map(product => (
    <ProductCard
      key={product.id}
      product={product}
      onAdd={handleAddToCart}   // stable function ✅
    />
  ));
}

// ── EVENT DELEGATION MANUALLY ─────────────
// Handle click on parent, check event.target.dataset
function QuickActions({ productId }) {
  const handleAction = (e) => {
    const action = e.target.dataset.action; // custom data attribute
    if (!action) return;

    switch (action) {
      case 'add':    handleAddToCart(productId); break;
      case 'wish':   handleWishlist(productId);  break;
      case 'share':  handleShare(productId);     break;
    }
  };

  return (
    <div onClick={handleAction}>    {/* ONE handler for all buttons */}
      <button data-action="add">Add to Cart</button>
      <button data-action="wish">Wishlist</button>
      <button data-action="share">Share</button>
    </div>
  );
}

// ── STOPPING PROPAGATION ─────────────────
function Card({ onClick }) {
  return (
    <div onClick={onClick} className="card">
      <h3>Product Name</h3>
      {/* Delete button inside card — clicking it shouldn't trigger card click */}
      <button
        onClick={(e) => {
          e.stopPropagation();  // stops event bubbling up to div
          handleDelete();
        }}
      >
        Delete
      </button>
    </div>
  );
}
```

---

## 🟠 Next.js Connection

```jsx
// Events work only in Client Components!
// Server Components can't have event handlers

'use client';
// next.js forms: Server Actions let you handle forms server-side
import { useTransition } from 'react';

function ContactForm() {
  const [isPending, startTransition] = useTransition();

  // Server Action (runs on server when form submitted)
  async function submitForm(formData) {
    'use server';  // marks this as server action
    const email = formData.get('email');
    await saveToDatabase({ email });
  }

  return (
    // action={submitForm}: Next.js handles submission server-side
    // No event.preventDefault() needed — no JS required!
    <form action={submitForm}>
      <input name="email" type="email" required />
      <button type="submit" disabled={isPending}>
        {isPending ? 'Sending...' : 'Submit'}
      </button>
    </form>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Calling the function instead of passing reference
```jsx
// WRONG: handleClick() runs DURING render, not on click!
<button onClick={handleClick()}>Click</button>  // ❌

// CORRECT: pass the function reference
<button onClick={handleClick}>Click</button>    // ✅

// For arguments: wrap in arrow function
<button onClick={() => handleClick(product.id)}>Click</button> // ✅
```

❌ **Mistake 2:** Forgetting preventDefault on form submit
```jsx
// WRONG: page reloads on submit!
function Form() {
  const handleSubmit = (e) => {  // ❌ missing preventDefault
    fetch('/api/submit', { ... });
  };
  return <form onSubmit={handleSubmit}>...</form>;
}

// CORRECT:
const handleSubmit = (e) => {
  e.preventDefault();  // ✅ stops page reload
  fetch('/api/submit', { ... });
};
```

---

## 🧠 Tricky Interview Question

```jsx
function App() {
  const [count, setCount] = useState(0);

  return (
    <div onClick={() => setCount(c => c + 1)}>
      <button onClick={(e) => {
        e.stopPropagation();
        setCount(c => c + 10);
      }}>
        +10
      </button>
    </div>
  );
}
// Click the button. What is the count after click?
```
**Answer:** `10`. The button's `onClick` runs: `e.stopPropagation()` stops the event from bubbling up to the `div`, so the div's `onClick` does NOT run. Only `setCount(c => c + 10)` executes. Without `stopPropagation`, count would be `11` (div gets +1, button gets +10).

---

## ⚫ Interview Questions + Answers

**Q1: What is a Synthetic Event in React?**
A1: A Synthetic Event is React's wrapper around the native browser event. It provides a consistent API (`event.target`, `event.preventDefault()`, `event.stopPropagation()`) that works identically across all browsers, normalizing browser differences. Access the underlying native event via `event.nativeEvent`. In React 17+, synthetic events are no longer pooled — you can access them asynchronously.

**Q2: What is event delegation in React?**
A2: React uses a single event listener at the root element (document or React root) rather than attaching listeners to each DOM node. When an event fires, it bubbles to the root, and React determines which component's handler to call. This is more performant (one listener vs potentially thousands) and automatically handles dynamically added/removed elements.

**Q3: How do you pass arguments to event handlers?**
A3: Use an arrow function wrapper: `onClick={() => handleClick(id)}`. This creates a new function on each render (performance cost) but is fine for most cases. For `React.memo`'d children, use `useCallback` to create stable references. You can also use data attributes: `data-id={id}` + read `e.target.dataset.id` in one shared handler (event delegation pattern).

**Q4: What is the difference between onClick and onclick?**
A4: In React JSX, use `onClick` (camelCase) — it's a React prop. `onclick` (lowercase) is the HTML attribute — setting it would be treated as a custom attribute string, not an event handler. React's camelCase convention applies to all events: `onChange`, `onSubmit`, `onMouseEnter`, `onKeyDown`, etc.

**Q5: What is event bubbling and how do you stop it?**
A5: Event bubbling = when an event fires on an element, it propagates ("bubbles") up through all parent elements. A click on a `<button>` inside a `<div>` triggers both the button's and div's click handlers. Stop it with `event.stopPropagation()`. Use `event.preventDefault()` to stop the default browser action (form submit reloading the page, link navigation) without stopping propagation.

---

## 🔷 When to Use + When Not to Use
✅ **Use React event handlers when:**
- User interactions (click, change, submit, keypress)
- Form handling (controlled inputs)
- Mouse/touch events for UI interaction

❌ **Avoid direct DOM addEventListener when:**
- You're in a React component — use JSX event props instead
- Exception: `window`, `document`, or third-party elements — use `useEffect` for these with cleanup

---

## 📊 Visual Diagram

```
EVENT FLOW IN REACT:
──────────────────────────────────────────────
  User clicks button
         │
         ▼
  Native click event fires on <button> DOM node
         │
         ▼
  Event BUBBLES up: button → div → body → document/root
         │
         ▼
  React's root listener catches it
         │
         ▼
  React creates SyntheticEvent wrapper
         │
         ▼
  React calls matching onClick handler(s) in component tree

BUBBLING (parent handler also fires):
──────────────────────────────────────────────
  <div onClick={divHandler}>           ← fires 2nd (bubble)
    <button onClick={btnHandler}>      ← fires 1st
      Click Me
    </button>
  </div>

  e.stopPropagation() in btnHandler → divHandler NOT called

COMMON EVENT NAMES:
──────────────────────────────────────────────
  Mouse:    onClick onDoubleClick onMouseEnter onMouseLeave onMouseMove
  Keyboard: onKeyDown onKeyUp onKeyPress
  Form:     onChange onSubmit onFocus onBlur
  Touch:    onTouchStart onTouchEnd onTouchMove
  Drag:     onDragStart onDrop onDragOver
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Synthetic Event | React's cross-browser event wrapper | React का cross-browser event wrapper |
| Event delegation | One listener at root for all events | Root पर एक listener सभी events के लिए |
| Bubbling | Event propagates up the DOM tree | Event DOM tree में ऊपर जाना |
| preventDefault | Stop default browser behavior | Default browser behavior रोकना |
| stopPropagation | Stop event from bubbling | Event को bubble से रोकना |
| camelCase | onClick not onclick | onClick नहीं onclick |

---

## ⚡ 3-Line Summary
**English:**
1. React events use camelCase props (`onClick`, `onChange`) and accept function references — never call the function: `onClick={fn}` not `onClick={fn()}`.
2. Synthetic Events provide consistent cross-browser API — use `e.preventDefault()` for forms, `e.stopPropagation()` to stop bubbling.
3. Pass arguments via arrow function wrapper: `onClick={() => handleClick(id)}` — or `useCallback` for `memo`'d children.

**Hindi:**
1. React events camelCase props use करते हैं (`onClick`, `onChange`) और function references accept करते हैं — function call मत करो: `onClick={fn}` नहीं `onClick={fn()}`।
2. Synthetic Events consistent cross-browser API provide करते हैं — forms के लिए `e.preventDefault()`, bubbling रोकने के लिए `e.stopPropagation()`।
3. Arguments pass करने के लिए arrow function wrapper: `onClick={() => handleClick(id)}` — या `memo`'d children के लिए `useCallback`।

---

## ➡️ Next Topic
**27. Synthetic Events** — Synthetic Events की deep dive — event pooling, nativeEvent, और cross-browser normalization।
