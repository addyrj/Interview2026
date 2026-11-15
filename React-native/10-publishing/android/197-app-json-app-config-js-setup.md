# 197. app.json + app.config.js Setup
# हिंदी में: app.json और app.config.js की Setup
# Platform: Both ✅ (Android ✅ | iOS ✅) — यह note Android publishing पर केंद्रित

> Expo SDK 52 (check current docs — APIs change between SDKs). सिर्फ Expo projects में लागू (CLI में `AndroidManifest.xml`/`build.gradle`)। Keys जैसे `android.package`, `android.versionCode`, `android.permissions`, `plugins`, `extra` असली Expo config keys हैं; नए SDK में कुछ बदल सकते हैं।

---

## 🔵 Simple Definition (English)
In Expo, **app.json** (static) or **app.config.js / app.config.ts** (dynamic) is the single config for your app: name, slug, version, icons, splash, Android package name, permissions, plugins. `app.config.js` is JavaScript, so it can read environment variables and create different configs for dev, staging and production.

## 🔵 सरल परिभाषा (Hindi)
Expo में **app.json** (static) या **app.config.js / app.config.ts** (dynamic) आपके app की एकमात्र config है: name, slug, version, icons, splash, Android package name, permissions, plugins। `app.config.js` JavaScript है, इसलिए environment variables पढ़कर dev, staging और production के लिए अलग config बना सकता है।

---

## 🔴 Problem it Solves
```
❌ Android/iOS native files (AndroidManifest.xml, Info.plist, gradle) हाथ से बदलना
❌ Dev/staging/prod के लिए अलग package name/app name/API URL
❌ गलत package name (बाद में बदल नहीं सकते Play पर)
Expo config:
  ✅ एक जगह सारी settings
  ✅ prebuild/EAS इसे native में बदल देते हैं
  ✅ app.config.js से env-based variants
```

## 🔴 यह क्यों बना? (Hindi)
```
Native files हर platform में अलग और जटिल हैं।
Expo एक config से दोनों platform बनाता है।
Dynamic config से एक codebase, कई environments।
```

---

## 🟢 How it Works — Step by Step
```
Step 1 → app.json में "expo": { name, slug, version, android: { package, versionCode } }
Step 2 → icon (1024x1024 PNG), adaptive icon (foreground + backgroundColor), splash सेट
Step 3 → Permissions: android.permissions में सिर्फ ज़रूरी
Step 4 → Plugins: config plugins (expo-camera, expo-build-properties आदि)
Step 5 → app.config.js बनाओ → app.json को import करके override (config पैरामीटर)
Step 6 → env var APP_VARIANT=production से अलग name/package
Step 7 → eas.json के build profile में "env": { "APP_VARIANT": "production" }
Step 8 → npx expo config --type public → final resolved config देखो
Step 9 → EAS Build/prebuild native project बनाता है
```

## 🟢 कैसे काम करता है? (Hindi)
```
Expo CLI app.config.js चलाकर final JSON config निकालता है।
Prebuild/EAS उसे native project (manifest, gradle) में बदलता है।
इसलिए config बदली तो नया native build चाहिए (OTA से package/permissions नहीं बदलते)।
```

---

## 🟡 Real World Example
**Swiggy-जैसी टीम:** तीन variants — `com.example.swiggy.dev` ("Swiggy Dev", नीला icon), `...staging` और `com.example.swiggy` ("Swiggy"). एक phone में तीनों install। Production config में Google Maps API key अलग, Dev में अलग। यह सब `app.config.js` में `APP_VARIANT` से तय होता है।

## 🟡 Real Example Hindi mein
Dev, staging और prod तीनों अलग package name से एक ही phone में install; icon/नाम/API keys `APP_VARIANT` से बदलते हैं।

---

## 💻 Code Example — Basic
```json
{
  "expo": {
    "name": "My Shop",
    "slug": "my-shop",
    "version": "1.0.0",
    "orientation": "portrait",
    "icon": "./assets/icon.png",
    "userInterfaceStyle": "automatic",
    "splash": { "image": "./assets/splash.png", "resizeMode": "contain", "backgroundColor": "#ffffff" },
    "android": {
      "package": "com.example.myshop",
      "versionCode": 1,
      "adaptiveIcon": {
        "foregroundImage": "./assets/adaptive-icon.png",
        "backgroundColor": "#ffffff"
      },
      "permissions": ["ACCESS_FINE_LOCATION", "CAMERA"]
    },
    "ios": { "bundleIdentifier": "com.example.myshop", "buildNumber": "1" },
    "plugins": ["expo-router"]
  }
}
```
```
Notes (JSON में comments नहीं होते, इसलिए यहाँ):
- name: home screen पर दिखने वाला नाम | slug: URL-friendly id
- android.package: Play पर permanent ID (reverse-domain) — publish के बाद बदल नहीं सकते
- versionCode: integer, हर Play upload पर बढ़ाओ | version: user को दिखने वाला
- permissions: सिर्फ ज़रूरी; ज्यादा permissions = review/users का भरोसा कम
- adaptiveIcon: Android 8+ shapes (गोल/चौकोन) के लिए foreground + background
```

