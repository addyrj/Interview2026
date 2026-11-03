# 18. defaultProps
# हिंदी में: defaultProps — Props की Default Values

---

## 🔵 Simple Definition (English)
**`defaultProps`** is a static property that gives a component fallback values for props the parent did not pass. It only applies when the prop is `undefined`. In modern React, **default parameters** in destructuring (`function Button({ size = 'md' })`) do the same job, and React 19 removed `defaultProps` for function components.

## 🔵 सरल परिभाषा (Hindi)
**`defaultProps`** एक static property है जो उन props के लिए fallback values देती है जो parent ने नहीं भेजे। यह सिर्फ तब लागू होती है जब prop `undefined` हो। आधुनिक React में destructuring के **default parameters** (`function Button({ size = 'md' })`) यही काम करते हैं, और React 19 ने function components के लिए `defaultProps` हटा दिया है।

---

## 🔴 Problem it Solves

Many props are optional. Without defaults, every use must pass them, or the component needs `if (!size) size = 'md'` lines scattered in the body. Missing props become `undefined`, leading to broken output such as a button with `class="btn-undefined"` or a crash on `items.map`. Defaults give each component a safe baseline, so `<Button>Order</Button>` works with no extra props.

```jsx
// PROBLEM: forgetting a prop breaks the UI
function Button({ variant, children }) {
  return <button className={`btn btn-${variant}`}>{children}</button>;
}
<Button>Order</Button>      // renders class="btn btn-undefined"

// SOLUTION: provide a default
function Button2({ variant = 'primary', children }) {
  return <button className={`btn btn-${variant}`}>{children}</button>;
}
<Button2>Order</Button2>    // class="btn btn-primary"
```

## 🔴 यह क्यों बना? (Hindi)
कई props optional होते हैं। Defaults के बिना हर बार उन्हें भेजना पड़ता है, या component के अंदर जगह-जगह `if (!size) size = 'md'` जैसी lines लिखनी पड़ती हैं। Missing props `undefined` बन जाते हैं, जिससे `class="btn-undefined"` वाला बटन या `items.map` पर crash जैसी दिक्कतें आती हैं। Defaults हर component को सुरक्षित baseline देते हैं, ताकि `<Button>Order</Button>` बिना extra props के काम करे।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Parent renders <Button>Order</Button>     (no variant passed)
Step 2 → React builds the props object:            { children: 'Order' }
Step 3 → OLD WAY (class or function): React reads Button.defaultProps and fills missing keys
Step 4 → MODERN WAY: JavaScript default parameter fills it:  { variant = 'primary' }
Step 5 → Default applies ONLY when value === undefined
           undefined → default used
           null      → NO default (null is a real value)
           0, '', false → NO default
Step 6 → Component renders with variant = 'primary'

VERSION NOTE: React 18.3 warns about defaultProps on function components.
              React 19 ignores them for function components (class components still support them).
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Parent <Button>Order</Button> render करता है     (variant नहीं भेजा)
Step 2 → React props object बनाता है:                      { children: 'Order' }
Step 3 → पुराना तरीका (class या function): React Button.defaultProps पढ़कर missing keys भरता है
Step 4 → आधुनिक तरीका: JavaScript का default parameter भरता है:  { variant = 'primary' }
Step 5 → Default सिर्फ तब लागू होता है जब value === undefined
           undefined → default इस्तेमाल होगा
           null      → default नहीं (null असली value है)
           0, '', false → default नहीं
Step 6 → Component variant = 'primary' के साथ render होता है

Version नोट: React 18.3 function components पर defaultProps के लिए warning देता है।
              React 19 function components के लिए उन्हें ignore करता है (class components में अब भी चलता है)।
```

---

## 🟡 Real World Example
**Zomato restaurant list:** `RestaurantList` receives `restaurants` from search, plus optional `pageSize`, `showRatings` and `emptyMessage`. The home page passes only `restaurants`. The component defaults `pageSize = 10`, `showRatings = true` and `emptyMessage = 'No restaurants found'`. The "Favorites" screen overrides only `emptyMessage = 'No favorites yet'`. One component, many screens, minimal props.

## 🟡 Real Example Hindi mein
**Zomato restaurant list:** `RestaurantList` को search से `restaurants` मिलता है, और optional `pageSize`, `showRatings` व `emptyMessage` भी। Home page सिर्फ `restaurants` भेजता है। Component में `pageSize = 10`, `showRatings = true` और `emptyMessage = 'No restaurants found'` default हैं। "Favorites" screen सिर्फ `emptyMessage = 'No favorites yet'` बदलती है। एक component, कई screens, कम से कम props।

---

## 💻 Code Example — Basic

```jsx
// Old style (defaultProps) versus modern style (default parameters)
import PropTypes from 'prop-types';

// ---------- OLD: works in React ≤ 18 (warns in 18.3, ignored for functions in 19) ----------
function OldButton({ variant, size, children }) {
  return <button className={`btn btn-${variant} btn-${size}`}>{children}</button>;
}
OldButton.defaultProps = {          // static property with fallback values
  variant: 'primary',
  size: 'md',
};
OldButton.propTypes = { variant: PropTypes.string, size: PropTypes.string, children: PropTypes.node };

