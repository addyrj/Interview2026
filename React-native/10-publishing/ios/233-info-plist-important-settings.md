# 233. Info.plist — Important Settings
# हिंदी में: Info.plist की ज़रूरी settings
# Platform: Android ❌ (Android में AndroidManifest.xml) | iOS ✅

> Expo SDK 52+ (React Native 0.76+)। Expo SDK 52 (check current docs — APIs change between SDKs). Expo में `ios.infoPlist` और `ios.config` के keys docs से verify करें।

---

## 🔵 Simple Definition (English)
`Info.plist` is an XML file inside every iOS app that tells the system the app's name, version, bundle ID, permission messages, supported orientations and other settings. In Expo you rarely edit it directly — you set values in `app.json` (`ios.infoPlist`).

## 🔵 सरल परिभाषा (Hindi)
`Info.plist` हर iOS app के अंदर की XML फ़ाइल है जो system को app का नाम, version, bundle ID, permission messages, orientations और बाकी settings बताती है। Expo में इसे सीधे नहीं बदलते — `app.json` के `ios.infoPlist` में values देते हैं।

---

## 🔴 Problem it Solves
- iOS को app चलाने से पहले उसके बारे में metadata चाहिए।
- बिना permission description (usage string) के app crash या App Store reject होता है।

## 🔴 यह क्यों बना? (Hindi)
Apple privacy के लिए user को बताना ज़रूरी करता है कि आप camera/location क्यों माँग रहे हैं। यह कारण Info.plist में लिखा जाता है और popup में दिखता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Build के समय iOS Info.plist पढ़ता है
Step 2 → Name/Version/Bundle ID से app की पहचान
Step 3 → NS...UsageDescription keys से permission popup का text
Step 4 → UIBackgroundModes, LSApplicationQueriesSchemes आदि से capabilities
Step 5 → App Store upload पर Apple इन्हें validate करता है
```

## 🟢 कैसे काम करता है? (Hindi)
ज़रूरी keys:
- `CFBundleDisplayName` — home screen पर नाम
- `CFBundleIdentifier` — Bundle ID
- `CFBundleShortVersionString` — user को दिखने वाला version (1.2.0)
- `CFBundleVersion` — build number (हर upload पर बढ़ाओ)
- `NSCameraUsageDescription`, `NSPhotoLibraryUsageDescription`, `NSLocationWhenInUseUsageDescription`, `NSMicrophoneUsageDescription` — permission कारण
- `ITSAppUsesNonExemptEncryption` — export compliance (अक्सर `false`)
- `UIBackgroundModes` — background audio/location/fetch/remote-notification
- `LSApplicationQueriesSchemes` — `Linking.canOpenURL` के लिए whitelist (जैसे `whatsapp`, `tez`)
- `UISupportedInterfaceOrientations` — orientation
**Xcode में:** Target → Info tab में key-value list दिखती है (Xcode में keys का दोस्ताना नाम जैसे "Privacy - Camera Usage Description")।

---

## 🟡 Real World Example
Swiggy का map screen location माँगता है। Info.plist में `NSLocationWhenInUseUsageDescription` = "आपके पास के restaurants दिखाने के लिए location चाहिए"। यह text popup में दिखता है; text vague हो तो Apple review reject कर सकता है।

## 🟡 Real Example Hindi mein
Paytm UPI apps खोलने के लिए `Linking.canOpenURL('phonepe://')` इस्तेमाल करे तो `LSApplicationQueriesSchemes` में `phonepe` जोड़ना होगा, वरना iOS हमेशा false देगा।

---

## 💻 Code Example — Basic
```jsx
// app.json (Expo) — Info.plist की values यहाँ
// {
//   "expo": {
//     "ios": {
//       "bundleIdentifier": "com.mycompany.foodapp",          // CFBundleIdentifier
//       "buildNumber": "3",                                    // CFBundleVersion
//       "infoPlist": {
//         "NSCameraUsageDescription": "खाने की फोटो लेने के लिए camera चाहिए",       // camera कारण
//         "NSLocationWhenInUseUsageDescription": "पास के restaurants दिखाने के लिए", // location कारण
//         "LSApplicationQueriesSchemes": ["whatsapp", "tez"],  // canOpenURL whitelist
//         "UIBackgroundModes": ["remote-notification"]         // push के लिए background mode
//       },
//       "config": { "usesNonExemptEncryption": false }         // ITSAppUsesNonExemptEncryption=false
//     }
//   }
// }
```

## 💻 Code Example — Advanced
```jsx
// Bare CLI में ios/MyApp/Info.plist (XML) का हिस्सा
// <key>CFBundleDisplayName</key>
// <string>Food App</string>                                  <!-- home screen नाम -->
// <key>NSCameraUsageDescription</key>
// <string>खाने की फोटो लेने के लिए camera चाहिए</string>       <!-- camera कारण -->
// <key>ITSAppUsesNonExemptEncryption</key>
// <false/>                                                   <!-- सिर्फ standard HTTPS encryption हो तो -->
// <key>LSApplicationQueriesSchemes</key>
// <array><string>whatsapp</string></array>                   <!-- whitelist -->

