# 261. CodePush (Microsoft — deprecated)
# हिंदी में: CodePush — Microsoft का OTA (अब बंद)
# Platform: Android ✅ | iOS ✅ | Both ✅

> Expo SDK 52+ context (check current docs — APIs change between SDKs). CodePush was part of Visual Studio App Center; Microsoft retired App Center on 31 March 2025. Verify the current status of the open-source `react-native-code-push` package and of any hosted alternatives before choosing.

---

## 🔵 Simple Definition (English)
CodePush was Microsoft's cloud service plus `react-native-code-push` library for pushing JS bundle updates to React Native apps without store releases. The hosted service (App Center) was retired in 2025, so new projects should use EAS Update, a self-hosted solution, or a third-party replacement.

## 🔵 सरल परिभाषा (Hindi)
CodePush Microsoft की cloud service और `react-native-code-push` library थी, जिससे store release के बिना JS bundle updates भेजे जाते थे। Hosted service (App Center) 2025 में बंद हो गई, इसलिए नए projects को EAS Update, self-hosted solution या किसी third-party विकल्प का इस्तेमाल करना चाहिए।

---

## 🔴 Problem it Solves
```
CodePush solved: instant JS fixes for bare React Native apps (before Expo Updates existed).
It is deprecated because: its hosting platform was shut down.
```

## 🔴 यह क्यों बना? (Hindi)
Bare React Native apps के लिए तेज़ JS fix पाने को CodePush बना था। अब App Center बंद होने से यह hosted रूप में उपलब्ध नहीं; legacy projects को migrate करना पड़ता है।

---

## 🟢 How it Works — Step by Step
```
(Legacy flow, for understanding old codebases)
Step 1 → Register app in App Center, get deployment keys (Staging / Production)
Step 2 → Install react-native-code-push, native-link, put key in native config
Step 3 → Wrap root component with codePush(options)
Step 4 → appcenter codepush release-react -a owner/app -d Production
Step 5 → App checks on start/resume, downloads, installs on restart or immediately
Step 6 → Mandatory updates, rollback, staged rollout percentage supported
```

### Migration options
| Option | Notes |
|--------|-------|
| EAS Update (expo-updates) | Hosted by Expo; works in Expo and bare RN with expo modules |
| Self-hosted expo-updates server | You implement the Expo Updates protocol |
| Community/hosted CodePush-compatible services | Third-party; evaluate maintenance, pricing and security yourself |
| Self-hosted CodePush server (open-source) | You must run and secure it |
| No OTA | Regular store releases only |

## 🟢 कैसे काम करता है? (Hindi)
1. App Center में app बनाकर Staging/Production deployment keys मिलती थीं।
2. `react-native-code-push` install करके key native config में रखते थे।
3. Root component को `codePush(options)` से wrap करते थे।
4. `appcenter codepush release-react` से bundle release होता था।
5. App check -> download -> restart/immediate install करता था।
6. Mandatory update, rollback और staged percentage support था।

Migration में: expo-updates install करो, `runtimeVersion` और `channel` तय करो, पुराने codePush wrapper को हटाओ।

---

## 🟡 Real World Example
कई पुराने Indian startups के bare RN apps (e-commerce, fintech) ने CodePush पर 2-3 साल निर्भर रहकर hotfix दिए। 2025 के बाद ऐसी टीमों ने या तो EAS Update पर migrate किया या अपना server चलाया। (यह एक general pattern है, किसी specific company का दावा नहीं।)

## 🟡 Real Example Hindi mein
पुराने bare RN apps अक्सर CodePush पर निर्भर थे। App Center बंद होने के बाद ऐसी टीमों ने EAS Update या self-hosted server पर migration किया।

---

## 💻 Code Example — Basic (legacy CodePush wrapper)
```jsx
// App.js - LEGACY pattern; do not start new projects with this
import React from 'react';                                         // React
import { View, Text } from 'react-native';                         // UI
import codePush from 'react-native-code-push';                     // legacy library

const options = {                                                  // CodePush options
  checkFrequency: codePush.CheckFrequency.ON_APP_RESUME,           // check when app returns to foreground
  installMode: codePush.InstallMode.ON_NEXT_RESTART,               // apply on next restart
};

function App() {                                                   // root component
  return <View><Text>Hello</Text></View>;                          // demo UI
}

export default codePush(options)(App);                             // wrap root with CodePush
```

