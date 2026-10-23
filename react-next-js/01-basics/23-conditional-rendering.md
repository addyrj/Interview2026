# 23. Conditional Rendering
# हिंदी में: Conditional Rendering — Condition के हिसाब से UI दिखाना

---

## 🔵 Simple Definition (English)
**Conditional rendering** means showing different UI based on conditions — state, props, user actions, data availability. Since JSX only accepts **expressions** (not statements), React has several patterns for it: ternary, `&&`, early return, object maps, and more.

## 🔵 सरल परिभाषा (Hindi)
**Conditional rendering** का मतलब है conditions के आधार पर अलग-अलग UI दिखाना — state, props, user actions, data availability। JSX सिर्फ **expressions** accept करता है (statements नहीं), इसलिए React में इसके कई patterns हैं: ternary, `&&`, early return, object maps।

---

## 🔴 Problem it Solves
```jsx
// Every app needs to show/hide elements based on conditions:
// - Show loading spinner while data fetches
// - Show error message if request fails
// - Show login form if not authenticated
// - Show empty state if list is empty
// - Show different layouts based on screen size
// React gives you tools to do this cleanly inside JSX
```

## 🔴 यह क्यों बना? (Hindi)
```jsx
// हर app में conditions पर based UI चाहिए:
// - Data fetch हो रहा है → loading spinner
// - Error आई → error message
// - List खाली है → empty state
// - Login नहीं किया → login form
// React: JSX में cleanly यह सब करने के tools देता है
```

---

## 🟢 How it Works — Step by Step

```
React JSX accepts only EXPRESSIONS (things that return a value):
  ✅ value ? a : b        → ternary expression
  ✅ condition && element → short-circuit AND
  ✅ condition || element → short-circuit OR
  ✅ fn()                 → function call
  ✅ arr.map(fn)          → array expression

React JSX does NOT accept STATEMENTS:
  ❌ if (...) { ... }     → if statement (NOT an expression)
  ❌ for (...) { ... }    → for loop (NOT an expression)
  ❌ switch (...) { ... } → switch statement (NOT an expression)

SOLUTION: compute conditionals BEFORE JSX, or use expressions
```

## 🟢 कैसे काम करता है? (Hindi)
```
React JSX सिर्फ EXPRESSIONS accept करता है:
  ✅ ternary: condition ? a : b
  ✅ && short-circuit
  ✅ function calls, .map()

React JSX STATEMENTS accept नहीं करता:
  ❌ if/else, for, switch

SOLUTION: JSX से पहले conditionals compute करो,
          या expressions use करो
```

---

## 🟡 Real World Example
**Zomato Order Tracking:** One component shows different UI based on order status — "Placing order" (loading), "Order placed" (success info), "Preparing" (kitchen animation), "Out for delivery" (map), "Delivered" (rate button), "Failed" (retry button). All from one component with conditional rendering.

## 🟡 Real Example Hindi mein
**Zomato Order Tracking:** एक component अलग-अलग UI दिखाता है order status के हिसाब से — placing (loading), placed (success), preparing (kitchen animation), out for delivery (map), delivered (rate), failed (retry)। यह सब conditional rendering से।

---

## 💻 Code Example — Basic

