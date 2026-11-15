# 248. App Privacy Setup
# हिंदी में: App Privacy Setup (Privacy Labels + Privacy Manifest)
# Platform: Android ❌ | iOS ✅ (Android का equivalent: Play Console → Data safety form)

> Targets: **Expo SDK 52 (check current docs — APIs change between SDKs)**. Apple की privacy requirements (privacy manifest, required-reason APIs) 2024 से लागू हुईं और बदलती रहती हैं — current Apple docs देखो।

---

## 🔵 Simple Definition (English)
App Privacy tells Apple and users what data your app (and its SDKs) collects and why. It has three parts: the **privacy policy URL**, the **privacy "nutrition label"** answers in App Store Connect, and a **privacy manifest** (`PrivacyInfo.xcprivacy`) inside the app.

## 🔵 सरल परिभाषा (Hindi)
App Privacy Apple और users को बताता है कि आपका app (और उसके SDKs) कौन सा data collect करते हैं और क्यों। इसके तीन हिस्से हैं: **privacy policy URL**, ASC में **privacy "nutrition label"** के जवाब, और app के अंदर **privacy manifest** (`PrivacyInfo.xcprivacy`)।

---

## 🔴 Problem it Solves
- Users को install से पहले पता चले कि app उनका location/contacts/purchase data लेता है।
- Third-party SDKs छुपकर fingerprinting न करें।

## 🔴 यह क्यों बना? (Hindi)
Apple privacy पर सख़्त है। Users को "food label" जैसा साफ़ summary मिलता है, और developers को हर data type का purpose घोषित करना पड़ता है। झूठी जानकारी = rejection/removal।

---

## 🟢 How it Works — Step by Step
1. Public **Privacy Policy URL** तैयार करो।
2. ASC → App → **General → App Privacy → Get Started**।
3. सवाल: "Do you or your third-party partners collect data from this app?" Yes/No।
4. Yes हो तो data types चुनो: Contact Info, Location, Identifiers (User ID/Device ID), Usage Data, Purchases, Diagnostics, आदि।
5. हर type के लिए: **purposes** (App Functionality, Analytics, Advertising...), **linked to user?**, **used for tracking?**।
6. Tracking करते हो (ads/cross-app) → app में `NSUserTrackingUsageDescription` और ATT prompt (`expo-tracking-transparency`)।
7. Privacy manifest: Expo SDK 51+ में Expo modules के manifests आते हैं; अपने usage के लिए `ios.privacyManifests` config।
8. **Publish** दबाओ।

```
Step 1 → Privacy Policy URL
Step 2 → ASC → App Privacy → Get Started
Step 3 → Data types चुनो
Step 4 → Purpose + Linked + Tracking
Step 5 → App में ATT / manifest
Step 6 → Publish
```

## 🟢 कैसे काम करता है? (Hindi)
1. Privacy policy की public URL बनाओ।
2. ASC में हर data type चुनो और purpose बताओ।
3. Tracking हो तो ATT permission माँगो।
4. Privacy manifest app में जोड़ो और Publish करो।

**Console screen (description):** App Privacy page पर बीच में बड़ा "Get Started" बटन। फिर सवालों की सूची के साथ checkboxes (जैसे "Location → Precise Location"). हर चुने type पर तीन-step wizard: (1) Used for? (checkbox list), (2) "Is this data linked to the user's identity?" Yes/No, (3) "Is it used for tracking?" Yes/No। अंत में preview card जैसा "Data Linked to You" box और "Publish" बटन।

---

## 🟡 Real World Example
**Zomato/Swiggy** location (delivery address), phone number, purchase history, device ID (analytics) घोषित करते हैं — "Linked to You". **Paytm** financial info और contacts (अगर माँगता है) बताता है। Ads वाले apps ATT prompt दिखाते हैं।

## 🟡 Real Example Hindi mein
Zomato/Swiggy location, phone number और order history declare करते हैं। Paytm financial info declare करता है। Ads दिखाने वाले apps ATT permission prompt दिखाते हैं।

---

## 💻 Code Example — Basic
```json
// app.json — privacy-related iOS config (Expo SDK 52; JSON में comments हटाओ)
{
  "expo": {
    "ios": {
      "infoPlist": {
        "NSLocationWhenInUseUsageDescription": "Show restaurants near you",
        "NSUserTrackingUsageDescription": "Used to show relevant offers"
      },
      "privacyManifests": {
        "NSPrivacyAccessedAPITypes": [
          {
            "NSPrivacyAccessedAPIType": "NSPrivacyAccessedAPICategoryUserDefaults",
            "NSPrivacyAccessedAPITypeReasons": ["CA92.1"]
          }
        ]
      }
    }
  }
}
```
`ios.privacyManifests` Expo config में SDK 51+ में आया; reason code (`CA92.1`) Apple की required-reason list से आता है — अपना use case देखकर सही code चुनो।

