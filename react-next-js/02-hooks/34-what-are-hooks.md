# 34. What are Hooks + Rules of Hooks
# हिंदी में: Hooks क्या हैं + Rules of Hooks — पूरी समझ

---

## 🔵 Simple Definition (English)
**Hooks** are special functions in React (starting with `use`) that let **functional components** use React features like state, lifecycle, context, and refs — features that were previously only available in class components. Introduced in React 16.8.

## 🔵 सरल परिभाषा (Hindi)
**Hooks** React में special functions हैं (जो `use` से शुरू होते हैं) जो **functional components** को React features use करने देते हैं — जैसे state, lifecycle, context, refs — जो पहले सिर्फ class components में available थे। React 16.8 में introduce हुए।

---

## 🔴 Problem it Solves
Before Hooks (React < 16.8):
- State and lifecycle → only in class components
- Logic reuse between components was hard (HOCs, render props = confusing)
- Class components = verbose, confusing `this`, complicated lifecycle methods
- Sharing stateful logic meant wrapping component trees (wrapper hell)

## 🔴 यह क्यों बना? (Hindi)
Hooks से पहले (React < 16.8):
- State और lifecycle → सिर्फ class components में
- Components के बीच logic reuse करना मुश्किल था
- Class components verbose, confusing `this`, complicated lifecycle
- Stateful logic share करने के लिए component tree wrap करना पड़ता था

---

## 🟢 How it Works — Step by Step

```
Step 1 → You write a functional component (just a function!)

Step 2 → Call Hooks at the TOP of the function
         const [count, setCount] = useState(0);
         const name = useContext(ThemeContext);

Step 3 → React internally maintains a "hooks list" for each component
         Hooks are identified by their CALL ORDER (not by name)

Step 4 → On re-render, React matches each hook call to its stored value
         by position — this is why ORDER MATTERS (no conditionals!)

Step 5 → Hook returns current value + setter/methods
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → आप functional component लिखते हो (सिर्फ एक function!)

Step 2 → Function के TOP पर Hooks call करते हो
         const [count, setCount] = useState(0);

Step 3 → React internally हर component के लिए "hooks list" maintain करता है
         Hooks उनके CALL ORDER से identify होते हैं (name से नहीं)

Step 4 → Re-render पर React हर hook call को position से stored value से match करता है
         इसीलिए ORDER MATTERS — conditionals में call नहीं करते!

Step 5 → Hook current value + setter/methods return करता है
```

---

## 🟡 Real World Example
**Amazon Product Page:** A single product page uses 5+ hooks — `useState` for cart/wishlist state, `useEffect` for fetching similar products, `useContext` for user auth, `useRef` for image zoom container, `useMemo` for price calculations. Before hooks, you'd need a complex class component with lifecycle methods OR multiple HOCs wrapped around each other.

## 🟡 Real Example Hindi mein
**Amazon Product Page:** एक product page में 5+ hooks — `useState` cart/wishlist के लिए, `useEffect` similar products fetch के लिए, `useContext` user auth के लिए, `useRef` image zoom के लिए, `useMemo` price calculations के लिए। Hooks से पहले class component या HOCs की wrapping करनी पड़ती।

---

## 💻 Code Example — Basic

