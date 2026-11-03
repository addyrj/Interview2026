# 164. React Native vs React Web
# हिंदी में: React Native vs React Web — क्या same है, क्या अलग

---

## 🔵 Simple Definition (English)
React Web renders components to HTML in a browser using `react-dom`. React Native renders the same kind of components to native mobile views using the React Native renderer. The React core (components, hooks, state, props) is shared; the UI primitives, styling and platform APIs are different.

## 🔵 सरल परिभाषा (Hindi)
React Web components को `react-dom` से browser में HTML बनाता है। React Native उसी तरह के components को React Native renderer से native mobile views में बदलता है। React का core (components, hooks, state, props) share होता है; UI primitives, styling और platform APIs अलग होते हैं।

---

## 🔴 Problem it Solves

Developers who know React Web often assume "it is all React" and try to move code to mobile unchanged. It fails: `div` does not exist, CSS files do not exist, `localStorage` does not exist and routing works differently. The opposite problem is teams rewriting working business logic in each platform. Understanding exactly which layer is shared (logic) and which layer is different (view and platform) lets you reuse the right code and avoid wasted rewrites.

## 🔴 यह क्यों बना? (Hindi)
React Web जानने वाले developers अक्सर मान लेते हैं कि "सब React ही है" और code को बिना बदले mobile पर ले जाते हैं। यह fail होता है: `div` नहीं है, CSS files नहीं हैं, `localStorage` नहीं है और routing अलग तरह से चलती है। उल्टी समस्या यह है कि teams हर platform में चल रहा business logic दोबारा लिखती हैं। कौन सी layer share होती है (logic) और कौन सी अलग (view व platform) यह समझने से सही code reuse होता है और बेकार rewrite बचता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Same: JSX syntax, function components, props, state, hooks, context, reducers
Step 2 → Same: state libraries (Redux Toolkit, Zustand) and TanStack Query v5
Step 3 → Different renderer: react-dom (DOM nodes) vs react-native (native views)
Step 4 → Different primitives: div/span/button/img/input vs View/Text/Pressable/Image/TextInput
Step 5 → Different styling: CSS, classes, cascade vs StyleSheet objects, Flexbox column default
Step 6 → Different navigation: URLs and <a>/react-router vs screens stack (React Navigation / Expo Router)
Step 7 → Different platform APIs: localStorage, window, document vs AsyncStorage/SecureStore, Linking, permissions
Step 8 → Different distribution: deploy a website vs App Store / Play Store releases (OTA updates for JS only)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Same: JSX syntax, function components, props, state, hooks, context, reducers
Step 2 → Same: state libraries (Redux Toolkit, Zustand) और TanStack Query v5
Step 3 → अलग renderer: react-dom (DOM nodes) vs react-native (native views)
Step 4 → अलग primitives: div/span/button/img/input vs View/Text/Pressable/Image/TextInput
Step 5 → अलग styling: CSS, classes, cascade vs StyleSheet objects, Flexbox में default column
Step 6 → अलग navigation: URLs और <a>/react-router vs screens का stack (React Navigation / Expo Router)
Step 7 → अलग platform APIs: localStorage, window, document vs AsyncStorage/SecureStore, Linking, permissions
Step 8 → अलग distribution: website deploy करना vs App Store / Play Store release (सिर्फ JS के लिए OTA updates)
```

---

## 🟡 Real World Example
**Amazon cart on web vs app:** The cart logic is the same: add item, change quantity, compute total, apply coupon. A shared `useCart` hook and a `cartReducer` can run on both. On the website the cart page uses `<div>`, CSS Grid and a `<Link href="/checkout">`. In the mobile app the same cart uses `<View>`, `FlatList`, `Pressable` and `navigation.navigate('Checkout')`. The cart is persisted in `localStorage` on web but in `AsyncStorage` or secure storage on mobile.

## 🟡 Real Example Hindi mein
**Amazon cart web बनाम app:** Cart का logic same है: item जोड़ना, quantity बदलना, total निकालना, coupon लगाना। Shared `useCart` hook और `cartReducer` दोनों जगह चल सकते हैं। Website पर cart page `<div>`, CSS Grid और `<Link href="/checkout">` इस्तेमाल करता है। Mobile app में वही cart `<View>`, `FlatList`, `Pressable` और `navigation.navigate('Checkout')` इस्तेमाल करता है। Cart web पर `localStorage` में और mobile पर `AsyncStorage` या secure storage में save होता है।

---

## 💻 Code Example — Basic

```jsx
// SAME logic, DIFFERENT view: a shared hook used by a web and a native component
// File: shared/useCounter.js (works in both React Web and React Native)
import { useState, useCallback } from 'react';          // only React core is imported (no DOM, no RN)

