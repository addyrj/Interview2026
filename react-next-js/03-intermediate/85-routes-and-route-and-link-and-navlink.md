# 85. Routes + Route + Link + NavLink
# हिंदी में: Routes, Route, Link और NavLink — Route matching और navigation links

---

## 🔵 Simple Definition (English)
`<Routes>` ek container hai jo current URL ke liye sabse achha matching `<Route>` chunta hai. `<Route>` ek URL pattern aur uska element batata hai. `<Link>` URL badalne wala link hai, aur `<NavLink>` ek special link hai jo active page ko khud pehchanta hai, taaki hum uska style badal sakein.

## 🔵 सरल परिभाषा (Hindi)
`<Routes>` एक container है जो current URL के लिए सबसे अच्छा matching `<Route>` चुनता है। `<Route>` एक URL pattern और उसका element बताता है। `<Link>` URL बदलने वाला link है, और `<NavLink>` एक खास link है जो खुद पहचानता है कि कौन सा page active है, ताकि हम उसका style बदल सकें।

---

## 🔴 Problem it Solves
Navigation menu mein user ko pata hona chahiye ki woh abhi kis section mein hai (highlight). Har link ka `active` class manually lagana, URL ke saath sync rakhna, aur screen readers ke liye `aria-current` lagana bahut kaam aur galtiyon wala hai. Plain `<a>` tags page reload karte hain. `Link` aur `NavLink` in dono problems ko ek jagah handle karte hain.

## 🔴 यह क्यों बना? (Hindi)
Navigation menu में user को पता होना चाहिए कि वह अभी किस section में है (highlight)। हर link पर `active` class खुद लगाना, URL के साथ sync रखना, और screen readers के लिए `aria-current` लगाना काम और गलतियों वाला है। Plain `<a>` tags page reload करते हैं। `Link` और `NavLink` इन दोनों समस्याओं को एक जगह संभालते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → <Routes> current location (pathname) padhta hai
Step 2 → Har <Route path> ko pattern se match karta hai (static > dynamic > *)
Step 3 → Best match ka element render karta hai
Step 4 → <NavLink to="/x"> current URL ko dekh kar isActive batata hai
Step 5 → isActive true ho to class/style callback aur aria-current="page" lagta hai
Step 6 → end prop ke bina, /products prefix /products/42 par bhi active maana jaata hai
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → <Routes> current location (pathname) पढ़ता है
Step 2 → हर <Route path> को pattern से match करता है (static > dynamic > *)
Step 3 → सबसे अच्छे match का element render करता है
Step 4 → <NavLink to="/x"> current URL देखकर isActive बताता है
Step 5 → isActive true हो तो class/style callback और aria-current="page" लगता है
Step 6 → end prop के बिना, /products prefix /products/42 पर भी active माना जाता है
```

---

## 🟡 Real World Example
**Zomato restaurant app bottom menu:** Tabs "Home", "Search", "Orders", "Account" hain। User "Orders" tab par hai, to Orders tab highlight hota hai। Orders ke andar `/orders/123` kholne par bhi Orders tab active rehta hai, kyunki woh section ka prefix hai। Yeh behavior `NavLink` se free milta hai, aur `end` prop se "Home" tab ko sirf exact `/` par active rakha jaata hai।

## 🟡 Real Example Hindi mein
**Zomato restaurant app bottom menu:** Tabs "Home", "Search", "Orders", "Account" हैं। User "Orders" tab पर है, तो Orders tab highlight होता है। Orders के अंदर `/orders/123` खोलने पर भी Orders tab active रहता है, क्योंकि वह section का prefix है। यह behavior `NavLink` से मुफ्त मिलता है, और `end` prop से "Home" tab को सिर्फ exact `/` पर active रखा जाता है।

---

## 💻 Code Example — Basic

```jsx
import { BrowserRouter, Routes, Route, Link, NavLink } from 'react-router-dom'; // v6 imports

function Home() { return <h1>Home</h1>; }                 // page for "/"
function Products() { return <h1>Products</h1>; }         // page for "/products"
function ProductDetail() { return <h1>Product detail</h1>; } // page for "/products/:id"

export default function App() {
  return (
    <BrowserRouter>                                       {/* gives routing context to everything inside */}
      <nav>
        <NavLink to="/" end>Home</NavLink>                {/* end: active only on exact "/" */}
        <NavLink to="/products">Products</NavLink>        {/* active on /products and /products/42 */}
        <Link to="/products/42">Quick view</Link>         {/* plain link, no active styling */}
      </nav>
      <Routes>                                            {/* matches the current URL */}
        <Route path="/" element={<Home />} />             {/* exact match */}
        <Route path="/products" element={<Products />} /> {/* match for the list */}
        <Route path="/products/:id" element={<ProductDetail />} /> {/* dynamic segment */}
      </Routes>
    </BrowserRouter>
  );
}
```

## 💻 Code Example — Advanced

```jsx
import { NavLink, Routes, Route, Link, Outlet } from 'react-router-dom'; // v6 imports

