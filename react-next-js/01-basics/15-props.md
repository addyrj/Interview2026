# 15. Props — Passing Data to Components
# हिंदी में: Props — Components को Data Pass करना

---

## 🔵 Simple Definition (English)
**Props** (short for properties) are how you pass data from a **parent component to a child component**. Props are read-only — the child cannot modify them. They work like HTML attributes but can pass any JavaScript value: strings, numbers, objects, arrays, functions, even other components.

## 🔵 सरल परिभाषा (Hindi)
**Props** (properties का short form) वो तरीका है जिससे आप **parent component से child component को data pass** करते हो। Props read-only होते हैं — child उन्हें modify नहीं कर सकता। HTML attributes की तरह काम करते हैं लेकिन कोई भी JavaScript value pass कर सकते हो: strings, numbers, objects, arrays, functions, यहाँ तक कि अन्य components भी।

---

## 🔴 Problem it Solves
```jsx
// WITHOUT props: hardcoded, not reusable
function ProductCard() {
  return (
    <div>
      <h2>Pizza</h2>     {/* always Pizza — can't reuse! */}
      <p>₹299</p>
    </div>
  );
}

// WITH props: dynamic, reusable
function ProductCard({ name, price }) {
  return (
    <div>
      <h2>{name}</h2>    {/* whatever parent passes */}
      <p>₹{price}</p>
    </div>
  );
}

// Use same component for different data:
<ProductCard name="Pizza" price={299} />
<ProductCard name="Burger" price={149} />
<ProductCard name="Pasta" price={199} />
```

## 🔴 यह क्यों बना? (Hindi)
```jsx
// Props के बिना: hardcoded values — component reuse नहीं होता
// Props से: parent dynamic data pass करता है → same component different data के साथ
// Props = component का "input interface"
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → Parent renders child with attributes:
         <ProductCard name="Pizza" price={299} onClick={handleClick} />

Step 2 → React bundles all attributes into a 'props' object:
         props = { name: "Pizza", price: 299, onClick: handleClick }

Step 3 → React calls: ProductCard(props)
         OR with destructuring: ProductCard({ name, price, onClick })

Step 4 → Child uses props — READ ONLY! Can't do props.name = "Burger"

Step 5 → Parent re-renders with new props → child re-renders with new values
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Parent child को attributes के साथ render करता है
Step 2 → React सभी attributes को 'props' object में bundle करता है
Step 3 → React calls: ProductCard(props)
Step 4 → Child props use करता है — READ ONLY! Modify नहीं कर सकता
Step 5 → Parent नए props के साथ re-render → child भी नए values के साथ
```

---

## 🟡 Real World Example
**Zomato RestaurantCard:** Same component renders all 50+ restaurant cards on the page. Each card looks identical in structure but shows different data (name, rating, cuisine, delivery time). All this comes from props — parent passes each restaurant's data, child renders it.

## 🟡 Real Example Hindi मे
**Zomato RestaurantCard:** Same component page पर 50+ restaurant cards render करती है। हर card की structure same है लेकिन data अलग (name, rating, cuisine, delivery time)। यह सब props से आता है — parent हर restaurant का data pass करता है, child उसे render करता है।

---

## 💻 Code Example — Basic

```jsx
// ── PROPS BASICS ──────────────────────────

// 1. String props: use quotes (no {})
// 2. All other types: use {} — numbers, booleans, objects, arrays, functions
function RestaurantCard({ name, rating, cuisine, deliveryTime, isOpen, tags, onSelect }) {
  return (
    <div
      className={`card ${isOpen ? 'open' : 'closed'}`}
      onClick={onSelect}  // function prop called on click
    >
      <h3>{name}</h3>
      <span>⭐ {rating}</span>
      <span>{cuisine}</span>
      <span>🕐 {deliveryTime} mins</span>
      <span>{isOpen ? '🟢 Open' : '🔴 Closed'}</span>
      <div>
        {tags.map(tag => <span key={tag} className="tag">{tag}</span>)}
      </div>
    </div>
  );
}

// Parent passes different props for each card
function RestaurantList() {
  const handleSelect = (name) => console.log('Selected:', name);

  return (
    <div>
      <RestaurantCard
        name="Pizza Palace"           // string: no {}
        rating={4.5}                  // number: needs {}
        cuisine="Italian"             // string: no {}
        deliveryTime={30}             // number: needs {}
        isOpen={true}                 // boolean: needs {}
        tags={['veg', 'pizza', 'fast']}  // array: needs {}
        onSelect={() => handleSelect('Pizza Palace')} // function: needs {}
      />

      <RestaurantCard
        name="Burger Barn"
        rating={4.2}
        cuisine="American"
        deliveryTime={20}
        isOpen={false}
        tags={['non-veg', 'burgers']}
        onSelect={() => handleSelect('Burger Barn')}
      />
    </div>
  );
}

// ── CHILDREN PROP ─────────────────────────
// Special prop: the content between opening and closing tags
function Card({ title, children }) {
  return (
    <div className="card">
      <h2>{title}</h2>
      <div className="card-body">
        {children}  {/* renders whatever is between <Card> tags */}
      </div>
    </div>
  );
}

// Usage:
function App() {
  return (
    <Card title="Order Summary">
      <p>Pizza × 1 — ₹299</p>    {/* these become children */}
      <p>Burger × 2 — ₹298</p>
      <strong>Total: ₹597</strong>
    </Card>
  );
}
```

