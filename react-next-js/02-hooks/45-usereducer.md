# 45. useReducer — Complete Guide
# हिंदी में: useReducer — Complex State को Manage करना

---

## 🔵 Simple Definition (English)
`useReducer` is an alternative to `useState` for managing **complex state logic**. You define a **reducer function** that takes the current state and an action, and returns the new state. Like Redux but built into React. Best when state has multiple sub-values or the next state depends on the previous one in complex ways.

## 🔵 सरल परिभाषा (Hindi)
`useReducer` `useState` का alternative है **complex state logic** manage करने के लिए। आप एक **reducer function** define करते हो जो current state और action लेता है, और new state return करता है। Redux जैसा लेकिन React में built-in। Best जब state के multiple sub-values हों या next state previous पर complex तरीके से depend करे।

---

## 🔴 Problem it Solves

```jsx
// PROBLEM: Multiple related states, complex update logic
function Cart() {
  const [items, setItems] = useState([]);
  const [discount, setDiscount] = useState(0);
  const [coupon, setCoupon] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const addItem = (product) => {
    setItems(prev => [...prev, { ...product, qty: 1 }]);
    setDiscount(calculateNewDiscount([...items, product])); // depends on items
    // Many interrelated state updates — hard to keep consistent!
  };

  const removeItem = (id) => {
    const newItems = items.filter(i => i.id !== id);
    setItems(newItems);
    setDiscount(calculateNewDiscount(newItems)); // must update discount too
    if (newItems.length === 0) setCoupon('');   // must clear coupon too
    // Missing any one update = bug!
  };
}
// Scattered, easy to forget related updates → bugs
```

## 🔴 यह क्यों बना? (Hindi)
```jsx
// PROBLEM: Multiple related states scattered across useState calls
// Related updates miss करना easy = bugs

// useReducer: सारी state logic एक reducer में
// Action dispatch करो → reducer सब consistently update करता है
// State transitions का one source of truth!
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define a reducer function
         function reducer(state, action) {
           switch (action.type) {
             case 'ADD_ITEM': return { ...state, items: [...state.items, action.payload] }
             case 'REMOVE': return { ...state, items: state.items.filter(i => i.id !== action.id) }
             default: return state;
           }
         }

Step 2 → Initialize with useReducer
         const [state, dispatch] = useReducer(reducer, initialState);

Step 3 → Dispatch actions to update state
         dispatch({ type: 'ADD_ITEM', payload: product });
         dispatch({ type: 'REMOVE', id: 5 });

Step 4 → Reducer runs, returns new state
         React re-renders with new state

KEY: All state update logic in ONE place (reducer) — not scattered
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Reducer function define करो
         (state, action) => newState

Step 2 → useReducer से initialize करो
         const [state, dispatch] = useReducer(reducer, initialState)

Step 3 → Actions dispatch करो state update के लिए
         dispatch({ type: 'ADD_ITEM', payload: product })

Step 4 → Reducer run होता है, new state return करता है
         React re-render करता है new state के साथ

KEY: सारी state update logic एक जगह (reducer) — scattered नहीं
```

---

## 🟡 Real World Example
**Amazon Shopping Cart:** Adding item, removing item, applying coupon, changing quantity, toggling gift wrap — each action might affect multiple state values (items list, totals, discount, coupon validity). `useReducer` puts all these transitions in one place — you can't accidentally forget to update one piece when another changes.

## 🟡 Real Example Hindi मे
**Amazon Shopping Cart:** Item add करना, remove करना, coupon apply करना, quantity change करना — हर action multiple state values affect कर सकती है। `useReducer` इन सब transitions को एक जगह रखता है — कोई भी update accidentally miss नहीं होती।

---

## 💻 Code Example — Basic

