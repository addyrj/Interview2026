# 257. App Store Optimization (ASO)
# हिंदी में: App Store Optimization — App को search में ऊपर लाना
# Platform: Android ✅ | iOS ✅ | Both ✅

> Expo SDK 52+ examples (check current docs — APIs change between SDKs). Character limits below are what App Store Connect / Play Console documented at the time of writing; verify in the console.

---

## 🔵 Simple Definition (English)
ASO is SEO for app stores: improving your app's name, keywords, description, icon, screenshots and ratings so more people find it and install it. It is metadata work, not code, but developers often own it.

## 🔵 सरल परिभाषा (Hindi)
ASO app stores के लिए SEO है: app का नाम, keywords, description, icon, screenshots और ratings सुधारना ताकि ज़्यादा लोग app ढूँढें और install करें। यह मुख्यतः metadata का काम है, code का नहीं।

---

## 🔴 Problem it Solves
```
PROBLEM: Millions of apps; users search "food delivery" and only see top few.
SOLUTION: Optimise metadata + conversion (icon, screenshots) + ratings to rank higher.
```

## 🔴 यह क्यों बना? (Hindi)
Store में लाखों apps हैं और user सिर्फ top कुछ results देखता है। अच्छे keywords, screenshots और ratings से आपका app ऊपर दिखता है और ज़्यादा installs मिलते हैं।

---

## 🟢 How it Works — Step by Step
```
Step 1 → Keyword research (what Indians search: "recharge", "upi", "food order")
Step 2 → Write Title + Subtitle (iOS) with the main keywords
Step 3 → Fill iOS Keywords field (100 chars, comma separated, no spaces, no repeats of title words)
Step 4 → Write a persuasive description (Play indexes it; iOS description does not affect search ranking)
Step 5 → Design icon + first 3 screenshots (most users see only these)
Step 6 → Localise (Hindi, Tamil, etc.) for India
Step 7 → Ask for ratings at happy moments (SKStoreReviewController)
Step 8 → Track: impressions, product page views, conversion rate, A/B test (Product Page Optimization / Store Listing Experiments)
```

### Field comparison (verify limits in console)
| Field | iOS App Store | Google Play |
|-------|---------------|-------------|
| Title | 30 chars (App Name) | 30 chars (App name) |
| Subtitle / Short description | Subtitle 30 chars | Short description 80 chars |
| Keywords | 100 chars hidden Keywords field | No keyword field; description is indexed |
| Description | 4000 chars (not used for search ranking) | 4000 chars (indexed) |
| Promotional text | 170 chars, editable without review | N/A |
| Screenshots | Up to 10 per size | Up to 8 per type |
| A/B tests | Product Page Optimization | Store Listing Experiments |

### Console screens (in words)
- **App Store Connect → App → App Information**: fields Name, Subtitle, Category, Content Rights.
- **Version page → App Store localization list on left**: click "+" beside language (e.g. Hindi), then the page shows Promotional Text, Description, Keywords, Support URL, Marketing URL.
- **Analytics tab**: charts for Impressions, Product Page Views, Conversion Rate, Downloads.

## 🟢 कैसे काम करता है? (Hindi)
1. Keyword research करो — भारतीय users क्या search करते हैं।
2. Title और Subtitle में मुख्य keywords रखो।
3. iOS Keywords field (100 characters) बिना spaces और बिना repeat के भरो।
4. Description आकर्षक लिखो (Play में यह search में गिना जाता है)।
5. Icon और पहले 3 screenshots बेहतरीन बनाओ।
6. Hindi जैसी local भाषाओं में localise करो।
7. खुश users से ही rating माँगो।
8. Analytics देखकर A/B test चलाओ।

---

## 🟡 Real World Example
Zomato का title "Zomato: Food Delivery & Dining" जैसा pattern (brand + keyword) इस्तेमाल करता है; PhonePe/Paytm अपने screenshots में UPI/Recharge features दिखाते हैं। Hindi localisation से Tier-2/3 शहरों के users ज़्यादा convert होते हैं।

## 🟡 Real Example Hindi mein
Zomato जैसे apps brand के साथ मुख्य keyword title में डालते हैं। Paytm/PhonePe screenshots में UPI और recharge दिखाते हैं। Hindi में listing होने से छोटे शहरों के users ज़्यादा install करते हैं।

---

## 💻 Code Example — Basic (ask for rating with expo-store-review)
```jsx
// RateAppButton.jsx - triggers native rating prompt (iOS: SKStoreReviewController, Android: Play In-App Review)
import React from 'react';                                    // React
import { Pressable, Text, Linking, Platform } from 'react-native'; // UI + linking
import * as StoreReview from 'expo-store-review';            // npx expo install expo-store-review

export default function RateAppButton() {                    // simple button
  const onPress = async () => {                              // press handler
    try {                                                    // protect against errors
      if (await StoreReview.hasAction()) {                   // is native prompt available?
        await StoreReview.requestReview();                   // OS may or may not show it (rate limited)
      } else {                                               // fallback
        const url = Platform.OS === 'ios'
          ? 'itms-apps://apps.apple.com/app/id1234567890?action=write-review' // App Store review page
          : 'market://details?id=com.example.foodapp';       // Play Store page
        await Linking.openURL(url);                          // open store
      }
    } catch (e) {
      console.warn('Review failed', e);                      // do not crash
    }
  };
  return <Pressable onPress={onPress}><Text>Rate us</Text></Pressable>; // UI
}
```

