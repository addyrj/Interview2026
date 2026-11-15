# 09. When to Use Expo vs CLI
# हिंदी में: Expo कब use करें और React Native CLI कब
# Platform: Android ✅ | iOS ✅ | Both ✅

> Target: Expo SDK 52 / React Native 0.76. Expo SDK NN (check current docs — APIs change between SDKs). Note: topic 08 explained *what* they are; this topic is the **decision guide**.

---

## 🔵 Simple Definition (English)
Choosing between **Expo** and **React Native CLI** is a project decision: Expo gives a managed toolchain (fast start, EAS cloud builds, ready modules), CLI gives you the raw native projects from day one. Today both can be mixed: an Expo project can have `android/` and `ios/` folders (**prebuild**), so the choice is less strict than before.

## 🔵 सरल परिभाषा (Hindi)
**Expo** और **React Native CLI** में से चुनना एक project का फ़ैसला है: Expo managed toolchain देता है (तेज़ शुरुआत, EAS cloud builds, ready modules), CLI पहले दिन से raw native projects देता है। आजकल दोनों mix हो सकते हैं: Expo project में भी `android/` और `ios/` folders (**prebuild**) बन सकते हैं, इसलिए यह चुनाव पहले जितना सख्त नहीं रहा।

---

## 🔴 Problem it Solves
```
Wrong choice at start causes pain later:
❌ CLI chosen by a small team -> days lost on Gradle/Xcode/CocoaPods errors
❌ Expo Go chosen, then a custom native SDK (e.g. a bank SDK) is required
❌ No Mac in the team, but iOS builds are needed
❌ Upgrading RN versions by hand = painful diffs
A clear decision checklist avoids rework.
```

## 🔴 यह क्यों बना? (Hindi)
```
शुरुआत में गलत चुनाव बाद में परेशानी देता है:
❌ छोटी team ने CLI लिया -> Gradle/Xcode/CocoaPods errors में दिन बर्बाद
❌ Expo Go लिया, फिर custom native SDK (जैसे bank SDK) चाहिए
❌ Team में Mac नहीं, पर iOS build चाहिए
❌ RN version हाथ से upgrade करना = मुश्किल diff
साफ़ decision checklist से दोबारा काम नहीं करना पड़ता।
```

---

## 🟢 How it Works — Step by Step

```
Step 1 → List needs: custom native SDK? background tasks? team size?

Step 2 → Need only common features (camera, push, maps, storage)?
         -> Expo (managed or with dev builds)

Step 3 → Need a custom/private native SDK (e.g. Paytm payment SDK)?
         -> Expo + config plugin / prebuild   OR   CLI

Step 4 → No Mac but need iOS build?
         -> Expo + EAS Build (cloud Mac)

Step 5 → Existing native app adding RN screens (brownfield)?
         -> CLI-style native integration

Step 6 → Default in 2024+: start with Expo, "eject" never needed
         because prebuild can generate native folders any time
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → ज़रूरतें लिखो: custom native SDK? background tasks? team size?
Step 2 → सिर्फ common features (camera, push, maps, storage)?
         -> Expo (managed या dev builds के साथ)
Step 3 → Custom/private native SDK चाहिए (जैसे payment SDK)?
         -> Expo + config plugin / prebuild   या   CLI
Step 4 → Mac नहीं पर iOS build चाहिए?
         -> Expo + EAS Build (cloud Mac)
Step 5 → पहले से native app में RN screens जोड़ने हैं (brownfield)?
         -> CLI-style native integration
Step 6 → 2024+ में default: Expo से शुरू करो; prebuild से native folders
         कभी भी बन जाते हैं, इसलिए "eject" की ज़रूरत नहीं
```

---

## 🟡 Real World Example
A startup building a **Zomato-like** food app with maps, push notifications, camera upload and payments (Razorpay has an Expo config plugin route via dev builds) usually starts on **Expo + EAS** and ships in weeks. A large fintech like **Paytm / PhonePe** with many proprietary native SDKs, custom build pipelines and existing native code typically works in a **native-first / CLI-style** setup.

