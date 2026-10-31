# 89. Dynamic Routing
# हिंदी में: Dynamic Routing — URL के हिस्से से पेज तय करना

---

## 🔵 Simple Definition (English)
Dynamic routing means a route's URL has **placeholders** (like `:productId`) that change per request. One route definition serves thousands of pages — `/products/42`, `/products/43` — and the component reads the value with `useParams()`.

## 🔵 सरल परिभाषा (Hindi)
Dynamic routing का मतलब है कि route के URL में **placeholder** (जैसे `:productId`) होता है, जो हर request पर बदलता है। एक route definition हज़ारों pages चला सकती है — `/products/42`, `/products/43` — और component `useParams()` से value पढ़ता है।

---

## 🔴 Problem it Solves
Without dynamic routes you need one `<Route>` per product — `/products/1`, `/products/2`, and so on. That is impossible for a catalogue of 10 lakh Flipkart listings, and a product added tomorrow would need a code change and deploy. A dynamic segment lets one component render any record whose id is in the URL. The URL becomes the source of truth for "which item am I looking at?", which also makes pages shareable and bookmarkable.

## 🔴 यह क्यों बना? (Hindi)
Dynamic routes से पहले हर product के लिए अलग `<Route>` लिखना पड़ता था — `/products/1`, `/products/2` और आगे। Flipkart के 10 लाख listings के लिए यह असंभव है, और कल आए नए product के लिए भी code deploy करना पड़ता। Dynamic segment से एक ही component URL में दिए id का record दिखा सकता है। URL ही तय करता है कि "मैं कौन सा item देख रहा हूँ" — इससे pages shareable और bookmarkable बनते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define a route with a dynamic segment:
         <Route path="/products/:productId" element={<ProductPage />} />

Step 2 → User opens /products/42
         React Router matches the pattern and extracts productId = "42"

Step 3 → ProductPage calls useParams() → { productId: "42" }
         The value is ALWAYS a string

Step 4 → Use the id to look up data and render the matching product

Step 5 → <Link to="/products/43"> or navigate('/products/43') changes the URL
         Same component instance re-renders with the new param (no remount)

KEY: useParams values are strings. Use Number() before numeric comparison.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Route में dynamic segment लिखो: path="/products/:productId"
Step 2 → User /products/42 खोलता है, React Router productId = "42" निकालता है
Step 3 → ProductPage में useParams() → { productId: "42" } (हमेशा string)
Step 4 → इसी id से data लाओ और सही product दिखाओ
Step 5 → Link या navigate से URL बदलो → वही component नए param के साथ re-render होता है
KEY: useParams की values string होती हैं। Number तुलना से पहले Number() लगाओ।
```

---

## 🟡 Real World Example
**Zomato restaurant page:** The route `/restaurant/:restaurantId` serves every restaurant in India with one component. When you open `/restaurant/88412`, the page reads `restaurantId = "88412"`, fetches that restaurant's menu, and renders it. Tapping a "Similar restaurants" card just changes the URL to another id — the same route component updates. Sharing that link on WhatsApp opens the exact same restaurant for your friend.

## 🟡 Real Example Hindi mein
**Zomato restaurant page:** Route `/restaurant/:restaurantId` पूरे भारत के हर restaurant को एक ही component से दिखाता है। `/restaurant/88412` खोलने पर page `restaurantId = "88412"` पढ़ता है, उस restaurant का menu लाता है और दिखाता है। "Similar restaurants" card पर टैप करने से सिर्फ URL का id बदलता है — वही route component update हो जाता है। WhatsApp पर link भेजने से दोस्त को भी वही restaurant खुलता है।

---

## 💻 Code Example — Basic

```jsx
// Import the router building blocks from react-router-dom (v6 API)
import { BrowserRouter, Routes, Route, Link, useParams } from 'react-router-dom';

// Component that reads the dynamic part of the URL
function ProductPage() {
  // useParams() returns an object with every :segment of the matched URL
  const { productId } = useParams(); // "/products/42" gives "42"

  // productId is a STRING even though it looks like a number
  return <h2>Product #{productId}</h2>; // renders: Product #42
}

// Simple list page that links to three dynamic URLs
function ProductList() {
  // Return a list of links, one per product id
  return (
    <ul>
      {[1, 2, 3].map((id) => ( // loop over the ids 1, 2 and 3
        // key helps React track list items; to= builds /products/1, /products/2 ...
        <li key={id}>
          <Link to={`/products/${id}`}>Open product {id}</Link>
        </li>
      ))}
    </ul>
  );
}

