# 229. App ID + Bundle ID
# हिंदी में: App ID और Bundle ID
# Platform: Android ❌ (Android में applicationId) | iOS ✅

> Expo SDK 52+ (React Native 0.76+)। Expo SDK 52 (check current docs — APIs change between SDKs).

---

## 🔵 Simple Definition (English)
The **Bundle ID** is the unique reverse-DNS name of your iOS app (like `com.zomato.app`). The **App ID** is the record in Apple's developer portal that combines your Team ID with the Bundle ID and the capabilities (Push, Sign in with Apple, etc.) the app may use.

## 🔵 सरल परिभाषा (Hindi)
**Bundle ID** आपके iOS app का unique reverse-DNS नाम है (जैसे `com.zomato.app`)। **App ID** Apple developer portal का record है जो Team ID + Bundle ID + capabilities (Push, Sign in with Apple आदि) को जोड़ता है।

---

## 🔴 Problem it Solves
- दुनिया भर के लाखों apps में हर app की अलग पहचान चाहिए।
- Apple को पता होना चाहिए कि app को कौन-सी capabilities की अनुमति है।

## 🔴 यह क्यों बना? (Hindi)
नाम (जैसे "Food App") कई apps में एक जैसे हो सकते हैं, पर Bundle ID unique होती है। Capabilities (जैसे Push) हर app के लिए अलग से allow करनी होती हैं — यह नियंत्रण App ID देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Bundle ID तय करो: com.<company>.<app> (lowercase, केवल अक्षर/अंक/./-)
Step 2 → Portal → Certificates, IDs & Profiles → Identifiers → ➕ → App IDs → App
Step 3 → Description + Bundle ID (Explicit) डालो
Step 4 → Capabilities चुनो (Push Notifications, Sign in with Apple, Associated Domains...)
Step 5 → Register → यही Profile में जुड़ेगा
Step 6 → Expo: app.json → ios.bundleIdentifier में वही लिखो
```

## 🟢 कैसे काम करता है? (Hindi)
**Explicit App ID** — एक ही app के लिए (`com.mycompany.foodapp`); Push, IAP जैसी capabilities के लिए ज़रूरी।
**Wildcard App ID** — `com.mycompany.*`; कई apps पर लागू पर capabilities सीमित।
**Screens:** Identifiers सूची में ➕ बटन, फिर radio list (App IDs, Services IDs...), फिर "Register an App ID" form जिसमें Description, Bundle ID (Explicit/Wildcard radio) और नीचे Capabilities की checkbox list।
Bundle ID एक बार App Store Connect में app बन जाने के बाद **बदली नहीं जा सकती**।

---

## 🟡 Real World Example
Swiggy के पास Customer app `in.swiggy.app` और Delivery Partner app एक अलग Bundle ID से — दोनों के लिए अलग App IDs, अलग Push settings और अलग store listings। Staging के लिए `in.swiggy.app.staging` जैसी तीसरी ID होती है।

## 🟡 Real Example Hindi mein
Zomato अपने Customer और Zomato Restaurant Partner app के लिए अलग Bundle IDs रखता है ताकि दोनों एक ही phone पर साथ install रह सकें।

---

## 💻 Code Example — Basic
```jsx
// app.json में Bundle ID (Expo)
// {
//   "expo": {
//     "name": "Food App",
//     "slug": "food-app",
//     "ios": {
//       "bundleIdentifier": "com.mycompany.foodapp", // Apple portal वाली ID से हू-ब-हू मेल खाए
//       "buildNumber": "1"                            // हर store upload पर बढ़ाओ
//     },
//     "android": { "package": "com.mycompany.foodapp" } // Android का equivalent
//   }
// }
```

## 💻 Code Example — Advanced
```jsx
// Environment के अनुसार अलग Bundle ID — app.config.js (Expo dynamic config)
const IS_STAGING = process.env.APP_ENV === 'staging'; // env से तय करो

