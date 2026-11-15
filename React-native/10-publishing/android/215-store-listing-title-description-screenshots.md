---

# 215. Store Listing (Title, Description, Screenshots)
# हिंदी में: Store Listing (Title, Description, Screenshots)
# Platform: Android ✅ | iOS ❌ (iOS me App Store Connect "App Information/Version" page)

> Expo SDK 53/54 (check current docs — APIs change between SDKs). Character limits aur image sizes Google time-time par update karta hai — Console me dikhe limits ko final maano.

---

## 🔵 Simple Definition (English)
The **store listing** is your app's public page on Google Play: title, short description, full description, icon, feature graphic, and screenshots. It decides whether a visitor taps **Install**. Common limits: title 30 chars, short description 80, full description 4000.

## 🔵 सरल परिभाषा (Hindi)
**Store listing** Google Play पर आपकी app का public page है: title, short description, full description, icon, feature graphic और screenshots। इसी से तय होता है कि visitor **Install** दबाएगा या नहीं। आम limits: title 30 characters, short description 80, full description 4000।

---

## 🔴 Problem it Solves
- Users decide in seconds; a bad listing = low installs even with a great app.
- Search ranking on Play Store (ASO) depends on title/description keywords.
- Google reviews listing for misleading text/images (metadata policy).

## 🔴 यह क्यों बना? (Hindi)
- Users कुछ ही सेकंड में तय करते हैं; खराब listing = कम installs, चाहे app कितनी भी अच्छी हो।
- Play Store Search ranking (ASO) title/description के keywords पर निर्भर है।
- Google listing में भ्रामक text/images की जाँच करता है (metadata policy)।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Play Console → Grow users → Store presence → Main store listing
         (menu naam badal sakta hai)
Step 2 → App name (30), Short description (80), Full description (4000)
Step 3 → App icon: 512x512 PNG (32-bit), max 1 MB
Step 4 → Feature graphic: 1024x500 PNG/JPEG
Step 5 → Phone screenshots: kam se kam 2 (max 8), 16:9 ya 9:16, JPEG/24-bit PNG
Step 6 → Optional: 7-inch/10-inch tablet screenshots, promo video (YouTube URL)
Step 7 → Category + Tags + Contact email/website/phone
Step 8 → Custom listings / translations (Hindi, Tamil ...) add karo
Step 9 → Save → release ke saath review me jata hai
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Play Console → Grow users → Store presence → Main store listing
         (menu का नाम बदल सकता है)
Step 2 → App name (30), Short description (80), Full description (4000)
Step 3 → App icon: 512x512 PNG (32-bit), अधिकतम 1 MB
Step 4 → Feature graphic: 1024x500 PNG/JPEG
Step 5 → Phone screenshots: कम से कम 2 (अधिकतम 8), 16:9 या 9:16, JPEG/24-bit PNG
Step 6 → Optional: tablet screenshots, promo video (YouTube URL)
Step 7 → Category + Tags + Contact email/website/phone
Step 8 → Custom listings / translations (Hindi, Tamil ...) जोड़ो
Step 9 → Save → release के साथ review में जाता है
```

**Console screens (described in words):**
- **Main store listing page:** Left me form fields — "App name" (counter 0/30), "Short description" (0/80), "Full description" (0/4000). Right me phone ka live preview.
- **Graphics section:** Do upload boxes: "App icon" (square, dotted border) aur "Feature graphic" (wide). Neeche "Phone screenshots" grid jahan drag-drop se images aati hain aur remove "x" dikhta hai.
- **Translations tab:** Language selector "Manage translations" jisme Hindi add karne par alag text fields khulte hain.

---

## 🟡 Real World Example
**Swiggy** ka listing: short description me "Food delivery & Instamart" jaisa value-proposition; screenshots me pehle 2 me best offers/tracking UI. Har screenshot par ek chhota caption ("Order in 30 mins"). **Paytm** screenshots me UPI, recharge, wallet features ko sequence me dikhata hai. Pehle 2-3 screenshots install decision ka bada hissa hote hain.

## 🟡 Real Example Hindi mein
**Swiggy** की listing: short description में "Food delivery & Instamart" जैसा value-proposition; पहले 2 screenshots में best offers/tracking UI। हर screenshot पर छोटा caption ("30 मिनट में order")। **Paytm** अपने screenshots में UPI, recharge, wallet features क्रम से दिखाता है। पहले 2-3 screenshots का install decision में बड़ा हाथ होता है।

---

## 💻 Code Example — Basic
Listing text ke limits check karne ka Node script (runs with plain node).

```js
// listingCheck.js — run: node listingCheck.js
// Play Console ke common limits (Console me dikhe limits final)
const LIMITS = { title: 30, short: 80, full: 4000 };

