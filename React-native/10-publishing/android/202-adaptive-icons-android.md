# 202. Adaptive Icons (Android)
# हिंदी में: Android Adaptive Icons
# Platform: Android ✅ (API 26 / Android 8+) | iOS ❌

> Target: **Expo SDK 52 (React Native 0.76)** — check current docs — APIs change between SDKs. `monochromeImage` (themed icons, Android 13+) is available in recent SDKs; verify for yours.

---

## 🔵 Simple Definition (English)
An adaptive icon has two layers — a foreground (logo) and a background. The phone's launcher masks them into a circle, squircle or square and can animate them (parallax).

## 🔵 सरल परिभाषा (Hindi)
Adaptive icon में दो layers होती हैं — foreground (logo) और background। Phone का launcher इन्हें गोल, squircle या square shape में काटता है और animation भी दे सकता है।

---

## 🔴 Problem it Solves
- Each phone brand wanted its own icon shape; plain PNG icons looked inconsistent (white box inside a circle).
- Android 8 introduced adaptive icons to unify shapes while keeping branding.
- Android 13 added themed (monochrome) icons that follow wallpaper colours.

## 🔴 यह क्यों बना? (Hindi)
- हर phone brand अपनी shape चाहता था; साधारण PNG कहीं सफ़ेद box जैसा दिखता था।
- Android 8 ने adaptive icons से shapes एक जैसी कीं।
- Android 13 में themed (monochrome) icons आए जो wallpaper के रंग लेते हैं।

---

## 🟢 How it Works — Step by Step
```
Step 1 → Canvas is 108x108 dp per layer
Step 2 → Only the centre 72x72 dp is always visible
Step 3 → Safe zone for logo: centre 66x66 dp circle (so no mask cuts it)
Step 4 → Outer 18dp each side is for parallax/animation and gets cropped
Step 5 → Launcher applies mask (circle/squircle) over both layers
Step 6 → Expo: provide foregroundImage (+ backgroundColor or backgroundImage)
Step 7 → For Android 13 themed icon: provide monochromeImage (single colour, transparent bg)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → हर layer का canvas 108x108 dp
Step 2 → बीच का 72x72 dp हमेशा दिखता है
Step 3 → Logo के लिए safe zone: बीच का 66x66 dp circle
Step 4 → बाहर के 18dp parallax के लिए हैं और कट जाते हैं
Step 5 → Launcher दोनों layers पर mask लगाता है
Step 6 → Expo: foregroundImage + backgroundColor/backgroundImage दो
Step 7 → Android 13 themed icon के लिए monochromeImage दो
```

---

## 🟡 Real World Example
**Paytm**'s blue background with white-and-blue logo remains crisp as a circle on Pixel and squircle on Samsung. **Zomato** uses a solid red background layer + white wordmark foreground; the logo stays inside the safe zone so it is never clipped.

## 🟡 Real Example Hindi mein
**Paytm** का नीला background और logo Pixel पर गोल और Samsung पर squircle में साफ़ दिखता है। **Zomato** लाल background layer और सफ़ेद wordmark foreground रखता है; logo safe zone में रहता है इसलिए कटता नहीं।

---

## 💻 Code Example — Basic
```json
{
  "expo": {
    "android": {
      "adaptiveIcon": {
        "foregroundImage": "./assets/adaptive-icon.png",
        "backgroundColor": "#E23744"
      }
    }
  }
}
```
Foreground file: 1024x1024 PNG, transparent background, logo inside centre ~66% area.