// ---------- MODERN: default parameters (works in every React version) ----------
function Button({ variant = 'primary', size = 'md', children }) { // defaults sit next to the props
  return (
    <button className={`btn btn-${variant} btn-${size}`}>        {/* uses the default if not passed */}
      {children}
    </button>
  );
}

export default function App() {
  return (
    <>
      <Button>Order now</Button>                          {/* primary + md */}
      <Button variant="danger">Cancel</Button>            {/* danger + md */}
      <Button size="lg" variant={undefined}>Big</Button>  {/* undefined → default 'primary' */}
      <Button variant={null}>Null</Button>                {/* null → class "btn-null" (no default!) */}
    </>
  );
}
```

## 💻 Code Example — Advanced

```jsx
// Real world: defaults for primitives, objects, arrays and callbacks, plus merged config
import { useMemo } from 'react';

// Defaults declared OUTSIDE the component: same reference on every render (no extra re-renders)
const EMPTY_LIST = [];                                  // shared constant instead of `= []` in params
const DEFAULT_FILTERS = { veg: false, maxPrice: 1000 }; // default object, created once
const noop = () => {};                                  // safe default callback

function RestaurantList({
  restaurants = EMPTY_LIST,                // array default: .map never crashes
  pageSize = 10,                           // number default
  showRatings = true,                      // boolean default (note: false is respected)
  emptyMessage = 'No restaurants found',   // string default
  filters,                                 // object: merged below
  onSelect = noop,                         // function default
}) {
  // Merge a partial filters prop over the defaults: { veg: true } keeps maxPrice 1000
  const f = useMemo(() => ({ ...DEFAULT_FILTERS, ...filters }), [filters]);

  const visible = useMemo(
    () => restaurants
      .filter((r) => (f.veg ? r.veg : true) && r.avgPrice <= f.maxPrice) // apply filters
      .slice(0, pageSize),                                               // apply page size
    [restaurants, f, pageSize]
  );

  if (visible.length === 0) return <p>{emptyMessage}</p>;   // default message shown

  return (
    <ul>
      {visible.map((r) => (
        <li key={r.id} onClick={() => onSelect(r.id)}>
          {r.name} {showRatings && <span>{r.rating}★</span>}
        </li>
      ))}
    </ul>
  );
}

export default RestaurantList;

