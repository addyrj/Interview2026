# 182. Next.js Parallel Routes
# हिंदी में: Next.js Parallel Routes — एक ही layout में कई pages एक साथ

---

## 🔵 Simple Definition (English)
**Parallel Routes** let you render several pages at the same time inside one layout, using folders that start with `@` called **slots** (like `@analytics` and `@team`). The layout receives each slot as a prop, next to `children`.

## 🔵 सरल परिभाषा (Hindi)
**Parallel Routes** से आप एक ही layout के अंदर कई pages एक साथ render कर सकते हैं, इसके लिए `@` से शुरू होने वाले folders इस्तेमाल होते हैं जिन्हें **slots** कहते हैं (जैसे `@analytics` और `@team`)। Layout को हर slot `children` के बगल में एक prop की तरह मिलता है।

---

## 🔴 Problem it Solves

A dashboard shows many independent panels: revenue, orders, notifications. If you put them in one page component, one slow query delays all panels, and one error breaks the whole page. Splitting them into manually coordinated components gives no separate loading or error UI per panel, and conditional views (login modal vs dashboard) need messy state. Parallel routes give each panel its own route segment, with its own `loading.js` and `error.js`.

```jsx
// PROBLEM: one page, one failure point, one loading state
export default async function Dashboard() {
  const [a, b] = await Promise.all([getRevenue(), getOrders()]); // slowest wins, any error kills all
}

// SOLUTION: independent slots
// app/dashboard/@revenue/page.js   → own loading + error
// app/dashboard/@orders/page.js    → own loading + error
```

## 🔴 यह क्यों बना? (Hindi)
Dashboard में कई स्वतंत्र panels होते हैं: revenue, orders, notifications। अगर सब एक page component में रखें तो एक धीमी query सब panels को रोक देती है, और एक error पूरा page तोड़ देती है। उन्हें हाथ से अलग components में बाँटने पर भी हर panel का अलग loading या error UI नहीं मिलता, और conditional views (login modal बनाम dashboard) के लिए गंदी state लगती है। Parallel routes हर panel को अपना route segment देते हैं, अपनी `loading.js` और `error.js` के साथ।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create folders that start with @ inside a route: app/dashboard/@revenue, @orders
Step 2 → Each slot has its own page.js (and optional loading.js, error.js)
Step 3 → Slots are NOT URL segments: /dashboard stays /dashboard
Step 4 → app/dashboard/layout.js receives props: { children, revenue, orders }
Step 5 → The layout places each slot anywhere in the JSX
Step 6 → Soft navigation (Link) keeps each slot's active state; a hard reload needs default.js
Step 7 → default.js is the fallback shown when Next.js cannot recover a slot's state

Conditional rendering: the layout can show a slot based on auth/role
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Route के अंदर @ से शुरू होने वाले folders बनाओ: app/dashboard/@revenue, @orders
Step 2 → हर slot की अपनी page.js होती है (और optional loading.js, error.js)
Step 3 → Slots URL segments नहीं हैं: /dashboard, /dashboard ही रहता है
Step 4 → app/dashboard/layout.js को props मिलते हैं: { children, revenue, orders }
Step 5 → Layout हर slot को JSX में कहीं भी रख सकता है
Step 6 → Soft navigation (Link) में हर slot की active state बनी रहती है; hard reload पर default.js चाहिए
Step 7 → default.js वह fallback है जो तब दिखता है जब Next.js किसी slot की state वापस नहीं बना पाता

Conditional rendering: layout auth/role के हिसाब से कोई slot दिखा सकता है
```

---

## 🟡 Real World Example
**Zomato restaurant partner dashboard:** One screen shows live orders, today's revenue and customer reviews side by side. Revenue is a heavy aggregate query (slow), orders are real-time (fast), reviews might fail if the review service is down. With parallel routes, orders appear immediately, revenue shows a skeleton, and a failing reviews panel shows its own "Retry" without breaking the others. Admins also see an extra `@admin` slot that normal staff do not.

## 🟡 Real Example Hindi mein
**Zomato restaurant partner dashboard:** एक screen पर live orders, आज की revenue और customer reviews साथ-साथ दिखते हैं। Revenue भारी aggregate query है (धीमी), orders real-time हैं (तेज़), reviews तब फेल हो सकते हैं जब review service बंद हो। Parallel routes से orders तुरंत दिखते हैं, revenue skeleton दिखाती है, और फेल हुआ reviews panel अपना "Retry" दिखाता है, बाकी नहीं टूटते। Admins को एक अतिरिक्त `@admin` slot भी दिखता है जो सामान्य staff को नहीं दिखता।

---

## 💻 Code Example — Basic

```
app/dashboard/
├── layout.jsx
├── page.jsx             ← becomes the "children" slot
├── @revenue/
│   ├── page.jsx
│   └── loading.jsx
└── @orders/
    ├── page.jsx
    └── error.jsx
