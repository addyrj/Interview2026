# 235. App Icons Setup (iOS)
# हिंदी में: iOS App Icons सेटअप
# Platform: Android ❌ (अलग adaptive icon) | iOS ✅

> Expo SDK 52+ (React Native 0.76+)। Expo SDK 52 (check current docs — APIs change between SDKs). iOS 18 के dark/tinted icon variants के config keys SDK के साथ बदल सकते हैं — Expo docs verify करें।

---

## 🔵 Simple Definition (English)
The iOS app icon is the picture on the home screen and App Store. Apple needs a **1024×1024 px PNG with no transparency (no alpha) and no rounded corners** — iOS rounds the corners itself. Xcode/Expo generates the smaller sizes.

## 🔵 सरल परिभाषा (Hindi)
iOS app icon home screen और App Store पर दिखने वाली तस्वीर है। Apple को **1024×1024 px PNG चाहिए, बिना transparency (alpha) और बिना गोल कोनों के** — कोने iOS खुद गोल करता है। छोटे sizes Xcode/Expo अपने आप बनाते हैं।

---

## 🔴 Problem it Solves
- अलग-अलग devices (iPhone, iPad, Spotlight, Settings) के लिए कई sizes चाहिए थे।
- गलत icon format पर App Store upload fail होता है।

## 🔴 यह क्यों बना? (Hindi)
पहले हर size हाथ से बनानी पड़ती थी। अब एक बड़ी 1024 image से सब sizes generate होते हैं (single-size asset catalog)।

---

## 🟢 How it Works — Step by Step

```
Step 1 → 1024×1024 PNG बनाओ (RGB, alpha channel नहीं, कोने चौकोर)
Step 2 → Expo: ./assets/icon.png रखो, app.json में "icon": "./assets/icon.png"
Step 3 → (वैकल्पिक) iOS के लिए अलग: "ios": { "icon": "./assets/ios-icon.png" }
Step 4 → eas build / prebuild → AppIcon asset catalog अपने आप बनता है
Step 5 → CLI: Xcode → Images.xcassets → AppIcon → 1024 image ड्रैग करो
Step 6 → Device/TestFlight पर जाँचो
```

## 🟢 कैसे काम करता है? (Hindi)
Expo prebuild के समय `icon` से `ios/<App>/Images.xcassets/AppIcon.appiconset` बनता है। iOS 11+ में सिर्फ 1024 icon देना काफी है (Xcode 14+ single size)। iOS corner mask खुद लगाता है, इसलिए खुद गोल कोने बनाओगे तो किनारे पर सफेद/काले कोने दिखेंगे।
**Xcode screen:** Images.xcassets में AppIcon चुनो; बीच में एक बड़ा खाना "App Icon – 1024pt" जिसमें image drop करते हैं; दाईं तरफ Attributes inspector में "iOS: Single Size" विकल्प।

---

## 🟡 Real World Example
Swiggy का नारंगी icon चौकोर 1024 PNG होता है; iOS उसे rounded square में काटता है। Festival sale में icon बदलना हो तो नया binary चाहिए (alternate icons को छोड़कर)।

## 🟡 Real Example Hindi mein
Zomato का लाल icon सिर्फ एक 1024 PNG से बनता है; डिज़ाइनर alpha हटाकर export करता है ताकि App Store Connect upload में "Invalid icon" error न आए।

---

## 💻 Code Example — Basic
```jsx
// app.json — icon config
// {
//   "expo": {
//     "icon": "./assets/icon.png",            // सभी platforms का default icon (1024x1024)
//     "ios": {
//       "icon": "./assets/ios-icon.png"       // सिर्फ iOS के लिए (वैकल्पिक override)
//     }
//   }
// }

// Alpha channel हटाने का Mac command (ImageMagick installed हो तो):
// magick icon.png -background white -alpha remove -alpha off icon-noalpha.png
// Size जाँचो:
// sips -g pixelWidth -g pixelHeight -g hasAlpha icon.png   // macOS built-in
```

