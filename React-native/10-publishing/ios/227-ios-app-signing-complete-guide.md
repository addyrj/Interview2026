# 227. iOS App Signing — Complete Guide
# हिंदी में: iOS App Signing पूरी गाइड
# Platform: Android ❌ | iOS ✅

> Expo SDK 52+ (React Native 0.76+)। Expo SDK 52 (check current docs — APIs change between SDKs). Xcode/Apple portal के menu नाम version के साथ बदलते हैं।

---

## 🔵 Simple Definition (English)
App signing is Apple's way of proving **who built the app** and that it was **not tampered with**. Every iOS app must be signed with a certificate (identity) and a provisioning profile (permission slip) before it can run on a device or go to the App Store.

## 🔵 सरल परिभाषा (Hindi)
App signing Apple का तरीका है यह साबित करने का कि app **किसने बनाया** और बीच में **बदला नहीं गया**। हर iOS app को certificate (पहचान) और provisioning profile (अनुमति-पर्ची) से sign करना ज़रूरी है, तभी वह device पर चलेगा या App Store जाएगा।

---

## 🔴 Problem it Solves
- Malware वाले fake apps को रोकना।
- यह तय करना कि कौन-सा app किस device पर और किस developer की तरफ से चल सकता है।
- App update सिर्फ वही developer भेज सके जिसने original app बनाया।

## 🔴 यह क्यों बना? (Hindi)
Apple हर app को verify करना चाहता है। बिना signature के iOS app खोलेगा ही नहीं। Signing से Apple को पता रहता है कि app किसका है, किन capabilities (Push, iCloud) के साथ है और किन devices पर test हो सकता है।

---

## 🟢 How it Works — Step by Step

```
चार हिस्से मिलकर signing बनाते हैं:

 1. Certificate      = "मैं कौन हूँ" (private key आपके Mac में)
 2. App ID/Bundle ID = "यह कौन-सा app है" (com.company.app)
 3. Devices          = "किन phones पर चलेगा" (सिर्फ Development/Ad Hoc)
 4. Provisioning Profile = ऊपर के तीनों को जोड़ने वाली फ़ाइल (.mobileprovision)

Step 1 → Certificate बनाओ (CSR से)
Step 2 → App ID रजिस्टर करो
Step 3 → Profile बनाओ (cert + App ID + devices)
Step 4 → Build के समय Xcode/EAS app को cert से sign करता है और profile embed करता है
Step 5 → Device/Apple verify करता है → चलने देता है
```

## 🟢 कैसे काम करता है? (Hindi)
Build के अंत में app binary पर आपके certificate की private key से digital signature लगता है। साथ में provisioning profile app के अंदर रखी जाती है। iOS खोलते समय जाँचता है: signature सही है? profile valid है? Bundle ID match करता है? device list में है (dev हो तो)? सब हाँ → app चलता है।

---

## 🟡 Real World Example
Paytm की iOS team में 10 developers हैं। सबके Macs में अलग private keys होती थीं और बार-बार "No signing certificate" error आता था। फिर उन्होंने shared Distribution certificate (.p12) एक secure vault में रखा और CI (GitHub Actions/EAS) से signing कराई — अब हर release एक जैसा चलता है।

## 🟡 Real Example Hindi mein
Zomato की release pipeline में signing certificate CI के secrets में रखा है। कोई भी developer अपने laptop से सीधे App Store build नहीं निकालता — सब CI से होता है, इसलिए "मेरे Mac पर चल रहा था" वाली समस्या नहीं।

---

## 💻 Code Example — Basic
```jsx
// Expo में signing सबसे आसान: EAS सब बनाता है
// Terminal commands:
// eas build --platform ios --profile production   // पहली बार: Apple login → cert + profile auto बनेंगे
// eas credentials                                  // existing credentials देखो/बदलो

// eas.json (JSON, comment रूप में):
// {
//   "build": {
//     "production": {
//       "ios": { "credentialsSource": "remote" }   // EAS server पर credentials रखो (default)
//     }
//   }
// }
```

