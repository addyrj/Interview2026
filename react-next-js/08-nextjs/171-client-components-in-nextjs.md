# 171. Client Components in Next.js
# हिंदी में: Next.js में Client Components — Interactive Components

---

## 🔵 Simple Definition (English)
**Client Components** are React components marked with `'use client'` at the top of the file. They are pre-rendered to HTML on the server and then hydrated in the browser, where they can use state, effects, event handlers and browser APIs.

## 🔵 सरल परिभाषा (Hindi)
**Client Components** ऐसे React components हैं जिनकी file के ऊपर `'use client'` लिखा होता है। वे server पर HTML में pre-render होते हैं और फिर browser में hydrate होते हैं, जहाँ वे state, effects, event handlers और browser APIs इस्तेमाल कर सकते हैं।

---

## 🔴 Problem it Solves

Server Components are great for display but cannot respond to clicks, keep state or access `window`. A real app needs a search box that filters as you type, a cart that updates, modals, maps and charts. Next.js needs a clear signal about which code must be shipped to the browser. `'use client'` is that signal. It lets you keep most of the tree on the server while opting in only the interactive pieces.

## 🔴 यह क्यों बना? (Hindi)
Server Components दिखाने के लिए बढ़िया हैं पर clicks का जवाब नहीं दे सकते, state नहीं रख सकते और `window` तक नहीं पहुँच सकते। असली app को ऐसा search box चाहिए जो type करते ही filter करे, cart जो update हो, modals, maps और charts। Next.js को साफ़ संकेत चाहिए कि कौन सा code browser को भेजना है। `'use client'` वही संकेत है। इससे ज़्यादातर tree server पर रहता है और सिर्फ interactive हिस्से opt-in होते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Add 'use client' as the very first statement of a file (before imports)
Step 2 → That file becomes a boundary: it and all modules it imports go to the client bundle
Step 3 → On the first request the server still renders it to HTML (fast first paint)
Step 4 → The browser downloads its JS and hydrates: attaches handlers, initializes state
Step 5 → After hydration it behaves like normal React: state change → re-render → DOM update
Step 6 → Children passed from a Server Component stay server-rendered (composition)
Step 7 → Props that cross the boundary must be serializable (no functions, except Server Actions)

Place 'use client' as LOW in the tree as possible (on leaves), to keep the bundle small.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → File के बिल्कुल पहले statement (imports से भी पहले) के रूप में 'use client' जोड़ो
Step 2 → वह file boundary बन जाती है: वह और उसके सभी imports client bundle में जाते हैं
Step 3 → पहली request पर server उसे फिर भी HTML में render करता है (तेज़ first paint)
Step 4 → Browser उसकी JS download करके hydrate करता है: handlers जुड़ते हैं, state शुरू होती है
Step 5 → Hydration के बाद यह सामान्य React जैसा है: state बदली → re-render → DOM update
Step 6 → Server Component से आए children server-rendered ही रहते हैं (composition)
Step 7 → Boundary पार करने वाले props serializable होने चाहिए (functions नहीं, सिवाय Server Actions)

'use client' को tree में जितना हो सके नीचे (leaves पर) लगाओ, ताकि bundle छोटा रहे।
```

---

## 🟡 Real World Example
**Swiggy cart widget:** The restaurant menu (item names, descriptions, prices) is a Server Component. Each item has an "ADD" button with a quantity stepper (`-  1  +`). The stepper needs `useState`, `onClick` and perhaps `localStorage` for the cart. So only `QuantityStepper` is a Client Component. A search bar with live filtering is another Client Component. Everything else stays on the server.

## 🟡 Real Example Hindi mein
**Swiggy cart widget:** Restaurant menu (item के नाम, descriptions, prices) Server Component है। हर item में "ADD" बटन और quantity stepper (`-  1  +`) है। Stepper को `useState`, `onClick` और शायद cart के लिए `localStorage` चाहिए। इसलिए सिर्फ `QuantityStepper` Client Component है। Live filtering वाला search bar दूसरा Client Component है। बाकी सब server पर रहता है।

---

## 💻 Code Example — Basic

```jsx
// File: app/menu/QuantityStepper.js: a small Client Component
'use client';                                              // must be the first statement in the file

import { useState } from 'react';                          // hooks are allowed here

export default function QuantityStepper({ itemId, price }) {
  const [qty, setQty] = useState(0);                       // quantity chosen by the user

  return (
    <div>
      {qty === 0 ? (
        <button onClick={() => setQty(1)}>ADD</button>     // first tap adds the item
      ) : (
        <span>
          <button onClick={() => setQty(qty - 1)}>-</button>{/* decrease; at 0 shows ADD again */}
          <strong> {qty} </strong>                         {/* current quantity */}
          <button onClick={() => setQty(qty + 1)}>+</button>{/* increase */}
          <small> ₹{qty * price}</small>                   {/* running total */}
        </span>
      )}
    </div>
  );
}

