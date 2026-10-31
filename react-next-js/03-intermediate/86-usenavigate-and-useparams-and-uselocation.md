# 86. useNavigate + useParams + useLocation
# हिंदी में: useNavigate, useParams और useLocation — Code से navigate करना, URL params पढ़ना, और current location जानना

---

## 🔵 Simple Definition (English)
Ye teen hooks React Router ki functionality code ke andar se use karne dete hain. `useNavigate` se hum programmatically page badalte hain (login ke baad, form submit ke baad). `useParams` se URL ke dynamic parts (`/order/:id` mein `id`) padhte hain. `useLocation` se current URL, query string, aur us navigation ke saath bheji gayi `state` milti hai.

## 🔵 सरल परिभाषा (Hindi)
ये तीन hooks React Router की functionality को code के अंदर से इस्तेमाल करने देते हैं। `useNavigate` से हम programmatically page बदलते हैं (login के बाद, form submit के बाद)। `useParams` से URL के dynamic हिस्से (`/order/:id` में `id`) पढ़ते हैं। `useLocation` से current URL, query string, और उस navigation के साथ भेजा गया `state` मिलता है।

---

## 🔴 Problem it Solves
`<Link>` sirf user ke click par navigate kar sakta hai. Lekin login ke baad, payment success ke baad, ya session expire hone par app ko khud redirect karna padta hai। Dynamic URLs (`/order/123`, `/order/456`) ke liye component ko ID jaananni padti hai। Aur user jis page se aaya tha, usko wapas jaane ke liye us information ki zaroorat hoti hai। Yeh hooks in sab cases ko ek consistent tarike se handle karte hain।

## 🔴 यह क्यों बना? (Hindi)
`<Link>` सिर्फ user के click पर navigate कर सकता है। पर login के बाद, payment success के बाद, या session expire होने पर app को खुद redirect करना पड़ता है। Dynamic URLs (`/order/123`, `/order/456`) के लिए component को ID जाननी पड़ती है। और user जिस page से आया था, उसे वापस जाने के लिए उस जानकारी की ज़रूरत होती है। ये hooks इन सब cases को एक consistent तरीके से संभालते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Route define karo: <Route path="/order/:id" element={<Order />} />
Step 2 → URL /order/123 par useParams() → { id: "123" }  (hamesha string)
Step 3 → useNavigate() ek function deta hai: navigate('/cart') ya navigate(-1)
Step 4 → navigate(path, { replace: true, state: {...} }) history entry badalta hai
Step 5 → Naye page par useLocation() → { pathname, search, hash, state, key }
Step 6 → state.from se user ko wahan bhejo jahan se woh aaya tha
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Route define करो: <Route path="/order/:id" element={<Order />} />
Step 2 → URL /order/123 पर useParams() → { id: "123" }  (हमेशा string)
Step 3 → useNavigate() एक function देता है: navigate('/cart') या navigate(-1)
Step 4 → navigate(path, { replace: true, state: {...} }) history entry बदलता है
Step 5 → नए page पर useLocation() → { pathname, search, hash, state, key }
Step 6 → state.from से user को वहाँ भेजो जहाँ से वह आया था
```

---

## 🟡 Real World Example
**Zomato order tracking:** User checkout karta hai, payment success hota hai, aur app automatically `/orders/8831` par bhejta hai (`useNavigate` ke saath, `replace` ke saath taaki payment page back button se na khule). Order page `useParams` se `8831` padhta hai aur us order ka status fetch karta hai। Agar user login nahi hai, to `useLocation` mein current URL `state` ke roop mein save hota hai, taaki login ke baad wahin wapas aaye।

## 🟡 Real Example Hindi mein
**Zomato order tracking:** User checkout करता है, payment success होता है, और app automatically `/orders/8831` पर भेजता है (`useNavigate` के साथ, `replace` के साथ ताकि payment page back button से न खुले)। Order page `useParams` से `8831` पढ़ता है और उस order का status fetch करता है। अगर user login नहीं है, तो `useLocation` में current URL `state` के रूप में save होता है, ताकि login के बाद वहीं वापस आए।

---

## 💻 Code Example — Basic

```jsx
import { useNavigate, useParams, useLocation } from 'react-router-dom'; // v6 hooks