```jsx
import { useState, useEffect, useRef } from 'react';

// ── HOOKS IN ACTION ───────────────────────
function ProductPage({ productId }) {
  // Hook 1: useState — local state
  const [product, setProduct] = useState(null);
  const [isWishlisted, setIsWishlisted] = useState(false);
  const [quantity, setQuantity] = useState(1);

  // Hook 2: useEffect — side effect (data fetch)
  useEffect(() => {
    fetch(`/api/products/${productId}`)
      .then(r => r.json())
      .then(setProduct);
  }, [productId]);

  // Hook 3: useRef — DOM reference
  const imageRef = useRef(null);

  const zoomImage = () => {
    if (imageRef.current) {
      imageRef.current.style.transform = 'scale(1.5)';
    }
  };

  if (!product) return <div>Loading...</div>;

  return (
    <div>
      <img ref={imageRef} src={product.image} onClick={zoomImage} />
      <h1>{product.name}</h1>
      <p>₹{product.price * quantity}</p>

      <input
        type="number"
        value={quantity}
        onChange={e => setQuantity(Number(e.target.value))}
        min="1"
      />

      <button onClick={() => setIsWishlisted(w => !w)}>
        {isWishlisted ? '❤️ Wishlisted' : '🤍 Add to Wishlist'}
      </button>
    </div>
  );
}

// BEFORE HOOKS — same thing as a class component (verbose!):
class ProductPageOLD extends React.Component {
  state = { product: null, isWishlisted: false, quantity: 1 };
  imageRef = React.createRef();

  componentDidMount() {
    fetch(`/api/products/${this.props.productId}`)
      .then(r => r.json())
      .then(product => this.setState({ product }));
  }

  componentDidUpdate(prevProps) {
    if (prevProps.productId !== this.props.productId) {
      // must repeat the fetch logic here too!
    }
  }

  render() { /* ... */ }
}
// Same logic, way more code!
```

## 💻 Code Example — Advanced

```jsx
// ── RULES OF HOOKS — WHY THEY EXIST ─────
// React tracks hooks by CALL ORDER, not by name
// Internal representation (simplified):

// Component renders → React builds hooks array:
// [
//   hook[0] = useState(0)    → { state: 0, setState: fn }
//   hook[1] = useState('')   → { state: '', setState: fn }
//   hook[2] = useEffect(fn)  → { effect: fn, deps: [...] }
//   hook[3] = useRef(null)   → { current: null }
// ]
// On next render, each hook is matched by POSITION 0,1,2,3

// RULE 1: Only call Hooks at the TOP LEVEL
// ❌ WRONG — conditional hook changes call order!
function BadComponent({ showUser }) {
  const [count, setCount] = useState(0);

  if (showUser) {
    const user = useContext(UserContext); // ← position changes!
    // First render (showUser=true):  hooks = [useState, useContext]
    // Next render (showUser=false): hooks = [useState]
    // React: "hook[1] was useContext, now nothing — MISMATCH!" → error!
  }

  return <div>{count}</div>;
}

// ✅ CORRECT — always call, use value conditionally
function GoodComponent({ showUser }) {
  const [count, setCount] = useState(0);
  const user = useContext(UserContext); // always called

  return (
    <div>
      {count}
      {showUser && <span>{user.name}</span>} {/* use conditionally */}
    </div>
  );
}

// RULE 2: Only call Hooks from React functions
// ❌ WRONG — hook in regular function
function regularFunction() {
  const [x] = useState(0); // ❌ not a component or custom hook
}

// ✅ CORRECT — hook in component or custom hook
function MyComponent() {
  const [x] = useState(0); // ✅ React component
}

function useMyHook() {
  const [x] = useState(0); // ✅ custom hook (starts with 'use')
  return x;
}

// ── CUSTOM HOOK — REUSING STATEFUL LOGIC ─
// The REAL power of hooks — extract and share logic!
function useWindowSize() {
  const [size, setSize] = useState({
    width: window.innerWidth,
    height: window.innerHeight,
  });

  useEffect(() => {
    const handleResize = () => setSize({
      width: window.innerWidth,
      height: window.innerHeight,
    });
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return size;
}

// Use it in ANY component — no HOC, no wrapper hell!
function ResponsiveHeader() {
  const { width } = useWindowSize(); // reusing logic!
  return <header>{width > 768 ? 'Full Nav' : 'Hamburger'}</header>;
}

function ResponsiveSidebar() {
  const { width } = useWindowSize(); // same logic, different component!
  return width > 768 ? <aside>Sidebar</aside> : null;
}
```

---

## 🟠 Next.js Connection

