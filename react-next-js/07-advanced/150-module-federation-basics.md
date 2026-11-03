# 150. Module Federation Basics
# हिंदी में: Module Federation — Runtime पर दूसरे App का Code लोड करना

---

## 🔵 Simple Definition (English)
**Module Federation** is a bundler feature (Webpack 5, also Rspack and Vite via plugins) that lets one app load JavaScript modules from **another separately built and deployed app at runtime**. A **host** imports from a **remote**, and both can share libraries like React so they are downloaded once.

## 🔵 सरल परिभाषा (Hindi)
**Module Federation** एक bundler feature है (Webpack 5, साथ में Rspack और plugins से Vite) जो एक app को **दूसरे अलग से build और deploy हुए app** के JavaScript modules **runtime पर** लोड करने देता है। **Host** किसी **remote** से import करता है, और दोनों React जैसी libraries साझा कर सकते हैं ताकि वे एक ही बार download हों।

---

## 🔴 Problem it Solves

Before Module Federation, sharing code between apps meant publishing an npm package: every consumer had to reinstall, rebuild and redeploy to get a change. Alternatives like iframes isolate too much (no shared styles, routing or state), and copy-pasting code is unmaintainable. Micro frontends needed a way to load another team's *latest deployed* code **without rebuilding the host**.

```
PROBLEM: shared via npm package
Cart team fixes a bug → publish v1.2.4 → Shell team bumps version → rebuild → redeploy shell
(days of coordination for a one-line fix)
```

## 🔴 यह क्यों बना? (Hindi)
Module Federation से पहले apps के बीच code साझा करने का मतलब था npm package publish करना: हर उपयोगकर्ता को बदलाव पाने के लिए reinstall, rebuild और redeploy करना पड़ता था। iframes बहुत ज़्यादा अलग कर देते हैं (styles, routing, state साझा नहीं), और copy-paste का रखरखाव नामुमकिन है। Micro frontends को ऐसा तरीका चाहिए था जिसमें दूसरी team का *नवीनतम deployed* code **host को दोबारा build किए बिना** लोड हो।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Remote app configures ModuleFederationPlugin: name, filename (remoteEntry.js), exposes
Step 2 → Remote build emits remoteEntry.js: a small manifest of what it exposes and shares
Step 3 → Host app configures remotes: { cart: 'cart@https://cart.example.com/remoteEntry.js' }
Step 4 → In host code: const Cart = lazy(() => import('cart/CartApp'))  (async boundary)
Step 5 → At runtime the browser fetches remoteEntry.js, then only the chunks it needs
Step 6 → Shared deps (react, react-dom) are negotiated: singleton + version range -> one copy
Step 7 → Remote deploys a new build; host users get it on next load, with no host rebuild

Re-render behavior: the remote component is a normal React component inside the host's tree, so it
re-renders with the host's props and context like any other (context only works if React is a shared singleton).
Performance impact: extra request for remoteEntry.js (waterfall) and chunks; lazy load per route, use
singleton sharing and preload remotes you know you need.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Remote app ModuleFederationPlugin configure करता है: name, filename (remoteEntry.js), exposes
Step 2 → Remote build एक छोटा manifest remoteEntry.js बनाता है: क्या expose और share होता है
Step 3 → Host app remotes configure करता है: { cart: 'cart@https://cart.example.com/remoteEntry.js' }
Step 4 → Host code में: const Cart = lazy(() => import('cart/CartApp'))  (async सीमा)
Step 5 → Runtime पर browser remoteEntry.js लाता है, फिर सिर्फ ज़रूरी chunks
Step 6 → Shared deps (react, react-dom) में बात तय होती है: singleton + version range -> एक ही copy
Step 7 → Remote नया build deploy करे तो host users को अगली load पर वह मिल जाता है, host rebuild नहीं

Re-render behavior: remote component host के tree में सामान्य React component है, इसलिए host के props
और context के साथ आम तरह से re-render होता है (context तभी चलता है जब React shared singleton हो)।
Performance impact: remoteEntry.js की अतिरिक्त request (waterfall) और chunks; route के हिसाब से lazy load,
singleton sharing, और जिन remotes की ज़रूरत पता हो उन्हें preload करो।
```

---

## 🟡 Real World Example
**An e-commerce platform (Flipkart-style):** The `shell` app owns the header and routing. The `cart` team builds a separate app that exposes `./CartApp`. The shell loads `cart/CartApp` when the user opens `/cart`. When the cart team ships a fix at 3 pm, users see it on the next page load, and the shell is never rebuilt. Both apps share one React copy, so the page does not download React twice.

## 🟡 Real Example Hindi mein
**एक e-commerce platform (Flipkart जैसा):** `shell` app header और routing संभालता है। `cart` team एक अलग app बनाती है जो `./CartApp` expose करता है। Shell जब user `/cart` खोलता है तब `cart/CartApp` लोड करता है। Cart team दोपहर 3 बजे fix ship करे तो users को अगली page load पर वह दिखता है, और shell दोबारा build नहीं होता। दोनों apps एक ही React copy साझा करते हैं, इसलिए React दो बार download नहीं होता।

---

## 💻 Code Example — Basic

```js
// Basic: REMOTE app webpack.config.js (cart team). Needs: webpack@5
const { ModuleFederationPlugin } = require('webpack').container; // built-in since Webpack 5
const deps = require('./package.json').dependencies;             // reuse installed versions

