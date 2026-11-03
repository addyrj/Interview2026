# 149. Micro Frontends Basics
# हिंदी में: Micro Frontends — बड़े Frontend को स्वतंत्र हिस्सों में बाँटना

---

## 🔵 Simple Definition (English)
**Micro frontends** split one large web app into smaller frontend apps that different teams build, test and deploy **independently**. A thin "shell" (host) loads them and shows them together as one product for the user.

## 🔵 सरल परिभाषा (Hindi)
**Micro frontends** एक बड़े web app को छोटे frontend apps में बाँटते हैं, जिन्हें अलग-अलग teams **स्वतंत्र रूप से** बनाती, test करती और deploy करती हैं। एक पतला "shell" (host) उन्हें लोड करके user को एक ही product की तरह दिखाता है।

---

## 🔴 Problem it Solves

A single frontend "monolith" with 100 developers has slow builds, merge conflicts, a shared release train (one bug blocks everyone), and a forced single tech stack. A small checkout fix needs the entire app to be rebuilt and redeployed, and the team that owns search is blocked by the team that owns payments.

```
PROBLEM: one repo, one build, one deploy
[ Header + Search + Catalog + Cart + Checkout + Profile ]  ← 100 devs, 1 release every 2 weeks
Bug in Profile → whole release waits
```

## 🔴 यह क्यों बना? (Hindi)
100 developers वाले एक frontend "monolith" में build धीमा होता है, merge conflicts आते हैं, release एक साथ होती है (एक bug सबको रोक देता है), और एक ही tech stack ज़बरदस्ती रहता है। Checkout के छोटे fix के लिए पूरा app दोबारा build और deploy करना पड़ता है, और search की team payments की team पर अटक जाती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Split by BUSINESS DOMAIN (search, catalog, cart, checkout), not by technical layer
Step 2 → Each team owns its micro frontend end to end: code, build, deploy, (often) its API
Step 3 → A host/shell app provides the page frame, routing, auth and shared dependencies
Step 4 → Integration at runtime (Module Federation, import maps, web components) or build time (npm packages)
Step 5 → Micro frontends talk through a small contract: URL, props, custom events, shared event bus
Step 6 → Shared design system keeps the look consistent; shared libs (React) are loaded once
Step 7 → Each part deploys alone; the shell picks up the new version on the next load

Re-render behavior: each micro frontend has its own React tree (or its own root); a state change
in one does not re-render another. Cross-app updates happen only through events/props at the boundary.
Performance impact: risk of duplicated libraries and extra network requests; mitigate with shared
dependencies, lazy loading each remote and a shared design system.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → BUSINESS DOMAIN के हिसाब से बाँटो (search, catalog, cart, checkout), technical layer के हिसाब से नहीं
Step 2 → हर team अपने micro frontend की पूरी मालिक है: code, build, deploy, (अक्सर) API भी
Step 3 → Host/shell app page का ढाँचा, routing, auth और shared dependencies देता है
Step 4 → Integration runtime पर (Module Federation, import maps, web components) या build time पर (npm packages)
Step 5 → Micro frontends छोटे contract से बात करते हैं: URL, props, custom events, shared event bus
Step 6 → Shared design system look एक-सा रखता है; shared libs (React) एक बार लोड होती हैं
Step 7 → हर हिस्सा अकेले deploy होता है; shell अगली load पर नया version उठा लेता है