```jsx
import { useState } from 'react';

// ── ALL CONDITIONAL PATTERNS ──────────────

function OrderStatus({ status, user, items }) {

  // PATTERN 1: Early return (guard clause)
  // Use when: entire component shouldn't render
  if (!user) return <LoginPrompt />;  // entire page guard

  // PATTERN 2: Variable assignment before JSX
  // Use when: complex logic — compute result, use in JSX
  let statusMessage;
  let statusIcon;
  if (status === 'pending')    { statusMessage = 'Placing order...'; statusIcon = '⏳'; }
  else if (status === 'placed')  { statusMessage = 'Order placed!';   statusIcon = '✅'; }
  else if (status === 'cooking') { statusMessage = 'Kitchen at work'; statusIcon = '👨‍🍳'; }
  else if (status === 'delivered') { statusMessage = 'Enjoy!';        statusIcon = '🎉'; }
  else                           { statusMessage = 'Unknown status';  statusIcon = '❓'; }

  return (
    <div>
      {/* PATTERN 3: Ternary operator */}
      {/* Use when: either/or — two different elements */}
      <h2>
        {status === 'delivered'
          ? 'Order Delivered! 🎉'
          : 'Order in Progress...'}
      </h2>

      {/* PATTERN 4: && short-circuit */}
      {/* Use when: show something OR show nothing */}
      {status === 'delivered' && (
        <button>Rate your order ⭐</button>
      )}

      {/* PATTERN 5: !! or Boolean() to prevent '0' bug */}
      {/* items.length && <List/> would render "0" if empty! */}
      {items.length > 0 && (          // ✅ explicit comparison
        <ul>
          {items.map(item => <li key={item.id}>{item.name}</li>)}
        </ul>
      )}

      {/* PATTERN 6: null to render nothing */}
      {status === 'cancelled' ? <CancelledMessage /> : null}

      {/* Variable from above */}
      <p>{statusIcon} {statusMessage}</p>

    </div>
  );
}

// ── OBJECT MAP PATTERN ────────────────────
// Use when: many conditions → clean alternative to long if/else
const ORDER_STATUS_UI = {
  pending:   { icon: '⏳', text: 'Placing...', color: 'gray'   },
  placed:    { icon: '✅', text: 'Placed!',    color: 'green'  },
  cooking:   { icon: '👨‍🍳', text: 'Cooking',   color: 'orange' },
  delivered: { icon: '🎉', text: 'Delivered!', color: 'green'  },
  cancelled: { icon: '❌', text: 'Cancelled',  color: 'red'    },
};

function StatusBadge({ status }) {
  const config = ORDER_STATUS_UI[status] || ORDER_STATUS_UI.pending;
  return (
    <span style={{ color: config.color }}>
      {config.icon} {config.text}
    </span>
  );
}
```

## 💻 Code Example — Advanced

```jsx
import { useState, useEffect } from 'react';

// ── LOADING / ERROR / SUCCESS PATTERN ────
// The most common async pattern in React
function ProductDetails({ productId }) {
  const [state, setState] = useState({
    data: null,
    loading: true,
    error: null,
  });

  useEffect(() => {
    setState({ data: null, loading: true, error: null });

    fetch(`/api/products/${productId}`)
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then(data => setState({ data, loading: false, error: null }))
      .catch(err => setState({ data: null, loading: false, error: err.message }));
  }, [productId]);

  const { data: product, loading, error } = state;

  // GUARD CLAUSE PATTERN: handle loading/error first
  if (loading) return <Spinner />;
  if (error)   return <ErrorMessage message={error} onRetry={() => setState({ ...state, loading: true })} />;
  if (!product) return null; // shouldn't happen but TypeScript safety

  // Main render — product is guaranteed non-null here!
  return (
    <div>
      <h1>{product.name}</h1>
      <p>₹{product.price}</p>
      {product.discount > 0 && (
        <span className="badge">-{product.discount}% OFF</span>
      )}
    </div>
  );
}

// ── COMPLEX CONDITIONAL RENDERING ────────
// Use component for complex logic
function CartSummary({ cart }) {
  const isEmpty = cart.items.length === 0;
  const hasDiscount = cart.discount > 0;
  const isFreeDelivery = cart.total >= 500;

  return (
    <div className="cart-summary">
      {/* Early return for empty cart */}
      {isEmpty ? (
        <EmptyCart message="Your cart is empty" />
      ) : (
        <>
          <CartItemList items={cart.items} />

          {/* Conditional discount row */}
          {hasDiscount && (
            <div className="discount-row">
              <span>Discount</span>
              <span className="green">-₹{cart.discount}</span>
            </div>
          )}

          {/* Delivery fee — conditional on order value */}
          <div className="delivery-row">
            <span>Delivery</span>
            {isFreeDelivery ? (
              <span className="green">FREE</span>
            ) : (
              <span>₹{cart.deliveryFee}</span>
            )}
          </div>

          {/* Progress to free delivery */}
          {!isFreeDelivery && (
            <p className="delivery-hint">
              Add ₹{500 - cart.total} more for free delivery!
            </p>
          )}

          <div className="total">
            Total: ₹{cart.total + (isFreeDelivery ? 0 : cart.deliveryFee) - cart.discount}
          </div>

          <button className="checkout-btn">Proceed to Checkout</button>
        </>
      )}
    </div>
  );
}

// ── ROLE-BASED RENDERING ─────────────────
function DashboardPage({ user }) {
  const canEdit    = user?.role === 'admin' || user?.role === 'editor';
  const canDelete  = user?.role === 'admin';
  const isVerified = user?.emailVerified;

  return (
    <div>
      <h1>Dashboard</h1>

      {!isVerified && (
        <div className="banner warning">
          Please verify your email to unlock all features.
        </div>
      )}

      {canEdit && <EditToolbar />}

      <ContentList />

      {canDelete && (
        <div className="danger-zone">
          <h3>Danger Zone</h3>
          <button className="delete-all">Delete All</button>
        </div>
      )}
    </div>
  );
}
```