module.exports = {
  entry: './src/index.js',                                       // normal app entry (standalone mode)
  output: { publicPath: 'auto' },                                // remoteEntry finds its own chunks
  plugins: [
    new ModuleFederationPlugin({
      name: 'cart',                                              // global name other apps use: "cart"
      filename: 'remoteEntry.js',                                // manifest file the host downloads
      exposes: { './CartApp': './src/CartApp' },                 // public API: cart/CartApp
      shared: {
        react: { singleton: true, requiredVersion: deps.react },           // one React for everyone
        'react-dom': { singleton: true, requiredVersion: deps['react-dom'] }, // same for react-dom
      },
    }),
  ],
};
```

```js
// Basic: HOST app webpack.config.js (shell team)
const { ModuleFederationPlugin } = require('webpack').container;
const deps = require('./package.json').dependencies;

module.exports = {
  entry: './src/index.js',
  plugins: [
    new ModuleFederationPlugin({
      name: 'shell',                                             // host name
      remotes: { cart: 'cart@http://localhost:3002/remoteEntry.js' }, // name@url of the remote manifest
      shared: {
        react: { singleton: true, requiredVersion: deps.react },
        'react-dom': { singleton: true, requiredVersion: deps['react-dom'] },
      },
    }),
  ],
};
```

## 💻 Code Example — Advanced

```jsx
// Advanced: host code with lazy remote, error boundary, loading fallback and a typed contract
// shell/src/App.jsx
import { lazy, Suspense, Component } from 'react';
import { createRoot } from 'react-dom/client';

// "cart/CartApp" is resolved by Module Federation at runtime (bundler turns it into a remote load)
const CartApp = lazy(() => import('cart/CartApp'));

// Error boundary: remote may be down or return an incompatible build
class RemoteBoundary extends Component {
  state = { error: null };
  static getDerivedStateFromError(error) { return { error }; }       // show fallback
  render() {
    if (this.state.error) {
      return (
        <div role="alert">
          <p>Cart is temporarily unavailable.</p>
          <button onClick={() => this.setState({ error: null })}>Retry</button>
        </div>
      );
    }
    return this.props.children;
  }
}

