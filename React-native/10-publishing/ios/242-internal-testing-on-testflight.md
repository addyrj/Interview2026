# 242. Internal Testing on TestFlight
# हिंदी में: TestFlight पर Internal Testing
# Platform: Android ❌ | iOS ✅ (Android का equivalent: Play Console Internal testing track)

> Targets: **Expo SDK 52 (check current docs — APIs change between SDKs)**. Limits Apple बदल सकता है — ASC help देखो।

---

## 🔵 Simple Definition (English)
Internal testing lets up to 100 members of your own App Store Connect team test a build through TestFlight. No Apple review is needed, so builds are available right after processing.

## 🔵 सरल परिभाषा (Hindi)
Internal testing में आपकी अपनी App Store Connect team के अधिकतम 100 सदस्य TestFlight से build test कर सकते हैं। Apple review नहीं लगता, इसलिए processing के तुरंत बाद build मिल जाती है।

---

## 🔴 Problem it Solves
- Developers/QA को हर build तुरंत चाहिए — review का इंतज़ार नहीं कर सकते।
- UDID register किए बिना team के phones पर install करना है।

## 🔴 यह क्यों बना? (Hindi)
Team के लोग रोज़ नई build test करते हैं। Beta App Review (कुछ घंटे/दिन) इसमें बाधा होती, इसलिए internal group को review से छूट मिली है।

---

## 🟢 How it Works — Step by Step
1. Teammate को ASC में user बनाओ: **Users and Access → Users → +** (role: App Manager / Developer / Marketing आदि)।
2. उसे Apple ID से invitation accept करना होगा।
3. TestFlight tab → **Internal Testing → +** → group बनाओ (जैसे "QA Team")।
4. Group में users add करो; "Enable automatic distribution" ON करो तो हर नई build अपने-आप मिलेगी।
5. Tester iPhone पर **TestFlight** app install करता है, उसी Apple ID से login करता है।
6. App के पास "Install" दबाता है।

```
Step 1 → ASC में user add (role)
Step 2 → User invitation accept
Step 3 → Internal group बनाओ
Step 4 → Builds / auto-distribution चालू
Step 5 → TestFlight app में Install
```

## 🟢 कैसे काम करता है? (Hindi)
1. पहले teammate को ASC user बनाओ।
2. Internal Testing में group बनाओ और उसे add करो।
3. Automatic distribution ON रखो।
4. Tester TestFlight app से install करे।

**Console screen (description):** TestFlight tab → left sidebar में "Internal Testing" के नीचे "+" बटन। Group का नाम डालने वाला dialog आता है, उसमें checkbox "Enable automatic distribution". Group page पर तीन sections: **Testers** (list with email, status Invited/Installed), **Builds**, और **Group settings**.

---

## 🟡 Real World Example
**Zomato** का QA हर commit वाली build internal group से लेता है। **Swiggy** के product managers भी Marketing role से internal tester बनकर नया feature देखते हैं, बिना developer की मदद के।

## 🟡 Real Example Hindi mein
Zomato का QA हर नई build internal group से install करता है। Swiggy के PM भी internal tester बनकर नया feature देख लेते हैं।

---