```jsx
import { useReducer } from 'react';

// ── STEP 1: Define initial state ──────────
const initialState = {
  count: 0,
  step: 1,
  history: [],
};

// ── STEP 2: Define reducer ────────────────
// Pure function: (state, action) => newState
// NEVER mutate state directly — always return new object
function counterReducer(state, action) {
  switch (action.type) {
    case 'INCREMENT':
      return {
        ...state,
        count: state.count + state.step,
        history: [...state.history, state.count + state.step],
      };
    case 'DECREMENT':
      return {
        ...state,
        count: state.count - state.step,
        history: [...state.history, state.count - state.step],
      };
    case 'RESET':
      return { ...initialState }; // reset to initial
    case 'SET_STEP':
      return { ...state, step: action.payload };
    default:
      return state; // unknown action → return unchanged state
  }
}

// ── STEP 3: Use in component ──────────────
function Counter() {
  const [state, dispatch] = useReducer(counterReducer, initialState);

  return (
    <div>
      <h2>Count: {state.count}</h2>
      <p>Step: {state.step}</p>

      {/* Dispatch actions — no direct state manipulation! */}
      <button onClick={() => dispatch({ type: 'INCREMENT' })}>
        +{state.step}
      </button>
      <button onClick={() => dispatch({ type: 'DECREMENT' })}>
        -{state.step}
      </button>
      <button onClick={() => dispatch({ type: 'RESET' })}>
        Reset
      </button>

      <input
        type="number"
        value={state.step}
        onChange={e => dispatch({
          type: 'SET_STEP',
          payload: Number(e.target.value)
        })}
        min="1"
      />

      <p>History: {state.history.join(', ')}</p>
    </div>
  );
}
```

## 💻 Code Example — Advanced

```jsx
import { useReducer, useCallback } from 'react';

// ── REAL-WORLD: Shopping Cart ─────────────
const cartInitialState = {
  items: [],       // [{ id, name, price, qty }]
  coupon: null,    // { code, discount }
  loading: false,
  error: null,
};

function cartReducer(state, action) {
  switch (action.type) {

    case 'ADD_ITEM': {
      const existingIndex = state.items.findIndex(i => i.id === action.payload.id);

      if (existingIndex >= 0) {
        // Item exists — increment quantity
        const updatedItems = state.items.map((item, index) =>
          index === existingIndex ? { ...item, qty: item.qty + 1 } : item
        );
        return { ...state, items: updatedItems };
      }

      // New item
      return {
        ...state,
        items: [...state.items, { ...action.payload, qty: 1 }],
      };
    }

    case 'REMOVE_ITEM':
      return {
        ...state,
        items: state.items.filter(i => i.id !== action.id),
        // If cart becomes empty, clear coupon too (related update!)
        coupon: state.items.length === 1 ? null : state.coupon,
      };

    case 'UPDATE_QTY':
      return {
        ...state,
        items: state.items.map(item =>
          item.id === action.id
            ? { ...item, qty: Math.max(1, action.qty) }
            : item
        ),
      };

    case 'APPLY_COUPON':
      return {
        ...state,
        coupon: { code: action.code, discount: action.discount },
        error: null,
      };

    case 'REMOVE_COUPON':
      return { ...state, coupon: null };

    case 'CLEAR_CART':
      return { ...cartInitialState };

    case 'SET_LOADING':
      return { ...state, loading: action.loading };

    case 'SET_ERROR':
      return { ...state, error: action.error, loading: false };

    default:
      return state;
  }
}

// Derived values — computed from state (not stored in state)
function getCartSummary(state) {
  const subtotal = state.items.reduce(
    (sum, item) => sum + item.price * item.qty, 0
  );
  const discount = state.coupon ? subtotal * state.coupon.discount : 0;
  const total = subtotal - discount;
  const itemCount = state.items.reduce((sum, item) => sum + item.qty, 0);
  return { subtotal, discount, total, itemCount };
}

// ── COMPONENT: Uses cartReducer ───────────
function ShoppingCart() {
  const [cart, dispatch] = useReducer(cartReducer, cartInitialState);
  const { subtotal, discount, total, itemCount } = getCartSummary(cart);

  // Stable callbacks — dispatch itself is stable!
  const handleAddItem = useCallback((product) => {
    dispatch({ type: 'ADD_ITEM', payload: product });
  }, []);

  const handleRemove = useCallback((id) => {
    dispatch({ type: 'REMOVE_ITEM', id });
  }, []);

  const handleApplyCoupon = useCallback(async (code) => {
    dispatch({ type: 'SET_LOADING', loading: true });
    try {
      const coupon = await validateCoupon(code);
      dispatch({ type: 'APPLY_COUPON', code, discount: coupon.discount });
    } catch (err) {
      dispatch({ type: 'SET_ERROR', error: err.message });
    }
  }, []);

  return (
    <div>
      <h2>Cart ({itemCount} items)</h2>

      {cart.items.map(item => (
        <div key={item.id}>
          {item.name}
          <input
            type="number"
            value={item.qty}
            onChange={e => dispatch({
              type: 'UPDATE_QTY',
              id: item.id,
              qty: Number(e.target.value)
            })}
          />
          ₹{item.price * item.qty}
          <button onClick={() => handleRemove(item.id)}>×</button>
        </div>
      ))}

      <div>
        Subtotal: ₹{subtotal}
        {cart.coupon && <div>Discount: -₹{discount.toFixed(0)}</div>}
        <strong>Total: ₹{total.toFixed(0)}</strong>
      </div>

      {cart.error && <p className="error">{cart.error}</p>}

      <button onClick={() => dispatch({ type: 'CLEAR_CART' })}>
        Clear Cart
      </button>
    </div>
  );
}
```

