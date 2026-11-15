# 254. App Review Guidelines
# हिंदी में: App Review Guidelines — Apple के नियम
# Platform: Android ❌ | iOS ✅

> Expo SDK 52+ examples (check current docs — APIs change between SDKs). The guidelines document is updated several times a year; treat this note as a map, not as legal text.

---

## 🔵 Simple Definition (English)
The App Review Guidelines are Apple's written rulebook for the App Store. It has five main sections: Safety, Performance, Business, Design, Legal. Reviewers use it to approve or reject apps. Reading it once before building saves a lot of rework.

## 🔵 सरल परिभाषा (Hindi)
App Review Guidelines Apple का लिखित rulebook है। इसमें पाँच मुख्य हिस्से हैं: Safety, Performance, Business, Design, Legal। Reviewer इन्हीं से approve या reject करता है। Build करने से पहले एक बार पढ़ लो तो बाद में rework बचता है।

---

## 🔴 Problem it Solves
```
Without written rules: every reviewer decision would feel random.
With guidelines: developers know exactly what is allowed
                 and can cite a number when they appeal.
```

## 🔴 यह क्यों बना? (Hindi)
नियम लिखित न हों तो हर reject मनमाना लगेगा। Guidelines से developer को साफ पता होता है कि क्या allowed है और appeal में number cite कर सकता है।

---

## 🟢 How it Works — Step by Step
```
Step 1 → Open developer.apple.com/app-store/review/guidelines
Step 2 → Read the intro (Before You Submit) checklist
Step 3 → Map your app features to sections 1-5
Step 4 → Note risky features (payments, UGC, kids, health, crypto, login)
Step 5 → Build compliance into the app (not as an afterthought)
Step 6 → Quote guideline numbers in review notes when helpful
```

### The five sections (map)
| Section | Covers | RN / Expo relevance |
|---------|--------|---------------------|
| 1. Safety | Objectionable content, user-generated content (report/block), kids, physical harm | Chat apps need report + block + moderation |
| 2. Performance | App completeness (2.1), beta labels, accurate metadata (2.3), hardware compat (2.4), software requirements (2.5) | Crashes, placeholder UI, public APIs only, OTA rule 2.5.2 |
| 3. Business | Payments (3.1.1 IAP, 3.1.3 exceptions), subscriptions, ads | Digital goods use IAP; physical goods can use Razorpay/UPI |
| 4. Design | Copycats (4.1), minimum functionality (4.2), spam, Sign in with Apple (4.8) | WebView-only wrappers get rejected |
| 5. Legal | Privacy (5.1), IP, gambling (5.3), VPN, developer code of conduct | Privacy policy, data collection consent, real-money gaming licenses |

### Before You Submit checklist (from Apple's intro, paraphrased)
- Test for crashes and bugs
- Make sure all metadata is complete and accurate
- Update contact info; provide a demo account and notes
- Enable backend services during review
- Include any non-obvious features in review notes

## 🟢 कैसे काम करता है? (Hindi)
1. Guidelines page खोलो।
2. शुरुआत की "Before You Submit" list पढ़ो।
3. अपने features को 5 sections से match करो।
4. Risky features (payment, chat, kids, health, login) पहचानो।
5. Compliance को design में शुरू से रखो।
6. Review notes में ज़रूरत पर guideline number लिखो।

---

## 🟡 Real World Example
Dream11/MPL जैसे real-money gaming apps पर 5.3 (Gambling) लागू होता है: licensed, geo-restricted, 18+ और local laws का पालन चाहिए। Instagram-जैसे UGC apps को 1.2 के तहत report, block और content filtering देनी होती है। Paytm/PhonePe जैसे finance apps को 5.1 के तहत privacy और data-handling बताना पड़ता है।

## 🟡 Real Example Hindi mein
Dream11 जैसे gaming apps को gambling rules (5.3) और license दिखाने होते हैं। Instagram जैसे apps में user content होता है, इसलिए report/block/moderation ज़रूरी है (1.2)। Paytm जैसे finance apps को privacy rules (5.1) मानने होते हैं।

---

## 💻 Code Example — Basic (UGC: report + block UI, guideline 1.2)
```jsx
// ReportBlockMenu.jsx - minimal Report/Block actions for user content
import React from 'react';                                       // React
import { View, Text, Pressable, Alert } from 'react-native';    // UI primitives

export default function ReportBlockMenu({ userId, onBlock }) {   // userId: author, onBlock: callback
  const report = () => {                                         // report handler
    Alert.alert('Reported', 'Our team will review within 24 hours.'); // acknowledge to user
    // TODO: POST /reports { userId } to backend (moderation queue)
  };
  const block = () => {                                          // block handler
    onBlock(userId);                                             // hide this user's content
    Alert.alert('Blocked', 'You will no longer see their posts.'); // confirm
  };
  return (
    <View style={{ flexDirection: 'row', gap: 16 }}>
      <Pressable onPress={report}><Text>Report</Text></Pressable>
      <Pressable onPress={block}><Text>Block</Text></Pressable>
    </View>
  );
}
```

