# 224. App Updates — How to Push
# हिंदी में: ऐप अपडेट कैसे भेजें (Play Store + OTA)
# Platform: Both ✅ (Android ✅ | iOS ✅ — OTA दोनों पर, Store update दोनों पर)

> Expo SDK 52+ (React Native 0.76+) पर आधारित। Expo SDK 52 (check current docs — APIs change between SDKs). `expo-updates` और EAS Update के config keys SDK के साथ बदल सकते हैं।

---

## 🔵 Simple Definition (English)
Pushing an app update means shipping new code to users who already installed your app. There are two ways: (1) a **Store update** (new binary uploaded to Play Store / App Store) and (2) an **OTA update** (Over-The-Air — only the JavaScript bundle and assets change, using EAS Update / `expo-updates`).

## 🔵 सरल परिभाषा (Hindi)
App update push करने का मतलब है उन users तक नया code पहुँचाना जिन्होंने app पहले से install किया है। दो तरीके हैं: (1) **Store update** — नया binary Play Store / App Store पर upload करना, और (2) **OTA update** (Over-The-Air) — सिर्फ JavaScript bundle और assets बदलते हैं, EAS Update / `expo-updates` से।

---

## 🔴 Problem it Solves
- Bug fix के लिए Play Store review (घंटों से दिनों तक) का इंतज़ार करना पड़ता था।
- Users पुराना version चलाते रहते थे, इसलिए production में कई versions एक साथ होते थे।
- Zomato जैसे app में checkout bug हो तो हर घंटे का नुकसान लाखों में होता है।

## 🔴 यह क्यों बना? (Hindi)
पहले हर छोटे fix के लिए नया build बनाकर store में submit करना पड़ता था और review का wait करना पड़ता था। OTA से JS-only fix कुछ मिनट में users तक पहुँच जाता है। लेकिन native code (नया permission, नई native library) बदला हो तो नया binary ही चाहिए।

---

## 🟢 How it Works — Step by Step

```
STORE UPDATE (binary change):
Step 1 → version बढ़ाओ (version + android.versionCode / ios.buildNumber)
Step 2 → eas build --platform all --profile production
Step 3 → eas submit (Play Console / App Store Connect)
Step 4 → Review pass → staged rollout (e.g. 10% → 50% → 100%)

OTA UPDATE (JS/assets only):
Step 1 → code बदलो (कोई native change नहीं)
Step 2 → eas update --branch production --message "Fix cart total"
Step 3 → App अगली बार खुलने पर update check करता है
Step 4 → Bundle download होता है → अगले launch पर apply (या reload पर)
```

## 🟢 कैसे काम करता है? (Hindi)
1. App में `expo-updates` होता है। हर build में एक **runtimeVersion** बंधा होता है।
2. जब आप `eas update` चलाते हैं, नया JS bundle EAS servers पर upload होता है।
3. App launch पर server से पूछता है: "इस runtimeVersion के लिए कोई नया bundle है?"
4. हाँ तो bundle download होकर cache होता है और (default में) अगले launch पर चलता है।
5. अगर runtimeVersion match नहीं करता (native बदला), तो OTA apply नहीं होता — नया store build चाहिए।

---

## 🟡 Real World Example
Swiggy जैसे app में festival sale के दिन banner का text गलत चला गया। JS-only fix है, इसलिए team `eas update --branch production` चलाती है और 5-10 मिनट में ज़्यादातर active users को fix मिल जाता है — Play Store review का wait नहीं। लेकिन अगर Swiggy को नया Google Pay SDK जोड़ना हो (native module), तो नया Play Store build ज़रूरी है।

## 🟡 Real Example Hindi mein
Paytm जैसे app में recharge screen पर typo आया — OTA update से कुछ मिनट में ठीक। पर नया "Tap to Pay" (NFC, native) feature चाहिए तो नया binary बनाकर Play Store/App Store में submit करना होगा।

---

## 💻 Code Example — Basic
```jsx
// app.json का हिस्सा (OTA के लिए config)
// {
//   "expo": {
//     "version": "1.0.1",                       // user को दिखने वाला version
//     "runtimeVersion": { "policy": "appVersion" }, // OTA सिर्फ same app version पर
//     "updates": { "url": "https://u.expo.dev/YOUR-PROJECT-ID" }, // eas update configure से बनता है
//     "android": { "versionCode": 2 },          // हर Play upload पर बढ़ाओ
//     "ios": { "buildNumber": "2" }             // हर App Store upload पर बढ़ाओ
//   }
// }

// Terminal commands (comment में, copy-paste ready):
// npm install -g eas-cli            // EAS CLI install
// eas login                         // Expo account login
// eas update:configure              // project में updates setup
// eas update --branch production --message "Fix cart total" // OTA publish
```

