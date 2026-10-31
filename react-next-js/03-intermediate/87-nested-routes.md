# 87. Nested Routes
# हिंदी में: Nested Routes — Layout के अंदर child pages, Outlet और index routes

---

## 🔵 Simple Definition (English)
Nested routes ka matlab hai ki ek route ke andar doosre routes hote hain. Parent route ek layout (sidebar, header) dikhata hai, aur child route ka content `<Outlet />` ki jagah render hota hai. Yeh dashboard, admin panel, aur account pages mein bahut kaam aata hai, jahan header/sidebar same rehte hain aur sirf andar ka content badalta hai.

## 🔵 सरल परिभाषा (Hindi)
Nested routes का मतलब है कि एक route के अंदर दूसरे routes होते हैं। Parent route एक layout (sidebar, header) दिखाता है, और child route का content `<Outlet />` की जगह render होता है। यह dashboard, admin panel, और account pages में बहुत काम आता है, जहाँ header/sidebar वही रहते हैं और सिर्फ अंदर का content बदलता है।

---

## 🔴 Problem it Solves
Bina nested routes ke, har page par header, sidebar, aur layout ko copy-paste karna padta है। Layout ka ek bhi change (jaise menu ka item) sab pages mein manually badalna padta. Aur har page khud तय करता है कि sidebar kahan hai, jisse inconsistency aati hai. Nested routes layout ko ek jagah rakhte hain, aur child pages sirf apna content dete hain.

## 🔴 यह क्यों बना? (Hindi)
Nested routes के बिना, हर page पर header, sidebar, और layout को copy-paste करना पड़ता है। Layout का एक बदलाव (जैसे menu का नया item) सब pages में हाथ से बदलना पड़ता है। और हर page खुद तय करता है कि sidebar कहाँ है, जिससे inconsistency आती है। Nested routes layout को एक जगह रखते हैं, और child pages सिर्फ अपना content देते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Parent route define karo: <Route path="/admin" element={<AdminLayout />}>
Step 2 → AdminLayout ke andar <Outlet /> rakho (child yahin render hoga)
Step 3 → Child routes define karo (relative paths): <Route path="orders" .../>
Step 4 → index route: parent ka default child (URL /admin par kya dikhega)
Step 5 → URL /admin/orders → AdminLayout + Orders page, ek saath
Step 6 → Outlet context se parent ka data child tak bhejo (useOutletContext)
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Parent route define करो: <Route path="/admin" element={<AdminLayout />}>
Step 2 → AdminLayout के अंदर <Outlet /> रखो (child यहीं render होगा)
Step 3 → Child routes define करो (relative paths): <Route path="orders" .../>
Step 4 → index route: parent का default child (URL /admin पर क्या दिखेगा)
Step 5 → URL /admin/orders → AdminLayout + Orders page, एक साथ
Step 6 → Outlet context से parent का data child तक भेजो (useOutletContext)
```

---

## 🟡 Real World Example
**Amazon Seller Central:** `/seller` par ek layout hai jisme left side par menu (Orders, Inventory, Payments) aur top par seller ka naam hota hai। Jab seller `/seller/inventory` kholta hai, to layout same rehta hai aur sirf right side ka content Inventory page ka ho jaata hai। Index route `/seller` par dashboard summary dikhata hai।

## 🟡 Real Example Hindi mein
**Amazon Seller Central:** `/seller` पर एक layout है जिसमें बाईं तरफ menu (Orders, Inventory, Payments) और ऊपर seller का नाम होता है। जब seller `/seller/inventory` खोलता है, तो layout वही रहता है और सिर्फ दाईं तरफ का content Inventory page का हो जाता है। Index route `/seller` पर dashboard summary दिखाता है।

---

## 💻 Code Example — Basic

```jsx
import { Routes, Route, Outlet, NavLink } from 'react-router-dom'; // v6 nested route pieces

// Parent layout: header + sidebar stay on screen; the child goes into <Outlet />
function DashboardLayout() {
  return (
    <div style={{ display: 'flex' }}>
      <aside>                                             {/* sidebar, same on every child page */}
        <NavLink to="/dashboard" end>Overview</NavLink>   {/* index page, exact match */}
        <NavLink to="/dashboard/orders">Orders</NavLink>  {/* /dashboard/orders */}
        <NavLink to="/dashboard/settings">Settings</NavLink> {/* /dashboard/settings */}
      </aside>
      <main>
        <Outlet />                                        {/* the matched child renders HERE */}
      </main>
    </div>
  );
}

function Overview() { return <h2>Overview</h2>; }          // index child
function Orders() { return <h2>Your orders</h2>; }         // child at /dashboard/orders
function Settings() { return <h2>Settings</h2>; }         // child at /dashboard/settings

export default function App() {
  return (
    <Routes>
      <Route path="/dashboard" element={<DashboardLayout />}> {/* parent route */}
        <Route index element={<Overview />} />            {/* default child for /dashboard */}
        <Route path="orders" element={<Orders />} />      {/* relative: /dashboard/orders */}
        <Route path="settings" element={<Settings />} />  {/* relative: /dashboard/settings */}
      </Route>
    </Routes>
  );
}
```

## 💻 Code Example — Advanced

```jsx
import { Routes, Route, Outlet, useOutletContext, useParams, Navigate } from 'react-router-dom';

