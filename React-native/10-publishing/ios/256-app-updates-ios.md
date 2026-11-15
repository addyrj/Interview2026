# 256. App Updates (iOS)
# हिंदी में: iOS App Updates — नया version कैसे भेजें
# Platform: Android ❌ | iOS ✅

> Expo SDK 52+ examples (check current docs — APIs change between SDKs).

---

## 🔵 Simple Definition (English)
An app update is a new version of an already-live iOS app. You bump the version/build number, upload a new build, fill "What's New", pass review again, and release. JS-only fixes can alternatively ship via OTA (EAS Update) without a store update.

## 🔵 सरल परिभाषा (Hindi)
App update पहले से live app का नया version है। Version/build number बढ़ाओ, नया build upload करो, "What's New" लिखो, review pass करो और release करो। सिर्फ JS वाले fixes OTA (EAS Update) से भी भेजे जा सकते हैं।

---

## 🔴 Problem it Solves
```
PROBLEM: Users stay on old versions with bugs / old APIs.
         Backend changes can break old app versions.
SOLUTION: Versioned releases + optional/forced update prompts + OTA for JS-only fixes.
```

## 🔴 यह क्यों बना? (Hindi)
Users पुराने version पर अटके रहते हैं और backend बदलने पर पुराने app टूट जाते हैं। Updates, forced-update prompt और OTA से सभी को सही version पर लाया जाता है।

---

## 🟢 How it Works — Step by Step
```
Step 1 → Decide update type: JS-only (OTA) or native/store update
Step 2 → Store update: bump "version" (user-visible, e.g. 2.5.0)
Step 3 → Bump ios.buildNumber (must be higher than any previous upload for that version)
Step 4 → eas build + eas submit
Step 5 → In App Store Connect: "+ Version" -> new version, What's New, select build
Step 6 → Submit for review, then release (phased recommended)
Step 7 → App prompts old users (optional/forced) using minimum-version flag from backend
```

### Version vs build number
| Field | app.json key | Visible to user | Rule |
|-------|--------------|-----------------|------|
| Version | `expo.version` (CFBundleShortVersionString) | Yes | Semantic: 2.5.0 |
| Build number | `expo.ios.buildNumber` (CFBundleVersion) | Only in TestFlight | Must increase per upload |

### Console screen description
- **My Apps → App → "+" beside "iOS App"** in the sidebar: dialog "New Version" with a text box for version number.
- On the new version page: **"What's New in This Version"** text area (4000 chars), build selector, and the same release options as the first release.
- **TestFlight tab** shows each build with number, status "Processing" then "Ready to Submit" and a yellow "Missing Compliance" warning if export-compliance is not answered (set `ios.config.usesNonExemptEncryption: false` when appropriate, or `ITSAppUsesNonExemptEncryption` in Info.plist).

## 🟢 कैसे काम करता है? (Hindi)
1. तय करो: सिर्फ JS बदला (OTA) या native भी (store update)।
2. `version` बढ़ाओ (user को दिखता है)।
3. `buildNumber` बढ़ाओ (हर upload पर अलग होना चाहिए)।
4. `eas build` और `eas submit` चलाओ।
5. App Store Connect में नया version बनाकर What's New भरो और review भेजो।
6. पुराने users के लिए backend से minimum version भेजकर update prompt दिखाओ।

---

## 🟡 Real World Example
Paytm/PhonePe जैसे apps में जब UPI backend बदलता है तो पुराने versions block कर दिए जाते हैं और "Please update the app" screen आती है (forced update)। Swiggy का छोटा UI bug OTA से ठीक हो सकता है, पर नया native SDK (जैसे नया payment SDK) store update माँगता है।

## 🟡 Real Example Hindi mein
UPI या security बदलाव होने पर Paytm जैसे apps पुराने version को "Update required" screen दिखाते हैं। UI की छोटी गलती OTA से ठीक होती है, पर नया native SDK जोड़ना हो तो App Store update ज़रूरी है।

---

## 💻 Code Example — Basic (app.json versions)
```json
{
  "expo": {
    "name": "FoodApp",
    "version": "2.5.0",
    "ios": {
      "bundleIdentifier": "com.example.foodapp",
      "buildNumber": "57",
      "config": { "usesNonExemptEncryption": false }
    }
  }
}
```
```bash
eas build --platform ios --profile production   # build with updated numbers
eas submit --platform ios --latest              # upload to App Store Connect
```

