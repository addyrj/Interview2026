# 139. Client Components vs Server Components
# हिंदी में: Client Components बनाम Server Components — कौन सा code कहाँ चलता है

---

## 🔵 Simple Definition (English)
A **Server Component** runs only on the server and sends its rendered result to the browser, with no component JavaScript. A **Client Component** (marked with `'use client'`) is also pre-rendered on the server but its JavaScript is sent to the browser, so it can use state, effects and event handlers.

## 🔵 सरल परिभाषा (Hindi)
**Server Component** सिर्फ server पर चलता है और सिर्फ rendered नतीजा browser को भेजता है, component का JavaScript नहीं भेजता। **Client Component** (`'use client'` वाला) भी पहले server पर pre-render होता है, लेकिन उसका JavaScript browser को जाता है, इसलिए वह state, effects और event handlers इस्तेमाल कर सकता है।

---

## 🔴 Problem it Solves

In a classic React SPA every component ships its JavaScript to the browser, even components that only display data. A product page imports a markdown library, a date library and a big formatter, and all of it lands in the bundle. Data also needs a client-side fetch after the JS loads (a waterfall: HTML, JS, then API call, then content). Server Components let non-interactive parts stay on the server (zero bundle cost, direct database access), while only the interactive parts become Client Components.

```jsx
// PROBLEM (SPA): heavy library ships to every user just to show text
import { marked } from 'marked';                  // ~40KB in the browser bundle
function Description({ md }) {
  return <div dangerouslySetInnerHTML={{ __html: marked(md) }} />; // rendered in the browser
}

// SOLUTION (Server Component): marked stays on the server, browser gets only HTML
// (no 'use client' at the top → this is a Server Component by default in the App Router)
```

## 🔴 यह क्यों बना? (Hindi)
पारंपरिक React SPA में हर component का JavaScript browser को जाता है, चाहे वह सिर्फ data दिखाता हो। Product page markdown library, date library और बड़ा formatter import करता है और सब bundle में चला जाता है। Data के लिए JS load होने के बाद client-side fetch भी चाहिए (waterfall: HTML, JS, API call, फिर content)। Server Components से non-interactive हिस्से server पर रहते हैं (bundle में शून्य cost, सीधे database access), और सिर्फ interactive हिस्से Client Components बनते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → In the Next.js App Router, every component is a Server Component by default
Step 2 → A Server Component can be async, await data, and read the DB/secrets directly
Step 3 → Add 'use client' at the TOP of a file to mark a boundary: this file and everything it imports become client code
Step 4 → Server renders the tree into a special RSC payload (a serialized description of the UI)
Step 5 → HTML is generated for the first paint; the browser also gets JS only for Client Components
Step 6 → Browser hydrates ONLY the Client Components (attaches events, state)
Step 7 → Server Components can pass props (serializable only) and children to Client Components

RULES:
Server Component → NO useState/useEffect/onClick/browser APIs
Client Component → CAN'T import a Server Component, but CAN receive one as children
Re-render: Server Components do not re-render in the browser; they re-run on the server on navigation/refresh
Performance: smaller bundle, fewer waterfalls, less hydration work
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Next.js App Router में हर component डिफ़ॉल्ट रूप से Server Component होता है
Step 2 → Server Component async हो सकता है, data await कर सकता है, DB/secrets सीधे पढ़ सकता है
Step 3 → File के सबसे ऊपर 'use client' लिखो: यह file और इसके सारे imports client code बन जाते हैं
Step 4 → Server UI को एक खास RSC payload में बदलता है (UI का serialized विवरण)
Step 5 → पहली painting के लिए HTML बनता है; browser को JS सिर्फ Client Components का मिलता है
Step 6 → Browser सिर्फ Client Components को hydrate करता है (events, state जुड़ते हैं)
Step 7 → Server Component, Client Component को props (सिर्फ serializable) और children दे सकता है

नियम:
Server Component → useState/useEffect/onClick/browser APIs नहीं
Client Component → Server Component import नहीं कर सकता, लेकिन children के रूप में ले सकता है
Re-render: Server Components browser में re-render नहीं होते; navigation/refresh पर server पर दोबारा चलते हैं
Performance: छोटा bundle, कम waterfalls, कम hydration
```

---

## 🟡 Real World Example
**Swiggy restaurant page:** The menu list, restaurant name, ratings and photos come from the database and never change on the screen, so they are Server Components (zero JS, SEO-friendly HTML). The "Add to cart" button with a quantity counter needs `useState` and `onClick`, so only that small button is a Client Component. The page loads fast, and only the interactive island pays the JavaScript cost.

## 🟡 Real Example Hindi mein
**Swiggy restaurant page:** Menu list, restaurant का नाम, ratings और photos database से आते हैं और screen पर बदलते नहीं, इसलिए ये Server Components हैं (शून्य JS, SEO-friendly HTML)। Quantity counter वाला "Add to cart" बटन `useState` और `onClick` माँगता है, इसलिए सिर्फ वही छोटा बटन Client Component है। Page जल्दी load होता है और JavaScript का cost सिर्फ interactive हिस्से को चुकाना पड़ता है।

---

## 💻 Code Example — Basic

```jsx
// Basic: one Server Component with data + one Client Component with state
// ---------- app/menu/page.jsx (Server Component: no directive needed) ----------
import AddButton from './AddButton';                  // a Client Component, imported normally

