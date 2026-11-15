# 15. Project Structure — Complete Guide
# हिंदी में: Project Structure — पूरी जानकारी
# Platform: Android ✅ | iOS ✅ | Both ✅

> Target: Expo SDK 52 (default template) and React Native 0.76 CLI template. Expo SDK NN (check current docs — templates change between SDKs).

---

## 🔵 Simple Definition (English)
Project structure is the layout of files and folders in a React Native project: config files (`package.json`, `app.json`), JS/TS source, assets, and (for CLI or after prebuild) native `android/` and `ios/` folders. Knowing what each part does tells you where to change what.

## 🔵 सरल परिभाषा (Hindi)
Project structure एक React Native project में files और folders की बनावट है: config files (`package.json`, `app.json`), JS/TS source, assets, और (CLI या prebuild के बाद) native `android/` व `ios/` folders। हर हिस्से का काम जानने से पता चलता है कि कौन सा बदलाव कहाँ करना है।

---

## 🔴 Problem it Solves
```
❌ "Where do I put the app icon / permissions / API URL?"
❌ Editing generated native files that get overwritten
❌ Messy src with 100 files in one folder
❌ New teammates cannot find anything
```

## 🔴 यह क्यों बना? (Hindi)
```
❌ "App icon / permissions / API URL कहाँ रखें?"
❌ Generated native files बदल देना, जो overwrite हो जाती हैं
❌ एक ही folder में 100 files
❌ नए साथी को कुछ मिलता ही नहीं
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → Root config: package.json (deps + scripts), tsconfig.json,
         babel.config.js, metro.config.js

Step 2 → Expo: app.json / app.config.js = name, icon, splash, permissions,
         bundle IDs, plugins

Step 3 → Source code: app/ (expo-router) or App.tsx + src/

Step 4 → assets/ = images, fonts; loaded by require() or expo-font

Step 5 → android/ & ios/ = native projects (always in CLI; in Expo only
         after `npx expo prebuild`, and may be git-ignored)

Step 6 → node_modules/ = installed packages (never commit)

Step 7 → Build: Metro bundles JS; Gradle/Xcode bundle native + JS
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Root config: package.json (deps + scripts), tsconfig.json,
         babel.config.js, metro.config.js
Step 2 → Expo: app.json / app.config.js = नाम, icon, splash, permissions,
         bundle IDs, plugins
Step 3 → Source code: app/ (expo-router) या App.tsx + src/
Step 4 → assets/ = images, fonts; require() या expo-font से load
Step 5 → android/ और ios/ = native projects (CLI में हमेशा; Expo में
         `npx expo prebuild` के बाद, और git-ignore हो सकते हैं)
Step 6 → node_modules/ = installed packages (commit नहीं करते)
Step 7 → Build: Metro JS bundle बनाता है; Gradle/Xcode native + JS जोड़ते हैं
```

---

## 🟡 Real World Example
A team building a **Zomato-like** app uses folders like `src/screens`, `src/components`, `src/services/api.ts`, `src/store`, `src/hooks`. Restaurant cards live in `components/RestaurantCard.tsx`, the order API in `services/orderApi.ts`, so a new developer fixes a cart bug by opening `store/cartSlice.ts` straight away.

## 🟡 Real Example Hindi mein
**Zomato जैसा** app बनाने वाली team `src/screens`, `src/components`, `src/services/api.ts`, `src/store`, `src/hooks` जैसे folders रखती है। Restaurant cards `components/RestaurantCard.tsx` में, order API `services/orderApi.ts` में, इसलिए नया developer cart bug के लिए सीधे `store/cartSlice.ts` खोल लेता है।

---

## 💻 Code Example — Basic

```text
# Basic: default Expo SDK 52 template (create-expo-app) - what each item is
FoodApp/
├── app/                  # expo-router screens: file name = URL/route
│   ├── (tabs)/           # a tab group (folder in parentheses does not appear in URL)
│   │   ├── index.tsx     # Home tab
│   │   ├── explore.tsx   # Explore tab
│   │   └── _layout.tsx   # tab bar configuration
│   ├── _layout.tsx       # root layout (Stack, fonts, theme)
│   └── +not-found.tsx    # 404 screen
├── assets/               # images + fonts
├── components/           # reusable UI pieces
├── constants/            # colors, config values
├── hooks/                # custom hooks
├── scripts/              # reset-project.js (removes the demo code)
├── app.json              # Expo config (name, icon, plugins, bundle IDs)
├── package.json          # dependencies + scripts
├── tsconfig.json         # TypeScript settings
└── node_modules/         # installed packages (git-ignored)
```

## 💻 Code Example — Advanced