```jsx
// Hooks work in Next.js Client Components only!
// Server Components can't use hooks (they run on server, no React state)

// ❌ Server Component (no hooks allowed):
// app/page.jsx — no 'use client'
async function ServerPage() {
  // Can't use useState, useEffect here
  const data = await fetchData(); // async/await instead
  return <div>{data.name}</div>;
}

// ✅ Client Component (hooks work normally):
'use client';
// app/components/SearchBar.jsx
import { useState, useEffect } from 'react';

function SearchBar() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);

  useEffect(() => {
    // Hooks work here — it's a client component
    if (query) fetchSearch(query).then(setResults);
  }, [query]);

  return (
    <input value={query} onChange={e => setQuery(e.target.value)} />
  );
}

// BEST PRACTICE: Server Component wraps Client Component
// Server fetches initial data → passes as props → Client adds interactivity
async function ProductsPage() {
  const initialProducts = await fetchProducts(); // server

  return (
    <div>
      <h1>Products</h1>
      <ProductFilter initialData={initialProducts} /> {/* client */}
    </div>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Calling hooks conditionally
```jsx
// WRONG:
function App({ isLoggedIn }) {
  if (!isLoggedIn) return <Login />; // early return before hook!
  const [data, setData] = useState(null); // ❌ sometimes hook[0], sometimes doesn't exist
}

// CORRECT: hooks before any early returns
function App({ isLoggedIn }) {
  const [data, setData] = useState(null); // ✅ always at top
  if (!isLoggedIn) return <Login />;
  return <Dashboard data={data} />;
}
```

❌ **Mistake 2:** Calling hooks inside loops
```jsx
// WRONG:
function List({ items }) {
  return items.map(item => {
    const [liked, setLiked] = useState(false); // ❌ hook in loop
    return <div onClick={() => setLiked(l => !l)}>{item.name}</div>;
  });
}

// CORRECT: extract to component
function ListItem({ item }) {
  const [liked, setLiked] = useState(false); // ✅ one hook per component
  return <div onClick={() => setLiked(l => !l)}>{item.name}</div>;
}

function List({ items }) {
  return items.map(item => <ListItem key={item.id} item={item} />);
}
```

---

## 🧠 Tricky Interview Question

```jsx
function useData(id) {
  const [data, setData] = useState(null);

  if (!id) {
    return null; // early return in custom hook — is this okay?
  }

  useEffect(() => {
    fetchData(id).then(setData);
  }, [id]);

  return data;
}
```
**Answer:** This violates Rules of Hooks. The `useEffect` is called conditionally (only when `id` is truthy). On first render `id` might be undefined (useState = hook[0]), then on re-render with `id` it tries to call useEffect as hook[1] — but previous render didn't have it. React will throw: "Rendered more hooks than previous render." Fix: move early return AFTER all hook calls.

---

## ⚫ Interview Questions + Answers

**Q1: What are React Hooks and why were they introduced?**
A1: Hooks are functions starting with `use` that let functional components access React features (state, lifecycle, context, refs). They were introduced in React 16.8 to solve three problems: (1) Stateful logic between components was hard to share (needed HOCs or render props). (2) Complex class components with confusing `this` and split lifecycle logic. (3) Classes didn't minify well and confused both humans and compilers.

**Q2: What are the Rules of Hooks?**
A2: Two rules: (1) Only call hooks at the TOP LEVEL — never inside loops, conditions, or nested functions. This ensures hooks are called in the same order every render (React tracks them by position). (2) Only call hooks from React functions — functional components or custom hooks (not regular JS functions, class methods, or event handlers).

**Q3: Why can't you call hooks conditionally?**
A3: React identifies each hook by its call order (position) in the component. If you skip a hook call based on a condition, the positions of all subsequent hooks shift. React then mismatches stored values to the wrong hooks — you get state from the wrong hook, causing subtle, hard-to-debug bugs. The ESLint `exhaustive-deps` rule and `react-hooks/rules-of-hooks` catch this.

**Q4: What is a custom hook and when should you create one?**
A4: A custom hook is a function starting with `use` that calls other hooks to extract and reuse stateful logic. Create one when the same stateful behavior appears in multiple components (data fetching, subscriptions, form state, window size). Custom hooks don't share state — each component gets its own isolated state from the hook.

**Q5: What built-in hooks does React provide?**
A5: Basic: `useState`, `useEffect`, `useContext`. Additional: `useReducer`, `useCallback`, `useMemo`, `useRef`, `useImperativeHandle`, `useLayoutEffect`, `useDebugValue`. React 18: `useId`, `useTransition`, `useDeferredValue`, `useSyncExternalStore`, `useInsertionEffect`. React 19: `useActionState`, `useOptimistic`, `use`.

---

## 🔷 When to Use + When Not to Use
✅ **Use Hooks when:**
- Any functional component that needs state or lifecycle
- Sharing stateful logic between components (custom hook)
- Accessing context, refs, or other React features

❌ **Don't use Hooks in:**
- Class components (use class lifecycle methods instead)
- Regular JavaScript functions (not components)
- Next.js Server Components (no client-side state needed)

---

## 📊 Visual Diagram

```
HOOKS = REACT FEATURES IN FUNCTIONS
─────────────────────────────────────────
  CLASS COMPONENT (old):
  ┌─────────────────────────────┐
  │ class MyComp extends React  │
  │   state = {...}             │
  │   componentDidMount() {...} │
  │   componentDidUpdate() {...}│
  │   render() { return JSX }   │
  └─────────────────────────────┘

  FUNCTIONAL COMPONENT + HOOKS (new):
  ┌─────────────────────────────┐
  │ function MyComp() {         │
  │   useState()    ← state     │
  │   useEffect()   ← lifecycle │
  │   useContext()  ← context   │
  │   return JSX                │
  │ }                           │
  └─────────────────────────────┘