// Route in the parent: <Route path="/order/:id" element={<OrderPage />} />

function OrderPage() {
  const { id } = useParams();                             // { id: "8831" } from the URL (always a string)
  const location = useLocation();                         // current location object
  const navigate = useNavigate();                         // function to change pages

  return (
    <div>
      <h1>Order #{id}</h1>                                {/* show the order id from the URL */}
      <p>Current path: {location.pathname}</p>            {/* e.g. "/order/8831" */}
      <button onClick={() => navigate('/orders')}>        {/* go to the list on click */}
        Back to all orders
      </button>
      <button onClick={() => navigate(-1)}>               {/* same as the browser Back button */}
        Go back
      </button>
    </div>
  );
}

export default OrderPage;                                 // make it importable
```

## 💻 Code Example — Advanced

```jsx
import { useEffect, useState } from 'react';                                   // React hooks
import { useNavigate, useParams, useLocation, Navigate } from 'react-router-dom'; // v6 hooks

// Login page: after success, go back to the page the user tried to open
export function LoginPage({ onLogin }) {
  const navigate = useNavigate();                         // programmatic navigation
  const location = useLocation();                         // where we came from (set by the guard)
  const from = location.state?.from?.pathname || '/';     // default home if nothing was saved
  const [error, setError] = useState(null);               // login error message

  async function handleSubmit(e) {
    e.preventDefault();                                   // stop the form from reloading the page
    const ok = await onLogin();                           // call your auth function (returns boolean)
    if (!ok) {                                            // login failed
      setError('Wrong password');                         // show message, stay on this page
      return;                                             // do not navigate
    }
    navigate(from, { replace: true });                    // go to the saved page; replace = no back to login
  }

  return (
    <form onSubmit={handleSubmit}>
      {error && <p role="alert">{error}</p>}             {/* accessible error text */}
      <button type="submit">Log in</button>               {/* submit button */}
    </form>
  );
}

// Order page: validate the param, then fetch with an AbortController
export function OrderPage() {
  const { id } = useParams();                             // string from the URL
  const navigate = useNavigate();                         // for the not-found redirect
  const [order, setOrder] = useState(null);               // fetched data
  const orderId = Number(id);                             // convert to a number once

  useEffect(() => {
    if (!Number.isInteger(orderId) || orderId <= 0) {     // invalid id like "abc" or "-1"
      navigate('/404', { replace: true });                // send to not-found page
      return;                                             // stop here
    }
    const controller = new AbortController();             // cancel if the user leaves
    fetch(`/api/orders/${orderId}`, { signal: controller.signal }) // fetch the order
      .then(res => (res.ok ? res.json() : Promise.reject(res.status))) // non-2xx → reject
      .then(setOrder)                                     // store the data
      .catch(status => {                                  // rejected or network error
        if (status === 404) navigate('/404', { replace: true }); // missing order
      });
    return () => controller.abort();                      // cleanup
  }, [orderId, navigate]);                                // refetch when the id changes

  return order ? <h1>{order.status}</h1> : <p>Loading…</p>; // simple render
}

// Guard that remembers the URL the user wanted (used with LoginPage)
export function RequireLogin({ loggedIn, children }) {
  const location = useLocation();                         // current URL before the redirect
  if (!loggedIn) {                                        // not logged in
    return <Navigate to="/login" replace state={{ from: location }} />; // pass the URL along
  }
  return children;                                        // logged in: show the page
}
```

---

## 🟠 Real app integration

Express: validate the path parameter on the server too. A React page can receive any URL the user types, and the API must never trust it:

```javascript
const express = require('express');                       // web framework
const app = express();                                    // create the app
// db is a pg Pool created elsewhere