## 💻 Code Example — Advanced

```jsx
import { useState } from 'react';

// ── DESTRUCTURING + DEFAULT VALUES ────────
function Button({
  label,
  onClick,
  variant = 'primary',    // default value
  size = 'medium',         // default value
  disabled = false,        // default value
  icon = null,             // default value
  ...rest                  // capture all other props (className, style, etc.)
}) {
  const classes = `btn btn-${variant} btn-${size}`;

  return (
    <button
      className={classes}
      onClick={onClick}
      disabled={disabled}
      {...rest}           // spread remaining props to DOM element
    >
      {icon && <span className="icon">{icon}</span>}
      {label}
    </button>
  );
}

// ── FUNCTION PROPS (CALLBACK PATTERN) ─────
// Parent passes function → child calls it → parent updates state
function Counter({ initialCount = 0, onCountChange }) {
  const [count, setCount] = useState(initialCount);

  const increment = () => {
    const newCount = count + 1;
    setCount(newCount);
    onCountChange?.(newCount);  // optional chaining — if provided, call it
  };

  return (
    <div>
      <span>{count}</span>
      <button onClick={increment}>+</button>
    </div>
  );
}

function App() {
  const [totalCount, setTotalCount] = useState(0);

  return (
    <div>
      <p>Total: {totalCount}</p>
      <Counter
        initialCount={0}
        onCountChange={count => setTotalCount(count)}
      />
    </div>
  );
}

// ── RENDER PROPS PATTERN ──────────────────
// Function prop that returns JSX — flexible, powerful
function DataFetcher({ url, render }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(url).then(r => r.json()).then(d => {
      setData(d);
      setLoading(false);
    });
  }, [url]);

  // Call the render prop with current state
  return render({ data, loading });
}

// Usage: caller decides how to render the data!
function UserPage() {
  return (
    <DataFetcher
      url="/api/users/1"
      render={({ data: user, loading }) =>
        loading
          ? <Spinner />
          : <UserCard user={user} />
      }
    />
  );
}

// ── PROP SPREADING ────────────────────────
// Pass all parent props down to child (use carefully!)
function EnhancedInput({ label, error, ...inputProps }) {
  // inputProps = { type, value, onChange, placeholder, ... }
  return (
    <div>
      <label>{label}</label>
      <input {...inputProps} className={error ? 'invalid' : ''} />
      {error && <span className="error">{error}</span>}
    </div>
  );
}

// Usage: pass input props naturally
<EnhancedInput
  label="Email"
  type="email"
  value={email}
  onChange={handleChange}
  placeholder="Enter email"
  error={emailError}
/>
```

---

## 🟠 Next.js Connection

```jsx
// Props work the same in Next.js Server and Client Components

// ── NEXT.JS: searchParams and params are props ──
// app/products/[id]/page.jsx
async function ProductPage({ params, searchParams }) {
  // params = { id: '123' } — from URL /products/123
  // searchParams = { color: 'red', size: 'M' } — from URL ?color=red&size=M

  const product = await fetch(`/api/products/${params.id}`).then(r => r.json());

  return (
    <div>
      <h1>{product.name}</h1>
      {searchParams.color && <p>Color: {searchParams.color}</p>}
    </div>
  );
}

// Server → Client component: pass data as props
async function Dashboard() {
  const userData = await getCurrentUser(); // server

  return (
    <ClientDashboard
      user={userData}           // props flow server → client
      initialData={userData.cart}
    />
  );
}

'use client';
function ClientDashboard({ user, initialData }) {
  // received as props from Server Component ✅
  const [cart, setCart] = useState(initialData);
  return <div>Hello, {user.name}!</div>;
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Modifying props
```jsx
// WRONG: props are read-only — never mutate!
function Card({ style }) {
  style.color = 'red'; // ❌ mutates parent's object!
  return <div style={style}>Card</div>;
}

// CORRECT: create a new object
function Card({ style }) {
  return <div style={{ ...style, color: 'red' }}>Card</div>; // ✅
}
```

❌ **Mistake 2:** Forgetting {} for non-string props
```jsx
// WRONG: price becomes string "299", not number 299
<ProductCard price="299" />     // ❌ string
<ProductCard isActive="true" /> // ❌ string (always truthy!)
<ProductCard items="[1,2,3]" /> // ❌ string, not array

// CORRECT: {} for non-strings
<ProductCard price={299} />     // ✅ number
<ProductCard isActive={true} /> // ✅ boolean
<ProductCard items={[1,2,3]} /> // ✅ array
```

❌ **Mistake 3:** Prop drilling too deep
```jsx
// WRONG: passing userId through 5 layers that don't use it
// App → Page → Section → Widget → Button (only Button needs userId)
// Solution: Context API or state management

