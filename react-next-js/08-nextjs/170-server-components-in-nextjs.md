# 170. Server Components in Next.js
# हिंदी में: Next.js में Server Components — Server पर चलने वाले Components

---

## 🔵 Simple Definition (English)
**Server Components** are React components that render only on the server. Their code and dependencies are never sent to the browser, only the rendered result is. In the Next.js App Router every component is a Server Component by default, and it can be `async` so it can fetch data directly.

## 🔵 सरल परिभाषा (Hindi)
**Server Components** ऐसे React components हैं जो सिर्फ server पर render होते हैं। उनका code और dependencies browser को नहीं भेजे जाते, सिर्फ rendered नतीजा जाता है। Next.js App Router में हर component default में Server Component है, और वह `async` हो सकता है ताकि सीधे data fetch कर सके।

---

## 🔴 Problem it Solves

In classic React every component ships its JavaScript to the browser, even components that only display data. To get data you needed `useEffect` plus loading state, or an API layer, creating "waterfalls" (render, then fetch, then render). Heavy libraries (markdown parser, date library) were downloaded by every user. Secrets could not be used in components. Server Components run on the server near the database, can use secrets, fetch data with `await`, and send zero JavaScript for the parts that are not interactive.

## 🔴 यह क्यों बना? (Hindi)
Classic React में हर component की JavaScript browser को जाती है, चाहे वह सिर्फ data दिखाता हो। Data के लिए `useEffect` और loading state या API layer चाहिए थी, जिससे "waterfall" बनते थे (render, फिर fetch, फिर render)। भारी libraries (markdown parser, date library) हर user को download करनी पड़ती थीं। Components में secrets इस्तेमाल नहीं हो सकते थे। Server Components server पर, database के पास चलते हैं, secrets इस्तेमाल कर सकते हैं, `await` से data लाते हैं, और जो हिस्से interactive नहीं हैं उनके लिए शून्य JavaScript भेजते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Request arrives; Next.js starts rendering the route's component tree on the server
Step 2 → Server Components run (await data, read env secrets, query a database)
Step 3 → React produces the "RSC payload": a compact description of the UI tree
Step 4 → Next.js turns it into HTML (for fast first paint) and streams it to the browser
Step 5 → Places where a Client Component sits are marked with a reference to its JS bundle
Step 6 → Browser shows HTML at once, downloads only Client Component JS, and hydrates only those
Step 7 → On client-side navigation, the browser fetches the RSC payload for the new route and merges it in

Rules: can use async/await, fs, DB, secrets, server-only packages
Cannot use: useState, useEffect, useRef state, event handlers (onClick), browser APIs (window), context consumers
Can pass: Server Component output as children/props to Client Components (props must be serializable)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Request आता है; Next.js server पर route का component tree render करना शुरू करता है
Step 2 → Server Components चलते हैं (data await, env secrets पढ़ना, database query)
Step 3 → React "RSC payload" बनाता है: UI tree का compact विवरण
Step 4 → Next.js उसे HTML (तेज़ first paint के लिए) में बदलकर browser को stream करता है
Step 5 → जहाँ Client Component है वहाँ उसके JS bundle का reference लगा होता है
Step 6 → Browser HTML तुरंत दिखाता है, सिर्फ Client Component की JS download करता है, और सिर्फ उन्हें hydrate करता है
Step 7 → Client-side navigation पर browser नए route का RSC payload लाकर merge कर देता है

नियम: async/await, fs, DB, secrets, server-only packages चला सकते हैं
नहीं चला सकते: useState, useEffect, event handlers (onClick), browser APIs (window), context consumers
भेज सकते हैं: Server Component का output children/props में Client Components को (props serializable होने चाहिए)
```

---

## 🟡 Real World Example
**Zomato restaurant listing:** The list of 20 restaurants (name, rating, image, cuisines) is pure display, so it is a Server Component that queries the database directly with the DB password staying on the server. The "favourite" heart button and the filter chips need clicks, so those are small Client Components. The user downloads JS only for hearts and filters, not for the whole list or the data-formatting libraries.

## 🟡 Real Example Hindi mein
**Zomato restaurant listing:** 20 restaurants की list (नाम, rating, image, cuisines) सिर्फ दिखाने के लिए है, इसलिए वह Server Component है जो database को सीधे query करता है और DB password server पर ही रहता है। "Favourite" heart बटन और filter chips को clicks चाहिए, इसलिए वे छोटे Client Components हैं। User सिर्फ hearts और filters की JS download करता है, पूरी list या data-formatting libraries की नहीं।

---

## 💻 Code Example — Basic

```jsx
// File: app/restaurants/page.js: an async Server Component (no 'use client')
async function getRestaurants() {
  const res = await fetch('https://api.example.com/restaurants', {
    headers: { Authorization: `Bearer ${process.env.API_SECRET}` }, // secret stays on the server
    next: { revalidate: 300 },                                       // cache the response for 5 minutes
  });
  if (!res.ok) throw new Error('Failed to load restaurants');        // caught by the nearest error.js
  return res.json();                                                 // plain data
}

