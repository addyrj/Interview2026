# 249. Store Listing (iOS)
# हिंदी में: iOS Store Listing — App का Product Page
# Platform: Android ❌ | iOS ✅ (Android का equivalent: Play Console → Main store listing)

> Targets: **Expo SDK 52 (check current docs — APIs change between SDKs)**. Character limits Apple बदल सकता है — ASC के counters देखो।

---

## 🔵 Simple Definition (English)
The store listing is your app's product page on the App Store: description, promotional text, keywords, support URL, "What's New" and more. It is written per version and per language.

## 🔵 सरल परिभाषा (Hindi)
Store listing App Store पर आपके app का product page है: description, promotional text, keywords, support URL, "What's New" आदि। यह हर version और हर language के लिए लिखी जाती है।

---

## 🔴 Problem it Solves
- Users को 5 सेकंड में समझना है कि app क्या करता है।
- ASO (App Store Optimization) — सही keywords से search में दिखना।

## 🔴 यह क्यों बना? (Hindi)
लाखों apps में आपका app तभी मिलेगा जब नाम, subtitle, keywords और description सही हों। Listing ही conversion (download) बढ़ाती है।

---

## 🟢 How it Works — Step by Step
1. ASC → App → **App Store → iOS App → [Version] (1.0 Prepare for Submission)**।
2. Language चुनो (Primary + extra, जैसे Hindi)।
3. भरो:
   - **Promotional Text** (≤170 chars, बिना review के कभी भी बदल सकते हो)
   - **Description** (≤4000)
   - **Keywords** (≤100 chars, comma-separated, बिना space)
   - **Support URL** (required), **Marketing URL** (optional)
   - **What's New in This Version** (update में)
   - **Copyright** (जैसे `2026 MyCompany Pvt Ltd`)
4. **Version Release** option: Manual / Automatic / Scheduled।
5. **App Review Information:** contact, demo account, notes (topic 251)।
6. Screenshots (topic 250)।
7. Save।

```
Step 1 → Version page खोलो
Step 2 → Language चुनो
Step 3 → Promo, Description, Keywords, URLs
Step 4 → What's New + Copyright
Step 5 → Save
```

## 🟢 कैसे काम करता है? (Hindi)
1. Version page खोलो और language चुनो।
2. Description, keywords, URLs भरो।
3. What's New और copyright लिखो।
4. Save करो।

**Console screen (description):** Version page ऊपर "iOS App Version 1.0" heading और language dropdown। सबसे ऊपर screenshots का drag-drop area (iPhone 6.9"/6.5" tabs)। नीचे लगातार text boxes: Promotional Text (counter 0/170), Description (0/4000), Keywords (0/100), Support URL, Marketing URL, Version, Copyright, फिर "Build" section जिसमें "+" बटन से processed build चुनते हैं।

---

## 🟡 Real World Example
**Swiggy** की description पहली 2-3 lines में "Food delivery, Instamart groceries" बताती है (क्योंकि "more" से पहले सिर्फ यही दिखता है)। **Zomato** promo text में offers बदलता रहता है — बिना नई version review के। **Paytm** keywords: "upi,recharge,bill pay,wallet"।

## 🟡 Real Example Hindi mein
Swiggy की description की पहली 2-3 lines में मुख्य बात होती है क्योंकि सिर्फ वही दिखती है। Zomato promo text बिना नई version के बदलता रहता है। Paytm keywords में upi, recharge जैसे शब्द रखता है।

---