```

```jsx
// app/dashboard/layout.jsx: receives each slot as a prop
export default function DashboardLayout({ children, revenue, orders }) {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
      <section>{children}</section>                    {/* app/dashboard/page.jsx */}
      <section>{revenue}</section>                     {/* app/dashboard/@revenue/page.jsx */}
      <section>{orders}</section>                      {/* app/dashboard/@orders/page.jsx */}
    </div>
  );
}
```

```jsx
// app/dashboard/@revenue/page.jsx: slow panel
const sleep = (ms) => new Promise(r => setTimeout(r, ms)); // simulate a slow query

export default async function Revenue() {
  await sleep(2000);                                   // heavy query; only THIS slot waits
  return <h2>Revenue today: ₹1,24,500</h2>;
}
```

## 💻 Code Example — Advanced

```jsx
// app/dashboard/layout.jsx: show a slot conditionally by role
import { cookies } from 'next/headers';                // read the session on the server

export default async function DashboardLayout({ children, revenue, orders, admin }) {
  const role = (await cookies()).get('role')?.value;   // Next.js 15+: cookies() is async
  return (
    <div>
      <nav>Dashboard</nav>
      {children}                                       {/* main page */}
      {role === 'admin' ? admin : null}                {/* @admin slot only for admins */}
      <div style={{ display: 'flex', gap: 16 }}>
        {revenue}                                      {/* independent loading and errors */}
        {orders}
      </div>
    </div>
  );
}
```

```jsx
// app/dashboard/@admin/default.jsx: needed when no matching page exists for this URL
export default function Default() {
  return null;                                         // render nothing instead of a 404
}
```

```jsx
// app/dashboard/@orders/error.jsx: isolated error UI, only this panel breaks
'use client';

export default function OrdersError({ reset }) {
  return (
    <div role="alert">
      <p>Orders unavailable.</p>
      <button onClick={() => reset()}>Retry</button>   {/* retries only this slot */}
    </div>
  );
}
```

---

## 🟠 Real App Integration

Parallel routes are also the base for modals (topic 183). A common pattern is a `@modal` slot that returns `null` by default and shows a dialog when the URL matches an intercepted route.

```jsx
// app/layout.jsx: root layout with a @modal slot
export default function RootLayout({ children, modal }) {
  return (
    <html lang="en">
      <body>
        {children}                                     {/* normal page */}
        {modal}                                        {/* login/product modal overlay */}
      </body>
    </html>
  );
}

// app/@modal/default.jsx
export default function Default() { return null; }      // no modal by default
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Forgetting `default.js` for a slot, then getting 404 on page refresh
✅ **Correct:** Add `default.js` for every slot (and the `children` slot when needed)

```jsx
// Wrong: /dashboard/settings matches children but no page exists in @revenue
// After a hard refresh Next.js cannot find @revenue/settings → 404 ❌

// Right: app/dashboard/@revenue/default.jsx
export default function Default() { return null; }      // ✅ fallback when the slot has no match
```

❌ **Mistake 2:** Thinking `@slot` is part of the URL
✅ **Correct:** Slots are invisible in the URL; link to the route, not the slot

```jsx
// Wrong
<Link href="/dashboard/@revenue">Revenue</Link>         {/* ❌ no such URL */}

// Right
<Link href="/dashboard">Revenue</Link>                  {/* ✅ slots appear because of the layout */}
```

---

## 🧠 Tricky Interview Question

```
app/
├── layout.jsx          (receives children, team)
├── page.jsx
└── @team/
    ├── page.jsx
    └── settings/page.jsx
```
The user clicks `<Link href="/settings">` from the home page, then refreshes the browser. What happens?