app.get('/api/orders/:id', async (req, res) => {          // GET /api/orders/8831
  const id = Number(req.params.id);                       // params are always strings
  if (!Number.isInteger(id) || id <= 0) {                 // reject "abc", "1.5", "-3"
    return res.status(400).json({ error: 'Invalid order id' }); // 400 Bad Request
  }
  const { rows } = await db.query(                        // parameterized query
    'SELECT id, status, total FROM orders WHERE id = $1 AND user_id = $2', // ownership check
    [id, req.user.id]                                     // req.user set by your auth middleware
  );
  if (rows.length === 0) {                                // not found, or not yours
    return res.status(404).json({ error: 'Order not found' }); // same answer for both (no leak)
  }
  res.json(rows[0]);                                      // the order as JSON
});
```

Next.js App Router: `useParams` is available in Client Components, and the route params are passed as props to Server Components (in Next.js 15+ `params` is a Promise, so you must `await` it):

```jsx
// app/orders/[id]/page.js — Server Component
export default async function Page({ params }) {          // Next.js 15+: params is a Promise
  const { id } = await params;                            // await before reading the dynamic segment
  return <h1>Order #{id}</h1>;                            // id is still a string
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Treating `useParams` values as numbers
✅ **Correct:** Params are strings. Convert them and validate.

```jsx
// Wrong: "007" and 7 are different values
const { id } = useParams();                               // "007"
if (id === 7) showOrder();                                // ❌ always false

// Right: convert once, then compare
const orderId = Number(id);                               // 7
if (orderId === 7) showOrder();                           // ✅
```

❌ **Mistake 2:** Calling `navigate()` during render
✅ **Correct:** Navigate inside an effect or an event handler.

```jsx
// Wrong: every render triggers a navigation (and a warning)
function Old() {
  const navigate = useNavigate();
  if (!user) navigate('/login');                          // ❌ side effect in render
  return <p>Profile</p>;
}

// Right: put the side effect in useEffect, or use <Navigate />
function Fixed() {
  const navigate = useNavigate();
  useEffect(() => {
    if (!user) navigate('/login', { replace: true });     // ✅ runs after render
  }, [user, navigate]);
  return <p>Profile</p>;
}
```

❌ **Mistake 3:** Using `navigate(-1)` when the user opened the page directly
✅ **Correct:** Check that there is somewhere to go back to, or give a clear fallback link.

```jsx
// Wrong: on a fresh tab, "back" leaves your app entirely
<button onClick={() => navigate(-1)}>Back</button>        // ❌ may close the app's history

// Right: prefer a real link to a known page, or check history state
<button onClick={() => (location.key !== 'default' ? navigate(-1) : navigate('/orders'))}>
  Back                                                    {/* ✅ fallback when no history */}
</button>
```

---

## 🧠 Tricky Interview Question

```jsx
function Order() {
  const { id } = useParams();                             // route: /order/:id, URL: /order/007
  console.log(typeof id, id);                             // (1)
  console.log(id === 7);                                  // (2)
  console.log(Number(id) === 7);                          // (3)
  return <p>Order {id}</p>;
}
// Route: <Route path="/order/:id" element={<Order />} /> and the URL is /order/007
// What are the three console outputs?
```

**Answer:** `string 007`, then `false`, then `true`. `useParams()` always returns strings, so `id` is the text `"007"`, not the number `7`. The strict comparison `id === 7` is false because the types differ. `Number("007")` is `7` (leading zeros are dropped by the conversion), so the third check is true. The rendered text is `Order 007`, because the string keeps its zeros. I checked these outputs by rendering this component with `react-router-dom@6.30.6`.

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between `useNavigate` and `<Navigate />`?**
A1: `useNavigate()` returns a function you call from an event handler or an effect. `<Navigate />` is a component that redirects when it renders. Use `<Navigate />` for guards in render (for example "not logged in"), and `useNavigate` for actions after the user clicks something.

**Q2: What does `replace: true` change?**
A2: It replaces the current history entry instead of adding a new one. After login or a redirect, the Back button does not return to the login page.

**Q3: What does `useLocation` give you, and what is `location.state` used for?**
A3: It gives `pathname`, `search`, `hash`, `state`, and a unique `key`. `state` is data attached to one navigation (it does not appear in the URL). Typical use: `navigate('/login', { state: { from: location } })`, so the login page knows where to send the user back.

**Q4: Why is `useParams` always a string?**
A4: URLs are text. React Router does not guess types, so `/order/7` gives `"7"`. Convert with `Number()` (or validate with a regex) before you compare or send it to a database.

**Q5: Why must you navigate inside `useEffect` and not in render?**
A5: Render must be pure: calling it twice (Strict Mode, concurrent rendering) must give the same result. A navigation in render changes global state during render, which can cause loops or warnings. Effects and event handlers are the right places for side effects.

---

## 🔷 When to Use + When Not to Use

✅ **Use when:**
- You must redirect after a form submit, login, or payment
- A page depends on an ID in the URL (product, order, user profile)
- You need to remember where the user came from (login redirect, "back" link)

❌ **Avoid when:**
- The user clicks a plain link: `<Link>` is simpler and more accessible
- You want to pass large data between pages: use a store or fetch by ID, not `state`
- You want to read a query string value only: `useSearchParams` (topic 81) fits better than `useLocation().search`

---

## 📊 Visual Diagram

```
Route:       /order/:id                 URL: /order/8831?tab=items#top
                 │                              │
                 ▼                              ▼
useParams()  →  { id: "8831" }        useLocation()  →  {
                                                          pathname: "/order/8831",
                                                          search:   "?tab=items",
                                                          hash:     "#top",
                                                          state:    { from: {...} },  // from navigate()
                                                          key:      "k7x2p"
                                                        }

useNavigate()
  navigate("/orders")                  → push a new history entry
  navigate("/orders", { replace: true }) → replace the current entry
  navigate(-1)                         → go back one entry (like the Back button)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| useNavigate | Code se navigate karne ka function dene wala hook | Code से navigate करने का function |
| useParams | URL ke dynamic segments dene wala hook | URL के dynamic हिस्से देने वाला hook |
| useLocation | Current location (path, query, state) dene wala hook | Current location देने वाला hook |
| replace | History entry ko overwrite karna | History entry को overwrite करना |
| location.state | Navigation ke saath bheja gaya hidden data | Navigation के साथ भेजा गया hidden data |
| Side effect | Render ke bahar ka kaam, jaise navigate ya fetch | Render के बाहर का काम |

---

## ⚡ 3-Line Summary
**English:**
1. `useNavigate` code se page badalta hai, `useParams` URL ke dynamic parts (hamesha string) deta hai, aur `useLocation` current URL aur `state` deta hai।
2. Params ko `Number()` se convert aur validate karo, aur navigation ko render ke bajaye effect ya event handler mein karo।
3. Login redirect ke liye `state.from` aur `replace: true` ka use karo, taaki user back button se confuse na ho।

**Hindi:**
1. `useNavigate` code से page बदलता है, `useParams` URL के dynamic हिस्से (हमेशा string) देता है, और `useLocation` current URL और `state` देता है।
2. Params को `Number()` से convert और validate करो, और navigation को render की बजाय effect या event handler में करो।
3. Login redirect के लिए `state.from` और `replace: true` इस्तेमाल करो, ताकि user back button से confuse न हो।

---

## ➡️ Next Topic
**87. Nested Routes** — layout routes, `<Outlet />`, index routes, aur outlet context से child pages तक data भेजना।
