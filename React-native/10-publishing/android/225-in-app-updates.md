# 225. In-App Updates
# हिंदी में: ऐप के अंदर अपडेट (Play Core In-App Updates)
# Platform: Android ✅ | iOS ❌ (iOS पर official equivalent नहीं)

> Expo SDK 52+ (React Native 0.76+)। Expo SDK 52 (check current docs — APIs change between SDKs). In-app updates native Google Play API है, इसलिए Expo Go में नहीं चलता — development build चाहिए। Library props/versions npm page पर verify करें।

---

## 🔵 Simple Definition (English)
In-app updates is a Google Play feature that lets your app ask the user to update **without leaving the app**. It has two modes: **Flexible** (download in background, user keeps using app) and **Immediate** (full-screen blocking update).

## 🔵 सरल परिभाषा (Hindi)
In-app update Google Play का feature है जिससे app खुद user से update करने को कह सकता है — Play Store पर गए बिना। दो modes: **Flexible** (background में download, user app चलाता रहता है) और **Immediate** (full-screen, update पूरा होने तक block)।

---

## 🔴 Problem it Solves
- Users Play Store जाकर manually update नहीं करते, इसलिए पुराने buggy versions चलते रहते हैं।
- Critical security fix को सब users तक पहुँचाना मुश्किल था।
- "Update available" का custom dialog सिर्फ Play Store link खोलता था — friction ज़्यादा।

## 🔴 यह क्यों बना? (Hindi)
Google ने Play Core In-App Update API दिया ताकि update का experience smooth हो: user app छोड़े बिना update स्वीकार करे। Critical bug के लिए Immediate mode से सबको force update कराया जा सकता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → App launch पर Play को पूछो: update available? (AppUpdateManager)
Step 2 → Response में updateAvailability + updatePriority (0-5) मिलती है
Step 3 → Priority कम → FLEXIBLE: background download, पूरा होने पर "Restart" snackbar
Step 4 → Priority ज़्यादा / critical bug → IMMEDIATE: full-screen Play UI
Step 5 → Install के बाद app restart → नया version
```

## 🟢 कैसे काम करता है? (Hindi)
1. App Google Play से पूछता है कि नया version है या नहीं।
2. Play बताता है update उपलब्ध है और उसकी priority (Play Console में आप set करते हैं)।
3. आप तय करते हैं Flexible या Immediate।
4. Play खुद download/install UI संभालता है।
5. ध्यान दें: यह सिर्फ **Play Store से installed** app पर काम करता है — APK sideload या debug पर नहीं।

---

## 🟡 Real World Example
Paytm जैसे financial app में security patch आता है। Team Immediate update चुनती है ताकि पुराना vulnerable version न चले। वहीं Zomato में नया UI theme है — Flexible update, user खाना order करता रहे और background में download होता रहे।

## 🟡 Real Example Hindi mein
Swiggy में नया "Instamart" tab आया — Flexible update। अगर payment bug था जो पैसे काट रहा था — Immediate update, जब तक update न हो app आगे नहीं बढ़ेगा।

---

## 💻 Code Example — Basic
```jsx
// Install (development build में; Expo Go में नहीं चलेगा):
// npx expo install sp-react-native-in-app-updates   // community library (Play Core wrapper)
// npx expo prebuild                                   // native folders बनाओ (या EAS dev build)

import React, { useEffect } from 'react'; // React और useEffect
import { Platform } from 'react-native'; // platform check के लिए
import SpInAppUpdates, { IAUUpdateKind } from 'sp-react-native-in-app-updates'; // library

export default function useInAppUpdate() { // custom hook
  useEffect(() => { // app mount पर चलेगा
    if (Platform.OS !== 'android') return; // iOS पर कुछ मत करो
    const inAppUpdates = new SpInAppUpdates(false); // false = debug logs बंद
    inAppUpdates
      .checkNeedsUpdate() // Play से पूछो
      .then((result) => { // response आया
        if (result.shouldUpdate) { // update चाहिए
          inAppUpdates.startUpdate({ updateType: IAUUpdateKind.FLEXIBLE }); // flexible शुरू
        }
      })
      .catch((e) => console.log('update check failed', e)); // error log
  }, []); // सिर्फ एक बार
}
```

## 💻 Code Example — Advanced
```jsx
import { useEffect } from 'react'; // hook
import { Platform, Linking, Alert } from 'react-native'; // RN APIs
import SpInAppUpdates, { IAUUpdateKind } from 'sp-react-native-in-app-updates'; // Android library

const STORE_URL = 'https://apps.apple.com/app/id0000000000'; // अपना iOS App Store link डालो

