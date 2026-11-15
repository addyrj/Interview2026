# 200. App Icons Setup (Android)
# हिंदी में: Android में App Icon कैसे Set करें
# Platform: Android ✅ | iOS ✅ (अलग sizes/process)

> Target: **Expo SDK 52 (React Native 0.76)** — check current docs — APIs change between SDKs.

---

## 🔵 Simple Definition (English)
The app icon is the small picture on the phone's home screen and in the Play Store. In Expo you give one 1024x1024 PNG in `app.json`; for CLI you place many sizes in `mipmap-*` folders.

## 🔵 सरल परिभाषा (Hindi)
App icon वह छोटी तस्वीर है जो phone की home screen और Play Store में दिखती है। Expo में `app.json` में एक 1024x1024 PNG देते हैं; CLI में अलग-अलग sizes `mipmap-*` folders में रखते हैं।

---

## 🔴 Problem it Solves
- Phones have different screen densities (mdpi to xxxhdpi); one image looks blurry or huge.
- Launchers (Samsung, Pixel, Xiaomi) apply different shapes.
- Brand identity: a default RN logo looks unprofessional and fails store review quality checks.

## 🔴 यह क्यों बना? (Hindi)
- Phones की screen density अलग होती है; एक ही image कहीं blur तो कहीं बहुत बड़ी दिखती है।
- अलग launchers अलग shapes लगाते हैं।
- Brand पहचान के लिए default RN logo सही नहीं लगता।

---

## 🟢 How it Works — Step by Step
```
Step 1 → Design a 1024x1024 PNG (square, no transparency for legacy icon, no rounded corners)
Step 2 → Expo: set "icon": "./assets/icon.png" in app.json
Step 3 → Expo: set android.adaptiveIcon for Android 8+ (see topic 202)
Step 4 → EAS/prebuild resizes it into all mipmap densities automatically
Step 5 → CLI: put ic_launcher.png in each mipmap-* folder (or Android Studio Image Asset)
Step 6 → Rebuild the app (icon is native → no OTA update, no Fast Refresh)
Step 7 → Separately upload a 512x512 icon in Play Console store listing
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → 1024x1024 PNG बनाओ (square, rounded corners नहीं)
Step 2 → Expo: app.json में "icon" set करो
Step 3 → Android 8+ के लिए android.adaptiveIcon set करो (topic 202)
Step 4 → Build के समय सभी densities अपने आप बन जाती हैं
Step 5 → CLI: हर mipmap-* folder में ic_launcher.png रखो
Step 6 → App दोबारा build करो (icon native है, OTA से नहीं बदलता)
Step 7 → Play Console में 512x512 icon अलग से upload करो
```

---

## 🟡 Real World Example
**Zomato's** red icon and **Swiggy's** orange icon are the same artwork in every density. Their adaptive icons use a solid brand colour background and a white logo foreground so the shape (circle/squircle) can change per phone brand.

## 🟡 Real Example Hindi mein
**Zomato** का लाल और **Swiggy** का नारंगी icon हर density में एक ही artwork है। Adaptive icon में brand colour background और सफ़ेद logo foreground होता है ताकि हर phone पर shape (गोल/squircle) बदल सके।

---

## 💻 Code Example — Basic
Expo `app.json`:
```json
{
  "expo": {
    "name": "FoodApp",
    "slug": "food-app",
    "icon": "./assets/icon.png",
    "android": {
      "package": "com.mycompany.foodapp",
      "adaptiveIcon": {
        "foregroundImage": "./assets/adaptive-icon.png",
        "backgroundColor": "#E23744"
      }
    }
  }
}
```
Check asset sizes with a small Node script:
```js
// Node script: verify icon dimensions before building
// PNG width/height are stored at byte offsets 16 and 20 of the file
const fs = require('fs');                         // file system module

function pngSize(path) {                          // read PNG dimensions
  const buf = fs.readFileSync(path);              // load file bytes
  return { w: buf.readUInt32BE(16), h: buf.readUInt32BE(20) }; // width, height
}

const s = pngSize('./assets/icon.png');           // read the icon
console.log(s);                                   // print sizes
if (s.w !== 1024 || s.h !== 1024) {               // validate expected size
  console.error('Icon must be 1024x1024');        // show error
  process.exit(1);                                // fail the script (CI friendly)
}
```

