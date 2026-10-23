# 20. useState Hook — Complete Guide
# हिंदी में: useState — React की सबसे ज़रूरी Hook, पूरी Guide

---

## 🔵 Simple Definition (English)
`useState` is a React Hook that lets you add **state** (data that changes over time) to functional components. When state updates, React automatically re-renders the component with the new value. It returns `[currentValue, setterFunction]`.

## 🔵 सरल परिभाषा (Hindi)
`useState` React Hook है जो functional components में **state** (समय के साथ बदलने वाला data) add करने देती है। State update होने पर React automatically component को नई value के साथ re-render करता है। यह `[currentValue, setterFunction]` return करती है।

---

## 🔴 Problem it Solves
Before hooks, only class components had state. Functional components were "dumb" — no memory between renders. `useState` gave functional components the ability to remember values across renders without writing a class.

## 🔴 यह क्यों बना? (Hindi)
Hooks से पहले सिर्फ class components में state थी। Functional components "dumb" थे — renders के बीच कोई memory नहीं। `useState` ने functional components को class लिखे बिना renders के बीच values याद रखने की capability दी।

---

## 🟢 How it Works — Step by Step

```
Step 1 → useState(initialValue) called on first render
         React stores 'initialValue' in memory slot

Step 2 → Returns [currentValue, setState]
         currentValue = current stored value

Step 3 → User action triggers setState(newValue)

Step 4 → React schedules a re-render

Step 5 → Component re-runs from top
         useState returns [newValue, setState]
         (initial value IGNORED after first render)

Step 6 → React diffs → updates only changed DOM nodes
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → पहले render पर useState(initialValue) call होता है
         React 'initialValue' को memory slot में store करता है

Step 2 → [currentValue, setState] return करता है

Step 3 → User action → setState(newValue) trigger

Step 4 → React re-render schedule करता है

Step 5 → Component top से re-run होता है
         useState [newValue, setState] return करता है
         (initial value second render से ignore होता है)

Step 6 → React diff → सिर्फ changed DOM nodes update
```

---

## 🟡 Real World Example
**Amazon Cart:** When you click "Add to Cart" — cart count increases from 0 to 1. `const [cartCount, setCartCount] = useState(0)`. Clicking add: `setCartCount(c => c + 1)`. The cart icon in header auto-updates because it reads the same state.

## 🟡 Real Example Hindi mein
**Amazon Cart:** "Add to Cart" click करने पर cart count 0 से 1 होता है। `const [cartCount, setCartCount] = useState(0)`. Add click: `setCartCount(c => c + 1)`. Header में cart icon auto-update होता है क्योंकि वह same state पढ़ता है।

---

## 💻 Code Example — Basic

```jsx
import { useState } from 'react';

// ── BASIC STATE TYPES ─────────────────────
function StateExamples() {
  // Number state
  const [count, setCount] = useState(0);

  // String state
  const [name, setName] = useState('');

  // Boolean state (toggle)
  const [isOpen, setIsOpen] = useState(false);

  // Array state
  const [items, setItems] = useState([]);

  // Object state
  const [user, setUser] = useState({ name: '', email: '' });

  // Null state (loading pattern)
  const [data, setData] = useState(null);

  return (
    <div>
      {/* Number: increment / decrement */}
      <button onClick={() => setCount(c => c - 1)}>-</button>
      <span>{count}</span>
      <button onClick={() => setCount(c => c + 1)}>+</button>

      {/* String: controlled input */}
      <input value={name} onChange={e => setName(e.target.value)} />
      <p>Hello, {name || 'stranger'}!</p>

      {/* Boolean: toggle */}
      <button onClick={() => setIsOpen(prev => !prev)}>
        {isOpen ? 'Close' : 'Open'}
      </button>
      {isOpen && <div>Modal Content</div>}

      {/* Array: add item */}
      <button onClick={() => setItems(prev => [...prev, `Item ${prev.length + 1}`])}>
        Add Item
      </button>
      {items.map((item, i) => <li key={i}>{item}</li>)}

      {/* Object: update one field */}
      <input
        value={user.name}
        onChange={e => setUser(prev => ({ ...prev, name: e.target.value }))}
        placeholder="Your name"
      />
    </div>
  );
}

// ── LAZY INITIAL STATE ────────────────────
// If initial state is expensive to compute, use function:
function ExpensiveInit() {
  // WRONG: runs on every render (even though only used once)
  // const [data, setData] = useState(expensiveComputation());

  // CORRECT: function only runs on first render!
  const [data, setData] = useState(() => {
    const saved = localStorage.getItem('savedData');
    return saved ? JSON.parse(saved) : [];  // only runs once
  });

  return <div>{data.length} items</div>;
}
```