## 💻 Code Example — Advanced
```js
// ---------- app.config.js — dynamic, env-based variants ----------
// app.json भी रखा हो तो वह `config` में आता है और हम उसे extend करते हैं
const IS_DEV = process.env.APP_VARIANT === 'development';      // dev variant?
const IS_STAGING = process.env.APP_VARIANT === 'staging';      // staging variant?

// Helper: variant के हिसाब से value चुनो
const pick = (dev, staging, prod) => (IS_DEV ? dev : IS_STAGING ? staging : prod);

module.exports = ({ config }) => ({
  ...config,                                                   // app.json की settings रखो
  name: pick('Shop (Dev)', 'Shop (Staging)', 'My Shop'),       // अलग नाम
  slug: 'my-shop',                                             // slug एक ही रखो (EAS project)
  version: '1.2.0',                                            // user-visible version
  android: {
    ...config.android,
    package: pick('com.example.myshop.dev', 'com.example.myshop.staging', 'com.example.myshop'),
    // versionCode: remote version source (eas.json appVersionSource: "remote") हो तो EAS संभालता है;
    // वरना यहाँ manual:
    versionCode: 12,
    adaptiveIcon: {
      foregroundImage: pick('./assets/icon-dev.png', './assets/icon-staging.png', './assets/adaptive-icon.png'),
      backgroundColor: '#ffffff',
    },
    permissions: ['ACCESS_FINE_LOCATION'],                     // minimal
    // Google Maps API key (secret नहीं, पर Cloud Console में package+SHA से restrict करो)
    config: { googleMaps: { apiKey: process.env.GOOGLE_MAPS_KEY } },
  },
  plugins: [
    ...(config.plugins ?? []),                                 // existing plugins
    ['expo-build-properties', { android: { compileSdkVersion: 34, targetSdkVersion: 34 } }],
    // SDK के अनुसार values बदलती हैं — SDK docs में recommended देखो
  ],
  extra: {                                                     // runtime में Constants.expoConfig.extra
    apiUrl: pick('https://dev.api.example.com', 'https://staging.api.example.com', 'https://api.example.com'),
    eas: { projectId: 'YOUR-EAS-PROJECT-ID' },                 // eas init से मिलता है
  },
});

// App में पढ़ना:
//   import Constants from 'expo-constants';
//   const apiUrl = Constants.expoConfig.extra.apiUrl;
// ध्यान: secrets (private keys) extra में मत डालो — यह app bundle में public होता है।
// Check: APP_VARIANT=production npx expo config --type public   (not run here)
```
```jsonc
// ---------- eas.json में variant env ----------
{
  "build": {
    "development": { "developmentClient": true, "env": { "APP_VARIANT": "development" } },
    "preview":     { "distribution": "internal", "env": { "APP_VARIANT": "staging" } },
    "production":  { "env": { "APP_VARIANT": "production" } }
  }
}
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Unique ID | `android.package` | `ios.bundleIdentifier` |
| Build number | `android.versionCode` (integer) | `ios.buildNumber` (string) |
| Permissions | `android.permissions` (manifest) | `ios.infoPlist` usage descriptions (NSCameraUsageDescription...) |
| Icon | adaptiveIcon (foreground/background) | single 1024x1024 icon |
| Maps key | `android.config.googleMaps.apiKey` | `ios.config.googleMapsApiKey` |
| Deep links | `android.intentFilters` | `ios.associatedDomains` |

---

## 🟠 Expo vs CLI Difference
Expo way:
```js
// app.config.js / app.json — सब यहाँ
// android.package, versionCode, permissions → prebuild से AndroidManifest/gradle में
```
CLI way:
```xml
<!-- android/app/src/main/AndroidManifest.xml (permissions) -->
<uses-permission android:name="android.permission.CAMERA" />
<!-- android/app/build.gradle -->
<!-- defaultConfig { applicationId "com.example.myshop"; versionCode 1; versionName "1.0.0" } -->
<!-- App name: android/app/src/main/res/values/strings.xml → <string name="app_name">My Shop</string> -->
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: package name बाद में बदलना ("com.test.app" छोड़ देना)
✅ Correct: शुरू में final reverse-domain, publish के बाद बदल नहीं सकते