// Config-driven menu: one place to add or rename sections
const MENU = [
  { to: '/', label: 'Home', end: true },                   // "end" so "/" is not active everywhere
  { to: '/products', label: 'Products' },                  // prefix match is what we want here
  { to: '/orders', label: 'Orders' },                      // also active on /orders/:id
];

function SideNav() {
  return (
    <nav aria-label="Main">                               {/* accessible landmark */}
      {MENU.map(item => (
        <NavLink
          key={item.to}                                   // unique key per menu entry
          to={item.to}                                    // target URL
          end={item.end}                                  // undefined = prefix matching
          className={({ isActive }) =>                    // class depends on the active state
            isActive ? 'nav-item nav-item--active' : 'nav-item'
          }
          style={({ isActive }) => ({ fontWeight: isActive ? 700 : 400 })} // inline style, same idea
        >
          {item.label}                                    {/* visible text */}
        </NavLink>
      ))}
    </nav>
  );
}

function Layout() {
  return (
    <div style={{ display: 'flex' }}>
      <SideNav />                                         {/* stays on screen for every route */}
      <main style={{ flex: 1 }}>
        <Outlet />                                        {/* the matched child page renders here */}
      </main>
    </div>
  );
}

function OrderDetail() {
  return (
    <div>
      <h2>Order details</h2>                              {/* detail page */}
      <Link to="/orders" replace>Back to orders</Link>    {/* replace: no extra history entry */}
    </div>
  );
}

export function AppRoutes() {
  return (
    <Routes>
      <Route element={<Layout />}>                        {/* layout route: no path, just a wrapper */}
        <Route index element={<h1>Home</h1>} />           {/* "/" */}
        <Route path="products" element={<h1>Products</h1>} /> {/* "/products" */}
        <Route path="orders" element={<h1>Orders</h1>} /> {/* "/orders" */}
        <Route path="orders/:id" element={<OrderDetail />} /> {/* "/orders/:id" */}
        <Route path="*" element={<h1>404 Not Found</h1>} /> {/* unknown URLs */}
      </Route>
    </Routes>
  );
}
```

---

## 🟠 Real app integration

In Next.js (App Router) you use `next/link` for navigation, and you check the active state in a Client Component with `usePathname`. The same prefix rule has to be written by hand:

```jsx
'use client';                                             // hooks need a Client Component
import Link from 'next/link';                             // Next.js client navigation
import { usePathname } from 'next/navigation';            // current path, e.g. "/orders/42"

const MENU = [
  { href: '/', label: 'Home' },                           // exact-match item
  { href: '/orders', label: 'Orders' },                   // prefix-match item
];

