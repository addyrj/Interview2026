# 240. TestFlight — Complete Guide
# हिंदी में: TestFlight — पूरी गाइड
# Platform: Android ❌ | iOS ✅ (Android का equivalent: Play Console Internal/Closed/Open testing)

> Targets: **Expo SDK 52 (check current docs — APIs change between SDKs)**. Limits/UI Apple बदलता रहता है — App Store Connect help देखो।

---

## 🔵 Simple Definition (English)
**TestFlight** is Apple's free beta-testing service inside App Store Connect. You upload a build, invite testers, and they install it with the TestFlight app before the public release.

## 🔵 सरल परिभाषा (Hindi)
**TestFlight** Apple की free beta-testing service है (App Store Connect के अंदर)। Build upload करो, testers को invite करो, और वे TestFlight app से public release से पहले app install करके test करते हैं।

---

## 🔴 Problem it Solves
- App Store पर सीधे release = bugs सब users तक पहुँचते हैं।
- Ad-hoc distribution में हर device का UDID register करना पड़ता है (max 100 devices/year/type)।
- Testers को feedback और crash reports देने का आसान तरीका नहीं था।

## 🔴 यह क्यों बना? (Hindi)
Apple चाहता था कि developers बिना UDID की झंझट के बड़े group पर beta test कर सकें। TestFlight में सिर्फ email या public link से tester जुड़ जाता है, crash reports और screenshots feedback automatically मिलते हैं।

---

## 🟢 How it Works — Step by Step
1. Build `.ipa` बनाओ (EAS Build, topic 239)।
2. `eas submit -p ios` या Transporter से App Store Connect पर upload करो।
3. Apple build को process करता है ("Processing" → 10-30 मिनट)।
4. Export compliance सवाल का जवाब दो (या `ITSAppUsesNonExemptEncryption: false` पहले से set)।
5. Testers के groups बनाओ: **Internal** (तुम्हारी team) या **External** (बाहर के लोग)।
6. Tester को email/public link मिलता है → TestFlight app install → app install।
7. Build **90 दिन** बाद expire होती है।

```
Step 1 → Build .ipa
Step 2 → Upload to App Store Connect
Step 3 → Apple processing (Processing → Ready to Test)
Step 4 → Export compliance
Step 5 → Create tester group (Internal / External)
Step 6 → Tester installs via TestFlight app
Step 7 → Feedback + crash reports; repeat with new build
```

## 🟢 कैसे काम करता है? (Hindi)
1. Build बनाओ और upload करो।
2. Apple processing करता है; status "Processing" से "Ready to Submit/Test" होता है।
3. Tester groups बनाओ — internal या external।
4. Tester TestFlight app खोलकर install करता है।
5. 90 दिन बाद build expire; नई build upload करते रहो।

**Console screen (description):** App Store Connect → My Apps → आपका app → ऊपर tabs: *App Store | TestFlight | Xcode Cloud*. **TestFlight** tab पर left sidebar में "iOS Builds", "Internal Testing", "External Testing" sections हैं। Build की table में Version, Build number, Status (Processing / Missing Compliance / Ready to Test), और "Expires in 89 days" दिखता है।

---

## 🟡 Real World Example
**Zomato** jaisi app हर हफ्ते नया version पहले internal TestFlight group (employees) को देती है, फिर 1000 external beta users को। Crash rate कम दिखे तभी production release होता है। **Paytm** UPI flow जैसे critical features पर पहले छोटा external group test करता है।

## 🟡 Real Example Hindi mein
Zomato हर हफ्ते नया version पहले employees (internal group) और फिर कुछ हज़ार beta users (external) को TestFlight से देता है। Crash कम हों तभी App Store पर release होता है।

---

## 💻 Code Example — Basic
```json
// eas.json — TestFlight के लिए production profile + submit config
{
  "cli": { "appVersionSource": "remote" },
  "build": {
    "production": { "autoIncrement": true }
  },
  "submit": {
    "production": {
      "ios": {
        "ascAppId": "1234567890"
      }
    }
  }
}
```
```bash
# Build बनाओ
eas build -p ios --profile production
# सबसे latest build को TestFlight/App Store Connect पर भेजो
eas submit -p ios --latest
```

## 💻 Code Example — Advanced
```jsx
// TestFlightBadge.jsx — beta build पहचान कर "Beta" banner दिखाओ
// (expo-application से installation info; SDK 52 में उपलब्ध)
import React from 'react';                       // React import
import { View, Text, StyleSheet, Platform } from 'react-native'; // UI + platform check
import * as Application from 'expo-application'; // app version/build info

// ENV variable build profile से आता है (eas.json "env")
const CHANNEL = process.env.EXPO_PUBLIC_CHANNEL; // 'beta' | 'production'

export default function TestFlightBadge() {
  // सिर्फ iOS और beta channel पर banner दिखाओ
  if (Platform.OS !== 'ios' || CHANNEL !== 'beta') return null;
  return (
    <View style={styles.banner}>
      {/* version + build number दिखाओ ताकि tester bug report में लिख सके */}
      <Text style={styles.text}>
        BETA {Application.nativeApplicationVersion} ({Application.nativeBuildVersion})
      </Text>
    </View>
  );
}

// Styles
const styles = StyleSheet.create({
  banner: { backgroundColor: '#ff9800', padding: 4, alignItems: 'center' }, // orange strip
  text: { color: '#fff', fontWeight: '600', fontSize: 12 },                // white text
});
```
```json
// eas.json — beta profile जो env set करे (store distribution → TestFlight)
{
  "build": {
    "beta": {
      "distribution": "store",
      "autoIncrement": true,
      "env": { "EXPO_PUBLIC_CHANNEL": "beta" }
    }
  }
}
```
Not run: native `expo-application` device पर ही चलेगा; JSX syntax-check हुआ।

