# 19. Metro Bundler
# हिंदी में: Metro Bundler क्या है?
# Platform: Android ✅ | iOS ✅ | Both ✅

---

## 🔵 Simple Definition (English)
**Metro** is the JavaScript bundler for React Native (like Webpack/Vite for React.js). It takes all your JS/TS files, `require()`/`import` calls, and assets, and bundles them into a single `index.android.bundle` or `index.ios.bundle` file that the app loads. In development, Metro runs as a local server — it watches for changes and hot-reloads your app in milliseconds.

## 🔵 सरल परिभाषा (Hindi)
**Metro** React Native का JavaScript bundler है (जैसे React.js के लिए Webpack/Vite)। सभी JS/TS files, imports, और assets लेकर एक single bundle file बनाता है जो app load करती है। Development में Metro local server की तरह run होता है — changes watch करता है और milliseconds में hot-reload करता है।

---

## 🔴 Problem it Solves
```
PROBLEM: App can't load hundreds of separate JS files
  Your app has:
  - src/screens/Home.tsx
  - src/components/Button.tsx
  - node_modules/react/index.js (hundreds of files)
  - node_modules/react-native/Libraries/...

  The mobile app can't import files from the filesystem
  at runtime like Node.js can!

METRO SOLUTION:
  At BUILD time: combines ALL files into ONE bundle
  → index.android.bundle (everything the Android app needs)
  → index.ios.bundle (everything the iOS app needs)

IN DEVELOPMENT:
  Metro runs on your machine (localhost:8081)
  App connects to Metro and loads JS from it
  When you save a file: Metro re-bundles just that module
  → Fast Refresh: only re-renders changed components
```

## 🔴 यह क्यों बना? (Hindi)
```
Mobile app runtime पर filesystem से files import नहीं कर सकती।
Metro सब JS files को एक bundle में combine करता है।
Development में local server — file save होते ही hot reload।
```

---

## 🟢 How it Works — Step by Step

```
DEVELOPMENT MODE:
──────────────────────────────────────────────────────
  Step 1 → npx expo start (or npx react-native start)
            Metro server starts at localhost:8081

  Step 2 → App opens, connects to Metro via WebSocket

  Step 3 → Metro sends the JS bundle to the app
            App executes bundle → your screen appears

  Step 4 → You edit a file and save
            Metro detects the change (file watcher)

  Step 5 → Metro re-transforms just the changed module
            (NOT the whole bundle — only what changed)

  Step 6 → Metro sends the diff via WebSocket to app
            App applies Fast Refresh
            Only the changed component re-renders!

PRODUCTION MODE:
──────────────────────────────────────────────────────
  Step 1 → npm run build (or eas build)
            Metro runs in production mode

  Step 2 → Metro transforms all files:
            - TypeScript → JavaScript (via Babel)
            - JSX → React.createElement()
            - ES modules → CommonJS (require)

  Step 3 → Metro minifies + tree-shakes
            Removes dead code, shortens variable names

  Step 4 → Metro outputs:
            - index.android.bundle (or index.ios.bundle)
            - Source maps (.map files for debugging)

  Step 5 → Bundle is embedded in APK/IPA

METRO TRANSFORMER (Babel):
──────────────────────────────────────────────────────
  Your TSX file:
    const greeting: string = "Hello";
    const el = <Text>{greeting}</Text>;

  After Metro (Babel transform):
    var greeting = "Hello";
    var el = React.createElement(Text, null, greeting);
```

## 🟢 कैसे काम करता है? (Hindi)
```
Dev: Metro server (8081) → App connect → Bundle serve → Fast Refresh
Prod: TypeScript → Babel → minify → single bundle → APK/IPA में embed
```

---

## 🟡 Real World Example
**Paytm development team:** 50 developers each working on different screens. Each dev runs Metro on their machine. When they save a payment component change, Metro hot-reloads only that component — the rest of the app stays intact. Without Metro: every change = full app rebuild = minutes of wait. With Metro: change → visible on device in ~300ms. This is why "Fast Refresh" is one of React Native's most loved developer experience features.