export function useCounter(initial = 0) {
  const [count, setCount] = useState(initial);           // state works identically on both platforms
  const inc = useCallback(() => setCount(c => c + 1), []); // stable increment function
  const dec = useCallback(() => setCount(c => Math.max(0, c - 1)), []); // never below zero
  return { count, inc, dec };                            // return the logic, not the UI
}

// File: web/CartButtons.jsx (React Web view)
import { useCounter } from '../shared/useCounter';       // reuse shared logic
export function CartButtonsWeb() {
  const { count, inc, dec } = useCounter();              // same hook
  return (
    <div className="qty">                                 {/* HTML element + CSS class */}
      <button onClick={dec}>-</button>                    {/* onClick on a DOM button */}
      <span>{count}</span>                                {/* plain text in a span */}
      <button onClick={inc}>+</button>
    </div>
  );
}

// File: native/CartButtons.jsx (React Native view)
import { View, Text, Pressable } from 'react-native';     // native primitives
import { useCounter } from '../shared/useCounter';        // same hook again
export function CartButtonsNative() {
  const { count, inc, dec } = useCounter();               // zero duplicated logic
  return (
    <View style={{ flexDirection: 'row', alignItems: 'center' }}> {/* row layout via style object */}
      <Pressable onPress={dec}><Text>-</Text></Pressable> {/* onPress, text inside Text */}
      <Text style={{ marginHorizontal: 12 }}>{count}</Text>
      <Pressable onPress={inc}><Text>+</Text></Pressable>
    </View>
  );
}
```

## 💻 Code Example — Advanced

```jsx
// Platform-specific storage behind one interface, plus file-extension based components
// File: shared/storage.js: a tiny adapter so shared code never touches localStorage directly
export function createStorage(adapter) {
  return {
    async get(key) {                                      // always async, so it fits both platforms
      const raw = await adapter.getItem(key);             // adapter: localStorage wrapper or AsyncStorage
      return raw ? JSON.parse(raw) : null;                // parse or return null
    },
    async set(key, value) {
      await adapter.setItem(key, JSON.stringify(value));  // serialize before saving
    },
  };
}

// File: web/storage.js
import { createStorage } from '../shared/storage';
// Wrap the synchronous localStorage so it looks async
export const storage = createStorage({
  getItem: async k => localStorage.getItem(k),            // browser only API
  setItem: async (k, v) => localStorage.setItem(k, v),
});

// File: native/storage.js (needs: npx expo install @react-native-async-storage/async-storage)
import AsyncStorage from '@react-native-async-storage/async-storage';
import { createStorage } from '../shared/storage';
export const storage = createStorage(AsyncStorage);       // AsyncStorage already has getItem/setItem

// File: shared/useCartStorage.js
import { useEffect, useState } from 'react';
export function useCartStorage(storage) {                 // storage is injected: platform decides
  const [cart, setCart] = useState([]);                   // list of items
  const [ready, setReady] = useState(false);              // avoid overwriting before load
  useEffect(() => {
    storage.get('cart').then(saved => {                   // load once on mount
      if (saved) setCart(saved);                          // restore saved cart
      setReady(true);                                     // now saving is safe
    });
  }, [storage]);
  useEffect(() => {
    if (ready) storage.set('cart', cart);                 // persist on every change after load
  }, [cart, ready, storage]);
  return [cart, setCart];
}

