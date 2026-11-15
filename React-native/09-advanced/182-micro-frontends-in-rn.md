# 182. Micro Frontends in RN
# हिंदी में: React Native में Micro Frontends
# Platform: Android ✅ | iOS ✅ | Both ✅

> **Expo SDK 54 (React Native 0.81) target** — check current docs — APIs change between SDKs. Runtime module loading uses **Re.Pack** (webpack/Rspack-based bundler by Callstack) with **Module Federation**; Re.Pack replaces Metro, so it needs a bare / prebuild project (not Expo Go). Config API names below are version-dependent and **not run** here.

---

## 🔵 Simple Definition (English)
**Micro frontends** split a big app into small independent mini-apps (features) owned by different teams, each built and deployed separately and loaded into a **host app** at runtime. In RN, this is done with **Re.Pack + Module Federation** (or simpler: package-level modularization).

## 🔵 सरल परिभाषा (Hindi)
**Micro frontends** एक बड़े app को छोटे स्वतंत्र mini-apps (features) में बाँटते हैं, जिन्हें अलग teams संभालती हैं, अलग build/deploy करती हैं और **host app** में runtime पर load होते हैं। RN में यह **Re.Pack + Module Federation** से होता है (या आसान तरीका: package-level modularization)।

---

## 🔴 Problem it Solves
```
❌ One giant bundle: 100 developers, merge conflicts, slow CI
❌ One team's bug blocks the entire app release
❌ App store review needed for every small feature change
❌ Hard to scale teams independently
✅ Each mini-app deploys independently; host loads latest bundle at runtime
```

## 🔴 यह क्यों बना? (Hindi)
```
❌ एक विशाल bundle: 100 developers, merge conflicts, धीमा CI
❌ एक team का bug पूरे app की release रोक देता है
❌ हर छोटे feature पर App Store review
❌ Teams को स्वतंत्र रूप से scale करना कठिन
✅ हर mini-app अलग deploy; host runtime पर नया bundle load करता है
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → Host app (shell): navigation, auth, shared deps (react, react-native)
Step 2 → Each mini-app (remote) is built as a separate JS bundle (federated module)
Step 3 → Remotes expose screens: exposes: { './CheckoutScreen': './src/Checkout' }
Step 4 → Host registers remotes (name -> URL of remoteEntry bundle)
Step 5 → At runtime ScriptManager downloads the remote's bundle (cached)
Step 6 → Host lazy-imports: React.lazy(() => import('checkout/CheckoutScreen'))
Step 7 → Shared singletons (react, react-native) avoid duplicates; version rules in config
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Host app (shell): navigation, auth, shared deps (react, react-native)
Step 2 → हर mini-app (remote) अलग JS bundle (federated module) की तरह build
Step 3 → Remote screens expose करता है: exposes: { './CheckoutScreen': './src/Checkout' }
Step 4 → Host remotes register करता है (name -> remoteEntry bundle का URL)
Step 5 → Runtime पर ScriptManager remote का bundle download करता है (cache)
Step 6 → Host lazy-import करता है: React.lazy(() => import('checkout/CheckoutScreen'))
Step 7 → Shared singletons (react, react-native) duplicates रोकते हैं
```

---

## 🟡 Real World Example
**Super-apps** like **Paytm, PhonePe, Tata Neu** host many "mini-apps" (recharge, flights, insurance, bill pay) built by separate teams. **Zomato** could ship "District" and "Food Delivery" as independent modules inside one host. Federation lets the insurance team release a fix without waiting for the whole app release (within store policy: JS-only updates).

## 🟡 Real Example Hindi mein
**Paytm, PhonePe, Tata Neu** जैसे **super-apps** में कई "mini-apps" (recharge, flights, insurance, bill pay) अलग teams बनाती हैं। **Zomato** "District" और "Food Delivery" को एक host में स्वतंत्र modules की तरह रख सकता है। Federation से insurance team पूरे app release का इंतज़ार किए बिना fix भेज सकती है (store policy के भीतर: सिर्फ JS updates)।

---

## 💻 Code Example — Basic
```js
// A simple, SAFE first step: "feature modules" inside one repo (no runtime loading)
// features/checkout/index.js — a feature exposes ONE public entry
export { default as CheckoutScreen } from './CheckoutScreen'; // screen component
export { checkoutReducer } from './state';                     // its state slice
export const checkoutRoutes = [{ name: 'Checkout', component: null }]; // placeholder metadata

// app/registry.js — the host registers features instead of importing internals
import { CheckoutScreen } from '../features/checkout';    // only public API allowed
import { RechargeScreen } from '../features/recharge';    // another team's feature

export const FEATURES = [
  { name: 'Checkout', screen: CheckoutScreen },            // feature 1
  { name: 'Recharge', screen: RechargeScreen },            // feature 2
];
// Navigation renders FEATURES.map(...) — adding a feature = adding one line
```

## 💻 Code Example — Advanced
```js
// webpack.config.mjs of the HOST (Re.Pack). Names follow Re.Pack docs; verify your version.
import path from 'node:path';
import * as Repack from '@callstack/repack';

export default (env) => {
  const { mode, platform } = env;                            // dev/prod and android/ios
  return {
    mode,
    context: path.resolve('.'),
    entry: './index.js',
    resolve: { ...Repack.getResolveOptions(platform) },       // RN-aware resolution
    module: { rules: [...Repack.getJsTransformRules()] },     // Babel etc.
    plugins: [
      new Repack.RepackPlugin({ platform }),                  // core plugin
      new Repack.plugins.ModuleFederationPluginV2({           // Module Federation (v2 plugin)
        name: 'host',                                         // this container's name
        remotes: {
          // name@URL -> where remote's manifest/entry is served
          checkout: `checkout@http://localhost:9001/${platform}/mf-manifest.json`,
        },
        shared: {
          react: { singleton: true, eager: true },            // exactly ONE React
          'react-native': { singleton: true, eager: true },   // exactly ONE RN
        },
      }),
    ],
  };
};
```
```jsx
// Host runtime: tell ScriptManager where to download federated bundles, then lazy-load a remote screen
import React, { Suspense } from 'react';
import { ActivityIndicator, Text, View } from 'react-native';
import { ScriptManager, Script } from '@callstack/repack/client';