---

## 🟠 Next.js Connection

```jsx
// useReducer works in Next.js Client Components

// Good pattern: useReducer + Context for global state
// (alternative to Redux for medium complexity apps)

'use client';
// context/CartContext.jsx
import { createContext, useContext, useReducer } from 'react';

const CartContext = createContext(null);

export function CartProvider({ children }) {
  const [cart, dispatch] = useReducer(cartReducer, cartInitialState);

  return (
    <CartContext.Provider value={{ cart, dispatch }}>
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  const context = useContext(CartContext);
  if (!context) throw new Error('useCart must be used within CartProvider');
  return context;
}

// app/layout.jsx
export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        <CartProvider>
          {children}
        </CartProvider>
      </body>
    </html>
  );
}

// Any component anywhere:
'use client';
function AddToCartButton({ product }) {
  const { dispatch } = useCart();
  return (
    <button onClick={() => dispatch({ type: 'ADD_ITEM', payload: product })}>
      Add to Cart
    </button>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Mutating state in reducer
```jsx
// WRONG: mutating state directly
function reducer(state, action) {
  if (action.type === 'ADD') {
    state.items.push(action.item); // ❌ mutates state!
    return state;                  // same reference → React won't re-render!
  }
}

// CORRECT: return new state object
function reducer(state, action) {
  if (action.type === 'ADD') {
    return {
      ...state,
      items: [...state.items, action.item], // ✅ new array
    };
  }
}
```

❌ **Mistake 2:** Async logic in reducer
```jsx
// WRONG: reducers must be pure — no side effects!
function reducer(state, action) {
  if (action.type === 'FETCH') {
    fetch('/api/data').then(...); // ❌ side effect in reducer!
    return state;
  }
}

// CORRECT: dispatch before/after async logic in component
async function handleFetch() {
  dispatch({ type: 'SET_LOADING', loading: true });
  try {
    const data = await fetch('/api/data').then(r => r.json());
    dispatch({ type: 'SET_DATA', data });
  } catch (err) {
    dispatch({ type: 'SET_ERROR', error: err.message });
  }
}
```

---

## 🧠 Tricky Interview Question

```jsx
const init = (count) => ({ count, doubled: count * 2 });

function reducer(state, action) {
  switch (action.type) {
    case 'INCREMENT': return { count: state.count + 1, doubled: (state.count + 1) * 2 };
    default: return state;
  }
}