// CORRECT: for deep data needs, use Context
```

---

## 🧠 Tricky Interview Question

```jsx
function Greeting({ name = 'Guest' }) {
  return <h1>Hello, {name}!</h1>;
}

// What does each render?
<Greeting />                    // (a)
<Greeting name="Aditya" />      // (b)
<Greeting name={null} />        // (c)
<Greeting name={undefined} />   // (d)
```
**Answer:**
- (a) `Hello, Guest!` — no prop → default value `'Guest'` used
- (b) `Hello, Aditya!` — prop value used
- (c) `Hello, !` — `null` is not `undefined`, so default NOT used; `null` renders empty string in JSX
- (d) `Hello, Guest!` — `undefined` triggers default value

Key insight: default props only activate for `undefined`, not `null`.

---

## ⚫ Interview Questions + Answers

**Q1: What are props in React?**
A1: Props are inputs passed from a parent component to a child component — like function arguments. They're bundled as a plain object by React. You can pass any JavaScript value: primitives, objects, arrays, functions, other components. Props are read-only in the child — the child describes what it needs, the parent provides it.

**Q2: Can a child component modify its props?**
A2: No — props are immutable (read-only) in the child. If a child needs to change a value, it should communicate back to the parent via a callback function prop (`onChange`, `onSelect`). The parent holds the state, updates it on the callback, and re-renders the child with new props. This "lifting state up" pattern keeps data flow predictable.

**Q3: What is the children prop?**
A3: `children` is a special prop automatically provided by React — it contains whatever you put between a component's opening and closing tags. `<Card>Hello</Card>` → `props.children = "Hello"`. It can be text, elements, components, or an array. You can also explicitly pass: `<Card children={<p>Hello</p>} />`. Use it to build wrapper/container components (modals, cards, layouts).

**Q4: What is prop drilling and when is it a problem?**
A4: Prop drilling = passing props through intermediate components that don't use them, just to reach a deeply nested component. It's a problem when: chains are 3+ levels deep, intermediate components become cluttered with unrelated props, changes require updating many files. Solution: Context API for app-level data, or composition (pass the consuming component itself down, not just data).

**Q5: What is the difference between props and state?**
A5: Props = data passed IN from parent (external, read-only). State = data managed BY the component itself (internal, mutable via setState). Props change when parent re-renders with new values. State changes via useState setter. A component's job: use props as "instructions from outside" and state as "memory of what's happened inside." When in doubt: can the parent own this? → props. Does only this component need it? → state.

---

## 🔷 When to Use + When Not to Use
✅ **Use props when:**
- Passing data from parent to child
- Configuring a reusable component (button variant, size)
- Passing event handlers up (callback pattern)
- Composing layouts (`children` prop)

❌ **Don't use props when:**
- Data needs to go 5+ levels deep → Context or state manager
- Data is shared globally (auth, theme) → Context
- Component needs to own and mutate the data → State

---

## 📊 Visual Diagram

```
PROPS FLOW (one-way, top-down):
──────────────────────────────────────────────
  App (owns state: products=[...])
      │
      │ products={products}   ← passes prop
      ▼
  ProductList({ products })
      │
      │ product={product}     ← passes single item
      ▼
  ProductCard({ product })
      │
      │ price={product.price} ← passes field
      ▼
  PriceTag({ price })

DATA FLOW:
──────────────────────────────────────────────
  Parent                   Child
  ┌──────────────┐         ┌──────────────┐
  │ state = data │         │              │
  │              │─props──►│ reads props  │
  │              │◄─event──│ calls fn prop│
  │ updates state│         │              │
  └──────────────┘         └──────────────┘
  One-way data flow: parent → child (props)
  Child communicates up via callback functions
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Props | Data inputs from parent | Parent से data inputs |
| Read-only | Cannot be modified by child | Child modify नहीं कर सकता |
| Destructuring | Extract props into variables | Props को variables में extract करना |
| Default props | Fallback when prop not provided | Prop न दिया जाए तो fallback |
| children | Content between component tags | Component tags के बीच का content |
| Prop drilling | Passing props many levels down | Props कई levels नीचे pass करना |
| Callback prop | Function passed as prop | Function को prop की तरह pass करना |

---

## ⚡ 3-Line Summary
**English:**
1. Props pass data from parent to child — like function arguments. They're read-only in the child.
2. Any JS value can be a prop: strings (no `{}`), numbers/booleans/objects/functions (use `{}`). `children` is the content between tags.
3. Callback props (functions) let children communicate back to parent — child calls the function, parent updates state.

**Hindi:**
1. Props parent से child को data pass करते हैं — function arguments जैसे। Child में read-only होते हैं।
2. कोई भी JS value prop हो सकती है: strings (no `{}`), numbers/booleans/objects/functions (`{}` चाहिए)। `children` tags के बीच का content है।
3. Callback props (functions) children को parent से communicate करने देते हैं — child function call करता है, parent state update करता है।

---

## ➡️ Next Topic
**16. Props — Types + Validation** — PropTypes से props को validate करना और TypeScript के साथ type-safe props।