// listing draft
const listing = {
  title: 'FoodieIndia',
  short: 'Order food online from 1000+ restaurants. Fast delivery.',
  full: 'FoodieIndia lets you order from nearby restaurants.\n- Live tracking\n- UPI payments',
};

// har field ke liye check
const report = Object.entries(LIMITS).map(([key, max]) => {
  // field ki length (undefined ho to 0)
  const len = (listing[key] || '').length;
  // result object
  return { key, len, max, ok: len > 0 && len <= max };
});

// table print
console.table(report);
// koi fail ho to exit code 1 (CI me useful)
if (report.some((r) => !r.ok)) process.exit(1);
```

## 💻 Code Example — Advanced
Screenshots ke liye real app screens ko store-ready size me render karne ka tareeka (Expo `react-native-view-shot` se) — native module, isliye *not run* here.

```jsx
// ScreenshotHelper.jsx — dev-only helper (Expo: npx expo install react-native-view-shot)
import React, { useRef } from 'react';                    // React + ref
import { View, Button, Alert } from 'react-native';       // RN components
import ViewShot from 'react-native-view-shot';             // view ko image me badalta hai

// Screen jiska screenshot chahiye wo children me aayegi
export default function ScreenshotHelper({ children }) {
  // ViewShot ref
  const ref = useRef(null);
  // capture handler
  const capture = async () => {
    try {
      // PNG me capture, tmpfile path milega
      const uri = await ref.current.capture();
      // dev ko path dikhao (yahan se device se file nikalo)
      Alert.alert('Saved', uri);
    } catch (e) {
      // error handling
      Alert.alert('Capture failed', String(e));
    }
  };
  // UI: content + capture button
  return (
    <View style={{ flex: 1 }}>
      <ViewShot ref={ref} options={{ format: 'png', quality: 1 }} style={{ flex: 1 }}>
        {children}
      </ViewShot>
      {__DEV__ && <Button title="Capture" onPress={capture} />}
    </View>
  );
}
```

Simpler tareeka: emulator/device se `adb exec-out screencap -p > shot1.png` ya Android Studio Emulator ka screenshot button.

---

## 📱 Android vs iOS Difference
| Feature | Android (Play) | iOS (App Store) |
|---------|----------------|-----------------|
| Title limit | 30 chars | 30 chars |
| Short text | 80 chars short description | 30 chars subtitle |
| Full text | 4000 chars | 4000 chars description |
| Keywords | Description se index hota hai | Alag 100-char keywords field |
| Screenshots | min 2 phone | min 1 per required device size |
| Feature graphic | 1024x500 required | Not applicable |
| Promo video | YouTube URL | App Preview video upload |

---

## 🟠 Expo vs CLI Difference
Expo way:
```json
{ "expo": { "name": "FoodieIndia", "icon": "./assets/icon.png" } }
```
(Listing text Console me hi likhte ho. `eas metadata` ka support mainly iOS ke liye hai; Android listing manual ya Fastlane supply se.)

CLI way:
```bash
# Fastlane supply se listing text/screenshots push (optional, advanced)
# fastlane/metadata/android/en-US/title.txt, short_description.txt, full_description.txt
fastlane supply --track internal --skip_upload_apk --skip_upload_aab
```

---

## ⚠️ Common Mistakes to Avoid
❌ **Mistake 1:** Title me "Best", "#1", "Free", emojis, ya price likhna.
✅ **Correct:** Clean brand name (30 chars). Keywords description me.

❌ **Mistake 2:** Screenshots me dusri brand/phone mockup ya misleading features.
✅ **Correct:** Asli app screens; sirf wo features jo app me hain.

❌ **Mistake 3:** Icon me alpha/transparency ya sizes galat.
✅ **Correct:** 512x512, 32-bit PNG, 1 MB tak.

❌ **Mistake 4:** Sirf English listing.
✅ **Correct:** India ke liye Hindi + regional translations add karo.

---

## 🧠 Tricky Interview Question
**Q: App ka rank gir gaya, kya karoge — sirf screenshot badal dena kaafi hai?**

**Answer:** Nahi. Rank ke factors: installs/retention, crash rate (Android vitals), ratings, listing relevance. Screenshots **conversion** badhate hain. Plan: (1) Android vitals/crash fix, (2) title/short description me relevant keywords natural tarah se, (3) A/B testing — Console ke "Store listing experiments" se icon/screenshots/description test, (4) ratings prompt (in-app review API). Sirf creative badalna incomplete hai.

---

## ⚫ Interview Questions + Answers

**Q1: Short description kitni lambi hoti hai?**
A1: 80 characters; search results aur listing ke upar dikhti hai.

**Q2: Feature graphic kya hai?**
A2: 1024x500 banner jo featured jagahon aur video preview ke upar dikhta hai.

**Q3: Kitne screenshots chahiye?**
A3: Phone ke liye min 2, max 8. Tablet aur Wear/TV ke alag requirements ho sakte hain.

**Q4: Store listing experiments kya hain?**
A4: A/B test: icon, screenshots, descriptions ke variants kuch % users ko dikhao aur install conversion compare karo.

**Q5: Listing translate karna kyun zaroori hai?**
A5: India jaisi multilingual market me local language listing se conversion badhta hai.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Pehli release se pehle, aur har major feature update ke baad refresh.

❌ Avoid when:
- Keyword stuffing, fake reviews/awards, ya competitor ke naam use karna.

---

## 📊 Visual Diagram
```
 ┌───────────────────────────────┐
 │  [icon 512]  FoodieIndia      │  title (30)
 │  Short description (80)       │
 │  ★ 4.4   10M+ downloads       │
 ├───────────────────────────────┤
 │ [ss1] [ss2] [ss3] [ss4] ...   │  screenshots 2-8
 ├───────────────────────────────┤
 │ Full description (4000)       │
 │ Data safety   Privacy policy  │
 └───────────────────────────────┘
 Feature graphic 1024x500 (banner / video cover)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ASO | App Store Optimization | Store में ranking सुधारना |
| Feature graphic | 1024x500 banner | Banner image |
| Short description | 80-char tagline | छोटा विवरण |
| Listing experiment | A/B test | A/B परीक्षण |
| Conversion | Visitors who install | Install करने वाले visitors |

---

## ⚡ 3-Line Summary
**English:**
1. Fill title (30), short (80), full (4000), icon 512, feature graphic, 2+ screenshots.
2. Keep it honest, localized, and keyword-aware without stuffing.
3. Use listing experiments to improve install conversion.

**Hindi:**
1. Title (30), short (80), full (4000), icon 512, feature graphic, 2+ screenshots भरो।
2. सच्चा, स्थानीय भाषा वाला और बिना keyword stuffing के रखो।
3. Install conversion बढ़ाने के लिए listing experiments चलाओ।

---

## ➡️ Next Topic
**216. Upload AAB to Play Console** — listing तैयार, अब असली build upload करते हैं।