```jsx
// Advanced: a scalable src/ layout + path alias + app.config.js with env + platform config
//
// src/
//   components/RestaurantCard.tsx
//   screens/HomeScreen.tsx
//   services/api.ts
//   store/cartStore.ts
//   hooks/useDebounce.ts
//   utils/format.ts
//
// ---- app.config.js (dynamic Expo config; replaces app.json when present) ----
module.exports = ({ config }) => ({
  ...config, // keep values from app.json if it exists
  name: process.env.APP_ENV === 'prod' ? 'FoodApp' : 'FoodApp (Dev)', // display name per env
  slug: 'food-app', // unique project slug
  version: '1.0.0', // user-visible version
  orientation: 'portrait', // lock to portrait
  icon: './assets/icon.png', // app icon
  ios: {
    bundleIdentifier: 'com.example.foodapp', // iOS unique ID
    infoPlist: { NSCameraUsageDescription: 'Scan QR for table ordering' }, // iOS permission text
  },
  android: {
    package: 'com.example.foodapp', // Android applicationId
    permissions: ['CAMERA'], // Android permission
  },
  extra: { apiUrl: process.env.API_URL ?? 'https://api.example.com' }, // custom values read in JS
  plugins: ['expo-router'], // config plugins
});

// ---- Read the extra value in JS ----
// import Constants from 'expo-constants';
// const API_URL = Constants.expoConfig?.extra?.apiUrl;
//
// ---- tsconfig.json path alias (Expo template already has "@/*") ----
// { "compilerOptions": { "paths": { "@/*": ["./*"] } } }
// import Card from '@/components/RestaurantCard';
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Native folder | `android/` | `ios/` |
| Main config file | `AndroidManifest.xml`, `build.gradle` | `Info.plist`, `Podfile`, `.xcodeproj` |
| App ID | `package` / `applicationId` | `bundleIdentifier` |
| Permissions | `AndroidManifest.xml` / `android.permissions` | `Info.plist` usage strings (required text) |
| App icon location | `res/mipmap-*` | `Images.xcassets/AppIcon` |
| Lock file for native deps | Gradle files | `Podfile.lock` |

---

## 🟠 Expo vs CLI Difference
Expo way:
```text
# Expo (managed): no native folders until prebuild
MyApp/ app/  assets/  app.json  package.json  tsconfig.json
# Edit app.json/app.config.js; native folders generated by `npx expo prebuild`
```
CLI way:
```text
# CLI: native folders live in the repo
MyApp/ android/  ios/  App.tsx  index.js  app.json  babel.config.js
       metro.config.js  package.json  Gemfile  __tests__/
# Edit native files directly (AndroidManifest.xml, Info.plist)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Editing `android/` or `ios/` by hand in an Expo project that uses prebuild.
✅ Correct: use `app.json` or a config plugin; hand edits are lost when prebuild is re-run with `--clean`.

❌ Mistake 2: Committing `node_modules`, `.expo`, `Pods`.
✅ Correct: keep them in `.gitignore`.

❌ Mistake 3: Putting everything inside `App.tsx`.
✅ Correct: split into screens, components, services, hooks.

❌ Mistake 4: Hardcoding secrets in `app.json`.
✅ Correct: use env variables (`EXPO_PUBLIC_*` for public values) or EAS secrets; remember any value inside the app bundle can be read by users.

---

## 🧠 Tricky Interview Question
**Q:** "You changed the app name in `app.json`, reloaded the app, and the home-screen name did not change. Why?"

Answer: The launcher name is **native** config. A JS reload cannot change it. You need a new native build (`npx expo prebuild` + rebuild, or a new EAS build). Expo Go always shows "Expo Go".

---

## ⚫ Interview Questions + Answers
Q1: What is the role of `index.js` in a CLI project?
A1: It registers the root component with `AppRegistry.registerComponent`.

Q2: What does `app.json` hold in Expo?
A2: App name, slug, icon, splash, platform IDs, permissions, plugins, extra values.

Q3: Should `android/` and `ios/` be committed in an Expo project?
A3: Optional. With Continuous Native Generation they can be git-ignored and regenerated.

Q4: Where do babel and metro configs live?
A4: Root: `babel.config.js`, `metro.config.js`.

Q5: What is `.expo/`?
A5: Local Expo cache/state; do not commit it.

---

## 🔷 When to Use + When Not to Use
✅ Use a feature-based `src/` structure when:
- App has many screens and a team of 3+

❌ Avoid over-structure when:
- Tiny prototype: a few files are fine

---

## 📊 Visual Diagram
```
 package.json ─► deps ─► node_modules
 app.json ─────► prebuild ─► android/ + ios/
 app/ or src/ ─► Metro ─► JS bundle ─┐
 assets/ ───────────────────────────┤
 android/ (Gradle) ─► APK/AAB ◄─────┤
 ios/ (Xcode)      ─► IPA     ◄─────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| app.json | Expo app config | Expo की app config |
| expo-router | File-based routing | File के नाम से routing |
| Prebuild | Generate native folders | native folders बनाना |
| Config plugin | Edit native config via JS | JS से native config बदलना |
| node_modules | Installed packages | install हुए packages |
| Path alias | Short import path (`@/`) | छोटा import path |

---

## ⚡ 3-Line Summary
English: Config files, source, assets and native folders each have a job.
In Expo edit app.json; in CLI edit native files directly.
Organise src by feature to keep the app maintainable.

Hindi: Config files, source, assets और native folders का अपना-अपना काम है।
Expo में app.json बदलें; CLI में native files सीधे बदलें।
App को maintainable रखने के लिए src को feature के हिसाब से बाँटें।

---

## ➡️ Next Topic
**16. Running on Android Emulator** — run your project on the virtual Android device.

---