// Dynamic config (app.config.js) — env के अनुसार
export default ({ config }) => ({ // Expo config function
  ...config, // बाकी config
  ios: {
    ...config.ios, // iOS बाकी
    infoPlist: {
      ...(config.ios?.infoPlist ?? {}), // पुरानी infoPlist बनाए रखो
      NSCameraUsageDescription: 'Camera का उपयोग फोटो खींचने के लिए होता है', // कारण
    },
  },
});
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Config file | AndroidManifest.xml | Info.plist |
| Permission reason text | ज़रूरी नहीं (system popup) | ज़रूरी usage description |
| URL scheme query | `<queries>` tag | LSApplicationQueriesSchemes |
| Version | versionName / versionCode | ShortVersion / CFBundleVersion |
| Missing key का असर | Runtime में permission नहीं | Crash या App Store reject |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// app.json → ios.infoPlist  (prebuild पर Info.plist में merge होता है)
// कई Expo plugins (expo-camera आदि) अपने keys के लिए options देते हैं
```
CLI way:
```jsx
// ios/<App>/Info.plist सीधे Xcode (Info tab) या text editor से edit
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Usage description ख़ाली या "Need camera" जैसी vague।
✅ Correct: साफ़ कारण लिखो कि feature में क्यों चाहिए।

❌ Mistake 2: `CFBundleVersion` वही रखना।
✅ Correct: हर upload पर बढ़ाओ।

❌ Mistake 3: ज़रूरत न होने पर भी बहुत सारी permissions जोड़ना।
✅ Correct: सिर्फ वही जो इस्तेमाल हो — नहीं तो review में सवाल।

---

## 🧠 Tricky Interview Question
Q: `Linking.canOpenURL('whatsapp://')` iOS पर हमेशा false देता है, Android पर true। क्यों?

Answer: iOS में `LSApplicationQueriesSchemes` में scheme whitelist होना ज़रूरी है (privacy)। जोड़ने के बाद app rebuild करो। Android 11+ पर भी `<queries>` चाहिए होता है।

---

## ⚫ Interview Questions + Answers
Q1: Info.plist क्या है?
A1: iOS app की metadata/config XML फ़ाइल।

Q2: Expo में कैसे बदलें?
A2: `app.json` → `ios.infoPlist`।

Q3: ITSAppUsesNonExemptEncryption क्या?
A3: Export compliance flag; सिर्फ standard HTTPS हो तो `false` रखने से हर बार सवाल नहीं पूछा जाता।

Q4: CFBundleVersion vs CFBundleShortVersionString?
A4: पहला build number, दूसरा user-visible version।

Q5: Permission string न दें तो?
A5: iOS app को crash कर सकता है और App Store rejection होगा।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Permissions, URL schemes, background modes, orientation सेट करने हों।

❌ Avoid when:
- Expo managed में हाथ से Info.plist edit करना (prebuild पर overwrite होगा) — config use करो।

---

## 📊 Visual Diagram
```
 app.json (ios.infoPlist) ──prebuild──► Info.plist ──build──► IPA ──► iOS reads ──► popup text / behavior
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| plist | Property list XML | गुण-सूची फ़ाइल |
| Usage Description | Permission reason | permission का कारण |
| CFBundleVersion | Build number | build नंबर |
| UIBackgroundModes | Background abilities | background क्षमताएँ |
| Export compliance | Encryption declaration | encryption घोषणा |

---

## ⚡ 3-Line Summary
English: Info.plist holds app metadata and permission texts.
English: In Expo, edit it through app.json ios.infoPlist.
English: Missing keys cause crashes or rejection.
Hindi: Info.plist में app का metadata और permission text होता है।
Hindi: Expo में app.json के ios.infoPlist से बदलो।
Hindi: Keys न हों तो crash या rejection।

---

## ➡️ Next Topic
234. App Permissions in iOS — permission माँगने का सही तरीका।