## 💻 Code Example — Advanced
```jsx
// Local credentials (अपनी .p12 और profile) इस्तेमाल करना — credentials.json
// {
//   "ios": {
//     "provisioningProfilePath": "ios/certs/profile.mobileprovision", // profile फ़ाइल path
//     "distributionCertificate": {
//       "path": "ios/certs/dist.p12",       // certificate + private key
//       "password": "ENV_OR_PROMPT"         // असली password repo में कभी commit मत करो
//     }
//   }
// }
// eas.json में: "ios": { "credentialsSource": "local" }

// Signing verify करने की shell commands (Mac पर):
// security find-identity -v -p codesigning        // Keychain में उपलब्ध signing identities
// codesign -dv --verbose=4 MyApp.app              // built app की signature देखो
// security cms -D -i profile.mobileprovision      // profile की content decode करो

// Node में profile expiry जाँच (decoded plist को JSON में बदलकर):
const expiry = new Date('2027-01-01'); // profile की ExpirationDate यहाँ डालो
const daysLeft = Math.floor((expiry - new Date()) / 86400000); // बचे दिन
console.log(daysLeft < 30 ? 'Profile जल्द expire होगी' : 'OK'); // चेतावनी या ठीक
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Signing asset | एक keystore (.jks) | Certificate + Provisioning Profile |
| कौन जारी करता है | आप खुद (या Play App Signing) | Apple |
| Expiry | Keystore ~25+ साल | Certificate 1 साल, profile 1 साल |
| Key खोए तो | Play App Signing से recovery संभव | Revoke करके नया cert बना सकते हैं |
| Device restriction | नहीं | Dev/AdHoc में UDID list |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// EAS Build: credentials अपने आप, remote store
// eas build --platform ios
```
CLI way:
```jsx
// CLI: Xcode → Signing & Capabilities → ✔ Automatically manage signing → Team चुनो
// या manual: certificate + profile खुद download करके Xcode में चुनो
// Archive: Product → Archive
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: .p12 / private key बैकअप न रखना।
✅ Correct: Keychain से .p12 export करके secure vault में रखो; वरना दूसरे Mac से sign नहीं हो पाएगा।

❌ Mistake 2: Development profile से App Store build करना।
✅ Correct: Store के लिए Distribution cert + App Store profile।

❌ Mistake 3: Certificates को Git में commit करना।
✅ Correct: Secrets manager / EAS remote credentials।

---

## 🧠 Tricky Interview Question
Q: Certificate valid है, फिर भी build में "No profile matching" error आ रहा है। क्यों?

Answer: Profile में bundle ID या certificate मेल नहीं खाता, या profile expire/revoked है, या capability (Push) profile में enabled नहीं है। Fix: portal में profile regenerate करो, सही cert attach करो और Xcode में refresh।

---

## ⚫ Interview Questions + Answers
Q1: Certificate और Provisioning Profile में फर्क?
A1: Certificate = developer की पहचान; Profile = app + cert + devices + entitlements को जोड़ने वाली अनुमति।

Q2: CSR क्या है?
A2: Certificate Signing Request — Keychain Access में बनती है, जिससे Apple certificate जारी करता है।

Q3: Automatic vs Manual signing?
A3: Automatic में Xcode/EAS सब बनाता है; Manual में आप खुद certs/profiles चुनते हैं (CI में अक्सर manual)।

Q4: Entitlements क्या हैं?
A4: App की विशेष क्षमताएँ (Push, Sign in with Apple, App Groups) जो profile में allow होनी चाहिए।

Q5: Certificate expire हो तो?
A5: पहले से बने app users के लिए चलता रहता है, पर नया build/update नए cert से करना होगा।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- हर real device build, TestFlight और App Store build पर (ज़रूरी)।

❌ Avoid when:
- Simulator build — signing की ज़रूरत नहीं।

---

## 📊 Visual Diagram
```
 Certificate (cert + private key) ─┐
 App ID (com.x.app + capabilities) ─┼─► Provisioning Profile ─► Xcode/EAS signs IPA ─► iOS verifies
 Devices UDID (dev/adhoc only) ─────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Certificate | Developer identity | डेवलपर की पहचान |
| Provisioning Profile | Permission file | अनुमति फ़ाइल |
| CSR | Cert request | certificate अनुरोध |
| Entitlement | Special capability | विशेष क्षमता |
| UDID | Device unique id | device की unique ID |

---

## ⚡ 3-Line Summary
English: Signing = certificate + App ID + profile (+ devices).
English: Apple verifies the signature before the app runs.
English: Use EAS remote credentials or CI to avoid key chaos.
Hindi: Signing = certificate + App ID + profile (+ devices)।
Hindi: चलने से पहले Apple signature verify करता है।
Hindi: EAS remote credentials/CI से key की गड़बड़ी से बचो।

---

## ➡️ Next Topic
228. Certificates (Development + Distribution) — दोनों certificates कैसे बनाते हैं।