// Root component: declares which URL shows which component
export default function App() {
  return (
    // BrowserRouter listens to the browser URL through the History API
    <BrowserRouter>
      {/* Routes renders the FIRST Route whose path matches the URL */}
      <Routes>
        {/* Static route: matches exactly "/" */}
        <Route path="/" element={<ProductList />} />
        {/* Dynamic route: ":productId" matches any single URL segment */}
        <Route path="/products/:productId" element={<ProductPage />} />
      </Routes>
    </BrowserRouter>
  );
}
```

## 💻 Code Example — Advanced

```jsx
// Data router API (v6.4+): createBrowserRouter + RouterProvider
import {
  createBrowserRouter, // builds the route tree from plain objects
  RouterProvider,      // renders whichever route matches the URL
  Outlet,              // slot where a child route's element is shown
  Navigate,            // declarative redirect component
  useParams,           // reads :segments from the current URL
  Link,                // client-side navigation link (no full reload)
} from 'react-router-dom';

// Fake data store; a real app would fetch this from an API
const RESTAURANTS = {
  7: { name: 'Biryani House', items: { 1: 'Chicken Biryani', 2: 'Paneer Tikka' } },
};

// Layout for one restaurant. Shared by the menu page and the item page.
function RestaurantLayout() {
  // Params from the PARENT route (restaurantId) are visible here
  const { restaurantId } = useParams();
  const restaurant = RESTAURANTS[restaurantId]; // object lookup by string key

  // Unknown id: redirect home. replace = no extra history entry (back button is safe)
  if (!restaurant) return <Navigate to="/" replace />;

  return (
    <section>
      <h1>{restaurant.name}</h1>
      {/* Outlet shows the matched child route (menu or item page) */}
      <Outlet />
    </section>
  );
}

// Menu page: shown at /restaurants/:restaurantId (index child route)
function MenuPage() {
  const { restaurantId } = useParams(); // parent param is merged in
  const items = RESTAURANTS[restaurantId].items; // safe: layout already checked it

  return (
    <ul>
      {Object.entries(items).map(([id, name]) => ( // [ "1", "Chicken Biryani" ] pairs
        <li key={id}>
          {/* Absolute path so the link works from any nested depth */}
          <Link to={`/restaurants/${restaurantId}/items/${id}`}>{name}</Link>
        </li>
      ))}
    </ul>
  );
}

// Item page: shown at /restaurants/:restaurantId/items/:itemId
function ItemPage() {
  const { restaurantId, itemId } = useParams(); // both params are available
  const name = RESTAURANTS[restaurantId]?.items[itemId]; // optional chaining = no crash

  // Item does not exist: send the user back to the menu
  if (!name) return <Navigate to={`/restaurants/${restaurantId}`} replace />;

  return <p>You ordered: {name}</p>;
}

// Route tree: nesting mirrors the URL structure
const router = createBrowserRouter([
  // Home page; plain element, no params
  { path: '/', element: <p>Open /restaurants/7 to see a restaurant</p> },
  {
    path: '/restaurants/:restaurantId', // dynamic parent segment
    element: <RestaurantLayout />,      // layout wraps all children
    errorElement: <p>Something went wrong</p>, // shown if a child throws
    children: [
      { index: true, element: <MenuPage /> },            // /restaurants/7
      { path: 'items/:itemId', element: <ItemPage /> },   // /restaurants/7/items/1
    ],
  },
]);