Re-render behavior: हर micro frontend का अपना React tree (या अपना root) होता है; एक में state बदलने से
दूसरा re-render नहीं होता। Apps के बीच update सिर्फ events/props से सीमा पर होता है।
Performance impact: libraries का दोहराव और अतिरिक्त network requests का खतरा; shared dependencies,
हर remote की lazy loading और shared design system से कम होता है।
```

---

## 🟡 Real World Example
**Amazon / Flipkart:** The search bar, product listing, cart, checkout and seller recommendations are owned by different teams. The cart team can ship a new "Save for later" feature on Tuesday without waiting for the search team. The shell (header, footer, auth) is shared, and each team's section loads as its own bundle.

## 🟡 Real Example Hindi mein
**Amazon / Flipkart:** Search bar, product listing, cart, checkout और seller recommendations अलग-अलग teams के पास हैं। Cart team मंगलवार को "Save for later" feature बिना search team का इंतज़ार किए ship कर सकती है। Shell (header, footer, auth) साझा है, और हर team का section अपना अलग bundle बनकर लोड होता है।

---

## 💻 Code Example — Basic

```jsx
// Basic: a shell that lazy-loads a "remote" micro frontend and talks to it with a custom event
import { lazy, Suspense, useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';

// In real life this import() points to another team's deployed bundle (see Module Federation topic).
// Here we simulate the remote as a local lazy component.
const CartApp = lazy(() =>
  Promise.resolve({
    default: function CartApp() {                          // the "remote" component
      const add = () =>
        window.dispatchEvent(new CustomEvent('cart:add', { detail: { id: 'dosa', qty: 1 } })); // publish event
      return <button onClick={add}>Add Dosa (from Cart MFE)</button>;
    },
  })
);

function Shell() {
  const [count, setCount] = useState(0);                   // shell state: header badge
  useEffect(() => {
    const onAdd = (e) => setCount((c) => c + e.detail.qty); // subscribe to MFE events
    window.addEventListener('cart:add', onAdd);             // contract: event name + payload
    return () => window.removeEventListener('cart:add', onAdd); // cleanup to avoid leaks
  }, []);

  return (
    <div>
      <header>Shop Shell - Cart ({count})</header>
      <Suspense fallback={<p>Loading cart module...</p>}>  {/* remote may load slowly or fail */}
        <CartApp />
      </Suspense>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<Shell />);
```

## 💻 Code Example — Advanced

```jsx
// Advanced: shell with error isolation + typed event bus + route-based remotes
import { Component, lazy, Suspense, useSyncExternalStore } from 'react';
import { createRoot } from 'react-dom/client';

// --- 1. A tiny shared store (the contract between micro frontends) ---
const cartStore = (() => {
  let state = { items: 0 };                                // single source of truth for cross-MFE data
  const listeners = new Set();                             // subscribers
  return {
    getSnapshot: () => state,                              // stable reference until changed
    subscribe: (cb) => { listeners.add(cb); return () => listeners.delete(cb); },
    add: (n) => { state = { items: state.items + n }; listeners.forEach((l) => l()); }, // new object each change
  };
})();

function useCart() {
  return useSyncExternalStore(cartStore.subscribe, cartStore.getSnapshot, cartStore.getSnapshot); // 3rd arg: server snapshot (needed for SSR)
}

// --- 2. Error boundary: one broken micro frontend must not crash the shell ---
class MfeBoundary extends Component {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; }  // switch to fallback UI
  componentDidCatch(err) { console.error('MFE failed:', this.props.name, err); } // report to monitoring
  render() {
    return this.state.failed ? <p>{this.props.name} is unavailable right now.</p> : this.props.children;
  }
}

// --- 3. Remotes (simulated). Replace with: lazy(() => import('cart/CartApp')) ---
const Catalog = lazy(() => Promise.resolve({
  default: () => <button onClick={() => cartStore.add(1)}>Add item</button>,
}));
const Checkout = lazy(() => Promise.reject(new Error('remote down'))); // simulate a failing deploy

function Header() {
  const { items } = useCart();                             // shell reads shared store
  return <header>Cart items: {items}</header>;
}

function Shell() {
  return (
    <div>
      <Header />
      <MfeBoundary name="Catalog">
        <Suspense fallback={<p>Loading catalog...</p>}><Catalog /></Suspense>
      </MfeBoundary>
      <MfeBoundary name="Checkout">                         {/* failure stays isolated here */}
        <Suspense fallback={<p>Loading checkout...</p>}><Checkout /></Suspense>
      </MfeBoundary>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<Shell />);
```

---

## 🟠 Next.js Connection

Next.js supports micro frontends in two main ways: **Multi-Zones** (separate Next.js apps each owning a path prefix, such as `/cart/*`, stitched together with rewrites or a reverse proxy; navigation between zones is a full page load), and **Module Federation** through community plugins (`@module-federation/nextjs-mf`), which is more fragile with the App Router and is version-dependent. Many teams choose a monorepo with shared packages instead (Turborepo/Nx), which gives most of the team independence with less runtime complexity.

```js
// next.config.js of the main "shell" app (Multi-Zones: forward /cart/* to another Next.js app)
module.exports = {
  async rewrites() {
    return [
      { source: '/cart', destination: `${process.env.CART_URL}/cart` },          // cart zone
      { source: '/cart/:path*', destination: `${process.env.CART_URL}/cart/:path*` }, // nested routes
    ];
  },
};
// In the cart app, set basePath-like assetPrefix (e.g. assetPrefix: '/cart-static') so assets don't clash.
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Splitting too early or too small ("a micro frontend per button")
✅ **Correct:** Start with a modular monolith; split by business domain only when team size or release pain demands it

```jsx
// Wrong: 12 remotes for a 4-person team → heavy infra, slow pages            ❌
// Right: one app with clear modules/packages; extract a remote later         ✅
```

❌ **Mistake 2:** Sharing global state directly (one giant Redux store across all MFEs)
✅ **Correct:** Keep state private; communicate through narrow contracts (URL, events, small shared store)

```jsx
// Wrong: cart MFE imports the catalog MFE's reducers                         ❌
// Right: cart MFE listens to 'cart:add' events with a documented payload     ✅
window.dispatchEvent(new CustomEvent('cart:add', { detail: { id: 'dosa', qty: 1 } }));
```

❌ **Mistake 3:** Loading React several times (each MFE bundles its own copy)
✅ **Correct:** Share React as a singleton, or the app gets bigger and hooks break ("Invalid hook call")

```js
// Wrong: every remote bundles react (duplicate copies)                       ❌
// Right: webpack/rspack shared: { react: { singleton: true }, 'react-dom': { singleton: true } } ✅
```

---

## 🧠 Tricky Interview Question

```jsx
// Host and remote each bundle their OWN copy of React (not shared).
// The remote component uses useState and is rendered by the host with the host's React.
const Remote = lazy(() => import('cart/CartApp'));
function Host() { return <Suspense fallback="..."><Remote /></Suspense>; }
```
**Answer:** It usually fails with an "Invalid hook call" error or `Cannot read properties of null (reading 'useState')`. Hooks rely on an internal dispatcher set by the React copy that renders the tree. If the remote's `useState` comes from a second React copy, that copy's dispatcher is not set, so hooks break. The fix is to mark `react` and `react-dom` as **singleton shared** dependencies with compatible versions so one copy is used.

---

## ⚫ Interview Questions + Answers

Q1: What are micro frontends and why use them?
A1: An architecture where a frontend is composed of independently developed and deployed parts, owned by separate teams. They help scale organisations: faster builds per team, independent releases, technology freedom, and failure isolation.

Q2: What are the main integration approaches?
A2: Build-time (npm packages: simple, but coupled releases), server-side composition (SSI, edge includes), runtime in the browser (Module Federation, import maps, iframes, Web Components), and framework-specific (Next.js Multi-Zones, single-spa).

Q3: How do micro frontends communicate?
A3: Prefer loose coupling: URL/query params, props passed by the shell, browser CustomEvents, or a very small shared store/event bus. Avoid shared mutable global state. Define and version the contract.

Q4: What are the downsides?
A4: Operational complexity, duplicate dependencies, inconsistent UX, harder end-to-end testing and debugging, and more network requests. For small teams a monolith or monorepo is often better.

Q5: How do you keep UI and performance consistent?
A5: Share a design system (tokens and components as a versioned package), share heavy libraries as singletons, lazy load remotes, set performance budgets per team, and monitor Core Web Vitals for the whole page.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- Many teams (roughly 5+ squads) work on one large product
- Teams need independent deploys and different release speeds
- You are migrating gradually from a legacy app to a new stack

❌ **Avoid when:**
- A small team owns the app (a monolith or monorepo is simpler)
- The product is highly interconnected with tightly shared state
- You cannot invest in platform tooling, shared design system, and monitoring

---

## 📊 Visual Diagram

```
                 ┌───────────────────── SHELL / HOST ─────────────────────┐
                 │  auth · routing · layout · design system · shared React │
                 └──────┬─────────────┬──────────────┬──────────────┬─────┘
                        │             │              │              │
                  [ Search ]    [ Catalog ]      [ Cart ]      [ Checkout ]
                  Team A        Team B           Team C        Team D
                  own repo      own repo         own repo      own repo
                  own deploy    own deploy       own deploy    own deploy

   Communication:  URL · props · CustomEvents · tiny shared store
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Micro frontend | Independently deployed UI part | स्वतंत्र रूप से deploy होने वाला UI हिस्सा |
| Shell / Host | App that loads the others | बाकी को लोड करने वाला मुख्य app |
| Remote | Micro frontend loaded by host | Host द्वारा लोड किया गया हिस्सा |
| Monolith | One big app | एक बड़ा app |
| Multi-Zones | Next.js apps joined by path | Path से जुड़े कई Next.js apps |
| Singleton | Only one copy loaded | सिर्फ एक copy लोड होना |
| Contract | Agreed way to communicate | बातचीत का तय तरीका |
| Monorepo | Many packages in one repo | एक repo में कई packages |

---

## ⚡ 3-Line Summary
**English:**
1. Micro frontends split a big frontend by business domain so teams can build and deploy independently.
2. A shell loads the parts at runtime or build time, and parts talk through small contracts.
3. They add complexity: share React as a singleton, isolate errors, and use them only when team scale needs them.

**Hindi:**
1. Micro frontends बड़े frontend को business domain के हिसाब से बाँटते हैं ताकि teams स्वतंत्र रूप से build और deploy कर सकें।
2. Shell हिस्सों को runtime या build time पर लोड करता है, और हिस्से छोटे contracts से बात करते हैं।
3. इनसे जटिलता बढ़ती है: React को singleton share करो, errors को अलग रखो, और तभी इस्तेमाल करो जब team scale माँगे।

---

## ➡️ Next Topic
**150. Module Federation Basics** — Micro frontends को runtime पर जोड़ने की सबसे लोकप्रिय तकनीक। host, remote और shared dependencies की असली configuration वहीं सीखेंगे।