## 💻 Code Example — Advanced

```jsx
import { useState, useCallback } from 'react';

// ── COMPLETE FORM WITH useState ───────────
function CheckoutForm() {
  // Grouped state — all form fields in one object
  const [form, setForm] = useState({
    name: '',
    email: '',
    phone: '',
    address: '',
    city: '',
    pincode: '',
  });

  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  // Generic handler — updates any field
  const handleChange = (field) => (e) => {
    setForm(prev => ({ ...prev, [field]: e.target.value }));
    // Clear error when user types
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const validate = () => {
    const newErrors = {};
    if (!form.name.trim()) newErrors.name = 'Name is required';
    if (!form.email.includes('@')) newErrors.email = 'Invalid email';
    if (form.phone.length !== 10) newErrors.phone = 'Phone must be 10 digits';
    if (!form.pincode.match(/^\d{6}$/)) newErrors.pincode = 'Invalid pincode';
    return newErrors;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const validationErrors = validate();

    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }

    setIsSubmitting(true);
    try {
      await fetch('/api/checkout', {
        method: 'POST',
        body: JSON.stringify(form),
        headers: { 'Content-Type': 'application/json' },
      });
      setSubmitSuccess(true);
      setForm({ name: '', email: '', phone: '', address: '', city: '', pincode: '' });
    } catch (err) {
      setErrors({ submit: 'Failed to place order. Try again.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  if (submitSuccess) {
    return <div className="success">Order placed! ✅</div>;
  }

  return (
    <form onSubmit={handleSubmit}>
      {['name', 'email', 'phone', 'pincode'].map(field => (
        <div key={field}>
          <input
            value={form[field]}
            onChange={handleChange(field)}
            placeholder={field.charAt(0).toUpperCase() + field.slice(1)}
            className={errors[field] ? 'input-error' : ''}
          />
          {errors[field] && <span className="error">{errors[field]}</span>}
        </div>
      ))}

      {errors.submit && <p className="error">{errors.submit}</p>}

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Placing Order...' : 'Place Order'}
      </button>
    </form>
  );
}

// ── FUNCTIONAL UPDATE vs DIRECT UPDATE ────
function UpdatePatterns() {
  const [count, setCount] = useState(0);

  // WRONG: stale closure — may read old count
  const directUpdate = () => {
    setCount(count + 1);  // ❌ if called multiple times, uses old count
    setCount(count + 1);  // both use same count! result: count + 1, not +2
  };

  // CORRECT: functional update — always gets latest value
  const functionalUpdate = () => {
    setCount(c => c + 1);  // ✅ gets CURRENT count at call time
    setCount(c => c + 1);  // adds 1 to the result of prev line → +2
  };

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={directUpdate}>Direct (+1, not reliable)</button>
      <button onClick={functionalUpdate}>Functional (+2, reliable)</button>
    </div>
  );
}

// ── MULTIPLE STATE vs OBJECT STATE ────────
// Use multiple: independent values (toggle, counter, tab)
// Use object: related values (form fields, user data)
function GoodPatterns() {
  // ✅ Multiple for unrelated state
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('orders');
  const [searchQuery, setSearchQuery] = useState('');

  // ✅ Object for related state
  const [product, setProduct] = useState({
    name: '',
    price: 0,
    category: '',
    inStock: true,
  });

  // Update one field:
  const updateField = (field, value) =>
    setProduct(prev => ({ ...prev, [field]: value }));

  return null;
}
```

---

## 🟠 Next.js Connection