---

## 🟠 Next.js Connection

```jsx
// Conditional rendering works identically in Next.js
// Key difference: Server Components can't use useState/hooks

// ── SERVER COMPONENT — use if/else freely ─
async function ProductPage({ params, searchParams }) {
  const product = await getProduct(params.id);

  // Server-side conditional — no hooks needed!
  if (!product) {
    notFound(); // Next.js: renders 404 page
  }

  return (
    <div>
      <h1>{product.name}</h1>
      {product.inStock
        ? <OrderButton productId={product.id} />  {/* Client Component */}
        : <OutOfStockBadge />}                     {/* Server Component */}
    </div>
  );
}

// ── CLIENT COMPONENT — hooks-based conditions ─
'use client';
function InteractiveProduct({ product }) {
  const [activeTab, setActiveTab] = useState('description');

  return (
    <div>
      <TabBar active={activeTab} onChange={setActiveTab} />

      {activeTab === 'description' && <Description text={product.description} />}
      {activeTab === 'reviews' && <ReviewList productId={product.id} />}
      {activeTab === 'specs' && <SpecsTable specs={product.specs} />}
    </div>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** The `0 &&` bug
```jsx
// WRONG: renders "0" on screen when cart is empty!
function CartIcon() {
  const cartCount = 0;
  return <div>{cartCount && <Badge count={cartCount} />}</div>;
  // 0 && anything = 0 (falsy, but JSX renders numbers!)
  // Result: <div>0</div> — "0" shows on screen!
}

// CORRECT: explicit boolean check
return <div>{cartCount > 0 && <Badge count={cartCount} />}</div>;
// OR: convert to boolean
return <div>{!!cartCount && <Badge count={cartCount} />}</div>;
```

❌ **Mistake 2:** Returning `undefined` from ternary
```jsx
// WRONG: undefined in JSX is sometimes visible
{isLoggedIn ? <Profile /> : undefined} // ❌ — use null instead

// CORRECT: null renders nothing
{isLoggedIn ? <Profile /> : null}       // ✅
// OR: && which returns undefined but React handles it
{isLoggedIn && <Profile />}             // ✅
```

---

## 🧠 Tricky Interview Question

```jsx
function App() {
  const [showA, setShowA] = useState(true);

  return (
    <div>
      {showA ? <ComponentA /> : <ComponentB />}
      <button onClick={() => setShowA(s => !s)}>Toggle</button>
    </div>
  );
}

function ComponentA() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(c => c + 1)}>A: {count}</button>;
}

function ComponentB() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(c => c + 1)}>B: {count}</button>;
}