HOOKS CALL ORDER (React tracks by position):
─────────────────────────────────────────
  Render 1:                Render 2:
  hook[0] = useState(0)    hook[0] = useState   ← same ✅
  hook[1] = useState('')   hook[1] = useState   ← same ✅
  hook[2] = useEffect(fn)  hook[2] = useEffect  ← same ✅

  WITH CONDITIONAL:
  Render 1 (x=true):       Render 2 (x=false):
  hook[0] = useState        hook[0] = useState   ← OK
  hook[1] = useState ←IF    → SKIPPED!           ← MISMATCH ❌
  hook[2] = useEffect       hook[1] = useEffect  ← wrong position!
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Hook | Function starting with `use` | `use` से शुरू होने वाला function |
| Rules of Hooks | 2 constraints for using hooks | Hooks use करने के 2 नियम |
| Call order | Sequence hooks are called | Hooks call होने का sequence |
| Custom Hook | Reusable stateful logic | Reusable stateful logic |
| HOC | Higher Order Component (old pattern) | पुराना reuse pattern |
| Lifecycle | Component birth/update/death | Component का जन्म/update/मृत्यु |

---

## ⚡ 3-Line Summary
**English:**
1. Hooks are `use*` functions that give functional components access to state, lifecycle, context, refs — all React features.
2. Rules: call only at top level (never in conditions/loops), only from React functions (components or custom hooks).
3. Custom hooks extract shared stateful logic — the real power of hooks over HOCs/render props.

**Hindi:**
1. Hooks `use*` functions हैं जो functional components को state, lifecycle, context, refs — सभी React features देते हैं।
2. Rules: सिर्फ top level पर call करो (conditions/loops में नहीं), सिर्फ React functions से (components या custom hooks)।
3. Custom hooks shared stateful logic extract करते हैं — HOCs/render props से Hooks का असली फायदा।

---

## ➡️ Next Topic
**35. useState — Deep Dive** — useState के सभी patterns — functional updates, lazy init, और batching।

---

## 📚 Go Deeper — External Resources

| Type | Link | What you'll learn |
|------|------|-------------------|
| 📺 YouTube | [Akshay Saini — React Hooks](https://www.youtube.com/results?search_query=react+hooks+akshay+saini+namaste+react) | Hooks explained in Hindi |
| 📺 YouTube | [Web Dev Simplified — React Hooks](https://www.youtube.com/results?search_query=react+hooks+all+web+dev+simplified) | All hooks explained |
| 📝 Article | [react.dev — Hooks Reference](https://react.dev/reference/react) | Official hooks reference |
| 📝 Article | [react.dev — Rules of Hooks](https://react.dev/reference/rules/rules-of-hooks) | Official rules with examples |