export default async function RestaurantsPage() {                    // component itself can be async
  const restaurants = await getRestaurants();                        // no useEffect, no loading state
  return (
    <ul>
      {restaurants.map(r => (                                        // render list on the server
        <li key={r.id}>
          {r.name} · {r.rating}★                                     {/* output is HTML, no JS for this */}
        </li>
      ))}
    </ul>
  );
}
// Re-render behavior: this component never re-renders in the browser; it is rendered per request or build.
```

## 💻 Code Example — Advanced

```jsx
// Advanced: server fetching in parallel, Suspense streaming, and a Client Component leaf.

// File: app/restaurants/[id]/page.js
import { Suspense } from 'react';                                    // Suspense enables streaming
import FavouriteButton from './FavouriteButton';                     // Client Component (interactive)
import 'server-only';                                                // build error if imported into client code (npm i server-only)

async function getRestaurant(id) {
  const res = await fetch(`https://api.example.com/restaurants/${id}`, { cache: 'force-cache' });
  return res.json();
}
async function getReviews(id) {
  const res = await fetch(`https://api.example.com/restaurants/${id}/reviews`, { cache: 'no-store' });
  return res.json();                                                 // slow, always fresh
}

// Reviews is its own async Server Component, so it can stream separately
async function Reviews({ id }) {
  const reviews = await getReviews(id);                              // waits here, not blocking the whole page
  return (
    <ul>
      {reviews.map(r => <li key={r.id}>{r.text}</li>)}
    </ul>
  );
}

export default async function Page({ params }) {
  const { id } = await params;                                       // Next.js 15: params is a Promise
  const restaurant = await getRestaurant(id);                        // fast data, blocks only the shell
  return (
    <main>
      <h1>{restaurant.name}</h1>                                     {/* in the first HTML chunk */}
      <FavouriteButton id={restaurant.id} initial={restaurant.fav} />{/* props are serializable data */}
      <Suspense fallback={<p>Loading reviews...</p>}>                {/* shown immediately */}
        <Reviews id={id} />                                          {/* streams in when ready */}
      </Suspense>
    </main>
  );
}

// File: app/restaurants/[id]/FavouriteButton.js
'use client';                                                         // interactive → Client Component
import { useState, useTransition } from 'react';
import { toggleFavourite } from './actions';                         // Server Action (see topic 184)
export default function FavouriteButton({ id, initial }) {
  const [fav, setFav] = useState(initial);                           // local UI state
  const [pending, start] = useTransition();                          // non-blocking update marker
  return (
    <button
      disabled={pending}
      onClick={() => start(async () => {                              // run the server call as a transition
        setFav(f => !f);                                              // optimistic flip
        await toggleFavourite(id);                                    // persist on the server
      })}
    >
      {fav ? '♥ Saved' : '♡ Save'}
    </button>
  );
}
```

---

## 🟠 Next.js Connection

This topic is Next.js specific: RSC is a React feature, but Next.js App Router is the main production implementation. Key Next.js points: `fetch` caching defaults changed (Next.js 14: cached by default; 15: not cached by default, version-dependent), identical `fetch` calls in one render are deduplicated, non-fetch data sources can use `React.cache()` for dedup, and `server-only` guards modules that must never reach the client. You can mix: a Client Component can render Server Components passed to it as `children`.

```jsx
// Pattern: Client wrapper + Server children (the server part stays on the server)
// File: app/components/Collapsible.js
'use client';
import { useState } from 'react';
export default function Collapsible({ title, children }) {            // children is already-rendered server UI
  const [open, setOpen] = useState(false);
  return (
    <div>
      <button onClick={() => setOpen(o => !o)}>{title}</button>
      {open && children}                                              {/* server-rendered content, toggled on client */}
    </div>
  );
}