export default ({ config }) => ({ // Expo config function
  ...config, // बाकी config जस का तस
  name: IS_STAGING ? 'Food App (Stg)' : 'Food App', // display name
  ios: {
    ...config.ios, // iOS की बाकी settings
    bundleIdentifier: IS_STAGING
      ? 'com.mycompany.foodapp.staging' // staging ID (अलग App ID portal में बनाओ)
      : 'com.mycompany.foodapp', // production ID
    buildNumber: '1', // build number
  },
  android: {
    ...config.android, // Android settings
    package: IS_STAGING ? 'com.mycompany.foodapp.staging' : 'com.mycompany.foodapp', // Android package
  },
});

// Terminal: APP_ENV=staging eas build --platform ios --profile preview
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| नाम | `applicationId` / `package` | `bundleIdentifier` |
| Portal registration | ज़रूरी नहीं (Play Console में बनता है) | App ID register करना पड़ता है |
| Capabilities | Manifest permissions | Portal में capabilities + entitlements |
| Format | com.company.app | com.company.app (hyphen allowed, underscore नहीं) |
| बाद में बदलना | नहीं (नया app बनेगा) | नहीं (नया app बनेगा) |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// app.json: "ios": { "bundleIdentifier": "com.mycompany.foodapp" }
// EAS App ID खुद register कर सकता है (Apple login के बाद)
```
CLI way:
```jsx
// Xcode → Target → General → Identity → Bundle Identifier में लिखो
// Portal में App ID हाथ से या "Automatically manage signing" से बन जाएगी
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Bundle ID में underscore/space/capital की गड़बड़ी।
✅ Correct: lowercase, `.` और `-` का इस्तेमाल।

❌ Mistake 2: Portal की ID और app.json की ID अलग होना।
✅ Correct: हू-ब-हू एक जैसी रखो।

❌ Mistake 3: Wildcard ID पर Push enable करने की कोशिश।
✅ Correct: Push के लिए Explicit App ID।

---

## 🧠 Tricky Interview Question
Q: Release के बाद Bundle ID बदलना पड़े तो?

Answer: बदली नहीं जा सकती; नई Bundle ID = नया app। पुराने users, reviews, ratings, purchases नहीं जाते। इसलिए शुरू में ही सोचकर सही ID रखो।

---

## ⚫ Interview Questions + Answers
Q1: App ID और Bundle ID में फर्क?
A1: Bundle ID सिर्फ नाम है; App ID = Team ID prefix + Bundle ID + capabilities का portal record।

Q2: Explicit vs Wildcard?
A2: Explicit एक app, पूरी capabilities; Wildcard कई apps, सीमित capabilities।

Q3: Staging और production साथ कैसे चलाएँ?
A3: अलग Bundle IDs।

Q4: Team ID prefix क्यों?
A4: App ID का पूरा रूप `TEAMID.bundle.id` है, जो keychain sharing आदि में काम आता है।

Q5: Bundle ID कहाँ-कहाँ दिखती है?
A5: Xcode, Info.plist (CFBundleIdentifier), App Store Connect, provisioning profile।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- हर app में (अनिवार्य)।

❌ Avoid when:
- Wildcard पर निर्भर रहना जब Push/IAP चाहिए।

---

## 📊 Visual Diagram
```
 Team ID (ABCDE12345)
      +
 Bundle ID (com.mycompany.foodapp)
      +
 Capabilities (Push, SIWA)
      ▼
   App ID  ──► Provisioning Profile ──► Signed IPA
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Bundle ID | Reverse-DNS app name | app का unique नाम |
| App ID | Team+Bundle+Capabilities | पोर्टल का record |
| Explicit | Exact bundle id | सटीक ID |
| Wildcard | `*` वाली ID | कई apps की ID |
| Capability | Special feature | विशेष सुविधा |

---

## ⚡ 3-Line Summary
English: Bundle ID names the app; App ID adds Team ID and capabilities.
English: Use Explicit IDs for Push/IAP.
English: Bundle ID cannot be changed after release.
Hindi: Bundle ID नाम है; App ID में Team ID और capabilities जुड़ती हैं।
Hindi: Push/IAP के लिए Explicit ID।
Hindi: Release के बाद Bundle ID बदली नहीं जाती।

---

## ➡️ Next Topic
230. Provisioning Profiles — App ID + certificate को जोड़ने वाली फ़ाइल (पहले से notes में मौजूद); फिर 232 Xcode Setup।