// Parent passes data DOWN to every child through the outlet context (no prop drilling)
function AdminLayout() {
  const user = { name: 'Asha', role: 'admin' };           // in a real app: from auth state
  return (
    <div>
      <header>Admin: {user.name}</header>                 {/* shown for every admin page */}
      <Outlet context={{ user }} />                       {/* children read this with useOutletContext */}
    </div>
  );
}

// Child reads the parent's data without props or a global store
function UserList() {
  const { user } = useOutletContext();                    // { user } from AdminLayout
  return <p>Signed in as {user.role}</p>;                 // role comes from the parent
}

// Three levels deep: /admin/users/:userId/edit
function UserDetail() {
  const { userId } = useParams();                         // param from the middle route
  return (
    <section>
      <h3>User {userId}</h3>                              {/* string from the URL */}
      <Outlet />                                          {/* the edit page renders here */}
    </section>
  );
}

function EditUser() {
  const { userId } = useParams();                         // same param, read again (any level can)
  return <form aria-label={`Edit user ${userId}`} />;    // placeholder form
}

export function AdminRoutes() {
  return (
    <Routes>
      <Route path="/admin" element={<AdminLayout />}>     {/* level 1: layout */}
        <Route index element={<Navigate to="users" replace />} /> {/* /admin → /admin/users */}
        <Route path="users" element={<UserList />} />     {/* level 2: list */}
        <Route path="users/:userId" element={<UserDetail />}> {/* level 2: detail with nested child */}
          <Route path="edit" element={<EditUser />} />    {/* level 3: /admin/users/:userId/edit */}
        </Route>
        <Route path="*" element={<p>Admin page not found</p>} /> {/* unknown admin URL */}
      </Route>
    </Routes>
  );
}
```

Note the difference between the two child routes: `path="users"` and the `index` route are both direct children of `/admin`, but only `index` matches the bare `/admin` URL.

---

## 🟠 Real app integration

Next.js App Router expresses nested layouts with files: a `layout.js` wraps every `page.js` in its folder and below. `children` is the Next.js equivalent of `<Outlet />`:

```jsx
// app/dashboard/layout.js — wraps every page under /dashboard
export default function DashboardLayout({ children }) {   // children = the matched page
  return (
    <div style={{ display: 'flex' }}>                     {/* same layout for every child */}
      <aside>Sidebar</aside>                              {/* stays on screen */}
      <main>{children}</main>                             {/* the child page renders here */}
    </div>
  );
}
```

Express: nested routers work the same way. A parent router mounts child routers, and each level adds its own middleware (for example "must be an admin"):

```javascript
const express = require('express');                       // web framework
const app = express();                                    // create the app

const adminRouter = express.Router();                     // parent router for /api/admin
adminRouter.use((req, res, next) => {                     // runs for EVERY admin route
  if (req.user?.role !== 'admin') return res.status(403).json({ error: 'Forbidden' }); // deny
  next();                                                 // allowed: continue to children
});

const usersRouter = express.Router();                     // child router for users
usersRouter.get('/', (req, res) => res.json([]));         // GET /api/admin/users
usersRouter.get('/:id', (req, res) => res.json({ id: req.params.id })); // GET /api/admin/users/:id

adminRouter.use('/users', usersRouter);                   // nest: /users is handled by usersRouter
app.use('/api/admin', adminRouter);                       // mount the whole tree
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Forgetting `<Outlet />` in the parent, so child pages never appear
✅ **Correct:** Render `<Outlet />` where the child should appear.

```jsx
// Wrong: the layout has no Outlet, so children match but render nothing
function Layout() {
  return <div><header>Admin</header></div>;           // ❌ no <Outlet />
}

// Right: the child renders inside the layout
function Layout2() {
  return <div><header>Admin</header><Outlet /></div>; // ✅
}
```

❌ **Mistake 2:** Using absolute paths for children (`/users`) instead of relative ones
✅ **Correct:** Child paths are relative to the parent. An absolute child path must start with the full parent path, or it throws.

```jsx
// Wrong: /users is not under /admin, so React Router throws
<Route path="/admin" element={<Layout />}>
  <Route path="/users" element={<Users />} />          // ❌ error at render
</Route>

// Right: relative child path, matches /admin/users
<Route path="/admin" element={<Layout />}>
  <Route path="users" element={<Users />} />           // ✅
</Route>
```

❌ **Mistake 3:** Expecting the parent layout to disappear when a URL matches no child
✅ **Correct:** A parent route matches only when a child (or its own path) matches. When nothing matches, the whole `<Routes>` renders nothing, with a warning.

```jsx
// Wrong assumption: "the Shop heading always shows for /shop/..."
<Routes>
  <Route path="/shop" element={<div><h1>Shop</h1><Outlet /></div>}>
    <Route path="products" element={<p>Products</p>} />
  </Route>
</Routes>
// /shop/unknown renders NOTHING, not even the heading

// Right: add a catch-all child so the layout still shows
<Routes>
  <Route path="/shop" element={<div><h1>Shop</h1><Outlet /></div>}>
    <Route path="products" element={<p>Products</p>} />
    <Route path="*" element={<p>Not found</p>} />      // ✅ layout stays on unknown children
  </Route>
</Routes>
```