## 🟡 Real Example Hindi मे
**Paytm dev team:** 50 developers, सब अलग screens पर। File save → Metro detect → Component hot-reload → 300ms में device पर दिखे। Metro के बिना: हर change = full rebuild = minutes waste। Metro = developer productivity का backbone।

---

## 💻 Code Example — Basic

```bash
# Metro starts automatically when you run your app
npx expo start              # Expo: starts Metro + Expo dev server
npx react-native start      # CLI: starts Metro on port 8081

# Metro output in terminal:
# ▲ Metro waiting on exp://192.168.1.5:19000
# › Press a │ open Android
# › Press i │ open iOS simulator
# › Press w │ open web

# Custom Metro port (if 8081 is taken):
npx react-native start --port 8082
npx expo start --port 8082
```

```jsx
// metro.config.js — Metro configuration file
// Exists in project root, created by default

const { getDefaultConfig } = require('expo/metro-config');
// or for CLI: const { getDefaultConfig } = require('@react-native/metro-config');

const config = getDefaultConfig(__dirname);

// Add support for additional file extensions
config.resolver.assetExts.push(
  'bin',    // binary files
  'txt',    // text files
  'csv',    // CSV data files
);

// Add SVG transformer support
config.transformer.babelTransformerPath = require.resolve('react-native-svg-transformer');
config.resolver.assetExts = config.resolver.assetExts.filter(ext => ext !== 'svg');
config.resolver.sourceExts.push('svg');

module.exports = config;
```

## 💻 Code Example — Advanced

```bash
# Common Metro tasks:

# Clear Metro cache (when you get weird errors)
npx expo start --clear
npx react-native start --reset-cache

# Build production bundle manually
npx react-native bundle \
  --platform android \
  --dev false \
  --entry-file index.js \
  --bundle-output android/app/src/main/assets/index.android.bundle \
  --assets-dest android/app/src/main/res

# Check bundle size (important for performance!)
npx react-native bundle \
  --platform android \
  --dev false \
  --entry-file index.js \
  --bundle-output /tmp/bundle.js \
  --minify true

# Then analyze: how big is the bundle?
ls -lh /tmp/bundle.js
# Good: < 5MB
# Warning: 5-10MB
# Problem: > 10MB (users on slow data see slow download)

# Source map for debugging crashes
npx react-native bundle \
  --platform android \
  --dev false \
  --entry-file index.js \
  --bundle-output /tmp/bundle.js \
  --sourcemap-output /tmp/bundle.js.map
```

```javascript
// metro.config.js — Advanced: Adding module aliases
const { getDefaultConfig } = require('expo/metro-config');
const path = require('path');

const config = getDefaultConfig(__dirname);

// Module aliases: '@components' → 'src/components'
// So you can write: import Button from '@components/Button'
// instead of: import Button from '../../components/Button'
config.resolver.extraNodeModules = {
  '@components': path.resolve(__dirname, 'src/components'),
  '@screens': path.resolve(__dirname, 'src/screens'),
  '@utils': path.resolve(__dirname, 'src/utils'),
  '@hooks': path.resolve(__dirname, 'src/hooks'),
  '@assets': path.resolve(__dirname, 'assets'),
};

module.exports = config;
// Also needs tsconfig.json "paths" for TypeScript to understand aliases!
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Bundle file | `index.android.bundle` | `index.ios.bundle` |
| Bundle location in APK | `assets/` folder in APK | Embedded in IPA |
| Bundle fetched from | `localhost:8081` (dev) | `localhost:8081` (dev) |
| Hot reload connection | Metro WebSocket | Metro WebSocket |

---

## 🟠 Expo vs CLI Difference

Expo way:
```bash
# Expo wraps Metro with extra features
npx expo start

# Expo Go loads bundle from Metro
# Expo Dev Build also uses Metro
# EAS Build runs Metro in cloud during build
```

CLI way:
```bash
# Direct Metro control
npx react-native start