function Counter({ startCount }) {
  const [state, dispatch] = useReducer(reducer, startCount, init);
  return <div>Count: {state.count}, Doubled: {state.doubled}</div>;
}
```
**What is the third argument `init` in useReducer?**

**Answer:** The third argument to `useReducer` is an **initializer function** — called lazily on mount with `initialState` as argument. `useReducer(reducer, startCount, init)` → calls `init(startCount)` once to get the initial state. This is "lazy initialization" — similar to `useState(() => expensiveCalc())`. Useful when the initial state requires computation or transformation of the passed value.

---

## ⚫ Interview Questions + Answers

**Q1: What is useReducer and when should you use it over useState?**
A1: `useReducer(reducer, initialState)` manages state through a pure function (reducer) that handles actions. Use it over `useState` when: (1) State has multiple related fields that update together. (2) The next state depends on the previous in complex ways. (3) Update logic involves multiple related pieces. (4) You want to express state transitions explicitly (action-based). Simple standalone values are fine with `useState`.

**Q2: What is a reducer function?**
A2: A reducer is a pure function `(currentState, action) => newState`. It must be pure: no side effects, no mutations, deterministic (same inputs → same output). It receives the current state and an action object (typically `{ type: string, payload: any }`), and returns the complete new state. React's built-in `Array.prototype.reduce` follows the same pattern — hence the name.

**Q3: How does useReducer differ from Redux?**
A3: `useReducer` is local to a component — state doesn't leave the component unless shared via Context. Redux has a global store shared across the whole app. Redux has middleware support (thunk, saga for async), time-travel debugging, and Redux DevTools. `useReducer` + Context can replace Redux for simple global state. Use Redux (or Zustand) when you need: global state at scale, advanced debugging, async middleware, large team conventions.

**Q4: Can you dispatch multiple actions at once?**
A4: Not directly — each `dispatch` triggers one state update. In React 18, multiple dispatches in the same synchronous block are batched into one re-render. If you need to update multiple parts of state together, either: (1) Dispatch one action that the reducer handles by updating all relevant parts. (2) Use multiple dispatches (they'll be batched in React 18). Approach 1 is preferred — keeps related state transitions atomic.

**Q5: What is the action object convention in useReducer?**
A5: By convention (from Redux): `{ type: 'ACTION_TYPE', payload: data }`. `type` is always a string (often SCREAMING_SNAKE_CASE), `payload` carries the data. You can add other fields like `id`, `error`, `meta`. The `type` field is mandatory for `switch` routing; other fields are optional. This convention makes debugging easier but isn't enforced by React — you can dispatch any value including a string or number.

---

## 🔷 When to Use + When Not to Use
✅ **Use useReducer when:**
- State has 3+ related fields that change together
- Multiple actions update state in complex/interrelated ways
- You want to test state logic separately (pure function!)
- Building a mini-Redux pattern for a section

❌ **Use useState instead when:**
- Simple boolean toggle
- Single independent value
- Two unrelated fields in the same component

---

## 📊 Visual Diagram

```
useState vs useReducer:
────────────────────────────────────────────
  useState:
  Component ──setCount(5)──► React re-renders
  (direct)

  useReducer:
  Component ──dispatch({type:'ADD_ITEM', payload: p})──►
    Reducer(currentState, action) ──► newState ──►
  React re-renders (state is the whole newState)

REDUCER FLOW:
────────────────────────────────────────────
          dispatch({ type: 'ADD_ITEM', payload: pizza })
                        │
                        ▼
  reducer(currentState, action) {
    switch (action.type) {
      case 'ADD_ITEM': ←── matched!
        return {
          ...currentState,
          items: [...currentState.items, action.payload]
        }
    }
  }
                        │
                        ▼
              newState = { items: [..., pizza], ... }
                        │
                        ▼
              React re-renders with newState
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Reducer | Pure function: (state, action) → newState | Pure function जो state transform करे |
| Action | Object describing what happened | क्या हुआ यह describe करने वाला object |
| Dispatch | Function to send actions to reducer | Actions reducer को भेजने का function |
| Action type | String identifying the action | Action identify करने वाली string |
| Payload | Data carried with the action | Action के साथ data |
| Initial state | Starting state object | शुरुआती state object |

---

## ⚡ 3-Line Summary
**English:**
1. `useReducer(reducer, initialState)` manages complex state via dispatch + reducer — all update logic in one pure function.
2. Reducer is `(state, action) => newState` — must be pure (no mutations, no side effects).
3. Use over `useState` when state has many related fields or complex transitions — keeps updates atomic and testable.

**Hindi:**
1. `useReducer(reducer, initialState)` complex state को dispatch + reducer से manage करता है — सारी update logic एक pure function में।
2. Reducer `(state, action) => newState` है — pure होना चाहिए (mutations नहीं, side effects नहीं)।
3. `useState` की जगह जब state के many related fields हों या complex transitions हों — updates atomic और testable रहते हैं।

---

## ➡️ Next Topic
**46. useReducer vs useState** — कब क्या use करना है — decision guide।

---

## 📚 Go Deeper — External Resources

| Type | Link | What you'll learn |
|------|------|-------------------|
| 📺 YouTube | [Akshay Saini — useReducer](https://www.youtube.com/results?search_query=usereducer+hook+react+akshay+saini) | useReducer in Hindi |
| 📺 YouTube | [Web Dev Simplified — useReducer](https://www.youtube.com/results?search_query=usereducer+react+web+dev+simplified) | Complete useReducer guide |
| 📝 Article | [react.dev — useReducer](https://react.dev/reference/react/useReducer) | Official reference |
| 📝 Article | [react.dev — Extracting State Logic](https://react.dev/learn/extracting-state-logic-into-a-reducer) | Migration guide |