async function getDishes() {                          // server-only data function (hypothetical API)
  const res = await fetch('https://example.com/api/dishes'); // runs on the server
  return res.json();                                  // parsed JSON array
}

export default async function MenuPage() {            // async Server Component is allowed
  const dishes = await getDishes();                   // await data directly, no useEffect
  return (
    <ul>
      {dishes.map((d) => (                            // render each dish on the server
        <li key={d.id}>
          {d.name} - Rs {d.price}                     {/* static text: no JS shipped for this */}
          <AddButton dishId={d.id} />                 {/* interactive island (client) */}
        </li>
      ))}
    </ul>
  );
}

// ---------- app/menu/AddButton.jsx (Client Component) ----------
'use client';                                         // boundary: this file runs in the browser too
import { useState } from 'react';                     // hooks allowed only in Client Components

export default function AddButton({ dishId }) {       // dishId is a serializable prop (string/number)
  const [qty, setQty] = useState(0);                  // local interactive state
  return (
    <button onClick={() => setQty(qty + 1)}>          {/* event handler needs the client */}
      Add ({qty})
    </button>
  );
}
```

## 💻 Code Example — Advanced

```jsx
// Advanced: Server Component passed as children into a Client Component (the "donut" pattern)
// ---------- app/components/Collapsible.jsx (Client Component) ----------
'use client';                                          // needs state for open/close
import { useState } from 'react';                      // local UI state

export default function Collapsible({ title, children }) {
  const [open, setOpen] = useState(false);             // is the panel open?
  return (
    <section>
      <button onClick={() => setOpen((o) => !o)}>{title}</button> {/* toggles visibility */}
      {open && <div>{children}</div>}                  {/* children can be Server Components */}
    </section>
  );
}

// ---------- app/components/Reviews.jsx (Server Component) ----------
import { db } from '@/lib/db';                         // hypothetical server-only DB client

export default async function Reviews({ restaurantId }) {
  const reviews = await db.review.findMany({           // direct DB access, secrets never leave server
    where: { restaurantId },
    take: 5,
  });
  return (
    <ul>
      {reviews.map((r) => <li key={r.id}>{r.text}</li>)} {/* rendered on the server */}
    </ul>
  );
}

// ---------- app/restaurants/[id]/page.jsx (Server Component) ----------
import Collapsible from '@/app/components/Collapsible';
import Reviews from '@/app/components/Reviews';

export default async function Page({ params }) {
  const { id } = await params;                         // Next.js 15: params is a Promise
  return (
    <Collapsible title="Show reviews">                 {/* client wrapper handles toggle */}
      <Reviews restaurantId={id} />                    {/* server content passed as children: allowed */}
    </Collapsible>
  );
}

// ---------- lib/secret.js: protect server-only code from leaking into client bundles ----------
import 'server-only';                                  // build fails if a Client Component imports this
export const API_KEY = process.env.PAYMENT_API_KEY;    // never exposed to the browser
```

---

## 🟠 Next.js Connection

This topic is the heart of the Next.js App Router (Next.js 13.4+, stable in 14 and 15). Rules to remember: `'use client'` marks a boundary, not each component. Props from server to client must be serializable (no functions, class instances; Server Actions are the exception). Context providers must be Client Components, so wrap them in a small `'use client'` file and render them from the root layout.

```jsx
// app/providers.jsx
'use client';                                          // providers use context → client
import { ThemeProvider } from './theme';               // hypothetical context provider
export default function Providers({ children }) {
  return <ThemeProvider>{children}</ThemeProvider>;    // children stay server-rendered
}

// app/layout.jsx (Server Component)
import Providers from './providers';
export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body><Providers>{children}</Providers></body>   {/* server layout, client provider */}
    </html>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Putting `'use client'` at the top of every file "to be safe"
✅ **Correct:** Keep it default-server, and add `'use client'` only on the leaf components that need interactivity

```jsx
// Wrong: the whole page becomes client code, bundle grows, no direct DB access
'use client';                                          // ❌ not needed, page has no state
export default function Page() { return <h1>Static</h1>; }

// Right: only the interactive leaf is a client component
import LikeButton from './LikeButton';                 // LikeButton has 'use client'
export default function Page() {                       // ✅ stays a Server Component
  return <><h1>Static</h1><LikeButton /></>;
}
```

❌ **Mistake 2:** Using hooks or event handlers in a Server Component
✅ **Correct:** Move that part into a Client Component

```jsx
// Wrong: Server Component with state → build/runtime error
export default function Page() {
  const [n, setN] = useState(0);                       // ❌ hooks not allowed on the server
  return <button onClick={() => setN(n + 1)}>{n}</button>; // ❌ event handlers not allowed
}

// Right: extract Counter ('use client') and render it from the Server Component
```

❌ **Mistake 3:** Importing a Server Component inside a Client Component
✅ **Correct:** Pass it as `children` or a prop from a Server parent