## 💻 Code Example — Basic
```js
// check-listing.js — listing की limits जाँचने वाला Node script
const listing = {                                   // आपका draft
  promo: 'Free delivery on first 3 orders!',
  description: 'Order food from 1000s of restaurants. Fast delivery. Live tracking.',
  keywords: 'food,delivery,biryani,pizza,restaurant,order',
};
const max = { promo: 170, description: 4000, keywords: 100 }; // Apple limits
let ok = true;                                      // result flag
for (const k of Object.keys(max)) {                 // हर field पर loop
  const n = [...listing[k]].length;                 // unicode-safe length (Hindi भी)
  console.log(`${k}: ${n}/${max[k]}`);              // count दिखाओ
  if (n > max[k]) ok = false;                       // limit पार?
}
// keywords में space नहीं होना चाहिए (comma के बाद)
if (/,\s/.test(listing.keywords)) { console.log('Remove spaces after commas'); ok = false; }
process.exit(ok ? 0 : 1);                           // exit code
```
## 💻 Code Example — Advanced
```bash
# fastlane deliver से metadata files (version-control में) ASC पर push
# folder: fastlane/metadata/en-US/{description.txt, keywords.txt, promotional_text.txt, release_notes.txt}
fastlane deliver --skip_binary_upload --skip_screenshots --force
```
```json
// Expo का eas metadata (preview feature; schema docs में) — store.config.json
{
  "configVersion": 0,
  "apple": {
    "info": {
      "en-US": {
        "title": "FoodApp",
        "subtitle": "Order food fast",
        "description": "Order from 1000s of restaurants.",
        "keywords": ["food", "delivery", "biryani"],
        "marketingUrl": "https://example.com",
        "supportUrl": "https://example.com/support",
        "privacyPolicyUrl": "https://example.com/privacy"
      }
    }
  }
}
```
```bash
# store.config.json को ASC पर push (EAS Metadata; keys docs से verify करो)
eas metadata:push
```
`eas metadata` का schema बदल सकता है; ऊपर के keys का exact नाम current EAS Metadata docs से मिलाओ — ASC UI और `eas metadata:push` not run।

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Short text | Short description 80 | Subtitle 30 + Promo 170 |
| Long text | Full description 4000 | Description 4000 |
| Keywords | कोई field नहीं (description से) | 100-char keywords field |
| Update notes | What's new 500 | What's New 4000 |
| Graphics | Feature graphic 1024×500 | कोई feature graphic नहीं |
| Edit without review | कई fields | सिर्फ Promotional Text |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
# EAS Metadata से listing code में रखो
eas metadata:push
```
CLI way:
```bash
# fastlane deliver — दोनों (Expo/bare) में काम करता है
fastlane deliver
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Keywords में app का नाम दोहराना।
✅ Correct: नाम/subtitle पहले से indexed हैं; नए शब्द डालो।

❌ Mistake 2: Description में दूसरे platform (Android/Google Play) का ज़िक्र।
✅ Correct: सिर्फ iOS/Apple की भाषा।

❌ Mistake 3: Support URL न देना या dead link।
✅ Correct: Working support page।

❌ Mistake 4: Placeholder/Lorem ipsum text।
✅ Correct: Final copy → वरना rejection (2.3)।

---

## 🧠 Tricky Interview Question
"Release के बाद typo मिली। क्या नई build/review के बिना description ठीक कर सकते हैं?"

Answer: नहीं — Description, keywords, screenshots बदलने के लिए नई version submit + review चाहिए। सिर्फ **Promotional Text** (170 chars) कभी भी बिना review बदल सकते हो। इसलिए important announcements promo text में रखो।

---

## ⚫ Interview Questions + Answers
Q1: Keywords limit?
A1: 100 characters, comma-separated, space की ज़रूरत नहीं।

Q2: Promo text की खासियत?
A2: Review के बिना edit हो सकता है।

Q3: Support URL ज़रूरी है?
A3: हाँ, required।

Q4: ASO क्या है?
A4: App Store Optimization — name/subtitle/keywords/screenshots से discoverability बढ़ाना।

Q5: Localization कैसे?
A5: ASC में language जोड़ो और हर के लिए text भरो।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- हर submission और हर update।

❌ Avoid when:
- Keyword stuffing/misleading claims (rejection)।

---

## 📊 Visual Diagram
```
 Name (30) ── Subtitle (30) ── Keywords (100, hidden)
        │
 Screenshots ── Promo (170) ── Description (4000) ── What's New
        │
 Support URL ── Privacy URL ── Copyright
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ASO | Store optimization | store में बेहतर दिखना |
| Promotional text | Editable anytime blurb | कभी भी बदलने वाला text |
| Keywords | Hidden search terms | छुपे search शब्द |
| What's New | Release notes | नया क्या है |
| Localization | Per-language listing | भाषा के अनुसार listing |

---

## ⚡ 3-Line Summary
English: The store listing holds description, keywords, URLs and release notes.
Only promotional text can change without review.
Keep it truthful and complete.

Hindi: Store listing में description, keywords, URLs और release notes होते हैं।
सिर्फ promotional text बिना review बदलता है।
इसे सच्चा और पूरा रखो।

---

## ➡️ Next Topic
**250. Screenshots + Preview Video** — listing का सबसे असरदार हिस्सा।
