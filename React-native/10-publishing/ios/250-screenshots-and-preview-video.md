# 250. Screenshots + Preview Video
# हिंदी में: Screenshots और App Preview Video
# Platform: Android ❌ | iOS ✅ (Android का equivalent: Play Console graphics + promo video)

> Targets: **Expo SDK 52 (check current docs — APIs change between SDKs)**. Required screenshot sizes Apple नई iPhones के साथ बदलता है — ASC "Screenshot Specifications" page देखो।

---

## 🔵 Simple Definition (English)
Screenshots and app preview videos are the images and short videos shown on your App Store page. Apple needs screenshots for specific device sizes, and the preview video (15-30 seconds) is optional.

## 🔵 सरल परिभाषा (Hindi)
Screenshots और app preview videos वे images और छोटे videos हैं जो App Store page पर दिखते हैं। Apple को खास device sizes के screenshots चाहिए; preview video (15-30 सेकंड) optional है।

---

## 🔴 Problem it Solves
- Users text से ज़्यादा screenshots देखकर download तय करते हैं।
- सही size न हो तो ASC upload reject करता है।

## 🔴 यह क्यों बना? (Hindi)
App Store visual है। पहले 2-3 screenshots ही conversion तय करते हैं। Apple fixed sizes माँगता है ताकि हर device पर साफ़ दिखे।

---

## 🟢 How it Works — Step by Step
1. Required size पता करो (ASC → Version page → Screenshots; आमतौर पर सबसे बड़े iPhone (6.9" या 6.7") का set चाहिए, बाकी sizes ASC auto scale कर सकता है; iPad support हो तो iPad set भी)।
2. Simulator में screenshots लो: `xcrun simctl io booted screenshot shot.png` (Mac) या Cmd+S।
3. Design करो (Figma/Previewed/AppMockUp) — heading text + device frame।
4. Format: PNG या JPEG, no alpha, exact pixel size; 1 से 10 screenshots।
5. ASC में device tab चुनो → drag & drop → order set करो।
6. **App Preview** (optional): 15-30 सेकंड, max 3, `.mov/.m4v/.mp4`, device की actual screen recording।
7. Save।

```
Step 1 → Required sizes check
Step 2 → Screenshots capture (simulator/device)
Step 3 → Design (text + frame)
Step 4 → Export exact size, no alpha
Step 5 → ASC में upload + order
Step 6 → (Optional) Preview video
```

## 🟢 कैसे काम करता है? (Hindi)
1. ASC में बताई size देखो।
2. Simulator में screenshots लो।
3. Heading text के साथ design करो।
4. सही size में export करके upload करो।
5. Preview video optional है।