## 💻 Code Example — Advanced
CLI densities (put files in `android/app/src/main/res/`) and manifest link:
```bash
# Required launcher sizes (px) per density folder
# mipmap-mdpi    48x48
# mipmap-hdpi    72x72
# mipmap-xhdpi   96x96
# mipmap-xxhdpi  144x144
# mipmap-xxxhdpi 192x192
# Generate them from one source with ImageMagick (if installed)
for d in "mdpi 48" "hdpi 72" "xhdpi 96" "xxhdpi 144" "xxxhdpi 192"; do
  set -- $d                                      # $1=density $2=size
  mkdir -p android/app/src/main/res/mipmap-$1    # create folder
  convert assets/icon.png -resize ${2}x${2} \
    android/app/src/main/res/mipmap-$1/ic_launcher.png  # resize and save
done
```
```xml
<!-- In AndroidManifest.xml <application> reference the icons -->
<application
    android:icon="@mipmap/ic_launcher"
    android:roundIcon="@mipmap/ic_launcher_round" />
```
Environment-specific icons in Expo (dev vs prod) using `app.config.js`:
```js
// app.config.js - dynamic config
const IS_DEV = process.env.APP_VARIANT === 'development'; // env switch

module.exports = {
  expo: {
    name: IS_DEV ? 'FoodApp (Dev)' : 'FoodApp',                       // name per variant
    slug: 'food-app',                                                  // project slug
    icon: IS_DEV ? './assets/icon-dev.png' : './assets/icon.png',      // different icon
    android: {
      package: IS_DEV ? 'com.mycompany.foodapp.dev' : 'com.mycompany.foodapp', // separate package
    },
  },
};
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Source in Expo | `icon` + `android.adaptiveIcon` | `icon` (1024x1024, no alpha) |
| Shape | Launcher decides (circle, squircle) | Always rounded square by OS |
| Transparency | Allowed in legacy; adaptive foreground transparent | Alpha NOT allowed |
| Folder (CLI) | `res/mipmap-*` | `Images.xcassets/AppIcon` |
| Store icon | 512x512 PNG in Play Console | 1024x1024 in App Store Connect |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// app.json -> "icon": "./assets/icon.png" (one file, auto-resized)
```
CLI way:
```jsx
// Android Studio -> right click res -> New -> Image Asset
// or manually place PNGs in mipmap-mdpi ... mipmap-xxxhdpi
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Changing icon and expecting it in Expo Go / OTA update.
✅ Correct: Icon is native; create a new build (`eas build`).

❌ Mistake 2: Using a non-square or low-res image.
✅ Correct: 1024x1024 square PNG.

❌ Mistake 3: Putting text near the edge; launcher masks it.
✅ Correct: Keep logo inside the centre safe zone.

❌ Mistake 4: Old icon cached after reinstall on emulator.
✅ Correct: Uninstall the app and reinstall; clear launcher cache.

---

## 🧠 Tricky Interview Question
"You updated `icon.png` and published an OTA update with `eas update`. Users still see the old icon. Why?"

Answer: Icons are part of the native binary resources. OTA updates only replace JS bundle and JS-loaded assets. A new store build is required.

---

## ⚫ Interview Questions + Answers
Q1: Which size does Expo expect for icon?
A1: 1024x1024 PNG.

Q2: What is `roundIcon`?
A2: A circular version used by some launchers (Android 7.1); adaptive icons made it largely unnecessary.

Q3: What are mipmap folders?
A3: Resource folders per density; launcher icons go into `mipmap` (not `drawable`) so launchers can scale them.

Q4: How to have different icons for dev and prod builds?
A4: Use `app.config.js` with env variable and distinct package names.

Q5: What icon does Play Store need?
A5: 512x512 PNG (32-bit, up to 1024 KB) in the store listing — different from the in-app icon.

---

## 🔷 When to Use + When Not to Use
✅ Use when: preparing any release build.

❌ Avoid when: expecting hot reload to show icon changes.

---

## 📊 Visual Diagram
```
 icon.png (1024x1024)
        │ prebuild / EAS
        ▼
 ┌─────────┬─────────┬─────────┬──────────┬───────────┐
 │ mdpi 48 │ hdpi 72 │ xhdpi 96│ xxhdpi144│ xxxhdpi192│
 └─────────┴─────────┴─────────┴──────────┴───────────┘
        │
        ▼ ic_launcher in AndroidManifest
     Home screen icon
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| mipmap | Icon resource folders | Icon resource folders |
| Density | Pixels per inch class | Pixel density वर्ग |
| Adaptive icon | Foreground + background layers | दो layers वाला icon |
| Launcher | Home screen app | Home screen app |

---

## ⚡ 3-Line Summary
English: Provide a 1024x1024 icon in `app.json` for Expo; CLI needs mipmap folders.
Icon is native, so rebuild is required.
Upload separate 512x512 icon to Play Console.

Hindi: Expo में 1024x1024 icon `app.json` में दो; CLI में mipmap folders चाहिए।
Icon native है इसलिए rebuild ज़रूरी है।
Play Console में 512x512 icon अलग से डालो।

---

## ➡️ Next Topic
**201. Splash Screen Setup (Android)** — app खुलते समय की पहली screen।
