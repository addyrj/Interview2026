# 247. Pricing + Availability
# हिंदी में: Pricing और Availability (कीमत और उपलब्ध देश)
# Platform: Android ❌ | iOS ✅ (Android का equivalent: Play Console → Pricing and distribution)

> Targets: **Expo SDK 52 (check current docs — APIs change between SDKs)**. Price tiers/territories और tax rules Apple बदलता रहता है।

---

## 🔵 Simple Definition (English)
Pricing and Availability decides whether your app is free or paid, what price it has in each country, and in which countries and release dates it can be downloaded.

## 🔵 सरल परिभाषा (Hindi)
Pricing और Availability तय करती है कि app free है या paid, हर देश में उसकी कीमत क्या होगी, और किन देशों में और कब से download हो सकेगा।

---

## 🔴 Problem it Solves
- अलग देशों में अलग currency और tax होता है।
- कुछ देशों में law/policy की वजह से app नहीं देना होता।
- Launch date control (pre-order) चाहिए।

## 🔴 यह क्यों बना? (Hindi)
Apple price को देश के हिसाब से अपने-आप convert करता है। Developer एक base price चुनता है और बाकी देशों के लिए Apple tax/currency संभालता है।

---

## 🟢 How it Works — Step by Step
1. ASC → App → **General → Pricing and Availability**।
2. **Price Schedule:** Free चुनो या Base Country (जैसे India) में price point चुनो। Apple बाकी देशों की कीमत खुद निकालता है।
3. अलग देश के लिए price override कर सकते हो।
4. **App Availability:** सभी countries या चुनिंदा (Remove/Add Countries)।
5. **Pre-Orders** (optional): Release से पहले orders लेना।
6. **Apple Silicon Mac / Vision availability** का checkbox (iOS app Mac पर भी)।
7. Paid app हो तो **Agreements, Tax, and Banking** पूरा (Paid Apps Agreement) — वरना Submit नहीं होगा।

```
Step 1 → Pricing and Availability खोलो
Step 2 → Free या Price point
Step 3 → Countries चुनो
Step 4 → (Optional) Pre-order
Step 5 → Paid हो तो Agreements/Tax/Bank
```

## 🟢 कैसे काम करता है? (Hindi)
1. Pricing section खोलो।
2. Free रखो या base price चुनो।
3. देश चुनो जहाँ app चाहिए।
4. Paid app हो तो tax और bank info ज़रूर भरो।

**Console screen (description):** पेज पर "Price Schedule" heading, "Add Price" बटन और dropdown "Base Country or Region" (India/US...). Price point dropdown में "Free" या ₹ amounts की सूची। नीचे "App Availability" box जिसमें "Edit" बटन; क्लिक पर 175+ देशों की checklist और "Select All". ऊपर पीला banner अगर "Paid Apps Agreement" बाकी है।

---

## 🟡 Real World Example
**Zomato/Swiggy/Paytm** apps free हैं — कमाई delivery fee/commission/payments से। **Games** (जैसे paid premium) price लगाते हैं। कुछ fintech apps सिर्फ India में available रखते हैं क्योंकि RBI compliance सिर्फ India के लिए है।

## 🟡 Real Example Hindi mein
Zomato, Swiggy, Paytm free apps हैं और कमाई दूसरे तरीकों से करते हैं। कई fintech apps सिर्फ India में उपलब्ध रखते हैं क्योंकि compliance सिर्फ India का है।

---

## 💻 Code Example — Basic
```jsx
// PriceLabel.jsx — localized price दिखाओ (Intl API; Hermes पर supported)
import React from 'react';                      // React
import { Text } from 'react-native';            // Text component

export default function PriceLabel({ amount = 0 }) {
  // India ₹ format में दिखाओ
  const label = new Intl.NumberFormat('en-IN', {
    style: 'currency', currency: 'INR',         // INR currency
    maximumFractionDigits: 0,                   // दशमलव नहीं
  }).format(amount);
  // 0 हो तो "Free" दिखाओ
  return <Text>{amount === 0 ? 'Free' : label}</Text>;
}
```
`Intl.NumberFormat` Hermes में Android/iOS दोनों पर काम करता है (RN 0.70+; अगर पुराने version में दिक्कत हो तो polyfill)।