export default function SideNav() {
  const pathname = usePathname();                         // read the current URL path
  return (
    <nav aria-label="Main">                               {/* landmark for screen readers */}
      {MENU.map(item => {
        const active = item.href === '/'                  // "/" only matches exactly
          ? pathname === '/'
          : pathname === item.href || pathname.startsWith(item.href + '/'); // prefix + boundary
        return (
          <Link
            key={item.href}                               // stable key
            href={item.href}                              // Next.js uses href, not "to"
            aria-current={active ? 'page' : undefined}    // same meaning as NavLink
            className={active ? 'nav-item nav-item--active' : 'nav-item'}
          >
            {item.label}                                  {/* visible text */}
          </Link>
        );
      })}
    </nav>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Forgetting `end` on the home link, so it is always highlighted
✅ **Correct:** Use `end` for the `/` link (exact match), but not for section links.

```jsx
// Wrong: this link is active on EVERY page that starts with "/"
<NavLink to="/">Home</NavLink>                            // ❌ looks active everywhere

// Right: the home link is active only on the exact "/" URL
<NavLink to="/" end>Home</NavLink>                        // ✅
```

Note: `NavLink to="/"` without `end` is not active on `/products` either, because React Router treats the root path specially. The bug usually appears with other top-level paths such as `/orders`, which are active on `/orders/42` by prefix.

❌ **Mistake 2:** Using a plain `<a>` for internal navigation
✅ **Correct:** Use `<Link>` (or `<NavLink>`) so the page does not reload.

```jsx
// Wrong: full reload, and the active state is lost
<a href="/products">Products</a>                           // ❌

// Right: client-side navigation
<Link to="/products">Products</Link>                      // ✅
```

❌ **Mistake 3:** Putting a catch-all `*` route above the real routes
✅ **Correct:** In v6 the ranking is automatic, so `*` is always the last choice. Still, keep it at the end of your list so the code is easy to read.

```jsx
// Wrong: the reader thinks "*" catches first (it does not in v6, but it is confusing)
<Routes>
  <Route path="*" element={<NotFound />} />               // ❌ hard to read
  <Route path="/products" element={<Products />} />
</Routes>

// Right: real routes first, catch-all last
<Routes>
  <Route path="/products" element={<Products />} />       // ✅
  <Route path="*" element={<NotFound />} />
</Routes>
```

---

## 🧠 Tricky Interview Question

```jsx
function Menu() {
  return (
    <MemoryRouter initialEntries={['/products/42']}>
      <NavLink
        to="/products"
        className={({ isActive }) => (isActive ? 'active' : 'idle')}
      >
        Products
      </NavLink>
    </MemoryRouter>
  );
}
// The current URL is /products/42. What HTML does the link get?
```

**Answer:** `<a aria-current="page" class="active" href="/products">Products</a>`. `NavLink` matches by prefix by default, so `/products` is active on `/products/42`. The class callback returns `'active'`, and React Router adds `aria-current="page"` for screen readers. If you add `end` (`<NavLink to="/products" end>`), the match becomes exact, and the output is `class="idle"` with no `aria-current`. I checked this output by rendering the code with `react-router-dom@6.30.6` and `react-dom/server`.

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between `Link` and `NavLink`?**
A1: Both change the URL without reloading. `NavLink` also knows whether its target matches the current location, so it can set `className`, `style`, and `aria-current="page"` based on `isActive`. `Link` has no active state.

**Q2: What does the `end` prop do on `NavLink`?**
A2: Without `end`, the link is active for any URL that starts with its path segment (prefix match). With `end`, it is active only on the exact path. Use `end` for home and for index-like links.

**Q3: How does `<Routes>` choose between `/products` and `/products/:id`?**
A3: It ranks matches. Static segments beat dynamic segments, so `/products/new` wins over `/products/:id` if both exist. The `*` catch-all has the lowest rank. You do not need to order the routes manually in v6.

**Q4: Why is `aria-current="page"` important?**
A4: Screen readers use it to tell the user which item in a navigation menu is the current page. Without it, a visual highlight is the only signal, and a blind user cannot tell where they are.

**Q5: What is the difference between `replace` and a normal `Link` click?**
A5: A normal click pushes a new history entry, so the Back button returns to the previous page. `replace` overwrites the current entry, so Back skips it. Use `replace` for redirects or steps that should not be in history, such as "Back to orders" after an update.

---

## 🔷 When to Use + When Not to Use

✅ **Use when:**
- You have a navigation menu that should show the current section
- You need links that change the URL inside an SPA
- You want accessible navigation (`aria-current`) without extra code

❌ **Avoid when:**
- The link goes to another website: use a plain `<a href>` (it is not part of the app)
- You need the same styling on every link: `Link` is enough, and `NavLink` adds unneeded logic
- The app is in Next.js App Router: use `next/link` and `usePathname` (see the Real app integration section)

---

## 📊 Visual Diagram

```
URL: /products/42

Routes (ranked):   /products/:id    ◄── best match (dynamic)
                   /products
                   *

NavLink "Products" to="/products"  (no end)
   current "/products/42" starts with "/products/" → isActive = true   ✅
   class="active"  aria-current="page"

NavLink "Home" to="/" end
   current "/products/42" !== "/" (exact)          → isActive = false  ❌
   class="idle"

Link "Quick view" to="/products/42"
   plain link, no isActive, no class callback
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Route | URL pattern aur uska element | URL pattern और उसका element |
| Link | Client-side navigation ka link | Client-side navigation का link |
| NavLink | Link jo active state jaanta hai | Link जो active state जानता है |
| end | NavLink ko exact match karne wala prop | Exact match करने वाला prop |
| Prefix match | Path ka shuruaati hissa match hona | Path के शुरुआती हिस्से का match |
| aria-current | Screen readers ko current page batane wala attribute | Current page बताने वाला attribute |

---

## ⚡ 3-Line Summary
**English:**
1. `<Routes>` aur `<Route>` URL pattern ke hisaab se element chunte hain; v6 mein ranking automatic hai.
2. `<Link>` URL badalta hai bina reload ke, aur `<NavLink>` active state ke saath class, style, aur `aria-current` deta hai.
3. `NavLink` prefix par active hota hai, isliye home jaise links par `end` lagao.

**Hindi:**
1. `<Routes>` और `<Route>` URL pattern के हिसाब से element चुनते हैं; v6 में ranking अपने-आप होती है।
2. `<Link>` बिना reload के URL बदलता है, और `<NavLink>` active state के साथ class, style, और `aria-current` देता है।
3. `NavLink` prefix पर active होता है, इसलिए home जैसे links पर `end` लगाओ।

---

## ➡️ Next Topic
**86. useNavigate + useParams + useLocation** — programmatic navigation, URL params, और current location का state।