// App just hands the router to the provider
export default function App() {
  return <RouterProvider router={router} />;
}
```

---

## 🟠 Real App Integration (React + Next.js)

In a React Router app, the route tree above is the whole routing layer. In **Next.js App Router** the same idea is done with folders: a folder named `[restaurantId]` becomes a dynamic segment, and the page receives it as `params`. Next.js 15+ passes `params` as a Promise, so you `await` it.

```jsx
// app/restaurants/[restaurantId]/page.jsx  →  URL /restaurants/7
export default async function RestaurantPage({ params }) {
  // Next.js 15+: params is a Promise, so await it before reading the segment
  const { restaurantId } = await params;           // "7" (string)

  // Fetch data on the server for this id (no client-side loader needed)
  const res = await fetch(`https://api.example.com/restaurants/${restaurantId}`);
  const restaurant = await res.json();              // plain object from the API

  // Render the restaurant; this runs on the server, so no useParams hook
  return <h1>{restaurant.name}</h1>;
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Treating the param as a number
✅ **Correct:** `useParams` always returns strings. Convert when needed.

```jsx
// Wrong
const { productId } = useParams();
if (productId === 42) { /* never true: "42" !== 42 */ }

// Right
const { productId } = useParams();
if (Number(productId) === 42) { /* correct comparison */ }
```

❌ **Mistake 2:** Using `<a href>` for internal dynamic links
✅ **Correct:** Use `<Link>` so React Router handles navigation without a full page reload.

```jsx
// Wrong: full page reload, app state is lost
<a href={`/products/${id}`}>Product</a>

// Right: client-side navigation, state and component tree preserved
<Link to={`/products/${id}`}>Product</Link>
```

---

## 🧠 Tricky Interview Question

```jsx
import { renderToStaticMarkup } from 'react-dom/server';
import { MemoryRouter, Routes, Route, useParams } from 'react-router-dom';

function Show() {
  const { id } = useParams();          // read the dynamic segment
  return <p>id={id} type={typeof id}</p>;
}

// Render the route tree for the URL /items/007 (no browser needed)
const html = renderToStaticMarkup(
  <MemoryRouter initialEntries={['/items/007']}>
    <Routes>
      <Route path="/items/:id" element={<Show />} />
    </Routes>
  </MemoryRouter>
);
console.log(html);
```

**Answer:** The output is `<p>id=007 type=string</p>`. `useParams` returns the raw text from the URL, so `"007"` keeps its leading zeros and stays a string. A common wrong answer is `id=7`, which assumes the router converts numeric-looking text. It does not. If you need a number, call `Number(id)` yourself, which gives `7` and loses the zeros only at that point of conversion.

---

## ⚫ Interview Questions + Answers

**Q1: What is a dynamic segment in React Router?**
A1: A part of the path that starts with a colon, like `:productId`. It matches any single URL segment, and the matched value is exposed through `useParams()`.

**Q2: How do you read a dynamic param inside a component?**
A2: Call `useParams()` from `react-router-dom`. It returns an object whose keys are the segment names. For `/products/:productId`, it returns `{ productId: '...' }`.

**Q3: Are route params always strings?**
A3: Yes. The router never converts them. Convert with `Number()` or `parseInt()` when you need a number.

**Q4: How do nested routes share a param from the parent route?**
A4: Child routes inherit parent params. A child component can call `useParams()` and get the parent's `:restaurantId` along with its own `:itemId`. The parent renders `<Outlet />` where the child appears.

**Q5: Why use `<Navigate replace />` for a missing record?**
A5: `replace` swaps the current history entry instead of adding a new one, so the browser back button does not return the user to the broken URL and loop.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- Many records share one page layout (products, users, orders, restaurants)
- The URL should identify the record so it can be shared or bookmarked
- You want the back and forward buttons to work between records

❌ **Avoid when:**
- The value should not be visible in the URL (tokens, passwords, form drafts)
- Only one fixed page exists — a plain `<Route path="/about">` is simpler
- The value is UI-only state (selected tab, modal open) — keep it in component state

---

## 📊 Visual Diagram

```
URL                                   Route matched              useParams()
──────────────────────────────────    ──────────────────────     ──────────────────────
/                                 →   "/"                    →  {}
/products/42                      →   "/products/:productId"  →  { productId: "42" }
/products/43                      →   "/products/:productId"  →  { productId: "43" }
/products/42/reviews              →   no match (no route)     →  fallback / 404

NESTED:
/restaurants/7/items/1
   │
   ▼
<RestaurantLayout>      params: { restaurantId: "7" }
   └── <Outlet />
        └── <ItemPage>  params: { restaurantId: "7", itemId: "1" }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Dynamic segment | URL part starting with `:` that matches any value | `:` से शुरू होने वाला URL हिस्सा |
| useParams | Hook that returns the dynamic params as an object | Params object लौटाने वाला hook |
| Link | Client-side navigation component | Page reload बिना navigation करने वाला component |
| Outlet | Placeholder where a child route renders | Child route दिखाने की जगह |
| Navigate | Component that redirects declaratively | Declarative redirect करने वाला component |
| Index route | Child route that renders at the parent's exact path | Parent के exact path पर दिखने वाला child route |

---

## ⚡ 3-Line Summary
**English:**
1. Dynamic routes use `:placeholders` so one route serves many records, like `/products/:productId`.
2. `useParams()` gives the values as strings, so convert numbers yourself.
3. Nested routes share parent params and render children through `<Outlet />`.

**Hindi:**
1. Dynamic routes `:placeholder` से एक route से कई records दिखाते हैं, जैसे `/products/:productId`।
2. `useParams()` values string में देता है, इसलिए numbers को खुद convert करो।
3. Nested routes parent params share करते हैं और children को `<Outlet />` से दिखाते हैं।

---

## ➡️ Next Topic
**90. Lazy Loading Routes** — Route components को on-demand load करना, ताकि शुरुआती JavaScript bundle छोटा रहे। Dynamic routing के बाद यह सीखना स्वाभाविक है, क्योंकि हर dynamic page का code भी अलग से load हो सकता है।