# Manual bundle for production
npx react-native bundle --platform android --dev false ...
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Not clearing Metro cache when facing weird bugs
```bash
# WRONG: Debugging a weird "module not found" for 2 hours
# CORRECT: First thing to try:
npx expo start --clear
# or
npx react-native start --reset-cache

# Metro caches transformed files — stale cache = mystery bugs!
# Clear cache FIRST before debugging transformation issues.
```

❌ **Mistake 2:** Large bundle size ignoring performance impact
```bash
# Check your bundle size in CI:
# > 5MB = users on 4G wait extra seconds to update
# > 10MB = problem — remove unused libraries!

# Common bundle-bloating culprits:
# ❌ moment.js (500KB!) → replace with date-fns or dayjs
# ❌ lodash (full import) → use lodash/get instead
# ❌ unused icon packs (all icons loaded even if only 5 used)
# ❌ Large JSON files imported → load lazily from API instead

// WRONG: Imports ALL of lodash
import _ from 'lodash';

// CORRECT: Only import what you need
import get from 'lodash/get';
import debounce from 'lodash/debounce';
```

❌ **Mistake 3:** Relying on Fast Refresh for all testing (test on real device!)
```
Fast Refresh is great for quick iteration BUT:
- Behavior on device may differ from Metro hot-reload state
- Particularly for: animations, gestures, background/foreground
- Always test a cold start (kill app, reopen) before release
- Test debug build AND release build (different optimization levels)
```

---

## 🧠 Tricky Interview Question

**Q: Metro bundler shows a "require cycle" warning. What is it, and is it a problem?**

**Answer:** A require cycle (circular dependency) is when module A imports module B, and module B (directly or indirectly) imports module A. Example: `Home.tsx` imports `UserContext` which imports a hook from `Home.tsx`. Metro warns about this because in JavaScript modules, when a cycle is detected during initialization, the first time a module is accessed in the cycle it may be `undefined` — leading to subtle bugs that are hard to find. Solution: (1) Break the cycle by extracting shared code into a third module. (2) If the cycle is safe (both modules only use the import AFTER initialization, not at module-level), the warning can be suppressed. For production apps, treat all cycle warnings seriously — they often indicate architectural issues that cause random `undefined is not a function` crashes.

---

## ⚫ Interview Questions + Answers

**Q1: What is Metro bundler and what does it do?**
A1: Metro is the JavaScript bundler for React Native, built by Meta. In development: it runs as a local server (port 8081), watches for file changes, transforms (TypeScript → JS, JSX → createElement), and serves the bundle to the app via WebSocket — enabling Fast Refresh. In production: it transforms, minifies, and tree-shakes all files into a single `index.android.bundle` / `index.ios.bundle` file that's embedded in the APK/IPA.

**Q2: What is Fast Refresh in React Native?**
A2: Fast Refresh is Metro's hot-reload mechanism. When you save a file: Metro re-transforms only the changed module (not the whole bundle), sends the update via WebSocket to the running app, and React applies the change by re-rendering only the affected components — while preserving state in parent components. It's faster and more precise than the old "Hot Reloading" (which had issues with class components and hooks). Works with function components, hooks, and most modern React Native patterns.

**Q3: What does `npx expo start --clear` (or `--reset-cache`) do?**
A3: It clears Metro's transformation cache. Metro caches the result of Babel transforming each file, so subsequent starts are faster. When the cache is stale (e.g., after upgrading a library, changing babel config, or after weird unexplained errors), cleared cache forces Metro to re-transform everything from scratch. This fixes about 40% of "mysterious" Metro errors. Always try cache clear before deep debugging.

**Q4: How is Metro different from Webpack (used in React.js)?**
A4: Both are JavaScript bundlers, but tuned for different environments. Metro: optimized for React Native's mobile development workflow — Fast Refresh, source maps for mobile debugging, handles Hermes bytecode, watches native file extensions (.native.js, .android.js, .ios.js). Webpack: optimized for web — code splitting, tree shaking for web, CSS imports, browser compatibility. Conceptually similar but different plugins, configuration, and features. Vite (another web bundler) is to Webpack as Metro is to... nothing directly comparable yet in RN.

