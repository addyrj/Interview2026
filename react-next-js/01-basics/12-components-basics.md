# 12. Components — The Building Blocks of React
# हिंदी में: Components — React की Building Blocks

---

## 🔵 Simple Definition (English)
A **React component** is a reusable, self-contained piece of UI. It's a JavaScript function (or class) that accepts inputs (**props**) and returns JSX describing what should appear on screen. Components are the fundamental unit of any React application — you build the entire UI by composing them.

## 🔵 सरल परिभाषा (Hindi)
**React component** UI का एक reusable, self-contained टुकड़ा है। यह एक JavaScript function (या class) है जो inputs (**props**) accept करता है और JSX return करता है जो screen पर दिखाना है। Components किसी भी React application की fundamental unit हैं — आप उन्हें compose करके पूरी UI बनाते हो।

---

## 🔴 Problem it Solves
Without components:
```html
<!-- Repeat this HTML for every product -->
<div class="card">
  <img src="/pizza.jpg" />
  <h2>Pizza</h2>
  <p>₹299</p>
  <button>Add to Cart</button>
</div>
<!-- Same HTML again... and again... -->
```
With components:
```jsx
<ProductCard product={pizza} />
<ProductCard product={burger} />
<ProductCard product={pasta} />
// Write once, use everywhere — change once, updates everywhere
```

## 🔴 यह क्यों बना? (Hindi)
```jsx
// बिना components: हर product के लिए same HTML repeat
// Components से: एक बार लिखो, कहीं भी use करो
// Change करना = सिर्फ एक component बदलो → सब जगह update!
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define: function that returns JSX
         function Button({ label }) {
           return <button>{label}</button>;
         }

Step 2 → Component NAME must be CAPITALIZED
         <Button /> — React knows it's a component (not HTML element)
         <button /> — React treats as HTML element

Step 3 → Compose: use components inside other components
         <Header>
           <Logo />
           <Nav />
           <Button label="Login" />
         </Header>

Step 4 → React renders the component tree into Real DOM
         (Virtual DOM diff keeps it efficient)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Define: JSX return करने वाला function
Step 2 → Component NAME CAPITALIZED होना चाहिए
         <Button /> = React component
         <button /> = HTML element

Step 3 → Compose: components के अंदर components
Step 4 → React component tree को Real DOM में render करता है
```

---

## 🟡 Real World Example
**Zomato's UI** is entirely made of components: `AppHeader`, `SearchBar`, `RestaurantList`, `RestaurantCard`, `RatingBadge`, `AddToCartButton`, `CartDrawer`. Each is independent — you can update `RatingBadge` styling without touching `RestaurantCard`. Teams work on different components simultaneously.

## 🟡 Real Example Hindi mein
**Zomato की UI** पूरी components से बनी है: `AppHeader`, `SearchBar`, `RestaurantCard`, `RatingBadge`, etc। हर component independent है — `RatingBadge` बदलो, `RestaurantCard` को touch नहीं करना। Teams अलग-अलग components पर simultaneously काम कर सकती हैं।

---

## 💻 Code Example — Basic