## 🟡 Real Example Hindi mein
Maps, push notifications, camera upload और payments वाला **Zomato जैसा** food app बनाने वाला startup आम तौर पर **Expo + EAS** से शुरू करके कुछ हफ्तों में ship कर देता है। **Paytm / PhonePe** जैसी बड़ी fintech, जहाँ कई proprietary native SDKs, custom build pipelines और पुराना native code होता है, वहाँ आम तौर पर **native-first / CLI-style** setup चलता है।

---

## 💻 Code Example — Basic

```jsx
// Basic: a tiny helper that tells you which workflow you are running in
// Works on Android + iOS
import React from 'react'; // React
import { View, Text, StyleSheet } from 'react-native'; // UI parts
import Constants, { ExecutionEnvironment } from 'expo-constants'; // Expo constants

// Decide the runtime from expo-constants
function getRuntime() {
  // Running inside the Expo Go app?
  if (Constants.executionEnvironment === ExecutionEnvironment.StoreClient) {
    return 'Expo Go (limited native modules)'; // Expo Go label
  }
  // Running a standalone / development build?
  return 'Development or production build (any native module)'; // build label
}

export default function RuntimeBadge() {
  return (
    <View style={styles.box}>
      {/* Show the runtime so the team knows what is available */}
      <Text style={styles.text}>{getRuntime()}</Text>
    </View>
  );
}

// Styles
const styles = StyleSheet.create({
  box: { padding: 16, backgroundColor: '#eef', margin: 16, borderRadius: 8 }, // card
  text: { fontSize: 16 }, // label
});
```

## 💻 Code Example — Advanced