function App() {
  return (
    <div>
      <header>Shop</header>
      <RemoteBoundary>
        <Suspense fallback={<p>Loading cart...</p>}>
          {/* Props are the contract: keep them small, serializable and versioned */}
          <CartApp userId="u_42" onCheckout={(order) => console.log('order', order)} />
        </Suspense>
      </RemoteBoundary>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);
```

```jsx
// remote: cart/src/CartApp.jsx (exposed module; default export is a React component)
import { useState } from 'react';

export default function CartApp({ userId, onCheckout }) {
  const [items] = useState([{ id: 1, name: 'Dosa', price: 120 }]); // remote owns its own state
  const total = items.reduce((s, i) => s + i.price, 0);            // derived value
  return (
    <section>
      <h2>Cart for {userId}</h2>
      {items.map((i) => <p key={i.id}>{i.name} - Rs. {i.price}</p>)}
      <button onClick={() => onCheckout({ userId, total })}>Checkout Rs. {total}</button>
    </section>
  );
}
// Also needed: a bootstrap file so shared modules load asynchronously:
//   index.js:  import('./bootstrap');      bootstrap.js: createRoot(...).render(<App />)
```

---

## 🟠 Next.js Connection

Module Federation with Next.js is **version-dependent and fragile**. The Pages Router worked with the community plugin `@module-federation/nextjs-mf`; the App Router and Server Components have limited or experimental support, and the plugin's maintenance status has changed over time, so check its current docs. The official approach for splitting a Next.js product is **Multi-Zones**. For sharing component code, a monorepo with internal packages (Turborepo, pnpm workspaces) is usually the safer choice. Next.js uses Webpack or Turbopack, and Turbopack does not support Module Federation plugins at the time of writing (version-dependent).

```js
// next.config.js (Pages Router + nextjs-mf plugin, version-dependent example)
const NextFederationPlugin = require('@module-federation/nextjs-mf'); // community plugin

module.exports = {
  webpack(config, { isServer }) {
    config.plugins.push(
      new NextFederationPlugin({
        name: 'shell',                                                // host name
        remotes: {
          cart: `cart@http://localhost:3002/_next/static/${isServer ? 'ssr' : 'chunks'}/remoteEntry.js`,
        },
        filename: 'static/chunks/remoteEntry.js',                      // output location
      })
    );
    return config;
  },
};
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Importing the remote synchronously from the entry file ("Shared module is not available for eager consumption")
✅ **Correct:** Use an async boundary: `index.js` does `import('./bootstrap')`

```js
// Wrong: index.js
import React from 'react';                    // ❌ shared module needed before federation is ready
import './App';

// Right: index.js
import('./bootstrap');                         // ✅ async boundary lets sharing resolve first
```

❌ **Mistake 2:** Not marking React as a `singleton`
✅ **Correct:** Mark `react` and `react-dom` as singleton with a compatible `requiredVersion`

```js
// Wrong
shared: { react: {} }                                  // ❌ two copies possible → "Invalid hook call"
// Right
shared: { react: { singleton: true, requiredVersion: '^18.2.0' } }   // ✅
```

❌ **Mistake 3:** Hard-coding `localhost` remote URLs in production builds
✅ **Correct:** Inject URLs from environment config or load remotes dynamically from a manifest

```js
// Wrong
remotes: { cart: 'cart@http://localhost:3002/remoteEntry.js' }      // ❌ breaks in prod
// Right
remotes: { cart: `cart@${process.env.CART_URL}/remoteEntry.js` }    // ✅ per environment
```

---

## 🧠 Tricky Interview Question

```js
// host webpack config
shared: { react: { singleton: true, requiredVersion: '^18.0.0' } }
// remote webpack config
shared: { react: { singleton: true, requiredVersion: '^19.0.0' } }
```
**Answer:** The versions are incompatible, so only one can win. With `singleton: true`, Module Federation loads a single copy (normally the highest version that satisfies registered ranges, otherwise the first loaded) and prints a warning (or an error if `strictVersion: true`). The other app then runs on a React version it did not declare, which may break (for example, React 19 APIs missing under 18). The fix is to align versions across teams, upgrade together, or avoid sharing React across a major version boundary by loading the remote in its own root.

---

## ⚫ Interview Questions + Answers

Q1: What problem does Module Federation solve?
A1: It lets separately built and deployed apps share code at runtime, so a team can ship a change without the consumer rebuilding. It enables micro frontends and shared libraries without npm publishing or iframes.

Q2: Explain host, remote and shared.
A2: The host is the app that consumes modules. A remote is an app that exposes modules via `remoteEntry.js`. Shared dependencies (React, router, design system) are negotiated at runtime so only one compatible copy is loaded.

Q3: Why do you need a bootstrap file?
A3: Shared modules are resolved asynchronously. If the entry file imports React synchronously, the shared scope is not ready ("eager consumption" error). A dynamic `import('./bootstrap')` creates an async boundary so federation initialises first.

Q4: What are the risks?
A4: Runtime failures if a remote is down or incompatible, version mismatch of shared libs, no type safety across apps by default (use generated types), harder testing, and waterfalls from loading `remoteEntry.js` before chunks.

Q5: How is it different from iframes or npm packages?
A5: Compared to npm packages, updates arrive at runtime with no host rebuild. Compared to iframes, remotes share the same DOM, styles, router and React tree, so integration is deeper, though isolation is weaker.

---

## 🔷 When to Use + When Not to Use
✅ **Use when:**
- Several teams must deploy parts of one UI independently
- You migrate a legacy app piece by piece to a new stack
- You share a large component library or feature across multiple apps at runtime

❌ **Avoid when:**
- One small team owns everything (a monorepo with packages is simpler)
- You depend on Next.js App Router with Server Components (limited support)
- You cannot manage version compatibility and monitoring of remotes

---

## 📊 Visual Diagram

```
   Browser loads HOST (shell)
        │
        ├─ import('cart/CartApp')
        │        │
        │        ▼
        │   fetch https://cart.example.com/remoteEntry.js   (manifest)
        │        │
        │        ▼
        │   fetch chunk CartApp.[hash].js       ← only what is needed
        │
        └─ shared scope:  react (singleton) ◄──── used by host AND remote (one download)

   HOST  ──remotes──►  REMOTE (deployed separately, own CI/CD)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Host | App that consumes remote modules | Remote modules लेने वाला app |
| Remote | App that exposes modules | Modules expose करने वाला app |
| remoteEntry.js | Manifest file of a remote | Remote की manifest file |
| exposes | Modules a remote offers | Remote जो modules देता है |
| shared | Libraries used by both sides | दोनों तरफ़ साझा libraries |
| singleton | Only one copy allowed | केवल एक copy की अनुमति |
| Bootstrap | Async entry to init federation | Federation शुरू करने वाला async entry |
| Multi-Zones | Next.js alternative approach | Next.js का वैकल्पिक तरीका |

---

## ⚡ 3-Line Summary
**English:**
1. Module Federation lets a host load modules from separately deployed remotes at runtime.
2. Configure `exposes`, `remotes` and `shared` (React as singleton) and use an async bootstrap.
3. Wrap remotes in Suspense and error boundaries, and prefer Multi-Zones or a monorepo for Next.js.

**Hindi:**
1. Module Federation host को अलग से deploy हुए remotes के modules runtime पर लोड करने देता है।
2. `exposes`, `remotes` और `shared` (React singleton) configure करो और async bootstrap इस्तेमाल करो।
3. Remotes को Suspense और error boundary में रखो, और Next.js के लिए Multi-Zones या monorepo चुनो।

---

## ➡️ Next Topic
**151. Storybook for Components** — Remote और shared components को अलग से develop, document और test करने का तरीका। इससे shared design system भरोसेमंद बनता है।