// You increment ComponentA to count=3, then toggle.
// When you toggle back to ComponentA, what is its count?
```
**Answer:** `0`. When you toggle from A to B, React **unmounts** ComponentA and **mounts** ComponentB. When you toggle back, React **remounts** a fresh ComponentA — state resets to 0. React's diffing sees a component type change (A → B → A), so it destroys and recreates the tree each time. State doesn't persist across unmounts.

---

## ⚫ Interview Questions + Answers

**Q1: Why can't you use if/else directly inside JSX?**
A1: JSX is compiled to `React.createElement()` calls. Only expressions (things that evaluate to a value) can be passed as arguments. `if/else` is a statement (controls flow, doesn't return a value). You can use ternary `? :` (expression), `&&` (expression), IIFE `(() => { if...; return... })()` (expression), or compute before JSX and use variables.

**Q2: What are the different ways to conditionally render in React?**
A2: (1) Early return / guard clause — return early for edge cases. (2) Variable assignment — compute what to show in if/else before JSX. (3) Ternary `condition ? A : B` — two options. (4) `&&` short-circuit — show or nothing. (5) Object map `{conditions}[key]` — many options cleanly. (6) Component abstraction — extract complex conditional into its own component.

**Q3: What is the difference between returning `null` and `false` in JSX?**
A3: Both render nothing. `null`, `false`, `undefined`, `true` are valid children that render nothing. However, `0` renders as the string "0" — this is the common bug with `count && <Badge />`. React renders `false` as nothing, but renders `0` as text because it's a valid number value. Always use explicit boolean checks: `count > 0 &&` not `count &&`.

**Q4: Explain the loading/error/success pattern in React.**
A4: The standard pattern for async data: (1) State: `{ data: null, loading: true, error: null }`. (2) In useEffect: fetch → on success set `{ data, loading: false }` → on error set `{ error, loading: false }`. (3) Render with guard clauses: `if (loading) return <Spinner />`, `if (error) return <Error />`, then render data. This ensures all three states are handled explicitly.

**Q5: When should you use early returns vs inline ternaries?**
A5: Early return for: entire-component guards (auth, loading), guard clauses that change what the whole component renders. Inline ternary for: small local UI variations (button text, badge color, one element vs another). Rule of thumb: if the condition affects the whole component's render, early return; if it affects one part of JSX, inline ternary or &&.

---

## 🔷 When to Use + When Not to Use
✅ **Use each pattern when:**
- Early return: entire component condition, guard clauses
- Ternary: two clear alternatives (A or B)
- `&&`: show something or nothing
- Object map: 3+ conditions that need different UI
- Variable: complex logic that doesn't fit inline

❌ **Avoid:**
- `count &&` for numbers → use `count > 0 &&`
- Deeply nested ternaries → extract to component or variable
- Long if/else chains → object map or extracted component

---

## 📊 Visual Diagram

```
CONDITIONAL RENDERING PATTERNS:
──────────────────────────────────────────────
  Pattern              When to use
  ──────────────────────────────────────────
  if (x) return null   Whole component guard
  variable = ...       Complex logic before JSX
  x ? A : B            Two options (either/or)
  x && A               One option (show or nothing)
  map[x]               Many options (enum/status)
  component(x)         Very complex logic → extract!

THE 0 BUG:
──────────────────────────────────────────────
  cart.length && <Badge />
  
  When cart = []:
  cart.length = 0
  0 && <Badge /> = 0    ← renders "0"! ❌

  Fix: cart.length > 0 && <Badge />
  0 > 0 = false
  false && <Badge /> = false → renders nothing ✅

LOADING STATE PATTERN:
──────────────────────────────────────────────
  if (loading) → <Spinner />
       ↓
  if (error)   → <ErrorUI />
       ↓
  if (!data)   → null (edge case)
       ↓
  <MainUI />   ← happy path (data guaranteed here!)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Conditional rendering | Show UI based on condition | Condition के हिसाब से UI दिखाना |
| Ternary | `condition ? a : b` — two options | दो options में से एक |
| Short-circuit | `&&` — lazy evaluation | Lazy evaluation |
| Guard clause | Early return for edge cases | Edge cases के लिए early return |
| Object map | Key-value lookup for conditions | Conditions के लिए key-value lookup |
| Truthy/falsy | JS values that are true/false | JS में true/false जैसी values |

---

## ⚡ 3-Line Summary
**English:**
1. JSX only accepts expressions — use ternary, `&&`, object maps, or computed variables (not if/else directly in JSX).
2. `0 &&` renders "0" on screen — always use `count > 0 &&` or explicit boolean for numbers.
3. Loading/error/success pattern: guard clauses for loading and error states, then render main UI with guaranteed data.

**Hindi:**
1. JSX सिर्फ expressions accept करता है — ternary, `&&`, object maps, या computed variables use करो (if/else directly नहीं)।
2. `0 &&` screen पर "0" render करता है — numbers के लिए हमेशा `count > 0 &&` या explicit boolean use करो।
3. Loading/error/success pattern: loading और error के लिए guard clauses, फिर guaranteed data के साथ main UI।

---

## ➡️ Next Topic
**24. List Rendering + key Prop** — Arrays को JSX में render करना और key prop क्यों critical है।