```jsx
// Advanced: feature-gate a native-only feature so one codebase works in Expo Go AND dev builds
import React, { useState } from 'react'; // React + state
import { View, Text, Button, Platform, Alert, StyleSheet } from 'react-native'; // UI
import Constants, { ExecutionEnvironment } from 'expo-constants'; // runtime info

// True when we are inside Expo Go (custom native code NOT available)
const isExpoGo = Constants.executionEnvironment === ExecutionEnvironment.StoreClient;

export default function PaymentButton() {
  const [busy, setBusy] = useState(false); // loading flag

  const pay = async () => {
    // Block the custom SDK path in Expo Go with a clear message
    if (isExpoGo) {
      Alert.alert('Dev build needed', 'Create a development build to test payments.'); // info
      return; // stop here
    }
    try {
      setBusy(true); // show loading
      // Lazy-require so Expo Go never tries to load the missing native module
      const Pay = require('react-native-razorpay').default; // custom native SDK
      const res = await Pay.open({ key: 'rzp_test_xxx', amount: 49900, currency: 'INR' }); // open checkout
      Alert.alert('Paid', res.razorpay_payment_id); // success
    } catch (e) {
      Alert.alert('Payment failed', String(e?.description || e?.message || e)); // error handling
    } finally {
      setBusy(false); // hide loading
    }
  };

  return (
    <View style={styles.box}>
      {/* Platform-specific hint */}
      <Text>{Platform.OS === 'ios' ? 'Apple Pay also possible' : 'UPI intents available'}</Text>
      <Button title={busy ? 'Please wait...' : 'Pay Rs 499'} onPress={pay} disabled={busy} />
    </View>
  );
}

// Styles
const styles = StyleSheet.create({
  box: { padding: 20, gap: 12 }, // spacing
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Build machine (CLI) | Windows, Mac, Linux | **Mac only** (Xcode) |
| Build machine (Expo EAS) | Cloud | Cloud (no Mac needed) |
| Expo Go on device | Install from Play Store | Install from App Store |
| Custom native SDK | Gradle dependency | CocoaPods / SPM dependency |
| Store upload | Play Console (.aab) | App Store Connect (.ipa) |
| Account cost | One-time $25 | $99 / year |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Start: npx create-expo-app@latest MyApp
// Run:   npx expo start           (press "a" Android / "i" iOS)
// Build: eas build --platform all (cloud)
// Native folders when needed: npx expo prebuild
```
CLI way:
```jsx
// Start: npx @react-native-community/cli@latest init MyApp
// Run:   npx react-native run-android / run-ios
// Build: ./gradlew assembleRelease  and  Xcode Archive
// Native folders: always present in the repo
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Believing "Expo apps are not real / cannot go to production".
✅ Correct: Expo apps ship on both stores; the Expo docs themselves recommend it as the default way to start.

❌ Mistake 2: Choosing CLI only "to be professional".
✅ Correct: Choose by needs. CLI adds maintenance without a benefit for most apps.

❌ Mistake 3: Testing a custom native module in Expo Go.
✅ Correct: Make a **development build** (`npx expo run:android` or `eas build --profile development`).

❌ Mistake 4: Thinking "eject" is one-way.
✅ Correct: Use `npx expo prebuild`; native folders are generated and can be regenerated (CNG - Continuous Native Generation).

---

## 🧠 Tricky Interview Question
**Q:** "Your Expo app needs a private payment SDK that has only an Android AAR and iOS framework. Must you rewrite in CLI?"

Answer: **No.** Write a **config plugin** or local **Expo module** that adds the SDK during `prebuild`, then use a development build / EAS Build. You only fall back to CLI if the organization needs full manual control of native projects.

---

## ⚫ Interview Questions + Answers
Q1: Which one would you pick for a new startup app?
A1: Expo (with EAS and development builds), because setup, OTA updates and builds are faster.

Q2: What is Continuous Native Generation?
A2: `android/` and `ios/` are generated from `app.json` + config plugins by `expo prebuild`, so they need not be committed.

Q3: Can Expo apps use any npm native library?
A3: Yes with a development build and, if needed, a config plugin. Not inside Expo Go.

Q4: When is CLI still better?
A4: Brownfield apps (RN inside an existing native app), heavy custom native build setups, strict internal tooling.

Q5: Can I build iOS without a Mac?
A5: Yes with EAS Build (cloud). Submitting needs an Apple Developer account.

---

## 🔷 When to Use + When Not to Use
✅ Use Expo when:
- Small/medium team, fast MVP
- Need OTA updates (EAS Update)
- No Mac for every developer

✅ Use CLI when:
- Brownfield integration with existing native app
- Very custom native build pipeline

❌ Avoid Expo Go when:
- You rely on custom native modules
- You need exact production native config

---

## 📊 Visual Diagram
```
                Need custom native code?
                   /              \
                 NO               YES
                 |                 |
          Expo (Expo Go,     Expo dev build + config plugin
          then dev build)         (prebuild)  or  CLI
                 |                 |
              EAS Build  ------  EAS Build / local Gradle+Xcode
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Expo Go | Prebuilt sandbox app for testing | Testing के लिए तैयार app |
| Dev build | Your own app with dev tools | आपका अपना dev app |
| Prebuild | Generate android/ios folders | native folders बनाना |
| Config plugin | Edits native config automatically | native config अपने-आप बदलता है |
| EAS Build | Expo cloud build service | Expo की cloud build service |
| Brownfield | RN inside existing native app | पुराने native app में RN |

---

## ⚡ 3-Line Summary
English: Default to Expo for most new apps; it is faster and still allows native code.
Use CLI for brownfield or highly custom native pipelines.
Custom native modules need a development build, never Expo Go.

Hindi: ज़्यादातर नए apps के लिए Expo default रखें; यह तेज़ है और native code भी allow करता है।
Brownfield या बहुत custom native pipeline के लिए CLI लें।
Custom native modules के लिए development build चाहिए, Expo Go नहीं।

---

## ➡️ Next Topic
**10. Setting Up Environment (Mac/Windows)** — install Node, JDK, Watchman and SDKs so you can start building.

---