```jsx
// useState works exactly the same in Next.js Client Components
// BUT: must add 'use client' — useState needs browser

// ✅ Client Component (has state):
'use client';
import { useState } from 'react';

function SearchBar() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);

  const handleSearch = async (e) => {
    setQuery(e.target.value);
    if (e.target.value.length > 2) {
      const data = await fetch(`/api/search?q=${e.target.value}`).then(r => r.json());
      setResults(data);
    }
  };

  return (
    <div>
      <input value={query} onChange={handleSearch} placeholder="Search..." />
      {results.map(r => <div key={r.id}>{r.name}</div>)}
    </div>
  );
}

// ❌ Server Component (NO useState — no client-side state):
// async function ProductList() {
//   const [filter, setFilter] = useState('all'); // ❌ ERROR — not a client component
// }

// Pattern: Server fetches data, Client handles interaction
async function ProductPage() {          // Server Component
  const products = await getProducts(); // server-side fetch

  return (
    <div>
      <SearchBar />         {/* Client component — has useState */}
      <ProductList products={products} />  {/* Server component — no state */}
    </div>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Mutating state directly
```jsx
// WRONG: mutates the array — React doesn't detect change!
const [items, setItems] = useState([1, 2, 3]);
items.push(4);       // ❌ mutates!
setItems(items);     // same reference → NO re-render!

// CORRECT: create new array
setItems(prev => [...prev, 4]);  // new reference → re-renders ✅
setItems(prev => prev.filter(i => i !== 2)); // remove
setItems(prev => prev.map(i => i === 2 ? 20 : i)); // update
```

❌ **Mistake 2:** Reading state immediately after setting it
```jsx
const [count, setCount] = useState(0);

const handleClick = () => {
  setCount(count + 1);
  console.log(count); // WRONG: still 0! State updates are async
  // count will be 1 on NEXT render, not now
};

// CORRECT: use the value you're setting
const handleClick = () => {
  const newCount = count + 1;
  setCount(newCount);
  console.log(newCount); // ✅ correct value
};
```

❌ **Mistake 3:** Using state for derived values
```jsx
// WRONG: unnecessary state
const [items, setItems] = useState([...]);
const [count, setCount] = useState(0); // ❌ derived from items.length

// After adding/removing items, must update count too — gets out of sync!

// CORRECT: derive from existing state
const count = items.length; // ✅ always in sync, no extra state
const total = items.reduce((sum, i) => sum + i.price, 0); // derived
```

---

## 🧠 Tricky Interview Question

```jsx
function Counter() {
  const [count, setCount] = useState(0);

  const handleClick = () => {
    setCount(count + 1);
    setCount(count + 1);
    setCount(count + 1);
  };

  return <button onClick={handleClick}>Count: {count}</button>;
}
// After ONE click, what is count?
```
**Answer:** `1` (not 3). All three `setCount(count + 1)` use the same `count` value (the one from this render). React batches them — it's like calling `setCount(0 + 1)` three times. Result: 1.

**Fix for +3:** Use functional updates: `setCount(c => c + 1)` three times → each gets the accumulated value → result: 3.

---

## ⚫ Interview Questions + Answers

**Q1: What is useState and what does it return?**
A1: `useState(initialValue)` is a React Hook that adds state to functional components. It returns an array of exactly two items: `[currentValue, setterFunction]`. The current value is the state for this render. The setter function schedules a re-render with the new value. Convention: destructure as `const [name, setName] = useState(...)`.

**Q2: What is the difference between direct update and functional update?**
A2: Direct: `setCount(count + 1)` — uses `count` from the current closure. Can go stale if called multiple times or in async code. Functional: `setCount(c => c + 1)` — React passes the most current state value to the function. Always safe for multiple calls, async operations, and when new state depends on old state. **Always use functional updates when new state depends on previous state.**

**Q3: Why doesn't React re-render when you mutate an array/object directly?**
A3: React detects state changes by reference equality (`===`). If you `push()` to an array and call `setState(sameArray)`, the reference hasn't changed — React sees old === new and skips the re-render. Always create new arrays/objects: spread `[...old, newItem]` creates a new reference → React detects the change → re-renders.

**Q4: What is lazy initial state?**
A4: When the initial value requires expensive computation (reading localStorage, complex calculation), you can pass a function instead of a value: `useState(() => expensiveCompute())`. The function runs only on the first render. If you write `useState(expensiveCompute())`, the function runs on every render (even though the result is ignored after the first) — wasteful.

**Q5: How many state variables should a component have?**
A5: No fixed rule. Use multiple `useState` for unrelated values (tab, loading, search). Group related values into one object (form fields, pagination: `{page, limit, total}`). Avoid state for things derivable from existing state (total = items.length, filtered = items.filter(...)). Too many state variables can indicate a need to split the component or use `useReducer`.

---

## 🔷 When to Use + When Not to Use
✅ **Use useState when:**
- Value changes over time (user interaction, API response)
- The change should cause a re-render
- Data is local to this component (not shared)
- Simple toggles, counts, form fields

❌ **Avoid useState when:**
- Value doesn't need to trigger re-render → use `useRef`
- Derived from other state → compute directly
- Shared across many components → use Context/Redux/Zustand
- Complex state logic → use `useReducer`

---

## 📊 Visual Diagram

```
useState LIFECYCLE:
──────────────────────────────────────────────────
                    MOUNT (first render)
                          │
  useState(0)  →  React stores 0 in memory slot
                          │
                    Returns [0, setCount]
                          │
                    Component renders
                          │
                    User clicks button
                          │
                    setCount(1) called
                          │
               React schedules re-render
                          │
                    RE-RENDER
                          │
  useState(0)  →  React IGNORES 0, returns stored value
                          │
                    Returns [1, setCount]
                          │
                    Component renders with 1