## 💻 Code Example — Advanced (guideline-aware feature flags and platform handling)
```jsx
// compliance.js - central place for store-policy toggles
import { Platform } from 'react-native';                         // detect iOS / Android

export const compliance = {                                      // single source of truth
  // 3.1.1: digital subscription must use Apple IAP on iOS
  useStoreBilling: Platform.OS === 'ios',                        // iOS -> IAP, Android -> decide per Play policy
  // 4.8: show Sign in with Apple only on iOS
  showAppleSignIn: Platform.OS === 'ios',                        // button visible only on iOS
  // 5.1.1(v): in-app account deletion always on
  showDeleteAccount: true,                                       // required on iOS
};

// LoginButtons.jsx
import React from 'react';                                       // React
import { View, Button } from 'react-native';                     // UI
import * as AppleAuthentication from 'expo-apple-authentication'; // Expo module, iOS only (npx expo install expo-apple-authentication)

export function LoginButtons({ onGoogle, onApple }) {            // parent handlers
  return (
    <View style={{ gap: 12 }}>
      <Button title="Continue with Google" onPress={onGoogle} />
      {compliance.showAppleSignIn && (                           // 4.8 requirement
        <AppleAuthentication.AppleAuthenticationButton
          buttonType={AppleAuthentication.AppleAuthenticationButtonType.SIGN_IN}   // label type
          buttonStyle={AppleAuthentication.AppleAuthenticationButtonStyle.BLACK}   // style
          cornerRadius={8}                                       // rounded
          style={{ width: 240, height: 44 }}                     // size
          onPress={async () => {                                 // press handler
            try {
              const cred = await AppleAuthentication.signInAsync({ // opens native sheet
                requestedScopes: [AppleAuthentication.AppleAuthenticationScope.EMAIL],
              });
              onApple(cred);                                     // pass credential to backend
            } catch (e) {
              if (e.code !== 'ERR_REQUEST_CANCELED') console.warn(e); // ignore user cancel
            }
          }}
        />
      )}
    </View>
  );
}
```
The expo-apple-authentication snippet is not run (native iOS module).

---

## 📱 Android vs iOS Difference
| Feature | Android (Play policies) | iOS (App Review Guidelines) |
|---------|-------------------------|------------------------------|
| Document | Developer Program Policies | App Review Guidelines |
| Payments | Play Billing for digital goods | Apple IAP for digital goods |
| UGC | Moderation policy required | 1.2 report/block/filter |
| Login | No forced second login | 4.8 equivalent login rule |
| Kids | Families Policy | Kids Category rules (1.3) |
| Enforcement | Mostly automated + appeals | Human reviewer + Resolution Center |

---

## 🟠 Expo vs CLI Difference
Expo way:
```bash
npx expo install expo-apple-authentication   # compatible version chosen by Expo SDK
# app.json: "ios": { "usesAppleSignIn": true }   # enables the capability via prebuild
```
CLI way:
```bash
npm i expo-apple-authentication              # needs expo modules installed in bare RN
# Xcode: Target > Signing & Capabilities > + Capability > Sign in with Apple
cd ios && pod install                         # link the native module
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Never reading the guidelines until rejected.
✅ Correct: Skim all five sections during planning.

❌ Mistake 2: Using web payment links for digital goods.
✅ Correct: Use IAP (or check the current regional exceptions).

❌ Mistake 3: Using OTA to change the app's main purpose after approval.
✅ Correct: Only fix/improve; major changes need a new reviewed build.

❌ Mistake 4: UGC without report/block.
✅ Correct: Ship moderation tools before submit.

---

## 🧠 Tricky Interview Question
Is it allowed to download and execute JS from your server after App Review?

Answer: Yes, with limits. Guideline 2.5.2 allows interpreted code (JavaScript run by WebKit/JavaScriptCore) as long as it does not change the app's primary purpose, create a store-within-a-store, or bypass signing/security. That is why EAS Update/OTA is accepted, but turning a quiz app into a casino by OTA is a violation.

---

## ⚫ Interview Questions + Answers
Q1: Name the five sections.
A1: Safety, Performance, Business, Design, Legal.

Q2: Where do IAP rules live?
A2: Business, 3.1.1 (and 3.1.3 for exceptions).

Q3: What is guideline 4.2?
A3: Minimum functionality — the app must offer more than a repackaged website.

Q4: Which rule requires account deletion?
A4: 5.1.1(v).

Q5: What if you disagree with a rejection?
A5: Reply in Resolution Center, then appeal via App Review Board.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Planning features with payments, UGC, kids, health, finance, gaming

❌ Avoid:
- Memorising numbers; understand intent and re-check the live document

---

## 📊 Visual Diagram
```
 Guidelines
 ├─ 1 Safety      (UGC, kids, harm)
 ├─ 2 Performance (stable, complete, accurate)
 ├─ 3 Business    (IAP, subs, ads)
 ├─ 4 Design      (original, useful, Apple login)
 └─ 5 Legal       (privacy, IP, gambling)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| UGC | User-generated content | User का बनाया content |
| IAP | In-App Purchase | App के अंदर खरीद |
| Minimum functionality | App must be useful natively | कम से कम उपयोगी features |
| App Review Board | Appeal body | Appeal समिति |
| Privacy nutrition label | Data use summary | Data उपयोग का सार |

---

## ⚡ 3-Line Summary
English: Guidelines have 5 sections: Safety, Performance, Business, Design, Legal.
They decide approval, so plan compliance early.
Re-check the live document because rules change.

Hindi: Guidelines में 5 sections हैं: Safety, Performance, Business, Design, Legal।
इन्हीं से approval तय होता है, इसलिए पहले से plan करो।
Live document दोबारा देखो क्योंकि rules बदलते रहते हैं।

---

## ➡️ Next Topic
**255. Production Release (iOS)** — approval के बाद app को सही तरीके से live करना।