```jsx
// ── ANATOMY OF A COMPONENT ───────────────
import { useState } from 'react';

// SIMPLE: pure display component (no state)
function ProductBadge({ type }) {
  // type = 'bestseller' | 'new' | 'sale'
  const config = {
    bestseller: { label: '🔥 Best Seller', color: '#ff6b35' },
    new: { label: '✨ New',             color: '#4ecdc4' },
    sale: { label: '🏷️ Sale',           color: '#e74c3c' },
  };

  const { label, color } = config[type] || { label: '', color: '' };
  return (
    <span style={{ background: color, padding: '2px 8px', borderRadius: 4 }}>
      {label}
    </span>
  );
}

// STATEFUL: component with its own state
function ProductCard({ product }) {
  const [isWishlisted, setIsWishlisted] = useState(false);
  const [quantity, setQuantity] = useState(1);

  return (
    <div className="product-card">
      {/* Compose: use smaller component inside */}
      {product.badge && <ProductBadge type={product.badge} />}

      <img src={product.image} alt={product.name} />
      <h2>{product.name}</h2>
      <p>₹{product.price * quantity}</p>

      {/* Quantity selector */}
      <div>
        <button onClick={() => setQuantity(q => Math.max(1, q - 1))}>-</button>
        <span>{quantity}</span>
        <button onClick={() => setQuantity(q => q + 1)}>+</button>
      </div>

      {/* Wishlist toggle */}
      <button
        onClick={() => setIsWishlisted(w => !w)}
        aria-label={isWishlisted ? 'Remove from wishlist' : 'Add to wishlist'}
      >
        {isWishlisted ? '❤️' : '🤍'}
      </button>
    </div>
  );
}

// CONTAINER: orchestrates child components
function ProductGrid({ products }) {
  return (
    <div className="grid">
      {products.map(product => (
        // Each ProductCard is independent — own state, own lifecycle
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  );
}

// ROOT: top-level component
function App() {
  const products = [
    { id: 1, name: 'Pizza', price: 299, badge: 'bestseller', image: '/pizza.jpg' },
    { id: 2, name: 'Burger', price: 149, badge: 'new', image: '/burger.jpg' },
    { id: 3, name: 'Pasta', price: 199, badge: null, image: '/pasta.jpg' },
  ];

  return (
    <div>
      <h1>Zomato Eats</h1>
      <ProductGrid products={products} />
    </div>
  );
}

export default App;
```

## 💻 Code Example — Advanced

```jsx
// ── COMPONENT PATTERNS ────────────────────
import { useState, useCallback, memo } from 'react';

// PATTERN 1: Controlled component (form elements)
function EmailInput({ value, onChange, error }) {
  return (
    <div className="field">
      <input
        type="email"
        value={value}          // controlled by parent's state
        onChange={onChange}    // parent updates state
        className={error ? 'invalid' : ''}
      />
      {error && <span className="error-msg">{error}</span>}
    </div>
  );
}

// PATTERN 2: Compound components
// Parent shares state with children implicitly (via Context)
function Tabs({ children, defaultTab = 0 }) {
  const [activeTab, setActiveTab] = useState(defaultTab);

  return (
    <div className="tabs">
      {/* Pass activeTab and setter to children */}
      {React.Children.map(children, (child, index) =>
        React.cloneElement(child, {
          isActive: index === activeTab,
          onActivate: () => setActiveTab(index),
          index,
        })
      )}
    </div>
  );
}

function Tab({ label, isActive, onActivate, children }) {
  return (
    <div>
      <button
        className={isActive ? 'active' : ''}
        onClick={onActivate}
      >
        {label}
      </button>
      {isActive && <div className="tab-content">{children}</div>}
    </div>
  );
}

// Usage:
function ProductPage() {
  return (
    <Tabs defaultTab={0}>
      <Tab label="Description">Product description here...</Tab>
      <Tab label="Reviews">Customer reviews...</Tab>
      <Tab label="Delivery">Delivery info...</Tab>
    </Tabs>
  );
}

// PATTERN 3: Presentational vs Container
// Presentational: only renders, no side effects
const RestaurantCard = memo(function RestaurantCard({
  name, rating, cuisine, deliveryTime, onSelect
}) {
  return (
    <div className="restaurant-card" onClick={onSelect}>
      <h3>{name}</h3>
      <span>⭐ {rating}</span>
      <span>{cuisine}</span>
      <span>🕐 {deliveryTime} min</span>
    </div>
  );
});

// Container: fetches data, passes to presentational
function RestaurantListContainer({ cityId }) {
  const [restaurants, setRestaurants] = useState([]);
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    fetch(`/api/restaurants?city=${cityId}`)
      .then(r => r.json())
      .then(setRestaurants);
  }, [cityId]);

  const handleSelect = useCallback((id) => {
    setSelected(id);
    // navigate to restaurant page...
  }, []);

  return (
    <div>
      {restaurants.map(r => (
        <RestaurantCard
          key={r.id}
          {...r}
          onSelect={() => handleSelect(r.id)}
        />
      ))}
    </div>
  );
}
```