STATE UPDATE PATTERNS:
──────────────────────────────────────────────────
  Number:    setCount(c => c + 1)
  Boolean:   setIsOpen(v => !v)
  String:    setName(e.target.value)
  Array add: setItems(prev => [...prev, newItem])
  Array rem: setItems(prev => prev.filter(i => i.id !== id))
  Array upd: setItems(prev => prev.map(i => i.id === id ? {...i, done: true} : i))
  Object:    setUser(prev => ({ ...prev, name: 'New' }))
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| useState | Hook to add state to components | Component में state add करना |
| State | Data that changes and drives UI | बदलने वाला data जो UI drive करे |
| Re-render | Component re-runs after state change | State change पर component re-run |
| Setter function | Function to update state | State update करने वाली function |
| Functional update | `setState(prev => ...)` pattern | पुरानी state से नई calculate करना |
| Lazy init | Function for expensive initial state | Expensive initial state के लिए function |
| Derived state | Value computed from existing state | Existing state से compute की value |

---

## ⚡ 3-Line Summary
**English:**
1. `useState(initial)` → `[value, setter]` — call setter → React re-renders with new value.
2. Always create new arrays/objects (spread) — mutating skips re-render. Use functional updates `(prev => ...)` when new state depends on old.
3. Don't use state for derived values (compute them) or non-render-triggering data (use `useRef`).

**Hindi:**
1. `useState(initial)` → `[value, setter]` — setter call करो → React नई value के साथ re-render।
2. Arrays/objects हमेशा नए बनाओ (spread) — mutating re-render skip करता है। Old state पर depend करें तो functional update।
3. Derived values के लिए state मत बनाओ (compute करो) या non-render data के लिए `useRef` use करो।

---

## ➡️ Next Topic
**35. useState — Deep Dive** (02-hooks/ folder) — useState के advanced patterns, batching, और React 18 automatic batching।

---

## 📚 Go Deeper — External Resources

| Type | Link | What you'll learn |
|------|------|-------------------|
| 📺 YouTube | [Akshay Saini — useState](https://www.youtube.com/results?search_query=usestate+hook+react+akshay+saini+namaste) | Deep dive with examples |
| 📺 YouTube | [Web Dev Simplified — useState](https://www.youtube.com/results?search_query=usestate+hook+complete+guide+web+dev+simplified) | All patterns explained |
| 📝 Article | [react.dev — useState](https://react.dev/reference/react/useState) | Official complete reference |
| 📝 Article | [react.dev — State as Snapshot](https://react.dev/learn/state-as-a-snapshot) | Why state doesn't update immediately |