// File: app/menu/page.js (Server Component)
import Collapsible from '../components/Collapsible';
import MenuList from './MenuList';                                    // async Server Component with DB access
export default function Page() {
  return <Collapsible title="Menu"><MenuList /></Collapsible>;        // server component passed as children
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using hooks or event handlers in a Server Component
✅ **Correct:** Move interactive parts into a separate file with `'use client'`

```jsx
// Wrong: error "You're importing a component that needs useState"
export default function Page() { const [n, setN] = useState(0); return <button onClick={() => setN(n + 1)}>{n}</button>; }

// Right: Page stays on the server; Counter is a Client Component
import Counter from './Counter';
export default function Page() { return <Counter />; }
```

❌ **Mistake 2:** Passing functions or class instances from Server to Client Components
✅ **Correct:** Pass serializable props (strings, numbers, plain objects, arrays, Dates), or use Server Actions

```jsx
// Wrong: functions are not serializable (except Server Actions)
<ClientCard onSelect={() => console.log('x')} />

// Right: pass data; handle the event inside the Client Component
<ClientCard id={42} />
```

❌ **Mistake 3:** Fetching in a Client Component via `useEffect` what a Server Component could fetch
✅ **Correct:** Fetch on the server and pass data down

```jsx
// Wrong: waterfall: HTML → JS → fetch → render
'use client';
useEffect(() => { fetch('/api/restaurants').then(r => r.json()).then(setList); }, []);

// Right: Server Component
const list = await fetch('https://api.example.com/restaurants').then(r => r.json());
```

---

## 🧠 Tricky Interview Question

```jsx
// app/page.js (Server Component)
import Counter from './Counter';          // Counter.js starts with 'use client'
export default function Page() {
  console.log('Page rendered');
  return <Counter />;
}
// Counter.js
'use client';
import { useState } from 'react';
export default function Counter() {
  const [n, setN] = useState(0);
  console.log('Counter rendered', n);
  return <button onClick={() => setN(n + 1)}>{n}</button>;
}
```
**Answer:** `Page rendered` is logged **only in the server terminal**, once per request (or build), never in the browser. `Counter rendered 0` is logged on the **server** (during HTML pre-rendering) and again in the **browser** (hydration). After each click, only `Counter rendered 1`, `2`... appear in the browser console. `Page` never re-renders on the client because Server Components do not run there. (In dev, Next.js may also show server logs inside the browser console with a "Server" label; version-dependent.)

---

## ⚫ Interview Questions + Answers

Q1: What is a Server Component and what are its benefits?
A1: A component rendered only on the server. Benefits: zero client JS for it, direct access to databases and secrets, `async/await` data fetching, smaller bundles (heavy libraries stay on the server) and better first load.

Q2: What can a Server Component not do?
A2: It cannot use state or effect hooks, event handlers, browser-only APIs, or React context consumers. These need a Client Component.

Q3: Can a Client Component import a Server Component?
A3: Not directly: importing makes it part of the client bundle. But a Server Component can pass another Server Component as `children` or a prop to a Client Component, and it renders on the server.

Q4: What does `'use client'` actually do?
A4: It marks a module boundary. This file and everything it imports become part of the client bundle. It does not mean "client-only": Client Components are still pre-rendered to HTML on the server and then hydrated.

Q5: What is streaming and how do Suspense and `loading.js` relate?
A5: The server sends the page in chunks. Parts wrapped in `<Suspense>` show a fallback and are replaced when their async data is ready. `loading.js` is an automatic Suspense boundary around the route segment.

---

## 🔷 When to Use + When Not to Use
✅ **Use Server Components (the default) for:**
- Data display, lists, article content, layouts, SEO-relevant markup
- Anything that needs secrets, a database or heavy server-only libraries

❌ **Do not use (use Client Components) for:**
- State, effects, event handlers, forms with live validation
- Browser APIs (localStorage, geolocation), animations, drag and drop

---

## 📊 Visual Diagram

```
   SERVER                                     BROWSER
   ──────                                     ───────
   <Page>  (Server)  ── await DB ──┐
     ├─ <Header> (Server)          │  HTML + RSC payload
     ├─ <RestaurantList> (Server) ─┼────────────────────────▶  shows content immediately
     │    └─ <FavButton> (Client) ─┘  (reference to JS)         downloads FavButton.js only
     └─ <Suspense>                                              hydrates FavButton only
          └─ <Reviews> (Server, async) ──── streams later ───▶  replaces fallback

   JS shipped to browser: FavButton + React runtime. NOT shipped: Page, Header, RestaurantList, Reviews.
   Re-render: Server Components render per request; Client Components re-render on state change.
   Performance: smaller bundles, fewer waterfalls; server does more work (cache wisely).
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Server Component | Component rendered only on the server | सिर्फ server पर render होने वाला component |
| RSC payload | Serialized result of server rendering | Server rendering का serialized नतीजा |
| `'use client'` | Marks the client module boundary | Client module की सीमा तय करता है |
| Streaming | Sending UI progressively | UI धीरे-धीरे भेजना |
| Suspense | Shows fallback while waiting | इंतज़ार में fallback दिखाता है |
| Serializable | Can be converted to JSON-like data | JSON जैसे data में बदलने योग्य |
| `server-only` | Package that blocks client imports | Client imports रोकने वाला package |
| Waterfall | Sequential dependent requests | एक के बाद एक निर्भर requests |

---

## ⚡ 3-Line Summary
**English:**
1. Server Components render only on the server, can be async, and send no JavaScript to the browser.
2. They cannot use state, effects or event handlers; those go in small `'use client'` components.
3. Pass serializable props, use Suspense for streaming, and keep secrets in server-only code.

**Hindi:**
1. Server Components सिर्फ server पर render होते हैं, async हो सकते हैं, और browser को JavaScript नहीं भेजते।
2. वे state, effects या event handlers इस्तेमाल नहीं कर सकते; उनके लिए छोटे `'use client'` components बनाओ।
3. Serializable props भेजो, streaming के लिए Suspense इस्तेमाल करो, और secrets को server-only code में रखो।

---

## ➡️ Next Topic
**171. Client Components in Next.js** — अब उलटा पहलू: `'use client'` कब और कहाँ लगाएं, boundary कैसे काम करती है, और client bundle को छोटा कैसे रखें।