---

## 🟠 Next.js Connection

```jsx
// React components = Client Components (run in browser)
// Next.js adds SERVER Components (run on server, no JS to client)

// ── SERVER COMPONENT (default in App Router) ──
// app/components/ProductList.jsx
// NO 'use client' → runs on server
async function ProductList() {
  const products = await db.query('SELECT * FROM products LIMIT 20');
  // HTML generated on server — fast initial load, great SEO
  return (
    <ul>
      {products.map(p => <li key={p.id}>{p.name}</li>)}
    </ul>
  );
}

// ── CLIENT COMPONENT ──────────────────────
// Add 'use client' when you need: hooks, events, browser APIs
'use client';
function AddToCartButton({ productId }) {
  const [added, setAdded] = useState(false);

  return (
    <button onClick={() => setAdded(true)}>
      {added ? 'Added ✓' : 'Add to Cart'}
    </button>
  );
}

// ── COMPOSING BOTH ────────────────────────
// Server Component can include Client Components:
async function ProductPage({ params }) {
  const product = await getProduct(params.id); // server

  return (
    <div>
      <h1>{product.name}</h1>      {/* server-rendered */}
      <p>₹{product.price}</p>     {/* server-rendered */}
      <AddToCartButton productId={product.id} />  {/* client component */}
    </div>
  );
}
// Result: static product info (SEO) + interactive button (client) ✅
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Lowercase component names
```jsx
// WRONG: React treats it as HTML element (renders nothing or wrong thing)
function productCard() { return <div>Product</div>; }
<productCard />   // ❌ React: "unknown HTML element"

// CORRECT: PascalCase
function ProductCard() { return <div>Product</div>; }
<ProductCard />   // ✅
```

❌ **Mistake 2:** Defining components inside other components
```jsx
// WRONG: new component created on every render → remounts every time!
function Parent() {
  function Child() {           // ❌ redefined on every Parent render
    return <div>Child</div>;
  }
  return <Child />;            // remounts every render → slow + bugs
}

// CORRECT: define at module level
function Child() {             // ✅ defined once
  return <div>Child</div>;
}
function Parent() {
  return <Child />;
}
```

❌ **Mistake 3:** Modifying props directly
```jsx
// WRONG: props are readonly — don't mutate them!
function Card({ style }) {
  style.color = 'red';   // ❌ mutating prop — causes bugs!
  return <div style={style}>Card</div>;
}