## 💻 Code Example — Basic
```jsx
// FeedbackButton.jsx — tester को TestFlight से feedback बताने का hint
import React from 'react';                       // React
import { Pressable, Text, Linking, Platform } from 'react-native'; // UI + Linking

export default function FeedbackButton() {
  // सिर्फ iOS पर दिखाओ
  if (Platform.OS !== 'ios') return null;
  return (
    <Pressable
      // TestFlight app में बैठकर screenshot feedback देना है; यहाँ mail खोलते हैं
      onPress={() => Linking.openURL('mailto:qa@example.com?subject=Beta%20feedback')}
      style={{ padding: 12 }}
    >
      {/* Button label */}
      <Text>Send beta feedback</Text>
    </Pressable>
  );
}
```
## 💻 Code Example — Advanced
```jsx
// useBetaInfo.js — internal build पर extra debug info दिखाने वाला hook
import { useMemo } from 'react';                  // memo hook
import * as Application from 'expo-application';  // build info (expo-application)
import { Platform } from 'react-native';          // OS check

export function useBetaInfo() {
  return useMemo(() => {
    try {
      // version और build number — bug reports में काम आते हैं
      return {
        isIOS: Platform.OS === 'ios',
        version: Application.nativeApplicationVersion,
        build: Application.nativeBuildVersion,
        // env से channel; eas.json profile में set किया गया
        channel: process.env.EXPO_PUBLIC_CHANNEL ?? 'unknown',
      };
    } catch (e) {
      // अगर native module नहीं मिला (Expo Go में) तो safe fallback
      return { isIOS: Platform.OS === 'ios', version: null, build: null, channel: 'unknown' };
    }
  }, []);
}
```
Not run: native modules device पर ही; syntax-check ही संभव।

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Tester limit | Email list/Google Group | 100 internal users |
| Who can test | कोई भी Google account | सिर्फ ASC team users |
| Review | नहीं | नहीं |
| Auto-distribution | Track में release | Group setting में toggle |
| Tester app | Play Store | TestFlight |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
# Build + submit; internal group में auto-distribution ON हो तो तुरंत मिलेगी
eas build -p ios --profile production --auto-submit
```
CLI way:
```bash
# Xcode Archive → Upload; फिर वही ASC steps (group, testers)
# fastlane से group में add:
fastlane pilot distribute --distribute_external false --groups "QA Team"
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Tester को सिर्फ email invite करना, ASC user नहीं बनाना।
✅ Correct: Internal के लिए पहले ASC user बनाओ।

❌ Mistake 2: Tester किसी दूसरी Apple ID से TestFlight login करे।
✅ Correct: Invitation वाली Apple ID ही इस्तेमाल हो।

❌ Mistake 3: Group में build assign करना भूलना।
✅ Correct: "Automatic distribution" ON करो या Builds → + से जोड़ो।

---

## 🧠 Tricky Interview Question
"Client का PM TestFlight link माँग रहा है, पर वह आपकी ASC team में नहीं है। क्या internal group में डाल सकते हैं?"

Answer: नहीं। Internal testers सिर्फ ASC team users होते हैं। उसे या तो ASC user बनाओ (limited role, जैसे Marketing/Customer Support) या External group में email/public link से जोड़ो (Beta App Review के बाद)।

---

## ⚫ Interview Questions + Answers
Q1: Internal tester limit?
A1: 100।

Q2: Review चाहिए?
A2: नहीं।

Q3: Auto-distribution क्या है?
A3: नई processed build group को अपने-आप मिलती है।

Q4: Role कौन से ठीक रहते हैं?
A4: App Manager/Developer/Marketing — ज़रूरत के हिसाब से; least privilege रखो।

Q5: Tester कैसे install करता है?
A5: TestFlight app से, उसी Apple ID से।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Dev/QA/PM को तुरंत build चाहिए।
- Daily/nightly builds।

❌ Avoid when:
- बाहर के clients या users को देना है (External)।
- 100 से ज़्यादा testers।

---

## 📊 Visual Diagram
```
 ASC Team ──► Users & Access (roles)
                │
                ▼
        Internal Group "QA Team" ── auto-distribute ──► new Build
                │
                ▼
        TestFlight app on iPhone ──► Install
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Internal tester | ASC team user | team का tester |
| Group | Set of testers | testers का समूह |
| Auto distribution | New builds sent automatically | अपने-आप build भेजना |
| Role | Permission level | अनुमति का स्तर |

---

## ⚡ 3-Line Summary
English: Internal testing is for your ASC team, up to 100 people.
No Apple review is needed.
Enable auto-distribution to get every build fast.

Hindi: Internal testing आपकी ASC team के लिए है, अधिकतम 100 लोग।
Apple review नहीं चाहिए।
Auto-distribution ON रखो ताकि हर build जल्दी मिले।

---

## ➡️ Next Topic
**243. External Testing on TestFlight** — team के बाहर के users तक beta पहुँचाना।