## 💻 Code Example — Advanced
```jsx
import React, { useEffect, useState } from 'react'; // React और hooks
import { View, Text, Button, Alert, Platform } from 'react-native'; // UI components
import * as Updates from 'expo-updates'; // OTA API

export default function UpdateGate() { // OTA update check करने वाला component
  const [busy, setBusy] = useState(false); // loading flag

  const checkForOta = async () => { // manual check function
    if (__DEV__) { // dev mode में OTA काम नहीं करता
      Alert.alert('Dev build', 'OTA updates सिर्फ release build में चलते हैं');
      return; // आगे मत जाओ
    }
    try { // error handling
      setBusy(true); // loading शुरू
      const res = await Updates.checkForUpdateAsync(); // server से पूछो
      if (res.isAvailable) { // नया bundle मिला
        await Updates.fetchUpdateAsync(); // download करो
        Alert.alert('Update ready', 'App restart होगा', [
          { text: 'Restart', onPress: () => Updates.reloadAsync() }, // नया bundle load
        ]);
      } else {
        Alert.alert('Up to date', 'आप latest version पर हैं'); // कुछ नया नहीं
      }
    } catch (e) { // network या config error
      Alert.alert('Error', String(e?.message ?? e)); // error दिखाओ
    } finally {
      setBusy(false); // loading बंद
    }
  };

  return (
    <View style={{ padding: 24 }}>
      <Text>Platform: {Platform.OS}</Text>
      <Text>Update ID: {Updates.updateId ?? 'embedded build'}</Text>
      <Button title={busy ? 'Checking...' : 'Check for update'} onPress={checkForOta} disabled={busy} />
    </View>
  );
}
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Store update | Play Console, review कुछ घंटे-दिन | App Store Connect, review ~24-48 घंटे |
| Staged rollout | Play Console में % rollout | Phased release (7 दिन automatic) |
| OTA (JS only) | ✅ allowed | ✅ allowed, पर app का core purpose/feature न बदले (Apple guideline 3.3.2 के अनुसार नियम पढ़ें) |
| In-app update prompt | ✅ Play Core API (topic 225) | ❌ नहीं — बस App Store link |
| Version fields | `versionCode` (integer) | `buildNumber` (string) |
| Force update | In-app immediate update | अपना version-check + store redirect |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Expo (EAS Update) — सबसे आसान
// eas update --branch production --message "Fix"
// expo-updates पहले से Expo projects के साथ आता है (npx expo install expo-updates)
```
CLI way:
```jsx
// Bare React Native CLI:
// 1) npx expo install expo-updates  (bare में भी चलता है, extra native setup चाहिए)
// 2) या CodePush alternatives (self-hosted OTA) — Microsoft App Center CodePush retire हो चुका है
// 3) Store update: ./gradlew bundleRelease (Android) / Xcode Archive (iOS) manual
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Native library जोड़कर भी सिर्फ `eas update` चलाना।
✅ Correct: Native बदलाव पर नया build बनाओ और runtimeVersion बदलो, वरना पुराने binary पर crash हो सकता है।

❌ Mistake 2: `versionCode` बढ़ाना भूल जाना — Play Console upload reject करेगा।
✅ Correct: हर upload पर `versionCode` बढ़ाओ (या EAS में `autoIncrement: true`)।

❌ Mistake 3: सीधे production branch पर test न किया हुआ update भेजना।
✅ Correct: पहले `preview` branch/channel पर test करो, फिर promote करो।

---

## 🧠 Tricky Interview Question
Q: आपने `eas update` से fix भेजा पर user के phone पर पुराना code चल रहा है। क्यों?

Answer: (1) Default में update download होता है पर **अगले launch** पर apply होता है। (2) User का binary अलग runtimeVersion पर है। (3) Build का channel और आपके update का branch mapped नहीं हैं। (4) Dev build पर OTA नहीं चलता। Fix: runtimeVersion/channel check करो, या `fetchUpdateAsync` + `reloadAsync` से तुरंत apply करो।

---

## ⚫ Interview Questions + Answers
Q1: OTA update और Store update में क्या फर्क है?
A1: OTA सिर्फ JS bundle/assets बदलता है और minutes में पहुँचता है। Store update पूरा binary बदलता है, review चाहिए।

Q2: runtimeVersion क्यों ज़रूरी है?
A2: ताकि नया JS सिर्फ उसी native binary पर चले जो उसके साथ compatible है। वरना missing native module से crash होगा।

Q3: Rollback कैसे करें?
A3: पुराना update दोबारा publish करें (`eas update:republish`) या branch को पिछले update पर point करें। Details EAS docs में check करें।

Q4: Staged rollout क्या है?
A4: नया version पहले 5-10% users को दें, crash rate देखें, फिर बढ़ाएँ।

Q5: Force update कैसे करेंगे?
A5: Android में in-app immediate update; iOS में server से min-version लें और पुराने version पर blocking screen दिखाकर App Store खोलें।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- JS/UI bug fix, text/offer changes, छोटे feature tweaks।
- Hotfix जो review का wait नहीं कर सकता।

❌ Avoid when:
- Native module, permission, SDK upgrade, app.json में native config बदला हो।
- Store policy के खिलाफ app का मूल उद्देश्य बदल रहा हो।

---

## 📊 Visual Diagram
```
 Developer
    │
    ├── JS बदला? ──► eas update ──► EAS CDN ──► App launch पर download ──► अगला launch पर apply
    │
    └── Native बदला? ► eas build ► eas submit ► Review ► Staged rollout ► Users
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| OTA | Over-The-Air update | हवा से (बिना store) update |
| runtimeVersion | Native binary compatibility tag | native version का tag |
| Branch/Channel | Update stream और build की mapping | update की धारा |
| versionCode | Android integer build number | Android build नंबर |
| Staged rollout | धीरे-धीरे % users को release | चरणबद्ध release |

---

## ⚡ 3-Line Summary
English: Use OTA (EAS Update) for JS-only fixes, Store update for native changes.
English: runtimeVersion keeps new JS safe with the right binary.
English: Always test on a preview branch and roll out in stages.
Hindi: JS fix के लिए OTA, native बदलाव के लिए store update।
Hindi: runtimeVersion नया JS सही binary पर ही चलने देता है।
Hindi: पहले preview पर test करो, फिर धीरे-धीरे rollout करो।

---

## ➡️ Next Topic
225. In-App Updates — Android में user को app के अंदर ही update prompt दिखाना।