// Resolver: called when a remote script is needed
ScriptManager.shared.addResolver(async (scriptId, caller) => {
  if (scriptId === 'checkout') {
    return { url: Script.getRemoteURL('http://localhost:9001/checkout.container.bundle') }; // dev URL; use CDN in prod
  }
  return undefined;                                         // let other resolvers handle it
});

// Lazy import of the remote screen (module name 'checkout/CheckoutScreen' from exposes)
const CheckoutScreen = React.lazy(() => import('checkout/CheckoutScreen'));

// Simple error boundary: a broken remote must not crash the host app
class RemoteBoundary extends React.Component {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; } // switch to fallback UI
  render() {
    return this.state.failed
      ? <View style={{ padding: 24 }}><Text>Checkout is unavailable. Try again later.</Text></View>
      : this.props.children;
  }
}

export default function CheckoutRoute() {
  return (
    <RemoteBoundary>
      <Suspense fallback={<ActivityIndicator style={{ marginTop: 80 }} />}>
        <CheckoutScreen />
      </Suspense>
    </RemoteBoundary>
  );
}
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Remote bundle platform | `android` bundle (separate build) | `ios` bundle (separate build) |
| Store policy on downloaded JS | Allowed (Play policy: no changing app's primary purpose) | Allowed for interpreted JS but must not change the app's primary purpose (App Store guidelines 3.3.2) |
| Caching | App files directory | App sandbox |
| Native code in remotes | Not allowed (JS only) | Not allowed (JS only) |
| Cleartext HTTP (dev) | Needs `usesCleartextTraffic` for http | ATS exception needed for http |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
# Re.Pack replaces Metro, so Expo Go is NOT usable. Options:
# 1) Stay on Expo + Metro and use feature modules/monorepo packages (Code Example Basic)
# 2) Use EAS Update for JS-only OTA updates of the whole app
npx expo install expo-updates && eas update --branch production
```
CLI way:
```bash
# Bare RN + Re.Pack (Module Federation). Follow Re.Pack "getting started" for your RN version.
npm install --save-dev @callstack/repack webpack
npx react-native start        # Re.Pack dev server replaces Metro after setup
npx react-native run-android
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Duplicate React/RN in host and remote
✅ Correct: Declare `singleton: true` for `react` and `react-native` in `shared`.

❌ Mistake 2: Remote needs a native module that host lacks
✅ Correct: Remotes are JS-only; every native dependency must already be in the host binary.

❌ Mistake 3: No fallback when remote fails to load
✅ Correct: Wrap in error boundary + Suspense; set timeouts and retries.

---

## 🧠 Tricky Interview Question
**Q: A remote mini-app uses a new native library (e.g., a new camera SDK). Can you ship it by just deploying the remote bundle?**

**Answer:** No. Module Federation delivers **JavaScript only**. The native code must be in the host app binary (installed from the store). So you must release a new host build first; after that, remotes can use the library through JS.

---

## ⚫ Interview Questions + Answers

**Q1: What is a host and a remote?**
A1: Host = shell app that loads others; remote = independently built mini-app exposing modules.

**Q2: Why `singleton` shared deps?**
A2: Two React copies break hooks and context.

**Q3: Alternatives to Module Federation?**
A3: Monorepo with feature packages, OTA updates (EAS Update/CodePush-style), or native "brownfield" modules.

**Q4: Does Metro support Module Federation?**
A4: Not natively; Re.Pack (webpack/Rspack) does.

**Q5: Biggest risks?**
A5: Version compatibility, security of remote URLs, startup latency, harder debugging, store policy.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Super-app with many independent teams
- Need independent deploy cycles for features

❌ Avoid when:
- Small team/app (complexity not worth it)
- You rely on Expo Go / managed workflow

---

## 📊 Visual Diagram
```
                 HOST APP (shell)
        auth · navigation · react · react-native
          │            │             │
   fetch bundle   fetch bundle   fetch bundle
          ▼            ▼             ▼
   [Checkout]      [Recharge]    [Insurance]
   remote (JS)     remote (JS)   remote (JS)
   Team A          Team B        Team C
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Host | Shell app | मुख्य shell app |
| Remote | Loaded mini-app | Runtime पर load होने वाला mini-app |
| Module Federation | Share/load modules at runtime | Runtime पर modules share/load |
| Re.Pack | Webpack/Rspack bundler for RN | RN के लिए webpack/Rspack bundler |
| ScriptManager | Loads remote scripts | Remote scripts load करने वाला |
| Singleton | Only one instance | केवल एक instance |

---

## ⚡ 3-Line Summary
**English:**
1. Micro frontends split a big app into independently built and deployed mini-apps.
2. In RN use Re.Pack + Module Federation; remotes are JS-only and share singletons.
3. Add error boundaries; native code still needs a host app release.

**Hindi:**
1. Micro frontends बड़े app को स्वतंत्र रूप से build/deploy होने वाले mini-apps में बाँटते हैं।
2. RN में Re.Pack + Module Federation; remotes सिर्फ JS होते हैं और singletons share करते हैं।
3. Error boundary लगाओ; native code के लिए host app की नई release चाहिए।

---

## ➡️ Next Topic
**183+** — अगला advanced topic (How.md की list देखें)।
