# 181. Monorepo (RN + Web sharing code)
# हिंदी में: Monorepo (RN + Web के बीच Code Sharing)
# Platform: Android ✅ | iOS ✅ | Web ✅

> **Expo SDK 54 (React Native 0.81) target** — check current docs — APIs change between SDKs. Since Expo SDK 52, Metro monorepo support (workspaces) is auto-configured in new projects; older SDKs needed manual `metro.config.js` edits. Commands below are **not run** here.

---

## 🔵 Simple Definition (English)
A **monorepo** keeps several projects (mobile app, web app, shared UI library, shared API client) in **one Git repository** using workspaces (npm / yarn / pnpm) and often Turborepo or Nx. Shared packages are imported by both apps, so code is written once.

## 🔵 सरल परिभाषा (Hindi)
**Monorepo** में कई projects (mobile app, web app, shared UI library, shared API client) **एक Git repository** में रहते हैं — workspaces (npm / yarn / pnpm) और अक्सर Turborepo या Nx के साथ। Shared packages दोनों apps import करते हैं, इसलिए code एक बार लिखना पड़ता है।

---

## 🔴 Problem it Solves
```
❌ Separate repos for app and web: copy-paste components, versions drift
❌ A bug fix in the API client must be done in 2-3 repos
❌ Hard to test breaking changes across projects
✅ One repo: shared packages, one PR changes everything, one CI
```

## 🔴 यह क्यों बना? (Hindi)
```
❌ App और web के अलग repos: components copy-paste, versions अलग-अलग
❌ API client का bug 2-3 repos में ठीक करना
❌ Breaking changes सभी projects में test करना कठिन
✅ एक repo: shared packages, एक PR से सब बदलाव, एक CI
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → Root package.json declares "workspaces": ["apps/*", "packages/*"]
Step 2 → apps/mobile (Expo), apps/web (Next.js or Expo web), packages/ui, packages/api
Step 3 → Shared package has its own package.json with name "@acme/ui"
Step 4 → Apps depend on it: "@acme/ui": "*" (workspace link, symlinked in node_modules)
Step 5 → Metro must watch the shared folder (watchFolders) and resolve hoisted node_modules
Step 6 → Web bundler transpiles shared package (Next.js: transpilePackages) + alias react-native-web
Step 7 → Turborepo caches builds/tests: turbo run build lint test
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Root package.json में "workspaces": ["apps/*", "packages/*"]
Step 2 → apps/mobile (Expo), apps/web (Next.js या Expo web), packages/ui, packages/api
Step 3 → Shared package का अपना package.json, नाम "@acme/ui"
Step 4 → Apps उस पर depend करते हैं: "@acme/ui": "*" (workspace symlink)
Step 5 → Metro को shared folder देखना (watchFolders) और hoisted node_modules resolve करना
Step 6 → Web bundler shared package transpile करे (Next.js: transpilePackages) + react-native-web alias
Step 7 → Turborepo builds/tests cache करता है: turbo run build lint test
```

---

## 🟡 Real World Example
Teams like **Zomato/Swiggy** (consumer app + web + partner/restaurant app) can share a `design-system` package (buttons, colors, typography), a `api-client` package and `utils` across repos in one monorepo. **Solito** (open source) is a well-known pattern for sharing screens between Next.js and Expo apps.

## 🟡 Real Example Hindi mein
**Zomato/Swiggy** जैसी teams (consumer app + web + partner/restaurant app) एक monorepo में `design-system` package (buttons, colors, typography), `api-client` और `utils` share कर सकती हैं। **Solito** (open source) Next.js और Expo apps के बीच screens share करने का जाना-माना pattern है।

---

## 💻 Code Example — Basic
```json
{
  "name": "acme-monorepo",
  "private": true,
  "workspaces": ["apps/*", "packages/*"],
  "scripts": {
    "mobile": "npm run start --workspace=apps/mobile",
    "web": "npm run dev --workspace=apps/web"
  }
}
```
```
acme-monorepo/
├── package.json            <- workspaces config
├── apps/
│   ├── mobile/             <- Expo app (package.json: "@acme/ui": "*")
│   └── web/                <- Next.js app (uses react-native-web)
└── packages/
    ├── ui/                 <- shared components (View/Text based)
    │   ├── package.json    <- { "name": "@acme/ui", "main": "src/index.ts" }
    │   └── src/Button.tsx
    └── api/                <- shared fetch client + types
```
```tsx
// packages/ui/src/Button.tsx — shared component used by mobile AND web
import React from 'react';                                          // React
import { Pressable, Text, StyleSheet } from 'react-native';          // RN API (web: react-native-web)

type Props = { title: string; onPress: () => void };                  // typed props

export function Button({ title, onPress }: Props) {
  return (
    // Pressable works with touch (mobile) and click (web)
    <Pressable onPress={onPress} style={styles.btn} accessibilityRole="button">
      <Text style={styles.txt}>{title}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  btn: { backgroundColor: '#f97316', padding: 12, borderRadius: 8 }, // orange button
  txt: { color: '#fff', fontWeight: '700', textAlign: 'center' },    // white label
});
```