**Q5: What are platform-specific file extensions in Metro?**
A5: Metro supports platform-specific file resolution. If you have:
```
Button.tsx           — default
Button.android.tsx   — Android-only
Button.ios.tsx       — iOS-only
Button.native.tsx    — both Android + iOS (vs web)
```
Metro automatically picks the right file based on the target platform. `Button.android.tsx` loads on Android, `Button.ios.tsx` on iOS, falling back to `Button.tsx` if no platform file exists. This lets you have different native implementations with the same import: `import Button from './Button'` — Metro resolves the right one.

---

## 🔷 When to Use + When Not to Use
✅ **Metro features to USE:**
- `metro.config.js` for aliases (cleaner imports)
- Platform-specific files (`.android.js`, `.ios.js`)
- Cache clear when hitting weird transform errors
- Source maps for production crash debugging

❌ **Metro things to AVOID:**
- Circular dependencies (require cycles)
- Large bundles (check with `du -sh bundle.js`)
- Importing full libraries (import entire lodash, moment)

---

## 📊 Visual Diagram

```
METRO IN DEVELOPMENT MODE:
──────────────────────────────────────────────────────
  Your Machine:                     Phone/Emulator:
  ┌──────────────────────┐          ┌──────────────────┐
  │  Metro Server        │          │  Your App        │
  │  localhost:8081      │◄────────►│                  │
  │                      │ WebSocket│  Hermes Engine   │
  │  Watches files       │          │  executes bundle │
  │  Transforms JSX/TS   │          │                  │
  │  Sends updates       │─────────►│  Fast Refresh!   │
  └──────────────────────┘          └──────────────────┘

METRO IN PRODUCTION:
──────────────────────────────────────────────────────
  All your JS files
       │
       ▼
  Metro Transformer (Babel)
  → TypeScript → JS
  → JSX → createElement()
  → ES Modules → CommonJS
       │
       ▼
  Metro Bundler
  → Resolves all imports
  → Combines into ONE file
  → Minifies (removes whitespace, shortens names)
  → Tree shakes (removes unused exports)
       │
       ▼
  index.android.bundle (or .ios.bundle)
  + source maps for crash debugging
       │
       ▼
  Embedded in APK / IPA → App Store / Play Store
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Metro | RN's JavaScript bundler | RN का JS bundler |
| Bundle | All JS combined into one file | सब JS एक file में |
| Fast Refresh | Hot-reload that preserves state | State preserve करते हुए hot-reload |
| Transform | Convert TS/JSX to plain JS | TS/JSX को plain JS में convert |
| Tree shaking | Remove unused code from bundle | Unused code remove |
| Source map | Map between bundle and original code | Bundle और original code का map |
| Require cycle | Circular dependency between modules | Modules के बीच circular dependency |
| metro.config.js | Metro configuration file | Metro का config file |

---

## ⚡ 3-Line Summary
**English:**
1. Metro is React Native's bundler — in development it's a local server enabling Fast Refresh; in production it outputs a minified single bundle embedded in the APK/IPA.
2. Metro transforms TypeScript → JS, JSX → createElement, resolves imports, and applies Babel plugins — it's the compilation step before native code touches your JS.
3. Common troubleshooting: `--clear` / `--reset-cache` for weird errors, check bundle size for performance, and never ignore require cycle warnings.

**Hindi:**
1. Metro React Native का bundler है — dev में local server (Fast Refresh), production में minified single bundle (APK/IPA में embed)।
2. TypeScript → JS, JSX → createElement transform करता है, imports resolve करता है — यह native code से पहले का compilation step है।
3. Common fix: `--clear` weird errors के लिए; bundle size check करो; require cycle warnings ignore मत करो।

---

## ➡️ Next Topic
**20. Hot Reload vs Fast Refresh** — दोनों में क्या फर्क है, Fast Refresh कैसे state preserve करता है।