```jsx
// Wrong
'use client';
import Reviews from './Reviews';                       // ❌ Reviews becomes client code too
export default function Box() { return <Reviews />; }

// Right: Box accepts children, parent (server) passes <Reviews />
'use client';
export default function Box({ children }) { return <div>{children}</div>; } // ✅
```

---

## 🧠 Tricky Interview Question

```jsx
// app/page.jsx (Server Component)
import Child from './Child';
export default function Page() {
  console.log('Page rendered');                        // where does this print?
  return <Child onSave={() => console.log('saved')} />; // passing a function prop
}
// Child.jsx has 'use client' at the top
```
**Answer:** `'Page rendered'` prints in the **server** terminal, not in the browser console. The code also fails: a plain inline function cannot be passed from a Server Component to a Client Component because props must be serializable, and Next.js throws "Functions cannot be passed directly to Client Components unless you explicitly expose it by marking it with 'use server'". The fix is to define the handler inside the Client Component, or to pass a Server Action (a function marked `'use server'`).

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between Server and Client Components?
A1: Server Components render only on the server and add no component JS to the bundle; they can be async and access data sources directly. Client Components are pre-rendered on the server too but are hydrated in the browser, so they support state, effects and events.

Q2: Does `'use client'` mean the component renders only in the browser?
A2: No. Client Components are still pre-rendered to HTML on the server for the first load (SSR), then hydrated. `'use client'` only means that the code is also shipped to and executed in the browser.

Q3: Can a Client Component render a Server Component?
A3: It cannot import one (the import would make it client code), but it can render one received as `children` or another prop, because the server renders it first and passes the result into the slot.

Q4: What props can cross the server-to-client boundary?
A4: Serializable values: strings, numbers, booleans, null/undefined, arrays, plain objects, Date, Map, Set, Promises (React 19 with `use`), JSX elements, and Server Actions. Plain functions, class instances and symbols cannot cross.

Q5: Why are Server Components good for performance?
A5: Their code and dependencies are not in the JS bundle, data is fetched near the source without client-server round trips, and less JavaScript means less parsing and hydration work, which improves metrics like LCP and INP.

---

## 🔷 When to Use + When Not to Use
✅ **Use Server Components when:**
- Fetching data, reading databases or secrets
- Rendering content that has no interactivity (lists, articles, product details)
- Using heavy libraries that should not ship to the browser

❌ **Use Client Components when (not Server):**
- You need `useState`, `useEffect`, `useRef` or event handlers
- You need browser APIs (`window`, `localStorage`, geolocation)
- You use context providers or libraries that depend on client hooks (e.g., many UI/animation libraries)

---

## 📊 Visual Diagram

```
 Server (build/request time)                       Browser
 ┌──────────────────────────────────────┐        ┌──────────────────────────┐
 │ <Page>            Server  (0 JS)     │        │                          │
 │   ├─ <Header/>    Server  (0 JS)     │  RSC   │  HTML shown immediately  │
 │   ├─ <Menu/>      Server  (0 JS) ────┼─payload▶  JS downloaded only for  │
 │   │    └─ DB query                    │ + HTML │  the client islands      │
 │   └─ <AddButton/> CLIENT  ('use client')       │  ┌────────────────────┐  │
 │                                       │        │  │ <AddButton/> hydrated│ │
 └──────────────────────────────────────┘        │  └────────────────────┘  │
                                                  └──────────────────────────┘
 Server comp: runs once on server   |  Client comp: server HTML + browser hydration + re-renders
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Server Component | Renders only on the server, no client JS | सिर्फ server पर render होने वाला component |
| Client Component | Hydrated in the browser, supports state/events | Browser में hydrate होने वाला component |
| `'use client'` | Directive that marks the client boundary | Client boundary तय करने वाला directive |
| RSC payload | Serialized output of Server Components | Server Components का serialized नतीजा |
| Hydration | Attaching JS/events to server HTML | Server HTML में JS/events जोड़ना |
| Serializable props | Values that can be sent over the boundary | Boundary पार भेजे जा सकने वाले values |
| `server-only` | Package that blocks client imports | Client imports रोकने वाला package |
| Island | Small interactive Client Component in static page | स्थिर page में छोटा interactive हिस्सा |

---

## ⚡ 3-Line Summary
**English:**
1. Server Components render on the server with zero client JS; Client Components (`'use client'`) add state, effects and events.
2. Keep the boundary at the leaves, pass only serializable props, and pass Server Components to client ones as `children`.
3. The result is smaller bundles, no fetch waterfalls and faster pages.

**Hindi:**
1. Server Components server पर बिना client JS के render होते हैं; Client Components (`'use client'`) state, effects और events देते हैं।
2. Boundary को leaves पर रखो, सिर्फ serializable props भेजो, और Server Components को `children` बनाकर Client Components को दो।
3. नतीजा: छोटे bundles, fetch waterfalls नहीं और तेज़ pages।

---

## ➡️ Next Topic
**140. Streaming SSR** — Server Components के साथ page को टुकड़ों में browser तक कैसे भेजा जाता है, ताकि धीमा हिस्सा पूरे page को block न करे।