**Answer:** On the soft navigation (click), the `@team` slot matches `/settings` and shows `@team/settings/page.jsx`, while `children` (no `settings` folder in the main route) keeps showing its previous active page. After the hard refresh, Next.js has no previous state to keep, and `children` has no match for `/settings`, so it needs `app/default.jsx`; without it the result is a 404. This shows that parallel routes keep the active state of unmatched slots during soft navigation, but need `default.js` for hard loads.

---

## ⚫ Interview Questions + Answers

Q1: What are Parallel Routes?
A1: A way to render multiple pages in one layout simultaneously using `@slot` folders. The layout gets each slot as a prop and decides where to show it.

Q2: Do `@slot` names appear in the URL?
A2: No. `@analytics` is not a URL segment; `app/dashboard/@analytics/page.js` is served at `/dashboard`.

Q3: What is `default.js` for?
A3: It is the fallback for a slot (or `children`) when Next.js cannot match the current URL for that slot, mainly on hard navigation or refresh. Without it you may get a 404.

Q4: What are the benefits for loading and errors?
A4: Each slot can have its own `loading.js` and `error.js`, so panels stream and fail independently without blocking the rest of the page.

Q5: Where are parallel routes commonly used?
A5: Dashboards with independent panels, role-based views (admin vs user), and modals with intercepting routes (login modal, photo preview).

---

## 🔷 When to Use + When Not to Use
✅ **Use parallel routes when:**
- A screen has independent sections with different data sources and failure modes
- You want conditional views by role or auth state in one layout
- You are building URL-driven modals

❌ **Avoid when:**
- Sections are simple and share one data call (plain components or `<Suspense>` are simpler)
- You do not want to maintain `default.js` files for every slot
- Sections must share state heavily (use one page with client state)

---

## 📊 Visual Diagram

```
  URL: /dashboard

  layout.jsx = ({ children, revenue, orders }) =>
  ┌──────────────────────────────────────────────┐
  │  children  ← page.jsx                        │
  │  ┌─────────────────┐ ┌─────────────────────┐ │
  │  │ revenue         │ │ orders              │ │
  │  │ @revenue/page   │ │ @orders/page        │ │
  │  │ loading: skeleton│ │ error: Retry       │ │
  │  └─────────────────┘ └─────────────────────┘ │
  └──────────────────────────────────────────────┘
  Each slot streams and fails independently.

  Re-render behavior: slots are separate React subtrees; one slot's update or
  error does not re-render the others. Soft navigation changes only the slots
  whose route changes.
  Performance: parallel data fetching and streaming reduce time to first useful
  content; fewer waterfalls than one big awaiting page.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Slot | `@folder` rendered by a layout | Layout द्वारा render होने वाला `@folder` |
| Parallel Route | Several pages in one layout | एक layout में कई pages |
| default.js | Fallback when slot has no match | Slot का match न होने पर fallback |
| children slot | Implicit slot for page.js | page.js का implicit slot |
| Soft navigation | Client-side Link navigation | Link से client-side navigation |
| Hard navigation | Full page load or refresh | पूरा page load या refresh |
| Conditional route | Slot shown based on a condition | शर्त पर दिखने वाला slot |
| Independent streaming | Each part loads on its own | हर हिस्से का अलग load होना |

---

## ⚡ 3-Line Summary
**English:**
1. Parallel routes use `@slot` folders so one layout can render several independent pages as props.
2. Each slot has its own loading and error UI, and slots do not appear in the URL.
3. Add `default.js` to avoid 404 on hard navigation, and use slots for dashboards and modals.

**Hindi:**
1. Parallel routes `@slot` folders इस्तेमाल करते हैं ताकि एक layout कई स्वतंत्र pages को props की तरह render करे।
2. हर slot का अपना loading और error UI होता है, और slots URL में नहीं दिखते।
3. Hard navigation पर 404 से बचने के लिए `default.js` जोड़ो, और slots को dashboards व modals के लिए इस्तेमाल करो।

---

## ➡️ Next Topic
**183. Next.js Intercepting Routes** — `(.)`, `(..)`, `(...)` conventions से किसी route को current layout के अंदर modal की तरह दिखाना, और direct URL खोलने पर पूरा page दिखाना।