// Bundlers can also pick files by extension (Metro/RN): Button.native.jsx vs Button.web.jsx
// import Button from './Button'; → Metro chooses Button.native.jsx on iOS/Android
```

---

## 🟠 Next.js Connection

Next.js is the web side of the comparison, and it adds server rendering on top. Server Components, `next/image`, `next/link` and Route Handlers have no direct React Native equivalent (RN apps have no server rendering of UI). If you want web and native from one codebase you can use `react-native-web` (renders RN components to DOM) with Next.js, or tools like Solito and Expo Router's web output (version-dependent: check current docs).

```jsx
// app/cart/page.jsx (Next.js 14/15 Server Component) reusing shared logic
import CartClient from './CartClient';                    // Client Component (uses hooks)
import { getCoupons } from '@/shared/api';                // shared API function, no UI in it

export default async function CartPage() {
  const coupons = await getCoupons();                     // server side fetch, no loading spinner on client
  return <CartClient coupons={coupons} />;                // pass plain data to the client side
}
```

```jsx
// app/cart/CartClient.jsx
'use client';                                              // needed because we use state/localStorage
import { useCounter } from '@/shared/useCounter';          // same hook as the RN app
export default function CartClient({ coupons }) {
  const { count, inc } = useCounter();                     // shared logic
  return <button onClick={inc}>Items: {count} · {coupons.length} coupons</button>;
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using browser globals (`window`, `document`, `localStorage`) in shared code
✅ **Correct:** Hide them behind an adapter that each platform provides

```jsx
// Wrong: crashes in React Native (no localStorage) and in Next.js server rendering
const saved = localStorage.getItem('cart');

// Right: inject storage from the platform layer
function loadCart(storage) { return storage.get('cart'); }
```

❌ **Mistake 2:** Expecting CSS features in RN styles (`display: grid`, class selectors, `:hover`, cascade)
✅ **Correct:** Use Flexbox style objects and component props for states

```jsx
// Wrong in RN
<View style={{ display: 'grid', gridTemplateColumns: '1fr 1fr' }} />

// Right: Flexbox with wrap
<View style={{ flexDirection: 'row', flexWrap: 'wrap' }} />
```

❌ **Mistake 3:** Sharing UI components directly between web and mobile without a plan
✅ **Correct:** Share hooks, types and API code; keep thin separate view layers (or adopt react-native-web deliberately)

```jsx
// Wrong: one component importing both
import { View } from 'react-native';
import Link from 'next/link';               // ❌ mixing platform-specific imports

// Right: shared hook + one view per platform (see Basic example)
```

---

## 🧠 Tricky Interview Question

```jsx
// Does this React Native component work?
import { View, Text } from 'react-native';
export default function App() {
  return (
    <View style={{ width: 100, height: 100, backgroundColor: 'red' }}>
      <Text style={{ fontSize: 20 }}>Hello</Text>
      <View style={{ flex: 1, backgroundColor: 'blue' }} />
    </View>
  );
}
```
**Answer:** Yes. The outer `View` is 100 by 100. It uses Flexbox with the default `flexDirection: 'column'` (web default is `row`). The `Text` takes its natural height (about 20 to 24 points) and the inner blue `View` with `flex: 1` fills the remaining height. The key interview point: in RN every view is already a flex container, and the default direction is column, unlike web CSS where `div` is block layout and `display: flex` defaults to row.

---

## ⚫ Interview Questions + Answers

Q1: What do React Web and React Native share?
A1: The React core: components, JSX, props, state, hooks, context, reconciliation (the diffing algorithm), and most state or data libraries (Redux Toolkit, Zustand, TanStack Query). They differ in renderer and primitives.

Q2: How does layout differ?
A2: On web you use CSS (block, inline, grid, flex, with `row` default). In RN you use Flexbox only, with `column` default, unitless numbers (density-independent pixels) and no CSS cascade.

Q3: How does navigation differ?
A3: Web navigation is URL-based (browser history, `<a>`, react-router, Next.js routes). RN has no URL bar: navigation is a stack of screens managed by React Navigation or Expo Router, although both can support deep links.

Q4: How do updates and releases differ?
A4: Web deploys instantly to all users. Native apps go through App Store and Play Store review. Expo EAS Update or CodePush-style OTA updates can ship JS-only changes, but changes in native code need a store release.

Q5: Can I share UI code between Next.js and React Native?
A5: Possible with `react-native-web` or Solito style setups, but most teams share hooks, types, validation and API clients, and keep platform UI separate. Full UI sharing trades some web-specific features (SEO semantics, CSS flexibility) for reuse.

---

## 🔷 When to Use + When Not to Use
✅ **Choose React Web (Next.js) when:**
- SEO, instant deploys and URL sharing matter (blogs, marketplaces, landing pages)
- You do not need device features like push notifications, camera, background tasks
- You want server rendering and Server Components

✅ **Choose React Native when:**
- You need an installed app, push notifications, camera, offline storage, app store presence
- Gestures and native look-and-feel are important

❌ **Avoid:**
- Forcing 100 percent UI sharing when the web and app designs differ a lot
- Choosing React Native only because "it is React", with no mobile requirement (a PWA may be enough)

---

## 📊 Visual Diagram

```
                 ┌──────────────── Shared ────────────────┐
                 │ hooks · reducers · Redux/Zustand · API  │
                 │ TanStack Query · validation · types     │
                 └──────────────┬──────────────┬──────────┘
                                │              │
                      ┌─────────▼───┐    ┌─────▼──────────┐
                      │ React Web   │    │ React Native   │
                      │ react-dom   │    │ RN renderer    │
                      │ div/span    │    │ View/Text      │
                      │ CSS         │    │ StyleSheet     │
                      │ URL routing │    │ Screen stack   │
                      │ localStorage│    │ AsyncStorage   │
                      └─────────────┘    └────────────────┘

 Re-render behavior: identical rules (state change → component re-renders → children re-render
 unless memoized). Only the final "apply to screen" step differs: DOM updates vs native view updates.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| react-dom | Renderer that outputs DOM | DOM बनाने वाला renderer |
| Native view | Real platform UI widget | असली platform UI widget |
| StyleSheet | RN style object helper | RN के style objects का helper |
| Flexbox column default | RN lays children top to bottom | RN में children ऊपर से नीचे लगते हैं |
| AsyncStorage | Async key-value storage in RN | RN का async key-value storage |
| React Navigation | Screen navigation library for RN | RN के लिए screen navigation library |
| react-native-web | Runs RN components on web | RN components को web पर चलाता है |
| OTA update | Over-the-air JS update | Store के बिना JS update |

---

## ⚡ 3-Line Summary
**English:**
1. React core (hooks, state, props, context) is shared; renderer, primitives, styling and platform APIs differ.
2. RN uses `View`/`Text`/`Pressable`, Flexbox column layout, screen-stack navigation and native storage.
3. Share logic, not markup: shared hooks and API layers with thin platform views.

**Hindi:**
1. React core (hooks, state, props, context) share होता है; renderer, primitives, styling और platform APIs अलग हैं।
2. RN में `View`/`Text`/`Pressable`, Flexbox column layout, screens का stack navigation और native storage होता है।
3. Logic share करो, markup नहीं: shared hooks व API layer और पतली platform-specific views।

---

## ➡️ Next Topic
**165. PWA with React** — अगर native app नहीं चाहिए, तो web app को installable, offline-capable और push-ready कैसे बनाएं, यह अगला सवाल है।