export function useUpdateGate(minVersion) { // minVersion = server से आया न्यूनतम version
  useEffect(() => {
    const run = async () => { // async runner
      try {
        if (Platform.OS === 'android') { // Android: Play Core
          const iau = new SpInAppUpdates(false); // instance
          const res = await iau.checkNeedsUpdate(); // check
          if (!res.shouldUpdate) return; // update नहीं तो खत्म
          // critical हो तो IMMEDIATE, वरना FLEXIBLE
          const kind = minVersion ? IAUUpdateKind.IMMEDIATE : IAUUpdateKind.FLEXIBLE;
          await iau.startUpdate({ updateType: kind }); // Play UI खुलेगा
        } else { // iOS: official in-app API नहीं है
          // iOS पर manual: iTunes lookup API से latest version देखो, फिर Alert
          Alert.alert('Update available', 'कृपया App Store से update करें', [
            { text: 'Later', style: 'cancel' }, // बाद में
            { text: 'Update', onPress: () => Linking.openURL(STORE_URL) }, // store खोलो
          ]);
        }
      } catch (e) { // कोई भी failure app को crash न करे
        console.log('update gate error', e); // log
      }
    };
    run(); // चलाओ
  }, [minVersion]); // minVersion बदलने पर दोबारा
}
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Official in-app API | ✅ Play Core (Flexible/Immediate) | ❌ नहीं |
| Update UI | Play का native UI | App Store पेज पर redirect |
| Priority control | Play Console API से 0-5 | अपना server-side config |
| Sideload/debug पर | काम नहीं करता | लागू नहीं |
| Force update | Immediate mode | अपना blocking modal |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// Expo: library जोड़ने के बाद development build ज़रूरी
// npx expo install sp-react-native-in-app-updates
// eas build --profile development --platform android
// Expo Go में native module नहीं मिलता
```
CLI way:
```jsx
// Bare CLI: auto-linking से library link हो जाती है
// npm install sp-react-native-in-app-updates
// cd android && ./gradlew clean && cd ..
// npx react-native run-android   // Play-installed build पर ही असली test होगा
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Debug/sideload build पर test करके सोचना कि feature टूटा है।
✅ Correct: Play Console के Internal testing track से install करके test करो।

❌ Mistake 2: हर update पर Immediate mode लगाना।
✅ Correct: सिर्फ critical fix पर Immediate; बाकी पर Flexible, वरना users नाराज़ होंगे।

❌ Mistake 3: iOS पर भी वही code चलाना और crash पाना।
✅ Correct: हमेशा `Platform.OS === 'android'` guard लगाओ।

---

## 🧠 Tricky Interview Question
Q: User ने Flexible update download कर लिया, पर app बंद किया बिना restart किए। क्या update install हुआ?

Answer: Flexible update download के बाद **install** के लिए `completeUpdate` (restart) चाहिए। Play अक्सर app के बंद होने पर install कर देता है, पर guaranteed नहीं — इसलिए download पूरा होने पर "Restart to update" prompt दिखाना best practice है।

---

## ⚫ Interview Questions + Answers
Q1: Flexible और Immediate में क्या फर्क है?
A1: Flexible background download, app चलता रहता है; Immediate full-screen blocking जब तक पूरा न हो।

Q2: In-app update Expo Go में क्यों नहीं चलता?
A2: यह native module है जो Expo Go में bundled नहीं; development build चाहिए।

Q3: iOS पर क्या करेंगे?
A3: iTunes Lookup API या अपने backend से latest version लेकर custom prompt और App Store link खोलेंगे।

Q4: Priority कहाँ set होती है?
A4: Play Developer API / Console में हर release के लिए (0-5)।

Q5: OTA update और in-app update में क्या फर्क?
A5: OTA JS bundle बदलता है; in-app update नया **binary** Play से install करवाता है।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Native changes वाला नया version users तक जल्दी पहुँचाना हो।
- Critical security/payment fix force करना हो।

❌ Avoid when:
- सिर्फ JS fix है — OTA बेहतर है।
- iOS user base पर चाहिए — वहाँ API नहीं।

---

## 📊 Visual Diagram
```
 App open ─► Play Core check ─► update? ─┬─ नहीं ─► normal app
                                          └─ हाँ ─► priority?
                                               ├─ low  ─► FLEXIBLE (bg download ─► Restart snackbar)
                                               └─ high ─► IMMEDIATE (full-screen ─► auto restart)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Play Core | Google की update API | Google का library |
| Flexible | Background update | पीछे चलने वाला update |
| Immediate | Blocking update | रोककर होने वाला update |
| updatePriority | 0-5 urgency | जल्दी का स्तर |
| Sideload | Store के बाहर install | बाहर से install |

---

## ⚡ 3-Line Summary
English: In-app updates let Play update your app inside the app.
English: Use Flexible normally, Immediate only for critical fixes.
English: Android only; iOS needs a custom prompt to the App Store.
Hindi: In-app update से Play app के अंदर ही update कराता है।
Hindi: सामान्य में Flexible, critical में Immediate।
Hindi: सिर्फ Android; iOS पर custom prompt + App Store link।

---

## ➡️ Next Topic
226. Apple Developer Account Setup — iOS publish करने की पहली शर्त।