## 💻 Code Example — Advanced (forced-update gate)
```jsx
// ForceUpdateGate.jsx - blocks app if installed version < minimum from backend
import React, { useEffect, useState } from 'react';                   // React + hooks
import { View, Text, Pressable, Linking, Platform, ActivityIndicator } from 'react-native'; // UI
import Constants from 'expo-constants';                              // for app version

// compare "2.5.0" style versions: returns true if a < b
export const isOlder = (a, b) => {                                   // pure function, easy to test
  const pa = a.split('.').map(Number);                               // [2,5,0]
  const pb = b.split('.').map(Number);                               // [2,6,0]
  for (let i = 0; i < Math.max(pa.length, pb.length); i++) {         // compare each part
    const x = pa[i] || 0, y = pb[i] || 0;                            // missing part = 0
    if (x < y) return true;                                          // older
    if (x > y) return false;                                         // newer
  }
  return false;                                                      // equal
};

const STORE_URL = 'itms-apps://apps.apple.com/app/id1234567890';    // your App Store link

export default function ForceUpdateGate({ children }) {              // wraps whole app
  const [state, setState] = useState('loading');                     // loading | ok | blocked

  useEffect(() => {                                                  // check once on start
    (async () => {
      try {                                                          // network may fail
        const res = await fetch('https://api.example.com/config');   // backend config (example URL)
        const { minIosVersion } = await res.json();                  // e.g. "2.4.0"
        const current = Constants.expoConfig?.version ?? '0.0.0';    // installed version
        setState(Platform.OS === 'ios' && isOlder(current, minIosVersion) ? 'blocked' : 'ok');
      } catch {
        setState('ok');                                              // fail-open: do not lock users on error
      }
    })();
  }, []);

  if (state === 'loading') return <ActivityIndicator style={{ flex: 1 }} />; // splash-like
  if (state === 'blocked') {                                         // force update UI
    return (
      <View style={{ flex: 1, justifyContent: 'center', padding: 24 }}>
        <Text style={{ fontSize: 20, fontWeight: '700' }}>Update required</Text>
        <Pressable onPress={() => Linking.openURL(STORE_URL)}><Text>Open App Store</Text></Pressable>
      </View>
    );
  }
  return children;                                                   // normal app
}
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Version fields | versionName + versionCode | version + buildNumber |
| In-app update | Play In-App Updates API (flexible/immediate) | No official API; prompt + open App Store link |
| Review for update | Usually fast | Review every update |
| Auto-update | Play auto-update settings | iOS auto-update setting |
| Old version control | Can block via Play policy / app logic | App logic only |
| Release notes | "Release notes" per language | "What's New" per locale |

---

## 🟠 Expo vs CLI Difference
Expo way:
```json
{ "expo": { "version": "2.5.0", "ios": { "buildNumber": "57" } } }
```
```bash
eas build -p ios --auto-submit   # with "autoIncrement": true in eas.json
```
CLI way:
```bash
# Xcode: General > Identity: Version 2.5.0, Build 57
# or from terminal:
agvtool new-marketing-version 2.5.0     # sets version
agvtool next-version -all                # increments build number
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Reusing the same buildNumber.
✅ Correct: Increment each upload (EAS autoIncrement).

❌ Mistake 2: Forced-update gate that fails closed when API is down.
✅ Correct: Fail open so outages do not lock every user.

❌ Mistake 3: Shipping native changes via OTA.
✅ Correct: New native code needs a new build; OTA only matches same runtimeVersion.

❌ Mistake 4: Empty "What's New".
✅ Correct: Short, honest release notes.

---

## 🧠 Tricky Interview Question
You shipped version 2.5.0 (build 57), found a typo in the App Store metadata only. Do you need a new build?

Answer: No. Metadata edits on a version not yet released need no new binary; for an already-live version you can edit some fields (like description, keywords, screenshots) only via a new version submission, while certain fields (e.g. promotional text) can be changed without review. Check App Store Connect for which fields are editable.

---

## ⚫ Interview Questions + Answers
Q1: Version vs build number?
A1: Version is what users see; build number must be unique per upload.

Q2: How to force users to update?
A2: Backend minimum version + gate screen linking to the App Store.

Q3: Can you update an app without review?
A3: JS/asset changes via OTA, within Apple's rules.

Q4: What does "Missing Compliance" mean?
A4: Export compliance (encryption) question unanswered for that build.

Q5: Is there an iOS in-app update API?
A5: No official one like Android's; use a prompt and deep link.

---

## 🔷 When to Use + When Not to Use
✅ Store update when:
- Native code, permissions, SDKs, or app.json native config change

❌ Avoid store update when:
- A JS-only fix can go via EAS Update

---

## 📊 Visual Diagram
```
 Change?
   |- JS only ------> eas update ------> users (minutes)
   |- Native -------> bump version/build -> eas build -> submit -> review -> release
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| CFBundleShortVersionString | User-visible version | दिखने वाला version |
| CFBundleVersion | Build number | Build क्रमांक |
| What's New | Release notes | नया क्या है |
| Force update | Block old versions | अनिवार्य update |
| Export compliance | Encryption declaration | Encryption की घोषणा |

---

## ⚡ 3-Line Summary
English: Updates need a higher build number and new review.
Use a minimum-version gate to force upgrades.
JS-only fixes can use OTA.

Hindi: Update के लिए ऊँचा build number और नया review चाहिए।
Upgrade अनिवार्य करने को minimum-version gate लगाओ।
सिर्फ JS fix हो तो OTA इस्तेमाल करो।

---

## ➡️ Next Topic
**257. App Store Optimization (ASO)** — updates के साथ app की visibility कैसे बढ़ाएँ।