## 💻 Code Example — Advanced (ask only after a happy moment, with cooldown)
```jsx
// reviewPrompt.js - ask for review after 3 successful orders, at most every 90 days
import AsyncStorage from '@react-native-async-storage/async-storage'; // persistent storage
import * as StoreReview from 'expo-store-review';                      // native review API

const DAY = 24 * 60 * 60 * 1000;                                       // ms in a day

// pure decision function (easy to unit test)
export const shouldAsk = ({ successCount, lastAskedAt, now }) =>
  successCount >= 3 && (!lastAskedAt || now - lastAskedAt > 90 * DAY);  // 3 orders + 90 day gap

export async function maybeAskForReview() {                            // call after order success
  try {
    const count = Number((await AsyncStorage.getItem('orders_ok')) || 0) + 1; // increment success count
    await AsyncStorage.setItem('orders_ok', String(count));            // save it
    const last = Number((await AsyncStorage.getItem('review_last')) || 0);     // last ask time
    if (shouldAsk({ successCount: count, lastAskedAt: last, now: Date.now() })) {
      if (await StoreReview.hasAction()) {                             // check availability
        await StoreReview.requestReview();                             // show prompt
        await AsyncStorage.setItem('review_last', String(Date.now())); // remember
      }
    }
  } catch (e) {
    console.warn(e);                                                   // ignore review errors
  }
}
```
Native review prompt itself cannot be run here; `shouldAsk` is pure logic.

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Keyword field | None, description indexed | Hidden 100-char field |
| Short text | Short description 80 chars | Subtitle 30 chars |
| Preview video | YouTube link | App preview upload (up to 3) |
| Review prompt API | Play In-App Review | SKStoreReviewController (max ~3 shows / year) |
| Experiments | Store Listing Experiments | Product Page Optimization |
| Reply to reviews | Play Console | App Store Connect |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
npx expo install expo-store-review   # one command, correct version for SDK
```
CLI way:
```bash
npm i expo-store-review react-native-in-app-review  # (bare apps often use react-native-in-app-review)
cd ios && pod install
```
Both ways: store listing text is edited in the consoles (or via `eas metadata` for iOS — check current docs, it is a config-file driven metadata sync).

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Repeating title words in the iOS Keywords field.
✅ Correct: Title words are already indexed; use the 100 chars for new terms.

❌ Mistake 2: Keyword stuffing / competitor names.
✅ Correct: Relevant terms only; competitor names get rejected (2.3.7).

❌ Mistake 3: Asking for rating on first launch.
✅ Correct: Ask after a success moment.

❌ Mistake 4: Ignoring screenshots.
✅ Correct: First 3 screenshots tell the story with captions.

---

## 🧠 Tricky Interview Question
You called `StoreReview.requestReview()` but no dialog appeared in production. Bug?

Answer: Not necessarily. iOS limits how often the prompt appears (a few times per 365 days) and the OS decides; it never tells you if the user rated. Never attach it to a button that promises a dialog; use `?action=write-review` link for an explicit "Rate us" button.

---

## ⚫ Interview Questions + Answers
Q1: Does iOS use the description for ranking?
A1: No; title, subtitle and keywords field matter. Play indexes the description.

Q2: What is conversion rate in ASO?
A2: Product page views that become downloads.

Q3: Why localise?
A3: Each locale has its own keyword indexing and trust; Hindi helps in India.

Q4: Which metadata can change without review on iOS?
A4: Promotional text (and some others); check console.

Q5: What are the top ranking factors?
A5: Keywords, download velocity, ratings, retention, and conversion.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Organic installs matter; every release, refresh keywords

❌ Avoid:
- Fake reviews, keyword stuffing — risk of removal

---

## 📊 Visual Diagram
```
 Search query --> Rank (title/keywords/ratings/velocity)
                      |
               Product page (icon, screenshots, rating)
                      |
                  Install --> Retention --> better rank
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ASO | App store SEO | Store में ranking सुधार |
| Keywords field | Hidden iOS search terms | छुपे search शब्द |
| Conversion rate | Views -> installs | Install प्रतिशत |
| Localisation | Local language listing | स्थानीय भाषा |
| A/B test | Compare two listings | दो listing की तुलना |

---

## ⚡ 3-Line Summary
English: ASO improves discoverability and installs through metadata and visuals.
iOS has a hidden 100-char keywords field; Play indexes the description.
Ask for ratings at happy moments and localise.

Hindi: ASO metadata और visuals से discoverability और installs बढ़ाता है।
iOS में 100-char का hidden keywords field है; Play description index करता है।
खुश moment पर rating माँगो और local भाषा में listing दो।

---

## ➡️ Next Topic
**258. OTA Updates — What + Why** — अब stores के बाहर से JS updates भेजने की दुनिया।