❌ Mistake 2: `versionCode` नहीं बढ़ाया
✅ Correct: हर upload +1 (या EAS remote `autoIncrement`)

❌ Mistake 3: app.json और app.config.js दोनों में अलग values (भ्रम)
✅ Correct: app.config.js में `({ config }) => ({ ...config })` से app.json extend, `expo config` से verify

❌ Mistake 4: `extra` में secret keys
✅ Correct: Secrets server पर; EAS Secrets सिर्फ build-time के लिए (client में फिर भी दिखेंगे अगर bundle में गए)

❌ Mistake 5: बेवजह permissions (जैसे READ_SMS)
✅ Correct: न्यूनतम; Play Policy declaration से बचो

---

## 🧠 Tricky Interview Question
आपने `app.config.js` में `android.permissions` में `CAMERA` जोड़ा और OTA update (`eas update`) भेजा। क्या users के phone में permission आ जाएगी?

Answer: नहीं। Permissions/package/native config **native build** का हिस्सा हैं; OTA सिर्फ JS bundle और assets बदलता है। नया native build (नया AAB) बनाकर Play पर release करना पड़ेगा। Update चलाने के लिए `runtimeVersion` policy से यह भी तय होता है कि कौन सा OTA किस native build पर चलेगा।

---

## ⚫ Interview Questions + Answers
Q1: app.json vs app.config.js?
A1: app.json static JSON; app.config.js JS है — env vars, conditions, computed values। दोनों हों तो app.config.js को app.json की config `config` argument में मिलती है।

Q2: `slug` और `name` का फर्क?
A2: name = user को दिखने वाला; slug = Expo project का URL-safe identifier (EAS/Updates से जुड़ा)।

Q3: `expo-constants` से config कैसे पढ़ें?
A3: `Constants.expoConfig.extra` (पुराना `Constants.manifest` deprecated)।

Q4: Config plugin क्या है?
A4: JS function जो prebuild के समय native files (manifest/Info.plist/gradle) को बदलती है, ताकि native folders हाथ से edit न करने पड़ें।

Q5: `runtimeVersion` क्यों?
A5: OTA updates को compatible native builds तक सीमित करता है (policy: appVersion / fingerprint — SDK के अनुसार, docs देखो)।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Expo/EAS project, multiple environments, एक config से दोनों platform

❌ Avoid when:
- Bare RN CLI project (native files सीधे)
- Secrets रखने के लिए (`extra` public होता है)

---

## 📊 Visual Diagram
```
  app.json ──► app.config.js({config}) ──► final config (npx expo config)
                    ▲ env APP_VARIANT                │
                    │                                ▼
              eas.json profile            prebuild / EAS Build
                                                     │
                                  AndroidManifest.xml + build.gradle + Info.plist
```

---

## 🖥️ Console Screens (वर्णन)
```
expo.dev dashboard → Project → "Configuration"/"Environment variables" (EAS): variables की list — name,
  value (secret हो तो hidden), visibility (Plain text / Sensitive / Secret), और environment checkboxes
  (development / preview / production)।
Terminal: `npx expo config --type public` JSON print करता है; `android.package` और `extra` वहाँ दिखें।
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| app.json | Static Expo config | Static config |
| app.config.js | Dynamic Expo config | Dynamic config |
| package | Android app ID | Android app पहचान |
| versionCode | Integer build number | Build नंबर |
| Config plugin | Edits native files at prebuild | Native files बदलने वाला plugin |
| extra | Custom runtime values | अपने custom values |

---

## ⚡ 3-Line Summary
English: app.json / app.config.js is Expo's single config; app.config.js can use env vars for dev, staging, prod.
Set the Android package early, bump versionCode each upload, keep permissions minimal.
Native config changes need a new native build; OTA cannot change them.

Hindi: app.json / app.config.js Expo की एक config है; app.config.js env vars से dev, staging, prod बनाता है।
Android package शुरू में तय करो, हर upload पर versionCode बढ़ाओ, permissions कम रखो।
Native config बदलने पर नया native build चाहिए; OTA से नहीं बदलता।

---

## ➡️ Next Topic
अगला publishing topic (Play Store submission के बाद) — release checklist और testing tracks।

---