// <RestaurantList />                                     → "No restaurants found"
// <RestaurantList restaurants={data} filters={{ veg: true }} />   → veg only, price ≤ 1000
```

---

## 🟠 Real App Integration

In Next.js, defaults matter a lot for **pages**, because `searchParams` are optional strings (and a Promise in Next.js 15). Use default values when you read them, and note that a default prop or parameter is not a substitute for validating user input.

```jsx
// app/restaurants/page.jsx — Server Component (Next.js 15)
export default async function Page({ searchParams }) {
  const sp = await searchParams;               // Next.js 15: searchParams is a Promise
  const page = Number(sp.page ?? 1);           // default page 1 when ?page= is missing
  const veg = sp.veg === 'true';               // default false
  const sort = sp.sort ?? 'rating';            // default sort order

  const res = await fetch(
    `https://api.example.com/restaurants?page=${page}&veg=${veg}&sort=${sort}`,
    { cache: 'no-store' }                      // always fresh for filtered results
  );
  const restaurants = await res.json();
  return <p>{restaurants.length} results (page {page}, sort {sort})</p>;
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using `defaultProps` on function components in React 19
✅ **Correct:** Use default parameters

```jsx
// Wrong: ignored in React 19, warns in 18.3
function Badge({ color }) { return <span style={{ color }}>New</span>; }
Badge.defaultProps = { color: 'red' };        // ❌

// Right
function Badge2({ color = 'red' }) { return <span style={{ color }}>New</span>; } // ✅
```

❌ **Mistake 2:** Expecting a default to apply for `null`, `0`, `''` or `false`
✅ **Correct:** Defaults apply only to `undefined`; use `??` for `null`

```jsx
// Wrong: null stays null
function Price({ amount = 100 }) { return <p>{amount}</p>; }
<Price amount={null} />                        // ❌ renders nothing (null), not 100

// Right: also handle null
function Price2({ amount }) {
  const value = amount ?? 100;                 // ✅ null or undefined → 100 (0 stays 0)
  return <p>{value}</p>;
}
```

❌ **Mistake 3:** Creating a new object or array default inline (new reference on every render)
✅ **Correct:** Use a module-level constant, especially when the prop feeds `memo`, `useEffect` or `useMemo`

```jsx
// Wrong: a new [] each render → effect re-runs every time
function List({ items = [] }) {                // ❌ new array on every render when items is missing
  useEffect(() => { fetchStats(items); }, [items]);
  return null;
}

// Right
const NO_ITEMS = [];
function List2({ items = NO_ITEMS }) {         // ✅ same reference every render
  useEffect(() => { fetchStats(items); }, [items]);
  return null;
}
```

---

## 🧠 Tricky Interview Question

```jsx
function Counter({ start = 0, step = 1 }) {
  console.log('start =', start, 'step =', step);
  return null;
}

<Counter start={undefined} step={null} />;
<Counter start={0} step="" />;
```
Question: What is logged for each line?

**Answer:**
```
start = 0 step = null
start = 0 step =
```
In the first call `start` is `undefined`, so the default `0` is used, but `step` is `null`, and `null` is a real value, so no default is applied. In the second call `start` is the explicit `0`, and `step` is an empty string (printed as nothing). Defaults only replace `undefined`. This is a favorite question because many developers expect "falsy means default".

---

## ⚫ Interview Questions + Answers

Q1: What is `defaultProps`?
A1: A static property of a component (`Button.defaultProps = { size: 'md' }`) listing fallback values for props that are `undefined`. It was widely used for classes and functions before React 19.

Q2: What changed in React 19?
A2: `defaultProps` was removed for function components (class components still support it). React 18.3 prints deprecation warnings to help you migrate. Use ES6 default parameters instead.

Q3: Does a default value apply for `null`?
A3: No. Both `defaultProps` and default parameters apply only when the value is `undefined`. `null`, `0`, `''` and `false` are kept as given. Use `??` for null-or-undefined fallback.

Q4: What is the difference between `defaultProps` and default parameters in terms of performance?
A4: Both are cheap. The important detail is reference stability: an inline `= []` or `= {}` default creates a new object each render, which can break `memo` and effect dependencies. Use constants outside the component. (`defaultProps` objects were stable by nature.)

Q5: How do default values relate to optional props in TypeScript?
A5: In TypeScript, mark the prop optional (`size?: 'sm' | 'md'`) and assign the default in destructuring (`size = 'md'`). Inside the component TypeScript knows `size` is defined.

---

## 🔷 When to Use + When Not to Use
✅ **Use default parameters when:**
- A prop is optional and has a sensible baseline (variant, size, pageSize)
- You want safe empty values (`[]`, `{}`, `noop`) so the code never crashes on missing data
- You build a reusable UI component with a simple API

❌ **Avoid / be careful when:**
- You use `defaultProps` on function components in React 19 (it is ignored)
- A default hides a required piece of data (better to make the prop required and fail loudly)
- You write inline object or array defaults that go into `memo` or effect dependencies

---

## 📊 Visual Diagram

```
  <Button>Order</Button>                  <Button variant="danger">Cancel</Button>
        │                                          │
        ▼ props = { children }                     ▼ props = { variant:'danger', children }
  ┌──────────────────────────────┐          ┌──────────────────────────────┐
  │ function Button({            │          │ function Button({            │
  │   variant = 'primary',  ◀────┼ used     │   variant = 'primary',  ✖    │ NOT used
  │   size    = 'md'        ◀────┼ used     │   size    = 'md'        ◀────┼ used
  │ })                           │          │ })                           │
  └──────────────────────────────┘          └──────────────────────────────┘

  Rule:  value === undefined  →  default used
         null / 0 / '' / false →  kept as is

  Timeline:  React ≤ 18: defaultProps OK │ 18.3: warning │ 19: function defaultProps ignored
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `defaultProps` | Static object of fallback prop values | Fallback values का static object |
| Default parameter | JS syntax `{ size = 'md' }` | JS का `{ size = 'md' }` syntax |
| `undefined` | The only value that triggers a default | केवल यही value default चलाती है |
| Nullish coalescing `??` | Fallback for `null` or `undefined` | `null` या `undefined` के लिए fallback |
| Optional prop | Prop the parent may skip | जिसे parent छोड़ सकता है |
| Reference stability | Same object between renders | दो renders में वही object |
| Deprecated | Still works but scheduled for removal | अभी चलता है पर हटाया जाना है |
| Noop | Empty safe function `() => {}` | खाली सुरक्षित function |

---

## ⚡ 3-Line Summary
**English:**
1. `defaultProps` supplied fallback values for missing props, but it is removed for function components in React 19.
2. Use default parameters (`{ size = 'md' }`); they apply only to `undefined`, not to `null`, `0`, `''` or `false`.
3. Define array/object/function defaults outside the component to keep references stable.

**Hindi:**
1. `defaultProps` missing props के लिए fallback values देता था, लेकिन React 19 में function components के लिए हटा दिया गया है।
2. Default parameters (`{ size = 'md' }`) इस्तेमाल करो; ये सिर्फ `undefined` पर लगते हैं, `null`, `0`, `''` या `false` पर नहीं।
3. Array/object/function defaults को component के बाहर रखो ताकि reference स्थिर रहे।

---

## ➡️ Next Topic
**19. State — Basics** — Props की default values देख लीं, अब देखो कि component की अपनी बदलने वाली data (state) क्या होती है और props से कैसे अलग है.