## 💻 Code Example — Advanced (migration: abstract OTA behind one interface)
```jsx
// ota.js - one wrapper so you can swap provider without touching screens
import * as Updates from 'expo-updates';                           // new provider (EAS Update)

export const ota = {                                               // provider-agnostic API
  async check() {                                                  // returns true if update downloaded
    if (!Updates.isEnabled) return false;                          // dev mode guard
    const r = await Updates.checkForUpdateAsync();                 // ask server
    if (!r.isAvailable) return false;                              // nothing new
    await Updates.fetchUpdateAsync();                              // download
    return true;                                                   // ready to apply
  },
  apply() {                                                        // restart into new bundle
    return Updates.reloadAsync();
  },
};

// usage in a screen:
// const ready = await ota.check(); if (ready) ota.apply();
```
Neither block was run (needs native build; CodePush service no longer hosted).

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Deployment keys | Separate key per platform | Separate key per platform |
| Native setup | MainApplication + strings.xml | AppDelegate + Info.plist |
| Store policy | Allowed (no deceptive changes) | 2.5.2 limits apply |
| Rollback | Supported | Supported |
| Hosted service today | Retired (App Center) | Retired (App Center) |
| Migration path | EAS Update / self-host | Same |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
# Managed Expo never used CodePush (needs native code). Use EAS Update instead:
npx expo install expo-updates && eas update --branch production
```
CLI way (legacy bare RN):
```bash
npm i react-native-code-push
cd ios && pod install
appcenter codepush release-react -a <owner>/<app> -d Production   # no longer works on retired hosted service
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Starting a new project on App Center CodePush.
✅ Correct: Choose EAS Update or another maintained solution.

❌ Mistake 2: Same deployment key for staging and production.
✅ Correct: Separate keys/channels (applies to any OTA tool).

❌ Mistake 3: Assuming open-source library = hosted service still alive.
✅ Correct: Check who hosts the update server.

❌ Mistake 4: Big-bang migration without testing.
✅ Correct: Ship a binary with the new OTA client first, then move updates.

---

## 🧠 Tricky Interview Question
Your old app version (CodePush-based, no expo-updates) is in many users' hands. You migrated to EAS Update in version 5.0. Can you push EAS updates to users still on 4.x?

Answer: No. Old binaries do not contain expo-updates, so they cannot receive EAS updates. Users must install 5.0 from the store first (use forced-update prompts). Until then, those users cannot get OTA fixes.

---

## ⚫ Interview Questions + Answers
Q1: Is CodePush still available?
A1: The hosted App Center service was retired on 31 March 2025; check community/self-hosted options.

Q2: Can Expo managed workflow use CodePush?
A2: Not in the classic managed workflow; Expo has its own Updates.

Q3: What replaced it for most teams?
A3: EAS Update.

Q4: What did `installMode` control?
A4: When the downloaded update was applied (immediate, on restart, on resume).

Q5: What risk remains with any OTA?
A5: Native/JS mismatch; ensure compatible runtimeVersion.

---

## 🔷 When to Use + When Not to Use
✅ Use (knowledge) when:
- Maintaining or migrating a legacy bare RN app

❌ Avoid when:
- Starting a new app; the hosted service is gone

---

## 📊 Visual Diagram
```
 Legacy:  Dev -> appcenter codepush release -> App Center (RETIRED) -> App
 Today :  Dev -> eas update ----------------> Expo servers --------> App
                 or self-hosted update server
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| CodePush | Microsoft OTA service | Microsoft का OTA |
| App Center | Retired Microsoft platform | बंद platform |
| Deployment key | Identifies target env | Environment की key |
| installMode | When to apply update | कब लागू करें |
| Migration | Moving to another tool | दूसरे tool पर जाना |

---

## ⚡ 3-Line Summary
English: CodePush delivered JS OTA updates for bare RN; its hosted service was retired in 2025.
New projects should use EAS Update or a self-hosted/maintained alternative.
Migration needs a new binary containing the new OTA client.

Hindi: CodePush bare RN के लिए JS OTA देता था; hosted service 2025 में बंद हुई।
नए projects EAS Update या self-hosted/maintained विकल्प लें।
Migration के लिए नए OTA client वाला नया binary चाहिए।

---

## ➡️ Next Topic
**262. When OTA Update is Enough** — कब OTA काफ़ी है और कब नहीं।