---

## 📱 Android vs iOS Difference
| Feature | Android (Play Console) | iOS (TestFlight) |
|---------|---------|-----|
| Internal testers | 100 (email list) | up to 100 App Store Connect users |
| External testers | Closed/Open tracks, unlimited | up to 10,000 |
| Review needed | नहीं (closed); Open में basic | External को Beta App Review (पहली build/version) |
| Build life | कोई expiry नहीं | 90 दिन |
| Tester app | Play Store | TestFlight app |
| Feedback | Play Console reports | Screenshot feedback + crash logs |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
# build + submit एक command में
eas build -p ios --profile production --auto-submit
```
CLI way:
```bash
# Xcode: Product → Archive → Distribute App → App Store Connect → Upload
# या command line से Transporter/altool-replacement:
xcrun altool --upload-app -f build/App.ipa -t ios --apiKey KEYID --apiIssuer ISSUER
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Same build number दोबारा upload करना → "Invalid Binary / duplicate build".
✅ Correct: `autoIncrement: true` या हर बार buildNumber बढ़ाओ।

❌ Mistake 2: Export compliance ignore करना → build "Missing Compliance" में अटकती है।
✅ Correct: `ITSAppUsesNonExemptEncryption` set करो या web पर जवाब दो।

❌ Mistake 3: 90 दिन में नई build न डालना → testers app नहीं खोल पाते।
✅ Correct: Regular beta builds ship करो।

❌ Mistake 4: Development build (developmentClient) को TestFlight पर भेजना।
✅ Correct: Store distribution वाली production/beta profile इस्तेमाल करो।

---

## 🧠 Tricky Interview Question
"Build upload हुई लेकिन TestFlight में testers को नहीं दिख रही, status 'Missing Compliance' है।"

Answer: Apple export compliance (encryption) answer के बिना build tester को नहीं देता। App Store Connect में build के पास warning icon पर click करके सवाल का जवाब दो, या `ITSAppUsesNonExemptEncryption=false` Info.plist में डालो ताकि आगे से पूछे ही नहीं।

---

## ⚫ Interview Questions + Answers
Q1: TestFlight में internal और external testers का फर्क?
A1: Internal = App Store Connect users (max 100), कोई review नहीं। External = कोई भी (max 10,000), Beta App Review चाहिए।

Q2: Build कितने दिन valid रहती है?
A2: 90 दिन।

Q3: UDID चाहिए क्या?
A3: नहीं। TestFlight में UDID register नहीं करना पड़ता (ad-hoc में करना पड़ता है)।

Q4: Public link क्या है?
A4: External group के लिए link बनता है जिससे कोई भी (limit तक) join कर सकता है — email नहीं चाहिए।

Q5: EAS से TestFlight कैसे भेजें?
A5: `eas submit -p ios` या build के साथ `--auto-submit`।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Release से पहले real iPhones पर test करना है।
- Non-technical stakeholders को आसान install चाहिए।

❌ Avoid when:
- Quick local debug करना है — dev build / simulator बेहतर।
- Sensitive build जो 90 दिन से ज़्यादा चलनी चाहिए (enterprise program देखो)।

---

## 📊 Visual Diagram
```
 .ipa ──► App Store Connect ──► Processing ──► Compliance
                                                  │
                         ┌────────────────────────┴───────────┐
                         ▼                                    ▼
                 Internal group (≤100)               External group (≤10,000)
                 no review                           Beta App Review
                         │                                    │
                         └────────► TestFlight app ◄──────────┘
                                       │ feedback / crashes
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| TestFlight | Apple beta platform | Apple का beta testing tool |
| Internal tester | Team member in ASC | आपकी team का सदस्य |
| External tester | Outside user | बाहर का tester |
| Beta App Review | Light review for external | external beta की जाँच |
| Export compliance | Encryption declaration | encryption की घोषणा |
| Build expiry | 90 days | build की उम्र |

---

## ⚡ 3-Line Summary
English: TestFlight is Apple's beta service for iOS builds.
Internal testers skip review; external testers need Beta App Review.
Builds expire after 90 days.

Hindi: TestFlight iOS builds के लिए Apple की beta service है।
Internal testers को review नहीं चाहिए; external को Beta App Review चाहिए।
Build 90 दिन में expire होती है।

---

## ➡️ Next Topic
**241. Upload to TestFlight** — अब practically build upload करने के तरीके (EAS Submit, Transporter, Xcode) देखते हैं।