## 💻 Code Example — Advanced
```jsx
// Region-restricted feature: सिर्फ India में Paytm-style UPI बटन
import React from 'react';                                 // React
import { View, Text, Platform } from 'react-native';       // UI
import * as Localization from 'expo-localization';         // device region info

export default function PayOptions() {
  // device का region (जैसे 'IN'); SDK 52 में getLocales() इस्तेमाल करो
  const region = Localization.getLocales()?.[0]?.regionCode;
  const isIndia = region === 'IN';                         // India?
  return (
    <View>
      {/* India में UPI */}
      {isIndia && <Text>Pay with UPI</Text>}
      {/* बाकी जगह card */}
      {!isIndia && <Text>Pay with Card</Text>}
      {/* iOS में digital goods के लिए IAP rule याद रखो */}
      {Platform.OS === 'ios' && <Text style={{ fontSize: 10 }}>Digital items use Apple IAP</Text>}
    </View>
  );
}
```
नोट: Pricing ASC में server-side है; app code सिर्फ region के हिसाब से UI बदलता है। `expo-localization` native module — device पर ही चलेगा (not run).

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Price setting | Pricing templates / per-country | Base country + auto conversion |
| Commission | 15% (छोटे/subscription) या 30% | 15% (Small Business Program) या 30% |
| Pre-order | Available | Available |
| Free→Paid change | Free app को paid नहीं कर सकते | Free↔Paid बदल सकते हैं |
| Tax forms | Payments profile | Agreements, Tax, and Banking |

---

## 🟠 Expo vs CLI Difference
Expo way:
```json
{ "expo": { "ios": { "bundleIdentifier": "com.mycompany.foodapp" } } }
```
(Pricing सिर्फ ASC पर; code में कुछ नहीं।)
CLI way:
```bash
# fastlane deliver से price tier भी set हो सकता है (metadata/price_tier.txt)
fastlane deliver
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Paid Apps Agreement पूरा न करना।
✅ Correct: Tax/bank भरो; वरना paid/IAP काम नहीं करेगा।

❌ Mistake 2: गलती से सारे देश चुनना जहाँ legal approval नहीं।
✅ Correct: Legal-compliant देश ही रखो।

❌ Mistake 3: Digital goods के लिए external payment link देना।
✅ Correct: Apple IAP नियम (3.1.1) देखो — regional exceptions बदलते रहते हैं।

❌ Mistake 4: Launch date भूलना।
✅ Correct: Release option (manual/auto/scheduled) सोचकर चुनो।

---

## 🧠 Tricky Interview Question
"App को पहले free launch किया, अब ₹499 करना है। पुराने users का क्या होगा?"

Answer: Price बदलने से पहले download किए users app रखते हैं और नए users को price लगता है। iOS पर free ↔ paid बदलना संभव है, पर पहले से free users से पैसे नहीं लिए जाते। इसलिए आमतौर पर free + In-App Purchase/subscription मॉडल अपनाते हैं।

---

## ⚫ Interview Questions + Answers
Q1: Price कैसे तय होती है?
A1: Base country में price point चुनो; Apple बाकी देशों में convert करता है।

Q2: Paid app के लिए क्या ज़रूरी?
A2: Paid Apps Agreement + tax + bank।

Q3: Apple commission?
A3: Standard 30%; Small Business Program में 15% (शर्तें docs में)।

Q4: Pre-order क्या है?
A4: Release से पहले users order कर लेते हैं और release पर auto download।

Q5: देश कैसे रोकें?
A5: App Availability में countries unselect करो।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Launch से पहले price/regions तय करने हैं।

❌ Avoid when:
- App में सिर्फ IAP है — app free रखो और IAP products अलग बनाओ।

---

## 📊 Visual Diagram
```
 Base price (India ₹) ──► Apple converts ──► US $, UK £, ...
 Availability: [✔ India] [✔ US] [✘ Country X]
 Paid? ──► Agreements + Tax + Bank ──► ✅ can submit
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Price point | Fixed Apple price level | Apple की price level |
| Base country | Reference country for price | मूल देश |
| Pre-order | Order before release | release से पहले order |
| Paid Apps Agreement | Contract for paid apps | paid apps का अनुबंध |
| Availability | Countries where app is live | उपलब्ध देश |

---

## ⚡ 3-Line Summary
English: Pricing sets free or paid with a base country price.
Availability selects countries.
Paid apps need agreements, tax and bank info first.

Hindi: Pricing तय करती है कि app free है या paid, base देश की कीमत से।
Availability में देश चुनते हैं।
Paid apps के लिए पहले agreement, tax और bank info चाहिए।

---

## ➡️ Next Topic
**248. App Privacy Setup** — Apple को बताना कि app कौन सा user data collect करता है।