## 💻 Code Example — Advanced
```jsx
// TrackingConsent.jsx — ATT prompt (expo-tracking-transparency)
import React, { useEffect, useState } from 'react';              // hooks
import { Platform, Text, View } from 'react-native';             // UI
import {
  requestTrackingPermissionsAsync,                               // permission माँगो
  getTrackingPermissionsAsync,                                   // current status
} from 'expo-tracking-transparency';

export default function TrackingConsent() {
  const [status, setStatus] = useState('unknown');               // status state

  useEffect(() => {
    if (Platform.OS !== 'ios') return;                           // सिर्फ iOS पर ATT
    (async () => {
      try {
        const current = await getTrackingPermissionsAsync();     // पहले जाँचो
        if (current.status === 'undetermined') {                 // पूछा नहीं गया
          const res = await requestTrackingPermissionsAsync();   // system dialog
          setStatus(res.status);                                 // granted/denied
        } else {
          setStatus(current.status);                             // पुराना जवाब
        }
      } catch (e) {
        setStatus('error');                                      // fail हुआ तो error
      }
    })();
  }, []);

  return (
    <View>
      {/* Tracking granted होने पर ही ad SDK init करो */}
      <Text>Tracking: {status}</Text>
    </View>
  );
}
```
Not run: native API; सिर्फ syntax check। ATT dialog सिर्फ real iOS 14.5+ device पर दिखता है।

---

## 📱 Android vs iOS Difference
| Feature | Android | iOS |
|---------|---------|-----|
| Store form | Data safety form | App Privacy labels |
| Tracking consent | Advertising ID setting; Android 13+ AD_ID permission | ATT prompt अनिवार्य |
| In-app manifest | AndroidManifest permissions | `PrivacyInfo.xcprivacy` |
| SDK data | Developer जिम्मेदार | SDK के privacy manifests + signatures |
| Policy URL | ज़रूरी | ज़रूरी |

---

## 🟠 Expo vs CLI Difference
Expo way:
```json
{ "expo": { "ios": { "privacyManifests": { "NSPrivacyAccessedAPITypes": [] } } } }
```
CLI way:
```xml
<!-- Xcode: File → New → App Privacy File → PrivacyInfo.xcprivacy
     उसमें NSPrivacyTracking, NSPrivacyCollectedDataTypes, NSPrivacyAccessedAPITypes भरो -->
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: "No data collected" चुनना जबकि analytics SDK (Firebase, Sentry) चल रहा है।
✅ Correct: SDK का data भी गिनो।

❌ Mistake 2: ATT usage text के बिना tracking।
✅ Correct: `NSUserTrackingUsageDescription` + prompt।

❌ Mistake 3: Privacy policy URL टूटी हुई।
✅ Correct: Public, working HTTPS link।

❌ Mistake 4: Account deletion option न देना (जब account बनाने की सुविधा हो)।
✅ Correct: In-app account deletion दो (Guideline 5.1.1(v))।

---

## 🧠 Tricky Interview Question
"आप Firebase Analytics इस्तेमाल करते हैं, user login नहीं है। क्या 'Data Not Collected' चुन सकते हैं?"

Answer: नहीं। Firebase device identifiers और usage data collect करता है, जो purpose "Analytics" में आता है। सही उत्तर: Usage Data + Identifiers (Device ID) चुनो; "linked to user" आपकी setup पर निर्भर (user ID न हो तो often "not linked"), "tracking" तब Yes जब data ads/data brokers के लिए cross-app इस्तेमाल हो।

---

## ⚫ Interview Questions + Answers
Q1: Privacy label क्या है?
A1: App Store पेज पर दिखने वाला data-collection summary।

Q2: ATT क्या है?
A2: App Tracking Transparency; cross-app tracking से पहले user की अनुमति का system prompt।

Q3: Privacy manifest क्या है?
A3: `PrivacyInfo.xcprivacy` file जिसमें collected data और required-reason API usage घोषित है।

Q4: Label बदलना हो तो?
A4: ASC में कभी भी edit/publish कर सकते हैं — नई version submit किए बिना।

Q5: Third-party SDK का manifest?
A5: Apple की list वाले SDKs को अपना manifest और signature देना होता है।

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- हर app submission में (अनिवार्य)।

❌ Avoid when:
- (कभी skip नहीं) — पर "tracking" का दावा तब मत करो जब असल में नहीं करते।

---

## 📊 Visual Diagram
```
 Privacy Policy URL ──┐
 ASC Privacy Labels ──┼──► Shown on App Store page
 PrivacyInfo.xcprivacy┘     (inside app binary, checked at upload)
 ATT prompt  ──► only if tracking
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Privacy label | Data summary on store | store पर data का सारांश |
| ATT | Tracking permission prompt | tracking की अनुमति |
| Privacy manifest | In-app privacy file | app के अंदर privacy file |
| Required-reason API | APIs needing declared reason | कारण बताकर इस्तेमाल होने वाली API |
| Linked to user | Data tied to identity | user से जुड़ा data |

---

## ⚡ 3-Line Summary
English: App Privacy has a policy URL, store labels and an in-app privacy manifest.
Declare all data including SDK data.
Add ATT only if you track.

Hindi: App Privacy में policy URL, store labels और app के अंदर privacy manifest होते हैं।
SDK का data भी declare करो।
ATT तभी जोड़ो जब tracking करते हो।

---

## ➡️ Next Topic
**249. Store Listing (iOS)** — description, keywords, support URL आदि।