## 💻 Code Example — Advanced
```jsx
// Node script: icon validate (CI में) — sharp library: npm i -D sharp
const sharp = require('sharp'); // image library

async function validateIcon(path) { // icon जाँचने वाला function
  const meta = await sharp(path).metadata(); // image metadata पढ़ो
  const errors = []; // त्रुटियों की list
  if (meta.width !== 1024 || meta.height !== 1024) errors.push('Size 1024x1024 होना चाहिए'); // size
  if (meta.hasAlpha) errors.push('Alpha channel हटाओ (iOS में transparency मना)'); // alpha
  if (meta.format !== 'png') errors.push('PNG format चाहिए'); // format
  if (errors.length) throw new Error(errors.join(' | ')); // त्रुटि तो fail
  return 'Icon OK'; // सब ठीक
}

validateIcon('./assets/icon.png') // चलाओ
  .then(console.log) // सफलता
  .catch((e) => { console.error(e.message); process.exit(1); }); // CI fail

// iOS 18 dark/tinted variants के लिए Expo config options SDK के अनुसार अलग हैं —
// docs.expo.dev/develop/user-interface/app-icons देखो (यहाँ key अंदाज़े से नहीं लिखी)।
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Icon type | Adaptive (foreground + background layers) | एक चौकोर 1024 PNG |
| Corners | Launcher mask करता है | iOS गोल करता है |
| Transparency | foreground में allowed | मना (no alpha) |
| Config key | `android.adaptiveIcon` | `icon` / `ios.icon` |
| Store icon | 512×512 PNG | 1024×1024 PNG |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// app.json: "icon": "./assets/icon.png"  → build पर सब sizes अपने आप
```
CLI way:
```jsx
// Xcode → Images.xcassets → AppIcon → 1024 PNG drop
// या अलग-अलग sizes के लिए online/CLI generators
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Transparent PNG देना।
✅ Correct: Alpha हटाकर solid background।

❌ Mistake 2: खुद गोल कोने बनाना।
✅ Correct: चौकोर image दो।

❌ Mistake 3: Icon बदलकर सिर्फ OTA update भेजना।
✅ Correct: Icon native asset है — नया build चाहिए।

---

## 🧠 Tricky Interview Question
Q: App Store Connect "Invalid large app icon" दिखाता है जबकि image 1024×1024 है। कारण?

Answer: सबसे आम कारण alpha channel (transparency) है। Image को alpha हटाकर export करो; कभी colour profile या format (PNG न होना) भी कारण होता है।

---

## ⚫ Interview Questions + Answers
Q1: iOS icon का सही size?
A1: 1024×1024 PNG, no alpha।

Q2: Rounded corners कौन देता है?
A2: iOS खुद।

Q3: Icon बदलने के लिए OTA चलेगा?
A3: नहीं, native asset है।

Q4: Android से फर्क?
A4: Android adaptive layers; iOS एक image।

Q5: Icon कहाँ बनता है?
A5: Images.xcassets/AppIcon।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- हर app में अनिवार्य।

❌ Avoid when:
- Transparent/rounded/text-heavy icon (Apple guideline के खिलाफ)।

---

## 📊 Visual Diagram
```
 icon.png (1024, no alpha) ─► prebuild ─► AppIcon.appiconset ─► IPA ─► iOS rounds corners ─► Home screen
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Alpha | Transparency channel | पारदर्शिता चैनल |
| Asset catalog | Xcode image store | Xcode का image भंडार |
| AppIcon | Icon set name | icon सेट |
| 1024pt | App Store icon size | App Store icon size |
| Mask | Corner shape | कोनों का आकार |

---

## ⚡ 3-Line Summary
English: Use a 1024×1024 PNG without alpha or rounded corners.
English: Expo generates all sizes from app.json icon.
English: Icon changes need a new native build.
Hindi: 1024×1024 PNG, बिना alpha और गोल कोनों के।
Hindi: Expo app.json के icon से सब sizes बनाता है।
Hindi: Icon बदलने पर नया native build चाहिए।

---

## ➡️ Next Topic
236. Splash Screen Setup (iOS) — app खुलते समय की पहली screen।