## 💻 Code Example — Advanced
With background image and themed icon, plus CLI XML:
```json
{
  "expo": {
    "icon": "./assets/icon.png",
    "android": {
      "adaptiveIcon": {
        "foregroundImage": "./assets/adaptive-foreground.png",
        "backgroundImage": "./assets/adaptive-background.png",
        "monochromeImage": "./assets/adaptive-monochrome.png"
      }
    }
  }
}
```
```xml
<!-- CLI: res/mipmap-anydpi-v26/ic_launcher.xml -->
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <!-- Background layer (colour from res/values/ic_launcher_background.xml) -->
    <background android:drawable="@color/ic_launcher_background"/>
    <!-- Foreground layer (PNG/vector in drawable) -->
    <foreground android:drawable="@mipmap/ic_launcher_foreground"/>
    <!-- Android 13+ themed icon layer -->
    <monochrome android:drawable="@mipmap/ic_launcher_monochrome"/>
</adaptive-icon>
```
Safe-zone check script (Node, checks that outer 17% border of foreground is transparent is not trivial without a PNG decoder, so just check size):
```js
// Verify foreground is square and large enough
const fs = require('fs');                                   // file system
const buf = fs.readFileSync('./assets/adaptive-foreground.png'); // read bytes
const w = buf.readUInt32BE(16), h = buf.readUInt32BE(20);   // PNG width/height
if (w !== h || w < 1024) throw new Error('Use square 1024+ px foreground'); // validate
console.log('OK', w, h);                                    // success message
```

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Layers | Foreground + background (+ monochrome) | Single flat image |
| Shape | Launcher-controlled mask | Fixed rounded square |
| Animation | Parallax/pulse by launcher | None |
| Themed icon | Android 13+ monochrome | iOS 18 tinted/dark variants (separate asset) |
| Min version | API 26 | n/a |

---

## 🟠 Expo vs CLI Difference
Expo way:
```jsx
// app.json -> android.adaptiveIcon.{foregroundImage, backgroundColor}
```
CLI way:
```jsx
// Android Studio -> New -> Image Asset -> Launcher Icons (Adaptive and Legacy)
// edits mipmap-anydpi-v26/ic_launcher.xml
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Full-bleed logo in foreground — edges clipped.
✅ Correct: Keep logo inside 66dp safe zone (~61% of canvas).

❌ Mistake 2: Foreground with opaque white background.
✅ Correct: Transparent foreground; put colour in background layer.

❌ Mistake 3: Using the same file for `icon` and foreground without checking.
✅ Correct: Make separate assets for each.

❌ Mistake 4: Monochrome image with multiple colours.
✅ Correct: Single colour silhouette, transparent elsewhere.

---

## 🧠 Tricky Interview Question
"Why does your logo look tiny in the adaptive icon even though it filled the PNG?"

Answer: Only 72 of 108 dp (66%) is guaranteed visible and the logo must live in the 66dp safe zone, so launcher/design guidelines require padding around the logo. Design with padding, not edge-to-edge.

---

## ⚫ Interview Questions + Answers
Q1: Adaptive icon canvas size?
A1: 108x108 dp per layer; visible area 72x72 dp.

Q2: Min Android version?
A2: Android 8.0 (API 26); older uses the legacy `icon`.

Q3: What is monochrome layer?
A3: Android 13+ themed icon that tints with user's wallpaper palette.

Q4: Can the adaptive icon be changed by OTA?
A4: No — native resource.

Q5: Which Expo keys?
A5: `android.adaptiveIcon.foregroundImage`, `backgroundColor`, `backgroundImage`, `monochromeImage`.

---

## 🔷 When to Use + When Not to Use
✅ Use when: always for Android release (API 26+ is almost all devices).

❌ Avoid when: you need a precise shape — you cannot force a shape.

---

## 📊 Visual Diagram
```
 108dp canvas
 ┌──────────────────────┐
 │  parallax margin 18  │
 │   ┌──────────────┐   │
 │   │ visible 72dp │   │
 │   │  ┌────────┐  │   │
 │   │  │safe 66 │  │   │   foreground + background
 │   │  │ LOGO   │  │   │   ─► mask (circle/squircle) ─► Home screen
 │   │  └────────┘  │   │
 │   └──────────────┘   │
 └──────────────────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Adaptive icon | Layered icon | Layers वाला icon |
| Safe zone | Never-clipped centre | कभी न कटने वाला centre |
| Mask | Shape applied by launcher | Launcher की shape |
| Monochrome | Single-colour themed layer | एक रंग की themed layer |

---

## ⚡ 3-Line Summary
English: Adaptive icons = foreground + background layers masked by launcher.
Keep logo in the centre safe zone; add monochrome for Android 13.
Configure under `android.adaptiveIcon` in Expo.

Hindi: Adaptive icon = foreground + background layers जिन पर launcher mask लगाता है।
Logo को बीच के safe zone में रखो; Android 13 के लिए monochrome जोड़ो।
Expo में `android.adaptiveIcon` में configure करो।

---

## ➡️ Next Topic
**203. Build Release APK (Expo)** — अब app को build करके install करने लायक file बनाना।