## 💻 Code Example — Advanced
```js
// apps/mobile/metro.config.js — manual monorepo setup (needed on SDK <= 51; auto on SDK 52+)
const { getDefaultConfig } = require('expo/metro-config');   // Expo's Metro defaults
const path = require('path');                                  // path helper

const projectRoot = __dirname;                                 // apps/mobile
const workspaceRoot = path.resolve(projectRoot, '../..');      // monorepo root

const config = getDefaultConfig(projectRoot);                  // base config

config.watchFolders = [workspaceRoot];                         // watch shared packages for changes
config.resolver.nodeModulesPaths = [                           // where to look for modules
  path.resolve(projectRoot, 'node_modules'),                   // app-level
  path.resolve(workspaceRoot, 'node_modules'),                 // hoisted root-level
];
config.resolver.disableHierarchicalLookup = true;              // use only the paths above (avoids duplicate React)

module.exports = config;                                       // export to Metro
```
```js
// apps/web/next.config.js — Next.js web app consuming the same shared package
/** @type {import('next').NextConfig} */
module.exports = {
  transpilePackages: ['@acme/ui', 'react-native', 'react-native-web'], // compile RN + shared code for web
  webpack: (config) => {
    config.resolve.alias = {
      ...(config.resolve.alias || {}),
      'react-native$': 'react-native-web',                      // swap RN for web implementation
    };
    config.resolve.extensions = ['.web.js', '.web.ts', '.web.tsx', ...config.resolve.extensions]; // prefer .web files
    return config;
  },
};
```
```jsonc
// turbo.json — Turborepo pipeline (key name is "tasks" in Turborepo 2.x, "pipeline" in 1.x)
{
  "$schema": "https://turbo.build/schema.json",
  "tasks": {
    "build": { "dependsOn": ["^build"], "outputs": [".next/**", "dist/**"] },
    "lint": {},
    "test": { "dependsOn": ["^build"] }
  }
}
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Autolinking in monorepo | Gradle reads root node_modules via `settings.gradle` | CocoaPods via Podfile `require_relative` path to node_modules |
| Common error | "Unable to resolve module" (Metro) | Pod not found because deps hoisted |
| Fix | `watchFolders`, `nodeModulesPaths` | Podfile paths / `expo-modules-autolinking` |
| Native deps | Declare in app, not only in shared pkg | Same |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
# SDK 52+: create app in a workspace; Metro auto-detects monorepo
npx create-expo-app apps/mobile
# install a shared package
npm install @acme/ui --workspace=apps/mobile
npx expo start        # Metro handles workspace config automatically (SDK 52+)
```
CLI way:
```bash
# RN CLI: configure metro.config.js with watchFolders + nodeModulesPaths by hand
npx @react-native-community/cli init Mobile --directory apps/mobile
# Android/iOS paths in settings.gradle & Podfile may need pointing to the ROOT node_modules
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Two copies of React in the tree
✅ Correct: Hoist single `react`/`react-native` version; use `resolutions`/`overrides` and `disableHierarchicalLookup`.

❌ Mistake 2: Putting native modules only in shared package dependencies
✅ Correct: Autolinking looks at the app's dependencies; add native libs to the app too.

❌ Mistake 3: Shared package ships untranspiled TS and web build fails
✅ Correct: Add it to `transpilePackages` (Next.js) or build it to `dist`.

---

## 🧠 Tricky Interview Question
**Q: "Invalid hook call" appears only after moving to a monorepo. Code is fine. Why?**

**Answer:** Two different copies of `react` are loaded (e.g., `apps/mobile/node_modules/react` and root `node_modules/react`), so hooks from one copy run with the renderer of the other. Fix: one version at the root, dedupe with overrides/resolutions, and configure Metro `nodeModulesPaths`/`disableHierarchicalLookup`.

---

## ⚫ Interview Questions + Answers

**Q1: What is a workspace?**
A1: A package manager feature that links local packages together and installs dependencies once.

**Q2: Why Turborepo/Nx?**
A2: Task orchestration and caching so only changed packages rebuild/test.

**Q3: Metro needs what for monorepos?**
A3: `watchFolders` for shared packages and resolver paths for hoisted modules (automatic in recent Expo SDKs).

**Q4: How do you share navigation between web and mobile?**
A4: Use Expo Router (file-based, works on web) or Solito + React Navigation/Next.js.

**Q5: Downsides?**
A5: Tooling complexity, bigger CI, dependency-hoisting issues, native build config.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Mobile + web + shared libs by one org
- You need atomic cross-project changes

❌ Avoid when:
- Single small app
- Teams with unrelated release cycles and no shared code

---

## 📊 Visual Diagram
```
        packages/ui  packages/api  packages/utils
              ▲           ▲            ▲
      ┌───────┴───────────┴────────────┴───────┐
      │                                        │
  apps/mobile (Expo/Metro)           apps/web (Next.js + RNW)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Monorepo | Many projects, one repo | कई projects, एक repo |
| Workspace | Linked local packages | Linked local packages |
| Hoisting | Install deps at root | Dependencies root पर install |
| watchFolders | Metro folders to watch | Metro जिन folders को देखे |
| Turborepo | Build orchestrator | Build orchestrator |
| Solito | Next.js + Expo navigation bridge | Next.js + Expo navigation bridge |

---

## ⚡ 3-Line Summary
**English:**
1. A monorepo holds mobile, web and shared packages in one repo with workspaces.
2. Configure Metro (watchFolders, nodeModulesPaths) and web bundler (transpilePackages, alias).
3. Keep one copy of React to avoid hook errors.

**Hindi:**
1. Monorepo में mobile, web और shared packages workspaces के साथ एक repo में रहते हैं।
2. Metro (watchFolders, nodeModulesPaths) और web bundler (transpilePackages, alias) configure करो।
3. React की एक ही copy रखो ताकि hook errors न आएँ।

---

## ➡️ Next Topic
**182. Micro Frontends in RN** — बड़े apps को अलग-अलग teams के independent modules में बाँटना।