// CORRECT: spread and override
function Card({ style }) {
  return <div style={{ ...style, color: 'red' }}>Card</div>; // ✅
}
```

---

## 🧠 Tricky Interview Question

```jsx
function Counter() {
  const [count, setCount] = useState(0);
  console.log('Counter rendered');
  return <button onClick={() => setCount(count)}>Count: {count}</button>;
}
// If count = 5 and you click the button (setCount(5) — same value),
// does 'Counter rendered' log?
```
**Answer:** In React 18, **no** — React "bails out" of re-rendering when you call `setState` with the same value (compared with `Object.is`). Setting `count` to `5` when it's already `5` causes React to skip the re-render. However, in some cases React may still render once to check for changes before bailing out.

---

## ⚫ Interview Questions + Answers

**Q1: What is a React component?**
A1: A React component is a reusable, independent piece of UI — a JavaScript function that returns JSX. It encapsulates markup, logic, and styling. Components accept props (inputs) and can maintain internal state. React applications are entirely built by composing components into a tree.

**Q2: What is the difference between a component and an element?**
A2: A **React element** is a plain JS object describing what to render: `{ type: 'div', props: { className: 'card' } }`. It's the output of `React.createElement()` or JSX. A **component** is a function/class that produces elements when called. `<ProductCard />` (with capital P) is React calling the ProductCard function and getting an element tree back.

**Q3: Can a React component return multiple elements?**
A3: Yes — using Fragments. `return (<><h1>Title</h1><p>Text</p></>)` or `return React.Fragment`. Without a Fragment, you'd need a wrapper `<div>` which adds an unnecessary DOM node. Use `<Fragment key={...}>` (not `<>`) when each fragment needs a `key` prop in a list.

**Q4: What is the difference between a controlled and uncontrolled component?**
A4: **Controlled**: form element's value is driven by React state (`value={state}` + `onChange={setState}`). React is the single source of truth. Best for validation, conditional fields, form libraries. **Uncontrolled**: form element manages its own DOM state — accessed via `ref.current.value`. Simpler for basic forms, file inputs. React recommends controlled components for most cases.

**Q5: When should you split a component into smaller components?**
A5: Split when: (1) Component is doing too many things — hard to understand in one read. (2) Part of the component is reused elsewhere. (3) Part has independent state that doesn't affect the rest. (4) You can give the piece a clear, single name. Don't split just to split — premature abstraction is a cost. A good heuristic: if you need to name it, extract it; if the name is obvious, it probably deserves to be a component.

---

## 🔷 When to Use + When Not to Use
✅ **Create a component when:**
- UI piece is reused in multiple places
- Piece has its own state or logic
- Piece is complex enough to merit a name
- Different teams/developers own different parts

❌ **Don't create a component when:**
- It's only used once and adds no clarity
- The abstraction is a single line anyway
- You're "organizing" — consider custom hooks or variables instead

---

## 📊 Visual Diagram

```
COMPONENT TREE:
──────────────────────────────────────────────
  App
  ├── Header
  │   ├── Logo
  │   ├── SearchBar
  │   └── CartButton
  ├── Main
  │   ├── CategoryList
  │   │   └── CategoryItem (×5)
  │   └── ProductGrid
  │       └── ProductCard (×20)
  │           ├── ProductBadge
  │           ├── ProductImage
  │           └── AddToCartButton
  └── Footer

Each component:
  ┌──────────────────────────┐
  │  Props (inputs)          │
  │        ↓                 │
  │  [Component Logic]       │
  │  - State (optional)      │
  │  - Event handlers        │
  │  - Calculations          │
  │        ↓                 │
  │  JSX (output / "view")   │
  └──────────────────────────┘

COMPONENT = Function that:
  1. Takes props
  2. Manages state (optional)
  3. Returns JSX
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Component | Reusable UI building block | Reusable UI building block |
| Props | Inputs passed to component | Component को दिए जाने वाले inputs |
| State | Internal data that can change | Internal data जो बदल सकता है |
| Composition | Building UI by combining components | Components combine करके UI बनाना |
| PascalCase | ComponentName style | ComponentName style |
| Controlled | Form element driven by React state | React state से drive होने वाला form element |
| Uncontrolled | Form element manages own state | अपनी state manage करने वाला form element |

---

## ⚡ 3-Line Summary
**English:**
1. Components are functions that accept props and return JSX — the fundamental building block of all React UIs.
2. Component names MUST be PascalCase; React uses this to distinguish them from HTML elements.
3. Build UIs by composing components — small, focused, reusable pieces that each do one thing well.

**Hindi:**
1. Components functions हैं जो props accept करते हैं और JSX return करते हैं — सभी React UIs का fundamental building block।
2. Component names MUST PascalCase हों — React इससे उन्हें HTML elements से distinguish करता है।
3. Components compose करके UIs बनाओ — छोटे, focused, reusable pieces जो हर एक चीज़ अच्छे से करें।

---

## ➡️ Next Topic
**13. Functional vs Class Components** — दोनों के बीच difference, क्यों functional components ने class components को replace किया।