**Console screen (description):** Version page के ऊपर "Previews and Screenshots" box। उसके ऊपर device tabs (iPhone 6.9" Display, iPhone 6.5", iPad 13") — हर tab पर dashed border वाला drop area "Drag up to 10 screenshots here"। Upload के बाद thumbnails दिखते हैं जिन्हें drag करके क्रम बदल सकते हैं; हर thumbnail पर hover करने से delete (X) icon दिखता है। App Preview के लिए अलग छोटा drop area होता है।

---

## 🟡 Real World Example
**Zomato** के screenshots में बड़ा hindi/english heading ("Order in minutes") और phone frame होता है। **Swiggy** पहले screenshot में offers दिखाता है। **Paytm** UPI payment flow का short preview video रखता है।

## 🟡 Real Example Hindi mein
Zomato के screenshots में बड़ा heading और phone frame होता है। Swiggy पहले screenshot में offers दिखाता है। Paytm UPI payment का छोटा preview video रखता है।

---

## 💻 Code Example — Basic
```bash
# Mac पर iOS Simulator से screenshot (Xcode installed)
xcrun simctl boot "iPhone 15 Pro Max"            # device चालू करो (नाम आपके simulators से)
open -a Simulator                                # Simulator app खोलो
npx expo run:ios --device "iPhone 15 Pro Max"    # app चलाओ (dev build)
xcrun simctl io booted screenshot home.png       # screenshot लो
```
## 💻 Code Example — Advanced
```js
// check-shots.js — screenshots का pixel size जाँचो (Node + sharp; npm i sharp)
const sharp = require('sharp');                     // image library
const fs = require('fs');                           // folder पढ़ने के लिए

// Allowed sizes (ASC spec से मिलाओ; ये उदाहरण हैं — current spec देखो)
const allowed = ['1320x2868', '1290x2796', '1242x2688'];

(async () => {
  let bad = 0;                                       // गलत files की गिनती
  for (const f of fs.readdirSync('./shots')) {       // folder की हर file
    if (!/\.(png|jpe?g)$/i.test(f)) continue;        // सिर्फ images
    const m = await sharp('./shots/' + f).metadata();// metadata पढ़ो
    const size = `${m.width}x${m.height}`;           // WxH
    const alpha = m.hasAlpha;                        // alpha channel?
    const ok = allowed.includes(size) && !alpha;     // size सही और alpha नहीं
    console.log(f, size, alpha ? 'HAS ALPHA' : 'no alpha', ok ? 'OK' : 'FIX');
    if (!ok) bad++;                                  // गलत गिनो
  }
  process.exit(bad ? 1 : 0);                         // CI के लिए exit code
})();
```
नोट: `sharp` का `metadata()` `width/height/hasAlpha` देता है। Allowed sizes सिर्फ उदाहरण हैं — ASC की current table से बदलो। Simulator/ASC not run।

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Count | 2-8 phone screenshots | 1-10 per size |
| Format | PNG/JPEG, 24-bit | PNG/JPEG, no alpha |
| Extra graphic | Feature graphic 1024×500 | नहीं |
| Video | YouTube URL | Upload करो (15-30s, max 3) |
| Sizes | Flexible aspect ratio | Fixed pixel sizes per device |
| Device frames | अनुमत | अनुमत (marketing) |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
# Dev build simulator में
npx expo run:ios
```
CLI way:
```bash
# Bare RN
npx react-native run-ios --simulator "iPhone 15 Pro Max"
```
दोनों के screenshots का upload ASC में एक जैसा है।

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Alpha/transparency वाली PNG।
✅ Correct: Flatten करके export करो।

❌ Mistake 2: Screenshots में दूसरे platform का (Android status bar) UI।
✅ Correct: iOS device/simulator से लो।

❌ Mistake 3: Dummy/Lorem data या real user का personal data।
✅ Correct: साफ़ demo data।

❌ Mistake 4: Preview video में screen के बाहर का content।
✅ Correct: सिर्फ app की actual screen capture।

---

## 🧠 Tricky Interview Question
"6.9\" screenshots upload किये, पर 6.5\" वाले tab में 'Missing'। क्या दोबारा सब बनाएँ?"

Answer: अगर ASC बड़े size के set से छोटे sizes auto-scale कर देता है, तो अलग से जरूरी नहीं (current spec देखो)। अगर tab required है तो उसी set से सही pixel size export करो। नियम Apple बदलता रहता है, इसलिए ASC के "required" marker पर भरोसा करो।

---

## ⚫ Interview Questions + Answers
Q1: कितने screenshots?
A1: 1 से 10 प्रति device size।

Q2: Preview video की length?
A2: 15-30 सेकंड, अधिकतम 3।

Q3: Alpha क्यों नहीं?
A3: ASC transparent images reject करता है।

Q4: पहले screenshots क्यों ज़रूरी?
A4: Search results में पहले 2-3 ही दिखते हैं।

Q5: Simulator से screenshot कैसे?
A5: `xcrun simctl io booted screenshot file.png` या Cmd+S।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- हर release पर UI बदला हो तो update करो।

❌ Avoid when:
- Fake features दिखाना (misleading → rejection)।

---

## 📊 Visual Diagram
```
 Simulator/Device ──► raw PNG ──► Figma (text+frame) ──► export exact WxH, no alpha
                                                              │
                                              ASC drag & drop (order matters)
                                                              ▼
                                                  App Store product page
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Screenshot | Static store image | store की तस्वीर |
| App Preview | Short video | छोटा video |
| Alpha channel | Transparency data | पारदर्शिता |
| Display size | Device screen class | device की screen size |

---

## ⚡ 3-Line Summary
English: Provide screenshots in the required device sizes without alpha.
Use up to 10 screenshots and an optional 15-30s preview.
Put the best content first.

Hindi: ज़रूरी device sizes में बिना alpha के screenshots दो।
10 तक screenshots और optional 15-30 सेकंड का preview दो।
सबसे अच्छा content पहले रखो।

---

## ➡️ Next Topic
**251. Submit for App Review** — आख़िरी step: review में भेजना और rejection संभालना।