// File: app/menu/page.js: Server Component that uses it
// import QuantityStepper from './QuantityStepper';
// export default function Menu() {
//   return <ul>{['Biryani','Dosa'].map((n,i) => <li key={n}>{n} <QuantityStepper itemId={i} price={200} /></li>)}</ul>;
// }
// Re-render behavior: clicking + re-renders only QuantityStepper, never the Server Component page.
```

## 💻 Code Example — Advanced

```jsx
// Advanced: a live search with debounce, URL sync, and a browser-only API used safely.
// File: app/menu/MenuSearch.js
'use client';                                               // needs hooks and the browser
import { useState, useEffect, useRef, useTransition } from 'react';
import { useRouter, usePathname, useSearchParams } from 'next/navigation'; // App Router navigation hooks

export default function MenuSearch({ initial = '' }) {
  const router = useRouter();                               // programmatic navigation
  const pathname = usePathname();                           // current path
  const params = useSearchParams();                         // current query string (read-only)
  const [text, setText] = useState(initial);                // what the user typed (updates instantly)
  const [isPending, startTransition] = useTransition();     // marks URL update as non-urgent
  const first = useRef(true);                               // skip the effect on first render

  useEffect(() => {
    if (first.current) { first.current = false; return; }   // do not navigate on mount
    const id = setTimeout(() => {                           // debounce: wait 300 ms after last keystroke
      const next = new URLSearchParams(params.toString());  // copy current params
      if (text) next.set('q', text); else next.delete('q'); // set or remove ?q=
      startTransition(() => {                               // keep typing responsive
        router.replace(`${pathname}?${next.toString()}`);   // update URL; Server Component re-fetches by q
      });
    }, 300);
    return () => clearTimeout(id);                          // cancel previous timer on next keystroke
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [text]);                                               // only react to typing

  return (
    <label>
      Search menu
      <input
        value={text}                                        // controlled input
        onChange={e => setText(e.target.value)}             // update state on each key
        placeholder="Biryani..."
      />
      {isPending && <span> searching...</span>}             {/* feedback while the server renders new results */}
    </label>
  );
}

// File: app/menu/page.js: Server Component reads the same ?q= and filters on the server
// export default async function Menu({ searchParams }) {
//   const { q = '' } = await searchParams;            // Next.js 15: Promise
//   const items = await getMenu(q);                    // DB query with the filter
//   return (<><MenuSearch initial={q} /><ul>{items.map(i => <li key={i.id}>{i.name}</li>)}</ul></>);
// }
```

---

## 🟠 Next.js Connection

This is a Next.js topic. Important Next.js behavior: Client Components are **also rendered on the server** for the first HTML (SSR), so any `window` use during render fails there. Use `useEffect`, or `dynamic(() => import('./Map'), { ssr: false })` inside a Client Component for browser-only libraries (maps, charts). Context providers must be Client Components, so create a `Providers` file and wrap `children` in the root layout, which keeps the layout itself a Server Component.

```jsx
// File: app/providers.js
'use client';                                                  // providers use context/state → client
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'; // TanStack Query v5
import { useState } from 'react';
export default function Providers({ children }) {
  const [client] = useState(() => new QueryClient());          // one client per browser session
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}

// File: app/layout.js (Server Component)
// import Providers from './providers';
// export default function RootLayout({ children }) {
//   return <html lang="en"><body><Providers>{children}</Providers></body></html>; // children stay server-rendered
// }
```

```jsx
// File: app/components/LiveMap.js: browser-only library loaded without SSR
'use client';
import dynamic from 'next/dynamic';                            // lazy loading helper
const Map = dynamic(() => import('./HeavyMap'), {
  ssr: false,                                                  // skip server render (allowed only in Client Components)
  loading: () => <p>Loading map...</p>,                        // placeholder
});
export default function LiveMap() { return <Map />; }
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Putting `'use client'` on a big layout or page
✅ **Correct:** Move it to the smallest interactive component

```jsx
// Wrong: whole page + all its imports become client JS
'use client';
export default function Page() { return <><BigArticle /><LikeButton /></>; }

// Right: only the button is a Client Component
import LikeButton from './LikeButton';   // LikeButton.js has 'use client'
export default function Page() { return <><BigArticle /><LikeButton /></>; }
```

❌ **Mistake 2:** Accessing `window` or `localStorage` during render
✅ **Correct:** Use them in `useEffect` (or event handlers) because the component also renders on the server

```jsx
// Wrong: ReferenceError: window is not defined (during server pre-render)
'use client';
export default function Theme() { const t = localStorage.getItem('theme'); return <p>{t}</p>; }

// Right
'use client';
import { useState, useEffect } from 'react';
export default function Theme() {
  const [t, setT] = useState(null);                        // same on server and first client render
  useEffect(() => setT(localStorage.getItem('theme')), []); // read after hydration
  return <p>{t ?? '...'}</p>;
}
```

❌ **Mistake 3:** Importing a Server Component into a Client Component
✅ **Correct:** Pass it as `children` or a prop from a Server Component

```jsx
// Wrong: ServerStuff (with DB code) is pulled into the client bundle and breaks
'use client';
import ServerStuff from './ServerStuff';
export default function Shell() { return <ServerStuff />; }

// Right: Shell takes children; the Server parent composes it
'use client';
export default function Shell({ children }) { return <div>{children}</div>; }
```

---

## 🧠 Tricky Interview Question

```jsx
// app/page.js (Server Component)
import Counter from './Counter';
export default function Page() {
  return <Counter initial={new Date()} onDone={() => console.log('done')} />;
}
// Counter.js has 'use client'
```
**Answer:** The `Date` prop is fine (React can serialize Dates across the boundary), but the **`onDone` function prop is an error**: functions cannot be passed from a Server Component to a Client Component because they cannot be serialized. Next.js reports "Functions cannot be passed directly to Client Components unless you explicitly expose it by marking it with 'use server'". Fix: define `onDone` inside the Client Component, or make it a Server Action (`'use server'`) if it should run on the server.

---

## ⚫ Interview Questions + Answers

Q1: What does `'use client'` do and where do you put it?
A1: It declares a client boundary. It must be at the top of the file, before imports. The file and every module it imports become part of the client bundle. Components that need state, effects, handlers or browser APIs need it.

Q2: Are Client Components rendered only in the browser?
A2: No. In the App Router they are pre-rendered on the server to HTML and then hydrated. That is why browser-only code must be inside effects or loaded with `ssr: false`.

Q3: How do you keep the client bundle small?
A3: Keep components as Server Components by default, put `'use client'` on small leaf components, pass Server Components as `children` through client wrappers, and lazy-load heavy client code with `next/dynamic`.

Q4: How do you use context providers in the App Router?
A4: Create a Client Component that renders the provider and accepts `children`, then wrap `children` with it in the Server layout. Server Components inside `children` remain on the server.

Q5: What is a hydration mismatch and how do you fix it?
A5: When the HTML rendered on the server differs from what the client renders first (for example `Date.now()`, `Math.random()` or `window` checks), React warns and may re-render. Fix by rendering the same initial output on both and changing it in `useEffect`, or use `suppressHydrationWarning` for unavoidable text like timestamps.

---

## 🔷 When to Use + When Not to Use
✅ **Use Client Components when:**
- You need `useState`, `useEffect`, `useRef`, or custom hooks relying on them
- You need `onClick`, `onChange`, form interactivity, animations
- You use browser APIs or client-only libraries (maps, charts, rich text editors)

❌ **Avoid when:**
- The component only displays data (keep it a Server Component)
- You only need `'use client'` for one small part (extract that part)

---

## 📊 Visual Diagram

```
   Page (Server)
    ├─ Header (Server)               ← 0 KB JS
    ├─ MenuList (Server, async)      ← 0 KB JS
    │    └─ QuantityStepper ('use client')   ← JS shipped + hydrated
    └─ MenuSearch ('use client')     ← JS shipped + hydrated

   Boundary rule: everything imported BY a 'use client' file is client code.
   Composition rule: Server content can be passed INTO a client file as children.

   Lifecycle of a Client Component:
   server HTML render → browser gets HTML → JS loads → hydrate → interactive → state changes re-render

   Performance: each Client Component adds to the bundle; many small ones cost less than one giant one.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Client Component | Interactive component hydrated in browser | Browser में hydrate होने वाला interactive component |
| Client boundary | Where client code begins | जहाँ से client code शुरू होता है |
| Hydration | Attaching JS to server HTML | Server HTML से JS जोड़ना |
| Serializable props | Props convertible to plain data | Plain data में बदलने योग्य props |
| `next/dynamic` | Lazy loading for components | Components की lazy loading |
| `ssr: false` | Skip server rendering for a component | Server पर render न करना |
| Provider | Component that supplies context | Context देने वाला component |
| Leaf component | Component at the bottom of the tree | Tree के सबसे नीचे का component |

---

## ⚡ 3-Line Summary
**English:**
1. Client Components use `'use client'`, are pre-rendered on the server, then hydrated to support state, effects and events.
2. Put the boundary as low as possible and pass Server Components in as `children` to keep the bundle small.
3. Never use `window` during render, never pass functions across the boundary, and wrap providers in a client file.

**Hindi:**
1. Client Components में `'use client'` होता है, वे server पर pre-render होते हैं, फिर hydrate होकर state, effects और events चलाते हैं।
2. Boundary जितना हो सके नीचे रखो और Server Components को `children` बनाकर भेजो ताकि bundle छोटा रहे।
3. Render के दौरान `window` कभी इस्तेमाल मत करो, boundary पार functions मत भेजो, और providers को client file में wrap करो।

---

## ➡️ Next Topic
**172. getServerSideProps (Pages)** — अब Pages Router की data fetching: हर request पर server-side data कैसे लाते हैं (पुराने codebases और interviews में अभी भी बहुत पूछा जाता है)।