---

## 🧠 Tricky Interview Question

```jsx
const shop = (
  <Routes>
    <Route path="/shop" element={<div><h1>Shop</h1><Outlet /></div>}>
      <Route path="products" element={<p>Products</p>} />
      <Route index element={<p>Home</p>} />
    </Route>
  </Routes>
);
// Renders for: /shop, /shop/products, /shop/unknown
// What is the HTML for "/shop/unknown"?
```

**Answer:** The output is an empty string. Nothing is rendered: no `<h1>Shop</h1>`, no "Home", and no "Products". The parent route `/shop` has no catch-all child, and `/shop/unknown` does not match any child. React Router therefore does not match the parent route at all, so `<Routes>` returns `null` and logs a warning ("No routes matched location"). The output for `/shop` is `<div><h1>Shop</h1><p>Home</p></div>`, and for `/shop/products` it is `<div><h1>Shop</h1><p>Products</p></div>`. I checked all three outputs by rendering this code with `react-router-dom@6.30.6`. The fix is the catch-all child shown in Mistake 3.

---

## ⚫ Interview Questions + Answers

**Q1: What does `<Outlet />` do?**
A1: It is a placeholder inside a parent layout. React Router renders the matched child route's element at that spot. Without it, the child has nowhere to appear.

**Q2: What is an index route?**
A2: A child route with `index` (or `index: true` in the data router) that matches the parent's exact URL. For `/dashboard` it renders the default overview page. It is the child with no path of its own.

**Q3: What is the difference between a layout route and a normal parent route?**
A3: A layout route has an `element` but no `path` (for example `<Route element={<Layout />}>`). It adds a wrapper to its children without adding a URL segment. A normal parent route with a path adds that segment to the child URLs.

**Q4: How do you pass data from a layout to its children?**
A4: Use `<Outlet context={value} />` in the parent and `useOutletContext()` in the child. This avoids prop drilling. For data shared across the whole app, use a context provider or a store instead.

**Q5: Why does a child with an absolute path cause an error?**
A5: React Router requires an absolute child path to start with the combined path of all its parents. Otherwise it cannot compute the nested URL tree, so it throws during render. Use relative child paths unless you have a specific reason not to.

---

## 🔷 When to Use + When Not to Use

✅ **Use when:**
- Several pages share the same header, sidebar, or tabs (dashboard, admin, account)
- You want one place to change the layout for a whole section
- Child pages need parent data without many props

❌ **Avoid when:**
- The pages have nothing in common (a flat route list is simpler)
- The nesting goes deeper than 3 or 4 levels (the URL and code become hard to follow)
- You only need to share a small value: pass a prop or use a context provider

---

## 📊 Visual Diagram

```
URL: /admin/users/42/edit

<Route path="/admin" element={<AdminLayout />}>          ← level 1 (layout)
│   AdminLayout renders:  <header>...</header>  <Outlet />
│
├── <Route index element={<Navigate to="users" />} />     (/admin)
├── <Route path="users" element={<UserList />} />         (/admin/users)
└── <Route path="users/:userId" element={<UserDetail />}> ← level 2 (matches /admin/users/42)
    │   UserDetail renders:  <h3>User 42</h3>  <Outlet />
    │
    └── <Route path="edit" element={<EditUser />} />      ← level 3 (matches /edit)
                                                           EditUser renders in UserDetail's <Outlet />

Rendered tree:
AdminLayout
 └─ UserDetail (userId = 42)
     └─ EditUser
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Nested route | Ek route ke andar doosra route | एक route के अंदर दूसरा route |
| Outlet | Child route render hone ki jagah | Child route render होने की जगह |
| Index route | Parent ka default child | Parent का default child |
| Layout route | Bina path wala wrapper route | बिना path वाला wrapper route |
| Outlet context | Parent se children tak data | Parent से children तक data |
| Relative path | Parent ke hisaab se path | Parent के हिसाब से path |

---

## ⚡ 3-Line Summary
**English:**
1. Parent layout mein `<Outlet />` rakho, aur child routes uske andar render hote hain (header/sidebar same rehte hain).
2. `index` route parent ka default page hai, aur child paths relative rakho (absolute path error deta hai).
3. `<Outlet context>` aur `useOutletContext` se parent ka data children tak bina prop drilling ke pahunchta hai.

**Hindi:**
1. Parent layout में `<Outlet />` रखो, और child routes उसके अंदर render होते हैं (header/sidebar वही रहते हैं)।
2. `index` route parent का default page है, और child paths relative रखो (absolute path error देता है)।
3. `<Outlet context>` और `useOutletContext` से parent का data children तक बिना prop drilling के पहुँचता है।

---

## ➡️ Next Topic
**88. Protected Routes** — login वाले users को ही pages दिखाना, redirect back के साथ, और यह समझना कि client guard अकेला security नहीं है।
